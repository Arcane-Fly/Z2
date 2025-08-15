#!/bin/bash
set -e

echo "🔍 Validating deployment configuration..."

# Check frontend lockfile
echo "Checking frontend dependencies..."
cd frontend
if ! yarn install --immutable --check-cache; then
    echo "❌ Frontend lockfile validation failed"
    exit 1
fi
echo "✅ Frontend dependencies valid"

# Check backend dependencies
echo "Checking backend dependencies..."
cd ../backend
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Backend pyproject.toml not found"
    exit 1
fi
# Basic syntax check for pyproject.toml
python3 -c "
with open('pyproject.toml', 'r') as f:
    content = f.read()
# Basic validation - check it's not empty and contains expected sections
if '[tool.poetry]' in content or '[project]' in content:
    print('✅ Backend dependencies valid')
else:
    raise ValueError('Missing expected sections')
"

# Check Railway configuration
echo "Checking Railway configuration..."
cd ..

# Validate railway.json for Docker deployment
if [ -f "railway.json" ]; then
    if ! python3 -c "import json; json.load(open('railway.json'))" 2>/dev/null; then
        echo "❌ railway.json validation failed"
        exit 1
    fi
    BUILDER=$(python3 -c "import json; print(json.load(open('railway.json')).get('build', {}).get('builder', 'none'))")
    echo "✅ railway.json valid, using builder: $BUILDER"
fi

if [ -f "railpack.json" ]; then
    if ! python3 -c "import json; json.load(open('railpack.json'))" 2>/dev/null; then
        echo "❌ railpack.json validation failed"
        exit 1
    fi
    
    # Check for conflicting startCommand in frontend (should not exist when using Docker)
    FRONTEND_START=$(python3 -c "
import json
try:
    data = json.load(open('railpack.json'))
    print(data.get('services', {}).get('frontend', {}).get('deploy', {}).get('startCommand', 'none'))
except:
    print('none')
" 2>/dev/null)
    
    if [ "$FRONTEND_START" != "none" ]; then
        echo "⚠️  Warning: Frontend has startCommand in railpack.json but should use Docker"
    else
        echo "✅ Frontend deployment config clean (no yarn startCommand conflict)"
    fi
    
    echo "✅ railpack.json valid"
fi

# Check for container startup compatibility
echo "Checking container configuration..."
if [ -f "frontend/Dockerfile" ]; then
    if grep -q "nginx:alpine" frontend/Dockerfile && grep -q 'CMD.*nginx.*daemon off' frontend/Dockerfile; then
        echo "✅ Frontend Dockerfile properly configured for nginx"
    else
        echo "⚠️  Warning: Frontend Dockerfile may have startup issues"
    fi
fi

echo "✅ All validations passed"