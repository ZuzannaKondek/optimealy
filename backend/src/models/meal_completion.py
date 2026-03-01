"""MealCompletion model for tracking consumed meals."""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base

if TYPE_CHECKING:
    from src.models.meal_plan import Meal
    from src.models.user import User


class MealCompletion(Base):
    """MealCompletion model representing a consumed meal."""

    __tablename__ = "meal_completions"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Foreign Keys
    meal_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Completion Data
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    ingredients_deducted: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Snapshot of ingredient quantities deducted: {product_id: quantity_g}"
    )

    # Relationships
    meal: Mapped["Meal"] = relationship("Meal", back_populates="completions")
    user: Mapped["User"] = relationship("User", back_populates="meal_completions")

    def __repr__(self) -> str:
        return f"<MealCompletion(id={self.id}, meal_id={self.meal_id}, completed_at={self.completed_at})>"
