#!/bin/bash
set -e

echo "🔍 Validating Railpack configuration..."

# Check if we're in the right directory
if [[ ! -f "railpack.json" ]]; then
    echo "❌ railpack.json not found in current directory"
    exit 1
fi

# Validate JSON syntax
if ! python -m json.tool railpack.json > /dev/null 2>&1; then
    echo "❌ Invalid railpack.json syntax"
    exit 1
fi

# Check for required schema
if ! jq -e '."$schema"' railpack.json | grep -q "schema.railpack.com"; then
    echo "❌ Missing or invalid Railpack schema reference"
    exit 1
fi

# Check for required fields
if ! jq -e '.provider' railpack.json > /dev/null; then
    echo "❌ Missing provider field"
    exit 1
fi

if ! jq -e '.deploy.startCommand' railpack.json > /dev/null; then
    echo "❌ Missing deploy.startCommand"
    exit 1
fi

# Validate provider is python
provider=$(jq -r '.provider' railpack.json)
if [[ "$provider" != "python" ]]; then
    echo "❌ Provider should be 'python', found: $provider"
    exit 1
fi

# Check start command
start_command=$(jq -r '.deploy.startCommand' railpack.json)
if [[ ! "$start_command" =~ uvicorn.*app\.main:app ]]; then
    echo "❌ Start command should contain 'uvicorn app.main:app'"
    exit 1
fi

# Check if start command has proper host and port binding
if [[ ! "$start_command" =~ "--host 0.0.0.0" ]] || [[ ! "$start_command" =~ "--port \$PORT" ]]; then
    echo "❌ Start command should bind to 0.0.0.0 and use \$PORT variable"
    exit 1
fi

echo "✅ Railpack configuration valid"
echo "📋 Configuration summary:"
echo "  Provider: $(jq -r '.provider' railpack.json)"
echo "  Python version: $(jq -r '.packages.python // "default"' railpack.json)"
echo "  Start command: $(jq -r '.deploy.startCommand' railpack.json)"

# Test if the app module can be imported (if we're in the right directory)
if [[ -f "pyproject.toml" ]] && command -v poetry > /dev/null; then
    echo "🧪 Testing if the FastAPI app can be imported..."
    if poetry run python -c "from app.main import app; print('✅ FastAPI app imported successfully')" 2>/dev/null; then
        echo "✅ FastAPI application module is valid"
    else
        echo "⚠️  Warning: Could not import FastAPI app (this is expected if dependencies are not installed)"
    fi
fi

echo "✅ Validation complete"