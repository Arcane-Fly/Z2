"""
Custom database types that work across different database backends.
"""

from sqlalchemy import JSON, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB


class UniversalJSON(TypeDecorator):
    """
    A JSON type that works with both PostgreSQL (JSONB) and SQLite (JSON).
    This follows agent-os best practices for database compatibility.
    """

    impl = JSON

    def load_dialect_impl(self, dialect):
        """Load the appropriate JSON type based on the database dialect."""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())

    cache_ok = True
