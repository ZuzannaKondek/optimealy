"""add expiry_date to user_pantry_items

Revision ID: j7k8l9m0n1o2
Revises: i4j5k6l7m8n9
Create Date: 2026-03-01 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "j7k8l9m0n1o2"
down_revision: Union[str, None] = "i4j5k6l7m8n9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add optional expiry_date column to user_pantry_items table
    op.add_column("user_pantry_items", sa.Column("expiry_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("user_pantry_items", "expiry_date")
