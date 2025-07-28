# Railway Deployment Configuration for Z2 Monorepo

This repository now includes Railway deployment configurations to resolve the monorepo build strategy detection issue.

## Problem Solved

**Issue**: Railway's Nixpacks auto-detection was failing because the monorepo structure contained multiple services (`backend/`, `frontend/`) and Dockerfiles (`Dockerfile.backend`, `Dockerfile.frontend`) without explicit service configuration.

**Solution**: Created explicit Railway configurations using Docker builder to avoid Nixpacks conflicts.

## Configuration Files Added

### 1. `railpack.json` (Primary Solution)
Main configuration file defining both services with explicit Docker builders:
- Backend service: Uses `Dockerfile.backend` with root directory `./backend`
- Frontend service: Uses `Dockerfile.frontend` with root directory `./frontend`
- Both configured with health checks and Railway-specific settings

### 2. Service-Specific `railway.json` Files (Backup Solution)
- `backend/railway.json`: Backend service configuration
- `frontend/railway.json`: Frontend service configuration

### 3. `nginx.conf`
Added missing nginx configuration for frontend static file serving with:
- SPA routing support
- Health check endpoint at `/health`
- Static asset caching
- Security headers

## Docker Improvements

### Backend (`Dockerfile.backend`)
- Added `ARG RAILWAY_ENVIRONMENT` for Railway-specific builds
- Fixed Poetry dependency installation with `--no-root` flag
- Added health check using `/health` endpoint
- Improved CMD format for better signal handling

### Frontend (`Dockerfile.frontend`)
- Added `ARG RAILWAY_ENVIRONMENT` for Railway-specific builds
- Fixed build dependencies (removed `--only=production` to include TypeScript)
- Added health check support with curl installation
- Added dynamic port configuration

## Environment Variables

### Backend Environment Variables (`backend_env_vars.txt`)
```
PORT=$PORT
NODE_ENV=production
PYTHON_VERSION=3.11
POETRY_VERSION=1.6.1
FRONTEND_URL=${{z2-frontend.RAILWAY_PUBLIC_DOMAIN}}
DATABASE_URL=${{database.DATABASE_URL}}
REDIS_URL=${{redis.REDIS_URL}}
DEBUG=false
LOG_LEVEL=INFO
```

### Frontend Environment Variables (`frontend_env_vars.txt`)
```
VITE_API_URL=${{z2-backend.RAILWAY_PUBLIC_DOMAIN}}
VITE_API_BASE_URL=https://${{z2-backend.RAILWAY_PUBLIC_DOMAIN}}/api
VITE_WS_BASE_URL=wss://${{z2-backend.RAILWAY_PUBLIC_DOMAIN}}
NODE_ENV=production
VITE_ENABLE_DEBUG=false
PORT=$PORT
```

## Deployment Steps

### Option 1: Using Railpack Configuration (Recommended)
1. The `railpack.json` file should be automatically detected by Railway
2. Create two separate services in Railway Dashboard:
   - Backend service pointing to this repository
   - Frontend service pointing to this repository
3. Apply the environment variables from the respective `.txt` files

### Option 2: Using Service-Specific Configuration
1. Create backend service with root directory: `backend/`
2. Create frontend service with root directory: `frontend/`
3. Railway will use the respective `railway.json` files

### Option 3: Railway CLI
```bash
railway login
railway link  # Link to existing project
railway service create backend --source ./backend
railway service create frontend --source ./frontend
```

## Validation

### Local Testing
Both Docker builds have been tested and verified:
```bash
# Test backend build
docker build -f Dockerfile.backend -t z2-backend .

# Test frontend build  
docker build -f Dockerfile.frontend -t z2-frontend .
```

### Configuration Validation
All JSON configurations have been validated:
- ✅ `railpack.json` - Valid JSON
- ✅ `backend/railway.json` - Valid JSON
- ✅ `frontend/railway.json` - Valid JSON

## Expected Results

After deployment, you should see:
1. Railway build logs showing "Using Docker" instead of "Using Nixpacks"
2. Successful service deployments with health checks
3. Inter-service communication via Railway reference variables
4. No more build strategy detection failures

## Backup

The original `railway.toml` has been preserved as `railway.toml.backup-original` for reference.