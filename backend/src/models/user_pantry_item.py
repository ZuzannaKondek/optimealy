"""User Pantry Item Model

Tracks which ingredients users have in their pantry/fridge.
Used to reduce waste calculations by accounting for existing inventory.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.database.connection import Base


class UserPantryItem(Base):
    """
    Model representing an ingredient a user has in their pantry.
    
    Used to track user's existing inventory so meal plans can account
    for what they already have, reducing waste calculations.
    """
    
    __tablename__ = "user_pantry_items"
    
    # Primary Key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid()
    )
    
    # Foreign Keys
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Quantity (in grams or ml)
    quantity_g: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Quantity in grams (or ml for liquids)"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    # user: Mapped["User"] = relationship("User", back_populates="pantry_items")
    # product: Mapped["Product"] = relationship("Product")
    
    def __repr__(self) -> str:
        return f"<UserPantryItem(user_id={self.user_id}, product_id={self.product_id}, quantity_g={self.quantity_g})>"
