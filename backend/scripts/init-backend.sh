#!/bin/bash
# Builder-Agnostic Backend Initialization Script
# This script ensures Poetry is available and runs the backend initialization

set -e

# Source the executable finder
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/../scripts/find-executable.sh" ]; then
    source "$SCRIPT_DIR/../scripts/find-executable.sh"
elif [ -f "./scripts/find-executable.sh" ]; then
    source "./scripts/find-executable.sh"
fi

echo "🚀 Initializing Z2 Backend..."

# Find Python executable
PYTHON=$(find_executable python3 || find_executable python)
if [ -z "$PYTHON" ]; then
    echo "❌ Python not found. Please ensure Python 3.11+ is installed."
    exit 1
fi

echo "✅ Using Python: $PYTHON"

# Find or install Poetry
POETRY=$(find_executable poetry)
if [ -z "$POETRY" ]; then
    echo "📦 Poetry not found. Installing..."
    
    # Try pip install first (faster and more reliable in containers)
    if $PYTHON -m pip install poetry==1.8.5 >/dev/null 2>&1; then
        echo "✅ Poetry installed via pip"
        POETRY=$(find_executable poetry)
    else
        echo "📦 Trying official Poetry installer..."
        curl -sSL https://install.python-poetry.org | $PYTHON -
        
        # Check common Poetry installation locations
        for poetry_path in "$HOME/.local/bin/poetry" "/usr/local/bin/poetry" "/usr/bin/poetry"; do
            if [ -x "$poetry_path" ]; then
                POETRY="$poetry_path"
                break
            fi
        done
    fi
    
    if [ -z "$POETRY" ]; then
        echo "❌ Poetry installation failed. Cannot proceed."
        exit 1
    fi
fi

echo "✅ Using Poetry: $POETRY"

# Verify Poetry is working
if ! $POETRY --version >/dev/null 2>&1; then
    echo "❌ Poetry is not working correctly"
    exit 1
fi

# Configure Poetry for containerized environments
echo "🔧 Configuring Poetry..."
$POETRY config virtualenvs.create false
$POETRY config virtualenvs.in-project false

# Install dependencies
echo "📦 Installing dependencies..."
$POETRY install --no-root --only=main

# Initialize database if init script exists
if [ -f "scripts/init_db.py" ]; then
    echo "🗄️  Initializing database..."
    $PYTHON scripts/init_db.py
elif [ -f "init_db.py" ]; then
    echo "🗄️  Initializing database..."
    $PYTHON init_db.py
else
    echo "⚠️  Database initialization script not found, skipping..."
fi

echo "✅ Backend initialization complete!"