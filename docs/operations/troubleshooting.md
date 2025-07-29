# Z2 Platform Troubleshooting Guide

This guide helps diagnose and resolve common issues with the Z2 AI Workforce Platform.

## Table of Contents

1. [Health Check Issues](#health-check-issues)
2. [Database Problems](#database-problems)
3. [Redis Connection Issues](#redis-connection-issues)
4. [Authentication Problems](#authentication-problems)
5. [LLM Provider Issues](#llm-provider-issues)
6. [Performance Problems](#performance-problems)
7. [Container Issues](#container-issues)
8. [Kubernetes Problems](#kubernetes-problems)
9. [Monitoring and Metrics](#monitoring-and-metrics)
10. [Log Analysis](#log-analysis)

## Health Check Issues

### Symptom: `/health` endpoint returns 503
**Possible Causes:**
- Database connectivity issues
- Redis connection problems
- LLM provider API issues

**Diagnosis:**
```bash
# Check health endpoint details
curl -v http://localhost:8000/health

# Check individual health probes
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready

# Check logs
docker-compose logs backend | grep -i health
kubectl logs deployment/z2-backend -n z2 | grep -i health
```

**Solutions:**
1. Check database connectivity:
```bash
# Test database connection
psql -h db-host -U username -d database_name -c "SELECT 1;"
```

2. Check Redis connectivity:
```bash
# Test Redis connection
redis-cli -h redis-host ping
```

3. Verify environment variables:
```bash
# Check configuration
docker exec backend env | grep -E "(DATABASE_URL|REDIS_URL)"
```

### Symptom: Health checks timeout
**Possible Causes:**
- Slow database queries
- Network latency
- Resource constraints

**Solutions:**
1. Increase health check timeout:
```yaml
# Kubernetes
livenessProbe:
  timeoutSeconds: 10  # Increase from 5
readinessProbe:
  timeoutSeconds: 10
```

2. Optimize database queries:
```sql
-- Check for slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC LIMIT 10;
```

## Database Problems

### Symptom: Connection pool exhausted
**Error:** `asyncpg.exceptions.TooManyConnectionsError`

**Diagnosis:**
```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Check connection limits
SHOW max_connections;

-- Identify blocking queries
SELECT pid, usename, application_name, state, query 
FROM pg_stat_activity 
WHERE state = 'active';
```

**Solutions:**
1. Increase connection pool size:
```python
# In database configuration
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,  # Increase from 10
    max_overflow=30,  # Increase from 20
    pool_pre_ping=True
)
```

2. Implement connection pooling with PgBouncer:
```ini
[databases]
z2_prod = host=localhost port=5432 dbname=z2_prod

[pgbouncer]
pool_mode = transaction
max_client_conn = 100
default_pool_size = 25
```

### Symptom: Migration failures
**Error:** `alembic.util.exc.CommandError`

**Diagnosis:**
```bash
# Check migration status
poetry run alembic current
poetry run alembic history
```

**Solutions:**
1. Run migrations manually:
```bash
# Upgrade to head
poetry run alembic upgrade head

# Downgrade if needed
poetry run alembic downgrade -1
```

2. Fix migration conflicts:
```bash
# Generate new migration
poetry run alembic revision --autogenerate -m "fix_conflict"
```

## Redis Connection Issues

### Symptom: Redis connection refused
**Error:** `redis.exceptions.ConnectionError`

**Diagnosis:**
```bash
# Test Redis connectivity
redis-cli -h redis-host -p 6379 ping

# Check Redis logs
docker logs redis-container
kubectl logs deployment/redis -n z2
```

**Solutions:**
1. Verify Redis configuration:
```bash
# Check Redis config
redis-cli CONFIG GET "*"

# Check Redis info
redis-cli INFO
```

2. Restart Redis service:
```bash
# Docker Compose
docker-compose restart redis

# Kubernetes
kubectl rollout restart deployment/redis -n z2
```

### Symptom: Redis memory issues
**Error:** `OOM command not allowed when used memory > 'maxmemory'`

**Solutions:**
1. Increase Redis memory:
```yaml
# Kubernetes
resources:
  limits:
    memory: "1Gi"  # Increase memory
```

2. Configure eviction policy:
```redis
# redis.conf
maxmemory-policy allkeys-lru
```

## Authentication Problems

### Symptom: JWT token errors
**Error:** `Invalid token` or `Token expired`

**Diagnosis:**
```bash
# Check token with online JWT decoder
# Verify SECRET_KEY is consistent across instances
```

**Solutions:**
1. Ensure SECRET_KEY consistency:
```bash
# Check all instances have same secret
kubectl get secret z2-secrets -o yaml -n z2
```

2. Adjust token expiration:
```python
# Increase token lifetime
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Increase from 30
```

### Symptom: User login failures
**Error:** `Invalid credentials`

**Diagnosis:**
```sql
-- Check user exists
SELECT id, email, is_active FROM users WHERE email = 'user@example.com';

-- Check password hash
SELECT password_hash FROM users WHERE email = 'user@example.com';
```

**Solutions:**
1. Reset user password:
```python
# In Python shell
from app.core.security import get_password_hash
new_hash = get_password_hash("new_password")
# Update in database
```

## LLM Provider Issues

### Symptom: OpenAI API errors
**Error:** `openai.AuthenticationError` or `RateLimitError`

**Diagnosis:**
```bash
# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models

# Check rate limits in logs
grep -i "rate.limit" logs/
```

**Solutions:**
1. Verify API keys:
```bash
# Check environment variables
echo $OPENAI_API_KEY | head -c 20
```

2. Implement retry logic:
```python
# Add exponential backoff
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_openai_api():
    # API call here
    pass
```

### Symptom: Model not found errors
**Error:** `Model 'gpt-4' not found`

**Solutions:**
1. Update model names:
```python
# Use current model names
DEFAULT_MODEL = "gpt-4o-mini"  # Updated name
```

2. Check available models:
```python
import openai
client = openai.OpenAI()
models = client.models.list()
print([model.id for model in models.data])
```

## Performance Problems

### Symptom: High response times
**Diagnosis:**
```bash
# Check metrics
curl http://localhost:8000/metrics | grep duration

# Check system resources
top
htop
df -h
```

**Solutions:**
1. Optimize database queries:
```sql
-- Add indexes
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_agents_user_id ON agents(user_id);
```

2. Implement caching:
```python
# Add Redis caching
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_operation():
    # Cached operation
    pass
```

### Symptom: Memory leaks
**Diagnosis:**
```bash
# Monitor memory usage
docker stats
kubectl top pods -n z2

# Check for memory leaks in logs
grep -i "memory" logs/
```

**Solutions:**
1. Increase memory limits:
```yaml
resources:
  limits:
    memory: "2Gi"
```

2. Optimize connection handling:
```python
# Ensure proper connection cleanup
async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
```

## Container Issues

### Symptom: Container startup failures
**Error:** `Exit code 1` or `CrashLoopBackOff`

**Diagnosis:**
```bash
# Check container logs
docker logs container-name
kubectl logs pod-name -n z2

# Check container events
kubectl describe pod pod-name -n z2
```

**Solutions:**
1. Fix startup dependencies:
```yaml
# Add init containers
initContainers:
- name: wait-for-db
  image: postgres:15-alpine
  command: ['sh', '-c', 'until pg_isready -h postgres; do sleep 1; done']
```

2. Adjust resource limits:
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

### Symptom: Permission denied errors
**Error:** `Permission denied` when accessing files

**Solutions:**
1. Fix file permissions:
```dockerfile
# In Dockerfile
RUN chown -R appuser:appuser /app
USER appuser
```

2. Use security context:
```yaml
# Kubernetes
securityContext:
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
```

## Kubernetes Problems

### Symptom: Pod scheduling failures
**Error:** `Insufficient resources` or `MatchNodeSelector`

**Diagnosis:**
```bash
# Check node resources
kubectl describe nodes

# Check pod events
kubectl describe pod pod-name -n z2
```

**Solutions:**
1. Adjust resource requests:
```yaml
resources:
  requests:
    memory: "256Mi"  # Reduce requests
    cpu: "100m"
```

2. Add node affinity:
```yaml
affinity:
  nodeAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      preference:
        matchExpressions:
        - key: node-type
          operator: In
          values: ["compute"]
```

### Symptom: Service discovery issues
**Error:** `Connection refused` between services

**Diagnosis:**
```bash
# Test service connectivity
kubectl exec -it pod-name -n z2 -- nslookup z2-backend
kubectl exec -it pod-name -n z2 -- curl http://z2-backend:8000/health
```

**Solutions:**
1. Check service configuration:
```bash
kubectl get svc -n z2
kubectl describe svc z2-backend -n z2
```

2. Verify network policies:
```bash
kubectl get networkpolicies -n z2
```

## Monitoring and Metrics

### Symptom: Missing metrics
**Problem:** Prometheus not scraping metrics

**Diagnosis:**
```bash
# Check Prometheus targets
curl http://prometheus:9090/api/v1/targets

# Test metrics endpoint
curl http://z2-backend:8000/metrics
```

**Solutions:**
1. Add Prometheus annotations:
```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8000"
    prometheus.io/path: "/metrics"
```

2. Configure service discovery:
```yaml
# prometheus.yml
- job_name: 'z2-backend'
  kubernetes_sd_configs:
  - role: pod
```

### Symptom: Grafana dashboard not loading
**Solutions:**
1. Import dashboard JSON:
```bash
# Copy dashboard file to Grafana
kubectl cp z2-overview.json grafana-pod:/tmp/
```

2. Check data source connection:
```bash
# Test Prometheus connection in Grafana
# Settings > Data Sources > Prometheus > Test
```

## Log Analysis

### Common Log Patterns

**Error Patterns:**
```bash
# Find error patterns
grep -E "(ERROR|CRITICAL|Exception)" logs/app.log

# Database errors
grep -E "(database|connection|pool)" logs/app.log

# Authentication errors
grep -E "(auth|token|login)" logs/app.log
```

**Performance Analysis:**
```bash
# Find slow requests
grep -E "duration.*[5-9]\.[0-9]{3}s" logs/app.log

# Memory warnings
grep -E "(memory|oom)" logs/app.log

# High CPU usage
grep -E "(cpu|load)" logs/app.log
```

### Log Aggregation

**ELK Stack Setup:**
```yaml
# elasticsearch.yml
cluster.name: z2-logs
network.host: 0.0.0.0

# logstash.conf
input {
  beats {
    port => 5044
  }
}
filter {
  if [fields][service] == "z2-backend" {
    json {
      source => "message"
    }
  }
}
output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "z2-logs-%{+YYYY.MM.dd}"
  }
}
```

**Filebeat Configuration:**
```yaml
filebeat.inputs:
- type: container
  paths:
    - '/var/lib/docker/containers/*/*.log'
  fields:
    service: z2-backend
    environment: production

output.logstash:
  hosts: ["logstash:5044"]
```

## Emergency Procedures

### Database Recovery
1. Stop all application instances
2. Restore from latest backup
3. Check data integrity
4. Restart applications
5. Monitor error logs

### Complete System Recovery
1. Scale down to zero replicas
2. Restore database and Redis
3. Update configurations
4. Scale up gradually
5. Run health checks
6. Verify functionality

### Rollback Procedure
```bash
# Kubernetes rollback
kubectl rollout undo deployment/z2-backend -n z2
kubectl rollout status deployment/z2-backend -n z2

# Docker rollback
docker-compose down
docker-compose up -d
```

## Getting Help

- Check logs first: `kubectl logs -f deployment/z2-backend -n z2`
- Monitor metrics: http://grafana.z2.com/dashboards
- Review error traces in Sentry
- Contact: ops-team@z2.com
- Escalation: DevOps team lead