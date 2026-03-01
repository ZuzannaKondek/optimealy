"""Grocery list API endpoints."""

from typing import Dict, List, Optional, Set, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.middleware.auth import get_current_user
from src.database.connection import get_db
from src.models.grocery import GroceryList, GroceryItem
from src.models.meal_plan import DailyMenu, Meal
from src.models.recipe import Recipe
from src.models.recipe_ingredient import RecipeIngredient
from src.models.product import Product
from src.models.user import User
from src.services.grocery_service import GroceryService


router = APIRouter(prefix="/meal-plans", tags=["Grocery"])


class GroceryItemResponse(BaseModel):
    item_id: str
    product_id: str
    product_name: str
    category: str
    required_quantity_g: float
    purchase_quantity_g: float
    purchase_unit: str
    estimated_item_cost: Optional[float]
    estimated_item_waste_g: float
    status: str
    used_in_recipes: Optional[List[dict]] = None


class GroceryListResponse(BaseModel):
    grocery_list_id: str
    meal_plan_id: str
    generated_at: str
    total_items: int
    estimated_total_cost: Optional[float]
    estimated_total_waste_g: float
    items: List[GroceryItemResponse]


@router.get("/{plan_id}/grocery", response_model=GroceryListResponse)
async def get_grocery_list(
    plan_id: str,
    group_by: str = Query("category", pattern="^(category|aisle|recipe)$"),
    exclude_owned: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GroceryListResponse:
    """
    Get (and generate if needed) the consolidated grocery list for a meal plan.
    """
    try:
        await GroceryService.generate_grocery_list(
            db,
            plan_id=plan_id,
            user_id=str(current_user.id),
            exclude_owned=exclude_owned,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    stmt = (
        select(GroceryList)
        .where(GroceryList.meal_plan_id == plan_id)
        .options(selectinload(GroceryList.items).selectinload(GroceryItem.product))
    )
    result = await db.execute(stmt)
    grocery_list = result.scalar_one_or_none()
    if grocery_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grocery list not found")

    # Build "used in recipes" map for this plan
    usage_stmt = (
        select(Meal)
        .join(DailyMenu, Meal.daily_menu_id == DailyMenu.id)
        .where(DailyMenu.meal_plan_id == plan_id)
        .options(
            selectinload(Meal.recipe)
            .selectinload(Recipe.recipe_ingredients)
            .selectinload(RecipeIngredient.product)
        )
    )
    usage_result = await db.execute(usage_stmt)
    meals = list(usage_result.scalars().all())

    used_in: Dict[str, Set[Tuple[str, str]]] = {}
    for meal in meals:
        if meal.recipe is None:
            continue
        recipe = meal.recipe
        for ri in recipe.recipe_ingredients:
            pid = str(ri.product_id)
            used_in.setdefault(pid, set()).add((str(recipe.id), recipe.name))

    items: List[GroceryItemResponse] = []
    for item in grocery_list.items:
        product: Optional[Product] = item.product
        used = [
            {"recipe_id": recipe_id, "recipe_name": recipe_name}
            for (recipe_id, recipe_name) in sorted(list(used_in.get(str(item.product_id), set())))
        ]
        items.append(
            GroceryItemResponse(
                item_id=str(item.id),
                product_id=str(item.product_id),
                product_name=product.name if product else "Unknown",
                category=item.category,
                required_quantity_g=float(item.required_quantity_g),
                purchase_quantity_g=float(item.purchase_quantity_g),
                purchase_unit=item.purchase_unit,
                estimated_item_cost=float(item.estimated_item_cost) if item.estimated_item_cost is not None else None,
                estimated_item_waste_g=float(item.estimated_item_waste_g),
                status=item.status,
                used_in_recipes=used or None,
            )
        )

    if group_by == "category":
        items.sort(key=lambda x: (x.category or "", x.product_name or ""))
    else:
        items.sort(key=lambda x: (x.product_name or ""))

    return GroceryListResponse(
        grocery_list_id=str(grocery_list.id),
        meal_plan_id=str(grocery_list.meal_plan_id),
        generated_at=grocery_list.generated_at.isoformat(),
        total_items=grocery_list.total_items,
        estimated_total_cost=float(grocery_list.estimated_total_cost)
        if grocery_list.estimated_total_cost is not None
        else None,
        estimated_total_waste_g=float(grocery_list.estimated_total_waste_g or 0.0),
        items=items,
    )

