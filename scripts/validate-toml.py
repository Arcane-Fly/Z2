#!/usr/bin/env python3
"""Simple TOML validation script for railway.toml"""
import sys
import tomllib
from pathlib import Path

def validate_toml(file_path):
    """Validate TOML file syntax"""
    try:
        with open(file_path, 'rb') as f:
            data = tomllib.load(f)
        print(f"✅ {file_path} is valid TOML")
        return True
    except Exception as e:
        print(f"❌ {file_path} has TOML syntax error: {e}")
        return False

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "railway.toml"
    success = validate_toml(file_path)
    sys.exit(0 if success else 1)
