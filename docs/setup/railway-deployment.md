# Z2 Platform - Railway Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Z2 AI Workforce Platform on Railway.app, including environment configuration, database setup, and ongoing maintenance procedures.

## Why Railway.app?

Railway is the recommended hosting platform for Z2 because:

- **Git-based Deployments**: Automatic deployments from GitHub
- **Managed Databases**: PostgreSQL and Redis with automatic backups
- **Environment Management**: Secure environment variable handling
- **Scaling**: Automatic scaling based on demand
- **Zero-Config Deployments**: Minimal configuration required
- **Developer Experience**: Excellent CLI and dashboard tools

## Prerequisites

- GitHub repository with Z2 code
- Railway.app account ([sign up here](https://railway.app))
- Railway CLI installed (`npm install -g @railway/cli`)
- Required LLM provider API keys

## Initial Setup

### 1. Create Railway Project

#### Option A: Using Railway Dashboard
1. Visit [railway.app/new](https://railway.app/new)
2. Select "Deploy from GitHub repo"
3. Choose your Z2 repository
4. Railway will automatically detect the configuration

#### Option B: Using Railway CLI
```bash
# Login to Railway
railway login

# Create new project in your Z2 directory
cd /path/to/Z2
railway project:create z2-platform

# Link to your repository
railway project:link
```

### 2. Service Configuration

Railway automatically detects the services from your `railway.toml` file:

```toml
# railway.toml (already configured)
services:
  backend:
    source: backend
    build:
      buildCommand: poetry install --no-dev
    deploy:
      startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
      healthcheckPath: /health
      restartPolicyType: on_failure
    variables:
      PORT: ${{PORT}}
    domains:
      - z2-api.railway.app
    
  frontend:
    source: frontend
    build:
      buildCommand: npm ci && npm run build
      publishPath: dist
    deploy:
      staticSite: true
    domains:
      - z2.railway.app

  postgres:
    image: postgres:15
    variables:
      POSTGRES_DB: z2
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${{Postgres.POSTGRES_PASSWORD}}

  redis:
    image: redis:7-alpine
```

## Environment Configuration

**IMPORTANT**: The following environment variables are now automatically configured in the railpack.json files for Railway deployment. Users deploying manually or on other platforms should set these variables via their platform's dashboard.

### Backend Environment Variables

Set these in Railway Dashboard → Project → Backend Service → Variables:

#### Core Application Variables (Auto-configured in railpack.json)
These variables are now automatically set by Railway when using railpack.json configuration:

```bash
# Application Identity
APP_NAME="Z2 AI Workforce Platform"
APP_VERSION="0.1.0"

# Environment Configuration  
DEBUG=false
LOG_LEVEL=INFO

# API Configuration
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["https://${{services.frontend.RAILWAY_PUBLIC_DOMAIN}}"]

# Infrastructure
PORT=$PORT  # Automatically provided by Railway
NODE_ENV=production
PYTHON_VERSION=3.12
POETRY_VERSION=1.6.1
STORAGE_PATH=/app/storage
```

#### Required Variables
```bash
# Database (Railway provides these automatically)
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# Security (generate secure values)
SECRET_KEY=your-production-secret-key-32-chars-min
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# LLM Provider API Keys (REQUIRED)
OPENAI_API_KEY=your-openai-production-key
ANTHROPIC_API_KEY=your-anthropic-production-key
GROQ_API_KEY=your-groq-production-key
GOOGLE_API_KEY=your-google-production-key
PERPLEXITY_API_KEY=your-perplexity-production-key

# Agent Configuration
MAX_AGENTS_PER_WORKFLOW=10
AGENT_TIMEOUT_SECONDS=300
MAX_WORKFLOW_DURATION_HOURS=24
DEFAULT_MODEL=openai/gpt-4.1-mini
MAX_TOKENS=4096
TEMPERATURE=0.7

# Monitoring
ENABLE_METRICS=true
ENABLE_TRACING=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# MCP Protocol
MCP_SERVER_NAME="Z2 AI Workforce Platform"
MCP_SERVER_VERSION="1.0.0"
MCP_PROTOCOL_VERSION="2025-03-26"
ENABLE_MCP_SESSIONS=true
SESSION_TIMEOUT_MINUTES=30
MAX_CONCURRENT_SESSIONS=100
```

#### Generating Secure Secret Key
```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
# OR
openssl rand -base64 32
```

### Model Configuration Updates

#### GPT-4.1 Model Migration
The platform has been updated to use GPT-4.1 models as the default instead of GPT-4o models for improved performance and capabilities:

**Model Mapping:**
- `gpt-4o` → `gpt-4.1` (flagship model)
- `gpt-4o-mini` → `gpt-4.1-mini` (default cost-optimized model)
- Multimodal/Vision tasks now use `gpt-4.1` by default

**Benefits of GPT-4.1:**
- Larger context window (1M tokens vs 128K)
- Enhanced reasoning capabilities
- Better code generation performance
- Updated knowledge cutoff (April 2025)

**Environment Variable Updates:**
```bash
# OLD
DEFAULT_MODEL=openai/gpt-4o-mini

# NEW
DEFAULT_MODEL=openai/gpt-4.1-mini
```

**Backward Compatibility:**
- GPT-4o models remain available for legacy configurations
- Existing API calls using gpt-4o models will continue to work
- Model registry supports both gpt-4o and gpt-4.1 families

### Frontend Environment Variables

**IMPORTANT**: The core frontend variables are now automatically configured in the railpack.json file. Additional variables should be set in Railway Dashboard → Project → Frontend Service → Variables:

#### Core Variables (Auto-configured in railpack.json)
```bash
# API Configuration
VITE_API_BASE_URL=https://${{services.backend.RAILWAY_PUBLIC_DOMAIN}}
VITE_WS_BASE_URL=wss://${{services.backend.RAILWAY_PUBLIC_DOMAIN}}

# Application Identity
VITE_APP_NAME="Z2 AI Workforce Platform"
VITE_APP_VERSION="0.1.0"

# Infrastructure
PORT=$PORT  # Automatically provided by Railway
NODE_ENV=production
```

#### Optional Additional Variables
Set these in Railway Dashboard → Project → Frontend Service → Variables:

```bash
# API Configuration
VITE_API_TIMEOUT=30000

# Authentication
VITE_AUTH_TOKEN_KEY=z2_auth_token
VITE_REFRESH_TOKEN_KEY=z2_refresh_token
VITE_AUTH_ENABLED=true

# Feature Flags
VITE_ENABLE_DEBUG=false
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_AGENT_BUILDER=true
VITE_ENABLE_WORKFLOW_DESIGNER=true
VITE_ENABLE_MCP_CLIENT=true
VITE_ENABLE_A2A_PROTOCOL=true

# UI Configuration
VITE_DEFAULT_THEME=light
VITE_ENABLE_DARK_MODE=true
VITE_SIDEBAR_COLLAPSED=false

# WebSocket
VITE_WS_BASE_URL=wss://${{backend.RAILWAY_PUBLIC_DOMAIN}}

# Monitoring (optional)
VITE_SENTRY_DSN=your-sentry-dsn-if-using
```

### Important Notes About Environment Variables

#### Why These Variables Are Critical
The environment variables configured in railpack.json are essential for production deployment:

1. **APP_NAME & APP_VERSION**: Used for service identification, logging, and monitoring
2. **DEBUG & LOG_LEVEL**: Control application verbosity and debugging features
3. **API_V1_PREFIX**: Defines API routing structure for proper endpoint resolution
4. **CORS_ORIGINS**: Critical for security - prevents unauthorized cross-origin requests
5. **VITE_API_BASE_URL & VITE_WS_BASE_URL**: Frontend must know backend endpoints for communication

#### Manual Platform Deployment
For deployments outside Railway, ensure these variables are set via your platform's environment variable interface:

**Backend Required:**
- All variables listed in "Core Application Variables" section
- LLM Provider API keys
- Database and Redis connection strings

**Frontend Required:**
- All variables listed in "Core Variables" section
- Proper backend endpoint URLs

#### Security Considerations
- Never commit API keys or secrets to version control
- Use your platform's secret management for sensitive variables
- Regularly rotate API keys and secret keys
- Validate CORS_ORIGINS match your actual domain names

## Database Setup

### PostgreSQL Configuration

Railway automatically provisions a PostgreSQL database. No additional configuration is needed, but you can customize:

#### Database Settings (Optional)
```bash
# In Railway Dashboard → Postgres Service → Variables
POSTGRES_DB=z2
POSTGRES_USER=postgres
POSTGRES_PASSWORD=${{POSTGRES_PASSWORD}}  # Auto-generated
```

#### Running Migrations
```bash
# Option A: Using Railway CLI
railway run --service=backend alembic upgrade head

# Option B: Connect to database directly
railway connect postgres
# Then run migrations from your local machine with DATABASE_URL
```

### Redis Configuration

Railway automatically provisions Redis. Default configuration is sufficient for most use cases.

#### Redis Memory Optimization (Optional)
```bash
# In Railway Dashboard → Redis Service → Variables
MAXMEMORY=256mb
MAXMEMORY_POLICY=allkeys-lru
```

## Domain Configuration

### Custom Domain Setup

#### 1. Add Custom Domain in Railway
```bash
# Using Railway CLI
railway domain:add your-domain.com --service=frontend
railway domain:add api.your-domain.com --service=backend

# Using Dashboard
# Go to Project → Service → Domains → Add Domain
```

#### 2. DNS Configuration
```bash
# Add CNAME records in your DNS provider:
# your-domain.com → CNAME → railway.app
# api.your-domain.com → CNAME → railway.app

# Or A records to Railway's IP addresses
# Check Railway dashboard for current IPs
```

#### 3. Update Environment Variables
```bash
# Frontend
VITE_API_BASE_URL=https://api.your-domain.com

# Backend
CORS_ORIGINS=["https://your-domain.com"]
```

### SSL Certificate

Railway automatically provides SSL certificates for all domains via Let's Encrypt. No additional configuration required.

## Deployment Process

### Automatic Deployment

Railway automatically deploys when you push to your main branch:

```bash
# Make changes to your code
git add .
git commit -m "Update Z2 platform"
git push origin main

# Railway will automatically:
# 1. Detect changes
# 2. Build services
# 3. Run tests (if configured)
# 4. Deploy to production
# 5. Update DNS
```

### Manual Deployment

```bash
# Using Railway CLI
railway up --service=backend
railway up --service=frontend

# Deploy specific service
railway up --service=backend --detach
```

### Build Configuration

#### Backend Build Process
```dockerfile
# Dockerfile.backend (already configured)
FROM python:3.11-slim
WORKDIR /app
COPY backend/pyproject.toml backend/poetry.lock ./
RUN pip install poetry && poetry install --no-dev
COPY backend/ ./
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
```

#### Frontend Build Process
```dockerfile
# Dockerfile.frontend (already configured)
FROM node:18-alpine as builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

## Monitoring and Logging

### Railway Built-in Monitoring

Railway provides comprehensive monitoring out of the box:

#### Metrics Available
- CPU usage
- Memory consumption
- Network I/O
- Response times
- Error rates
- Request volume

#### Accessing Metrics
```bash
# Using Railway CLI
railway logs --service=backend --tail

# In Railway Dashboard
# Go to Project → Service → Metrics
```

### Custom Monitoring Setup

#### Application Performance Monitoring (APM)
```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

# Initialize Sentry for error tracking
if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
    )
```

#### Health Check Endpoint
```python
# backend/app/api/health.py
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": os.getenv("APP_VERSION", "unknown"),
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": await check_database_health(),
            "redis": await check_redis_health(),
            "llm_providers": await check_llm_providers()
        }
    }
```

### Log Management

#### Structured Logging
```python
# backend/app/utils/logging.py
import structlog

logger = structlog.get_logger()

# Usage in application
logger.info("Agent workflow started", 
           workflow_id=workflow.id, 
           user_id=user.id,
           agent_count=len(workflow.agents))
```

#### Log Aggregation
```bash
# Forward logs to external service (optional)
# Set environment variables:
LOG_DRAIN_URL=https://logs.papertrailapp.com/systems/your-system/events
LOG_LEVEL=INFO
```

## Security Configuration

### Environment Security

#### Secret Management
```bash
# Use Railway's secret management
railway variables:set SECRET_KEY --service=backend
railway variables:set OPENAI_API_KEY --service=backend

# Never commit secrets to git
echo "*.env" >> .gitignore
echo ".env.local" >> .gitignore
```

#### Database Security
```bash
# Railway automatically provides:
# - Encrypted connections (SSL/TLS)
# - Network isolation
# - Automatic backups
# - Security patches

# Optional: Restrict database access
DATABASE_SSL_REQUIRE=true
DATABASE_SSL_MODE=require
```

### Application Security

#### CORS Configuration
```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Rate Limiting
```python
# backend/app/middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/agents")
@limiter.limit("10/minute")
def get_agents(request: Request):
    return {"agents": []}
```

## Scaling Configuration

### Horizontal Scaling

Railway automatically scales your application based on demand:

```bash
# Configure scaling in Railway Dashboard
# Project → Service → Settings → Scaling

# Auto-scaling triggers:
# - CPU usage > 80%
# - Memory usage > 80%
# - Response time > 2 seconds
# - Queue depth > 10 requests
```

### Vertical Scaling

```bash
# Increase resources per instance
# Railway Dashboard → Service → Settings → Resources

# Recommended minimums:
# Backend: 1 vCPU, 1GB RAM
# Frontend: 0.5 vCPU, 512MB RAM
# Database: 1 vCPU, 2GB RAM
```

### Database Scaling

```bash
# PostgreSQL scaling options:
# - Read replicas for read-heavy workloads
# - Connection pooling (PgBouncer)
# - Vertical scaling (CPU/Memory)

# Redis scaling options:
# - Increase memory allocation
# - Enable Redis clustering (for high availability)
```

## Backup and Recovery

### Database Backups

Railway automatically creates daily backups of your PostgreSQL database:

```bash
# View available backups
railway backups --service=postgres

# Restore from backup
railway restore --service=postgres --backup-id=backup-123

# Create manual backup
railway backup:create --service=postgres
```

### File Storage Backups

```bash
# If using Railway volumes for file storage
railway volumes --service=backend

# Backup volume data
railway run --service=backend "tar -czf backup.tar.gz /app/storage"
```

### Application State Recovery

```python
# Implement graceful shutdown for agent workflows
# backend/app/main.py
import signal
import asyncio

async def shutdown_handler():
    """Gracefully shutdown running workflows"""
    logger.info("Shutting down gracefully...")
    await save_workflow_states()
    await cleanup_agents()

# Register signal handlers
signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)
```

## Troubleshooting

### Common Deployment Issues

#### Build Failures
```bash
# Check build logs
railway logs --service=backend --build

# Common issues:
# 1. Missing dependencies in pyproject.toml
# 2. Poetry lock file conflicts
# 3. Python version mismatch

# Solutions:
poetry lock --no-update
poetry install
git add poetry.lock && git commit -m "Update poetry lock"
```

#### Runtime Errors
```bash
# Check runtime logs
railway logs --service=backend --tail

# Common issues:
# 1. Missing environment variables
# 2. Database connection failures
# 3. LLM API key errors

# Debug environment variables
railway run --service=backend env
```

#### Database Connection Issues
```bash
# Test database connection
railway connect postgres

# Check connection string format
echo $DATABASE_URL
# Should be: postgresql://user:pass@host:port/db

# Verify database is running
railway status --service=postgres
```

### Performance Issues

#### High Memory Usage
```bash
# Monitor memory usage
railway metrics --service=backend

# Common causes:
# 1. Memory leaks in agent workflows
# 2. Large model contexts
# 3. Inefficient database queries

# Solutions:
# - Implement memory monitoring
# - Use streaming for large responses
# - Optimize database queries
```

#### Slow Response Times
```bash
# Check response time metrics
railway metrics --service=backend --metric=response_time

# Common causes:
# 1. Slow LLM API calls
# 2. Database query performance
# 3. Insufficient resources

# Solutions:
# - Implement request caching
# - Use faster LLM models
# - Scale up resources
```

## Maintenance Procedures

### Regular Updates

#### Dependency Updates
```bash
# Update Python dependencies
cd backend
poetry update
poetry lock
git add poetry.lock pyproject.toml
git commit -m "Update Python dependencies"

# Update Node.js dependencies
cd frontend
npm update
git add package-lock.json
git commit -m "Update Node.js dependencies"

# Deploy updates
git push origin main
```

#### Security Updates
```bash
# Check for security vulnerabilities
cd backend
poetry audit

cd frontend
npm audit

# Fix vulnerabilities
npm audit fix
poetry update --only security
```

### Database Maintenance

#### Vacuum and Analyze
```bash
# Connect to database
railway connect postgres

# Run maintenance queries
VACUUM ANALYZE;
REINDEX DATABASE z2;

# Check database size
SELECT pg_size_pretty(pg_database_size('z2'));
```

#### Monitor Database Performance
```sql
-- Find slow queries
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check table sizes
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Cost Optimization

#### Monitor Usage
```bash
# Check Railway usage dashboard
# Monitor metrics:
# - CPU hours
# - Memory usage
# - Network bandwidth
# - Database storage

# Optimize costs:
# - Use smaller instances for dev environments
# - Implement auto-scaling
# - Cache frequently accessed data
# - Optimize LLM API usage
```

#### LLM Cost Management
```python
# Implement cost tracking
# backend/app/utils/cost_tracking.py
class CostTracker:
    def track_llm_usage(self, model, input_tokens, output_tokens):
        cost = calculate_cost(model, input_tokens, output_tokens)
        self.log_cost(cost)
        return cost

# Use in MIL
async def generate_response(self, request):
    response = await self.provider.generate(request)
    self.cost_tracker.track_llm_usage(
        request.model,
        request.input_tokens,
        response.output_tokens
    )
    return response
```

## Support and Resources

### Railway Support
- **Documentation**: [docs.railway.app](https://docs.railway.app)
- **Community**: [Discord](https://discord.gg/railway)
- **Status Page**: [railway.app/status](https://railway.app/status)
- **Support**: help@railway.app

### Z2 Platform Support
- **Documentation**: This repository's docs/
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Community**: Discord (link in README)

---

*This Railway deployment guide is maintained to reflect current best practices. Last updated: 2024-12-19*