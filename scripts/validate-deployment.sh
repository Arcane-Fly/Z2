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
if [ -f "railway.json" ]; then
    if ! python3 -c "import json; json.load(open('railway.json'))" 2>/dev/null; then
        echo "❌ railway.json validation failed"
        exit 1
    fi
    echo "✅ railway.json valid"
fi

if [ -f "railpack.json" ]; then
    if ! python3 -c "import json; json.load(open('railpack.json'))" 2>/dev/null; then
        echo "❌ railpack.json validation failed"
        exit 1
    fi
    echo "✅ railpack.json valid"
fi

echo "✅ All validations passed"