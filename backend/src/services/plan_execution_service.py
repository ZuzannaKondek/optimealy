"""Service for meal plan execution and meal completion tracking."""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.exc import IntegrityError
import sqlalchemy as sa

from src.models.meal_plan import MealPlan, Meal
from src.models.meal_completion import MealCompletion
from src.models.user_pantry_item import UserPantryItem
from src.models.recipe_ingredient import RecipeIngredient
from src.models.product import Product
from src.services.grocery_service import GroceryService
from src.utils.unitConversion import convert_to_grams

logger = logging.getLogger(__name__)


class PlanExecutionService:
    """Service for managing meal plan execution."""

    @staticmethod
    async def activate_plan(db: AsyncSession, plan_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """
        Activate a meal plan for execution.

        - Validates no other active plan exists
        - Adds grocery list to pantry (additive)
        - Updates plan status to 'active'

        Returns:
            Dict with plan and updated_pantry

        Raises:
            ValueError: If validation fails
            IntegrityError: If unique constraint violated
        """
        # 1. Fetch the plan
        stmt = select(MealPlan).where(MealPlan.id == plan_id, MealPlan.user_id == user_id)
        result = await db.execute(stmt)
        plan = result.scalar_one_or_none()

        if not plan:
            raise ValueError("Plan not found")

        if plan.execution_status != "draft":
            raise ValueError(f"Plan already {plan.execution_status}")

        # 2. Check for existing active plan
        active_stmt = select(MealPlan).where(
            MealPlan.user_id == user_id, MealPlan.execution_status == "active"
        )
        active_result = await db.execute(active_stmt)
        if active_result.scalar_one_or_none():
            raise ValueError("You already have an active plan. Please complete or cancel it first.")

        # 3. Get grocery list and add to pantry (additive)
        grocery_list = await GroceryService.generate_grocery_list(
            db, plan_id=str(plan_id), user_id=str(user_id), exclude_owned=False
        )

        for item in grocery_list.items:
            # Get or create pantry item
            pantry_stmt = select(UserPantryItem).where(
                UserPantryItem.user_id == user_id, UserPantryItem.product_id == item.product_id
            )
            pantry_result = await db.execute(pantry_stmt)
            pantry_item = pantry_result.scalar_one_or_none()

            if pantry_item:
                # Add to existing quantity
                pantry_item.quantity_g = float(pantry_item.quantity_g) + float(
                    item.required_quantity_g
                )
            else:
                # Create new pantry item
                pantry_item = UserPantryItem(
                    user_id=user_id,
                    product_id=item.product_id,
                    quantity_g=float(item.required_quantity_g),
                )
                db.add(pantry_item)

        # 4. Update plan status
        plan.execution_status = "active"

        await db.commit()
        await db.refresh(plan)

        # 5. Fetch updated pantry
        updated_pantry = await db.execute(
            select(UserPantryItem).where(UserPantryItem.user_id == user_id)
        )
        pantry_items = updated_pantry.scalars().all()

        return {"plan": plan, "updated_pantry": pantry_items}

    @staticmethod
    async def cancel_plan(db: AsyncSession, plan_id: UUID, user_id: UUID) -> MealPlan:
        """
        Cancel an active meal plan.

        - Pantry remains unchanged
        - Updates plan status to 'cancelled'
        """
        stmt = select(MealPlan).where(MealPlan.id == plan_id, MealPlan.user_id == user_id)
        result = await db.execute(stmt)
        plan = result.scalar_one_or_none()

        if not plan:
            raise ValueError("Plan not found")

        if plan.execution_status != "active":
            raise ValueError("Plan is not active")

        plan.execution_status = "cancelled"

        await db.commit()
        await db.refresh(plan)

        return plan

    @staticmethod
    async def get_active_plan(db: AsyncSession, user_id: UUID) -> Optional[MealPlan]:
        """Get user's active plan, if any."""
        stmt = select(MealPlan).where(
            MealPlan.user_id == user_id, MealPlan.execution_status == "active"
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def complete_meal(db: AsyncSession, meal_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """
        Mark a meal as completed and deduct ingredients from pantry.

        Returns:
            Dict with completion and updated_pantry

        Raises:
            ValueError: If meal already completed or not found
        """
        # 1. Check if already completed
        existing_stmt = select(MealCompletion).where(
            MealCompletion.meal_id == meal_id, MealCompletion.user_id == user_id
        )
        existing_result = await db.execute(existing_stmt)
        if existing_result.scalar_one_or_none():
            raise ValueError("Meal already completed")

        # 2. Get meal with recipe and ingredients
        meal_stmt = select(Meal).where(Meal.id == meal_id)
        meal_result = await db.execute(meal_stmt)
        meal = meal_result.scalar_one_or_none()

        if not meal:
            raise ValueError("Meal not found")

        # 3. Get recipe ingredients
        ing_stmt = select(RecipeIngredient).where(RecipeIngredient.recipe_id == meal.recipe_id)
        ing_result = await db.execute(ing_stmt)
        ingredients = ing_result.scalars().all()

        # 4. Deduct from pantry
        deducted = {}
        for ing in ingredients:
            # Convert ingredient quantity to grams
            quantity_g = convert_to_grams(float(ing.quantity_value), ing.quantity_unit)

            # Calculate actual quantity for this meal (scaled by servings)
            quantity_needed = quantity_g * float(meal.servings)

            # Get current pantry item
            pantry_stmt = select(UserPantryItem).where(
                UserPantryItem.user_id == user_id, UserPantryItem.product_id == ing.product_id
            )
            pantry_result = await db.execute(pantry_stmt)
            pantry_item = pantry_result.scalar_one_or_none()

            if pantry_item:
                old_quantity = float(pantry_item.quantity_g)
                new_quantity = max(0, old_quantity - quantity_needed)
                pantry_item.quantity_g = new_quantity
                deducted[str(ing.product_id)] = quantity_needed
            else:
                # Item not in pantry, still track deduction
                deducted[str(ing.product_id)] = quantity_needed

        # 5. Create completion record
        completion = MealCompletion(
            meal_id=meal_id,
            user_id=user_id,
            completed_at=datetime.utcnow(),
            ingredients_deducted=deducted,
        )
        db.add(completion)

        await db.commit()
        await db.refresh(completion)

        # 6. Fetch updated pantry
        updated_pantry = await db.execute(
            select(UserPantryItem).where(UserPantryItem.user_id == user_id)
        )
        pantry_items = updated_pantry.scalars().all()

        return {"completion": completion, "updated_pantry": pantry_items}

    @staticmethod
    async def uncomplete_meal(
        db: AsyncSession, meal_id: UUID, user_id: UUID
    ) -> List[UserPantryItem]:
        """
        Uncomplete a meal and restore pantry quantities.

        Returns:
            Updated pantry items

        Raises:
            ValueError: If completion not found
        """
        # Get completion record
        stmt = select(MealCompletion).where(
            MealCompletion.meal_id == meal_id, MealCompletion.user_id == user_id
        )
        result = await db.execute(stmt)
        completion = result.scalar_one_or_none()

        if not completion:
            raise ValueError("Completion not found")

        # Restore pantry quantities
        for product_id_str, quantity in completion.ingredients_deducted.items():
            product_id = UUID(product_id_str)

            pantry_stmt = select(UserPantryItem).where(
                UserPantryItem.user_id == user_id, UserPantryItem.product_id == product_id
            )
            pantry_result = await db.execute(pantry_stmt)
            pantry_item = pantry_result.scalar_one_or_none()

            if pantry_item:
                pantry_item.quantity_g = float(pantry_item.quantity_g) + float(quantity)
            else:
                # Create pantry item if it doesn't exist
                pantry_item = UserPantryItem(
                    user_id=user_id, product_id=product_id, quantity_g=float(quantity)
                )
                db.add(pantry_item)

        # Delete completion record
        await db.delete(completion)

        await db.commit()

        # Fetch updated pantry
        updated_pantry = await db.execute(
            select(UserPantryItem).where(UserPantryItem.user_id == user_id)
        )
        return updated_pantry.scalars().all()

    @staticmethod
    async def get_today_meals(
        db: AsyncSession, plan_id: UUID, user_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Get today's meals from an active plan with completion status.

        Returns:
            List of meals with completion info
        """
        # Get plan
        plan_stmt = select(MealPlan).where(MealPlan.id == plan_id, MealPlan.user_id == user_id)
        plan_result = await db.execute(plan_stmt)
        plan = plan_result.scalar_one_or_none()

        if not plan:
            return []

        # Calculate which day we're on
        days_since_start = (datetime.utcnow().date() - plan.start_date).days
        current_day = days_since_start + 1  # Day 1-indexed

        # Check if current date is within plan range
        if current_day < 1 or current_day > plan.duration_days:
            return []

        # Get meals for today (this implementation needs DailyMenu lookup by day_number)
        from src.models.meal_plan import DailyMenu

        daily_menu_stmt = select(DailyMenu).where(
            DailyMenu.meal_plan_id == plan_id, DailyMenu.day_number == current_day
        )
        daily_menu_result = await db.execute(daily_menu_stmt)
        daily_menu = daily_menu_result.scalar_one_or_none()

        if not daily_menu:
            return []

        # Get meals with completions
        meals_stmt = select(Meal).where(Meal.daily_menu_id == daily_menu.id)
        meals_result = await db.execute(meals_stmt)
        meals = meals_result.scalars().all()

        # For each meal, check if completed
        result = []
        for meal in meals:
            completion_stmt = select(MealCompletion).where(
                MealCompletion.meal_id == meal.id, MealCompletion.user_id == user_id
            )
            completion_result = await db.execute(completion_stmt)
            completion = completion_result.scalar_one_or_none()

            result.append(
                {
                    "meal": meal,
                    "is_completed": completion is not None,
                    "completed_at": completion.completed_at if completion else None,
                }
            )

        return result

    @staticmethod
    async def check_and_complete_plans(db: AsyncSession) -> List[MealPlan]:
        """
        Check for active plans past their end date and complete them.

        This should be called by a scheduled job or on user login.

        Returns:
            List of plans that were auto-completed
        """
        today = datetime.utcnow().date()

        # Find active plans past their end date
        stmt = select(MealPlan).where(
            MealPlan.execution_status == "active",
            MealPlan.start_date + func.cast(MealPlan.duration_days, sa.types.Interval) < today,
        )
        result = await db.execute(stmt)
        expired_plans = result.scalars().all()

        completed_plans = []
        for plan in expired_plans:
            # Mark as completed
            plan.execution_status = "completed"
            completed_plans.append(plan)

        if completed_plans:
            await db.commit()

        return completed_plans
