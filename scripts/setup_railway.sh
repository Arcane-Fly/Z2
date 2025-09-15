#!/bin/bash
set -e

# Z2 Railway Environment Configuration Script
# This script sets up the necessary environment variables for Railway deployment

echo "🚀 Configuring Z2 for Railway deployment..."

# Check if Railway CLI is available
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "   npm install -g @railway/cli"
    echo "   Or visit: https://docs.railway.app/guides/cli"
    exit 1
fi

# Verify Railway login
if ! railway whoami &> /dev/null; then
    echo "❌ Not logged into Railway. Please run: railway login"
    exit 1
fi

echo "✅ Railway CLI is available and you're logged in"

# Function to set environment variable if not already set
set_env_if_missing() {
    local var_name=$1
    local var_value=$2
    local service_name=${3:-""}
    
    # Build the railway command
    local cmd="railway variables list"
    if [ ! -z "$service_name" ]; then
        cmd="$cmd --service $service_name"
    fi
    
    # Check if variable exists
    if $cmd 2>/dev/null | grep -q "^$var_name="; then
        echo "⚠️  $var_name already set in ${service_name:-'shared variables'}"
    else
        echo "🔧 Setting $var_name in ${service_name:-'shared variables'}"
        local set_cmd="railway variables set $var_name=\"$var_value\""
        if [ ! -z "$service_name" ]; then
            set_cmd="$set_cmd --service $service_name"
        fi
        eval $set_cmd
    fi
}

echo ""
echo "📦 Setting shared environment variables..."

# Critical infrastructure variables
set_env_if_missing "POETRY_VERSION" "1.8.5"
set_env_if_missing "STORAGE_PATH" "/opt/app/storage"
set_env_if_missing "NODE_ENV" "production"
set_env_if_missing "PYTHON_VERSION" "3.12"

# Application configuration
set_env_if_missing "APP_NAME" "Z2 AI Workforce Platform"
set_env_if_missing "APP_VERSION" "0.1.0" 
set_env_if_missing "DEBUG" "false"
set_env_if_missing "LOG_LEVEL" "INFO"
set_env_if_missing "API_V1_PREFIX" "/api/v1"

echo ""
echo "🗄️  Setting database and cache configuration..."

# Check if we have database service
if railway service list 2>/dev/null | grep -q "postgres"; then
    echo "✅ PostgreSQL service detected"
    # Railway will automatically set DATABASE_URL for postgres service
else
    echo "⚠️  No PostgreSQL service found. You may need to add one."
fi

# Check if we have Redis service  
if railway service list 2>/dev/null | grep -q "redis"; then
    echo "✅ Redis service detected"
    # Railway will automatically set REDIS_URL for redis service
else
    echo "⚠️  No Redis service found. You may need to add one."
fi

echo ""
echo "🤖 Setting AI provider placeholders..."
echo "   Note: Replace these with your actual API keys"

# Set placeholder values that indicate configuration is needed
set_env_if_missing "OPENAI_API_KEY" "your-openai-key-here"
set_env_if_missing "ANTHROPIC_API_KEY" "your-anthropic-key-here"
set_env_if_missing "GROQ_API_KEY" "your-groq-key-here"
set_env_if_missing "GOOGLE_API_KEY" "your-google-key-here"

echo ""
echo "🔐 Setting security configuration..."

# Generate a secure JWT secret if not provided
if ! railway variables list 2>/dev/null | grep -q "^JWT_SECRET="; then
    JWT_SECRET=$(openssl rand -base64 32 2>/dev/null || echo "change-this-jwt-secret-in-production-$(date +%s)")
    set_env_if_missing "JWT_SECRET" "$JWT_SECRET"
fi

echo ""
echo "🌐 Setting CORS configuration..."

# Set CORS origins for frontend-backend communication
set_env_if_missing "CORS_ORIGINS" "https://\${{services.frontend.RAILWAY_PUBLIC_DOMAIN}}"

echo ""
echo "🔍 Setting monitoring configuration..."

# Monitoring and observability
set_env_if_missing "ENABLE_METRICS" "true"
set_env_if_missing "ENABLE_TRACING" "true"

echo ""
echo "🎯 Setting service-specific variables..."

# Backend-specific variables
echo "   Setting backend variables..."
set_env_if_missing "DATABASE_ECHO" "false" "backend"
set_env_if_missing "MAX_TOKENS" "4096" "backend"
set_env_if_missing "TEMPERATURE" "0.7" "backend"

# Frontend-specific variables  
echo "   Setting frontend variables..."
set_env_if_missing "VITE_API_BASE_URL" "https://\${{services.backend.RAILWAY_PUBLIC_DOMAIN}}" "frontend"
set_env_if_missing "VITE_WS_BASE_URL" "wss://\${{services.backend.RAILWAY_PUBLIC_DOMAIN}}" "frontend"
set_env_if_missing "VITE_APP_NAME" "Z2 AI Workforce Platform" "frontend"
set_env_if_missing "VITE_APP_VERSION" "0.1.0" "frontend"

echo ""
echo "✅ Configuration complete!"
echo ""
echo "🚨 IMPORTANT: Next steps:"
echo "   1. Replace placeholder API keys with your actual keys:"
echo "      railway variables set OPENAI_API_KEY=\"your-actual-key\""
echo "      railway variables set ANTHROPIC_API_KEY=\"your-actual-key\""
echo "      railway variables set GROQ_API_KEY=\"your-actual-key\""
echo ""
echo "   2. Verify database and Redis services are connected:"
echo "      railway service list"
echo ""
echo "   3. Deploy your services:"
echo "      railway up"
echo ""
echo "   4. Monitor deployment:"
echo "      railway logs --service backend"
echo "      railway logs --service frontend"
echo ""
echo "🔗 Useful commands:"
echo "   railway variables list                 # View all variables"
echo "   railway status                         # Check service status"
echo "   railway domain list                    # View service URLs"