"""consolidate_meal_types

Revision ID: g2h3i4j5k6l7
Revises: f1a2b3c4d5e6
Create Date: 2026-01-18 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'g2h3i4j5k6l7'
down_revision: Union[str, None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Consolidate meal type system to single field with new values."""
    
    # Step 1: Check if course_type column exists and has data
    conn = op.get_bind()
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'meals' AND column_name = 'course_type'
        )
    """))
    course_type_exists = result.scalar()
    
    if course_type_exists:
        # Map course_type to lowercase meal_type if course_type has data
        op.execute(text("""
            UPDATE meals 
            SET meal_type = CASE 
                WHEN course_type = 'Breakfast' THEN 'breakfast'
                WHEN course_type = '2nd Breakfast' THEN 'second_breakfast'
                WHEN course_type = 'Dinner' THEN 'dinner'
                WHEN course_type = 'Dessert' THEN 'dessert'
                WHEN course_type = 'Supper' THEN 'supper'
                ELSE meal_type
            END
            WHERE course_type IS NOT NULL
        """))
        
        # Drop course_type column
        op.drop_column('meals', 'course_type')
    
    # Step 2: Update any old meal_type values to new values (if meals exist)
    op.execute(text("""
        UPDATE meals 
        SET meal_type = CASE 
            WHEN meal_type = 'lunch' THEN 'dinner'
            WHEN meal_type = 'snack' THEN 'dessert'
            ELSE meal_type
        END
        WHERE meal_type IN ('lunch', 'snack')
    """))
    
    # Step 3: Drop old constraint if it exists (may not exist depending on db state)
    try:
        op.drop_constraint('chk_meals_course_type', 'meals', type_='check')
    except:
        pass  # Constraint might not exist
    
    # Step 4: Add new check constraint for meal_type
    op.create_check_constraint(
        'chk_meals_meal_type',
        'meals',
        "meal_type IN ('breakfast', 'second_breakfast', 'dinner', 'dessert', 'supper')"
    )


def downgrade() -> None:
    """Revert to old meal type system."""
    
    # Step 1: Drop new constraint
    op.drop_constraint('chk_meals_meal_type', 'meals', type_='check')
    
    # Step 2: Add course_type column back
    op.add_column('meals', sa.Column('course_type', sa.String(50), nullable=True))
    
    # Step 3: Map meal_type back to old values
    op.execute(text("""
        UPDATE meals 
        SET meal_type = CASE 
            WHEN meal_type = 'second_breakfast' THEN 'lunch'
            WHEN meal_type = 'dessert' THEN 'snack'
            ELSE meal_type
        END
    """))
    
    # Step 4: Recreate old constraint
    op.create_check_constraint(
        'chk_meals_course_type',
        'meals',
        "course_type IS NULL OR course_type IN ('Breakfast', '2nd Breakfast', 'Dinner', 'Dessert', 'Supper')"
    )
