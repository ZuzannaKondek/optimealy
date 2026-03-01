"""User model for authentication and profile management."""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import uuid4
from sqlalchemy import String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base
from src.models.enums import ThemeType, UnitPreference

if TYPE_CHECKING:
    from src.models.meal_completion import MealCompletion


class User(Base):
    """User model for authentication and preferences."""

    __tablename__ = "users"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # User Preferences
    language_preference: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en",
    )
    theme_preference: Mapped[ThemeType] = mapped_column(
        SQLEnum(ThemeType, name="themetype", create_type=False),
        nullable=False,
        default=ThemeType.SYSTEM,
    )
    unit_preference: Mapped[UnitPreference] = mapped_column(
        SQLEnum(UnitPreference, name="unitpreference", create_type=False),
        nullable=False,
        default=UnitPreference.METRIC,
    )
    notification_settings: Mapped[dict] = mapped_column(
        JSONB,
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
    meal_completions: Mapped[List["MealCompletion"]] = relationship(
        "MealCompletion",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email={self.email})>"
