"""Seed default roles and permissions

Revision ID: c7bb81d27d15
Revises: b32d1e47ba53
Create Date: 2025-07-27 00:34:37.296933

"""
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c7bb81d27d15'
down_revision: str | Sequence[str] | None = 'b32d1e47ba53'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Define permissions table for inserts
    permissions_table = sa.table('permissions',
        sa.column('id', postgresql.UUID),
        sa.column('name', sa.String),
        sa.column('description', sa.String),
        sa.column('resource', sa.String),
        sa.column('action', sa.String),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime),
    )

    # Define roles table for inserts
    roles_table = sa.table('roles',
        sa.column('id', postgresql.UUID),
        sa.column('name', sa.String),
        sa.column('description', sa.String),
        sa.column('is_system_role', sa.Boolean),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime),
    )

    # Define role_permissions table for inserts
    role_permissions_table = sa.table('role_permissions',
        sa.column('role_id', postgresql.UUID),
        sa.column('permission_id', postgresql.UUID),
    )

    now = datetime.now(UTC)

    # Insert default permissions
    permissions_data = [
        # User permissions
        ('users:read', 'Read user information', 'users', 'read'),
        ('users:write', 'Create and update users', 'users', 'write'),
        ('users:delete', 'Delete users', 'users', 'delete'),

        # Agent permissions
        ('agents:read', 'Read agent information', 'agents', 'read'),
        ('agents:write', 'Create and update agents', 'agents', 'write'),
        ('agents:delete', 'Delete agents', 'agents', 'delete'),
        ('agents:execute', 'Execute agent tasks', 'agents', 'execute'),

        # Workflow permissions
        ('workflows:read', 'Read workflow information', 'workflows', 'read'),
        ('workflows:write', 'Create and update workflows', 'workflows', 'write'),
        ('workflows:delete', 'Delete workflows', 'workflows', 'delete'),
        ('workflows:execute', 'Execute workflows', 'workflows', 'execute'),

        # System permissions
        ('system:admin', 'Full system administration', 'system', 'admin'),
        ('system:manage', 'System management', 'system', 'manage'),
    ]

    permission_ids = {}
    for name, description, resource, action in permissions_data:
        perm_id = uuid.uuid4()
        permission_ids[name] = perm_id
        op.execute(
            permissions_table.insert().values(
                id=perm_id,
                name=name,
                description=description,
                resource=resource,
                action=action,
                created_at=now,
                updated_at=now,
            )
        )

    # Insert default roles
    roles_data = [
        ('admin', 'System Administrator with full access', True, True),
        ('manager', 'Platform Manager with broad access', True, True),
        ('developer', 'Developer with agent and workflow access', True, True),
        ('operator', 'Operator with execution access', True, True),
        ('viewer', 'Read-only access to resources', True, True),
    ]

    role_ids = {}
    for name, description, is_system_role, is_active in roles_data:
        role_id = uuid.uuid4()
        role_ids[name] = role_id
        op.execute(
            roles_table.insert().values(
                id=role_id,
                name=name,
                description=description,
                is_system_role=is_system_role,
                is_active=is_active,
                created_at=now,
                updated_at=now,
            )
        )

    # Define role-permission mappings
    role_permission_mappings = {
        'admin': [
            'users:read', 'users:write', 'users:delete',
            'agents:read', 'agents:write', 'agents:delete', 'agents:execute',
            'workflows:read', 'workflows:write', 'workflows:delete', 'workflows:execute',
            'system:admin', 'system:manage'
        ],
        'manager': [
            'users:read', 'users:write',
            'agents:read', 'agents:write', 'agents:execute',
            'workflows:read', 'workflows:write', 'workflows:execute',
            'system:manage'
        ],
        'developer': [
            'users:read',
            'agents:read', 'agents:write', 'agents:execute',
            'workflows:read', 'workflows:write', 'workflows:execute',
        ],
        'operator': [
            'users:read',
            'agents:read', 'agents:execute',
            'workflows:read', 'workflows:execute',
        ],
        'viewer': [
            'users:read',
            'agents:read',
            'workflows:read',
        ],
    }

    # Insert role-permission relationships
    for role_name, permission_names in role_permission_mappings.items():
        role_id = role_ids[role_name]
        for permission_name in permission_names:
            permission_id = permission_ids[permission_name]
            op.execute(
                role_permissions_table.insert().values(
                    role_id=role_id,
                    permission_id=permission_id,
                )
            )


def downgrade() -> None:
    """Downgrade schema."""
    # Clean up role-permission relationships
    op.execute("DELETE FROM role_permissions")

    # Clean up roles
    op.execute("DELETE FROM roles WHERE is_system_role = true")

    # Clean up permissions
    op.execute("DELETE FROM permissions")
