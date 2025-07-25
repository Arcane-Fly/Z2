# Z2 MCP Server - Deployment Guide

This guide covers deploying the Z2 MCP (Model Context Protocol) server to Railway.com and using the API.

## Railway.com Deployment

### Prerequisites

1. Railway.com account
2. GitHub repository with Z2 code
3. Environment variables configured

### Quick Deploy

1. **Connect Repository**
   ```bash
   # Connect your GitHub repository to Railway
   railway login
   railway link
   ```

2. **Configure Environment Variables**
   
   Set these variables in Railway dashboard or via CLI:
   
   ```bash
   # Required for production
   DEBUG=false
   LOG_LEVEL=INFO
   SECRET_KEY=your-production-secret-key-here
   
   # Database (Railway will provide these automatically)
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   
   # CORS for your frontend
   CORS_ORIGINS=["https://your-frontend-domain.railway.app"]
   
   # LLM Provider API Keys
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   GROQ_API_KEY=your-groq-key
   GOOGLE_API_KEY=your-google-key
   PERPLEXITY_API_KEY=your-perplexity-key
   ```

3. **Deploy**
   ```bash
   railway up
   ```

### Production Configuration

The `railway.toml` file includes all necessary configuration:

- **Port Configuration**: Uses `$PORT` environment variable
- **Health Checks**: `/health` endpoint for Railway monitoring
- **Services**: Backend, Frontend, PostgreSQL, Redis
- **Domains**: Automatic HTTPS domains

### Monitoring

- **Health Check**: `GET /health`
- **Metrics**: Available on port 8001 (if enabled)
- **Logs**: Available in Railway dashboard

## API Documentation

### MCP Protocol Endpoints

The Z2 server implements the [MCP specification](https://modelcontextprotocol.io/specification/2025-03-26).

#### Session Management

**Initialize MCP Session**
```http
POST /api/v1/mcp/initialize
Content-Type: application/json

{
  "protocolVersion": "2025-03-26",
  "capabilities": {
    "resources": {"subscribe": true},
    "tools": {"listChanged": true},
    "prompts": {"listChanged": true}
  },
  "clientInfo": {
    "name": "your-client",
    "version": "1.0.0"
  }
}
```

Response:
```json
{
  "protocolVersion": "2025-03-26",
  "serverInfo": {
    "name": "Z2 AI Workforce Platform",
    "version": "1.0.0"
  },
  "capabilities": {
    "resources": {"subscribe": true, "listChanged": true},
    "tools": {"listChanged": true},
    "prompts": {"listChanged": true},
    "sampling": {}
  }
}
```

#### Resources

**List Resources**
```http
GET /api/v1/mcp/resources
```

**Get Resource**
```http
GET /api/v1/mcp/resources/{resource_uri}
```

#### Tools

**List Tools**
```http
GET /api/v1/mcp/tools
```

**Execute Tool**
```http
POST /api/v1/mcp/tools/{tool_name}/call
Content-Type: application/json

{
  "agent_id": "default",
  "task": "Analyze the provided data",
  "parameters": {"format": "json"}
}
```

#### Prompts

**List Prompts**
```http
GET /api/v1/mcp/prompts
```

**Get Prompt**
```http
GET /api/v1/mcp/prompts/{prompt_name}?arguments={"data": "sample"}
```

### Consent & Access Control

#### Request Consent

```http
POST /api/v1/consent/consent/request
Content-Type: application/json

{
  "user_id": "user-123",
  "resource_type": "tool",
  "resource_name": "execute_agent",
  "description": "Execute agent for data analysis",
  "permissions": ["agent:execute"],
  "expires_in_hours": 24
}
```

Response:
```json
{
  "consent_id": "consent-uuid",
  "status": "granted",
  "granted_at": "2025-07-25T07:50:01Z",
  "expires_at": "2025-07-26T07:50:01Z",
  "permissions": ["agent:execute"]
}
```

#### Check Access

```http
POST /api/v1/consent/access/check
Content-Type: application/json

{
  "user_id": "user-123",
  "resource_type": "tool",
  "resource_name": "execute_agent",
  "permissions": ["agent:execute"]
}
```

Response:
```json
{
  "allowed": true,
  "reason": "Access granted"
}
```

#### Audit Logs

```http
GET /api/v1/consent/audit?user_id=user-123&limit=50
```

### Security Features

1. **Consent Management**: All tool/resource access requires explicit user consent
2. **Access Control Policies**: Configurable per-resource permission requirements
3. **Audit Logging**: Complete trail of all access requests and grants
4. **Rate Limiting**: Configurable limits per resource/user
5. **Session Management**: Secure session tracking with expiration

### Error Handling

All endpoints return standard HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid input)
- `401`: Unauthorized (authentication required)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found (resource doesn't exist)
- `422`: Unprocessable Entity (validation error)
- `500`: Internal Server Error

Error responses include detailed messages:
```json
{
  "detail": "Specific error description"
}
```

## Development Setup

### Local Development

1. **Install Dependencies**
   ```bash
   cd backend
   poetry install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run Server**
   ```bash
   poetry run uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
   ```

4. **Run Tests**
   ```bash
   poetry run pytest tests/ -v
   ```

### Testing with MCP Inspector

Use the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) to validate protocol compliance:

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Test your server
mcp-inspector http://localhost:3000/api/v1/mcp
```

### SDK Integration

Example using the Python MCP SDK:

```python
from mcp_client import MCPClient

# Connect to Z2 server
client = MCPClient("http://localhost:3000/api/v1/mcp")

# Initialize session
response = client.initialize({
    "protocolVersion": "2025-03-26",
    "capabilities": {},
    "clientInfo": {"name": "my-app", "version": "1.0.0"}
})

# List available tools
tools = client.list_tools()

# Execute a tool
result = client.call_tool("execute_agent", {
    "agent_id": "default",
    "task": "Analyze quarterly sales data"
})
```

## Production Checklist

- [ ] Environment variables configured
- [ ] Database and Redis services deployed
- [ ] CORS origins set for your frontend
- [ ] Health checks responding
- [ ] SSL/TLS configured (automatic with Railway)
- [ ] API rate limiting configured
- [ ] Monitoring and logging enabled
- [ ] Access control policies defined
- [ ] LLM provider API keys configured
- [ ] Tests passing

## Support

For issues and questions:

1. Check the [MCP specification](https://modelcontextprotocol.io/specification/2025-03-26)
2. Review Railway.com [production checklist](https://docs.railway.com/reference/production-readiness-checklist)
3. Check server logs in Railway dashboard
4. Test endpoints with the included test suite