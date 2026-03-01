"""Merge heads

Revision ID: b8dcc4d3c79a
Revises: a1b2c3d4e5f7, k6l7m8n9o0p1
Create Date: 2026-03-01 19:54:40.548628

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8dcc4d3c79a'
down_revision: Union[str, None] = ('a1b2c3d4e5f7', 'k6l7m8n9o0p1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
