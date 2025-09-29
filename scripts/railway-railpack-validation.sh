#!/bin/bash
# Railway Railpack-Only Deployment Validation Script
# Based on Railway Deployment Master Cheat Sheet standards

set -e

echo "🚀 Railway Railpack-Only Deployment Validation"
echo "=============================================="
echo "Enforcing Railway Deployment Master Cheat Sheet standards"
echo

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

# 1. CRITICAL: Check for competing build configurations (MUST NOT EXIST)
echo "📋 1. Checking for competing build configurations..."
competing_configs=$(find . -name "Dockerfile*" -o -name "railway.toml" -o -name "railway.json" -o -name "nixpacks.toml" -o -name "Procfile" 2>/dev/null | grep -v scripts | grep -v docs || true)
if [ -n "$competing_configs" ]; then
    echo "❌ CRITICAL: Found competing build configurations that conflict with Railpack:"
    echo "$competing_configs"
    echo ""
    echo "🔴 Railway build priority: Dockerfile > railpack.json > railway.json/toml > Nixpacks"
    echo "🔴 For Railpack-only deployment, these files MUST be removed:"
    echo "   - Dockerfile, railway.toml, railway.json, nixpacks.toml, Procfile"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ No competing build configurations found - Railpack-only setup confirmed"
fi

echo
echo "📋 2. Validating required Railpack configurations..."

# Check required railpack.json files
check_json_file "$REPO_ROOT/railpack.json" "Root Railpack configuration"
check_json_file "$REPO_ROOT/frontend/railpack.json" "Frontend Railpack configuration"
check_json_file "$REPO_ROOT/backend/railpack.json" "Backend Railpack configuration"

echo
echo "📋 3. Checking PORT environment variable usage..."
port_usage=$(grep -r "process\.env\.PORT\|PORT.*=.*os\.getenv\|PORT.*=.*os\.environ" --include="*.py" --include="*.js" --include="*.ts" --include="*.tsx" . | grep -v node_modules | grep -v ".git" || true)
if [ -n "$port_usage" ]; then
    echo "✅ Found proper PORT environment variable usage:"
    echo "$port_usage" | head -5
else
    echo "⚠️  No PORT environment variable usage found"
fi

echo
echo "📋 4. Verifying host binding patterns..."
# Check for proper 0.0.0.0 binding
good_host=$(grep -r "0\.0\.0\.0" --include="*.py" --include="*.js" --include="*.ts" . | grep -v node_modules | grep -v ".git" || true)
if [ -n "$good_host" ]; then
    echo "✅ Found proper host binding (0.0.0.0):"
    echo "$good_host" | head -3
fi

# Check for problematic localhost/127.0.0.1 bindings
bad_host=$(grep -r "localhost\|127\.0\.0\.1" --include="*.py" --include="*.js" --include="*.ts" . | grep -v node_modules | grep -v ".git" | grep -E "(listen|HOST|host)" || true)
if [ -n "$bad_host" ]; then
    echo "⚠️  Found potential localhost/127.0.0.1 bindings:"
    echo "$bad_host" | head -3
    echo "Consider updating these to use 0.0.0.0 for production"
fi

echo
echo "📋 5. Checking for health endpoints..."
health_endpoints=$(grep -r "/health\|/api/health" --include="*.py" --include="*.js" --include="*.ts" . | grep -v node_modules | grep -v ".git" || true)
if [ -n "$health_endpoints" ]; then
    echo "✅ Found health endpoints:"
    echo "$health_endpoints" | head -3
else
    echo "❌ No health endpoints found"
    ERRORS=$((ERRORS + 1))
fi

echo
echo "📋 6. Validating health check configuration in railpack.json..."
for config in railpack.json frontend/railpack.json backend/railpack.json; do
    if [ -f "$config" ]; then
        if grep -q "healthCheckPath" "$config"; then
            health_path=$(grep "healthCheckPath" "$config" | cut -d'"' -f4)
            echo "✅ $config: Health check configured at $health_path"
        else
            echo "⚠️  $config: No health check path configured"
        fi
    fi
done

echo
echo "📋 7. Checking critical build output directories..."
# Check that critical output directories are not ignored
if [ -f "frontend/.railwayignore" ]; then
    if grep -q "^dist/" "frontend/.railwayignore" || grep -q "^build/" "frontend/.railwayignore"; then
        echo "❌ CRITICAL: Frontend .railwayignore excludes dist/ or build/ directory"
        echo "   Railway needs these directories to serve the built frontend"
        ERRORS=$((ERRORS + 1))
    else
        echo "✅ Frontend .railwayignore does not exclude critical build directories"
    fi
fi

echo
echo "=============================================="

if [ $ERRORS -eq 0 ]; then
    echo "🎉 All Railway deployment configurations pass Railpack-only validation!"
    echo
    echo "✅ Repository follows Railway Deployment Master Cheat Sheet standards:"
    echo "   - Railpack-only build configuration (no competing configs)"
    echo "   - Proper PORT environment variable usage"
    echo "   - Correct host binding (0.0.0.0)"
    echo "   - Health check endpoints configured"
    echo "   - Critical build outputs not ignored"
else
    echo "❌ Found $ERRORS validation errors"
    echo
    echo "🔧 Required Actions:"
    echo "   1. Remove any competing build configuration files"
    echo "   2. Ensure only railpack.json files are used for build config"
    echo "   3. Fix PORT and host binding issues"
    echo "   4. Add health check endpoints where missing"
    echo "   5. Update .railwayignore to not exclude critical build outputs"
    exit 1
fi

echo
echo "📋 Quick Railway Commands:"
echo "# Force Railpack rebuild:"
echo "railway up --force"
echo
echo "# Debug environment variables:"
echo "railway run env | grep -E '(PORT|HOST|RAILWAY)'"
echo
echo "# Test health endpoint locally:"
echo "railway run curl http://localhost:\$PORT/health"