"""RecipeIngredient model linking recipes to products."""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Numeric, Boolean, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base


class RecipeIngredient(Base):
    """RecipeIngredient model representing the many-to-many relationship between recipes and products."""

    __tablename__ = "recipe_ingredients"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign Keys
    recipe_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Quantity Information
    quantity_value: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    quantity_unit: Mapped[str] = mapped_column(String(20), nullable=False)

    # Flags
    is_essential: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

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
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="recipe_ingredients")
    product: Mapped["Product"] = relationship("Product", back_populates="recipe_ingredients")

    # Constraints
    __table_args__ = (
        UniqueConstraint("recipe_id", "product_id", name="uq_recipe_product"),
        Index("idx_recipe_ingredient_recipe", "recipe_id"),
        Index("idx_recipe_ingredient_product", "product_id"),
    )

    def __repr__(self) -> str:
        """String representation of RecipeIngredient."""
        return (
            f"<RecipeIngredient(recipe_id={self.recipe_id}, "
            f"product_id={self.product_id}, quantity={self.quantity_value} {self.quantity_unit})>"
        )
