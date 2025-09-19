"""
Database session and connection management for Z2.
"""

from collections.abc import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = structlog.get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# Create async engine
engine = create_async_engine(
    settings.database_url_async,
    echo=settings.database_echo,
    future=True,
)

# Create session factory
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database connection (table creation handled by migrations)."""
    try:
        async with engine.begin() as conn:
            # Temporarily comment out model imports to isolate table creation issue
            # from app.models import (  # noqa: F401
            #     agent, 
            #     user, 
            #     workflow, 
            #     consent, 
            #     session,
            #     model_routing,
            #     api_key
            # )

            # Verify database connection instead of creating tables
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))

        logger.info("Database connection verified successfully")
    except Exception as e:
        logger.error("Failed to connect to database", error=str(e))
        if settings.debug:
            logger.warning(
                "Database connection failed in debug mode, continuing without database"
            )
        else:
            raise
