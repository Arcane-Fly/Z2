#!/usr/bin/env python3
"""
Railway Security Validation Script for Z2 Platform

This script validates that the Z2 platform follows Railway security best practices:
1. No ARG/ENV secrets in Dockerfiles
2. Proper use of Railway environment variable injection
3. Runtime environment variable configuration
4. No secrets exposed in build artifacts
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any


class SecurityValidator:
    """Validates Railway security configuration."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []
    
    def validate_all(self) -> bool:
        """Run all security validations."""
        print("🔒 Railway Security Validation for Z2 Platform")
        print("=" * 50)
        
        self.validate_no_dockerfiles_with_secrets()
        self.validate_railpack_security()
        self.validate_environment_variable_usage()
        self.validate_source_code_security()
        
        self.print_results()
        return len(self.errors) == 0
    
    def validate_no_dockerfiles_with_secrets(self):
        """Ensure no Dockerfiles contain secret ARG/ENV declarations."""
        print("📦 Validating Dockerfile Security...")
        
        # Find all Dockerfiles
        dockerfiles = []
        for pattern in ["**/Dockerfile*", "**/*.dockerfile"]:
            dockerfiles.extend(self.repo_path.glob(pattern))
        
        if not dockerfiles:
            self.successes.append("No Dockerfiles found - using Railway railpack (secure)")
            return
        
        secret_patterns = [
            r'ARG\s+.*(?:SECRET|KEY|PASSWORD|TOKEN)',
            r'ENV\s+.*(?:SECRET|KEY|PASSWORD|TOKEN)',
        ]
        
        for dockerfile in dockerfiles:
            content = dockerfile.read_text()
            for pattern in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    self.errors.append(
                        f"Security violation in {dockerfile}: Found secret in ARG/ENV"
                    )
                else:
                    self.successes.append(f"Dockerfile {dockerfile} is secure")
    
    def validate_railpack_security(self):
        """Validate railpack.json follows security best practices."""
        print("🚂 Validating Railway Configuration...")
        
        railpack_files = [
            self.repo_path / "railpack.json",
            self.repo_path / "frontend" / "railpack.json", 
            self.repo_path / "backend" / "railpack.json"
        ]
        
        for railpack_file in railpack_files:
            if not railpack_file.exists():
                continue
                
            try:
                config = json.loads(railpack_file.read_text())
                self._validate_railpack_config(config, railpack_file.name)
            except json.JSONDecodeError as e:
                self.errors.append(f"Invalid JSON in {railpack_file}: {e}")
    
    def _validate_railpack_config(self, config: Dict[str, Any], filename: str):
        """Validate a single railpack configuration."""
        
        # Check for proper variable injection syntax
        def check_variables(variables: Dict[str, str], context: str):
            for key, value in variables.items():
                if isinstance(value, str):
                    # Check for hardcoded secrets
                    if any(secret in key.upper() for secret in ['SECRET', 'KEY', 'PASSWORD']):
                        if not (value.startswith('${{') and value.endswith('}}')):
                            if not (key.endswith('_MINUTES') or key.endswith('_DAYS') or key.endswith('_HOURS')):
                                self.errors.append(
                                    f"{filename} {context}: {key} should use Railway injection: ${{{key}}}"
                                )
                        else:
                            self.successes.append(
                                f"{filename} {context}: {key} properly uses Railway injection"
                            )
        
        # Check services configuration
        if "services" in config:
            for service_name, service_config in config["services"].items():
                if "deploy" in service_config and "variables" in service_config["deploy"]:
                    check_variables(
                        service_config["deploy"]["variables"],
                        f"service.{service_name}.deploy.variables"
                    )
                if "steps" in service_config:
                    for step_name, step_config in service_config["steps"].items():
                        if "variables" in step_config:
                            check_variables(
                                step_config["variables"],
                                f"service.{service_name}.steps.{step_name}.variables"
                            )
        
        # Check build/deploy env
        for section in ["build", "deploy"]:
            if section in config and "env" in config[section]:
                check_variables(config[section]["env"], f"{section}.env")
    
    def validate_environment_variable_usage(self):
        """Validate application code properly reads environment variables."""
        print("⚙️ Validating Environment Variable Usage...")
        
        # Check backend security.py
        security_file = self.repo_path / "backend" / "app" / "utils" / "security.py"
        if security_file.exists():
            content = security_file.read_text()
            if 'os.getenv("JWT_SECRET_KEY"' in content:
                self.successes.append("Backend security.py properly reads JWT_SECRET_KEY from environment")
            else:
                self.errors.append("Backend security.py not reading JWT_SECRET_KEY from environment")
        
        # Check backend config.py
        config_file = self.repo_path / "backend" / "app" / "core" / "config.py"
        if config_file.exists():
            content = config_file.read_text()
            if 'alias="JWT_SECRET_KEY"' in content:
                self.successes.append("Backend config.py properly configured with JWT_SECRET_KEY alias")
            else:
                self.warnings.append("Backend config.py might not have proper JWT_SECRET_KEY alias")
    
    def validate_source_code_security(self):
        """Check for any hardcoded secrets in source code."""
        print("🔍 Scanning Source Code for Hardcoded Secrets...")
        
        # Patterns that might indicate hardcoded secrets
        dangerous_patterns = [
            r'["\']sk-[a-zA-Z0-9]{48}["\']',  # OpenAI API keys
            r'["\']pk_test_[a-zA-Z0-9]{24}["\']',  # Stripe test keys
            r'["\']pk_live_[a-zA-Z0-9]{24}["\']',  # Stripe live keys
            r'["\'][A-Za-z0-9]{32}["\']',  # Generic 32-char secrets
        ]
        
        # Files to scan
        source_files = []
        for pattern in ["**/*.py", "**/*.ts", "**/*.js", "**/*.tsx", "**/*.jsx"]:
            source_files.extend(self.repo_path.glob(pattern))
        
        # Exclude certain paths
        excluded_paths = [".env.example", "validate_railway_security.py", "node_modules", ".git"]
        
        violations_found = False
        for source_file in source_files:
            if any(excluded in str(source_file) for excluded in excluded_paths):
                continue
                
            try:
                content = source_file.read_text()
                for pattern in dangerous_patterns:
                    if re.search(pattern, content):
                        self.warnings.append(
                            f"Potential hardcoded secret in {source_file}"
                        )
                        violations_found = True
            except (UnicodeDecodeError, PermissionError):
                continue
        
        if not violations_found:
            self.successes.append("No hardcoded secrets found in source code")
    
    def print_results(self):
        """Print validation results."""
        print("\n" + "=" * 50)
        print("📊 Security Validation Results")
        print("=" * 50)
        
        if self.successes:
            print(f"\n✅ Passed ({len(self.successes)}):")
            for success in self.successes:
                print(f"  ✅ {success}")
        
        if self.warnings:
            print(f"\n⚠️ Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  ⚠️ {warning}")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  ❌ {error}")
        
        print(f"\n🔒 Security Status: {'PASS' if len(self.errors) == 0 else 'FAIL'}")
        
        if len(self.errors) == 0:
            print("🎉 All security validations passed! Railway deployment is secure.")
        else:
            print("🚨 Security violations found. Please fix before deploying to Railway.")


def main():
    """Main entry point."""
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    validator = SecurityValidator(repo_path)
    success = validator.validate_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()