# Z2 Deployment Architecture & Configuration

## Overview

This document outlines the standardized deployment architecture for the Z2 AI Workforce Platform, addressing critical issues identified in the smoke test analysis.

## Service Architecture

### Backend Service (Z2B)
- **Builder**: NIXPACKS with Python 3.12
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with asyncpg driver
- **Cache**: Redis
- **Storage**: Persistent volumes at `/opt/app/storage`
- **Health Check**: `/health` endpoint with comprehensive monitoring

### Frontend Service (Z2F) 
- **Builder**: NIXPACKS with Node.js 20
- **Framework**: React with Vite
- **Package Manager**: Yarn 4.9.2
- **Build**: Optimized static build with serve
- **Health Check**: `/` endpoint

## Configuration Files

### 1. Service-Specific Railpack Configurations

#### Backend (`backend/railpack.json`)
```json
{
  "version": "1",
  "metadata": {
    "name": "z2-backend"
  },
  "build": {
    "provider": "python",
    "nixpacksPlan": {
      "phases": {
        "setup": {
          "nixPkgs": ["python312", "poetry"],
          "commands": [
            "pip install --upgrade pip",
            "pip install poetry==1.8.5",
            "export PATH=$HOME/.local/bin:$PATH"
          ]
        },
        "install": {
          "commands": [
            "poetry config virtualenvs.create false",
            "poetry install --no-dev --no-interaction --no-ansi"
          ]
        }
      }
    }
  },
  "deploy": {
    "startCommand": "python scripts/init_db.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthCheckPath": "/health",
    "healthCheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

#### Frontend (`frontend/railpack.json`)
```json
{
  "version": "1", 
  "metadata": {
    "name": "z2-frontend"
  },
  "build": {
    "provider": "node",
    "steps": {
      "install": {
        "commands": [
          "corepack enable && corepack prepare yarn@4.9.2 --activate",
          "yarn install --frozen-lockfile"
        ]
      },
      "build": {
        "commands": ["yarn build"]
      }
    }
  },
  "deploy": {
    "startCommand": "yarn start",
    "healthCheckPath": "/",
    "healthCheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

**Note**: This project uses railpack-only configuration. No `railway.json`, `railway.toml`, `Dockerfile`, or other competing build configurations exist. See `docs/RAILWAY_SERVICE_OVERVIEW.md` for complete service architecture documentation.

## Key Fixes Implemented

### 1. Poetry v2.0+ Compatibility
- **Issue**: Poetry v2.0+ removed the `export` command causing build warnings
- **Fix**: Pinned Poetry to v1.8.5 and updated install commands
- **Impact**: Eliminates build warnings and ensures consistent dependency management

### 2. Storage Path Standardization
- **Issue**: Inconsistent storage paths across services
- **Fix**: Standardized all storage to `/opt/app/storage`
- **Impact**: Consistent file access and volume mounting

### 3. Enhanced Health Monitoring
- **Issue**: LLM provider health checks failing due to missing API keys
- **Fix**: Improved health checks to handle missing configurations gracefully
- **Endpoints**:
  - `/health` - Basic health check
  - `/health/live` - Kubernetes liveness probe
  - `/health/ready` - Kubernetes readiness probe
  - `/api/v1/health/detailed` - Comprehensive service status
  - `/api/v1/health/services` - Individual service checks
  - `/api/v1/health/providers` - LLM provider status

### 4. Service Architecture Standardization
- **Issue**: Redundant frontend services and architectural inconsistencies
- **Fix**: Consolidated to single frontend service using NIXPACKS
- **Impact**: Reduced complexity and improved deployment reliability

### 5. Build System Optimization
- **Issue**: Inconsistent build configurations
- **Fix**: Service-specific railpack.json files with proper isolation
- **Impact**: Better build reliability and easier maintenance

## Environment Variables

### Critical Variables
```bash
# Infrastructure
POETRY_VERSION=1.8.5
STORAGE_PATH=/opt/app/storage
NODE_ENV=production
PYTHON_VERSION=3.12

# Application
APP_NAME="Z2 AI Workforce Platform"
APP_VERSION=0.1.0
DEBUG=false
LOG_LEVEL=INFO
API_V1_PREFIX=/api/v1

# Security
JWT_SECRET=<generated-secret>

# CORS Configuration
CORS_ORIGINS=https://${{services.frontend.RAILWAY_PUBLIC_DOMAIN}}

# Frontend Variables
VITE_API_BASE_URL=https://${{services.backend.RAILWAY_PUBLIC_DOMAIN}}
VITE_WS_BASE_URL=wss://${{services.backend.RAILWAY_PUBLIC_DOMAIN}}
VITE_APP_NAME="Z2 AI Workforce Platform"
VITE_APP_VERSION=0.1.0

# AI Providers (replace with actual keys)
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
GROQ_API_KEY=your-groq-key-here
```

### Database & Cache
Railway automatically provides:
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection

## Deployment Process

### 1. Initial Setup
```bash
# Configure environment variables
./scripts/setup_railway.sh

# Validate configuration
python scripts/validate_config.py
```

### 2. Deploy Services
```bash
# Deploy backend
railway up --service backend

# Deploy frontend  
railway up --service frontend
```

### 3. Monitor Deployment
```bash
# Check service status
railway status

# View logs
railway logs --service backend --tail
railway logs --service frontend --tail

# Check health endpoints
curl https://your-backend-url/health
curl https://your-backend-url/api/v1/health/detailed
```

## Health Monitoring

### Service Health Levels
1. **Healthy**: All services operational
2. **Degraded**: Non-critical services (LLM providers) have issues
3. **Unhealthy**: Critical services (database, Redis) failing

### Monitoring Endpoints
- **Basic Health**: `GET /health`
- **Detailed Status**: `GET /api/v1/health/detailed`
- **Service Status**: `GET /api/v1/health/services`
- **Provider Status**: `GET /api/v1/health/providers`
- **Metrics**: `GET /metrics` (Prometheus format)

## Troubleshooting

### Common Issues

#### 1. Poetry Command Not Found
- **Cause**: Poetry v2.0+ compatibility issues
- **Solution**: Ensure POETRY_VERSION=1.8.5 is set

#### 2. Storage Path Errors
- **Cause**: Inconsistent storage paths
- **Solution**: Verify STORAGE_PATH=/opt/app/storage across all configs

#### 3. LLM Provider Failures
- **Cause**: Missing or invalid API keys
- **Solution**: Configure API keys or expect degraded status

#### 4. CORS Errors
- **Cause**: Incorrect frontend-backend communication
- **Solution**: Verify CORS_ORIGINS includes frontend domain

### Validation Commands
```bash
# Validate configurations
python scripts/validate_config.py

# Check environment variables
railway variables list

# Test health endpoints
curl -s https://your-backend-url/health | jq .

# Check build logs
railway logs --service backend --deployment latest
```

## Security Considerations

1. **API Keys**: Never commit real API keys to source control
2. **JWT Secret**: Use generated secrets, rotate regularly
3. **CORS**: Restrict to specific domains in production
4. **Health Checks**: Don't expose sensitive information

## Next Steps

1. Configure actual AI provider API keys
2. Set up monitoring dashboards
3. Implement automated testing in CI/CD
4. Configure backup and disaster recovery
5. Set up performance monitoring

For more information, see the deployment scripts in `/scripts/` directory.