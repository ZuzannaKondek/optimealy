"""Add allows_exact_quantity to products

Revision ID: c9edd5e6f8a1
Revises: b8dcc4d3c79a
Create Date: 2026-03-01 19:55:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c9edd5e6f8a1"
down_revision: Union[str, None] = "b8dcc4d3c79a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("allows_exact_quantity", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("products", "allows_exact_quantity")
