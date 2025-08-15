"""Initial migration

Revision ID: 762c4b3ee5d9
Revises:
Create Date: 2025-07-26 14:23:32.735618

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '762c4b3ee5d9'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=True),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('user_type', sa.String(length=20), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('avatar_url', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create agents table
    op.create_table('agents',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('role', sa.String(length=50), nullable=False),
    sa.Column('system_prompt', sa.Text(), nullable=False),
    sa.Column('model_preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('tools', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('skills', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('temperature', sa.Float(), nullable=False),
    sa.Column('max_tokens', sa.Integer(), nullable=False),
    sa.Column('timeout_seconds', sa.Integer(), nullable=False),
    sa.Column('max_iterations', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('total_executions', sa.Integer(), nullable=False),
    sa.Column('total_tokens_used', sa.Integer(), nullable=False),
    sa.Column('average_response_time', sa.Float(), nullable=True),
    sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('last_used', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agents_created_by'), 'agents', ['created_by'], unique=False)
    op.create_index(op.f('ix_agents_id'), 'agents', ['id'], unique=False)
    op.create_index(op.f('ix_agents_name'), 'agents', ['name'], unique=False)

    # Create workflows table
    op.create_table('workflows',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('goal', sa.Text(), nullable=False),
    sa.Column('agent_team', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('workflow_graph', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('execution_policy', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('input_schema', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('output_schema', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('current_step', sa.String(length=100), nullable=True),
    sa.Column('execution_context', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('intermediate_results', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('execution_duration_seconds', sa.Integer(), nullable=True),
    sa.Column('total_tokens_used', sa.Integer(), nullable=False),
    sa.Column('total_cost_usd', sa.Float(), nullable=False),
    sa.Column('success_rate', sa.Float(), nullable=True),
    sa.Column('is_template', sa.Boolean(), nullable=False),
    sa.Column('template_category', sa.String(length=50), nullable=True),
    sa.Column('version', sa.String(length=20), nullable=False),
    sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflows_created_by'), 'workflows', ['created_by'], unique=False)
    op.create_index(op.f('ix_workflows_id'), 'workflows', ['id'], unique=False)
    op.create_index(op.f('ix_workflows_name'), 'workflows', ['name'], unique=False)

    # Create workflow_executions table
    op.create_table('workflow_executions',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('input_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('output_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('execution_log', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('duration_seconds', sa.Integer(), nullable=True),
    sa.Column('tokens_used', sa.Integer(), nullable=False),
    sa.Column('cost_usd', sa.Float(), nullable=False),
    sa.Column('executed_by', postgresql.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['executed_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_executions_id'), 'workflow_executions', ['id'], unique=False)
    op.create_index(op.f('ix_workflow_executions_workflow_id'), 'workflow_executions', ['workflow_id'], unique=False)
    op.create_index(op.f('ix_workflow_executions_executed_by'), 'workflow_executions', ['executed_by'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_workflow_executions_executed_by'), table_name='workflow_executions')
    op.drop_index(op.f('ix_workflow_executions_workflow_id'), table_name='workflow_executions')
    op.drop_index(op.f('ix_workflow_executions_id'), table_name='workflow_executions')
    op.drop_table('workflow_executions')
    op.drop_index(op.f('ix_workflows_name'), table_name='workflows')
    op.drop_index(op.f('ix_workflows_id'), table_name='workflows')
    op.drop_index(op.f('ix_workflows_created_by'), table_name='workflows')
    op.drop_table('workflows')
    op.drop_index(op.f('ix_agents_name'), table_name='agents')
    op.drop_index(op.f('ix_agents_id'), table_name='agents')
    op.drop_index(op.f('ix_agents_created_by'), table_name='agents')
    op.drop_table('agents')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
