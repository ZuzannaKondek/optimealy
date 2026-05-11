"""rename_sweet_lunch_to_dessert

Revision ID: f1a2b3c4d5e6
Revises: e298c08e1bc0
Create Date: 2026-01-18 16:42:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = 'e298c08e1bc0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Update 'Sweet Lunch' to 'Dessert' in course_type column."""
    
    # Update any existing data with 'Sweet Lunch' to 'Dessert'
    op.execute("""
        UPDATE meals 
        SET course_type = 'Dessert' 
        WHERE course_type = 'Sweet Lunch'
    """)
    
    # Drop the old constraint if it exists
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    constraints = [c['name'] for c in inspector.get_check_constraints('meals')]
    
    if 'chk_meals_course_type' in constraints:
        op.drop_constraint('chk_meals_course_type', 'meals', type_='check')
        
        # Recreate with 'Dessert' instead of 'Sweet Lunch'
        op.create_check_constraint(
            'chk_meals_course_type',
            'meals',
            "course_type IS NULL OR course_type IN ('Breakfast', '2nd Breakfast', 'Dinner', 'Dessert', 'Supper')"
        )


def downgrade() -> None:
    """Revert 'Dessert' back to 'Sweet Lunch'."""
    
    # Update data back to 'Sweet Lunch'
    op.execute("""
        UPDATE meals 
        SET course_type = 'Sweet Lunch' 
        WHERE course_type = 'Dessert'
    """)
    
    # Drop and recreate constraint with 'Sweet Lunch'
    op.drop_constraint('chk_meals_course_type', 'meals', type_='check')
    op.create_check_constraint(
        'chk_meals_course_type',
        'meals',
        "course_type IS NULL OR course_type IN ('Breakfast', '2nd Breakfast', 'Dinner', 'Sweet Lunch', 'Supper')"
    )
