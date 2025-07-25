# Z2 Backend - MCP Server

The backend API for the Z2 AI Workforce Platform, implementing the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/specification/2025-03-26) for AI agent orchestration.

## Features

✅ **MCP Protocol Compliance**: Full implementation of MCP 2025-03-26 specification  
✅ **Consent & Access Control**: Secure resource access with user consent workflows  
✅ **Multi-Agent Orchestration**: Dynamic agent composition and workflow management  
✅ **Railway.com Ready**: Production-ready deployment configuration  
✅ **Comprehensive Testing**: Integration tests for all core functionality  

## Quick Start

### Development Setup

```bash
# Install dependencies
poetry install

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run server
poetry run uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload

# Run tests
poetry run pytest tests/ -v
```

### API Endpoints

- **Health Check**: `GET /health`
- **MCP Protocol**: `/api/v1/mcp/*`
- **Consent Management**: `/api/v1/consent/*`
- **Agent Management**: `/api/v1/agents/*`
- **Workflow Management**: `/api/v1/workflows/*`

### Test MCP Compliance

```bash
# Test MCP endpoints
curl http://localhost:3000/api/v1/mcp/resources
curl http://localhost:3000/api/v1/mcp/tools

# Initialize MCP session
curl -X POST http://localhost:3000/api/v1/mcp/initialize \
  -H "Content-Type: application/json" \
  -d '{"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}'
```

### Request Consent

```bash
# Request access to execute an agent
curl -X POST http://localhost:3000/api/v1/consent/consent/request \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user", "resource_type": "tool", "resource_name": "execute_agent", "description": "Test agent execution", "permissions": ["agent:execute"]}'
```

## Architecture

- **FastAPI**: High-performance async API framework
- **SQLAlchemy**: Database ORM with async support  
- **Redis**: Session and cache management
- **Pydantic**: Data validation and serialization
- **Pytest**: Comprehensive test coverage

## Documentation

- [Deployment Guide](./DEPLOYMENT.md) - Railway.com deployment instructions
- [API Documentation](http://localhost:3000/docs) - Interactive API docs (when running)
- [MCP Specification](https://modelcontextprotocol.io/specification/2025-03-26) - Protocol reference

## Environment Variables

Key configuration options:

```bash
# Application
DEBUG=false
LOG_LEVEL=INFO
PORT=3000

# Database
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...

# LLM Providers
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
GROQ_API_KEY=your-key

# MCP Configuration
MCP_PROTOCOL_VERSION=2025-03-26
ENABLE_MCP_SESSIONS=true
SESSION_TIMEOUT_MINUTES=30
```

## Production Deployment

Deploy to Railway.com with one command:

```bash
railway up
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete production setup instructions.