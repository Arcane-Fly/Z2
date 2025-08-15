#!/usr/bin/env python3
"""
Validate Railway environment variables before deployment.

This script validates the CORS_ORIGINS environment variable format
to prevent deployment failures due to configuration issues.
"""

import json
import os
import sys


def validate_cors_origins() -> bool:
    """Validate CORS_ORIGINS environment variable format."""
    cors_env = os.getenv("CORS_ORIGINS", "")

    if not cors_env:
        print("ℹ️  CORS_ORIGINS environment variable not set, will use defaults")
        return True

    try:
        # Test the same parsing logic as our Settings class
        if cors_env.strip().startswith("[") and cors_env.strip().endswith("]"):
            # JSON array format
            origins = json.loads(cors_env)
            if not isinstance(origins, list):
                raise ValueError("CORS_ORIGINS must be a list when using JSON format")

            # Filter out empty strings
            origins = [str(origin).strip() for origin in origins if origin]

            if not origins:
                print("⚠️  Empty CORS origins array, will use defaults")
            else:
                print(f"✅ CORS_ORIGINS valid JSON array ({len(origins)} origins): {origins}")
        else:
            # Comma-separated format
            origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]
            if not origins:
                print("⚠️  Empty CORS origins string, will use defaults")
            else:
                print(f"✅ CORS_ORIGINS valid comma-separated ({len(origins)} origins): {origins}")

        # Validate URL formats
        for origin in origins:
            if not (origin.startswith('http://') or origin.startswith('https://')):
                print(f"⚠️  Warning: Origin may be invalid (missing protocol): {origin}")

        return True

    except json.JSONDecodeError as e:
        print(f"❌ CORS_ORIGINS JSON parsing failed: {e}")
        print(f"   Value: {cors_env}")
        print("   Expected format: JSON array like '[\"https://domain.com\"]' or comma-separated like 'https://domain.com,http://localhost:3000'")
        return False
    except Exception as e:
        print(f"❌ CORS_ORIGINS validation failed: {e}")
        return False


def validate_database_url() -> bool:
    """Validate DATABASE_URL format."""
    db_url = os.getenv("DATABASE_URL", "")

    if not db_url:
        print("ℹ️  DATABASE_URL not set, will use default")
        return True

    if db_url.startswith(("postgresql://", "postgresql+asyncpg://", "sqlite://", "sqlite+aiosqlite://")):
        print(f"✅ DATABASE_URL format valid: {db_url.split('@')[0]}@...")
        return True
    else:
        print(f"⚠️  DATABASE_URL format may be invalid: {db_url[:50]}...")
        print("   Expected format: postgresql://user:pass@host:port/dbname")
        return True  # Don't fail on this, just warn


def validate_required_in_production() -> bool:
    """Validate required environment variables in production."""
    node_env = os.getenv("NODE_ENV", "development")
    debug = os.getenv("DEBUG", "false").lower()

    if node_env == "production" or debug == "false":
        required_vars = ["DATABASE_URL", "SECRET_KEY", "REDIS_URL"]
        missing_vars = []

        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            print(f"❌ Missing required production environment variables: {missing_vars}")
            return False
        else:
            print("✅ All required production environment variables are set")

    return True


def main() -> int:
    """Main validation function."""
    print("🔍 Z2 Backend Environment Validation")
    print("=" * 50)

    # Check NODE_ENV
    node_env = os.getenv("NODE_ENV", "development")
    debug = os.getenv("DEBUG", "false")
    print(f"Environment: {node_env} (debug={debug})")
    print()

    # Run validations
    validations = [
        ("CORS Origins", validate_cors_origins),
        ("Database URL", validate_database_url),
        ("Production Requirements", validate_required_in_production),
    ]

    all_passed = True

    for name, validator in validations:
        print(f"Validating {name}...")
        try:
            if not validator():
                all_passed = False
        except Exception as e:
            print(f"❌ {name} validation error: {e}")
            all_passed = False
        print()

    # Summary
    if all_passed:
        print("🎉 All environment variable validations passed!")
        print("✅ Ready for deployment")
        return 0
    else:
        print("💥 Some validations failed!")
        print("❌ Please fix the issues before deploying")
        return 1


if __name__ == "__main__":
    sys.exit(main())
