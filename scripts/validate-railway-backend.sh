#!/bin/bash
# Railway Backend Configuration Validator
# Validates that backend is properly configured for Railway deployment

set -e

echo "================================"
echo "Railway Backend Validator"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
ISSUES=0

# Navigate to script directory
cd "$(dirname "$0")/.."

echo "1. Checking backend/railpack.json exists..."
if [ -f "backend/railpack.json" ]; then
    echo -e "${GREEN}✓${NC} backend/railpack.json found"
else
    echo -e "${RED}✗${NC} backend/railpack.json NOT FOUND"
    ISSUES=$((ISSUES + 1))
    echo ""
    echo "Cannot continue without backend/railpack.json"
    exit 1
fi

echo ""
echo "2. Validating backend/railpack.json syntax..."
if python3 -m json.tool backend/railpack.json > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Valid JSON syntax"
else
    echo -e "${RED}✗${NC} Invalid JSON syntax"
    ISSUES=$((ISSUES + 1))
    echo ""
    echo "Cannot continue with invalid JSON"
    exit 1
fi

# Parse JSON once and store in variable
echo ""
echo "3. Loading railpack.json configuration..."
RAILPACK_JSON=$(cat backend/railpack.json)

echo ""
echo "4. Checking railpack.json provider..."
PROVIDER=$(echo "$RAILPACK_JSON" | python3 -c "import json, sys; data = json.load(sys.stdin); print(data.get('build', {}).get('provider', ''))" 2>/dev/null)
if [ "$PROVIDER" = "python" ]; then
    echo -e "${GREEN}✓${NC} Provider is 'python'"
elif [ -z "$PROVIDER" ]; then
    echo -e "${RED}✗${NC} Provider field not found in railpack.json"
    ISSUES=$((ISSUES + 1))
else
    echo -e "${RED}✗${NC} Provider is not 'python' (found: '$PROVIDER')"
    ISSUES=$((ISSUES + 1))
fi

echo ""
echo "5. Checking start command..."
START_CMD=$(echo "$RAILPACK_JSON" | python3 -c "import json, sys; data = json.load(sys.stdin); print(data.get('deploy', {}).get('startCommand', ''))" 2>/dev/null)
if [ -z "$START_CMD" ]; then
    echo -e "${RED}✗${NC} Start command not found in railpack.json"
    ISSUES=$((ISSUES + 1))
elif echo "$START_CMD" | grep -q "uvicorn"; then
    echo -e "${GREEN}✓${NC} Start command uses uvicorn"
    if echo "$START_CMD" | grep -q "\$PORT"; then
        echo -e "${GREEN}✓${NC} Start command uses \$PORT variable"
    else
        echo -e "${YELLOW}⚠${NC} Start command doesn't use \$PORT variable"
        ISSUES=$((ISSUES + 1))
    fi
    if echo "$START_CMD" | grep -q "0.0.0.0"; then
        echo -e "${GREEN}✓${NC} Start command binds to 0.0.0.0"
    else
        echo -e "${YELLOW}⚠${NC} Start command doesn't bind to 0.0.0.0"
        ISSUES=$((ISSUES + 1))
    fi
else
    echo -e "${RED}✗${NC} Start command doesn't use uvicorn (found: '$START_CMD')"
    ISSUES=$((ISSUES + 1))
fi

echo ""
echo "6. Checking health check path..."
HEALTH_PATH=$(echo "$RAILPACK_JSON" | python3 -c "import json, sys; data = json.load(sys.stdin); print(data.get('deploy', {}).get('healthCheckPath', ''))" 2>/dev/null)
if [ "$HEALTH_PATH" = "/health" ]; then
    echo -e "${GREEN}✓${NC} Health check path is '/health'"
elif [ -z "$HEALTH_PATH" ]; then
    echo -e "${YELLOW}⚠${NC} Health check path not found in railpack.json"
else
    echo -e "${YELLOW}⚠${NC} Health check path is not '/health' (found: '$HEALTH_PATH')"
fi

echo ""
echo "7. Checking for competing configuration files..."
COMPETING=0
for file in "backend/Dockerfile" "backend/railway.toml" "backend/railway.json" "backend/nixpacks.toml"; do
    if [ -f "$file" ]; then
        echo -e "${RED}✗${NC} Found competing config: $file"
        COMPETING=$((COMPETING + 1))
        ISSUES=$((ISSUES + 1))
    fi
done
if [ $COMPETING -eq 0 ]; then
    echo -e "${GREEN}✓${NC} No competing configuration files found"
fi

echo ""
echo "8. Checking health endpoint implementation..."
# Look for health endpoint in main.py using multiple patterns
if grep -qE '@app\.get.*health|@router\.get.*health|def health_check|async def health_check' backend/app/main.py 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Health check endpoint found in backend/app/main.py"
elif [ -f "backend/app/api/v1/endpoints/health.py" ]; then
    echo -e "${GREEN}✓${NC} Health check endpoint module found at backend/app/api/v1/endpoints/health.py"
else
    echo -e "${YELLOW}⚠${NC} Health check endpoint implementation not clearly detected"
    echo "  (This may be a false warning if the endpoint exists but uses a different pattern)"
fi

echo ""
echo "9. Checking pyproject.toml exists..."
if [ -f "backend/pyproject.toml" ]; then
    echo -e "${GREEN}✓${NC} backend/pyproject.toml found"
else
    echo -e "${RED}✗${NC} backend/pyproject.toml NOT FOUND"
    ISSUES=$((ISSUES + 1))
fi

echo ""
echo "================================"
echo "Validation Summary"
echo "================================"

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Backend code configuration is correct."
    echo ""
    echo -e "${YELLOW}IMPORTANT:${NC} The Railway service itself must be configured with:"
    echo "  - Root Directory: backend"
    echo "  - Builder: Railpack (auto-detect)"
    echo ""
    echo "See docs/RAILWAY_BACKEND_FIX.md for instructions."
    exit 0
else
    echo -e "${RED}✗ Found $ISSUES issue(s)${NC}"
    echo ""
    echo "Please fix the issues above before deploying."
    exit 1
fi
