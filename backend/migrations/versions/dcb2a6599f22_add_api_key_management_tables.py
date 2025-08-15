"""Add API key management tables

Revision ID: dcb2a6599f22
Revises: 7ff22b4ef3a3
Create Date: 2025-08-05 02:53:35.219937

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'dcb2a6599f22'
down_revision: str | Sequence[str] | None = '7ff22b4ef3a3'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('key_hash', sa.String(length=128), nullable=False),
        sa.Column('key_prefix', sa.String(length=10), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('allowed_endpoints', sa.JSON(), nullable=True),
        sa.Column('rate_limit_per_hour', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_hash')
    )
    op.create_index(op.f('ix_api_keys_id'), 'api_keys', ['id'], unique=False)
    op.create_index(op.f('ix_api_keys_name'), 'api_keys', ['name'], unique=False)
    op.create_index(op.f('ix_api_keys_key_hash'), 'api_keys', ['key_hash'], unique=True)
    op.create_index(op.f('ix_api_keys_key_prefix'), 'api_keys', ['key_prefix'], unique=False)
    op.create_index(op.f('ix_api_keys_user_id'), 'api_keys', ['user_id'], unique=False)
    op.create_index(op.f('ix_api_keys_created_at'), 'api_keys', ['created_at'], unique=False)

    # Create api_key_usage table
    op.create_table(
        'api_key_usage',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('api_key_id', sa.UUID(), nullable=False),
        sa.Column('endpoint', sa.String(length=200), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('request_size_bytes', sa.Integer(), nullable=True),
        sa.Column('response_size_bytes', sa.Integer(), nullable=True),
        sa.Column('error_type', sa.String(length=100), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['api_key_id'], ['api_keys.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_key_usage_id'), 'api_key_usage', ['id'], unique=False)
    op.create_index(op.f('ix_api_key_usage_api_key_id'), 'api_key_usage', ['api_key_id'], unique=False)
    op.create_index(op.f('ix_api_key_usage_endpoint'), 'api_key_usage', ['endpoint'], unique=False)
    op.create_index(op.f('ix_api_key_usage_status_code'), 'api_key_usage', ['status_code'], unique=False)
    op.create_index(op.f('ix_api_key_usage_created_at'), 'api_key_usage', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_api_key_usage_created_at'), table_name='api_key_usage')
    op.drop_index(op.f('ix_api_key_usage_status_code'), table_name='api_key_usage')
    op.drop_index(op.f('ix_api_key_usage_endpoint'), table_name='api_key_usage')
    op.drop_index(op.f('ix_api_key_usage_api_key_id'), table_name='api_key_usage')
    op.drop_index(op.f('ix_api_key_usage_id'), table_name='api_key_usage')
    op.drop_table('api_key_usage')

    op.drop_index(op.f('ix_api_keys_created_at'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_user_id'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_key_prefix'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_key_hash'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_name'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_id'), table_name='api_keys')
    op.drop_table('api_keys')
