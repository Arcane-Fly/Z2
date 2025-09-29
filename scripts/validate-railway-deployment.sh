#!/bin/bash
# ⚠️  DEPRECATED: This script validates multi-config setup that conflicts with Railway Master Cheat Sheet
# 
# 🔴 WARNING: This script expects multiple build configurations (railway.json, nixpacks.toml, Procfile)
# which should NOT exist according to Railway Deployment Master Cheat Sheet standards.
#
# ✅ USE INSTEAD: scripts/railway-railpack-validation.sh
# The new script enforces railpack-only configuration as required.

echo "⚠️  DEPRECATED VALIDATION SCRIPT"
echo "================================"
echo "This script validates multi-configuration setup that violates Railway best practices."
echo "Use scripts/railway-railpack-validation.sh instead for correct railpack-only validation."
echo
echo "Continuing with legacy validation for compatibility..."
echo

# Railway Deployment Configuration Validation Script

set -e

echo "🚀 Validating Railway Deployment Configurations"
echo "=============================================="

REPO_ROOT="/home/runner/work/Z2/Z2"
ERRORS=0

# Function to check file exists and is valid JSON
check_json_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        echo "✅ Found: $description"
        if jq empty "$file" 2>/dev/null; then
            echo "✅ Valid JSON: $description"
        else
            echo "❌ Invalid JSON: $description"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo "❌ Missing: $description at $file"
        ERRORS=$((ERRORS + 1))
    fi
}

# Function to check file exists
check_file_exists() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        echo "✅ Found: $description"
    else
        echo "❌ Missing: $description at $file"
        ERRORS=$((ERRORS + 1))
    fi
}

echo
echo "📋 Checking Railway Configuration Files..."

# Frontend configurations
check_json_file "$REPO_ROOT/frontend/railway.json" "Frontend Railway configuration"
check_file_exists "$REPO_ROOT/frontend/nixpacks.toml" "Frontend Nixpacks configuration"
check_file_exists "$REPO_ROOT/frontend/Procfile" "Frontend Procfile"

# Backend configurations  
check_json_file "$REPO_ROOT/backend/railway.json" "Backend Railway configuration"
check_file_exists "$REPO_ROOT/backend/nixpacks.toml" "Backend Nixpacks configuration"
check_file_exists "$REPO_ROOT/backend/Procfile" "Backend Procfile"

# Existing railpack configurations
check_json_file "$REPO_ROOT/railpack.json" "Root Railpack configuration"
check_json_file "$REPO_ROOT/frontend/railpack.json" "Frontend Railpack configuration"
check_json_file "$REPO_ROOT/backend/railpack.json" "Backend Railpack configuration"

echo
echo "🔍 Validating Configuration Content..."

# Check Railway.json configurations
if [ -f "$REPO_ROOT/frontend/railway.json" ]; then
    if jq -e '.build.builder == "NIXPACKS"' "$REPO_ROOT/frontend/railway.json" >/dev/null; then
        echo "✅ Frontend Railway.json: NIXPACKS builder specified"
    else
        echo "❌ Frontend Railway.json: Missing NIXPACKS builder"
        ERRORS=$((ERRORS + 1))
    fi
    
    if jq -e '.deploy.startCommand' "$REPO_ROOT/frontend/railway.json" >/dev/null; then
        START_CMD=$(jq -r '.deploy.startCommand' "$REPO_ROOT/frontend/railway.json")
        echo "✅ Frontend Railway.json: Start command: $START_CMD"
    else
        echo "❌ Frontend Railway.json: Missing start command"
        ERRORS=$((ERRORS + 1))
    fi
fi

if [ -f "$REPO_ROOT/backend/railway.json" ]; then
    if jq -e '.build.builder == "NIXPACKS"' "$REPO_ROOT/backend/railway.json" >/dev/null; then
        echo "✅ Backend Railway.json: NIXPACKS builder specified"
    else
        echo "❌ Backend Railway.json: Missing NIXPACKS builder"
        ERRORS=$((ERRORS + 1))
    fi
    
    if jq -e '.deploy.startCommand' "$REPO_ROOT/backend/railway.json" >/dev/null; then
        START_CMD=$(jq -r '.deploy.startCommand' "$REPO_ROOT/backend/railway.json")
        echo "✅ Backend Railway.json: Start command: $START_CMD"
    else
        echo "❌ Backend Railway.json: Missing start command"
        ERRORS=$((ERRORS + 1))
    fi
fi

echo
echo "🔧 Checking Nixpacks Configurations..."

# Check Nixpacks configurations
if [ -f "$REPO_ROOT/frontend/nixpacks.toml" ]; then
    if grep -q "nodejs_18" "$REPO_ROOT/frontend/nixpacks.toml"; then
        echo "✅ Frontend Nixpacks: Node.js runtime specified"
    else
        echo "❌ Frontend Nixpacks: Missing Node.js runtime"
        ERRORS=$((ERRORS + 1))
    fi
fi

if [ -f "$REPO_ROOT/backend/nixpacks.toml" ]; then
    if grep -q "python3" "$REPO_ROOT/backend/nixpacks.toml"; then
        echo "✅ Backend Nixpacks: Python runtime specified"
    else
        echo "❌ Backend Nixpacks: Missing Python runtime"
        ERRORS=$((ERRORS + 1))
    fi
fi

echo
echo "📝 Checking Procfiles..."

# Check Procfiles
if [ -f "$REPO_ROOT/frontend/Procfile" ]; then
    if grep -q "web:" "$REPO_ROOT/frontend/Procfile"; then
        PROC_CMD=$(grep "web:" "$REPO_ROOT/frontend/Procfile")
        echo "✅ Frontend Procfile: $PROC_CMD"
    else
        echo "❌ Frontend Procfile: Missing web process"
        ERRORS=$((ERRORS + 1))
    fi
fi

if [ -f "$REPO_ROOT/backend/Procfile" ]; then
    if grep -q "web:" "$REPO_ROOT/backend/Procfile"; then
        PROC_CMD=$(grep "web:" "$REPO_ROOT/backend/Procfile")
        echo "✅ Backend Procfile: $PROC_CMD"
    else
        echo "❌ Backend Procfile: Missing web process"
        ERRORS=$((ERRORS + 1))
    fi
fi

echo
echo "📚 Checking Documentation..."

check_file_exists "$REPO_ROOT/docs/railway-environment-variables.md" "Railway environment variables documentation"

echo
echo "🎯 Testing Configuration Syntax..."

# Test TOML syntax for Nixpacks files
if command -v python3 >/dev/null 2>&1; then
    for toml_file in "$REPO_ROOT/frontend/nixpacks.toml" "$REPO_ROOT/backend/nixpacks.toml"; do
        if [ -f "$toml_file" ]; then
            if python3 -c "import tomllib; tomllib.load(open('$toml_file', 'rb'))" 2>/dev/null; then
                echo "✅ Valid TOML syntax: $(basename "$toml_file")"
            else
                echo "❌ Invalid TOML syntax: $(basename "$toml_file")"
                ERRORS=$((ERRORS + 1))
            fi
        fi
    done
else
    echo "⚠️  Python3 not available, skipping TOML validation"
fi

echo
echo "=============================================="

if [ $ERRORS -eq 0 ]; then
    echo "🎉 All Railway deployment configurations are valid!"
    echo "✅ Repository is ready for Railway deployment with multiple fallback layers:"
    echo "   1. Railpack configurations (primary)"
    echo "   2. Railway.json configurations (explicit builder)"
    echo "   3. Nixpacks.toml configurations (advanced Nixpacks)"
    echo "   4. Procfile configurations (simple start commands)"
    echo
    echo "📋 Next steps:"
    echo "   1. Set environment variables in Railway dashboard"
    echo "   2. Deploy services to Railway"
    echo "   3. Monitor deployment logs for successful startup"
    echo "   4. Verify health endpoints respond correctly"
else
    echo "❌ Found $ERRORS configuration issues that need to be fixed."
    exit 1
fi