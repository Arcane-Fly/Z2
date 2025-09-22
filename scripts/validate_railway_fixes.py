#!/usr/bin/env python3
"""
Railway deployment fixes validation script.

This script validates that all the critical Railway deployment issues 
identified in the problem statement have been properly addressed.
"""

import json
import os
import sys
from pathlib import Path


def validate_frontend_corepack_fix():
    """Validate frontend corepack and yarn version fixes."""
    print("🔧 Validating Frontend Corepack Fixes...")
    
    issues = []
    
    # Check root railpack.json
    root_railpack = Path("railpack.json")
    if root_railpack.exists():
        with open(root_railpack) as f:
            config = json.load(f)
        
        frontend_config = config.get("services", {}).get("frontend", {})
        install_commands = frontend_config.get("steps", {}).get("install", {}).get("commands", [])
        
        if any("yarn@4.9.2" in cmd for cmd in install_commands):
            print("✅ Root railpack.json: Yarn 4.9.2 version specified")
        else:
            issues.append("❌ Root railpack.json: Missing Yarn 4.9.2 specification")
            
        if any("corepack enable" in cmd for cmd in install_commands):
            print("✅ Root railpack.json: Corepack enable command present")
        else:
            issues.append("❌ Root railpack.json: Missing corepack enable command")
    
    # Check frontend-specific railpack.json
    frontend_railpack = Path("frontend/railpack.json")
    if frontend_railpack.exists():
        with open(frontend_railpack) as f:
            config = json.load(f)
        
        install_commands = config.get("build", {}).get("steps", {}).get("install", {}).get("commands", [])
        
        if any("yarn@4.9.2" in cmd for cmd in install_commands):
            print("✅ Frontend railpack.json: Yarn 4.9.2 version specified")
        else:
            issues.append("❌ Frontend railpack.json: Missing Yarn 4.9.2 specification")
    
    # Check package.json consistency
    package_json = Path("package.json")
    if package_json.exists():
        with open(package_json) as f:
            config = json.load(f)
        
        package_manager = config.get("packageManager", "")
        if "yarn@4.9.2" in package_manager:
            print("✅ Root package.json: Yarn 4.9.2 package manager specified")
        else:
            issues.append("❌ Root package.json: Inconsistent yarn version")
    
    return issues


def validate_security_hardening():
    """Validate backend security hardening fixes."""
    print("\n🔒 Validating Backend Security Hardening...")
    
    issues = []
    
    # Check security.py for environment variable usage
    security_file = Path("backend/app/utils/security.py")
    if security_file.exists():
        with open(security_file) as f:
            content = f.read()
        
        if "os.getenv(\"JWT_SECRET_KEY\"" in content:
            print("✅ Backend security.py: JWT_SECRET_KEY reads from environment")
        else:
            issues.append("❌ Backend security.py: JWT_SECRET_KEY not reading from environment")
            
        if "JWT_ACCESS_TOKEN_EXPIRE_MINUTES" in content and "os.getenv" in content:
            print("✅ Backend security.py: JWT token expiration configurable")
        else:
            issues.append("❌ Backend security.py: JWT expiration not configurable")
    
    # Check railpack.json for secure environment variables
    backend_railpack = Path("backend/railpack.json")
    if backend_railpack.exists():
        with open(backend_railpack) as f:
            config = json.load(f)
        
        env_vars = config.get("deploy", {}).get("env", {})
        
        if "JWT_SECRET_KEY" in env_vars:
            print("✅ Backend railpack.json: JWT_SECRET_KEY environment variable configured")
        else:
            issues.append("❌ Backend railpack.json: Missing JWT_SECRET_KEY environment variable")
    
    return issues


def validate_configuration_consolidation():
    """Validate configuration consolidation fixes."""
    print("\n📂 Validating Configuration Consolidation...")
    
    issues = []
    
    # Check for removed competing files
    competing_files = [
        "backend/railway.toml",
        "frontend/railway.json"
    ]
    
    for file_path in competing_files:
        if Path(file_path).exists():
            issues.append(f"❌ Competing configuration file still exists: {file_path}")
        else:
            print(f"✅ Competing configuration file removed: {file_path}")
    
    # Check .railpacignore for proper exclusions
    railpacignore = Path(".railpacignore")
    if railpacignore.exists():
        with open(railpacignore) as f:
            content = f.read()
        
        if "node_modules/" in content:
            print("✅ .railpacignore: node_modules excluded")
        if ".cache/" in content:
            print("✅ .railpacignore: cache directories excluded")
    
    return issues


def validate_poetry_configuration():
    """Validate Poetry configuration consistency."""
    print("\n🏗️ Validating Poetry Configuration...")
    
    issues = []
    
    # Check root railpack.json Poetry version
    root_railpack = Path("railpack.json")
    if root_railpack.exists():
        with open(root_railpack) as f:
            config = json.load(f)
        
        backend_config = config.get("services", {}).get("backend", {})
        install_commands = backend_config.get("steps", {}).get("install", {}).get("commands", [])
        
        if any("poetry==1.8.5" in cmd for cmd in install_commands):
            print("✅ Root railpack.json: Poetry 1.8.5 version specified")
        else:
            issues.append("❌ Root railpack.json: Missing Poetry 1.8.5 specification")
    
    # Check backend railpack.json
    backend_railpack = Path("backend/railpack.json")
    if backend_railpack.exists():
        with open(backend_railpack) as f:
            config = json.load(f)
        
        install_commands = config.get("build", {}).get("steps", {}).get("install", {}).get("commands", [])
        
        if any("poetry==1.8.5" in cmd for cmd in install_commands):
            print("✅ Backend railpack.json: Poetry 1.8.5 version specified")
        else:
            issues.append("❌ Backend railpack.json: Missing Poetry 1.8.5 specification")
    
    return issues


def main():
    """Main validation function."""
    print("🚀 Railway Deployment Fixes Validation\n")
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    os.chdir(root_dir)
    print(f"Working directory: {os.getcwd()}")
    
    all_issues = []
    
    # Run all validations
    all_issues.extend(validate_frontend_corepack_fix())
    all_issues.extend(validate_security_hardening())
    all_issues.extend(validate_configuration_consolidation())
    all_issues.extend(validate_poetry_configuration())
    
    print(f"\n{'='*60}")
    
    if not all_issues:
        print("✅ All Railway deployment fixes have been properly implemented!")
        print("🚢 The repository is ready for Railway deployment!")
        print("\n📋 Summary of fixes:")
        print("   - Corepack hash mismatch resolved (Yarn 4.9.2)")
        print("   - JWT secrets moved to environment variables")
        print("   - Competing configuration files removed")
        print("   - Poetry version standardized to 1.8.5")
        print("   - Build system consolidation completed")
    else:
        print("❌ Some issues were found:")
        for issue in all_issues:
            print(f"   {issue}")
        print("\n📝 Please review and fix these issues before deploying.")
        sys.exit(1)


if __name__ == "__main__":
    main()