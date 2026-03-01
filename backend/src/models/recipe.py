"""Recipe model for the recipe database."""
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING, Dict
from uuid import uuid4
import logging

if TYPE_CHECKING:
    from src.models.recipe_ingredient import RecipeIngredient
    from src.models.meal_plan import Meal
from sqlalchemy import String, Text, Integer, Float, DateTime, ARRAY, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base
from src.models.enums import MealType, RecipeDifficulty, DietaryTag
from src.utils.unitConversion import convert_to_grams

logger = logging.getLogger(__name__)


class Recipe(Base):
    """Recipe model representing a recipe in the database."""

    __tablename__ = "recipes"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)

    # Classification
    meal_types: Mapped[List[str]] = mapped_column(
        ARRAY(String(50)),
        nullable=False,
    )
    cuisine_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    dietary_tags: Mapped[List[str]] = mapped_column(
        ARRAY(String(50)),
        nullable=False,
        default=list,
    )

    # Timing
    prep_time_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cook_time_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Servings
    total_servings: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    serving_size_unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    serving_size_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    instructions_single_serving: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default=None)

    # Metadata
    difficulty: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
    )
    popularity_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    recipe_ingredients: Mapped[List["RecipeIngredient"]] = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    meals: Mapped[List["Meal"]] = relationship(
        "Meal",
        back_populates="recipe",
    )

    # Indexes
    __table_args__ = (
        Index("idx_recipe_meal_types", "meal_types", postgresql_using="gin"),
        Index("idx_recipe_dietary_tags", "dietary_tags", postgresql_using="gin"),
        Index("idx_recipe_popularity", "popularity_score"),
    )

    @property
    def nutritional_info_per_serving(self) -> Dict[str, float]:
        """
        Calculate nutritional information per serving from ingredients.
        
        Returns:
            Dictionary with calories, protein, carbs, fat, and fiber per serving
        """
        if not self.recipe_ingredients:
            logger.warning(f"Recipe {self.name} has no ingredients")
            return {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}
        
        total_cal = total_protein = total_carbs = total_fat = total_fiber = 0.0
        missing_products = []
        
        for ingredient in self.recipe_ingredients:
            if not ingredient.product:
                missing_products.append(str(ingredient.product_id))
                continue
            
            # Convert quantity to grams
            quantity_g = convert_to_grams(
                float(ingredient.quantity_value),
                ingredient.quantity_unit
            )
            
            # Calculate nutrition based on per-100g values
            multiplier = quantity_g / 100.0
            nutr = ingredient.product.nutritional_info_per_100g
            
            total_cal += nutr.get('calories', 0) * multiplier
            total_protein += nutr.get('protein', 0) * multiplier
            total_carbs += nutr.get('carbs', 0) * multiplier
            total_fat += nutr.get('fat', 0) * multiplier
            total_fiber += nutr.get('fiber', 0) * multiplier
        
        if missing_products:
            logger.warning(
                f"Recipe {self.name} (id={self.id}) missing products: {missing_products}"
            )
        
        # Divide by servings to get per-serving values
        servings = max(self.total_servings, 0.1)  # Prevent division by zero
        
        return {
            'calories': round(total_cal / servings),
            'protein': round(total_protein / servings, 1),
            'carbs': round(total_carbs / servings, 1),
            'fat': round(total_fat / servings, 1),
            'fiber': round(total_fiber / servings, 1),
        }

    def __repr__(self) -> str:
        """String representation of Recipe."""
        return f"<Recipe(id={self.id}, name={self.name!r})>"
