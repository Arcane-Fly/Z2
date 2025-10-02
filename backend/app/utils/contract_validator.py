"""
Contract validator for MCP server operations.

This module provides runtime validation for MCP server requests and responses
using JSON Schema contracts defined in the contracts/ directory.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache

from jsonschema import Draft202012Validator, ValidationError
from jsonschema.validators import validator_for


class ContractValidationError(Exception):
    """Raised when contract validation fails."""
    
    def __init__(self, message: str, errors: list[str], contract_type: str):
        self.message = message
        self.errors = errors
        self.contract_type = contract_type
        super().__init__(self.format_error_message())
    
    def format_error_message(self) -> str:
        """Format validation errors into a readable message."""
        error_list = "\n  - ".join(self.errors)
        return f"{self.message} ({self.contract_type}):\n  - {error_list}"


class ContractValidator:
    """Validates data against JSON Schema contracts."""
    
    def __init__(self, contracts_dir: Optional[Path] = None):
        """Initialize the contract validator.
        
        Args:
            contracts_dir: Path to contracts directory. Defaults to repository root.
        """
        if contracts_dir is None:
            # Default to contracts/ directory at repository root
            current_file = Path(__file__).resolve()
            repo_root = current_file.parent.parent.parent.parent
            contracts_dir = repo_root / "contracts"
        
        self.contracts_dir = contracts_dir
        self._schema_cache: Dict[str, Dict[str, Any]] = {}
    
    @lru_cache(maxsize=128)
    def _load_schema(self, schema_path: str) -> Dict[str, Any]:
        """Load and cache a JSON schema.
        
        Args:
            schema_path: Relative path to schema file from contracts directory
            
        Returns:
            Loaded JSON schema
            
        Raises:
            FileNotFoundError: If schema file doesn't exist
            ValueError: If schema file is invalid JSON
        """
        full_path = self.contracts_dir / schema_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Contract schema not found: {schema_path}")
        
        try:
            with open(full_path, 'r') as f:
                schema = json.load(f)
            
            # Validate that the schema itself is valid
            validator_class = validator_for(schema)
            validator_class.check_schema(schema)
            
            return schema
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema {schema_path}: {e}")
    
    def validate(
        self,
        data: Any,
        schema_path: str,
        error_prefix: str = "Validation failed"
    ) -> Any:
        """Validate data against a schema contract.
        
        Args:
            data: Data to validate
            schema_path: Relative path to schema file
            error_prefix: Prefix for error messages
            
        Returns:
            Validated data (same as input if valid)
            
        Raises:
            ContractValidationError: If validation fails
        """
        try:
            schema = self._load_schema(schema_path)
            validator = Draft202012Validator(schema)
            
            errors = list(validator.iter_errors(data))
            
            if errors:
                error_messages = [
                    f"{'.'.join(str(p) for p in error.path)}: {error.message}"
                    for error in errors
                ]
                raise ContractValidationError(
                    error_prefix,
                    error_messages,
                    schema_path
                )
            
            return data
            
        except FileNotFoundError as e:
            # Schema not found - log warning but don't fail
            # This allows gradual adoption of contracts
            import logging
            logging.warning(f"Contract schema not found, skipping validation: {e}")
            return data
    
    def validate_request(self, operation: str, data: Any) -> Any:
        """Validate a request payload.
        
        Args:
            operation: Operation name (e.g., "pinecone.upsert")
            data: Request data to validate
            
        Returns:
            Validated request data
        """
        schema_path = self._get_schema_path(operation, "request")
        return self.validate(
            data,
            schema_path,
            f"Invalid request for {operation}"
        )
    
    def validate_response(self, operation: str, data: Any) -> Any:
        """Validate a response payload.
        
        Args:
            operation: Operation name (e.g., "pinecone.upsert")
            data: Response data to validate
            
        Returns:
            Validated response data
        """
        schema_path = self._get_schema_path(operation, "response")
        return self.validate(
            data,
            schema_path,
            f"Invalid response from {operation}"
        )
    
    def validate_error(self, data: Any) -> Any:
        """Validate an error envelope.
        
        Args:
            data: Error data to validate
            
        Returns:
            Validated error data
        """
        return self.validate(
            data,
            "shared/error.envelope.json",
            "Invalid error envelope"
        )
    
    def _get_schema_path(self, operation: str, message_type: str) -> str:
        """Convert operation name to schema path.
        
        Args:
            operation: Operation name (e.g., "pinecone.upsert" or "mcp.initialize")
            message_type: Either "request" or "response"
            
        Returns:
            Relative path to schema file
        """
        parts = operation.split(".")
        if len(parts) != 2:
            raise ValueError(
                f"Invalid operation name: {operation}. "
                "Expected format: 'server.operation'"
            )
        
        server, op = parts
        return f"{server}/{op}.{message_type}.json"


# Global validator instance
_default_validator: Optional[ContractValidator] = None


def get_validator() -> ContractValidator:
    """Get the default contract validator instance."""
    global _default_validator
    if _default_validator is None:
        _default_validator = ContractValidator()
    return _default_validator


def validate_request(operation: str, data: Any) -> Any:
    """Validate a request payload using the default validator.
    
    Args:
        operation: Operation name (e.g., "pinecone.upsert")
        data: Request data to validate
        
    Returns:
        Validated request data
    """
    return get_validator().validate_request(operation, data)


def validate_response(operation: str, data: Any) -> Any:
    """Validate a response payload using the default validator.
    
    Args:
        operation: Operation name (e.g., "pinecone.upsert")
        data: Response data to validate
        
    Returns:
        Validated response data
    """
    return get_validator().validate_response(operation, data)


def validate_error(data: Any) -> Any:
    """Validate an error envelope using the default validator.
    
    Args:
        data: Error data to validate
        
    Returns:
        Validated error data
    """
    return get_validator().validate_error(data)
