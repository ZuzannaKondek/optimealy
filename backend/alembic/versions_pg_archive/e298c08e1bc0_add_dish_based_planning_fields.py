"""add_dish_based_planning_fields

Revision ID: e298c08e1bc0
Revises: 83b7c722a3b0
Create Date: 2026-01-13 14:03:17.481180

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e298c08e1bc0'
down_revision: Union[str, None] = '83b7c722a3b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add dishes_per_day to meal_plans table (if not exists)
    from sqlalchemy import inspect
    from sqlalchemy.engine import Connection
    
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Check and add dishes_per_day to meal_plans
    meal_plans_columns = [col['name'] for col in inspector.get_columns('meal_plans')]
    if 'dishes_per_day' not in meal_plans_columns:
        op.add_column('meal_plans', sa.Column('dishes_per_day', sa.Integer(), nullable=True))
    
    # Check and add columns to meals
    meals_columns = [col['name'] for col in inspector.get_columns('meals')]
    if 'dish_weight_g' not in meals_columns:
        op.add_column('meals', sa.Column('dish_weight_g', sa.Numeric(precision=10, scale=2), nullable=True))
    if 'course_type' not in meals_columns:
        op.add_column('meals', sa.Column('course_type', sa.String(length=50), nullable=True))
    
    # Add check constraint for course_type (if not exists)
    constraints = [c['name'] for c in inspector.get_check_constraints('meals')]
    if 'chk_meals_course_type' not in constraints:
        op.create_check_constraint(
            'chk_meals_course_type',
            'meals',
            "course_type IS NULL OR course_type IN ('Breakfast', '2nd Breakfast', 'Dinner', 'Dessert', 'Supper')"
        )
    
    # Check and add instructions_single_serving to recipes
    recipes_columns = [col['name'] for col in inspector.get_columns('recipes')]
    if 'instructions_single_serving' not in recipes_columns:
        op.add_column('recipes', sa.Column('instructions_single_serving', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove instructions_single_serving from recipes
    op.drop_column('recipes', 'instructions_single_serving')
    
    # Remove check constraint and columns from meals
    op.drop_constraint('chk_meals_course_type', 'meals', type_='check')
    op.drop_column('meals', 'course_type')
    op.drop_column('meals', 'dish_weight_g')
    
    # Remove dishes_per_day from meal_plans
    op.drop_column('meal_plans', 'dishes_per_day')
