"""Add model routing and usage tracking tables

Revision ID: 7ff22b4ef3a3
Revises: f8a9c2d4e5b6
Create Date: 2025-08-05 02:40:25.858573

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ff22b4ef3a3'
down_revision: Union[str, Sequence[str], None] = 'f8a9c2d4e5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create model_routing_policies table
    op.create_table(
        'model_routing_policies',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('task_type', sa.String(length=50), nullable=False),
        sa.Column('model_id', sa.String(length=100), nullable=False),
        sa.Column('fallback_models', sa.JSON(), nullable=True),
        sa.Column('max_cost_per_request', sa.Float(), nullable=True),
        sa.Column('max_latency_ms', sa.Integer(), nullable=True),
        sa.Column('required_capabilities', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_routing_policies_id'), 'model_routing_policies', ['id'], unique=False)
    op.create_index(op.f('ix_model_routing_policies_name'), 'model_routing_policies', ['name'], unique=False)
    op.create_index(op.f('ix_model_routing_policies_task_type'), 'model_routing_policies', ['task_type'], unique=False)
    op.create_index(op.f('ix_model_routing_policies_created_at'), 'model_routing_policies', ['created_at'], unique=False)

    # Create model_usage_tracking table
    op.create_table(
        'model_usage_tracking',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('model_id', sa.String(length=100), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('task_type', sa.String(length=50), nullable=True),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.Column('input_tokens', sa.Integer(), nullable=True),
        sa.Column('output_tokens', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.Float(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('was_cached', sa.Boolean(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error_type', sa.String(length=100), nullable=True),
        sa.Column('request_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_usage_tracking_id'), 'model_usage_tracking', ['id'], unique=False)
    op.create_index(op.f('ix_model_usage_tracking_model_id'), 'model_usage_tracking', ['model_id'], unique=False)
    op.create_index(op.f('ix_model_usage_tracking_provider'), 'model_usage_tracking', ['provider'], unique=False)
    op.create_index(op.f('ix_model_usage_tracking_task_type'), 'model_usage_tracking', ['task_type'], unique=False)
    op.create_index(op.f('ix_model_usage_tracking_user_id'), 'model_usage_tracking', ['user_id'], unique=False)
    op.create_index(op.f('ix_model_usage_tracking_created_at'), 'model_usage_tracking', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_model_usage_tracking_created_at'), table_name='model_usage_tracking')
    op.drop_index(op.f('ix_model_usage_tracking_user_id'), table_name='model_usage_tracking')
    op.drop_index(op.f('ix_model_usage_tracking_task_type'), table_name='model_usage_tracking')
    op.drop_index(op.f('ix_model_usage_tracking_provider'), table_name='model_usage_tracking')
    op.drop_index(op.f('ix_model_usage_tracking_model_id'), table_name='model_usage_tracking')
    op.drop_index(op.f('ix_model_usage_tracking_id'), table_name='model_usage_tracking')
    op.drop_table('model_usage_tracking')
    
    op.drop_index(op.f('ix_model_routing_policies_created_at'), table_name='model_routing_policies')
    op.drop_index(op.f('ix_model_routing_policies_task_type'), table_name='model_routing_policies')
    op.drop_index(op.f('ix_model_routing_policies_name'), table_name='model_routing_policies')
    op.drop_index(op.f('ix_model_routing_policies_id'), table_name='model_routing_policies')
    op.drop_table('model_routing_policies')
