"""Recipe service for querying and filtering recipes."""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.recipe import Recipe
from src.models.recipe_ingredient import RecipeIngredient


class RecipeService:
    """Service for handling recipe queries and filtering."""

    @staticmethod
    async def get_all_recipes(
        db: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Recipe]:
        """
        Get all recipes with pagination.
        
        Args:
            db: Database session
            limit: Maximum number of recipes to return
            offset: Number of recipes to skip
            
        Returns:
            List of Recipe objects
        """
        stmt = (
            select(Recipe)
            .options(
                selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.product)
            )
            .limit(limit)
            .offset(offset)
            .order_by(Recipe.popularity_score.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_recipe_by_id(
        db: AsyncSession,
        recipe_id: str,
    ) -> Optional[Recipe]:
        """
        Get a recipe by its ID.
        
        Args:
            db: Database session
            recipe_id: UUID of the recipe
            
        Returns:
            Recipe object if found, None otherwise
        """
        stmt = (
            select(Recipe)
            .options(
                selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.product)
            )
            .where(Recipe.id == recipe_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def filter_recipes(
        db: AsyncSession,
        meal_types: Optional[List[str]] = None,
        dietary_tags: Optional[List[str]] = None,
        cuisine_types: Optional[List[str]] = None,
        exclude_ingredients: Optional[List[str]] = None,
        include_ingredients: Optional[List[str]] = None,
        max_prep_time: Optional[int] = None,
        max_cook_time: Optional[int] = None,
        difficulty: Optional[str] = None,
        limit: int = 100,
    ) -> List[Recipe]:
        """
        Filter recipes based on various criteria.
        
        Args:
            db: Database session
            meal_types: List of meal types to filter by
            dietary_tags: List of dietary tags to include
            cuisine_types: List of cuisine types to filter by
            exclude_ingredients: List of product IDs to exclude
            include_ingredients: List of product IDs that must be present
            max_prep_time: Maximum preparation time in minutes
            max_cook_time: Maximum cooking time in minutes
            difficulty: Difficulty level ('easy', 'medium', 'hard')
            limit: Maximum number of recipes to return
            
        Returns:
            List of Recipe objects matching the criteria
        """
        stmt = select(Recipe).options(
            selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.product)
        )
        
        conditions = []
        
        # Meal type filter (PostgreSQL array overlap operator)
        if meal_types:
            conditions.append(Recipe.meal_types.op('&&')(meal_types))
        
        # Dietary tags filter (PostgreSQL array overlap operator)
        if dietary_tags:
            conditions.append(Recipe.dietary_tags.op('&&')(dietary_tags))
        
        # Cuisine type filter
        if cuisine_types:
            conditions.append(Recipe.cuisine_type.in_(cuisine_types))
        
        # Exclude ingredients (recipes that use these products)
        if exclude_ingredients:
            exclude_subquery = (
                select(RecipeIngredient.recipe_id)
                .where(RecipeIngredient.product_id.in_(exclude_ingredients))
            )
            conditions.append(~Recipe.id.in_(exclude_subquery))
        
        # Include ingredients (recipes that must use these products)
        if include_ingredients:
            include_subquery = (
                select(RecipeIngredient.recipe_id)
                .where(RecipeIngredient.product_id.in_(include_ingredients))
                .group_by(RecipeIngredient.recipe_id)
                .having(
                    # Must include all specified ingredients
                    func.count(RecipeIngredient.product_id.distinct()) == len(include_ingredients)
                )
            )
            conditions.append(Recipe.id.in_(include_subquery))
        
        # Time filters
        if max_prep_time is not None:
            conditions.append(
                or_(
                    Recipe.prep_time_minutes.is_(None),
                    Recipe.prep_time_minutes <= max_prep_time,
                )
            )
        
        if max_cook_time is not None:
            conditions.append(
                or_(
                    Recipe.cook_time_minutes.is_(None),
                    Recipe.cook_time_minutes <= max_cook_time,
                )
            )
        
        # Difficulty filter
        if difficulty:
            conditions.append(Recipe.difficulty == difficulty)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.order_by(Recipe.popularity_score.desc()).limit(limit)
        
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_recipes_by_ids(
        db: AsyncSession,
        recipe_ids: List[str],
    ) -> List[Recipe]:
        """
        Get multiple recipes by their IDs.
        
        Args:
            db: Database session
            recipe_ids: List of recipe UUIDs
            
        Returns:
            List of Recipe objects
        """
        if not recipe_ids:
            return []
        
        stmt = (
            select(Recipe)
            .options(
                selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.product)
            )
            .where(Recipe.id.in_(recipe_ids))
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def get_single_serving_instructions(recipe: Recipe) -> str:
        """
        Get single-serving preparation instructions.
        
        Prefers stored instructions_single_serving if available,
        otherwise generates by scaling ingredient quantities.
        
        Args:
            recipe: Recipe model
            
        Returns:
            Single-serving preparation instructions
        """
        if recipe.instructions_single_serving:
            return recipe.instructions_single_serving
        
        # Generate by scaling
        if recipe.total_servings == 1.0:
            return recipe.instructions  # Already single-serving
        
        # Scale ingredient quantities in instructions
        scale_factor = 1.0 / recipe.total_servings
        scaled_instructions = RecipeService.scale_recipe_instructions(
            recipe.instructions,
            recipe.total_servings,
            scale_factor
        )
        return scaled_instructions

    @staticmethod
    def scale_recipe_instructions(
        instructions: str,
        original_servings: float,
        scale_factor: float,
    ) -> str:
        """
        Scale recipe instructions by adjusting ingredient quantities.
        
        Simple approach: Add note at top of instructions.
        More sophisticated: Parse instructions and scale each ingredient mention.
        
        Args:
            instructions: Original recipe instructions
            original_servings: Number of servings the recipe makes
            scale_factor: Factor to scale by (1.0 / original_servings for single serving)
            
        Returns:
            Scaled instructions with note
        """
        scaled = f"[Scaled to 1 serving from {original_servings:.1f} servings]\n\n"
        scaled += instructions
        scaled += f"\n\nNote: Use {scale_factor:.2f}x of each ingredient quantity listed above."
        return scaled
