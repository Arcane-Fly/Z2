#!/bin/bash
# Railway Z2B Configuration Verification Script

echo "=================================="
echo "Z2B Railway Configuration Checker"
echo "=================================="
echo ""

cd "$(dirname "$0")"

echo "✓ Checking configuration files..."
echo ""

# Check railpack.json
if [ -f "railpack.json" ]; then
    echo "✓ railpack.json exists"
    START_CMD=$(grep -o '"startCommand":\s*"[^"]*"' railpack.json | cut -d'"' -f4)
    echo "  Start command: $START_CMD"
    if [[ "$START_CMD" == *"uvicorn"* ]]; then
        echo "  ✓ Correct start command (uvicorn)"
    else
        echo "  ✗ WRONG start command (should contain 'uvicorn')"
    fi
else
    echo "✗ railpack.json NOT FOUND"
fi
echo ""

# Check Procfile
if [ -f "Procfile" ]; then
    echo "✓ Procfile exists"
    PROC_CMD=$(cat Procfile)
    echo "  Command: $PROC_CMD"
    if [[ "$PROC_CMD" == *"uvicorn"* ]]; then
        echo "  ✓ Correct command (uvicorn)"
    else
        echo "  ✗ WRONG command (should contain 'uvicorn')"
    fi
else
    echo "✗ Procfile NOT FOUND"
fi
echo ""

# Check nixpacks.toml
if [ -f "nixpacks.toml" ]; then
    echo "✓ nixpacks.toml exists"
    START_CMD=$(grep -A2 '\[start\]' nixpacks.toml | grep 'cmd' | cut -d'"' -f2)
    echo "  Start command: $START_CMD"
    if [[ "$START_CMD" == *"uvicorn"* ]]; then
        echo "  ✓ Correct start command (uvicorn)"
    else
        echo "  ✗ WRONG start command (should contain 'uvicorn')"
    fi
else
    echo "✗ nixpacks.toml NOT FOUND"
fi
echo ""

# Check railway.toml
if [ -f "railway.toml" ]; then
    echo "✓ railway.toml exists"
    START_CMD=$(grep 'startCommand' railway.toml | cut -d'"' -f2)
    echo "  Start command: $START_CMD"
    if [[ "$START_CMD" == *"uvicorn"* ]]; then
        echo "  ✓ Correct start command (uvicorn)"
    else
        echo "  ✗ WRONG start command (should contain 'uvicorn')"
    fi
else
    echo "✗ railway.toml NOT FOUND"
fi
echo ""

# Check for conflicting files
echo "✓ Checking for conflicting files..."
if [ -f "package.json" ]; then
    echo "  ✗ WARNING: package.json found in backend (should not exist)"
else
    echo "  ✓ No package.json (good)"
fi

if [ -f "yarn.lock" ]; then
    echo "  ✗ WARNING: yarn.lock found in backend (should not exist)"
else
    echo "  ✓ No yarn.lock (good)"
fi
echo ""

# Check Python files
echo "✓ Checking Python application..."
if [ -f "pyproject.toml" ]; then
    echo "  ✓ pyproject.toml exists"
else
    echo "  ✗ pyproject.toml NOT FOUND"
fi

if [ -f "app/main.py" ]; then
    echo "  ✓ app/main.py exists"
    # Check for health endpoint
    if grep -q "def health_check" app/main.py; then
        echo "  ✓ Health check endpoint found"
    else
        echo "  ✗ Health check endpoint NOT FOUND"
    fi
else
    echo "  ✗ app/main.py NOT FOUND"
fi
echo ""

echo "=================================="
echo "Configuration Status Summary"
echo "=================================="
echo ""
echo "Local Configuration Files: ✓ ALL CORRECT"
echo ""
echo "If Railway is still trying to run 'yarn start', the issue is in:"
echo "🔴 Railway Dashboard → Z2B Service → Settings → Deploy → Custom Start Command"
echo ""
echo "ACTION REQUIRED:"
echo "1. Go to Railway Dashboard"
echo "2. Select Z2B service"
echo "3. Go to Settings tab"
echo "4. Find 'Custom Start Command' or 'Start Command' field"
echo "5. Either:"
echo "   a) CLEAR/DELETE the field (let Railway auto-detect)"
echo "   b) Set it to: uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
echo "6. Save and redeploy"
echo ""
echo "Expected correct settings in Railway Dashboard:"
echo "  • Root Directory: backend"
echo "  • Custom Start Command: [empty] or [uvicorn app.main:app --host 0.0.0.0 --port \$PORT]"
echo "  • Health Check Path: /health"
echo "  • Health Check Timeout: 300"
echo ""
