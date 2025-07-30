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

### Environment Variables
The necessary environment variables are now defined in the `railpack.json` file. Railway will automatically provision these variables for each service.

## Deployment Steps

### Using Railpack Configuration
The `railpack.json` file will be automatically detected by Railway. When you create a new project from this repository, Railway will create the `backend`, `frontend`, `postgres`, and `redis` services, and configure them with the correct environment variables and settings.

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