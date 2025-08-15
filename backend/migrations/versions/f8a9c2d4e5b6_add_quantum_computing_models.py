"""Add quantum computing models

Revision ID: f8a9c2d4e5b6
Revises: c7bb81d27d15
Create Date: 2025-07-28 10:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f8a9c2d4e5b6'
down_revision: str | Sequence[str] | None = 'c7bb81d27d15'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create quantum_tasks table
    op.create_table('quantum_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('task_description', sa.Text(), nullable=False),
        sa.Column('collapse_strategy', sa.String(length=20), nullable=False),
        sa.Column('metrics_config', postgresql.JSONB(), nullable=False),
        sa.Column('max_parallel_executions', sa.Integer(), nullable=False),
        sa.Column('timeout_seconds', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('progress', sa.Float(), nullable=False),
        sa.Column('collapsed_result', postgresql.JSONB(), nullable=True),
        sa.Column('final_metrics', postgresql.JSONB(), nullable=True),
        sa.Column('execution_summary', postgresql.JSONB(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_execution_time', sa.Float(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quantum_tasks_id'), 'quantum_tasks', ['id'], unique=False)
    op.create_index(op.f('ix_quantum_tasks_name'), 'quantum_tasks', ['name'], unique=False)
    op.create_index(op.f('ix_quantum_tasks_status'), 'quantum_tasks', ['status'], unique=False)
    op.create_index(op.f('ix_quantum_tasks_user_id'), 'quantum_tasks', ['user_id'], unique=False)

    # Create quantum_variations table
    op.create_table('quantum_variations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('prompt_modifications', postgresql.JSONB(), nullable=False),
        sa.Column('parameters', postgresql.JSONB(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['quantum_tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quantum_variations_task_id'), 'quantum_variations', ['task_id'], unique=False)

    # Create quantum_thread_results table
    op.create_table('quantum_thread_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('thread_name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('result', postgresql.JSONB(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_time', sa.Float(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('completeness', sa.Float(), nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('total_score', sa.Float(), nullable=True),
        sa.Column('detailed_metrics', postgresql.JSONB(), nullable=False),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('provider_used', sa.String(length=50), nullable=True),
        sa.Column('model_used', sa.String(length=100), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('variation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['quantum_tasks.id'], ),
        sa.ForeignKeyConstraint(['variation_id'], ['quantum_variations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quantum_thread_results_status'), 'quantum_thread_results', ['status'], unique=False)
    op.create_index(op.f('ix_quantum_thread_results_task_id'), 'quantum_thread_results', ['task_id'], unique=False)
    op.create_index(op.f('ix_quantum_thread_results_variation_id'), 'quantum_thread_results', ['variation_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_quantum_thread_results_variation_id'), table_name='quantum_thread_results')
    op.drop_index(op.f('ix_quantum_thread_results_task_id'), table_name='quantum_thread_results')
    op.drop_index(op.f('ix_quantum_thread_results_status'), table_name='quantum_thread_results')
    op.drop_table('quantum_thread_results')

    op.drop_index(op.f('ix_quantum_variations_task_id'), table_name='quantum_variations')
    op.drop_table('quantum_variations')

    op.drop_index(op.f('ix_quantum_tasks_user_id'), table_name='quantum_tasks')
    op.drop_index(op.f('ix_quantum_tasks_status'), table_name='quantum_tasks')
    op.drop_index(op.f('ix_quantum_tasks_name'), table_name='quantum_tasks')
    op.drop_index(op.f('ix_quantum_tasks_id'), table_name='quantum_tasks')
    op.drop_table('quantum_tasks')
