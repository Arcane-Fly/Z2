# Pinecone Vector Operations

This directory contains JSON Schema contracts for Pinecone vector database operations.

## pinecone.upsert (v1)

**Purpose:** Insert or update vectors in a Pinecone namespace.

### Request

Validates against: `contracts/pinecone/upsert.request.json`

- `namespace` (string, required): Namespace for vector storage
- `vectors` (array, required): Array of vectors to upsert (minimum 1)
  - `id` (string, required): Unique vector identifier
  - `values` (array of numbers, required): Vector embedding values (minimum 8 dimensions)
  - `metadata` (object, optional): Optional metadata for the vector
- `batchSize` (integer, optional): Batch size for upsert operations (1-1000, default: 100)

**Example:**
```json
{
  "namespace": "production",
  "vectors": [
    {
      "id": "vec1",
      "values": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
      "metadata": {
        "source": "document-123",
        "timestamp": "2025-01-15T10:30:00Z"
      }
    }
  ],
  "batchSize": 100
}
```

### Response

Validates against: `contracts/pinecone/upsert.response.json`

- `upsertedCount` (integer, required): Number of vectors successfully upserted
- `warnings` (array of strings, optional): Non-critical warnings from the operation

**Example:**
```json
{
  "upsertedCount": 2,
  "warnings": []
}
```

### Errors

Uses standard `error.envelope.json` with codes:
- `INVALID_INPUT`: Invalid vector format or missing required fields
- `AUTH_REQUIRED`: Pinecone API key not provided or invalid
- `RATE_LIMIT`: Pinecone rate limit exceeded
- `UPSTREAM_ERROR`: Pinecone service error
- `INTERNAL_ERROR`: Unexpected error during processing

## pinecone.query (v1)

**Purpose:** Query similar vectors from Pinecone.

### Request

Validates against: `contracts/pinecone/query.request.json`

- `vector` (array of numbers, required): Query vector (minimum 8 dimensions)
- `namespace` (string, optional): Namespace to query
- `topK` (integer, optional): Number of results to return (1-10000, default: 10)
- `filter` (object, optional): Metadata filter
- `includeMetadata` (boolean, optional): Include metadata in results (default: true)
- `includeValues` (boolean, optional): Include vector values in results (default: false)

**Example:**
```json
{
  "namespace": "production",
  "vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
  "topK": 5,
  "filter": {
    "source": "document-123"
  },
  "includeMetadata": true,
  "includeValues": false
}
```

### Response

Validates against: `contracts/pinecone/query.response.json`

- `matches` (array, required): Query results
  - `id` (string, required): Vector identifier
  - `score` (number, required): Similarity score (0-1)
  - `values` (array of numbers, optional): Vector values (if requested)
  - `metadata` (object, optional): Vector metadata (if requested)
- `namespace` (string, optional): Namespace queried

**Example:**
```json
{
  "matches": [
    {
      "id": "vec1",
      "score": 0.95,
      "metadata": {
        "source": "document-123"
      }
    }
  ],
  "namespace": "production"
}
```

### Errors

Uses standard `error.envelope.json` with codes:
- `INVALID_INPUT`: Invalid query format or vector dimensions
- `AUTH_REQUIRED`: Pinecone API key not provided or invalid
- `NOT_FOUND`: Namespace does not exist
- `RATE_LIMIT`: Pinecone rate limit exceeded
- `UPSTREAM_ERROR`: Pinecone service error

## Usage Example

```python
from app.utils.contract_validator import validate_request, validate_response

# Upsert vectors
upsert_request = {
    "namespace": "production",
    "vectors": [
        {
            "id": "vec1",
            "values": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
            "metadata": {"source": "doc-123"}
        }
    ]
}

# Validate before sending to Pinecone
validate_request("pinecone.upsert", upsert_request)

# Call Pinecone SDK
result = await pinecone_client.upsert(**upsert_request)

# Validate response
validate_response("pinecone.upsert", result)
```

## Version History

- **v1.0.0** (2025-01-15): Initial schema definitions
  - Upsert operation with batch support
  - Query operation with filtering

## References

- [Pinecone API Documentation](https://docs.pinecone.io/reference/api)
- [Vector Database Best Practices](https://www.pinecone.io/learn/vector-database/)
