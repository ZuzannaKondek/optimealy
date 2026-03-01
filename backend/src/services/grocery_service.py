"""Grocery list generation service."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.grocery import GroceryItem, GroceryList
from src.models.meal_plan import DailyMenu, MealPlan, Meal
from src.models.recipe import Recipe
from src.models.recipe_ingredient import RecipeIngredient
from src.models.product import Product


class GroceryService:
    """Service for generating and retrieving grocery lists."""

    @staticmethod
    def _get_owned_quantities_g(meal_plan: MealPlan) -> Dict[str, float]:
        constraints = meal_plan.user_constraints or {}
        owned = constraints.get("ingredients_to_have") or []
        owned_by_product_id: Dict[str, float] = {}
        for item in owned:
            try:
                product_id = str(item.get("product_id"))
                qty_g = float(item.get("quantity_g") or 0)
                if product_id:
                    owned_by_product_id[product_id] = owned_by_product_id.get(
                        product_id, 0.0
                    ) + max(qty_g, 0.0)
            except Exception:
                # Ignore malformed entries
                continue
        return owned_by_product_id

    @staticmethod
    def _match_package_size_g(required_g: float, package_sizes: List[Any]) -> float:
        """
        Pick a purchase quantity (g) based on available package sizes.

        Assumptions (MVP):
        - Product.common_package_sizes is a list of numeric sizes in grams.
        """
        if required_g <= 0:
            return 0.0

        sizes: List[float] = []
        for s in package_sizes or []:
            try:
                sizes.append(float(s))
            except Exception:
                continue

        sizes = sorted([s for s in sizes if s > 0])
        if not sizes:
            return float(required_g)

        for s in sizes:
            if s >= required_g:
                return float(s)
        return float(sizes[-1])

    @staticmethod
    def _estimate_cost(purchase_g: float, product: Product) -> Optional[float]:
        if product.price_per_unit is None:
            return None
        try:
            price = float(product.price_per_unit)
        except Exception:
            return None

        unit = (product.standard_unit or "").lower()
        if unit in {"g", "gram", "grams"}:
            return price * purchase_g
        if unit in {"kg", "kilogram", "kilograms"}:
            return price * (purchase_g / 1000.0)
        return None

    @staticmethod
    async def generate_grocery_list(
        db: AsyncSession,
        *,
        plan_id: str,
        user_id: str,
        exclude_owned: bool = False,
    ) -> GroceryList:
        """
        Generate (or regenerate) a grocery list for the given plan.
        """
        stmt = select(MealPlan).where(MealPlan.id == plan_id, MealPlan.user_id == user_id)
        result = await db.execute(stmt)
        meal_plan = result.scalar_one_or_none()
        if meal_plan is None:
            raise ValueError("Meal plan not found")

        meals_stmt = (
            select(Meal)
            .join(DailyMenu, Meal.daily_menu_id == DailyMenu.id)
            .where(DailyMenu.meal_plan_id == meal_plan.id)
            .options(
                selectinload(Meal.recipe)
                .selectinload(Recipe.recipe_ingredients)
                .selectinload(RecipeIngredient.product)
            )
        )
        meals_result = await db.execute(meals_stmt)
        meals = list(meals_result.scalars().all())

        required_by_product_id: Dict[str, float] = defaultdict(float)
        products_by_id: Dict[str, Product] = {}

        for meal in meals:
            if meal.recipe is None:
                continue
            recipe = meal.recipe
            servings_used = float(meal.servings)
            recipe_total_servings = float(recipe.total_servings) if recipe.total_servings else 1.0
            scale = servings_used / recipe_total_servings

            for ri in recipe.recipe_ingredients:
                if ri.product is None:
                    continue
                product_id = str(ri.product_id)
                qty = float(ri.quantity_value) * scale
                required_by_product_id[product_id] += max(qty, 0.0)
                products_by_id[product_id] = ri.product

        owned_by_product_id = GroceryService._get_owned_quantities_g(meal_plan)

        # Find or create GroceryList
        existing_stmt = (
            select(GroceryList)
            .where(GroceryList.meal_plan_id == meal_plan.id)
            .options(selectinload(GroceryList.items))
        )
        existing_result = await db.execute(existing_stmt)
        grocery_list = existing_result.scalar_one_or_none()

        if grocery_list is None:
            grocery_list = GroceryList(
                meal_plan_id=meal_plan.id,
                total_items=0,
                generated_at=datetime.utcnow(),
            )
            db.add(grocery_list)
            await db.flush()
        else:
            # Regenerate items
            for item in list(grocery_list.items):
                await db.delete(item)
            grocery_list.generated_at = datetime.utcnow()

        total_cost = 0.0
        total_cost_has_value = False
        total_waste_g = 0.0

        items: List[GroceryItem] = []
        for product_id, required_g in required_by_product_id.items():
            product = products_by_id.get(product_id)
            if product is None:
                continue

            owned_g = float(owned_by_product_id.get(product_id, 0.0))
            to_buy_required_g = max(0.0, float(required_g) - owned_g)
            status = "already_have" if to_buy_required_g <= 0 else "needed"
            if exclude_owned and status == "already_have":
                continue

            # Use exact quantity if product allows it (e.g., loose produce sold by weight)
            if product.allows_exact_quantity:
                purchase_g = to_buy_required_g
                waste_g = 0.0
            else:
                purchase_g = GroceryService._match_package_size_g(
                    to_buy_required_g, product.common_package_sizes
                )
                waste_g = max(0.0, purchase_g - to_buy_required_g)
            estimated_cost = GroceryService._estimate_cost(purchase_g, product)

            if estimated_cost is not None:
                total_cost += estimated_cost
                total_cost_has_value = True
            total_waste_g += waste_g

            item = GroceryItem(
                grocery_list_id=grocery_list.id,
                product_id=product.id,
                required_quantity_g=float(required_g),
                purchase_quantity_g=float(purchase_g),
                purchase_unit="g",
                category=product.category,
                estimated_item_cost=estimated_cost,
                estimated_item_waste_g=float(waste_g),
                status=status,
            )
            items.append(item)
            db.add(item)

        grocery_list.total_items = len(items)
        grocery_list.estimated_total_waste_g = float(total_waste_g)
        grocery_list.estimated_total_cost = float(total_cost) if total_cost_has_value else None

        await db.commit()
        await db.refresh(grocery_list)

        return grocery_list
