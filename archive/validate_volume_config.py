#!/usr/bin/env python3
"""
Railway Volume Configuration Validation Script

This script validates that all Railway configuration files properly
define the app_storage volume and mount points.
"""

import json
import tomllib
from pathlib import Path


def validate_railway_toml():
    """Validate railway.toml has volume configuration."""
    print("🔍 Validating railway.toml...")
    
    with open("railway.toml", "rb") as f:
        config = tomllib.load(f)
    
    # Check volumes section
    volumes = config.get("volumes", {})
    assert "app_storage" in volumes, "app_storage volume not defined"
    print("✅ app_storage volume defined")
    
    # Check backend service volume mount
    backend = config.get("services", {}).get("backend", {})
    backend_volumes = backend.get("volumes", {}).get("volumes", [])
    assert "app_storage:/app/storage" in backend_volumes, "Backend volume mount missing"
    print("✅ Backend volume mount configured")
    
    # Check frontend service volume mount
    frontend = config.get("services", {}).get("frontend", {})
    frontend_volumes = frontend.get("volumes", {}).get("volumes", [])
    assert "app_storage:/app/storage" in frontend_volumes, "Frontend volume mount missing"
    print("✅ Frontend volume mount configured")
    
    # Check STORAGE_PATH environment variable
    backend_vars = backend.get("variables", {})
    assert backend_vars.get("STORAGE_PATH") == "/app/storage", "Backend STORAGE_PATH not set"
    print("✅ Backend STORAGE_PATH environment variable set")


def validate_railway_json_files():
    """Validate individual railway.json files have volume configuration."""
    print("\n🔍 Validating railway.json files...")
    
    # Validate backend railway.json
    with open("backend/railway.json") as f:
        backend_config = json.load(f)
    
    backend_volumes = backend_config.get("volumes", [])
    assert len(backend_volumes) == 1, "Backend should have exactly one volume"
    volume = backend_volumes[0]
    assert volume["name"] == "app_storage", "Backend volume name incorrect"
    assert volume["mountPath"] == "/app/storage", "Backend mount path incorrect"
    print("✅ Backend railway.json volume configured")
    
    # Validate frontend railway.json
    with open("frontend/railway.json") as f:
        frontend_config = json.load(f)
    
    frontend_volumes = frontend_config.get("volumes", [])
    assert len(frontend_volumes) == 1, "Frontend should have exactly one volume"
    volume = frontend_volumes[0]
    assert volume["name"] == "app_storage", "Frontend volume name incorrect"
    assert volume["mountPath"] == "/app/storage", "Frontend mount path incorrect"
    print("✅ Frontend railway.json volume configured")


def validate_railpack_json():
    """Validate railpack.json has volume configuration."""
    print("\n🔍 Validating railpack.json...")
    
    with open("railpack.json") as f:
        config = json.load(f)
    
    services = config.get("services", {})
    
    # Check backend service
    backend = services.get("backend", {})
    backend_vars = backend.get("variables", {})
    assert backend_vars.get("STORAGE_PATH") == "/app/storage", "Backend STORAGE_PATH missing in railpack.json"
    
    backend_volumes = backend.get("volumes", [])
    assert len(backend_volumes) == 1, "Backend should have one volume in railpack.json"
    volume = backend_volumes[0]
    assert volume["name"] == "app_storage", "Backend volume name incorrect in railpack.json"
    assert volume["mountPath"] == "/app/storage", "Backend mount path incorrect in railpack.json"
    print("✅ Backend service in railpack.json configured")
    
    # Check frontend service
    frontend = services.get("frontend", {})
    frontend_volumes = frontend.get("volumes", [])
    assert len(frontend_volumes) == 1, "Frontend should have one volume in railpack.json"
    volume = frontend_volumes[0]
    assert volume["name"] == "app_storage", "Frontend volume name incorrect in railpack.json"
    assert volume["mountPath"] == "/app/storage", "Frontend mount path incorrect in railpack.json"
    print("✅ Frontend service in railpack.json configured")


def validate_environment_files():
    """Validate environment variable files."""
    print("\n🔍 Validating environment variable files...")
    
    # Check backend env vars
    with open("backend_env_vars.txt") as f:
        backend_env = f.read()
    
    assert "STORAGE_PATH=/app/storage" in backend_env, "STORAGE_PATH missing from backend_env_vars.txt"
    print("✅ Backend environment variables configured")


def validate_docker_files():
    """Validate Dockerfiles create storage directories."""
    print("\n🔍 Validating Dockerfiles...")
    
    # Check backend Dockerfile
    with open("Dockerfile.backend") as f:
        backend_dockerfile = f.read()
    
    assert "mkdir -p /app/storage" in backend_dockerfile, "Backend Dockerfile doesn't create storage directory"
    assert "chmod 755 /app/storage" in backend_dockerfile, "Backend Dockerfile doesn't set permissions"
    print("✅ Backend Dockerfile configured")
    
    # Check frontend Dockerfile
    with open("Dockerfile.frontend") as f:
        frontend_dockerfile = f.read()
    
    assert "mkdir -p /app/storage" in frontend_dockerfile, "Frontend Dockerfile doesn't create storage directory"
    assert "chmod 755 /app/storage" in frontend_dockerfile, "Frontend Dockerfile doesn't set permissions"
    print("✅ Frontend Dockerfile configured")


def main():
    """Run all validation checks."""
    print("🚀 Railway Volume Configuration Validation")
    print("=" * 50)
    
    try:
        validate_railway_toml()
        validate_railway_json_files()
        validate_railpack_json()
        validate_environment_files()
        validate_docker_files()
        
        print("\n🎉 All validations passed!")
        print("✅ Railway volume configuration is properly set up")
        print("✅ Both frontend and backend services will have access to /app/storage")
        print("✅ Volume will persist data across deployments")
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())