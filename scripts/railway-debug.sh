#!/bin/bash
echo "📊 Railway Deployment Diagnostics"
echo "================================="
echo "Build System: ${RAILWAY_BUILDER:-Not Set}"
echo "Environment: ${RAILWAY_ENVIRONMENT:-Not Set}"
echo "Service: ${RAILWAY_SERVICE_NAME:-Not Set}"
echo "Node Version: $(node -v 2>/dev/null || echo 'Not Available')"
echo "Yarn Version: $(yarn -v 2>/dev/null || echo 'Not Available')"
echo "Python Version: $(python3 --version 2>/dev/null || echo 'Not Available')"
echo "Current Directory: $(pwd)"
echo "Directory Contents:"
ls -la
echo ""
echo "Package Manager Configuration:"
if [ -f "package.json" ]; then
    echo "packageManager field: $(grep -o '"packageManager": "[^"]*"' package.json || echo 'Not set')"
fi
if [ -f ".yarnrc.yml" ]; then
    echo "Yarn configuration found:"
    cat .yarnrc.yml
fi
echo ""
echo "Railway Configuration Files:"
[ -f "../railway.json" ] && echo "✅ railway.json found" || echo "❌ railway.json missing"
[ -f "../railpack.json" ] && echo "✅ railpack.json found" || echo "❌ railpack.json missing"
echo "================================="