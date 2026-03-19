"""Merge migration to combine product and pantry branches.

Revision ID: m9n0o1p2q3r4
Revises: d1f2g3h4i5j6, j7k8l9m0n1o2
Create Date: 2026-03-16 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "m9n0o1p2q3r4"
down_revision: Union[Sequence[str], None] = ("d1f2g3h4i5j6", "j7k8l9m0n1o2")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
