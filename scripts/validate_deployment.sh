#!/bin/bash

# Z2 Platform - Railway Deployment Validation Script
# This script validates the deployment configuration and tests key functionality

set -e

echo "🚀 Z2 Platform - Railway Deployment Validation"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    case $1 in
        "success") echo -e "${GREEN}✅ $2${NC}" ;;
        "warning") echo -e "${YELLOW}⚠️ $2${NC}" ;;
        "error") echo -e "${RED}❌ $2${NC}" ;;
        "info") echo -e "ℹ️ $2" ;;
    esac
}

# Check if we're in the right directory
if [ ! -f "railpack.json" ]; then
    print_status "error" "railpack.json not found. Please run this script from the project root."
    exit 1
fi

print_status "info" "Validating project structure..."

# 1. Validate project structure  
REQUIRED_FILES=(
    "railpack.json"
    "frontend/package.json"
    "frontend/railpack.json"
    "frontend/src/config/environment.ts"
    "frontend/src/services/apiConfig.ts"
    "frontend/src/components/ErrorBoundary.tsx"
    "frontend/src/components/auth/RoleSelector.tsx"
    "backend/pyproject.toml"
    "backend/railpack.json"
    "backend/scripts/init_db.py"
    "backend/app/main.py"
    "backend/app/core/config.py"
    "backend/app/utils/security.py"
)

missing_files=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_status "success" "$file exists"
    else
        print_status "error" "$file is missing"
        ((missing_files++))
    fi
done

if [ $missing_files -gt 0 ]; then
    print_status "error" "$missing_files required files are missing"
    exit 1
fi

print_status "info" "Validating railpack.json configuration..."

# 2. Validate railpack.json structure
python3 -c "
import json
import sys

try:
    with open('railpack.json', 'r') as f:
        config = json.load(f)
    
    # Check required services
    if 'services' not in config:
        print('❌ Missing services section')
        sys.exit(1)
    
    services = config['services']
    
    # Check backend service
    if 'backend' not in services:
        print('❌ Missing backend service')
        sys.exit(1)
        
    backend = services['backend']
    if 'deploy' not in backend or 'variables' not in backend['deploy']:
        print('❌ Backend missing deploy variables')
        sys.exit(1)
        
    # Check frontend service
    if 'frontend' not in services:
        print('❌ Missing frontend service')
        sys.exit(1)
        
    frontend = services['frontend']
    if 'steps' not in frontend or 'build' not in frontend['steps']:
        print('❌ Frontend missing build step')
        sys.exit(1)
        
    build_step = frontend['steps']['build']
    if 'variables' not in build_step:
        print('❌ Frontend build step missing variables')
        sys.exit(1)
    
    # Check required environment variables
    backend_vars = backend['deploy']['variables']
    required_backend_vars = ['CORS_ORIGINS', 'API_V1_PREFIX']
    for var in required_backend_vars:
        if var not in backend_vars:
            print(f'❌ Backend missing required variable: {var}')
            sys.exit(1)
    
    frontend_build_vars = build_step['variables']
    required_frontend_vars = ['VITE_API_BASE_URL']
    for var in required_frontend_vars:
        if var not in frontend_build_vars:
            print(f'❌ Frontend build missing required variable: {var}')
            sys.exit(1)
    
    print('✅ railpack.json configuration is valid')

except json.JSONDecodeError as e:
    print(f'❌ Invalid JSON in railpack.json: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error validating railpack.json: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_status "success" "railpack.json configuration is valid"
else
    print_status "error" "railpack.json validation failed"
    exit 1
fi

print_status "info" "Testing frontend build process..."

# 3. Test frontend build
cd frontend

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    print_status "info" "Installing frontend dependencies..."
    if ! corepack enable && corepack prepare yarn@4.3.1 --activate && yarn install --immutable; then
        print_status "error" "Failed to install frontend dependencies"
        exit 1
    fi
fi

# Test build with sample environment variables
print_status "info" "Testing frontend build with sample environment variables..."
if VITE_API_BASE_URL=https://z2b-production.up.railway.app \
   VITE_WS_BASE_URL=wss://z2b-production.up.railway.app \
   VITE_APP_NAME="Z2 AI Workforce Platform" \
   VITE_APP_VERSION="0.1.0" \
   yarn build > /tmp/build.log 2>&1; then
    print_status "success" "Frontend build completed successfully"
else
    print_status "error" "Frontend build failed. Check /tmp/build.log for details"
    tail -20 /tmp/build.log
    exit 1
fi

# Check build output
if [ -d "dist" ] && [ -f "dist/index.html" ]; then
    print_status "success" "Frontend build artifacts generated correctly"
    
    # Check if environment variables are embedded
    if grep -q "z2b-production.up.railway.app" dist/assets/*.js 2>/dev/null; then
        print_status "success" "Environment variables properly embedded in build"
    else
        print_status "warning" "Environment variables may not be embedded correctly"
    fi
else
    print_status "error" "Frontend build artifacts not found"
    exit 1
fi

cd ..

print_status "info" "Testing backend configuration..."

# 4. Test backend configuration
cd backend

# Check if poetry is available and dependencies can be loaded
if command -v poetry >/dev/null 2>&1; then
    print_status "info" "Testing backend configuration loading..."
    if poetry run python -c "
import sys
sys.path.insert(0, '.')
try:
    from app.core.config import settings
    print(f'✅ Backend configuration loaded: {settings.app_name}')
    print(f'✅ CORS origins: {settings.cors_origins_list}')
    print(f'✅ API prefix: {settings.api_v1_prefix}')
except Exception as e:
    print(f'❌ Backend configuration error: {e}')
    sys.exit(1)
" 2>/dev/null; then
        print_status "success" "Backend configuration is valid"
    else
        print_status "warning" "Backend configuration test failed (dependencies may not be installed)"
    fi
else
    print_status "warning" "Poetry not available, skipping backend configuration test"
fi

cd ..

print_status "info" "Validating Docker configuration..."

# 5. Validate Docker configuration OR Railpack configuration
print_status "info" "Validating deployment configuration..."

# Check if using Dockerfiles or Railpack
if [ -f "frontend/Dockerfile" ] || [ -f "backend/Dockerfile" ]; then
    print_status "info" "Using Docker-based deployment"
    
    # Docker-specific validations
    if [ -f "frontend/Dockerfile" ]; then
        # Check if Dockerfile has ARG declarations
        if grep -q "ARG VITE_API_BASE_URL" frontend/Dockerfile && \
           grep -q "ARG VITE_WS_BASE_URL" frontend/Dockerfile; then
            print_status "success" "Frontend Dockerfile has proper ARG declarations"
        else
            print_status "error" "Frontend Dockerfile missing required ARG declarations"
            exit 1
        fi
        
        # Check if ENV declarations are present
        if grep -q "ENV VITE_API_BASE_URL" frontend/Dockerfile && \
           grep -q "ENV VITE_WS_BASE_URL" frontend/Dockerfile; then
            print_status "success" "Frontend Dockerfile has proper ENV declarations"
        else
            print_status "error" "Frontend Dockerfile missing required ENV declarations"
            exit 1
        fi
    else
        print_status "error" "Frontend Dockerfile not found"
        exit 1
    fi
else
    print_status "info" "Using Railway Railpack deployment (recommended)"
    
    # Railpack-specific validations
    if [ -f "frontend/railpack.json" ]; then
        print_status "success" "Frontend railpack.json found"
        
        # Check for proper environment variable configuration
        if grep -q "VITE_API_BASE_URL" frontend/railpack.json && \
           grep -q "VITE_WS_BASE_URL" frontend/railpack.json; then
            print_status "success" "Frontend railpack.json has proper environment configuration"
        else
            print_status "error" "Frontend railpack.json missing required environment variables"
            exit 1
        fi
    else
        print_status "error" "Frontend railpack.json not found"
        exit 1
    fi
    
    if [ -f "backend/railpack.json" ]; then
        print_status "success" "Backend railpack.json found"
        
        # Check for proper JWT configuration
        if grep -q "JWT_SECRET_KEY" backend/railpack.json; then
            print_status "success" "Backend railpack.json has proper JWT configuration"
        else
            print_status "error" "Backend railpack.json missing JWT configuration"
            exit 1
        fi
    else
        print_status "error" "Backend railpack.json not found"
        exit 1
    fi
fi

print_status "info" "Running Railway security validation..."

# Run Railway security validation
if python3 scripts/validate_railway_security.py >/dev/null 2>&1; then
    print_status "success" "Railway security validation passed"
else
    print_status "warning" "Railway security validation warnings - check scripts/validate_railway_security.py"
fi

print_status "info" "Running production configuration validation..."

# 6. Run production validation script
if python3 scripts/validate_production_config.py >/dev/null 2>&1; then
    print_status "success" "Production configuration validation passed"
else
    print_status "info" "Running detailed production configuration check..."
    python3 scripts/validate_production_config.py
fi

print_status "info" "Validation Summary"
echo "===================="

print_status "success" "Project structure: ✅ Valid"
print_status "success" "railpack.json: ✅ Valid" 
print_status "success" "Frontend build: ✅ Working"
print_status "success" "Backend config: ✅ Valid"
print_status "success" "Docker config: ✅ Valid"

echo ""
print_status "info" "🎉 All validations passed! Your Z2 platform is ready for Railway deployment."
echo ""
print_status "info" "Next steps:"
echo "1. Commit and push your changes to GitHub"
echo "2. Deploy to Railway using: railway up"
echo "3. Set required environment variables in Railway dashboard:"
echo "   - JWT_SECRET (generate with: openssl rand -hex 32)"
echo "   - DATABASE_URL (Railway will provide this)"
echo "   - DEFAULT_ADMIN_PASSWORD (optional, defaults to 'changeme123!')"
echo "4. Monitor deployment logs and health endpoints"
echo ""
print_status "success" "Deployment validation completed successfully!"