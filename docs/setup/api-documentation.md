# Z2 API Documentation

## Overview

The Z2 API provides comprehensive access to the AI Workforce Platform's capabilities through a RESTful interface. This documentation covers all endpoints, authentication, request/response formats, and integration patterns.

## Base URL

```
Production:  https://api.z2.ai/v1
Staging:     https://api-staging.z2.ai/v1
Development: http://localhost:8000/api/v1
```

## Authentication

### JWT Token Authentication

All API requests require authentication via JWT tokens included in the Authorization header:

```http
Authorization: Bearer <access_token>
```

### Obtaining Tokens

#### Login Endpoint
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 1800
  }
}
```

#### Token Refresh
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Response Format

All API responses follow a consistent format:

```json
{
  "success": boolean,
  "data": object | array,
  "error": {
    "code": "string",
    "message": "string",
    "details": object
  },
  "meta": {
    "page": number,
    "total": number,
    "timestamp": "string"
  }
}
```

### Success Response
```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Research Assistant",
    "type": "researcher"
  },
  "meta": {
    "timestamp": "2024-12-19T10:30:00Z"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Must be a valid email address"
    }
  },
  "meta": {
    "timestamp": "2024-12-19T10:30:00Z"
  }
}
```

## API Endpoints

### Authentication Endpoints

#### POST /auth/login
Authenticate user and obtain access token.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string", 
  "token_type": "Bearer",
  "expires_in": 1800
}
```

#### POST /auth/refresh
Refresh an expired access token.

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

#### POST /auth/logout
Invalidate the current access token.

### User Management

#### GET /users/me
Get current user profile.

**Response:**
```json
{
  "id": "string",
  "email": "string",
  "name": "string",
  "role": "architect | operator | admin",
  "created_at": "string",
  "updated_at": "string"
}
```

#### PUT /users/me
Update current user profile.

**Request Body:**
```json
{
  "name": "string",
  "email": "string"
}
```

### Agent Management

#### GET /agents
List all agents for the current user.

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20)
- `type` (string): Filter by agent type
- `status` (string): Filter by status

**Response:**
```json
{
  "agents": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "type": "researcher | writer | coder | analyst | validator",
      "status": "active | inactive | error",
      "capabilities": ["string"],
      "config": {},
      "created_at": "string",
      "updated_at": "string"
    }
  ],
  "total": 42,
  "page": 1,
  "pages": 3
}
```

#### POST /agents
Create a new agent.

**Request Body:**
```json
{
  "name": "string",
  "description": "string",
  "type": "researcher | writer | coder | analyst | validator",
  "capabilities": ["string"],
  "system_prompt": "string",
  "config": {
    "model_preferences": {
      "primary_model": "gpt-4o",
      "fallback_model": "gpt-4o-mini",
      "temperature": 0.7,
      "max_tokens": 4096
    },
    "tools": ["web_search", "code_execution"],
    "memory_size": 1000
  }
}
```

#### GET /agents/{id}
Get agent details by ID.

**Response:**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "type": "string",
  "status": "string",
  "capabilities": ["string"],
  "system_prompt": "string",
  "config": {},
  "metrics": {
    "total_executions": 125,
    "success_rate": 0.94,
    "avg_duration_ms": 2350,
    "total_cost_usd": 15.67
  },
  "created_at": "string",
  "updated_at": "string"
}
```

#### PUT /agents/{id}
Update an existing agent.

#### DELETE /agents/{id}
Delete an agent.

#### POST /agents/{id}/test
Test an agent with sample input.

**Request Body:**
```json
{
  "input": "string",
  "context": {}
}
```

**Response:**
```json
{
  "output": "string",
  "execution_time_ms": 1250,
  "tokens_used": 450,
  "cost_usd": 0.023,
  "success": true
}
```

### Workflow Management

#### GET /workflows
List all workflows.

**Query Parameters:**
- `page` (integer): Page number
- `limit` (integer): Items per page
- `status` (string): Filter by status

**Response:**
```json
{
  "workflows": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "agents": ["agent_id_1", "agent_id_2"],
      "status": "draft | active | archived",
      "created_at": "string",
      "updated_at": "string"
    }
  ]
}
```

#### POST /workflows
Create a new workflow.

**Request Body:**
```json
{
  "name": "string",
  "description": "string",
  "definition": {
    "nodes": [
      {
        "id": "node1",
        "type": "agent",
        "agent_id": "string",
        "position": { "x": 100, "y": 100 }
      }
    ],
    "edges": [
      {
        "source": "node1",
        "target": "node2",
        "type": "data_flow"
      }
    ]
  }
}
```

#### POST /workflows/{id}/execute
Execute a workflow.

**Request Body:**
```json
{
  "input_data": {},
  "options": {
    "timeout_seconds": 300,
    "parallel_execution": true,
    "save_intermediate_results": true
  }
}
```

**Response:**
```json
{
  "execution_id": "string",
  "status": "pending",
  "estimated_duration_ms": 30000
}
```

#### GET /workflows/{id}/executions/{execution_id}
Get workflow execution status and results.

**Response:**
```json
{
  "id": "string",
  "workflow_id": "string", 
  "status": "pending | running | completed | failed",
  "progress": 0.65,
  "input_data": {},
  "output_data": {},
  "execution_trace": [
    {
      "timestamp": "string",
      "agent_id": "string",
      "action": "string",
      "result": {}
    }
  ],
  "started_at": "string",
  "completed_at": "string",
  "duration_ms": 25000,
  "total_cost_usd": 0.45
}
```

### Model Management

#### GET /models
List available LLM models and providers.

**Response:**
```json
{
  "providers": [
    {
      "name": "openai",
      "status": "healthy",
      "models": [
        {
          "id": "gpt-4o",
          "name": "GPT-4o",
          "capabilities": ["text", "vision", "tools"],
          "context_window": 128000,
          "cost_per_1k_input": 0.0025,
          "cost_per_1k_output": 0.01,
          "avg_latency_ms": 2500
        }
      ]
    }
  ]
}
```

#### POST /models/test
Test a model with sample input.

**Request Body:**
```json
{
  "model": "gpt-4o",
  "prompt": "string",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

#### GET /models/usage
Get model usage statistics.

**Query Parameters:**
- `timeframe` (string): "1h", "24h", "7d", "30d"
- `group_by` (string): "model", "provider", "user"

**Response:**
```json
{
  "usage": [
    {
      "model": "gpt-4o",
      "requests": 1250,
      "total_tokens": 450000,
      "total_cost_usd": 125.50,
      "avg_latency_ms": 2100
    }
  ],
  "timeframe": "24h"
}
```

### MCP (Model Context Protocol) Endpoints

#### GET /mcp/sessions
List active MCP sessions.

#### POST /mcp/sessions
Create a new MCP session.

#### GET /mcp/tools
List available MCP tools.

#### POST /mcp/tools/{tool_name}
Execute an MCP tool.

### Consent Management

#### POST /consent/request
Request user consent for data processing.

**Request Body:**
```json
{
  "request_type": "data_processing",
  "description": "Process customer data for analytics",
  "data_categories": ["personal_info", "usage_data"],
  "purpose": "analytics",
  "retention_period": "2_years"
}
```

#### GET /consent/status
Get consent status for current user.

#### POST /consent/grant
Grant consent for a specific request.

#### POST /consent/revoke
Revoke previously granted consent.

### Agent-to-Agent (A2A) Protocol

#### POST /a2a/handshake
Initiate A2A handshake between agents.

#### POST /a2a/negotiate
Negotiate communication parameters.

#### POST /a2a/message
Send message between agents.

#### GET /a2a/sessions
List active A2A sessions.

## WebSocket API

### Connection

Connect to WebSocket endpoint for real-time updates:

```
wss://api.z2.ai/ws?token=<access_token>
```

### Message Format

All WebSocket messages follow this format:

```json
{
  "type": "string",
  "id": "string",
  "timestamp": "string",
  "data": {}
}
```

### Event Types

#### Workflow Events
```json
{
  "type": "workflow.status_changed",
  "id": "workflow_123",
  "data": {
    "status": "running",
    "progress": 0.45
  }
}
```

#### Agent Events
```json
{
  "type": "agent.thinking",
  "id": "agent_456", 
  "data": {
    "message": "Analyzing document structure...",
    "progress": 0.2
  }
}
```

#### System Events
```json
{
  "type": "system.notification",
  "data": {
    "level": "info",
    "message": "Scheduled maintenance in 1 hour"
  }
}
```

## Error Codes

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing authentication token |
| `FORBIDDEN` | 403 | Insufficient permissions for this operation |
| `NOT_FOUND` | 404 | Requested resource not found |
| `VALIDATION_ERROR` | 422 | Request data validation failed |
| `RATE_LIMITED` | 429 | Too many requests, rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |

### Agent-Specific Error Codes

| Code | Description |
|------|-------------|
| `AGENT_NOT_FOUND` | Agent with specified ID does not exist |
| `AGENT_CREATION_FAILED` | Failed to create agent |
| `AGENT_EXECUTION_FAILED` | Agent execution encountered an error |
| `INVALID_AGENT_CONFIG` | Agent configuration is invalid |

### Workflow Error Codes

| Code | Description |
|------|-------------|
| `WORKFLOW_NOT_FOUND` | Workflow with specified ID does not exist |
| `WORKFLOW_EXECUTION_FAILED` | Workflow execution failed |
| `INVALID_WORKFLOW_DEFINITION` | Workflow definition is invalid |
| `WORKFLOW_TIMEOUT` | Workflow execution exceeded timeout |

### Model Error Codes

| Code | Description |
|------|-------------|
| `MODEL_NOT_AVAILABLE` | Requested model is not available |
| `MODEL_QUOTA_EXCEEDED` | Model usage quota exceeded |
| `MODEL_API_ERROR` | Error communicating with model provider |
| `INSUFFICIENT_CREDITS` | Not enough credits for model usage |

## Rate Limiting

The API implements rate limiting to ensure fair usage:

### Rate Limits

| Endpoint Pattern | Limit | Window |
|-----------------|-------|---------|
| `/auth/*` | 10 requests | 1 minute |
| `/agents/*` | 100 requests | 1 minute |
| `/workflows/*/execute` | 20 requests | 1 minute |
| `/models/test` | 50 requests | 1 minute |
| `/*` (general) | 1000 requests | 1 minute |

### Rate Limit Headers

Rate limit information is included in response headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
X-RateLimit-Window: 60
```

## SDKs and Integration

### Python SDK

```python
from z2_sdk import Z2Client

# Initialize client
client = Z2Client(
    api_key="your-api-key",
    base_url="https://api.z2.ai/v1"
)

# Create an agent
agent = await client.agents.create(
    name="Research Assistant",
    type="researcher",
    capabilities=["web_search", "document_analysis"]
)

# Execute workflow
execution = await client.workflows.execute(
    workflow_id="workflow-123",
    input_data={"query": "Latest AI developments"}
)

# Monitor execution
async for update in client.workflows.stream_execution(execution.id):
    print(f"Progress: {update.progress}%")
```

### JavaScript SDK

```javascript
import { Z2Client } from '@z2/sdk';

// Initialize client
const client = new Z2Client({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.z2.ai/v1'
});

// Create an agent
const agent = await client.agents.create({
  name: 'Content Writer',
  type: 'writer',
  capabilities: ['content_generation', 'editing']
});

// Execute workflow
const execution = await client.workflows.execute('workflow-123', {
  topic: 'AI in Healthcare'
});
```

### cURL Examples

#### Create Agent
```bash
curl -X POST https://api.z2.ai/v1/agents \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Data Analyst", 
    "type": "analyst",
    "capabilities": ["data_analysis", "visualization"]
  }'
```

#### Execute Workflow
```bash
curl -X POST https://api.z2.ai/v1/workflows/workflow-123/execute \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {"dataset": "sales_q4.csv"},
    "options": {"timeout_seconds": 600}
  }'
```

## Webhooks

Configure webhooks to receive real-time notifications about workflow executions and system events.

### Webhook Configuration

```json
{
  "url": "https://your-app.com/webhooks/z2",
  "events": [
    "workflow.completed",
    "workflow.failed", 
    "agent.error"
  ],
  "secret": "webhook-secret-for-verification"
}
```

### Webhook Payload

```json
{
  "id": "webhook-event-123",
  "type": "workflow.completed",
  "timestamp": "2024-12-19T10:30:00Z",
  "data": {
    "workflow_id": "workflow-123",
    "execution_id": "exec-456",
    "status": "completed",
    "duration_ms": 25000,
    "output_data": {}
  },
  "signature": "sha256=..."
}
```

### Webhook Verification

Verify webhook authenticity using the signature:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected}", signature)
```

## Pagination

Large result sets are paginated using cursor-based pagination:

### Request Parameters
- `limit` (integer): Number of items per page (max 100)
- `cursor` (string): Pagination cursor from previous response

### Response Format
```json
{
  "data": [...],
  "pagination": {
    "has_more": true,
    "next_cursor": "eyJpZCI6IjEyMyJ9",
    "previous_cursor": null,
    "total_count": 1250
  }
}
```

## Health and Status

### Health Check Endpoint

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2024-12-19T10:30:00Z",
  "components": {
    "database": "healthy",
    "redis": "healthy", 
    "llm_providers": {
      "openai": "healthy",
      "anthropic": "healthy"
    }
  },
  "uptime_seconds": 86400
}
```

### Status Page

Monitor API status at: https://status.z2.ai

---

*This API documentation is automatically generated from OpenAPI specifications and is kept up-to-date with the latest API changes. Last updated: 2024-12-19*