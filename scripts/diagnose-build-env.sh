#!/bin/bash
# Build Environment Diagnostic Script
# Helps diagnose path and executable issues across different builders

echo "=== Build Environment Diagnostic ==="
echo "Date: $(date)"
echo "User: $(whoami)"
echo "Working Directory: $(pwd)"
echo

# Detect builder type
BUILDER_TYPE="unknown"
if [ -n "${NIXPACKS_PATH:-}" ]; then
    BUILDER_TYPE="nixpacks"
    echo "Builder: Nixpacks (detected via NIXPACKS_PATH)"
elif [ -n "${RAILWAY_ENVIRONMENT:-}" ]; then
    BUILDER_TYPE="railway"
    echo "Builder: Railway"
elif [ -n "${VERCEL:-}" ]; then
    BUILDER_TYPE="vercel"
    echo "Builder: Vercel"
elif [ -f "/.dockerenv" ]; then
    BUILDER_TYPE="docker"
    echo "Builder: Docker"
else
    echo "Builder: Unknown/Local"
fi

echo "PATH: $PATH"
echo

# Check for problematic environment variables
echo "=== Environment Variables ==="
env_vars_to_check=(
    "NIXPACKS_PATH"
    "RAILWAY_ENVIRONMENT"
    "HOME"
    "USER"
    "NODE_ENV"
    "PYTHON_VERSION"
    "POETRY_VERSION"
)

for var in "${env_vars_to_check[@]}"; do
    if [ -n "${!var:-}" ]; then
        echo "✅ $var: ${!var}"
    else
        echo "❌ $var: (undefined)"
    fi
done
echo

# Test executable availability
echo "=== Available Executables ==="
executables_to_check=(
    "python"
    "python3"
    "pip"
    "pip3"
    "poetry"
    "node"
    "npm"
    "yarn"
    "git"
    "curl"
    "wget"
)

for cmd in "${executables_to_check[@]}"; do
    if command -v "$cmd" >/dev/null 2>&1; then
        location=$(command -v "$cmd")
        version=$($cmd --version 2>/dev/null | head -n1 || echo "version unknown")
        echo "✅ $cmd: $location ($version)"
    else
        echo "❌ $cmd: not found"
        
        # Try to find in common locations
        found_alternatives=""
        for path in "/usr/local/bin" "/usr/bin" "/bin" "$HOME/.local/bin"; do
            if [ -x "$path/$cmd" ]; then
                found_alternatives="$found_alternatives $path/$cmd"
            fi
        done
        
        if [ -n "$found_alternatives" ]; then
            echo "   Found in alternative locations:$found_alternatives"
        fi
    fi
done
echo

# Check for NIXPACKS_PATH references in codebase
echo "=== Checking for NIXPACKS_PATH References ==="
if command -v grep >/dev/null 2>&1; then
    nixpacks_refs=$(find . -type f \( -name "*.json" -o -name "*.sh" -o -name "*.py" -o -name "*.toml" -o -name "*.yml" -o -name "*.yaml" \) -exec grep -l "NIXPACKS_PATH" {} \; 2>/dev/null || true)
    
    if [ -n "$nixpacks_refs" ]; then
        echo "⚠️  NIXPACKS_PATH references found in:"
        echo "$nixpacks_refs"
        echo
        echo "Detailed references:"
        echo "$nixpacks_refs" | xargs grep -n "NIXPACKS_PATH" 2>/dev/null || true
    else
        echo "✅ No NIXPACKS_PATH references found in codebase"
    fi
else
    echo "❌ Cannot check for NIXPACKS_PATH references (grep not available)"
fi
echo

# Check directory structure and permissions
echo "=== Directory Structure ==="
dirs_to_check=(
    "."
    "./backend"
    "./frontend"
    "./scripts"
    "/usr/local/bin"
    "/usr/bin"
    "/bin"
    "$HOME/.local/bin"
)

for dir in "${dirs_to_check[@]}"; do
    if [ -d "$dir" ]; then
        perms=$(ls -ld "$dir" 2>/dev/null | cut -d' ' -f1 || echo "unknown")
        echo "✅ $dir: exists ($perms)"
        
        # For bin directories, list key executables
        if [[ "$dir" == *"bin"* ]] && [ -d "$dir" ]; then
            key_exes=$(ls "$dir" 2>/dev/null | grep -E '^(python|python3|pip|pip3|poetry|node|npm|yarn)$' | tr '\n' ' ' || true)
            if [ -n "$key_exes" ]; then
                echo "   Key executables: $key_exes"
            fi
        fi
    else
        echo "❌ $dir: does not exist"
    fi
done
echo

# Check build configuration files
echo "=== Build Configuration Files ==="
config_files=(
    "railpack.json"
    "backend/railpack.json"
    "frontend/railpack.json"
    "backend/Procfile"
    "frontend/Procfile"
    "backend/pyproject.toml"
    "frontend/package.json"
    "nixpacks.toml"
    "backend/nixpacks.toml"
    "frontend/nixpacks.toml"
)

for file in "${config_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file: exists"
        
        # Check for problematic patterns
        if grep -q "NIXPACKS_PATH" "$file" 2>/dev/null; then
            echo "   ⚠️  Contains NIXPACKS_PATH references"
        fi
        
        if grep -q '\$HOME/.local/bin' "$file" 2>/dev/null; then
            echo "   ⚠️  Contains HOME/.local/bin references"
        fi
    else
        echo "❌ $file: not found"
    fi
done
echo

# Summary and recommendations
echo "=== Summary & Recommendations ==="
echo "Builder Type: $BUILDER_TYPE"

# Generate recommendations based on findings
if [ "$BUILDER_TYPE" = "nixpacks" ] && command -v python3 >/dev/null 2>&1; then
    echo "✅ Nixpacks environment appears functional"
elif [ "$BUILDER_TYPE" = "railway" ] && command -v python3 >/dev/null 2>&1; then
    echo "✅ Railway environment appears functional"
elif command -v python3 >/dev/null 2>&1 && command -v node >/dev/null 2>&1; then
    echo "✅ Build environment appears functional"
else
    echo "⚠️  Build environment may have issues"
    echo "Recommendations:"
    echo "- Verify required executables are installed"
    echo "- Check PATH configuration"
    echo "- Review builder-specific documentation"
fi

echo
echo "=== Diagnostic Complete ==="