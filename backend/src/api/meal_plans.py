"""Meal Plans API endpoints."""
from typing import List, Optional, Dict, Any
from datetime import date
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db
from src.models.user import User
from src.models.meal_plan import MealPlan, DailyMenu, Meal
from src.models.recipe import Recipe
from src.models.recipe_ingredient import RecipeIngredient
from src.models.product import Product
from src.api.middleware.auth import get_current_user
from src.services.meal_plan_service import MealPlanService
from src.services.recipe_service import RecipeService
from src.services.plan_execution_service import PlanExecutionService
from src.core.exceptions import OptimizationError, ValidationError, DishConstraintError
from src.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/meal-plans", tags=["Meal Plans"])


# Request/Response Models
class IngredientConstraint(BaseModel):
    """Ingredient constraint for plan creation."""

    product_id: str
    quantity_g: float = Field(..., gt=0)


class CreateMealPlanRequest(BaseModel):
    """Request to create a meal plan."""

    name: str = Field(..., min_length=1, max_length=255)
    duration_days: int = Field(..., ge=1, le=30)
    target_calories_per_day: int = Field(..., ge=800, le=5000)
    target_protein_g: Optional[float] = Field(None, gt=0)
    target_carbs_g: Optional[float] = Field(None, gt=0)
    target_fat_g: Optional[float] = Field(None, gt=0)
    start_date: Optional[date] = None
    selected_meal_types: Optional[List[str]] = None
    ingredients_to_have: Optional[List[IngredientConstraint]] = None
    ingredients_to_want: Optional[List[str]] = None
    ingredients_to_exclude: Optional[List[str]] = None
    dietary_tags: Optional[List[str]] = None
    cuisine_types: Optional[List[str]] = None


class CreateMealPlanResponse(BaseModel):
    """Response after creating a meal plan."""

    message: str
    plan_id: str
    status_url: str


class MealPlanSummaryResponse(BaseModel):
    """Summary of a meal plan."""

    plan_id: str
    name: Optional[str] = None
    created_at: str
    start_date: str
    duration_days: int
    target_calories_per_day: int
    dishes_per_day: Optional[int] = None
    optimization_status: str
    execution_status: str = "draft"
    estimated_food_waste_g: Optional[float]
    pantry_additions_g: Optional[float]
    waste_reduction_percentage: Optional[float]
    estimated_total_cost: Optional[float]

    class Config:
        from_attributes = True


class RecipeDetailResponse(BaseModel):
    """Recipe detail information for meal responses."""

    id: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    cooking_time_minutes: Optional[int] = None
    prep_time_minutes: Optional[int] = None
    difficulty_level: Optional[str] = None
    instructions_single_serving: Optional[str] = None
    ingredients: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class MealResponse(BaseModel):
    """Meal information."""

    meal_id: str
    meal_type: str
    recipe_id: str
    recipe_name: str
    servings: float
    dish_weight_g: Optional[float] = None
    calculated_nutritional_info: dict
    recipe: Optional[RecipeDetailResponse] = None

    class Config:
        from_attributes = True


class DailyMenuResponse(BaseModel):
    """Daily menu information."""

    day_number: int
    menu_date: str
    actual_calories: int
    actual_protein_g: float
    actual_carbs_g: float
    actual_fat_g: float
    variance_from_target: Optional[dict] = None
    meals: List[MealResponse]

    class Config:
        from_attributes = True


class DayDetailResponse(BaseModel):
    """Detailed day information within a meal plan."""

    plan_id: str
    daily_menu: DailyMenuResponse


class MealPlanDetailResponse(BaseModel):
    """Detailed meal plan information."""

    plan_id: str
    name: Optional[str] = None
    user_id: str
    created_at: str
    start_date: str
    duration_days: int
    target_calories_per_day: int
    dishes_per_day: Optional[int] = None
    target_protein_g: Optional[float]
    target_carbs_g: Optional[float]
    target_fat_g: Optional[float]
    optimization_status: str
    execution_status: str = "draft"
    algorithm_execution_time_s: Optional[float]
    estimated_food_waste_g: Optional[float]
    pantry_additions_g: Optional[float]
    waste_reduction_percentage: Optional[float]
    estimated_total_cost: Optional[float]
    daily_menus: List[DailyMenuResponse]

    class Config:
        from_attributes = True


class OptimizationStatusResponse(BaseModel):
    """Optimization status response."""

    plan_id: str
    status: str
    progress_percentage: Optional[int] = None
    message: Optional[str] = None


# Endpoints
def _variance_pct(actual: float, target: Optional[float]) -> Optional[float]:
    if target is None or target == 0:
        return None
    return (actual - target) / target * 100.0


@router.post("/", response_model=CreateMealPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_meal_plan(
    request: CreateMealPlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CreateMealPlanResponse:
    """
    Create a new optimized meal plan.
    
    This endpoint triggers the optimization algorithm to generate a meal plan
    that minimizes food waste while meeting nutritional constraints.
    """
    # Log incoming request for debugging
    request_log = (
        f"=== CREATE MEAL PLAN REQUEST ===\n"
        f"User ID: {current_user.id}\n"
        f"Name: {request.name}\n"
        f"Duration Days: {request.duration_days}\n"
        f"Target Calories/Day: {request.target_calories_per_day}\n"
        f"Target Protein (g): {request.target_protein_g}\n"
        f"Target Carbs (g): {request.target_carbs_g}\n"
        f"Target Fat (g): {request.target_fat_g}\n"
        f"Start Date: {request.start_date}\n"
        f"Selected Meal Types: {request.selected_meal_types}\n"
        f"Ingredients to Have: {request.ingredients_to_have}\n"
        f"Ingredients to Want: {request.ingredients_to_want}\n"
        f"Ingredients to Exclude: {request.ingredients_to_exclude}\n"
        f"Dietary Tags: {request.dietary_tags}\n"
        f"Cuisine Types: {request.cuisine_types}\n"
        f"================================"
    )
    print(request_log)  # Use print to ensure it shows in Docker logs
    logger.info(request_log)
    
    try:
        # Convert ingredients_to_have to dict format
        ingredients_to_have = None
        if request.ingredients_to_have:
            ingredients_to_have = [
                {"product_id": item.product_id, "quantity_g": item.quantity_g}
                for item in request.ingredients_to_have
            ]
        
        # Ensure name is taken from the parsed request body (required for plan creation)
        plan_name = (request.name or "").strip()
        if not plan_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plan name is required",
            )

        meal_plan = await MealPlanService.create_meal_plan(
            db=db,
            user=current_user,
            name=plan_name,
            duration_days=request.duration_days,
            target_calories_per_day=request.target_calories_per_day,
            target_protein_g=request.target_protein_g,
            target_carbs_g=request.target_carbs_g,
            target_fat_g=request.target_fat_g,
            start_date=request.start_date,
            selected_meal_types=request.selected_meal_types,
            ingredients_to_have=ingredients_to_have,
            ingredients_to_want=request.ingredients_to_want,
            ingredients_to_exclude=request.ingredients_to_exclude,
            dietary_tags=request.dietary_tags,
            cuisine_types=request.cuisine_types,
        )
        
        logger.info(f"Meal plan created: id={meal_plan.id}, name={getattr(meal_plan, 'name', None)!r}")

        return CreateMealPlanResponse(
            message="Meal plan generation initiated",
            plan_id=str(meal_plan.id),
            status_url=f"/api/v1/meal-plans/{meal_plan.id}/status",
        )
        
    except ValueError as e:
        logger.error(
            f"Validation error creating meal plan for user {current_user.id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except DishConstraintError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "DISH_CONSTRAINT_VIOLATION",
                "message": e.message,
                "details": e.details,
            },
        )
    except RuntimeError as e:
        logger.error(
            f"Runtime error creating meal plan for user {current_user.id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(
            f"Unexpected error creating meal plan for user {current_user.id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the meal plan",
        )


@router.get("/", response_model=List[MealPlanSummaryResponse])
async def get_meal_plans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[MealPlanSummaryResponse]:
    """
    Get all meal plans for the current user.
    
    Supports pagination and filtering by optimization status.
    """
    meal_plans = await MealPlanService.get_user_meal_plans(
        db=db,
        user_id=str(current_user.id),
        limit=limit,
        offset=offset,
        status=status_filter,
    )
    
    return [
        MealPlanSummaryResponse(
            plan_id=str(plan.id),
            name=plan.name,
            created_at=plan.created_at.isoformat(),
            start_date=plan.start_date.isoformat(),
            duration_days=plan.duration_days,
            target_calories_per_day=plan.target_calories_per_day,
            dishes_per_day=plan.dishes_per_day,
            optimization_status=plan.optimization_status,
            execution_status=plan.execution_status,
            estimated_food_waste_g=float(plan.estimated_food_waste_g) if plan.estimated_food_waste_g else None,
            pantry_additions_g=float(plan.pantry_additions_g) if plan.pantry_additions_g else None,
            waste_reduction_percentage=float(plan.waste_reduction_percentage) if plan.waste_reduction_percentage else None,
            estimated_total_cost=float(plan.estimated_total_cost) if plan.estimated_total_cost else None,
        )
        for plan in meal_plans
    ]


@router.get("/active")
async def get_active_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Optional[Dict[str, Any]]:
    """
    Get the user's active meal plan, if any.
    """
    plan = await PlanExecutionService.get_active_plan(
        db=db,
        user_id=current_user.id
    )
    
    if not plan:
        return None
    
    return {
        "id": str(plan.id),
        "start_date": plan.start_date.isoformat(),
        "duration_days": plan.duration_days,
        "execution_status": plan.execution_status
    }


@router.get("/{plan_id}", response_model=MealPlanDetailResponse)
async def get_meal_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MealPlanDetailResponse:
    """
    Get detailed information for a specific meal plan.
    
    Includes all daily menus and meals.
    """
    meal_plan = await MealPlanService.get_meal_plan_by_id(
        db=db,
        plan_id=plan_id,
        user_id=str(current_user.id),
    )
    
    if meal_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )
    
    # Load daily menus with meals and recipe details
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    
    stmt = (
        select(DailyMenu)
        .where(DailyMenu.meal_plan_id == meal_plan.id)
        .options(
            selectinload(DailyMenu.meals)
            .selectinload(Meal.recipe)
            .selectinload(Recipe.recipe_ingredients)
            .selectinload(RecipeIngredient.product)
        )
        .order_by(DailyMenu.day_number)
    )
    result = await db.execute(stmt)
    daily_menus = list(result.scalars().all())
    
    # Build response
    daily_menus_response = []
    for menu in daily_menus:
        meals_response = []
        for meal in menu.meals:
            recipe_detail = None
            selected_meal_types = meal_plan.user_constraints.get("selected_meal_types", [])
            if meal.recipe and selected_meal_types:
                # Get single-serving instructions for dish-based plans
                instructions_single_serving = RecipeService.get_single_serving_instructions(meal.recipe)
                
                # Build ingredients list
                ingredients_list = []
                if meal.recipe.recipe_ingredients:
                    for ing in meal.recipe.recipe_ingredients:
                        ingredients_list.append({
                            "name": ing.product.name if ing.product else "Unknown",
                            "quantity": float(ing.quantity_value) if ing.quantity_value else 0.0,
                            "unit": ing.quantity_unit or "g",
                        })
                
                recipe_detail = RecipeDetailResponse(
                    id=str(meal.recipe.id),
                    name=meal.recipe.name,
                    description=meal.recipe.description,
                    image_url=None,
                    cooking_time_minutes=meal.recipe.cook_time_minutes,
                    prep_time_minutes=meal.recipe.prep_time_minutes,
                    difficulty_level=meal.recipe.difficulty,
                    instructions_single_serving=instructions_single_serving,
                    ingredients=ingredients_list if ingredients_list else None,
                )
            
            meals_response.append(MealResponse(
                meal_id=str(meal.id),
                meal_type=meal.meal_type,
                recipe_id=str(meal.recipe_id),
                recipe_name=meal.recipe.name if meal.recipe else "Unknown",
                servings=float(meal.servings),
                dish_weight_g=float(meal.dish_weight_g) if meal.dish_weight_g else None,
                calculated_nutritional_info=meal.calculated_nutritional_info,
                recipe=recipe_detail,
            ))
        
        daily_menus_response.append(DailyMenuResponse(
            day_number=menu.day_number,
            menu_date=menu.menu_date.isoformat(),
            actual_calories=menu.actual_calories,
            actual_protein_g=float(menu.actual_protein_g),
            actual_carbs_g=float(menu.actual_carbs_g),
            actual_fat_g=float(menu.actual_fat_g),
            variance_from_target={
                "calorie_variance_pct": _variance_pct(
                    float(menu.actual_calories),
                    float(meal_plan.target_calories_per_day),
                ),
                "protein_variance_pct": _variance_pct(
                    float(menu.actual_protein_g),
                    float(meal_plan.target_protein_g) if meal_plan.target_protein_g else None,
                ),
                "carbs_variance_pct": _variance_pct(
                    float(menu.actual_carbs_g),
                    float(meal_plan.target_carbs_g) if meal_plan.target_carbs_g else None,
                ),
                "fat_variance_pct": _variance_pct(
                    float(menu.actual_fat_g),
                    float(meal_plan.target_fat_g) if meal_plan.target_fat_g else None,
                ),
            },
            meals=meals_response,
        ))
    
    return MealPlanDetailResponse(
        plan_id=str(meal_plan.id),
        name=meal_plan.name,
        user_id=str(meal_plan.user_id),
        created_at=meal_plan.created_at.isoformat(),
        start_date=meal_plan.start_date.isoformat(),
        duration_days=meal_plan.duration_days,
        target_calories_per_day=meal_plan.target_calories_per_day,
        dishes_per_day=meal_plan.dishes_per_day,
        target_protein_g=float(meal_plan.target_protein_g) if meal_plan.target_protein_g else None,
        target_carbs_g=float(meal_plan.target_carbs_g) if meal_plan.target_carbs_g else None,
        target_fat_g=float(meal_plan.target_fat_g) if meal_plan.target_fat_g else None,
        optimization_status=meal_plan.optimization_status,
        execution_status=meal_plan.execution_status,
        algorithm_execution_time_s=float(meal_plan.algorithm_execution_time_s) if meal_plan.algorithm_execution_time_s else None,
        estimated_food_waste_g=float(meal_plan.estimated_food_waste_g) if meal_plan.estimated_food_waste_g else None,
        pantry_additions_g=float(meal_plan.pantry_additions_g) if meal_plan.pantry_additions_g else None,
        waste_reduction_percentage=float(meal_plan.waste_reduction_percentage) if meal_plan.waste_reduction_percentage else None,
        estimated_total_cost=float(meal_plan.estimated_total_cost) if meal_plan.estimated_total_cost else None,
        daily_menus=daily_menus_response,
    )


@router.get("/{plan_id}/days/{day_number}", response_model=DayDetailResponse)
async def get_meal_plan_day(
    plan_id: str,
    day_number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DayDetailResponse:
    """
    Get detailed information for a specific day in a meal plan.
    """
    meal_plan = await MealPlanService.get_meal_plan_by_id(
        db=db,
        plan_id=plan_id,
        user_id=str(current_user.id),
    )
    if meal_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )
    if day_number < 1 or day_number > meal_plan.duration_days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"day_number must be between 1 and {meal_plan.duration_days}",
        )

    from sqlalchemy.orm import selectinload
    from sqlalchemy import select

    from src.models.recipe_ingredient import RecipeIngredient
    from src.models.product import Product
    
    stmt = (
        select(DailyMenu)
        .where(DailyMenu.meal_plan_id == meal_plan.id)
        .where(DailyMenu.day_number == day_number)
        .options(
            selectinload(DailyMenu.meals)
            .selectinload(Meal.recipe)
            .selectinload(Recipe.recipe_ingredients)
            .selectinload(RecipeIngredient.product)
        )
    )
    result = await db.execute(stmt)
    daily_menu = result.scalars().first()
    if daily_menu is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily menu not found",
        )

    meals_response: List[MealResponse] = []
    for meal in daily_menu.meals:
        recipe_detail = None
        if meal.recipe:
            # Get single-serving instructions for dish-based plans
            instructions_single_serving = None
            if meal_plan.dishes_per_day is not None:
                instructions_single_serving = RecipeService.get_single_serving_instructions(meal.recipe)
            
            # Build ingredients list
            ingredients_list = []
            if meal.recipe.recipe_ingredients:
                for ing in meal.recipe.recipe_ingredients:
                    ingredients_list.append({
                        "name": ing.product.name if ing.product else "Unknown",
                        "quantity": float(ing.quantity_value) if ing.quantity_value else 0.0,
                        "unit": ing.quantity_unit or "g",
                    })
            
            recipe_detail = RecipeDetailResponse(
                id=str(meal.recipe.id),
                name=meal.recipe.name,
                description=meal.recipe.description,
                image_url=None,  # TODO: Add image_url to Recipe model if needed
                cooking_time_minutes=meal.recipe.cook_time_minutes,
                prep_time_minutes=meal.recipe.prep_time_minutes,
                difficulty_level=meal.recipe.difficulty,
                instructions_single_serving=instructions_single_serving,
                ingredients=ingredients_list if ingredients_list else None,
            )
        
        meals_response.append(
            MealResponse(
                meal_id=str(meal.id),
                meal_type=meal.meal_type,
                recipe_id=str(meal.recipe_id),
                recipe_name=meal.recipe.name if meal.recipe else "Unknown",
                servings=float(meal.servings),
                dish_weight_g=float(meal.dish_weight_g) if meal.dish_weight_g else None,
                calculated_nutritional_info=meal.calculated_nutritional_info,
                recipe=recipe_detail,
            )
        )

    daily_menu_response = DailyMenuResponse(
        day_number=daily_menu.day_number,
        menu_date=daily_menu.menu_date.isoformat(),
        actual_calories=daily_menu.actual_calories,
        actual_protein_g=float(daily_menu.actual_protein_g),
        actual_carbs_g=float(daily_menu.actual_carbs_g),
        actual_fat_g=float(daily_menu.actual_fat_g),
        variance_from_target={
            "calorie_variance_pct": _variance_pct(
                float(daily_menu.actual_calories),
                float(meal_plan.target_calories_per_day),
            ),
            "protein_variance_pct": _variance_pct(
                float(daily_menu.actual_protein_g),
                float(meal_plan.target_protein_g) if meal_plan.target_protein_g else None,
            ),
            "carbs_variance_pct": _variance_pct(
                float(daily_menu.actual_carbs_g),
                float(meal_plan.target_carbs_g) if meal_plan.target_carbs_g else None,
            ),
            "fat_variance_pct": _variance_pct(
                float(daily_menu.actual_fat_g),
                float(meal_plan.target_fat_g) if meal_plan.target_fat_g else None,
            ),
        },
        meals=meals_response,
    )

    return DayDetailResponse(plan_id=str(meal_plan.id), daily_menu=daily_menu_response)


@router.get("/{plan_id}/status", response_model=OptimizationStatusResponse)
async def get_optimization_status(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OptimizationStatusResponse:
    """
    Get the current optimization status of a meal plan.
    """
    meal_plan = await MealPlanService.get_meal_plan_by_id(
        db=db,
        plan_id=plan_id,
        user_id=str(current_user.id),
    )
    
    if meal_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )
    
    # Determine progress percentage based on status
    progress_percentage = None
    message = None
    
    if meal_plan.optimization_status == "pending":
        progress_percentage = 10
        message = "Preparing optimization..."
    elif meal_plan.optimization_status == "in_progress":
        progress_percentage = 50
        message = "Optimizing recipes for nutritional balance"
    elif meal_plan.optimization_status == "completed":
        progress_percentage = 100
        message = "Meal plan generated successfully"
    elif meal_plan.optimization_status == "failed":
        progress_percentage = 0
        message = "Optimization failed"
    
    return OptimizationStatusResponse(
        plan_id=str(meal_plan.id),
        status=meal_plan.optimization_status,
        progress_percentage=progress_percentage,
        message=message,
    )


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a meal plan.
    """
    deleted = await MealPlanService.delete_meal_plan(
        db=db,
        plan_id=plan_id,
        user_id=str(current_user.id),
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )


# Plan Execution Endpoints

@router.post("/{plan_id}/activate")
async def activate_meal_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Activate a meal plan for execution.
    
    This will:
    - Add all grocery items to the user's pantry
    - Mark the plan as active
    - Only one plan can be active at a time
    """
    try:
        from uuid import UUID
        result = await PlanExecutionService.activate_plan(
            db=db,
            plan_id=UUID(plan_id),
            user_id=current_user.id
        )
        
        return {
            "message": "Plan activated successfully",
            "plan": {
                "id": str(result["plan"].id),
                "execution_status": result["plan"].execution_status
            },
            "pantry_updated": True
        }
    except ValueError as e:
        if "already have an active plan" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{plan_id}/cancel")
async def cancel_meal_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Cancel an active meal plan.
    
    Pantry remains unchanged.
    """
    try:
        from uuid import UUID
        plan = await PlanExecutionService.cancel_plan(
            db=db,
            plan_id=UUID(plan_id),
            user_id=current_user.id
        )
        
        return {
            "message": "Plan cancelled successfully",
            "plan": {
                "id": str(plan.id),
                "execution_status": plan.execution_status
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{plan_id}/today")
async def get_today_meals(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Get today's meals from a plan with completion status.
    """
    from uuid import UUID
    meals = await PlanExecutionService.get_today_meals(
        db=db,
        plan_id=UUID(plan_id),
        user_id=current_user.id
    )
    
    result = []
    for meal_data in meals:
        meal = meal_data["meal"]
        # Transform nutritional info to match frontend expectations
        nutritional_info = meal.calculated_nutritional_info
        result.append({
            "id": str(meal.id),
            "meal_type": meal.meal_type,
            "recipe_id": str(meal.recipe_id),
            "servings": float(meal.servings),
            "is_completed": meal_data["is_completed"],
            "completed_at": meal_data["completed_at"].isoformat() if meal_data["completed_at"] else None,
            "nutritional_info": {
                "calories": nutritional_info.get("calories", 0),
                "protein_g": nutritional_info.get("protein", 0),
                "carbs_g": nutritional_info.get("carbs", 0),
                "fat_g": nutritional_info.get("fat", 0)
            }
        })
    
    return result


@router.post("/meals/{meal_id}/complete")
async def complete_meal(
    meal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Mark a meal as completed.
    
    This will automatically deduct the ingredients from the user's pantry.
    """
    try:
        from uuid import UUID
        result = await PlanExecutionService.complete_meal(
            db=db,
            meal_id=UUID(meal_id),
            user_id=current_user.id
        )
        
        return {
            "message": "Meal completed successfully",
            "completion": {
                "id": str(result["completion"].id),
                "completed_at": result["completion"].completed_at.isoformat()
            },
            "pantry_updated": True
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/meals/{meal_id}/complete")
async def uncomplete_meal(
    meal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Uncomplete a meal (undo completion).
    
    Only allowed within 24 hours of completion.
    Restores ingredient quantities to pantry.
    """
    try:
        from uuid import UUID
        await PlanExecutionService.uncomplete_meal(
            db=db,
            meal_id=UUID(meal_id),
            user_id=current_user.id
        )
        
        return {
            "message": "Meal uncompleted successfully",
            "pantry_updated": True
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
