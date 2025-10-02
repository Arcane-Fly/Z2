# MCP Protocol Operations

This directory contains JSON Schema contracts for core MCP (Model Context Protocol) operations.

## mcp.initialize (v1)

**Purpose:** Initialize MCP session with capability negotiation.

### Request

Validates against: `contracts/mcp/initialize.request.json`

- `protocolVersion` (string, required): MCP protocol version in YYYY-MM-DD format
- `capabilities` (object, required): Client capabilities
  - `resources` (object, optional): Resource-related capabilities
  - `tools` (object, optional): Tool-related capabilities
  - `prompts` (object, optional): Prompt-related capabilities
  - `sampling` (object, optional): Sampling-related capabilities
- `clientInfo` (object, required): Client application information
  - `name` (string, required): Client application name
  - `version` (string, required): Client application version

**Example:**
```json
{
  "protocolVersion": "2025-03-26",
  "capabilities": {
    "resources": {"subscribe": true},
    "tools": {"listChanged": true}
  },
  "clientInfo": {
    "name": "test-client",
    "version": "1.0.0"
  }
}
```

### Response

Validates against: `contracts/mcp/initialize.response.json`

- `protocolVersion` (string, required): MCP protocol version
- `serverInfo` (object, required): Server application information
  - `name` (string, required): Server application name
  - `version` (string, required): Server application version
- `capabilities` (object, required): Server capabilities
- `session_id` (string, required): Unique session identifier (UUID)

**Example:**
```json
{
  "protocolVersion": "2025-03-26",
  "serverInfo": {
    "name": "Z2 AI Workforce Platform",
    "version": "1.0.0"
  },
  "capabilities": {
    "resources": {"subscribe": true, "listChanged": true},
    "tools": {"listChanged": true, "progress": true, "cancellation": true}
  },
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Errors

Uses standard `error.envelope.json` with codes:
- `INVALID_INPUT`: Invalid request format or missing required fields
- `AUTH_REQUIRED`: Authentication required but not provided
- `UNAVAILABLE`: Server temporarily unavailable
- `INTERNAL_ERROR`: Unexpected server error

## Tool Definition Schema

**Purpose:** Define MCP tool metadata and input schema.

Validates against: `contracts/mcp/tool.definition.json`

- `name` (string, required): Unique tool identifier (alphanumeric + underscore)
- `description` (string, required): Human-readable tool description
- `inputSchema` (object, required): JSON Schema for tool input parameters
  - Must be an object schema with `properties` and optionally `required`

**Example:**
```json
{
  "name": "execute_agent",
  "description": "Execute an AI agent with specified parameters",
  "inputSchema": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Agent name"
      },
      "agents": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of agent IDs to execute"
      }
    },
    "required": ["name", "agents"]
  }
}
```

## Resource Definition Schema

**Purpose:** Define MCP resource metadata.

Validates against: `contracts/mcp/resource.definition.json`

- `uri` (string, required): Unique resource URI
- `name` (string, required): Human-readable resource name
- `description` (string, optional): Resource description
- `mimeType` (string, optional): Resource MIME type (e.g., "application/json")

**Example:**
```json
{
  "uri": "agent://default",
  "name": "Default Agent",
  "description": "Default Z2 AI agent for general tasks",
  "mimeType": "application/json"
}
```

## Usage in Backend

```python
from app.utils.contract_validator import validate_request, validate_response

# In MCP endpoint handler
@router.post("/initialize")
async def initialize_mcp_session(request: MCPInitializeRequest):
    # Validate incoming request
    try:
        validate_request("mcp.initialize", request.model_dump())
    except ContractValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Process request...
    response = create_response()
    
    # Validate outgoing response
    try:
        validate_response("mcp.initialize", response)
    except ContractValidationError as e:
        # Log error but continue (gradual adoption)
        logger.error(f"Response validation failed: {e}")
    
    return response
```

## Version History

- **v1.0.0** (2025-01-15): Initial schema definitions for MCP protocol
  - Initialize request/response
  - Tool definition
  - Resource definition

## References

- [MCP Protocol Specification](https://modelcontextprotocol.io/specification/2025-03-26)
- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/json-schema-core.html)
