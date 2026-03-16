"""Product alias lookup table."""

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base


if TYPE_CHECKING:
    from src.models.product import Product


class ProductAlias(Base):
    """Alias linking alternative names to canonical products."""

    __tablename__ = "product_aliases"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    alias: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    product_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product: Mapped["Product"] = relationship("Product", back_populates="product_aliases")

    def __repr__(self) -> str:
        return f"<ProductAlias(alias={self.alias!r}, product_id={self.product_id})>"
