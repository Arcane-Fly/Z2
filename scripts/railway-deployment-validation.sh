#!/bin/bash
# Pre-Deployment Validation Checklist
# Based on Railway Deployment Master Cheat Sheet

set -e

echo "🚀 Railway Deployment Validation Checklist"
echo "==========================================="

# 1. Check for conflicting build configs
echo "📋 1. Checking for competing build configurations..."
competing_configs=$(find . -name "Dockerfile*" -o -name "railway.toml" -o -name "nixpacks.toml" -o -name "Procfile" 2>/dev/null | grep -v scripts | grep -v docs || true)
if [ -n "$competing_configs" ]; then
    echo "❌ Found competing build configurations that conflict with Railpack:"
    echo "$competing_configs"
    echo "Railway build priority: Dockerfile > railpack.json > railway.json/toml > Nixpacks"
    echo "For Railpack-only deployment, remove: Dockerfile, railway.toml, nixpacks.toml, Procfile"
    exit 1
else
    echo "✅ No competing build configurations found - Railpack-only setup confirmed"
fi

# 2. Validate railpack.json syntax
echo "📋 2. Validating JSON syntax..."
for config in railpack.json backend/railpack.json frontend/railpack.json; do
    if [ -f "$config" ]; then
        if cat "$config" | jq '.' > /dev/null 2>&1; then
            echo "✅ $config: Valid JSON"
        else
            echo "❌ $config: Invalid JSON syntax"
            exit 1
        fi
    fi
done

# 3. Verify PORT usage in code
echo "📋 3. Checking PORT environment variable usage..."
port_usage=$(grep -r "process\.env\.PORT\|PORT.*=.*os\.getenv\|PORT.*=.*os\.environ" --include="*.py" --include="*.js" --include="*.ts" --include="*.tsx" . | grep -v node_modules | grep -v ".git" || true)
if [ -n "$port_usage" ]; then
    echo "✅ Found proper PORT environment variable usage:"
    echo "$port_usage" | head -3
else
    echo "⚠️  No PORT environment variable usage found in code"
fi

# 4. Check host binding
echo "📋 4. Verifying host binding patterns..."
good_hosts=$(grep -r "0\.0\.0\.0\|HOST.*=.*0\.0\.0\.0" --include="*.py" --include="*.js" --include="*.ts" . | grep -v node_modules | grep -v ".git" || true)
bad_hosts=$(grep -r "localhost\|127\.0\.0\.1" --include="*.py" --include="*.js" --include="*.ts" . | grep -v node_modules | grep -v ".git" | grep -v "# Example\|# Default\|# Development" || true)

if [ -n "$good_hosts" ]; then
    echo "✅ Found proper host binding (0.0.0.0):"
    echo "$good_hosts" | head -2
fi

if [ -n "$bad_hosts" ]; then
    echo "⚠️  Found potential localhost/127.0.0.1 bindings:"
    echo "$bad_hosts" | head -3
    echo "Consider updating these to use 0.0.0.0 for production"
fi

# 5. Verify health endpoint exists
echo "📋 5. Checking for health endpoints..."
health_endpoints=$(grep -r "/health\|/api/health" --include="*.py" --include="*.js" --include="*.ts" . | grep -v node_modules | grep -v ".git" || true)
if [ -n "$health_endpoints" ]; then
    echo "✅ Found health endpoints:"
    echo "$health_endpoints" | head -2
else
    echo "❌ No health endpoints found"
    exit 1
fi

# 6. Check railpack.json health check configuration
echo "📋 6. Validating health check configuration in railpack.json..."
for config in railpack.json backend/railpack.json frontend/railpack.json; do
    if [ -f "$config" ]; then
        if grep -q "healthCheckPath" "$config"; then
            health_path=$(grep "healthCheckPath" "$config" | cut -d'"' -f4)
            echo "✅ $config: Health check configured at $health_path"
        else
            echo "⚠️  $config: No health check path configured"
        fi
    fi
done

echo ""
echo "🎉 Railway deployment validation completed successfully!"
echo ""
echo "📋 Quick Fix Commands:"
echo "# Force Railpack rebuild:"
echo "railway up --force"
echo ""
echo "# Debug environment variables:"
echo "railway run env | grep -E '(PORT|HOST|RAILWAY)'"
echo ""
echo "# Test health endpoint locally:"
echo "railway run curl http://localhost:\$PORT/health"