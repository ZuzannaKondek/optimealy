"""Product model for the ingredient/product database."""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from src.models.recipe_ingredient import RecipeIngredient
    from src.models.grocery import GroceryItem
    from src.models.user_ingredient_preference import UserIngredientPreference
    from src.models.product_alias import ProductAlias
from sqlalchemy import String, Text, Integer, Numeric, DateTime, Index, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base
from src.models.enums import ProductCategory, Perishability


class Product(Base):
    """Product model representing an ingredient/product in the database."""

    __tablename__ = "products"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    canonical_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Nutritional Information (per 100g)
    nutritional_info_per_100g: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    # Package Information
    common_package_sizes: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    allows_exact_quantity: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )
    standard_unit: Mapped[str] = mapped_column(String(20), nullable=False)

    # Pricing (optional)
    price_per_unit: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)

    # Shelf Life
    shelf_life_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    perishability: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="moderate",
    )
    storage_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Unit Conversions
    unit_conversions: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
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
        back_populates="product",
    )
    grocery_items: Mapped[List["GroceryItem"]] = relationship(
        "GroceryItem",
        back_populates="product",
    )
    user_preferences: Mapped[List["UserIngredientPreference"]] = relationship(
        "UserIngredientPreference",
        back_populates="product",
    )
    product_aliases: Mapped[List["ProductAlias"]] = relationship(
        "ProductAlias",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("idx_product_perishability", "perishability"),
    )

    def __repr__(self) -> str:
        """String representation of Product."""
        return f"<Product(id={self.id}, name={self.name!r}, category={self.category})>"
