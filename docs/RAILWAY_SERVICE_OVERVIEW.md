# Z2 Railway Service Architecture Overview

**Last Updated**: October 12, 2025  
**Status**: Active Deployment Configuration

## Executive Summary

The Z2 Platform requires **FOUR services** on Railway for full functionality:

1. **Z2B (Backend)** - Python FastAPI application
2. **Z2F (Frontend)** - Node.js/Vite React application
3. **PostgreSQL** - Primary database
4. **Redis** - Cache and session store

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Z2 Platform on Railway                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │   Z2F        │      │   Z2B        │                     │
│  │  Frontend    │─────▶│  Backend     │                     │
│  │              │      │              │                     │
│  │ Node.js 22   │      │ Python 3.11  │                     │
│  │ Yarn 4.9.2   │      │ Poetry       │                     │
│  │ Vite + React │      │ FastAPI      │                     │
│  └──────────────┘      └───────┬──────┘                     │
│                                │                             │
│                                │                             │
│                        ┌───────▼────────┐                   │
│                        │  PostgreSQL    │                   │
│                        │  Database      │                   │
│                        │                │                   │
│                        │  postgres:15   │                   │
│                        └────────────────┘                   │
│                                                               │
│                        ┌────────────────┐                   │
│                        │  Redis         │                   │
│                        │  Cache         │                   │
│                        │                │                   │
│                        │  redis:7-alpine│                   │
│                        └────────────────┘                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Service Details

### 1. Z2B - Backend Service

**Purpose**: Core API server for Z2 platform

**Configuration**:
- **Service ID**: `169631f2-0f90-466d-89b8-a67f240a18b5`
- **Root Directory**: `backend`
- **Runtime**: Python 3.11 with Poetry
- **Framework**: FastAPI + uvicorn
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check**: `/health`
- **Build System**: Railpack-only (no Dockerfile)

**Dependencies**:
- PostgreSQL (via `DATABASE_URL` environment variable)
- Redis (via `REDIS_URL` environment variable)
- Multiple LLM provider API keys (OpenAI, Anthropic, Groq, Google, etc.)

**Key Features**:
- RESTful API endpoints
- User authentication and authorization
- AI agent workflow orchestration
- Vector database integration (ChromaDB)
- Real-time processing with Celery
- Database migrations with Alembic

**Required Environment Variables**:
```bash
# Database (auto-injected by Railway)
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# Security
SECRET_KEY=<your-secret-key>
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# LLM Providers
OPENAI_API_KEY=<your-key>
ANTHROPIC_API_KEY=<your-key>
GROQ_API_KEY=<your-key>
GOOGLE_API_KEY=<your-key>
PERPLEXITY_API_KEY=<your-key>

# Agent Configuration
MAX_AGENTS_PER_WORKFLOW=10
AGENT_TIMEOUT_SECONDS=300
DEFAULT_MODEL=groq/llama-3.3-70b-versatile
```

### 2. Z2F - Frontend Service

**Purpose**: User interface for Z2 platform

**Configuration**:
- **Service ID**: `94ef6eda-e787-47df-bf33-0a8a4bc25533`
- **Root Directory**: `frontend`
- **Runtime**: Node.js 22 with Yarn 4.9.2
- **Framework**: Vite + React + TypeScript
- **Build Command**: `yarn build` (creates `dist/` directory)
- **Start Command**: `yarn start` → `node server.js`
- **Health Check**: `/api/health`
- **Build System**: Railpack-only (no Dockerfile)

**Dependencies**:
- Z2B Backend API (via environment variable)

**Key Features**:
- Modern React SPA with TypeScript
- Vite for fast development and optimized builds
- Express server for static file serving
- Health check endpoint for Railway monitoring

**Required Environment Variables**:
```bash
# Backend API
VITE_API_URL=https://z2b-production.up.railway.app

# Optional: Feature flags
VITE_ENABLE_ANALYTICS=false
```

### 3. PostgreSQL Database Service

**Purpose**: Primary relational database for persistent data

**Configuration**:
- **Image**: `postgres:15`
- **Provisioning**: Automatic via Railway
- **Connection**: Injected as `DATABASE_URL` to backend

**Features**:
- Automatic daily backups
- Point-in-time recovery
- Connection pooling
- SSL/TLS encryption

**Database Schema**:
- Users and authentication
- AI agents and workflows
- Memory graphs and embeddings
- Roles and permissions
- Audit logs

**Access**:
```bash
# Connect via Railway CLI
railway connect postgres

# Or use DATABASE_URL directly
psql $DATABASE_URL
```

### 4. Redis Service

**Purpose**: Caching, session storage, and message broker

**Configuration**:
- **Image**: `redis:7-alpine`
- **Provisioning**: Automatic via Railway
- **Connection**: Injected as `REDIS_URL` to backend

**Use Cases**:
- Session management
- API response caching
- Rate limiting
- Celery task queue (message broker)
- Real-time features

**Access**:
```bash
# Connect via Railway CLI
railway connect redis

# Or use redis-cli
redis-cli -u $REDIS_URL
```

## Service Dependencies

```
Z2F (Frontend)
  └─▶ Z2B (Backend)
       ├─▶ PostgreSQL (Database)
       └─▶ Redis (Cache)
```

**Critical**: The backend (Z2B) MUST have both PostgreSQL and Redis available before it can start successfully. The frontend (Z2F) requires the backend to be running and accessible.

## Deployment Order

When deploying from scratch, follow this order:

1. **PostgreSQL** - Provision database first
2. **Redis** - Provision cache second
3. **Z2B Backend** - Deploy with DATABASE_URL and REDIS_URL configured
4. **Z2F Frontend** - Deploy last, pointing to backend URL

## Current Build System

**Railpack-Only Configuration** (as per Railway best practices):

```
/railpack.json              # Root monorepo configuration
/backend/railpack.json      # Backend Python/Poetry config
/frontend/railpack.json     # Frontend Node.js/Yarn config
```

**NO competing build configurations**:
- ❌ No `Dockerfile` files
- ❌ No `railway.toml` files
- ❌ No `railway.json` files
- ❌ No `nixpacks.toml` files
- ❌ No `Procfile` files

This ensures Railway uses railpack.json as the single source of build truth, following Railway Deployment Master Cheat Sheet standards.

## Validation

To validate the Railway configuration, use the compliant validation script:

```bash
bash scripts/railway-railpack-validation.sh
```

This checks:
- ✅ No competing build configurations exist
- ✅ Railpack.json files are valid JSON
- ✅ Proper PORT environment variable usage
- ✅ Host binding to 0.0.0.0 (not localhost)
- ✅ Health endpoints configured
- ✅ Critical build outputs (dist/) not ignored

## Monitoring and Health Checks

### Health Check Endpoints

All services expose health check endpoints for Railway monitoring:

- **Z2B Backend**: `https://<backend-url>/health`
- **Z2F Frontend**: `https://<frontend-url>/api/health`
- **PostgreSQL**: Automatic connection checks
- **Redis**: Automatic connection checks

### Monitoring Commands

```bash
# Check all service statuses
railway status

# View backend logs
railway logs -s Z2B --tail

# View frontend logs
railway logs -s Z2F --tail

# Test backend health
curl https://z2b-production.up.railway.app/health

# Test frontend health
curl https://z2-production.up.railway.app/api/health
```

## Cost Considerations

### Free Tier Limitations
- **$5/month credit** for hobby projects
- Services are billed based on:
  - CPU usage (per second)
  - Memory usage (per GB-hour)
  - Network egress (per GB)

### Recommended for Production
- **Team Plan**: $20/month per user
- Dedicated resources
- Priority support
- Higher resource limits

### Service Resource Estimates
- **PostgreSQL**: ~$3-5/month (minimal usage)
- **Redis**: ~$1-2/month (minimal usage)
- **Z2B Backend**: ~$5-15/month (depends on traffic)
- **Z2F Frontend**: ~$2-5/month (static serving)

**Total Estimate**: $11-27/month for low-medium traffic

## Troubleshooting

### Common Issues

#### Backend fails to start
```bash
# Check DATABASE_URL is set
railway run -s Z2B env | grep DATABASE_URL

# Check REDIS_URL is set
railway run -s Z2B env | grep REDIS_URL

# Verify database is accessible
railway run -s Z2B python -c "import asyncpg; print('OK')"
```

#### Frontend can't reach backend
```bash
# Check VITE_API_URL is set correctly
railway run -s Z2F env | grep VITE_API_URL

# Test backend connectivity
railway run -s Z2F curl $VITE_API_URL/health
```

#### Build failures
```bash
# Check for competing build configs
bash scripts/railway-railpack-validation.sh

# Review build logs
railway logs -s Z2B --deployment <deployment-id>

# Trigger manual rebuild
railway up -s Z2B --force
```

## Additional Services (Future Considerations)

The following services may be added in the future:

### Optional Services
- **ChromaDB** - Dedicated vector database (currently using embedded mode)
- **Celery Worker** - Separate worker service for background tasks
- **Nginx** - Reverse proxy and load balancer
- **Monitoring** - Prometheus/Grafana stack
- **Message Queue** - RabbitMQ (alternative to Redis for Celery)

### Not Currently Needed
These services are NOT required for the current Z2 deployment:
- Separate Celery workers (using embedded Celery in backend)
- Separate vector database (using embedded ChromaDB)
- CDN (Railway provides edge caching)
- Load balancer (Railway handles this automatically)

## Documentation References

- **Railway Deployment Guide**: [`docs/setup/railway-deployment.md`](setup/railway-deployment.md)
- **Railway Final Status**: [`docs/RAILWAY_FINAL_STATUS.md`](RAILWAY_FINAL_STATUS.md)
- **Railway Railpack Guide**: [`docs/RAILWAY_RAILPACK_GUIDE.md`](RAILWAY_RAILPACK_GUIDE.md)
- **Service Inspection Report**: [`docs/railway-service-inspection-2025-10-11.md`](railway-service-inspection-2025-10-11.md)
- **Architecture Documentation**: [`docs/DEPLOYMENT_ARCHITECTURE.md`](DEPLOYMENT_ARCHITECTURE.md)

## Quick Start

### Deploy all services to Railway:

```bash
# 1. Login to Railway
railway login

# 2. Create a new project
railway project:create z2-platform

# 3. Add PostgreSQL
railway add --service postgres

# 4. Add Redis
railway add --service redis

# 5. Deploy backend
cd backend
railway up

# 6. Deploy frontend
cd ../frontend
railway up
```

### Set required environment variables in Railway Dashboard:
1. Navigate to your project
2. Select Z2B service → Variables
3. Add LLM API keys and other required variables
4. Select Z2F service → Variables
5. Add VITE_API_URL pointing to Z2B service URL

---

**Summary**: Z2 requires **4 services** on Railway: Z2B (Backend), Z2F (Frontend), PostgreSQL (Database), and Redis (Cache). The backend depends on both database services, and the frontend depends on the backend. All services use railpack-only configuration for consistent, predictable deployments.
