# Z2 Platform Operations Documentation

This directory contains comprehensive operational documentation for the Z2 AI Workforce Platform.

## Documentation Structure

### Core Guides
- **[Deployment Guide](deployment.md)** - Complete deployment instructions for all environments
- **[Monitoring Guide](monitoring.md)** - Observability, metrics, and monitoring setup
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and resolution procedures

### Quick Reference
- **[Environment Configuration](#environment-configuration)** - Key settings per environment
- **[Health Check Endpoints](#health-check-endpoints)** - Monitoring endpoints reference
- **[Emergency Procedures](#emergency-procedures)** - Critical incident response

## Environment Configuration

### Development
```bash
# Core settings
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/z2_dev"
REDIS_URL="redis://localhost:6379/0"

# Start with Docker Compose
docker-compose up -d
```

### Staging
```bash
# Core settings
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL="postgresql+asyncpg://user:password@staging-db:5432/z2_staging"
REDIS_URL="redis://staging-redis:6379/0"

# Deploy to Kubernetes
kubectl apply -k k8s/overlays/staging/
```

### Production
```bash
# Core settings
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL="postgresql+asyncpg://user:password@prod-db:5432/z2_prod"
REDIS_URL="redis://prod-redis:6379/0"
SENTRY_DSN="your-production-sentry-dsn"

# Deploy to Kubernetes
kubectl apply -k k8s/overlays/production/
```

## Health Check Endpoints

| Endpoint | Purpose | Use Case |
|----------|---------|----------|
| `/health` | Comprehensive health | Load balancer health checks |
| `/health/live` | Liveness probe | Kubernetes liveness checks |
| `/health/ready` | Readiness probe | Kubernetes readiness checks |
| `/metrics` | Prometheus metrics | Prometheus scraping |
| `/metrics/json` | JSON metrics | Human-readable monitoring |

### Health Check Examples

```bash
# Basic health check
curl http://localhost:8000/health

# Kubernetes probes
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready

# Prometheus metrics
curl http://localhost:8000/metrics
```

## Emergency Procedures

### Service Down
1. **Check status**: `kubectl get pods -n z2-production`
2. **View logs**: `kubectl logs -f deployment/prod-z2-backend -n z2-production`
3. **Scale if needed**: `kubectl scale deployment prod-z2-backend --replicas=3`
4. **Monitor recovery**: Watch health endpoints and metrics

### Database Issues
1. **Check connections**: Monitor `z2_database_connections` metric
2. **Restart if needed**: `kubectl rollout restart deployment/postgres -n z2-production`
3. **Scale backend**: Reduce replicas to lower DB load
4. **Check queries**: Review slow query logs

### High Error Rate
1. **Check Sentry**: Review error trends and stack traces
2. **Check logs**: `kubectl logs deployment/prod-z2-backend -n z2-production | grep ERROR`
3. **Monitor metrics**: Watch error rate trends in Grafana
4. **Rollback if needed**: `kubectl rollout undo deployment/prod-z2-backend`

## Monitoring Quick Start

### Key Metrics to Watch
- **Request Rate**: `rate(z2_http_requests_total[5m])`
- **Error Rate**: `rate(z2_http_requests_total{status_code=~"5.."}[5m])`
- **Response Time**: `histogram_quantile(0.95, rate(z2_http_request_duration_seconds_bucket[5m]))`
- **Active Agents**: `z2_active_agents`
- **Database Connections**: `z2_database_connections`

### Grafana Dashboards
- **Z2 Overview**: General platform metrics
- **Z2 Performance**: Detailed performance analysis
- **Z2 Infrastructure**: System and container metrics

### Log Analysis
```bash
# Recent errors
kubectl logs deployment/prod-z2-backend -n z2-production | grep ERROR | tail -20

# Specific user issues
kubectl logs deployment/prod-z2-backend -n z2-production | grep "user_id=123"

# Performance issues
kubectl logs deployment/prod-z2-backend -n z2-production | grep "duration.*[5-9]\.[0-9]s"
```

## Load Testing

### Quick Load Test
```bash
cd load-tests
./run-load-test.sh --host http://staging.z2.com --users 10 --time 5m
```

### Stress Testing
```bash
./run-load-test.sh --test-type stress --users 50 --time 10m --headless
```

### Performance Baseline
```bash
./run-load-test.sh --test-type basic --users 5 --time 2m --csv baseline
```

## Backup and Recovery

### Database Backup
```bash
# Manual backup
kubectl exec postgres-pod -- pg_dump -U postgres z2_prod > backup_$(date +%Y%m%d).sql

# Automated backup (add to cron)
0 2 * * * /scripts/backup-database.sh
```

### Restore Database
```bash
# Restore from backup
kubectl cp backup_20240101.sql postgres-pod:/tmp/
kubectl exec postgres-pod -- psql -U postgres -d z2_prod < /tmp/backup_20240101.sql
```

## Scaling Guidelines

### Horizontal Scaling
```bash
# Scale backend pods
kubectl scale deployment prod-z2-backend --replicas=5 -n z2-production

# Auto-scaling setup
kubectl autoscale deployment prod-z2-backend --cpu-percent=70 --min=3 --max=10
```

### Vertical Scaling
```yaml
# Increase resource limits
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### Database Scaling
- **Read Replicas**: Set up PostgreSQL read replicas for read-heavy workloads
- **Connection Pooling**: Use PgBouncer for connection management
- **Partitioning**: Partition large tables by date or user

## Security Checklist

### Production Security
- [ ] All secrets stored in Kubernetes secrets
- [ ] TLS enabled for all external communications
- [ ] Network policies configured
- [ ] Pod security contexts enforced
- [ ] Database connections encrypted
- [ ] API rate limiting enabled
- [ ] Monitoring and alerting configured

### Access Control
- [ ] RBAC policies applied
- [ ] Service accounts configured with minimal permissions
- [ ] Secrets rotation scheduled
- [ ] Audit logging enabled

## Support and Escalation

### Contact Information
- **DevOps Team**: devops@z2.com
- **Platform Team**: platform@z2.com
- **On-Call**: oncall@z2.com (emergencies only)

### Escalation Paths
1. **L1 Support**: Basic troubleshooting using runbooks
2. **L2 Support**: DevOps team for infrastructure issues
3. **L3 Support**: Platform team for application issues
4. **Emergency**: On-call engineer for critical outages

### SLA Targets
- **Availability**: 99.9% uptime
- **Response Time**: 95th percentile < 2 seconds
- **Error Rate**: < 1% of all requests
- **Recovery Time**: < 15 minutes for critical issues

## Useful Commands

### Kubernetes
```bash
# Check pod status
kubectl get pods -n z2-production

# View logs
kubectl logs -f deployment/prod-z2-backend -n z2-production

# Port forward for debugging
kubectl port-forward svc/prod-z2-backend 8000:8000 -n z2-production

# Execute commands in pod
kubectl exec -it pod-name -n z2-production -- /bin/bash

# Check resource usage
kubectl top pods -n z2-production
kubectl top nodes
```

### Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Scale services
docker-compose up -d --scale backend=3

# Stop services
docker-compose down
```

### Database
```bash
# Connect to database
kubectl exec -it postgres-pod -n z2-production -- psql -U postgres -d z2_prod

# Check connections
SELECT count(*) FROM pg_stat_activity;

# Check slow queries
SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 5;
```

## Additional Resources

- **API Documentation**: `/docs` endpoint when debug mode is enabled
- **Architecture Diagrams**: `docs/architecture/`
- **Security Documentation**: `docs/security/`
- **Development Setup**: `README.md` in project root

---

For detailed information on any topic, refer to the specific guide files in this directory.