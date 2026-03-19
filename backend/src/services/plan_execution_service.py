"""Service for meal plan execution and meal completion tracking."""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from sqlalchemy.exc import IntegrityError
import sqlalchemy as sa

from src.models.meal_plan import MealPlan, Meal, DailyMenu
from src.models.meal_completion import MealCompletion
from src.models.user_pantry_item import UserPantryItem
from src.models.recipe_ingredient import RecipeIngredient
from src.models.recipe import Recipe
from src.models.product import Product
from src.models.product_alias import ProductAlias
from src.services.grocery_service import GroceryService
from src.utils.unitConversion import convert_to_grams
from src.utils.canonical import canonicalize_string

logger = logging.getLogger(__name__)


def _calculate_ingredient_grams_for_meal(
    meal_servings: float, recipe_total_servings: float, ingredient: RecipeIngredient
) -> Dict[str, Any]:
    """
    Calculate ingredient quantity in grams for a specific meal serving size.

    Args:
        meal_servings: Number of servings for this meal in the plan
        recipe_total_servings: Total servings the recipe was designed for
        ingredient: The RecipeIngredient to calculate

    Returns:
        Dict with product info, original quantity, and calculated grams
    """
    # Convert ingredient quantity to grams
    quantity_g = convert_to_grams(float(ingredient.quantity_value), ingredient.quantity_unit)

    # Scale by ratio of meal servings to recipe total servings
    scale = meal_servings / recipe_total_servings if recipe_total_servings > 0 else meal_servings
    quantity_needed_g = quantity_g * scale

    return {
        "product_id": str(ingredient.product_id),
        "product_name": ingredient.product.name if ingredient.product else "Unknown",
        "original_quantity_value": float(ingredient.quantity_value),
        "original_quantity_unit": ingredient.quantity_unit,
        "grams": round(quantity_needed_g, 2),
    }


class PlanExecutionService:
    """Service for managing meal plan execution."""

    @staticmethod
    async def activate_plan(db: AsyncSession, plan_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """
        Activate a meal plan for execution.

        - Validates no other active plan exists
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

        # Idempotent: if already active, just return success
        if plan.execution_status == "active":
            return {"plan": plan, "updated_pantry": []}

        if plan.execution_status not in ("draft", "cancelled"):
            raise ValueError(f"Plan already {plan.execution_status}")

        # 2. Check for existing active plan
        active_stmt = select(MealPlan).where(
            MealPlan.user_id == user_id, MealPlan.execution_status == "active"
        )
        active_result = await db.execute(active_stmt)
        if active_result.scalar_one_or_none():
            raise ValueError("You already have an active plan. Please complete or cancel it first.")

        # 3. Update plan status
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
        - Idempotent: cancelling an already cancelled plan returns success
        """
        stmt = select(MealPlan).where(MealPlan.id == plan_id, MealPlan.user_id == user_id)
        result = await db.execute(stmt)
        plan = result.scalar_one_or_none()

        if not plan:
            raise ValueError("Plan not found")

        # Idempotent: if already cancelled, just return success
        if plan.execution_status == "cancelled":
            return plan

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
        from sqlalchemy.orm import selectinload

        # 1. Check if already completed
        existing_stmt = select(MealCompletion).where(
            MealCompletion.meal_id == meal_id, MealCompletion.user_id == user_id
        )
        existing_result = await db.execute(existing_stmt)
        if existing_result.scalar_one_or_none():
            raise ValueError("Meal already completed")

        # 2. Get meal with recipe - include ownership check via MealPlan
        meal_stmt = (
            select(Meal)
            .join(DailyMenu, Meal.daily_menu_id == DailyMenu.id)
            .join(MealPlan, DailyMenu.meal_plan_id == MealPlan.id)
            .options(selectinload(Meal.recipe))
            .where(Meal.id == meal_id, MealPlan.user_id == user_id)
        )
        meal_result = await db.execute(meal_stmt)
        meal = meal_result.scalar_one_or_none()

        if not meal:
            raise ValueError("Meal not found")

        recipe = meal.recipe
        recipe_total_servings = (
            float(recipe.total_servings) if recipe and recipe.total_servings else 1.0
        )

        # 3. Get recipe ingredients (with product eager load)
        ing_stmt = (
            select(RecipeIngredient)
            .options(selectinload(RecipeIngredient.product))
            .where(RecipeIngredient.recipe_id == meal.recipe_id)
        )
        ing_result = await db.execute(ing_stmt)
        ingredients = ing_result.scalars().all()

        # 4. Deduct from pantry
        deducted: Dict[str, Dict[str, Any]] = {}
        for ing in ingredients:
            # Use shared helper for consistent calculation
            ing_info = _calculate_ingredient_grams_for_meal(
                float(meal.servings), recipe_total_servings, ing
            )
            quantity_needed = ing_info["grams"]

            # Get current pantry item
            pantry_stmt = select(UserPantryItem).where(
                UserPantryItem.user_id == user_id, UserPantryItem.product_id == ing.product_id
            )
            pantry_result = await db.execute(pantry_stmt)
            pantry_item = pantry_result.scalar_one_or_none()

            if not pantry_item:
                canonical_key = None
                product_name = ing.product.name if ing.product else None
                if ing.product and ing.product.canonical_key:
                    canonical_key = ing.product.canonical_key
                elif product_name:
                    canonical_key = canonicalize_string(product_name)

                if canonical_key:
                    fallback_stmt = (
                        select(UserPantryItem)
                        .join(Product, UserPantryItem.product_id == Product.id)
                        .outerjoin(ProductAlias, ProductAlias.product_id == Product.id)
                        .where(
                            UserPantryItem.user_id == user_id,
                            or_(
                                Product.canonical_key == canonical_key,
                                ProductAlias.alias == canonical_key,
                            ),
                        )
                        .limit(1)
                    )
                    fallback_result = await db.execute(fallback_stmt)
                    pantry_item = fallback_result.scalar_one_or_none()

            if pantry_item:
                old_quantity = float(pantry_item.quantity_g)
                new_quantity = max(0, old_quantity - quantity_needed)

                if new_quantity == 0:
                    # Delete pantry item entirely when quantity reaches 0
                    await db.delete(pantry_item)
                else:
                    pantry_item.quantity_g = new_quantity

                deducted[str(ing.product_id)] = {
                    "quantity": quantity_needed,
                    "deducted_product_id": str(pantry_item.product_id),
                }
            else:
                logger.warning(
                    f"Product {ing.product_id} ({ing.product.name if ing.product else 'Unknown'}) "
                    f"not found in pantry for user {user_id}, cannot deduct {quantity_needed}g"
                )
                # Item not in pantry, still track deduction
                deducted[str(ing.product_id)] = {
                    "quantity": quantity_needed,
                    "deducted_product_id": None,
                }

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
        updated_pantry_stmt = (
            select(UserPantryItem, Product)
            .join(Product, UserPantryItem.product_id == Product.id, isouter=True)
            .where(UserPantryItem.user_id == user_id)
        )

        updated_pantry_result = await db.execute(updated_pantry_stmt)
        pantry_rows = updated_pantry_result.all()

        serialized_pantry = [
            {
                "product_id": str(pantry_item.product_id),
                "quantity_g": float(pantry_item.quantity_g),
                "product_name": product.name if product else "Unknown",
            }
            for pantry_item, product in pantry_rows
        ]

        return {
            "completion": completion,
            "updated_pantry": serialized_pantry,
            "ingredients_deducted": deducted,
        }

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
        for ingredient_id_str, snapshot in completion.ingredients_deducted.items():
            if isinstance(snapshot, (int, float)):
                quantity = float(snapshot)
                deducted_product_id = None
            else:
                quantity = float(snapshot.get("quantity", 0))
                deducted_product_id = snapshot.get("deducted_product_id")
            target_product_id = (
                UUID(deducted_product_id) if deducted_product_id else UUID(ingredient_id_str)
            )

            pantry_stmt = select(UserPantryItem).where(
                UserPantryItem.user_id == user_id, UserPantryItem.product_id == target_product_id
            )
            pantry_result = await db.execute(pantry_stmt)
            pantry_item = pantry_result.scalar_one_or_none()

            if pantry_item:
                pantry_item.quantity_g = float(pantry_item.quantity_g) + float(quantity)
            else:
                # Create pantry item if it doesn't exist
                pantry_item = UserPantryItem(
                    user_id=user_id, product_id=target_product_id, quantity_g=float(quantity)
                )
                db.add(pantry_item)

        # Delete completion record
        await db.delete(completion)

        await db.commit()

        # Fetch updated pantry
        updated_pantry = await db.execute(
            select(UserPantryItem).where(UserPantryItem.user_id == user_id)
        )
        return list(updated_pantry.scalars().all())

    @staticmethod
    async def get_today_meals(
        db: AsyncSession, plan_id: UUID, user_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Get today's meals from an active plan with completion status and ingredients.

        Returns:
            List of meals with completion info and ingredient gramatures
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
        daily_menu_stmt = select(DailyMenu).where(
            DailyMenu.meal_plan_id == plan_id, DailyMenu.day_number == current_day
        )
        daily_menu_result = await db.execute(daily_menu_stmt)
        daily_menu = daily_menu_result.scalar_one_or_none()

        if not daily_menu:
            return []

        # Get meals with completions - eager load recipe and ingredients to avoid lazy loading issues
        from sqlalchemy.orm import selectinload

        meals_stmt = (
            select(Meal)
            .options(
                selectinload(Meal.recipe)
                .selectinload(Recipe.recipe_ingredients)
                .selectinload(RecipeIngredient.product)
            )
            .where(Meal.daily_menu_id == daily_menu.id)
        )
        meals_result = await db.execute(meals_stmt)
        meals = meals_result.scalars().all()

        # For each meal, check if completed and calculate ingredients
        result = []
        for meal in meals:
            completion_stmt = select(MealCompletion).where(
                MealCompletion.meal_id == meal.id, MealCompletion.user_id == user_id
            )
            completion_result = await db.execute(completion_stmt)
            completion = completion_result.scalar_one_or_none()

            # Calculate ingredient grams for this meal
            ingredients = []
            if meal.recipe and meal.recipe.recipe_ingredients:
                recipe_total_servings = (
                    float(meal.recipe.total_servings) if meal.recipe.total_servings else 1.0
                )
                for ing in meal.recipe.recipe_ingredients:
                    ing_info = _calculate_ingredient_grams_for_meal(
                        float(meal.servings), recipe_total_servings, ing
                    )
                    ingredients.append(ing_info)

            result.append(
                {
                    "meal": meal,
                    "is_completed": completion is not None,
                    "completed_at": completion.completed_at if completion else None,
                    "ingredients": ingredients,
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
