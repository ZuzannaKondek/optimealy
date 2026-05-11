"""Add canonical product keys and aliases.

Revision ID: d1f2g3h4i5j6
Revises: b8dcc4d3c79a
Create Date: 2026-03-16 00:00:00.000000

"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import unicodedata


# revision identifiers, used by Alembic.
revision: str = "d1f2g3h4i5j6"
down_revision: Union[str, Sequence[str], None] = "c9edd5e6f8a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def canonicalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", (text or "").lower())
    return "".join(ch for ch in normalized if ch.isalnum())


def _populate_canonical_keys() -> None:
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


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("canonical_key", sa.String(length=100), nullable=True),
    )

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

    _populate_canonical_keys()

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

    op.drop_index("ix_product_aliases_alias", table_name="product_aliases")
    op.drop_index("ix_product_aliases_product_id", table_name="product_aliases")
    op.drop_table("product_aliases")

    op.drop_column("products", "canonical_key")
