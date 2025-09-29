#!/bin/bash
set -euo pipefail

# Migration Validation Script
# This script validates that migrations were successful and the application is working correctly

echo "🔍 Validating Migration Results"
echo "==============================="

cd frontend

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Validation results
PASSED=0
FAILED=0
WARNINGS=0

# Function to log results
log_result() {
  local status=$1
  local message=$2
  
  case $status in
    "PASS")
      echo -e "✅ ${GREEN}PASS${NC}: $message"
      ((PASSED++))
      ;;
    "FAIL")
      echo -e "❌ ${RED}FAIL${NC}: $message"
      ((FAILED++))
      ;;
    "WARN")
      echo -e "⚠️  ${YELLOW}WARN${NC}: $message"  
      ((WARNINGS++))
      ;;
  esac
}

echo "📋 Running validation checklist..."
echo ""

# 1. TypeScript compilation
echo "🔧 Checking TypeScript compilation..."
if yarn type-check; then
  log_result "PASS" "TypeScript compilation successful"
else
  log_result "FAIL" "TypeScript compilation failed"
fi

# 2. Build process
echo ""
echo "🏗️  Testing build process..."
if yarn build; then
  log_result "PASS" "Application builds without errors"
  
  # Check for build artifacts
  if [ -d "dist" ]; then
    log_result "PASS" "Build output directory created"
    
    # Check bundle sizes
    if [ -f "dist/assets/index-*.js" ]; then
      BUNDLE_SIZE=$(du -h dist/assets/index-*.js | cut -f1)
      log_result "PASS" "Main bundle created (Size: $BUNDLE_SIZE)"
      
      # Warn if bundle is too large
      BUNDLE_SIZE_BYTES=$(du -b dist/assets/index-*.js | cut -f1)
      if [ "$BUNDLE_SIZE_BYTES" -gt 1048576 ]; then # > 1MB
        log_result "WARN" "Main bundle size is large (${BUNDLE_SIZE}). Consider code splitting."
      fi
    else
      log_result "FAIL" "Main bundle not found in build output"
    fi
  else
    log_result "FAIL" "Build output directory not created"
  fi
else
  log_result "FAIL" "Build process failed"
fi

# 3. Test suite
echo ""  
echo "🧪 Running test suite..."
if yarn test --run; then
  log_result "PASS" "All tests pass"
else
  log_result "FAIL" "Some tests failed"
fi

# 4. Feature directory structure validation
echo ""
echo "📁 Validating feature-based architecture..."

REQUIRED_FEATURES=("auth" "dashboard" "agents" "workflows" "models")
for feature in "${REQUIRED_FEATURES[@]}"; do
  if [ -d "src/features/$feature" ]; then
    log_result "PASS" "Feature directory exists: $feature"
    
    # Check for required subdirectories
    for subdir in "components" "hooks" "services" "types"; do
      if [ -d "src/features/$feature/$subdir" ]; then
        log_result "PASS" "  └─ $subdir directory exists"
      else
        log_result "WARN" "  └─ $subdir directory missing (may be normal if unused)"
      fi
    done
  else
    log_result "FAIL" "Feature directory missing: $feature"
  fi
done

# 5. Shared directory structure validation
echo ""
echo "🔗 Validating shared architecture..."

REQUIRED_SHARED=("components" "hooks" "utils" "types" "services")
for shared in "${REQUIRED_SHARED[@]}"; do
  if [ -d "src/shared/$shared" ]; then
    log_result "PASS" "Shared directory exists: $shared"
  else
    log_result "FAIL" "Shared directory missing: $shared"
  fi
done

# 6. Component co-location validation
echo ""
echo "🏠 Validating component co-location..."

COLOCATED_COUNT=0
TOTAL_COMPONENTS=0

find src -name "*.tsx" -not -path "*/node_modules/*" | while read -r component; do
  if [[ "$component" =~ /([^/]+)\.tsx$ ]]; then
    component_name="${BASH_REMATCH[1]}"
    component_dir=$(dirname "$component")
    
    # Skip if it's already in a component-specific directory
    if [[ "$component_dir" =~ /${component_name}$ ]]; then
      TOTAL_COMPONENTS=$((TOTAL_COMPONENTS + 1))
      
      # Check for co-located files
      has_test=false
      has_index=false
      
      if [ -f "$component_dir/${component_name}.test.tsx" ] || [ -f "$component_dir/${component_name}.test.ts" ]; then
        has_test=true
      fi
      
      if [ -f "$component_dir/index.ts" ]; then
        has_index=true
      fi
      
      if [ "$has_test" = true ] || [ "$has_index" = true ]; then
        COLOCATED_COUNT=$((COLOCATED_COUNT + 1))
      fi
    fi
  fi
done

# 7. Import path validation
echo ""
echo "🔗 Validating import paths..."

# Check for old import patterns that should be updated
OLD_IMPORTS=$(grep -r "from '\.\./\.\./components" src/ 2>/dev/null | wc -l || echo 0)
if [ "$OLD_IMPORTS" -eq 0 ]; then
  log_result "PASS" "No legacy component import paths found"
else
  log_result "WARN" "$OLD_IMPORTS files still use legacy import paths"
fi

# Check for proper alias usage
ALIAS_USAGE=$(grep -r "from '@/" src/ 2>/dev/null | wc -l || echo 0)
if [ "$ALIAS_USAGE" -gt 0 ]; then
  log_result "PASS" "Path aliases are being used ($ALIAS_USAGE imports)"
else
  log_result "WARN" "Path aliases not being used - consider updating imports"
fi

# 8. TypeScript strict mode validation
echo ""
echo "🔒 Validating TypeScript configuration..."

if [ -f "tsconfig.json" ]; then
  if grep -q '"strict": true' tsconfig.json; then
    log_result "PASS" "TypeScript strict mode is enabled"
  else
    log_result "FAIL" "TypeScript strict mode is not enabled"
  fi
  
  if grep -q '"paths"' tsconfig.json; then
    log_result "PASS" "Path mapping is configured"
  else
    log_result "WARN" "Path mapping not configured in tsconfig.json"
  fi
else
  log_result "FAIL" "tsconfig.json not found"
fi

# 9. Bundle optimization validation
echo ""
echo "⚡ Validating bundle optimization..."

if [ -f "vite.config.ts" ]; then
  if grep -q "manualChunks" vite.config.ts; then
    log_result "PASS" "Manual chunk splitting is configured"
  else
    log_result "WARN" "Manual chunk splitting not configured"
  fi
  
  if grep -q "terser" vite.config.ts; then
    log_result "PASS" "Minification is configured"
  else
    log_result "WARN" "Minification not explicitly configured"
  fi
else
  log_result "FAIL" "vite.config.ts not found"
fi

# 10. Package.json validation
echo ""
echo "📦 Validating package configuration..."

if grep -q '"sideEffects"' package.json; then
  log_result "PASS" "sideEffects field is configured for tree-shaking"
else
  log_result "WARN" "sideEffects field not configured - may impact tree-shaking"
fi

# 11. Development server test
echo ""
echo "🖥️  Testing development server..."

# Start dev server in background and test it
echo "Starting development server for validation..."
timeout 30s yarn dev &
DEV_PID=$!

sleep 10

if kill -0 $DEV_PID 2>/dev/null; then
  log_result "PASS" "Development server starts successfully"
  kill $DEV_PID 2>/dev/null || true
else
  log_result "FAIL" "Development server failed to start"
fi

# 12. ESLint validation
echo ""
echo "📏 Running ESLint validation..."

if command -v eslint &> /dev/null; then
  if yarn lint --max-warnings 0; then
    log_result "PASS" "ESLint passes with no warnings"
  else
    log_result "WARN" "ESLint found issues (may be acceptable)"
  fi
else
  log_result "WARN" "ESLint not available for validation"
fi

# Summary
echo ""
echo "📊 Validation Summary"
echo "===================="
echo -e "✅ ${GREEN}Passed${NC}: $PASSED"
echo -e "⚠️  ${YELLOW}Warnings${NC}: $WARNINGS"
echo -e "❌ ${RED}Failed${NC}: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}🎉 Migration validation successful!${NC}"
  echo ""
  echo "Next steps:"
  echo "1. Review any warnings above"
  echo "2. Test the application manually in a browser"
  echo "3. Monitor performance metrics"
  echo "4. Consider running additional integration tests"
  
  exit 0
else
  echo -e "${RED}❌ Migration validation failed!${NC}"
  echo ""
  echo "Please address the failed checks above before proceeding."
  echo "Consider rolling back the migration if issues are severe."
  
  exit 1
fi