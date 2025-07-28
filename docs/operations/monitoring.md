# Z2 Platform Monitoring and Observability Guide

This guide covers setting up comprehensive monitoring, logging, and observability for the Z2 AI Workforce Platform.

## Table of Contents

1. [Overview](#overview)
2. [Metrics Collection](#metrics-collection)
3. [Logging Strategy](#logging-strategy)
4. [Health Checks](#health-checks)
5. [Alerting](#alerting)
6. [Dashboards](#dashboards)
7. [Distributed Tracing](#distributed-tracing)
8. [Performance Monitoring](#performance-monitoring)

## Overview

The Z2 platform implements a comprehensive observability stack:

- **Metrics**: Prometheus for collection, Grafana for visualization
- **Logging**: Structured logging with correlation IDs, ELK stack for aggregation
- **Health Checks**: Multi-level health endpoints for Kubernetes probes
- **Error Tracking**: Sentry for exception tracking and performance monitoring
- **Distributed Tracing**: OpenTelemetry for request tracing

### Key Monitoring Endpoints

| Endpoint | Purpose | Description |
|----------|---------|-------------|
| `/health` | General health | Comprehensive service health check |
| `/health/live` | Liveness probe | Basic application responsiveness |
| `/health/ready` | Readiness probe | Service readiness for traffic |
| `/metrics` | Prometheus metrics | Metrics in Prometheus format |
| `/metrics/json` | JSON metrics | Human-readable metrics |

## Metrics Collection

### Prometheus Metrics

The Z2 backend exposes the following metrics:

#### HTTP Metrics
```python
# Request counters
z2_http_requests_total{method="GET", endpoint="/api/v1/agents", status_code="200"}

# Response time histograms
z2_http_request_duration_seconds{method="POST", endpoint="/api/v1/workflows"}

# Requests in progress
z2_http_requests_in_progress
```

#### Business Metrics
```python
# LLM provider requests
z2_model_requests_total{provider="openai", model="gpt-4o-mini", status="success"}

# Model response times
z2_model_request_duration_seconds{provider="anthropic", model="claude-3-sonnet"}

# Active agents and workflows
z2_active_agents
z2_workflow_executions_total{status="completed"}
```

#### Infrastructure Metrics
```python
# Database connections
z2_database_connections

# Redis operations
z2_redis_operations_total{operation="get", status="success"}
```

### Custom Metrics

Add custom metrics for business-specific monitoring:

```python
from prometheus_client import Counter, Histogram, Gauge

# Custom business metrics
user_registrations = Counter(
    'z2_user_registrations_total',
    'Total user registrations',
    ['source']
)

task_processing_time = Histogram(
    'z2_task_processing_seconds',
    'Time spent processing tasks',
    ['task_type', 'agent_role']
)

# Usage in code
user_registrations.labels(source='web').inc()
task_processing_time.labels(task_type='analysis', agent_role='researcher').observe(2.5)
```

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'z2-backend'
    static_configs:
      - targets: ['z2-backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
    
  - job_name: 'z2-backend-k8s'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names: [z2, z2-staging, z2-production]
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

## Logging Strategy

### Structured Logging

Z2 uses structured logging with correlation IDs for request tracing:

```python
import structlog
import uuid
from contextvars import ContextVar

# Correlation ID context
correlation_id_var: ContextVar[str] = ContextVar('correlation_id')

logger = structlog.get_logger(__name__)

# Example log entry
logger.info(
    "Agent execution started",
    agent_id="agent-123",
    workflow_id="workflow-456",
    user_id="user-789",
    correlation_id=correlation_id_var.get(),
    duration_ms=150.5
)
```

### Log Levels and Categories

#### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General application flow
- **WARNING**: Potentially harmful situations
- **ERROR**: Error events that don't stop the application
- **CRITICAL**: Very serious errors

#### Log Categories
```python
# Authentication logs
auth_logger = structlog.get_logger("z2.auth")
auth_logger.info("User login successful", user_id="123", method="password")

# Agent execution logs
agent_logger = structlog.get_logger("z2.agents")
agent_logger.info("Agent task completed", agent_id="agent-123", task_type="analysis")

# LLM provider logs
llm_logger = structlog.get_logger("z2.llm")
llm_logger.warning("Rate limit approached", provider="openai", requests_remaining=10)
```

### Centralized Logging with ELK Stack

#### Elasticsearch Configuration
```yaml
# elasticsearch.yml
cluster.name: z2-logs
node.name: elasticsearch-1
network.host: 0.0.0.0
discovery.type: single-node
xpack.security.enabled: false

# JVM settings
-Xms2g
-Xmx2g
```

#### Logstash Pipeline
```ruby
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
    
    # Parse timestamp
    date {
      match => [ "timestamp", "ISO8601" ]
    }
    
    # Extract correlation ID
    if [correlation_id] {
      mutate {
        add_tag => ["correlated"]
      }
    }
    
    # Classify log levels
    if [level] == "ERROR" or [level] == "CRITICAL" {
      mutate {
        add_tag => ["alert"]
      }
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

#### Filebeat Configuration
```yaml
# filebeat.yml
filebeat.inputs:
- type: container
  paths:
    - '/var/lib/docker/containers/*/*.log'
  
  processors:
  - add_docker_metadata:
      host: "unix:///var/run/docker.sock"
  
  - decode_json_fields:
      fields: ["message"]
      target: ""
      overwrite_keys: true

fields:
  service: z2-backend
  environment: ${ENV:production}

output.logstash:
  hosts: ["logstash:5044"]

logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/filebeat
  name: filebeat
  keepfiles: 7
  permissions: 0644
```

#### Kibana Dashboard Queries
```json
{
  "query": {
    "bool": {
      "must": [
        {"match": {"service": "z2-backend"}},
        {"range": {"@timestamp": {"gte": "now-1h"}}},
        {"match": {"level": "ERROR"}}
      ]
    }
  },
  "aggs": {
    "error_count_by_endpoint": {
      "terms": {
        "field": "endpoint.keyword",
        "size": 10
      }
    }
  }
}
```

## Health Checks

### Health Check Architecture

```mermaid
graph TD
    A[Load Balancer] -->|Health Check| B[/health]
    K[Kubernetes] -->|Liveness| C[/health/live]
    K -->|Readiness| D[/health/ready]
    
    B --> E[Database Check]
    B --> F[Redis Check]
    B --> G[LLM Provider Check]
    B --> H[System Resources]
    
    D --> E
    D --> F
    D --> G
    
    C --> I[Basic App Check]
```

### Health Check Implementation

```python
# Enhanced health checker
class HealthChecker:
    async def comprehensive_health_check(self) -> dict:
        checks = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_llm_providers(),
            self.check_system_resources(),
            return_exceptions=True
        )
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "checks": {
                "database": checks[0],
                "redis": checks[1], 
                "llm_providers": checks[2],
                "system": checks[3]
            }
        }
        
        # Determine overall status
        failed_checks = [
            name for name, check in health_status["checks"].items()
            if isinstance(check, Exception) or check.get("status") != "healthy"
        ]
        
        if failed_checks:
            if len(failed_checks) >= 2:
                health_status["status"] = "unhealthy"
            else:
                health_status["status"] = "degraded"
            health_status["failed_checks"] = failed_checks
            
        return health_status
```

### Kubernetes Health Probe Configuration

```yaml
# Deployment health probes
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
  successThreshold: 1

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
  successThreshold: 1

startupProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 30
```

## Alerting

### Prometheus Alerting Rules

```yaml
# alerts.yml
groups:
- name: z2.rules
  rules:
  
  # Application alerts
  - alert: HighErrorRate
    expr: |
      (
        rate(z2_http_requests_total{status_code=~"5.."}[5m]) /
        rate(z2_http_requests_total[5m])
      ) * 100 > 5
    for: 2m
    labels:
      severity: warning
      service: z2-backend
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }}% for the last 5 minutes"
      
  - alert: HighResponseTime
    expr: |
      histogram_quantile(0.95, 
        rate(z2_http_request_duration_seconds_bucket[5m])
      ) > 2
    for: 5m
    labels:
      severity: warning
      service: z2-backend
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }}s"
      
  - alert: ServiceDown
    expr: up{job="z2-backend"} == 0
    for: 1m
    labels:
      severity: critical
      service: z2-backend
    annotations:
      summary: "Z2 Backend service is down"
      description: "Z2 Backend has been down for more than 1 minute"
      
  # Infrastructure alerts
  - alert: DatabaseConnectionsHigh
    expr: z2_database_connections > 80
    for: 5m
    labels:
      severity: warning
      component: database
    annotations:
      summary: "High database connection count"
      description: "Database connections: {{ $value }}"
      
  - alert: MemoryUsageHigh
    expr: |
      (
        container_memory_usage_bytes{pod=~"z2-backend-.*"} /
        container_spec_memory_limit_bytes{pod=~"z2-backend-.*"}
      ) * 100 > 85
    for: 5m
    labels:
      severity: warning
      component: memory
    annotations:
      summary: "High memory usage"
      description: "Memory usage is {{ $value }}%"
```

### Alertmanager Configuration

```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@z2.com'

route:
  group_by: ['alertname', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  
  routes:
  - match:
      severity: critical
    receiver: 'critical-alerts'
    
  - match:
      service: z2-backend
    receiver: 'backend-team'

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://slack-webhook/alerts'
    
- name: 'critical-alerts'
  email_configs:
  - to: 'oncall@z2.com'
    subject: 'CRITICAL: {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      {{ end }}
      
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/xxx'
    channel: '#alerts-critical'
    title: 'CRITICAL Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
    
- name: 'backend-team'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/xxx'
    channel: '#backend-alerts'
    title: 'Backend Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

## Dashboards

### Grafana Dashboard Configuration

The Z2 platform includes pre-configured Grafana dashboards:

#### Overview Dashboard
- Request rate and response times
- Error rates by endpoint
- Active agents and workflows
- System resource usage

#### Performance Dashboard
- LLM provider metrics
- Database performance
- Cache hit rates
- Queue processing times

#### Infrastructure Dashboard
- Container metrics
- Kubernetes cluster health
- Network traffic
- Storage usage

### Dashboard Provisioning

```yaml
# grafana-datasources.yml
apiVersion: 1

datasources:
- name: Prometheus
  type: prometheus
  access: proxy
  url: http://prometheus:9090
  isDefault: true
  
- name: Elasticsearch
  type: elasticsearch
  access: proxy
  url: http://elasticsearch:9200
  database: "z2-logs-*"
  timeField: "@timestamp"
```

```yaml
# grafana-dashboards.yml
apiVersion: 1

providers:
- name: 'Z2 Dashboards'
  folder: 'Z2'
  type: file
  options:
    path: /etc/grafana/provisioning/dashboards
```

## Distributed Tracing

### OpenTelemetry Integration

```python
# tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Usage in code
@tracer.start_as_current_span("agent_execution")
async def execute_agent(agent_id: str, task: str):
    span = trace.get_current_span()
    span.set_attribute("agent.id", agent_id)
    span.set_attribute("task.type", task)
    
    try:
        result = await perform_task(task)
        span.set_attribute("task.result", "success")
        return result
    except Exception as e:
        span.set_attribute("task.result", "error")
        span.record_exception(e)
        raise
```

## Performance Monitoring

### Application Performance Monitoring (APM)

#### Sentry Configuration

```python
# Enhanced Sentry setup
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production",
    release="z2@1.0.0",
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
    integrations=[
        FastApiIntegration(auto_enabling_integrations=True),
        SqlalchemyIntegration(),
    ],
    before_send=filter_transactions,
    attach_stacktrace=True,
    send_default_pii=False
)

def filter_transactions(event, hint):
    # Filter out health check noise
    if event.get('transaction') in ['/health', '/health/live', '/health/ready']:
        return None
    return event
```

#### Custom Performance Metrics

```python
# Performance tracking
import time
from contextlib import contextmanager

@contextmanager
def track_performance(operation: str, **tags):
    start_time = time.time()
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        
        # Record to metrics
        metrics_collector.record_operation_duration(operation, duration, **tags)
        
        # Send to Sentry if slow
        if duration > 5.0:
            sentry_sdk.set_tag("slow_operation", operation)
            sentry_sdk.capture_message(
                f"Slow operation detected: {operation}",
                level="warning"
            )

# Usage
async def process_workflow(workflow_id: str):
    with track_performance("workflow_processing", workflow_id=workflow_id):
        # Processing logic
        pass
```

### Database Performance Monitoring

```sql
-- Enable pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Query performance monitoring
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    stddev_exec_time,
    rows
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Lock monitoring
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS current_statement_in_blocking_process
FROM pg_catalog.pg_locks blocked_locks
    JOIN pg_catalog.pg_stat_activity blocked_activity 
        ON blocked_activity.pid = blocked_locks.pid
    JOIN pg_catalog.pg_locks blocking_locks 
        ON blocking_locks.locktype = blocked_locks.locktype
    JOIN pg_catalog.pg_stat_activity blocking_activity 
        ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

## Monitoring Runbook

### Daily Monitoring Checklist

1. **System Health**
   - [ ] Check overall service status
   - [ ] Review error rates and response times
   - [ ] Verify all health checks are passing

2. **Resource Usage**
   - [ ] Monitor CPU and memory usage
   - [ ] Check database connection pools
   - [ ] Review disk space usage

3. **Business Metrics**
   - [ ] Check user activity levels
   - [ ] Monitor agent execution success rates
   - [ ] Review LLM provider API usage

4. **Alerts and Issues**
   - [ ] Review any active alerts
   - [ ] Check Sentry for new errors
   - [ ] Analyze slow queries and operations

### Incident Response

1. **Immediate Response**
   - Check service status dashboards
   - Review recent alerts and logs
   - Identify affected components

2. **Diagnosis**
   - Use correlation IDs to trace requests
   - Check infrastructure metrics
   - Review application logs

3. **Resolution**
   - Apply fixes based on runbook procedures
   - Monitor recovery metrics
   - Update incident documentation

4. **Post-Incident**
   - Conduct post-mortem analysis
   - Update monitoring and alerting
   - Improve runbook procedures