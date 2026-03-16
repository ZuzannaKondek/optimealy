"""Fix missing canonical_key column.

Revision ID: n2p3q4r5s6t7
Revises: m9n0o1p2q3r4
Create Date: 2026-03-16 00:00:00.000000

"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import unicodedata


# revision identifiers, used by Alembic.
revision: str = "n2p3q4r5s6t7"
down_revision: Union[str, None] = "m9n0o1p2q3r4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def canonicalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", (text or "").lower())
    return "".join(ch for ch in normalized if ch.isalnum())


def upgrade() -> None:
    # Add canonical_key column if it doesn't exist
    op.add_column(
        "products",
        sa.Column("canonical_key", sa.String(length=100), nullable=True),
    )

    # Create product_aliases table if it doesn't exist
    op.create_table(
        "product_aliases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("alias", sa.String(length=100), nullable=False),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_product_aliases_alias", "product_aliases", ["alias"], unique=True)
    op.create_index(
        "ix_product_aliases_product_id", "product_aliases", ["product_id"], unique=False
    )

    # Populate canonical keys
    connection = op.get_bind()
    result = connection.execute(sa.text("SELECT id, name FROM products"))
    seen_counts: dict[str, int] = {}

    for product_id, name in result.fetchall():
        raw_value = name or ""
        base = canonicalize(raw_value) or raw_value.lower() or str(product_id)
        count = seen_counts.get(base, 0)
        canonical = base if count == 0 else f"{base}-{count + 1}"
        seen_counts[base] = count + 1

        connection.execute(
            sa.text("UPDATE products SET canonical_key = :canonical WHERE id = :id"),
            {"canonical": canonical, "id": product_id},
        )

        connection.execute(
            sa.text(
                "INSERT INTO product_aliases (id, alias, product_id) VALUES (:id, :alias, :product_id)"
            ),
            {"id": str(uuid4()), "alias": canonical, "product_id": product_id},
        )

    # Make canonical_key NOT NULL
    op.alter_column(
        "products",
        "canonical_key",
        existing_type=sa.String(length=100),
        nullable=False,
    )

    op.create_index(
        "idx_products_canonical_key",
        "products",
        ["canonical_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("idx_products_canonical_key", table_name="products")
    op.alter_column(
        "products",
        "canonical_key",
        existing_type=sa.String(length=100),
        nullable=True,
    )
    op.drop_table("product_aliases")
    op.drop_column("products", "canonical_key")
