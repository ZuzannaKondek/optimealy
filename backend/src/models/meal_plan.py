"""MealPlan, DailyMenu, and Meal models."""

from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from src.models.grocery import GroceryList
    from src.models.meal_completion import MealCompletion
from sqlalchemy import String, Integer, Numeric, Date, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base
from src.models.enums import OptimizationStatus


class MealPlan(Base):
    """MealPlan model representing a generated optimized meal plan."""

    __tablename__ = "meal_plans"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Foreign Key
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Plan Configuration
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default=None)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    dishes_per_day: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=None)

    # Nutritional Targets
    target_calories_per_day: Mapped[int] = mapped_column(Integer, nullable=False)
    target_protein_g: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    target_carbs_g: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    target_fat_g: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)

    # User Constraints
    user_constraints: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    # Optimization Status
    optimization_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=OptimizationStatus.PENDING.value,
        index=True,
    )

    # Execution Status
    execution_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="draft",
        index=True,
        comment="Plan execution state: draft, active, completed, cancelled",
    )

    # Optimization Metrics
    algorithm_execution_time_s: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    estimated_food_waste_g: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="Perishable food waste in grams"
    )
    waste_reduction_percentage: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    pantry_additions_g: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Shelf-stable leftovers auto-added to pantry in grams",
    )
    estimated_total_cost: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    daily_menus: Mapped[List["DailyMenu"]] = relationship(
        "DailyMenu",
        back_populates="meal_plan",
        cascade="all, delete-orphan",
        order_by="DailyMenu.day_number",
    )
    grocery_list: Mapped[Optional["GroceryList"]] = relationship(
        "GroceryList",
        back_populates="meal_plan",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("idx_meal_plan_user_id", "user_id"),
        Index("idx_meal_plan_created_at", "created_at"),
        Index("idx_meal_plan_status", "optimization_status"),
    )

    def __repr__(self) -> str:
        """String representation of MealPlan."""
        return (
            f"<MealPlan(id={self.id}, user_id={self.user_id}, "
            f"duration={self.duration_days} days, status={self.optimization_status})>"
        )


class DailyMenu(Base):
    """DailyMenu model representing a single day's meals within a meal plan."""

    __tablename__ = "daily_menus"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign Key
    meal_plan_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meal_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Day Information
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    menu_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Actual Nutritional Values (calculated from meals)
    actual_calories: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_protein_g: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    actual_carbs_g: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    actual_fat_g: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

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
    meal_plan: Mapped["MealPlan"] = relationship("MealPlan", back_populates="daily_menus")
    meals: Mapped[List["Meal"]] = relationship(
        "Meal",
        back_populates="daily_menu",
        cascade="all, delete-orphan",
        order_by="Meal.meal_type",
    )

    # Indexes
    __table_args__ = (
        Index("idx_daily_menu_meal_plan_id", "meal_plan_id"),
        Index("idx_daily_menu_day_number", "day_number"),
    )

    def __repr__(self) -> str:
        """String representation of DailyMenu."""
        return (
            f"<DailyMenu(id={self.id}, meal_plan_id={self.meal_plan_id}, "
            f"day={self.day_number}, calories={self.actual_calories})>"
        )


class Meal(Base):
    """Meal model representing a single meal within a daily menu."""

    __tablename__ = "meals"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign Keys
    daily_menu_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("daily_menus.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipe_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recipes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Meal Information
    meal_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of meal: breakfast, second_breakfast, dinner, dessert, or supper",
    )
    servings: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    dish_weight_g: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, default=None
    )

    # Calculated Nutritional Information (for this meal)
    calculated_nutritional_info: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
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
    daily_menu: Mapped["DailyMenu"] = relationship("DailyMenu", back_populates="meals")
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="meals")
    completions: Mapped[List["MealCompletion"]] = relationship(
        "MealCompletion", back_populates="meal", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_meals_daily_menu_id", "daily_menu_id"),
        Index("idx_meals_recipe_id", "recipe_id"),
    )

    def __repr__(self) -> str:
        """String representation of Meal."""
        return (
            f"<Meal(id={self.id}, daily_menu_id={self.daily_menu_id}, "
            f"recipe_id={self.recipe_id}, type={self.meal_type}, servings={self.servings})>"
        )
