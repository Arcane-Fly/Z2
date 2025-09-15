#!/usr/bin/env python3
"""
Configuration validation script for Z2 deployment.

This script validates that all critical configurations are properly set
and reports any issues that could cause deployment failures.
"""

import json
import os
import sys
from pathlib import Path


def validate_railpack_configs():
    """Validate railpack.json configurations."""
    print("🔍 Validating railpack configurations...")
    
    configs = [
        "railpack.json",
        "backend/railpack.json", 
        "frontend/railpack.json"
    ]
    
    for config_path in configs:
        if Path(config_path).exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                print(f"✅ {config_path}: Valid JSON")
                
                # Check for critical fields
                if "version" in config:
                    print(f"   Version: {config['version']}")
                if "metadata" in config and "name" in config["metadata"]:
                    print(f"   Service: {config['metadata']['name']}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ {config_path}: Invalid JSON - {e}")
                return False
        else:
            print(f"⚠️  {config_path}: Not found")
    
    return True


def check_storage_paths():
    """Check storage path consistency."""
    print("\n📁 Checking storage path configurations...")
    
    expected_path = "/opt/app/storage"
    configs_to_check = [
        ("railpack.json", ["services", "backend", "variables", "STORAGE_PATH"]),
        ("railpack.json", ["services", "frontend", "variables", "STORAGE_PATH"]),
        ("backend/railpack.json", ["variables", "STORAGE_PATH"]),
        ("frontend/railpack.json", ["variables", "STORAGE_PATH"])
    ]
    
    for config_file, path_keys in configs_to_check:
        if Path(config_file).exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                
                # Navigate through nested keys
                current = config
                for key in path_keys:
                    if key in current:
                        current = current[key]
                    else:
                        current = None
                        break
                
                if current == expected_path:
                    print(f"✅ {config_file}: Storage path correct ({current})")
                elif current is not None:
                    print(f"⚠️  {config_file}: Storage path mismatch - found {current}, expected {expected_path}")
                else:
                    print(f"❓ {config_file}: Storage path not found at expected location")
                    
            except (json.JSONDecodeError, KeyError):
                print(f"❌ {config_file}: Could not check storage path")


def check_poetry_version():
    """Check Poetry version configuration."""
    print("\n🏗️  Checking Poetry version configuration...")
    
    configs_to_check = [
        "railpack.json",
        "backend/railpack.json"
    ]
    
    expected_version = "1.8.5"
    
    for config_file in configs_to_check:
        if Path(config_file).exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                
                found_version = None
                
                # Check in variables
                if "variables" in config and "POETRY_VERSION" in config["variables"]:
                    found_version = config["variables"]["POETRY_VERSION"]
                elif "services" in config and "backend" in config["services"]:
                    backend = config["services"]["backend"]
                    if "deploy" in backend and "variables" in backend["deploy"]:
                        found_version = backend["deploy"]["variables"].get("POETRY_VERSION")
                
                if found_version == expected_version:
                    print(f"✅ {config_file}: Poetry version correct ({found_version})")
                elif found_version:
                    print(f"⚠️  {config_file}: Poetry version mismatch - found {found_version}, expected {expected_version}")
                else:
                    print(f"❓ {config_file}: Poetry version not specified")
                    
            except (json.JSONDecodeError, KeyError):
                print(f"❌ {config_file}: Could not check Poetry version")


def main():
    """Main validation function."""
    print("🚀 Z2 Configuration Validation\n")
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    os.chdir(root_dir)
    print(f"Working directory: {os.getcwd()}")
    
    all_valid = True
    all_valid &= validate_railpack_configs()
    check_storage_paths()
    check_poetry_version()
    
    print(f"\n{'='*50}")
    if all_valid:
        print("✅ All critical configurations appear valid!")
        print("🚢 Ready for deployment!")
    else:
        print("❌ Some configuration issues found.")
        print("📝 Please review and fix before deploying.")
        sys.exit(1)


if __name__ == "__main__":
    main()