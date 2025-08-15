#!/usr/bin/env python3
"""
Database Initialization Script for Z2 Platform

This script initializes the database with proper tables and creates
a default admin user for production deployments.
"""

import asyncio
import os
import sys
from datetime import UTC, datetime
from uuid import uuid4

import structlog
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

# Add the parent directory to the path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.security import PasswordSecurity
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models.user import User

logger = structlog.get_logger(__name__)


async def verify_database_connection() -> bool:
    """Verify database connection and accessibility."""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection verified")
        return True
    except OperationalError as e:
        logger.error("❌ Database connection failed", error=str(e))
        return False
    except Exception as e:
        logger.error("❌ Unexpected database error", error=str(e))
        return False


async def create_tables() -> bool:
    """Create all database tables."""
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created/verified")
        return True
    except Exception as e:
        logger.error("❌ Failed to create database tables", error=str(e))
        return False


async def create_default_admin() -> bool:
    """Create a default admin user if none exists."""
    try:
        password_security = PasswordSecurity()

        async with SessionLocal() as db:
            # Check if any superuser exists
            existing_admin = await db.execute(
                text("SELECT id FROM users WHERE is_superuser = TRUE LIMIT 1")
            )
            if existing_admin.first():
                logger.info("✅ Admin user already exists")
                return True

            # Create default admin user
            default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "changeme123!")

            admin_user = User(
                id=uuid4(),
                username="admin",
                email="admin@z2.ai",
                full_name="Default Administrator",
                hashed_password=password_security.get_password_hash(default_password),
                user_type="admin",
                role="admin",
                is_active=True,
                is_superuser=True,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )

            db.add(admin_user)
            await db.commit()

            logger.info("✅ Default admin user created",
                       username="admin",
                       email="admin@z2.ai",
                       note="Please change the default password")
            return True

    except Exception as e:
        logger.error("❌ Failed to create default admin user", error=str(e))
        return False


async def initialize_database() -> bool:
    """Initialize the complete database setup."""
    logger.info("🚀 Starting database initialization")

    # Step 1: Verify connection
    if not await verify_database_connection():
        return False

    # Step 2: Create tables
    if not await create_tables():
        return False

    # Step 3: Create default admin (only if none exists)
    if not await create_default_admin():
        return False

    logger.info("✅ Database initialization completed successfully")
    return True


async def main():
    """Main initialization function."""
    print("Z2 Platform - Database Initialization")
    print("=" * 50)

    try:
        success = await initialize_database()

        if success:
            print("✅ Database initialization completed successfully!")
            print("\n📝 Next steps:")
            print("1. Update the default admin password")
            print("2. Configure environment variables")
            print("3. Start the application server")
            return 0
        else:
            print("❌ Database initialization failed")
            return 1

    except Exception as e:
        logger.error("❌ Initialization error", error=str(e))
        print(f"❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
