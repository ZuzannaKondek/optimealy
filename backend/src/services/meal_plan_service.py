"""Meal plan service for creating and managing meal plans."""
from typing import Dict, Any, Optional, List
from datetime import date, datetime, timedelta
from uuid import UUID
import logging
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)

from src.models.meal_plan import MealPlan, DailyMenu, Meal
from src.models.user import User
from src.models.recipe import Recipe
from src.models.product import Product
from src.models.enums import OptimizationStatus
from src.models.user_pantry_item import UserPantryItem
from src.services.recipe_service import RecipeService
from src.services.product_service import ProductService
from src.services.optimization.solver import OptimizationSolver
from src.core.config import settings

# Meal type order for display and sorting
COURSE_ORDER = ["breakfast", "second_breakfast", "dinner", "dessert", "supper"]

# No longer needed - meal types are now consistent throughout
# All meal types use lowercase: breakfast, second_breakfast, dinner, dessert, supper


# No longer needed - meal types are now consistent throughout the system
# User-selected meal types match recipe meal_types directly


class MealPlanService:
    """Service for creating and managing meal plans."""

    @staticmethod
    async def create_meal_plan(
        db: AsyncSession,
        user: User,
        name: str,
        duration_days: int,
        target_calories_per_day: int,
        target_protein_g: Optional[float] = None,
        target_carbs_g: Optional[float] = None,
        target_fat_g: Optional[float] = None,
        start_date: Optional[date] = None,
        ingredients_to_have: Optional[List[Dict[str, Any]]] = None,
        ingredients_to_want: Optional[List[str]] = None,
        ingredients_to_exclude: Optional[List[str]] = None,
        dietary_tags: Optional[List[str]] = None,
        cuisine_types: Optional[List[str]] = None,
        selected_meal_types: Optional[List[str]] = None,
    ) -> MealPlan:
        """
        Create a new meal plan using the optimization algorithm.
        
        Args:
            db: Database session
            user: User creating the plan
            duration_days: Number of days for the plan
            target_calories_per_day: Daily calorie target
            target_protein_g: Daily protein target (optional)
            target_carbs_g: Daily carbs target (optional)
            target_fat_g: Daily fat target (optional)
            start_date: Start date (defaults to today)
            ingredients_to_have: List of {product_id, quantity_g} user already has
            ingredients_to_want: List of product IDs user wants to use
            ingredients_to_exclude: List of product IDs to exclude
            dietary_tags: List of dietary tags to filter recipes
            cuisine_types: List of cuisine types to filter recipes
            selected_meal_types: List of course types selected by user (e.g., ["Breakfast", "Dinner", "Supper"])
            
        Returns:
            Created MealPlan object
            
        Raises:
            ValueError: If input validation fails
            RuntimeError: If optimization fails
        """
        # Validate inputs
        if duration_days < settings.MIN_PLAN_DURATION_DAYS:
            raise ValueError(f"Duration must be at least {settings.MIN_PLAN_DURATION_DAYS} days")
        
        if duration_days > settings.MAX_PLAN_DURATION_DAYS:
            raise ValueError(f"Duration cannot exceed {settings.MAX_PLAN_DURATION_DAYS} days")
        
        if target_calories_per_day < 800 or target_calories_per_day > 5000:
            raise ValueError("Calorie target must be between 800 and 5000")
        
        # Validate selected_meal_types if provided
        if selected_meal_types is not None:
            if not selected_meal_types:
                raise ValueError("selected_meal_types cannot be empty")
            # Minimum required: breakfast, dinner, supper
            required_types = {"breakfast", "dinner", "supper"}
            selected_set = set(selected_meal_types)
            if not required_types.issubset(selected_set):
                missing = required_types - selected_set
                raise ValueError(f"selected_meal_types must include at least: {', '.join(sorted(required_types))}. Missing: {', '.join(sorted(missing))}")
            # Validate all selected types are valid
            valid_types = set(COURSE_ORDER)
            invalid_types = selected_set - valid_types
            if invalid_types:
                raise ValueError(f"Invalid meal types: {', '.join(sorted(invalid_types))}. Valid types: {', '.join(sorted(valid_types))}")
            logger.info(f"Creating meal plan with selected meal types: {selected_meal_types}")
        
        # Set default start date
        if start_date is None:
            start_date = date.today()
        
        # Fetch user's pantry and merge with ingredients_to_have
        pantry_items = await MealPlanService._fetch_user_pantry(db, user.id)
        if pantry_items:
            logger.info(f"Found {len(pantry_items)} items in user's pantry")
            # Merge pantry with any explicitly provided ingredients_to_have
            if ingredients_to_have is None:
                ingredients_to_have = []
            ingredients_to_have = ingredients_to_have + pantry_items
        
        # Validate and normalize name
        plan_name = (name or "").strip()
        if not plan_name:
            raise ValueError("Plan name is required")

        # Create meal plan record with "in_progress" status
        meal_plan = MealPlan(
            user_id=user.id,
            name=plan_name,
            start_date=start_date,
            duration_days=duration_days,
            target_calories_per_day=target_calories_per_day,
            target_protein_g=target_protein_g,
            target_carbs_g=target_carbs_g,
            target_fat_g=target_fat_g,
            user_constraints={
                "ingredients_to_have": ingredients_to_have or [],
                "ingredients_to_want": ingredients_to_want or [],
                "ingredients_to_exclude": ingredients_to_exclude or [],
                "dietary_tags": dietary_tags or [],
                "cuisine_types": cuisine_types or [],
                "selected_meal_types": selected_meal_types or [],
            },
            optimization_status=OptimizationStatus.IN_PROGRESS.value,
        )
        
        db.add(meal_plan)
        await db.flush()
        
        try:
            # Get all recipes and products
            all_recipes = await RecipeService.get_all_recipes(db, limit=1000)
            all_products = await ProductService.get_all_products(db, limit=1000)
            
            # Filter recipes based on constraints
            # If selected_meal_types is provided, use them directly (no conversion needed)
            meal_types_filter = None
            if selected_meal_types:
                meal_types_filter = selected_meal_types
                logger.info(f"Filtering recipes by meal_types: {meal_types_filter}")
            
            print(f"=== RECIPE FILTERING ===")
            print(f"Total recipes available: {len(all_recipes)}")
            print(f"Meal types filter: {meal_types_filter}")
            print(f"Dietary tags filter: {dietary_tags}")
            print(f"Cuisine types filter: {cuisine_types}")
            print(f"Exclude ingredients: {len(ingredients_to_exclude or [])}")
            print(f"Include ingredients: {len(ingredients_to_want or [])}")
            
            filtered_recipes = await RecipeService.filter_recipes(
                db=db,
                meal_types=meal_types_filter,  # Filter by meal_types if selected_meal_types provided
                dietary_tags=dietary_tags,
                cuisine_types=cuisine_types,
                exclude_ingredients=ingredients_to_exclude,
                include_ingredients=ingredients_to_want,
                limit=500,
            )
            
            print(f"Filtered recipes count: {len(filtered_recipes)}")
            
            # Count recipes by meal_type
            if meal_types_filter:
                meal_type_counts = {}
                for recipe in filtered_recipes:
                    for mt in recipe.meal_types:
                        if mt in meal_types_filter:
                            meal_type_counts[mt] = meal_type_counts.get(mt, 0) + 1
                print(f"Filtered recipes by meal_type: {meal_type_counts}")
            print(f"========================")
            
            logger.info(
                f"Recipe filtering: total={len(all_recipes)}, filtered={len(filtered_recipes)}, "
                f"dietary_tags={dietary_tags}, cuisine_types={cuisine_types}, "
                f"exclude_count={len(ingredients_to_exclude or [])}, include_count={len(ingredients_to_want or [])}"
            )
            
            if not filtered_recipes:
                meal_plan.optimization_status = OptimizationStatus.FAILED.value
                await db.commit()
                raise ValueError("No recipes found matching the specified criteria")
            
            # Run optimization
            logger.info(
                f"[meal_plan_service] Starting optimization: "
                f"{len(filtered_recipes)} recipes, {duration_days} days, "
                f"target={target_calories_per_day} kcal, "
                f"meal_types={selected_meal_types}, "
                f"solver_timeout={settings.OPTIMIZATION_TIMEOUT_SECONDS}s"
            )
            t_solve_start = time.perf_counter()

            solver = OptimizationSolver(
                recipes=filtered_recipes,
                products=all_products,
                days=duration_days,
                target_calories=target_calories_per_day,
                target_protein=target_protein_g,
                target_carbs=target_carbs_g,
                target_fat=target_fat_g,
                excluded_product_ids=ingredients_to_exclude or [],
                timeout_seconds=settings.OPTIMIZATION_TIMEOUT_SECONDS,
                selected_meal_types=selected_meal_types,
            )
            
            solution, status, error_message = solver.solve()
            t_solve_elapsed = time.perf_counter() - t_solve_start
            logger.info(
                f"[meal_plan_service] Optimization finished in {t_solve_elapsed:.2f}s — "
                f"status={status}"
            )
            
            if solution is None:
                meal_plan.optimization_status = OptimizationStatus.FAILED.value
                await db.commit()
                
                # Log the error for debugging
                logger.error(
                    f"Optimization failed: status={status}, error_message={error_message}, "
                    f"recipes_count={len(filtered_recipes)}, selected_meal_types={selected_meal_types}, "
                    f"target_calories={target_calories_per_day}"
                )
                raise RuntimeError(error_message or f"Optimization failed with status: {status}")
            
            # Save solution to database
            await MealPlanService._save_solution_to_db(
                db=db,
                meal_plan=meal_plan,
                solution=solution,
                start_date=start_date,
            )
            
            meal_plan.algorithm_execution_time_s = solution.get("execution_time_s", 0.0)
            meal_plan.optimization_status = OptimizationStatus.COMPLETED.value
            
            # Commit meal plan first
            await db.commit()
            await db.refresh(meal_plan)
            
            # Calculate waste metrics after meal plan is committed
            # This requires generating the grocery list which needs a separate transaction
            try:
                waste_metrics = await MealPlanService._calculate_waste_metrics(
                    db=db,
                    meal_plan=meal_plan,
                )
                
                meal_plan.estimated_food_waste_g = waste_metrics.get("total_waste_g")
                meal_plan.pantry_additions_g = waste_metrics.get("pantry_additions_g")
                meal_plan.waste_reduction_percentage = waste_metrics.get("waste_reduction_percentage")
                meal_plan.estimated_total_cost = waste_metrics.get("total_cost")
                
                await db.commit()
                await db.refresh(meal_plan)
            except Exception as e:
                logger.warning(f"Failed to calculate waste metrics: {e}")
                # Continue without waste metrics rather than failing the whole plan
            
            return meal_plan
            
        except Exception as e:
            meal_plan.optimization_status = OptimizationStatus.FAILED.value
            await db.commit()
            raise

    @staticmethod
    async def _save_solution_to_db(
        db: AsyncSession,
        meal_plan: MealPlan,
        solution: Dict[str, Any],
        start_date: date,
    ) -> None:
        """Save optimization solution to database."""
        from src.services.optimization.utils import calculate_dish_weight
        from src.models.recipe import Recipe
        from sqlalchemy import select
        
        days_data = solution.get("days", {})
        
        for day_num in range(meal_plan.duration_days):
            day_key = f"day_{day_num + 1}"
            day_data = days_data.get(day_key, {})
            
            # Validate dish count for dish-based plans
            selected_meal_types = meal_plan.user_constraints.get("selected_meal_types", [])
            if selected_meal_types:
                recipes_data = day_data.get("recipes", [])
                expected_count = len(selected_meal_types)
                if len(recipes_data) != expected_count:
                    error_msg = (
                        f"Day {day_num + 1} has {len(recipes_data)} dishes, "
                        f"but expected {expected_count}"
                    )
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                logger.debug(
                    f"Day {day_num + 1}: Validated {len(recipes_data)} dishes "
                    f"(expected {expected_count})"
                )
            
            menu_date = start_date + timedelta(days=day_num)
            
            daily_menu = DailyMenu(
                meal_plan_id=meal_plan.id,
                day_number=day_num + 1,
                menu_date=menu_date,
                actual_calories=day_data.get("total_calories", 0),
                actual_protein_g=day_data.get("total_protein_g", 0.0),
                actual_carbs_g=day_data.get("total_carbs_g", 0.0),
                actual_fat_g=day_data.get("total_fat_g", 0.0),
            )
            
            db.add(daily_menu)
            await db.flush()
            
            # Add meals
            recipes_data = day_data.get("recipes", [])
            meals_to_create = []
            
            for recipe_data in recipes_data:
                # Get recipe to calculate dish weight
                recipe_id = recipe_data["recipe_id"]
                from sqlalchemy.orm import selectinload
                from src.models.recipe_ingredient import RecipeIngredient
                stmt = (
                    select(Recipe)
                    .where(Recipe.id == recipe_id)
                    .options(selectinload(Recipe.recipe_ingredients))
                )
                result = await db.execute(stmt)
                recipe = result.scalar_one_or_none()
                
                # Calculate dish weight if recipe exists
                dish_weight_g = None
                if recipe:
                    dish_weight_g = calculate_dish_weight(recipe)
                
                meal = Meal(
                    daily_menu_id=daily_menu.id,
                    recipe_id=recipe_id,
                    meal_type=recipe_data["meal_type"],
                    servings=recipe_data["servings"],
                    dish_weight_g=dish_weight_g,
                    calculated_nutritional_info={
                        "calories": recipe_data["calories"],
                        "protein": recipe_data["protein_g"],
                        "carbs": recipe_data["carbs_g"],
                        "fat": recipe_data["fat_g"],
                    },
                )
                meals_to_create.append(meal)
            
            # Note: No course assignment needed - meal_type is already set from solution
            
            for meal in meals_to_create:
                db.add(meal)

    # Note: _assign_courses_to_dishes removed - course_type no longer exists
    # Meal types are now consistent throughout (no course_type needed)

    @staticmethod
    async def _calculate_waste_metrics(
        db: AsyncSession,
        meal_plan: MealPlan,
    ) -> Dict[str, Any]:
        """
        Calculate waste metrics for a meal plan.
        
        Separates perishable waste (true waste) from shelf-stable leftovers
        (which are added to user's pantry automatically).
        
        Returns:
            Dictionary with waste metrics:
            - perishable_waste_g: Actual waste from perishable items
            - pantry_additions_g: Shelf-stable leftovers added to pantry
            - waste_reduction_percentage: Improvement vs. unoptimized baseline
            - total_cost: Estimated total cost (if available)
        """
        from src.services.grocery_service import GroceryService
        
        # Generate grocery list to get waste calculations
        try:
            grocery_list = await GroceryService.generate_grocery_list(
                db,
                plan_id=str(meal_plan.id),
                user_id=str(meal_plan.user_id),
                exclude_owned=False
            )
            
            # Separate waste by perishability
            perishable_waste_g = 0.0
            pantry_additions_g = 0.0
            shelf_stable_items_for_pantry = []
            
            for item in grocery_list.items:
                product_stmt = select(Product).where(Product.id == item.product_id)
                product_result = await db.execute(product_stmt)
                product = product_result.scalar_one_or_none()
                
                if not product:
                    continue
                
                waste_g = float(item.estimated_item_waste_g or 0.0)
                
                if waste_g > 0:
                    # Check if shelf-stable (using "stable" to match database values)
                    if product.perishability in ("stable", "shelf_stable"):
                        # Shelf-stable leftover → add to pantry
                        pantry_additions_g += waste_g
                        shelf_stable_items_for_pantry.append({
                            "product_id": str(product.id),
                            "quantity_g": waste_g
                        })
                    else:
                        # Perishable item → count as waste
                        perishable_waste_g += waste_g
            
            # Auto-add shelf-stable leftovers to user's pantry
            if shelf_stable_items_for_pantry:
                await MealPlanService._update_pantry_with_leftovers(
                    db, meal_plan.user_id, shelf_stable_items_for_pantry
                )
                logger.info(f"Added {len(shelf_stable_items_for_pantry)} shelf-stable items to pantry")
            
            # Calculate baseline waste (only for perishable items)
            baseline_waste_g = await MealPlanService._calculate_baseline_waste(
                db, meal_plan, grocery_list, perishable_only=True
            )
            
            # Calculate reduction percentage
            if baseline_waste_g > 0:
                waste_reduction_percentage = (
                    (baseline_waste_g - perishable_waste_g) / baseline_waste_g * 100
                )
                waste_reduction_percentage = max(0.0, min(100.0, waste_reduction_percentage))
            else:
                waste_reduction_percentage = 0.0
            
            total_cost = grocery_list.estimated_total_cost
            
            return {
                "total_waste_g": perishable_waste_g,
                "pantry_additions_g": pantry_additions_g,
                "waste_reduction_percentage": waste_reduction_percentage,
                "total_cost": total_cost,
            }
        except Exception as e:
            logger.warning(f"Failed to calculate waste metrics: {e}")
            return {
                "total_waste_g": 0.0,
                "pantry_additions_g": 0.0,
                "waste_reduction_percentage": 0.0,
                "total_cost": None,
            }
    
    @staticmethod
    async def _calculate_baseline_waste(
        db: AsyncSession,
        meal_plan: MealPlan,
        grocery_list,
        perishable_only: bool = False
    ) -> float:
        """
        Calculate baseline waste assuming naive purchasing strategy.
        
        Baseline scenario: Buy ingredients for each recipe independently,
        without considering ingredient reuse or what user already has.
        This represents the "unoptimized" approach for comparison.
        
        Args:
            perishable_only: If True, only count perishable items in baseline
        
        Returns:
            Total baseline waste in grams
        """
        from src.services.grocery_service import GroceryService
        
        # Sum waste for each grocery item if purchased independently
        baseline_waste_g = 0.0
        
        for item in grocery_list.items:
            # For baseline, ignore what user already has
            required_g = float(item.required_quantity_g)
            
            # Find smallest package that fits the requirement
            product_stmt = select(Product).where(Product.id == item.product_id)
            product_result = await db.execute(product_stmt)
            product = product_result.scalar_one_or_none()
            
            if product:
                # Skip shelf-stable items if only counting perishable
                if perishable_only and product.perishability == "shelf_stable":
                    continue
                
                purchase_g = GroceryService._match_package_size_g(
                    required_g, product.common_package_sizes
                )
                waste_g = max(0.0, purchase_g - required_g)
                baseline_waste_g += waste_g
        
        return baseline_waste_g
    
    @staticmethod
    async def _update_pantry_with_leftovers(
        db: AsyncSession,
        user_id: UUID,
        leftover_items: List[Dict[str, Any]]
    ) -> None:
        """
        Update user's pantry with shelf-stable leftovers.
        
        Adds leftover quantities to existing pantry items, or creates new entries.
        
        Args:
            db: Database session
            user_id: User ID
            leftover_items: List of {"product_id": str, "quantity_g": float}
        """
        for item in leftover_items:
            try:
                product_id = UUID(item["product_id"])
                leftover_qty = float(item["quantity_g"])
                
                if leftover_qty <= 0:
                    continue
                
                # Check if user already has this item in pantry
                query = select(UserPantryItem).where(
                    UserPantryItem.user_id == user_id,
                    UserPantryItem.product_id == product_id
                )
                result = await db.execute(query)
                existing = result.scalar_one_or_none()
                
                if existing:
                    # Add to existing quantity
                    existing.quantity_g = float(existing.quantity_g) + leftover_qty
                else:
                    # Create new pantry item
                    new_item = UserPantryItem(
                        user_id=user_id,
                        product_id=product_id,
                        quantity_g=leftover_qty
                    )
                    db.add(new_item)
                
                logger.info(f"Added {leftover_qty}g of product {product_id} to pantry for user {user_id}")
                
            except Exception as e:
                logger.warning(f"Failed to add leftover to pantry: {e}")
                continue
        
        await db.commit()

    @staticmethod
    async def get_user_meal_plans(
        db: AsyncSession,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> List[MealPlan]:
        """
        Get meal plans for a user.
        
        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of plans to return
            offset: Number of plans to skip
            status: Filter by optimization status (optional)
            
        Returns:
            List of MealPlan objects
        """
        stmt = (
            select(MealPlan)
            .where(MealPlan.user_id == user_id)
            .order_by(MealPlan.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        if status:
            stmt = stmt.where(MealPlan.optimization_status == status)
        
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_meal_plan_by_id(
        db: AsyncSession,
        plan_id: str,
        user_id: str,
    ) -> Optional[MealPlan]:
        """
        Get a meal plan by ID (ensuring it belongs to the user).
        
        Args:
            db: Database session
            plan_id: Meal plan ID
            user_id: User ID (for authorization)
            
        Returns:
            MealPlan object if found and authorized, None otherwise
        """
        stmt = select(MealPlan).where(
            MealPlan.id == plan_id,
            MealPlan.user_id == user_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_meal_plan(
        db: AsyncSession,
        plan_id: str,
        user_id: str,
    ) -> bool:
        """
        Delete a meal plan.
        
        Args:
            db: Database session
            plan_id: Meal plan ID
            user_id: User ID (for authorization)
            
        Returns:
            True if deleted, False if not found
        """
        meal_plan = await MealPlanService.get_meal_plan_by_id(db, plan_id, user_id)
        
        if meal_plan is None:
            return False
        
        await db.delete(meal_plan)
        await db.commit()
        
        return True
    
    @staticmethod
    async def _fetch_user_pantry(db: AsyncSession, user_id) -> List[Dict[str, Any]]:
        """
        Fetch user's pantry items and format as ingredients_to_have.
        
        Args:
            db: Database session
            user_id: User ID (UUID object or string)
            
        Returns:
            List of dicts with product_id and quantity_g
        """
        # user_id is already a UUID object from the User model, use it directly
        query = select(UserPantryItem).where(UserPantryItem.user_id == user_id)
        result = await db.execute(query)
        pantry_items = result.scalars().all()
        
        return [
            {
                "product_id": str(item.product_id),
                "quantity_g": float(item.quantity_g)
            }
            for item in pantry_items
        ]