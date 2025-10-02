# MCP Server Contracts

This directory contains JSON Schema contracts for all MCP (Model Context Protocol) server operations. These contracts serve as the source of truth for API interfaces, enabling:

- **Predictable Interoperability**: Agents and tools know exactly what to expect
- **Early Validation**: Catch errors at the boundary, not after failures
- **Self-Documentation**: Discover capabilities without diving into code
- **Safe Refactoring**: Schema diffs reveal breaking changes during upgrades

## Directory Structure

```
contracts/
├── shared/              # Reusable schemas across all servers
│   └── error.envelope.json
├── mcp/                 # Core MCP protocol schemas
│   ├── initialize.request.json
│   ├── initialize.response.json
│   ├── tool.definition.json
│   └── resource.definition.json
├── pinecone/           # Pinecone vector operations
│   ├── upsert.request.json
│   ├── upsert.response.json
│   ├── query.request.json
│   └── query.response.json
├── supabase/           # Supabase database operations
│   ├── sql.request.json
│   └── sql.response.json
├── browserbase/        # Browser automation operations
│   ├── navigate.request.json
│   └── navigate.response.json
├── github/             # GitHub API operations
│   ├── searchIssues.request.json
│   └── searchIssues.response.json
└── examples/           # Golden fixtures for testing
    ├── mcp.initialize.example.json
    ├── pinecone.upsert.example.json
    └── error.example.json
```

## Schema Contract Components

Each contract defines:

1. **Operations**: The specific action (e.g., `upsert`, `query`, `navigate`)
2. **Input Parameters**: Names, types, required/optional fields, enums, defaults
3. **Output Shape**: Success response structure, types, nullable rules
4. **Error Codes**: Standardized error types (see `shared/error.envelope.json`)
5. **Metadata**: Version, description, examples

## Error Handling

All operations use the standardized error envelope from `shared/error.envelope.json`:

```json
{
  "error": {
    "code": "INVALID_INPUT" | "AUTH_REQUIRED" | "NOT_FOUND" | "RATE_LIMIT" | "UPSTREAM_ERROR" | "UNAVAILABLE" | "INTERNAL_ERROR",
    "message": "Human-readable error message",
    "retriable": false,
    "details": { /* additional context */ }
  }
}
```

## Usage

### Python (Backend)

Use the contract validator utility in `backend/app/utils/contract_validator.py`:

```python
from app.utils.contract_validator import validate_request, validate_response

# Validate incoming request
validated_data = validate_request("pinecone.upsert", request_data)

# Perform operation
result = await pinecone_client.upsert(validated_data)

# Validate outgoing response
validated_result = validate_response("pinecone.upsert", result)
```

### TypeScript (Frontend)

Use the contract validator in `frontend/src/utils/contractValidator.ts`:

```typescript
import { validateRequest, validateResponse } from '@/utils/contractValidator';

// Validate before sending
const validRequest = validateRequest('pinecone.upsert', requestData);

// Validate after receiving
const validResponse = validateResponse('pinecone.upsert', responseData);
```

## Adding New Contracts

1. Create request and response schemas in the appropriate directory
2. Add examples to `contracts/examples/`
3. Update this README
4. Run validation tests: `npm run test:contracts` or `pytest tests/test_contracts.py`

## Validation

### JSON Schema Validation

All schemas use JSON Schema Draft 2020-12 and can be validated using:

```bash
# Python
python backend/scripts/validate_contracts.py

# Node.js
npm run validate:schemas
```

### CI/CD Integration

Contract validation runs automatically in CI:
- Schema syntax validation
- Example fixture validation
- Breaking change detection

## Versioning

Contracts follow semantic versioning:
- **Major**: Breaking changes to required fields or types
- **Minor**: New optional fields or non-breaking additions
- **Patch**: Documentation or example updates

Version history is tracked in `CHANGELOG.md` at the root of each server directory.

## References

- [JSON Schema Specification](https://json-schema.org/draft/2020-12/json-schema-core.html)
- [MCP Protocol Specification](https://modelcontextprotocol.io/specification/2025-03-26)
- [API Documentation](../docs/api/)

## Contributing

When modifying contracts:
1. Ensure backward compatibility when possible
2. Update examples and tests
3. Document breaking changes in PR description
4. Run full test suite before committing
