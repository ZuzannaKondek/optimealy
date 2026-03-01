"""remove_hardcoded_recipe_nutrition

Revision ID: a1b2c3d4e5f7
Revises: f1a2b3c4d5e6
Create Date: 2026-01-18 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f7'
down_revision: Union[str, None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove hardcoded nutritional_info_per_serving column.
    
    Nutritional information is now calculated dynamically from recipe ingredients.
    """
    op.drop_column('recipes', 'nutritional_info_per_serving')


def downgrade() -> None:
    """Restore nutritional_info_per_serving column with empty default."""
    op.add_column(
        'recipes',
        sa.Column(
            'nutritional_info_per_serving',
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb")
        )
    )
