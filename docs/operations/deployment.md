# Z2 Platform Deployment Guide

This guide covers deploying the Z2 AI Workforce Platform in different environments using various deployment strategies.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Local Development](#local-development)
4. [Staging Deployment](#staging-deployment)
5. [Production Deployment](#production-deployment)
6. [Kubernetes Deployment](#kubernetes-deployment)
7. [Monitoring Setup](#monitoring-setup)
8. [Backup and Restore](#backup-and-restore)

## Prerequisites

### Required Software
- Docker and Docker Compose
- Kubernetes cluster (for K8s deployment)
- kubectl CLI
- Helm (optional, for Helm charts)
- PostgreSQL 15+
- Redis 7+

### Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
# Application
APP_NAME="Z2 AI Workforce Platform"
DEBUG=false
SECRET_KEY="your-secure-secret-key"

# Database
DATABASE_URL="postgresql+asyncpg://user:password@host:port/database"

# Redis
REDIS_URL="redis://host:port/0"

# LLM Provider API Keys
OPENAI_API_KEY="your-openai-key"
ANTHROPIC_API_KEY="your-anthropic-key"
GROQ_API_KEY="your-groq-key"

# Monitoring
SENTRY_DSN="your-sentry-dsn"
ENABLE_METRICS=true
```

## Environment Configuration

### Development
```bash
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/z2_dev"
REDIS_URL="redis://localhost:6379/0"
```

### Staging
```bash
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL="postgresql+asyncpg://user:password@staging-db:5432/z2_staging"
REDIS_URL="redis://staging-redis:6379/0"
SENTRY_DSN="your-staging-sentry-dsn"
```

### Production
```bash
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL="postgresql+asyncpg://user:password@prod-db:5432/z2_prod"
REDIS_URL="redis://prod-redis:6379/0"
SENTRY_DSN="your-production-sentry-dsn"
ENABLE_METRICS=true
```

## Local Development

### Using Docker Compose

1. **Start services:**
```bash
docker-compose up -d
```

2. **Run database migrations:**
```bash
docker-compose exec backend poetry run alembic upgrade head
```

3. **Access services:**
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

4. **View logs:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Using Poetry (Backend only)

1. **Install dependencies:**
```bash
cd backend
poetry install
```

2. **Start PostgreSQL and Redis:**
```bash
docker-compose up -d postgres redis
```

3. **Run migrations:**
```bash
poetry run alembic upgrade head
```

4. **Start backend:**
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Staging Deployment

### Railway Deployment

This project is configured for deployment on Railway using `railpack.json`. When you create a project from this repository, Railway will automatically provision the `backend`, `frontend`, `postgres`, and `redis` services with the necessary environment variables.

For more information, see the `RAILWAY_DEPLOYMENT.md` file in the root of the repository.

### Docker-based Staging

1. **Build images:**
```bash
docker build -f Dockerfile.backend -t z2-backend:staging .
docker build -f Dockerfile.frontend -t z2-frontend:staging .
```

2. **Run with staging configuration:**
```bash
docker run -d --name z2-backend-staging \
  -p 8000:8000 \
  -e DATABASE_URL="staging-db-url" \
  -e DEBUG=false \
  z2-backend:staging
```

## Production Deployment

### High Availability Setup

#### Load Balancer Configuration
```nginx
upstream z2_backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 443 ssl http2;
    server_name api.z2.yourdomain.com;
    
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;
    
    location / {
        proxy_pass http://z2_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /metrics {
        deny all;
        allow 10.0.0.0/8;  # Internal networks only
        proxy_pass http://z2_backend;
    }
}
```

#### Database Setup
```sql
-- Create production database
CREATE DATABASE z2_prod;
CREATE USER z2_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE z2_prod TO z2_user;

-- Enable extensions
\c z2_prod
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

#### Redis Configuration
```redis
# redis.conf for production
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
```

## Kubernetes Deployment

### Prerequisites
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Install kustomize
curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
```

### Deploy to Staging
```bash
cd k8s/overlays/staging
kubectl apply -k .
```

### Deploy to Production
```bash
cd k8s/overlays/production

# Update secrets first
kubectl create secret generic z2-secrets \
  --from-literal=SECRET_KEY="your-prod-secret" \
  --from-literal=OPENAI_API_KEY="your-openai-key" \
  --from-literal=SENTRY_DSN="your-sentry-dsn" \
  --namespace=z2-production

kubectl apply -k .
```

### Verify Deployment
```bash
# Check pod status
kubectl get pods -n z2-production

# Check services
kubectl get svc -n z2-production

# Check ingress
kubectl get ingress -n z2-production

# View logs
kubectl logs -f deployment/prod-z2-backend -n z2-production
```

### Rolling Updates
```bash
# Update backend image
kubectl set image deployment/prod-z2-backend z2-backend=z2-backend:v1.1.0 -n z2-production

# Check rollout status
kubectl rollout status deployment/prod-z2-backend -n z2-production

# Rollback if needed
kubectl rollout undo deployment/prod-z2-backend -n z2-production
```

## Monitoring Setup

### Prometheus and Grafana

1. **Install Prometheus:**
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack
```

2. **Configure Z2 monitoring:**
```bash
kubectl apply -f monitoring/prometheus/prometheus.yml
```

3. **Import Grafana dashboards:**
```bash
kubectl create configmap z2-dashboard \
  --from-file=monitoring/grafana/dashboards/z2-overview.json \
  -n monitoring
```

### Application Metrics

Monitor these key metrics:
- Request rate: `rate(z2_http_requests_total[5m])`
- Response time: `histogram_quantile(0.95, rate(z2_http_request_duration_seconds_bucket[5m]))`
- Error rate: `rate(z2_http_requests_total{status_code=~"5.."}[5m])`
- Active agents: `z2_active_agents`
- Database connections: `z2_database_connections`

### Alerting Rules

```yaml
groups:
- name: z2.rules
  rules:
  - alert: HighErrorRate
    expr: rate(z2_http_requests_total{status_code=~"5.."}[5m]) > 0.05
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(z2_http_request_duration_seconds_bucket[5m])) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
```

## Backup and Restore

### Database Backup

```bash
# Create backup
pg_dump -h prod-db-host -U z2_user -d z2_prod > z2_backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DB_NAME="z2_prod"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_DIR/z2_backup_$TIMESTAMP.sql
gzip $BACKUP_DIR/z2_backup_$TIMESTAMP.sql

# Keep only last 7 days
find $BACKUP_DIR -name "z2_backup_*.sql.gz" -mtime +7 -delete
```

### Database Restore

```bash
# Restore from backup
gunzip -c z2_backup_20240101_120000.sql.gz | psql -h prod-db-host -U z2_user -d z2_prod
```

### File Storage Backup

```bash
# Backup storage volumes
kubectl exec -n z2-production pod/prod-z2-backend-xxx -- tar czf - /app/storage | \
  kubectl cp z2-production/prod-z2-backend-xxx:/dev/stdin ./storage_backup_$(date +%Y%m%d).tar.gz
```

### Redis Backup

```bash
# Create Redis backup
redis-cli --rdb dump.rdb

# Or use BGSAVE for non-blocking backup
redis-cli BGSAVE
```

## Scaling Strategies

### Horizontal Scaling

```bash
# Scale backend pods
kubectl scale deployment prod-z2-backend --replicas=5 -n z2-production

# Auto-scaling based on CPU
kubectl autoscale deployment prod-z2-backend --cpu-percent=70 --min=3 --max=10 -n z2-production
```

### Vertical Scaling

```yaml
# Update resource limits
spec:
  containers:
  - name: z2-backend
    resources:
      requests:
        memory: "2Gi"
        cpu: "1000m"
      limits:
        memory: "4Gi"
        cpu: "2000m"
```

### Database Scaling

1. **Read Replicas:**
```sql
-- Create read replica
CREATE PUBLICATION z2_pub FOR ALL TABLES;
```

2. **Connection Pooling:**
```bash
# Install PgBouncer
helm install pgbouncer bitnami/pgbouncer
```

3. **Partitioning:**
```sql
-- Partition large tables by date
CREATE TABLE workflows_2024 PARTITION OF workflows
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for common issues and solutions.

## Security

See [security.md](security.md) for security best practices and configurations.