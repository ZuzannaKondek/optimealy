"""add pantry additions field

Revision ID: i4j5k6l7m8n9
Revises: h3i4j5k6l7m8
Create Date: 2026-01-18 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'i4j5k6l7m8n9'
down_revision: Union[str, None] = 'h3i4j5k6l7m8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add pantry_additions_g field to meal_plans table
    op.add_column('meal_plans', sa.Column('pantry_additions_g', sa.Numeric(10, 2), nullable=True))


def downgrade() -> None:
    op.drop_column('meal_plans', 'pantry_additions_g')
