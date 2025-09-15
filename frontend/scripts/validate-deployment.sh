#!/bin/bash
set -e

echo "🔍 Validating Z2F deployment configuration..."

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
  echo "❌ This script should be run from the frontend directory"
  exit 1
fi

# Check Dockerfile syntax by attempting to build
echo "📦 Testing Docker build..."
if ! docker build --no-cache -f Dockerfile -t z2f-validation-test . > /dev/null 2>&1; then
  echo "❌ Dockerfile build failed"
  exit 1
fi

# Verify nginx configuration template has correct PORT variable
echo "🔧 Checking nginx template..."
if ! grep -q 'listen ${PORT}' nginx.conf.template; then
  echo "❌ nginx.conf.template missing PORT variable"
  exit 1
fi

# Ensure railway.json exists and doesn't have conflicting start command
echo "🚂 Validating Railway configuration..."
if [ ! -f "railway.json" ]; then
  echo "❌ railway.json missing"
  exit 1
fi

# Check if railway.json has a startCommand that might conflict
if grep -q '"startCommand".*yarn\|npm\|node' railway.json 2>/dev/null; then
  echo "⚠️  Warning: Node.js start command found in railway.json - this may conflict with nginx container"
fi

# Validate no yarn/node commands in production stage of Dockerfile
if grep -A20 "FROM nginx" Dockerfile | grep -E "yarn|npm|node"; then
  echo "⚠️  Warning: Node.js commands found in nginx stage"
fi

# Check if ENTRYPOINT is explicitly set
if ! grep -q "ENTRYPOINT.*nginx" Dockerfile; then
  echo "⚠️  Warning: No explicit nginx ENTRYPOINT found"
fi

echo "✅ Deployment configuration validated successfully"
echo "🏗️  Multi-stage build separates Node.js build from nginx runtime"
echo "🌐 nginx will serve static assets on Railway's dynamic PORT"