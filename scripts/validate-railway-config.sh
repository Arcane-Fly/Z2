#!/bin/bash

# ❌ DEPRECATED: This script is outdated and conflicts with Railway Deployment Master Cheat Sheet
# 
# 🚨 WARNING: This script references railway.json, Dockerfile, and nginx configurations
# that should NOT exist in a railpack-only deployment.
#
# ✅ USE INSTEAD: scripts/railway-railpack-validation.sh
# This enforces the correct Railway Deployment Master Cheat Sheet standards:
# - Railpack-only configuration (no competing build files)
# - Proper PORT/HOST binding
# - Health check validation

echo "❌ DEPRECATED SCRIPT"
echo "==================="
echo
echo "This script is deprecated and conflicts with Railway Deployment Master Cheat Sheet."
echo "It references railway.json and other competing build configurations that should NOT exist."
echo
echo "✅ Use the correct validation script instead:"
echo "   bash scripts/railway-railpack-validation.sh"
echo
echo "The new script enforces railpack-only standards per Railway best practices."
echo

exit 1
        echo "❌ Dockerfile builder not configured"
        exit 1
    fi
    
    # Check for health check
    if grep -q '"healthcheckPath"' frontend/railway.json; then
        echo "✅ Health check path configured"
    else
        echo "⚠️  Health check path not configured (recommended)"
    fi
else
    echo "❌ frontend/railway.json missing"
    exit 1
fi

# Check frontend Dockerfile
if [ -f "frontend/Dockerfile" ]; then
    echo "✅ frontend/Dockerfile exists"
    
    # Verify multi-stage build
    if grep -q "FROM node.*AS build" frontend/Dockerfile && grep -q "FROM nginx:alpine" frontend/Dockerfile; then
        echo "✅ Multi-stage Dockerfile (Node.js build → nginx runtime)"
    else
        echo "❌ Dockerfile not configured for multi-stage build"
        exit 1
    fi
    
    # Check for nginx CMD
    if grep -q 'CMD.*nginx.*daemon off' frontend/Dockerfile; then
        echo "✅ Nginx daemon off command in Dockerfile"
    else
        echo "❌ Missing nginx daemon off command"
        exit 1
    fi
else
    echo "❌ frontend/Dockerfile missing"
    exit 1
fi

# Check backend configuration  
echo
echo "Backend Configuration:"
echo "----------------------"

if [ -f "backend/railway.toml" ]; then
    echo "✅ backend/railway.toml exists"
    
    # Check for uvicorn startCommand
    if grep -q 'startCommand.*uvicorn' backend/railway.toml; then
        echo "✅ uvicorn startCommand configured"
    else
        echo "❌ uvicorn startCommand missing or incorrect"
        exit 1
    fi
    
    # Check for health check
    if grep -q 'healthcheckPath.*health' backend/railway.toml; then
        echo "✅ Health check path configured"
    else
        echo "❌ Health check path not configured"
        exit 1
    fi
else
    echo "❌ backend/railway.toml missing"
    exit 1
fi

# Check backend health endpoint
if [ -f "backend/app/main.py" ]; then
    if grep -q '@app\.get("/health")' backend/app/main.py; then
        echo "✅ Backend health endpoint exists"
    else
        echo "❌ Backend health endpoint missing"
        exit 1
    fi
else
    echo "❌ backend/app/main.py missing"
    exit 1
fi

# Check nginx health endpoint
if [ -f "frontend/nginx.conf.template" ]; then
    if grep -q 'location /health' frontend/nginx.conf.template; then
        echo "✅ Frontend nginx health endpoint exists"
    else
        echo "⚠️  Frontend nginx health endpoint missing (recommended)"
    fi
else
    echo "⚠️  frontend/nginx.conf.template missing"
fi

echo
echo "✅ All critical Railway configurations validated successfully!"
echo
echo "🚀 Ready for Railway deployment:"
echo "  - Frontend: Dockerfile with nginx startCommand override"
echo "  - Backend: nixpacks with uvicorn startCommand"
echo "  - Health checks: Configured for both services"
echo
echo "Next steps:"
echo "  1. Push changes to trigger Railway deployment"
echo "  2. Monitor logs: railway logs --service <service-name> --tail"
echo "  3. Verify health checks: curl https://<domain>/health"