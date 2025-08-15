#!/usr/bin/env python3
"""
Production Configuration Validation Script

This script validates that all required environment variables and configurations
are properly set for production deployment on Railway.
"""

import os
import json
import sys
from typing import Dict, List, Optional, Tuple
import urllib.parse


def validate_environment_variable(name: str, required: bool = True) -> Tuple[bool, Optional[str]]:
    """Validate a single environment variable."""
    value = os.getenv(name)
    if required and not value:
        return False, f"❌ {name} is required but not set"
    elif value:
        return True, f"✅ {name} is set"
    else:
        return True, f"ℹ️ {name} is optional and not set"


def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_cors_origins(cors_str: str) -> Tuple[bool, str]:
    """Validate CORS origins configuration."""
    if not cors_str:
        return False, "❌ CORS_ORIGINS is empty"
    
    try:
        # Try to parse as JSON first
        if cors_str.strip().startswith('['):
            origins = json.loads(cors_str)
            if not isinstance(origins, list):
                return False, "❌ CORS_ORIGINS JSON must be a list"
        else:
            # Parse as comma-separated
            origins = [o.strip() for o in cors_str.split(',')]
        
        # Validate each origin
        for origin in origins:
            if not validate_url(origin):
                return False, f"❌ Invalid CORS origin URL: {origin}"
        
        return True, f"✅ CORS origins valid: {origins}"
    
    except json.JSONDecodeError:
        return False, "❌ CORS_ORIGINS invalid JSON format"
    except Exception as e:
        return False, f"❌ CORS_ORIGINS validation error: {str(e)}"


def validate_database_url(db_url: str) -> Tuple[bool, str]:
    """Validate database URL format."""
    if not db_url:
        return False, "❌ DATABASE_URL is empty"
    
    if not db_url.startswith(('postgresql://', 'postgresql+asyncpg://')):
        return False, "❌ DATABASE_URL must be a PostgreSQL URL"
    
    try:
        parsed = urllib.parse.urlparse(db_url)
        if not all([parsed.hostname, parsed.username, parsed.path.lstrip('/')]):
            return False, "❌ DATABASE_URL missing required components"
        return True, f"✅ DATABASE_URL format valid (host: {parsed.hostname})"
    except Exception:
        return False, "❌ DATABASE_URL format invalid"


def main():
    """Main validation function."""
    print("Z2 Platform - Production Configuration Validation")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # Backend Environment Variables
    print("\n🔧 Backend Configuration:")
    backend_vars = [
        ('PORT', False),  # Railway provides this
        ('DATABASE_URL', True),
        ('JWT_SECRET', True),
        ('CORS_ORIGINS', True),
        ('APP_NAME', False),
        ('APP_VERSION', False),
        ('LOG_LEVEL', False),
        ('DEBUG', False),
        ('API_V1_PREFIX', False),
        ('DEFAULT_ADMIN_PASSWORD', False),
    ]
    
    for var_name, required in backend_vars:
        valid, message = validate_environment_variable(var_name, required)
        print(f"  {message}")
        if not valid:
            errors.append(message)
    
    # Special validations
    print("\n🔍 Advanced Configuration Validation:")
    
    # CORS Origins
    cors_origins = os.getenv('CORS_ORIGINS', '')
    if cors_origins:
        valid, message = validate_cors_origins(cors_origins)
        print(f"  {message}")
        if not valid:
            errors.append(message)
    
    # Database URL
    db_url = os.getenv('DATABASE_URL', '')
    if db_url:
        valid, message = validate_database_url(db_url)
        print(f"  {message}")
        if not valid:
            errors.append(message)
    
    # JWT Secret strength
    jwt_secret = os.getenv('JWT_SECRET', '')
    if jwt_secret:
        if len(jwt_secret) < 32:
            warnings.append("⚠️ JWT_SECRET should be at least 32 characters long")
            print(f"  ⚠️ JWT_SECRET length: {len(jwt_secret)} (recommend 32+)")
        else:
            print(f"  ✅ JWT_SECRET length adequate: {len(jwt_secret)} characters")
    
    # Frontend Environment Variables
    print("\n🎨 Frontend Configuration:")
    frontend_vars = [
        ('VITE_API_BASE_URL', True),
        ('VITE_WS_BASE_URL', False),
        ('VITE_APP_NAME', False),
        ('VITE_APP_VERSION', False),
    ]
    
    for var_name, required in frontend_vars:
        valid, message = validate_environment_variable(var_name, required)
        print(f"  {message}")
        if not valid:
            errors.append(message)
    
    # Validate frontend URLs
    api_url = os.getenv('VITE_API_BASE_URL', '')
    if api_url:
        if validate_url(api_url):
            if api_url.startswith('https://'):
                print(f"  ✅ VITE_API_BASE_URL uses HTTPS: {api_url}")
            else:
                warnings.append("⚠️ VITE_API_BASE_URL should use HTTPS in production")
                print(f"  ⚠️ VITE_API_BASE_URL should use HTTPS: {api_url}")
        else:
            errors.append(f"❌ VITE_API_BASE_URL invalid format: {api_url}")
            print(f"  ❌ VITE_API_BASE_URL invalid format")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Validation Summary:")
    
    if not errors and not warnings:
        print("🎉 All configurations are valid! Ready for production deployment.")
        return 0
    
    if warnings:
        print(f"\n⚠️ Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"  {warning}")
    
    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for error in errors:
            print(f"  {error}")
        print("\n🔧 Please fix the errors above before deploying to production.")
        return 1
    
    print("\n✅ Configuration valid with warnings. Review warnings before deployment.")
    return 0


if __name__ == "__main__":
    sys.exit(main())