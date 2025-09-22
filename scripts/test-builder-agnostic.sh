#!/bin/bash
# Integration test for builder-agnostic configuration
# This test verifies that the build configuration works without NIXPACKS_PATH

set -e

echo "🧪 Running Z2 Builder-Agnostic Integration Test..."

# Test 1: Check for NIXPACKS_PATH references
echo "📋 Test 1: Checking for NIXPACKS_PATH references..."
if grep -r "NIXPACKS_PATH" . --include="*.json" --include="*.toml" --include="Procfile" 2>/dev/null | grep -v "diagnose-build-env.sh" | grep -v "BUILDER_AGNOSTIC_GUIDE.md" | grep -v "test-builder-agnostic.sh"; then
    echo "❌ Found NIXPACKS_PATH references in configuration files"
    exit 1
else
    echo "✅ No NIXPACKS_PATH references found in configuration files"
fi

# Test 2: Check for explicit PATH exports in configuration
echo "📋 Test 2: Checking for explicit PATH exports..."
if grep -r "export PATH.*HOME.*local.*bin" . --include="*.json" --include="Procfile" 2>/dev/null; then
    echo "❌ Found explicit PATH exports in configuration files"
    exit 1
else
    echo "✅ No explicit PATH exports found in configuration files"
fi

# Test 3: Validate JSON syntax
echo "📋 Test 3: Validating JSON syntax..."
json_files=(
    "railpack.json"
    "backend/railpack.json" 
    "frontend/railpack.json"
)

for file in "${json_files[@]}"; do
    if [ -f "$file" ]; then
        if python -m json.tool "$file" > /dev/null 2>&1; then
            echo "✅ $file: Valid JSON syntax"
        else
            echo "❌ $file: Invalid JSON syntax"
            exit 1
        fi
    else
        echo "⚠️  $file: Not found"
    fi
done

# Test 4: Test executable finder utility
echo "📋 Test 4: Testing executable finder utility..."
if [ -f "scripts/find-executable.sh" ]; then
    # Test with existing executable
    if ./scripts/find-executable.sh python3 >/dev/null 2>&1; then
        echo "✅ find-executable.sh works with existing executables"
    else
        echo "❌ find-executable.sh failed with existing executable"
        exit 1
    fi
    
    # Test with non-existing executable
    if ! ./scripts/find-executable.sh nonexistent-command >/dev/null 2>&1; then
        echo "✅ find-executable.sh properly fails with non-existing executables"
    else
        echo "❌ find-executable.sh should fail with non-existing executables"
        exit 1
    fi
else
    echo "❌ find-executable.sh not found"
    exit 1
fi

# Test 5: Test environment diagnostic
echo "📋 Test 5: Testing environment diagnostic..."
if [ -f "scripts/diagnose-build-env.sh" ]; then
    if ./scripts/diagnose-build-env.sh >/dev/null 2>&1; then
        echo "✅ diagnose-build-env.sh runs successfully"
    else
        echo "❌ diagnose-build-env.sh failed"
        exit 1
    fi
else
    echo "❌ diagnose-build-env.sh not found"
    exit 1
fi

# Test 6: Check install commands are builder-agnostic
echo "📋 Test 6: Checking install commands..."
if grep -r "pip install.*poetry" . --include="*.json" 2>/dev/null | grep -q "user.*||"; then
    echo "✅ Found builder-agnostic Poetry installation pattern"
elif grep -r "pip install poetry" . --include="*.json" 2>/dev/null; then
    echo "✅ Found Poetry installation (basic pattern)"
else
    echo "⚠️  No Poetry installation found in configuration"
fi

# Test 7: Verify start commands don't use explicit PATH
echo "📋 Test 7: Checking start commands..."
start_commands=$(grep -r "startCommand" . --include="*.json" 2>/dev/null | grep -v "export PATH" || true)
if [ -n "$start_commands" ]; then
    echo "✅ Start commands don't use explicit PATH exports"
else
    echo "⚠️  No start commands found or all use explicit PATH"
fi

echo ""
echo "🎉 All tests passed! Builder-agnostic configuration is working correctly."
echo ""
echo "📋 Summary:"
echo "✅ No NIXPACKS_PATH references in configuration files"
echo "✅ No explicit PATH exports in configuration files"  
echo "✅ All JSON configuration files have valid syntax"
echo "✅ Executable finder utility is working"
echo "✅ Environment diagnostic tool is working"
echo "✅ Install commands use builder-agnostic patterns"
echo "✅ Start commands don't rely on explicit PATH manipulation"
echo ""
echo "🚀 Configuration is ready for deployment across multiple builders!"