"""
Tests for contract validation functionality.

Tests that JSON Schema contracts are properly validated for MCP operations.
"""

import json
import pytest
from pathlib import Path

from app.utils.contract_validator import (
    ContractValidator,
    ContractValidationError,
    validate_request,
    validate_response,
    validate_error,
)


class TestContractValidator:
    """Test suite for contract validation."""
    
    @pytest.fixture
    def contracts_dir(self):
        """Get the contracts directory path."""
        return Path(__file__).parent.parent.parent / "contracts"
    
    @pytest.fixture
    def validator(self, contracts_dir):
        """Create a contract validator instance."""
        return ContractValidator(contracts_dir)
    
    def test_load_valid_schema(self, validator):
        """Test loading a valid schema."""
        schema = validator._load_schema("shared/error.envelope.json")
        assert schema is not None
        assert "$schema" in schema
        assert schema["title"] == "error.envelope"
    
    def test_load_nonexistent_schema(self, validator):
        """Test loading a non-existent schema."""
        with pytest.raises(FileNotFoundError):
            validator._load_schema("nonexistent/schema.json")
    
    def test_validate_mcp_initialize_request(self, validator):
        """Test validating MCP initialize request."""
        valid_request = {
            "protocolVersion": "2025-03-26",
            "capabilities": {
                "resources": {"subscribe": True},
                "tools": {"listChanged": True},
                "prompts": {"listChanged": True},
                "sampling": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
        
        result = validator.validate_request("mcp.initialize", valid_request)
        assert result == valid_request
    
    def test_validate_mcp_initialize_request_invalid(self, validator):
        """Test validating invalid MCP initialize request."""
        invalid_request = {
            "protocolVersion": "2025-03-26",
            # Missing capabilities and clientInfo
        }
        
        with pytest.raises(ContractValidationError) as exc_info:
            validator.validate_request("mcp.initialize", invalid_request)
        
        assert "capabilities" in str(exc_info.value).lower()
    
    def test_validate_mcp_initialize_response(self, validator):
        """Test validating MCP initialize response."""
        valid_response = {
            "protocolVersion": "2025-03-26",
            "serverInfo": {
                "name": "Z2 AI Workforce Platform",
                "version": "1.0.0"
            },
            "capabilities": {
                "resources": {"subscribe": True},
                "tools": {"listChanged": True},
                "prompts": {"listChanged": True},
                "sampling": {}
            },
            "session_id": "550e8400-e29b-41d4-a716-446655440000"
        }
        
        result = validator.validate_response("mcp.initialize", valid_response)
        assert result == valid_response
    
    def test_validate_pinecone_upsert_request(self, validator):
        """Test validating Pinecone upsert request."""
        valid_request = {
            "namespace": "production",
            "vectors": [
                {
                    "id": "vec1",
                    "values": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
                    "metadata": {"source": "document-123"}
                }
            ],
            "batchSize": 100
        }
        
        result = validator.validate_request("pinecone.upsert", valid_request)
        assert result == valid_request
    
    def test_validate_pinecone_upsert_request_invalid_vectors(self, validator):
        """Test validating Pinecone upsert with insufficient vector dimensions."""
        invalid_request = {
            "namespace": "production",
            "vectors": [
                {
                    "id": "vec1",
                    "values": [0.1, 0.2]  # Too few dimensions (< 8)
                }
            ]
        }
        
        with pytest.raises(ContractValidationError) as exc_info:
            validator.validate_request("pinecone.upsert", invalid_request)
        
        assert "minitems" in str(exc_info.value).lower() or "values" in str(exc_info.value).lower()
    
    def test_validate_pinecone_upsert_response(self, validator):
        """Test validating Pinecone upsert response."""
        valid_response = {
            "upsertedCount": 2,
            "warnings": []
        }
        
        result = validator.validate_response("pinecone.upsert", valid_response)
        assert result == valid_response
    
    def test_validate_error_envelope(self, validator):
        """Test validating error envelope."""
        valid_error = {
            "error": {
                "code": "INVALID_INPUT",
                "message": "Required field 'namespace' is missing",
                "retriable": False,
                "details": {
                    "field": "namespace"
                }
            }
        }
        
        result = validator.validate_error(valid_error)
        assert result == valid_error
    
    def test_validate_error_envelope_invalid_code(self, validator):
        """Test validating error with invalid code."""
        invalid_error = {
            "error": {
                "code": "INVALID_CODE",  # Not in enum
                "message": "Some error"
            }
        }
        
        with pytest.raises(ContractValidationError) as exc_info:
            validator.validate_error(invalid_error)
        
        assert "code" in str(exc_info.value).lower()
    
    def test_validate_supabase_sql_request(self, validator):
        """Test validating Supabase SQL request."""
        valid_request = {
            "query": "SELECT * FROM users WHERE id = $1",
            "params": [123],
            "timeout": 30000,
            "readOnly": True
        }
        
        result = validator.validate_request("supabase.sql", valid_request)
        assert result == valid_request
    
    def test_validate_browserbase_navigate_request(self, validator):
        """Test validating Browserbase navigate request."""
        valid_request = {
            "url": "https://example.com",
            "waitUntil": "load",
            "timeout": 30000
        }
        
        result = validator.validate_request("browserbase.navigate", valid_request)
        assert result == valid_request
    
    def test_validate_github_search_request(self, validator):
        """Test validating GitHub search request."""
        valid_request = {
            "query": "is:issue is:open repo:owner/repo",
            "sort": "created",
            "order": "desc",
            "perPage": 30,
            "page": 1
        }
        
        result = validator.validate_request("github.searchIssues", valid_request)
        assert result == valid_request
    
    def test_global_validator_functions(self, contracts_dir):
        """Test global validator convenience functions."""
        # These should work without explicit validator instance
        request_data = {
            "namespace": "test",
            "vectors": [
                {
                    "id": "vec1",
                    "values": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
                }
            ]
        }
        
        result = validate_request("pinecone.upsert", request_data)
        assert result == request_data
        
        response_data = {
            "upsertedCount": 1,
            "warnings": []
        }
        
        result = validate_response("pinecone.upsert", response_data)
        assert result == response_data


class TestContractExamples:
    """Test that example fixtures validate against their schemas."""
    
    @pytest.fixture
    def contracts_dir(self):
        """Get the contracts directory path."""
        return Path(__file__).parent.parent.parent / "contracts"
    
    @pytest.fixture
    def examples_dir(self, contracts_dir):
        """Get the examples directory path."""
        return contracts_dir / "examples"
    
    @pytest.fixture
    def validator(self, contracts_dir):
        """Create a contract validator instance."""
        return ContractValidator(contracts_dir)
    
    def test_mcp_initialize_example(self, validator, examples_dir):
        """Test that MCP initialize example validates."""
        example_file = examples_dir / "mcp.initialize.example.json"
        if not example_file.exists():
            pytest.skip("Example file not found")
        
        with open(example_file) as f:
            example = json.load(f)
        
        # Validate request
        validator.validate_request("mcp.initialize", example["request"])
        
        # Validate response
        validator.validate_response("mcp.initialize", example["response"])
    
    def test_pinecone_upsert_example(self, validator, examples_dir):
        """Test that Pinecone upsert example validates."""
        example_file = examples_dir / "pinecone.upsert.example.json"
        if not example_file.exists():
            pytest.skip("Example file not found")
        
        with open(example_file) as f:
            example = json.load(f)
        
        # Validate request
        validator.validate_request("pinecone.upsert", example["request"])
        
        # Validate response
        validator.validate_response("pinecone.upsert", example["response"])
    
    def test_error_examples(self, validator, examples_dir):
        """Test that error examples validate."""
        example_file = examples_dir / "error.example.json"
        if not example_file.exists():
            pytest.skip("Example file not found")
        
        with open(example_file) as f:
            examples = json.load(f)
        
        # Validate all error examples
        for example in examples["examples"]:
            validator.validate_error(example["payload"])
