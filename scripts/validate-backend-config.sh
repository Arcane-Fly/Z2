#!/bin/bash
# Railway Configuration Validation Script for Backend Service

set -e

echo "🔍 Validating Railway backend configuration..."

# Check if we're in the backend directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the backend directory."
    exit 1
fi

echo "✅ Found pyproject.toml"

# Validate railpack.json syntax
if [ -f "railpack.json" ]; then
    echo "✅ Found railpack.json"
    
    # Check JSON syntax
    if jq empty railpack.json 2>/dev/null; then
        echo "✅ railpack.json has valid JSON syntax"
    else
        echo "❌ Error: railpack.json has invalid JSON syntax"
        exit 1
    fi
    
    # Check for required fields
    if jq -e '.provider' railpack.json >/dev/null 2>&1; then
        PROVIDER=$(jq -r '.provider' railpack.json)
        echo "✅ Provider configured: $PROVIDER"
    else
        echo "❌ Error: Missing provider field in railpack.json"
        exit 1
    fi
    
    if jq -e '.steps.install.commands' railpack.json >/dev/null 2>&1; then
        echo "✅ Install steps configured"
        
        # Check if Poetry installation is included
        if jq -e '.steps.install.commands[] | select(test("poetry"))' railpack.json >/dev/null 2>&1; then
            echo "✅ Poetry installation command found"
        else
            echo "❌ Warning: No Poetry installation command found"
        fi
    else
        echo "❌ Error: Missing install steps in railpack.json"
        exit 1
    fi
    
    if jq -e '.deploy.startCommand' railpack.json >/dev/null 2>&1; then
        START_CMD=$(jq -r '.deploy.startCommand' railpack.json)
        echo "✅ Start command configured: $START_CMD"
        
        # Check if start command uses Poetry
        if echo "$START_CMD" | grep -q "poetry run"; then
            echo "✅ Start command uses Poetry"
        else
            echo "⚠️  Warning: Start command doesn't use Poetry"
        fi
    else
        echo "❌ Error: Missing start command in railpack.json"
        exit 1
    fi
    
    # Check volume configuration
    if jq -e '.volumes' railpack.json >/dev/null 2>&1; then
        echo "✅ Volume configuration found"
        MOUNT_PATH=$(jq -r '.volumes[0].mountPath' railpack.json 2>/dev/null || echo "")
        if [ -n "$MOUNT_PATH" ]; then
            echo "✅ Volume mount path: $MOUNT_PATH"
        fi
    else
        echo "⚠️  Warning: No volume configuration found"
    fi
    
else
    echo "❌ Error: railpack.json not found"
    exit 1
fi

# Validate railway.json if present
if [ -f "railway.json" ]; then
    echo "✅ Found railway.json"
    
    if jq empty railway.json 2>/dev/null; then
        echo "✅ railway.json has valid JSON syntax"
        
        # Check builder configuration
        if jq -e '.build.builder' railway.json >/dev/null 2>&1; then
            BUILDER=$(jq -r '.build.builder' railway.json)
            echo "✅ Builder configured: $BUILDER"
        else
            echo "⚠️  Warning: No builder specified in railway.json"
        fi
    else
        echo "❌ Error: railway.json has invalid JSON syntax"
        exit 1
    fi
fi

# Check FastAPI app module
echo "🔍 Checking FastAPI application..."
if [ -d "app" ] && [ -f "app/main.py" ]; then
    echo "✅ FastAPI app directory structure found"
    
    # Check if main.py has app variable
    if grep -q "app.*=.*FastAPI" app/main.py 2>/dev/null; then
        echo "✅ FastAPI app instance found in main.py"
    else
        echo "⚠️  Warning: Could not verify FastAPI app instance in main.py"
    fi
else
    echo "❌ Error: FastAPI app structure not found (app/main.py)"
    exit 1
fi

echo ""
echo "🎉 Backend configuration validation completed successfully!"
echo ""
echo "📋 Next steps for Railway deployment:"
echo "1. Create a new service in Railway"
echo "2. Set root directory to 'backend/'"
echo "3. Railway will automatically detect and use:"
echo "   - railpack.json for build configuration"
echo "   - railway.json for builder specification"
echo "4. Monitor deployment logs for 'Using Railpack' confirmation"
echo ""