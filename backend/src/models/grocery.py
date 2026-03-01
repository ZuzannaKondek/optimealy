"""GroceryList and GroceryItem models."""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from src.models.meal_plan import MealPlan
    from src.models.product import Product
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base
from src.models.enums import GroceryItemStatus


class GroceryList(Base):
    """GroceryList model representing a consolidated shopping list for a meal plan."""

    __tablename__ = "grocery_lists"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign Key (One-to-One with MealPlan)
    meal_plan_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meal_plans.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Summary Information
    total_items: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_total_cost: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    estimated_total_waste_g: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)

    # Timestamps
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
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
    meal_plan: Mapped["MealPlan"] = relationship("MealPlan", back_populates="grocery_list")
    items: Mapped[List["GroceryItem"]] = relationship(
        "GroceryItem",
        back_populates="grocery_list",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of GroceryList."""
        return (
            f"<GroceryList(id={self.id}, meal_plan_id={self.meal_plan_id}, "
            f"total_items={self.total_items})>"
        )


class GroceryItem(Base):
    """GroceryItem model representing an individual item in a grocery list."""

    __tablename__ = "grocery_items"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign Keys
    grocery_list_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("grocery_lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Quantity Information
    required_quantity_g: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    purchase_quantity_g: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    purchase_unit: Mapped[str] = mapped_column(String(20), nullable=False)

    # Category (denormalized from product for shopping organization)
    category: Mapped[str] = mapped_column(String(50), nullable=False)

    # Cost and Waste
    estimated_item_cost: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    estimated_item_waste_g: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0.0,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=GroceryItemStatus.NEEDED.value,
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
    grocery_list: Mapped["GroceryList"] = relationship("GroceryList", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="grocery_items")

    # Indexes
    __table_args__ = (
        Index("idx_grocery_items_grocery_list_id", "grocery_list_id"),
        Index("idx_grocery_items_product_id", "product_id"),
    )

    def __repr__(self) -> str:
        """String representation of GroceryItem."""
        return (
            f"<GroceryItem(id={self.id}, grocery_list_id={self.grocery_list_id}, "
            f"product_id={self.product_id}, quantity={self.required_quantity_g}g)>"
        )
