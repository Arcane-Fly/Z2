#!/usr/bin/env python3
"""
Verify Superuser Script - Check if superuser exists in database
"""

import asyncio
import os
import sys

# Add the parent directory to the path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select
from app.database.session import SessionLocal
from app.models.user import User


async def verify_superuser():
    """Verify that the superuser exists in the database."""
    
    username = os.getenv("SUPER_USERNAME")
    email = os.getenv("SUPERUSER_EMAIL")
    
    if not username or not email:
        print("❌ Missing SUPER_USERNAME or SUPERUSER_EMAIL environment variables")
        return False
        
    async with SessionLocal() as db:
        try:
            # Check if user exists
            stmt = select(User).where(User.username == username)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"❌ User '{username}' not found in database")
                return False
                
            print(f"✅ User found: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Full Name: {user.full_name}")
            print(f"   User Type: {user.user_type}")
            print(f"   Active: {user.is_active}")
            print(f"   Superuser: {user.is_superuser}")
            print(f"   Created: {user.created_at}")
            
            if user.is_superuser:
                print("✅ User has superuser privileges")
                return True
            else:
                print("❌ User does not have superuser privileges")
                return False
                
        except Exception as e:
            print(f"❌ Error checking user: {str(e)}")
            return False


async def main():
    print("Z2 Platform - Verify Superuser")
    print("=" * 40)
    
    success = await verify_superuser()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)