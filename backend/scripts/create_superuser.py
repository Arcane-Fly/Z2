#!/usr/bin/env python3
"""
Create Superuser Script for Z2 Platform

This script creates a superuser in the database using environment variables.
It can be run standalone or imported as a module.

Environment Variables Required:
- SUPER_USERNAME: Username for the superuser
- SUPERUSER_EMAIL: Email for the superuser  
- SUPERUSER_PASSWORD: Password for the superuser
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

import structlog

# Add the parent directory to the path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import PasswordSecurity
from app.database.session import SessionLocal, engine
from app.models.user import User

logger = structlog.get_logger(__name__)


async def create_superuser(
    username: str,
    email: str,
    password: str,
    full_name: str = None
) -> bool:
    """
    Create a superuser in the database.
    
    Args:
        username: Username for the superuser
        email: Email address for the superuser
        password: Plain text password (will be hashed)
        full_name: Optional full name for the user
        
    Returns:
        bool: True if user was created, False if user already exists
    """
    password_security = PasswordSecurity()
    
    async with SessionLocal() as db:
        try:
            # Check if user already exists
            stmt = select(User).where(
                (User.username == username) | (User.email == email)
            )
            result = await db.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                if existing_user.username == username:
                    logger.warning(f"User with username '{username}' already exists")
                else:
                    logger.warning(f"User with email '{email}' already exists")
                
                # Update existing user to be superuser if not already
                if not existing_user.is_superuser:
                    existing_user.is_superuser = True
                    existing_user.is_active = True
                    # Update password if provided
                    if password:
                        existing_user.hashed_password = password_security.get_password_hash(password)
                    await db.commit()
                    logger.info(f"Updated existing user '{existing_user.username}' to superuser")
                    return True
                else:
                    logger.info(f"User '{existing_user.username}' is already a superuser")
                    return False
            
            # Validate password strength
            password_validation = password_security.validate_password_strength(password)
            if not password_validation["valid"]:
                logger.error("Password validation failed", errors=password_validation["errors"])
                raise ValueError(f"Password validation failed: {password_validation['errors']}")
            
            # Create new superuser
            hashed_password = password_security.get_password_hash(password)
            
            superuser = User(
                id=uuid4(),
                username=username,
                email=email,
                full_name=full_name or f"Superuser {username}",
                hashed_password=hashed_password,
                user_type="developer",  # Superusers are typically developers
                is_active=True,
                is_superuser=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            db.add(superuser)
            await db.commit()
            await db.refresh(superuser)
            
            logger.info(
                f"Superuser created successfully",
                user_id=str(superuser.id),
                username=superuser.username,
                email=superuser.email
            )
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create superuser: {str(e)}")
            raise


async def create_superuser_from_env() -> bool:
    """
    Create superuser from environment variables.
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Get environment variables
    username = os.getenv("SUPER_USERNAME")
    email = os.getenv("SUPERUSER_EMAIL") 
    password = os.getenv("SUPERUSER_PASSWORD")
    
    if not all([username, email, password]):
        missing = []
        if not username:
            missing.append("SUPER_USERNAME")
        if not email:
            missing.append("SUPERUSER_EMAIL")
        if not password:
            missing.append("SUPERUSER_PASSWORD")
        
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        return False
    
    logger.info(f"Creating superuser from environment variables", username=username, email=email)
    
    try:
        return await create_superuser(
            username=username,
            email=email,
            password=password,
            full_name=f"Superuser {username}"
        )
    except Exception as e:
        logger.error(f"Failed to create superuser from environment: {str(e)}")
        return False


async def main():
    """Main function to create superuser when run as script."""
    print("Z2 Platform - Create Superuser Script")
    print("=" * 50)
    
    try:
        # Try to create superuser from environment variables
        success = await create_superuser_from_env()
        
        if success:
            print("✅ Superuser created successfully!")
            return 0
        else:
            print("❌ Failed to create superuser")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)