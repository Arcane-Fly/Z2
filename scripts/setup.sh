#!/usr/bin/env bash

# Z2 Development Setup Script
# This script sets up the development environment for the Z2 platform

set -e

echo "🚀 Setting up Z2 Development Environment..."

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python 3.11+
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ is required but not installed."
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2)
required_version="3.11.0"
if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
    echo "❌ Python 3.11+ is required. Found: $python_version"
    exit 1
fi

# Check Node.js 18+
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 18+ is required but not installed."
    exit 1
fi

node_version=$(node --version | cut -d'v' -f2)
required_node_version="18.0.0"
if [[ "$(printf '%s\n' "$required_node_version" "$node_version" | sort -V | head -n1)" != "$required_node_version" ]]; then
    echo "❌ Node.js 18+ is required. Found: $node_version"
    exit 1
fi

# Check if PostgreSQL is available
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found. You'll need to install it or use Docker."
fi

# Check if Redis is available
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis not found. You'll need to install it or use Docker."
fi

echo "✅ Prerequisites check complete."

# Backend setup
echo "🐍 Setting up Python backend..."
cd backend

# Install Poetry if not installed
if ! command -v poetry &> /dev/null; then
    echo "📦 Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
poetry install

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating backend .env file..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your API keys and configuration."
fi

cd ..

# Frontend setup
echo "⚛️  Setting up React frontend..."
cd frontend

# Install dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating frontend .env file..."
    cp .env.example .env
fi

cd ..

# Create storage directory
echo "📁 Creating storage directory..."
mkdir -p storage

# Create initial documentation
echo "📚 Creating initial documentation..."
mkdir -p docs/{setup,api,guides}

echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Edit backend/.env with your API keys"
echo "2. Start PostgreSQL and Redis (or use Docker: docker-compose up postgres redis)"
echo "3. Run backend: cd backend && poetry run uvicorn app.main:app --reload"
echo "4. Run frontend: cd frontend && npm run dev"
echo "5. Visit http://localhost:3000 to see the application"
echo ""
echo "📖 For detailed setup instructions, see docs/setup/README.md"