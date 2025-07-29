#!/usr/bin/env python3
"""
Railway Railpack Volume Configuration Validation Script

This script validates that all Railway railpack configuration files properly
define the app_storage volume and mount points for both frontend and backend services.
"""

import json
import sys
from pathlib import Path


def validate_railpack_config(config_path: str, service_name: str = None):
    """Validate a single railpack.json configuration."""
    print(f"🔍 Validating {config_path}...")
    
    try:
        with open(config_path) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {config_path}: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ File not found: {config_path}")
        return False
    
    # Check if this is a multi-service configuration
    if "services" in config:
        return validate_multi_service_config(config, config_path)
    else:
        return validate_single_service_config(config, config_path, service_name)


def validate_multi_service_config(config: dict, config_path: str):
    """Validate multi-service railpack configuration."""
    services = config.get("services", {})
    
    if "frontend" not in services:
        print(f"❌ Frontend service not defined in {config_path}")
        return False
    
    if "backend" not in services:
        print(f"❌ Backend service not defined in {config_path}")
        return False
    
    # Validate frontend service
    frontend = services["frontend"]
    if not validate_frontend_service(frontend, "root railpack.json frontend service"):
        return False
    
    # Validate backend service
    backend = services["backend"]
    if not validate_backend_service(backend, "root railpack.json backend service"):
        return False
    
    print(f"✅ {config_path} multi-service configuration is valid")
    return True


def validate_single_service_config(config: dict, config_path: str, service_name: str):
    """Validate single-service railpack configuration."""
    if service_name == "frontend" or "node" in config.get("provider", ""):
        return validate_frontend_service(config, config_path)
    elif service_name == "backend" or "python" in config.get("provider", ""):
        return validate_backend_service(config, config_path)
    else:
        print(f"❌ Cannot determine service type for {config_path}")
        return False


def validate_frontend_service(config: dict, service_name: str):
    """Validate frontend service configuration."""
    # Check provider
    if config.get("provider") != "node":
        print(f"❌ {service_name}: Expected 'node' provider, got '{config.get('provider')}'")
        return False
    
    # Check start command (should NOT be poetry)
    deploy = config.get("deploy", {})
    start_command = deploy.get("startCommand", "")
    if "poetry" in start_command:
        print(f"❌ {service_name}: Start command contains 'poetry': {start_command}")
        return False
    
    if "npm" not in start_command and "yarn" not in start_command:
        print(f"❌ {service_name}: Start command should use npm or yarn: {start_command}")
        return False
    
    # Check volume configuration
    volumes = config.get("volumes", [])
    if not volumes:
        print(f"❌ {service_name}: No volumes configured")
        return False
    
    storage_volume = None
    for volume in volumes:
        if volume.get("name") == "app_storage":
            storage_volume = volume
            break
    
    if not storage_volume:
        print(f"❌ {service_name}: app_storage volume not found")
        return False
    
    if storage_volume.get("mountPath") != "/app/storage":
        print(f"❌ {service_name}: Volume mount path is '{storage_volume.get('mountPath')}', expected '/app/storage'")
        return False
    
    # Check environment variables
    variables = deploy.get("variables", {})
    if variables.get("STORAGE_PATH") != "/app/storage":
        print(f"❌ {service_name}: STORAGE_PATH is '{variables.get('STORAGE_PATH')}', expected '/app/storage'")
        return False
    
    print(f"✅ {service_name}: Frontend configuration is valid")
    return True


def validate_backend_service(config: dict, service_name: str):
    """Validate backend service configuration."""
    # Check provider
    if config.get("provider") != "python":
        print(f"❌ {service_name}: Expected 'python' provider, got '{config.get('provider')}'")
        return False
    
    # Check start command (should contain poetry)
    deploy = config.get("deploy", {})
    start_command = deploy.get("startCommand", "")
    if "poetry" not in start_command:
        print(f"❌ {service_name}: Start command should contain 'poetry': {start_command}")
        return False
    
    # Check volume configuration
    volumes = config.get("volumes", [])
    if not volumes:
        print(f"❌ {service_name}: No volumes configured")
        return False
    
    storage_volume = None
    for volume in volumes:
        if volume.get("name") == "app_storage":
            storage_volume = volume
            break
    
    if not storage_volume:
        print(f"❌ {service_name}: app_storage volume not found")
        return False
    
    if storage_volume.get("mountPath") != "/app/storage":
        print(f"❌ {service_name}: Volume mount path is '{storage_volume.get('mountPath')}', expected '/app/storage'")
        return False
    
    # Check environment variables
    variables = deploy.get("variables", {})
    if variables.get("STORAGE_PATH") != "/app/storage":
        print(f"❌ {service_name}: STORAGE_PATH is '{variables.get('STORAGE_PATH')}', expected '/app/storage'")
        return False
    
    print(f"✅ {service_name}: Backend configuration is valid")
    return True


def main():
    """Run all validation checks."""
    print("🚀 Railway Railpack Volume Configuration Validation")
    print("=" * 60)
    
    all_valid = True
    
    # Validate root railpack.json
    if not validate_railpack_config("railpack.json"):
        all_valid = False
    
    # Validate frontend railpack.json
    if not validate_railpack_config("frontend/railpack.json", "frontend"):
        all_valid = False
    
    # Validate backend railpack.json
    if not validate_railpack_config("backend/railpack.json", "backend"):
        all_valid = False
    
    if all_valid:
        print("\n🎉 All validations passed!")
        print("✅ Railway railpack configurations are properly set up")
        print("✅ Frontend service uses Node.js (no Poetry dependency)")
        print("✅ Backend service uses Python with Poetry")
        print("✅ Both services have /app/storage volume mount configured")
        print("✅ Volume will persist data across deployments")
        print("\n📋 Next Steps:")
        print("1. Deploy services to Railway")
        print("2. Ensure Railway service settings use correct root directories:")
        print("   - Frontend service: './frontend' root directory")
        print("   - Backend service: './backend' root directory")
        print("3. Verify volume mount path is '/app/storage' in Railway dashboard")
        return 0
    else:
        print("\n❌ Validation failed!")
        print("Please fix the configuration issues before deploying.")
        return 1


if __name__ == "__main__":
    exit(main())