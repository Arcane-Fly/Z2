#!/bin/bash

# Railway Build Simulation Script
# This script simulates the Railway build environment to test our fixes

set -e

echo "🚂 Railway Build Environment Simulation"
echo "========================================"

echo "📋 Environment Info:"
echo "Node Version: $(node -v)"
echo "Initial Yarn Version: $(yarn -v)"
echo "Working Directory: $(pwd)"

echo ""
echo "🔧 Phase 1: Corepack Activation (as Railway would do)"
corepack enable
corepack prepare yarn@4.9.2 --activate

echo "Yarn Version after corepack: $(yarn -v)"

echo ""
echo "🔨 Phase 2: Dependencies Installation"
yarn install --immutable

echo ""
echo "🏗️ Phase 3: Frontend Build"
cd frontend
yarn install --immutable
yarn build

echo ""
echo "🚀 Phase 4: Preview Server Test (simulate Railway deployment)"
echo "Testing vite preview command format..."

# Test the command that Railway would use
echo "Command: yarn vite preview --host 0.0.0.0 --port 4173"
timeout 5s yarn vite preview --host 0.0.0.0 --port 4173 &
SERVER_PID=$!
sleep 3

if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✅ Preview server started successfully!"
    kill $SERVER_PID
else
    echo "❌ Preview server failed to start"
    exit 1
fi

echo ""
echo "🎉 Railway Build Simulation Complete!"
echo "✅ All phases completed successfully"
echo "✅ Ready for Railway deployment"