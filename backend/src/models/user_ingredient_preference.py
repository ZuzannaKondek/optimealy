"""UserIngredientPreference model for user ingredient constraints."""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base
from src.models.enums import PreferenceType


class UserIngredientPreference(Base):
    """UserIngredientPreference model for temporary user constraints during plan creation."""

    __tablename__ = "user_ingredient_preferences"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign Keys
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Preference Information
    preference_type: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity_g: Mapped[float] = mapped_column(
        Numeric(10, 2),
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
    user: Mapped["User"] = relationship("User")
    product: Mapped["Product"] = relationship("Product", back_populates="user_preferences")

    # Indexes
    __table_args__ = (
        Index("idx_user_ingredient_preferences_user_id", "user_id"),
        Index("idx_user_ingredient_preferences_product_id", "product_id"),
    )

    def __repr__(self) -> str:
        """String representation of UserIngredientPreference."""
        return (
            f"<UserIngredientPreference(id={self.id}, user_id={self.user_id}, "
            f"product_id={self.product_id}, type={self.preference_type})>"
        )
