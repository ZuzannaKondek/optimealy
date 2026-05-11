"""add plan execution

Revision ID: j5k6l7m8n9o0
Revises: i4j5k6l7m8n9
Create Date: 2026-01-18 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'j5k6l7m8n9o0'
down_revision: Union[str, None] = 'i4j5k6l7m8n9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add execution_status to meal_plans
    op.add_column('meal_plans', sa.Column(
        'execution_status',
        sa.String(20),
        nullable=False,
        server_default='draft',
        comment='Plan execution state: draft, active, completed, cancelled'
    ))
    op.create_index('ix_meal_plans_execution_status', 'meal_plans', ['execution_status'])
    
    # Create unique constraint: only one active plan per user
    op.create_index(
        'idx_user_active_plan',
        'meal_plans',
        ['user_id'],
        unique=True,
        postgresql_where=sa.text("execution_status = 'active'")
    )
    
    # Create meal_completions table
    op.create_table(
        'meal_completions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('meal_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meals.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('ingredients_deducted', postgresql.JSONB, nullable=False, server_default='{}'),
    )
    op.create_index('ix_meal_completions_id', 'meal_completions', ['id'])
    op.create_index('ix_meal_completions_meal_id', 'meal_completions', ['meal_id'])
    op.create_index('ix_meal_completions_user_id', 'meal_completions', ['user_id'])


def downgrade() -> None:
    # Drop meal_completions table
    op.drop_index('ix_meal_completions_user_id', 'meal_completions')
    op.drop_index('ix_meal_completions_meal_id', 'meal_completions')
    op.drop_index('ix_meal_completions_id', 'meal_completions')
    op.drop_table('meal_completions')
    
    # Drop unique constraint
    op.drop_index('idx_user_active_plan', 'meal_plans')
    
    # Drop execution_status
    op.drop_index('ix_meal_plans_execution_status', 'meal_plans')
    op.drop_column('meal_plans', 'execution_status')
