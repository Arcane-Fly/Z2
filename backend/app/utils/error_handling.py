"""
Shared Error Handling Utilities for Z2 Backend - DRY Principle Implementation

This module provides reusable error handling patterns and utilities
to eliminate repetition across API endpoints.
"""

from typing import Any, Dict, Optional, Type, Union
from fastapi import HTTPException, status
import structlog

logger = structlog.get_logger(__name__)


class ErrorMessages:
    """Centralized error messages for consistency"""
    
    # Generic errors
    INTERNAL_ERROR = "An internal error occurred"
    INVALID_REQUEST = "Invalid request"
    UNAUTHORIZED = "Authentication required"
    FORBIDDEN = "Access denied"
    NOT_FOUND = "Resource not found"
    CONFLICT = "Resource already exists"
    VALIDATION_ERROR = "Validation failed"
    
    # Entity-specific errors
    USER_NOT_FOUND = "User not found"
    USER_EXISTS = "User already exists"
    INVALID_CREDENTIALS = "Invalid username or password"
    
    MODEL_NOT_FOUND = "Model '{model_id}' not found"
    INVALID_MODEL = "Invalid model configuration"
    MODEL_UNAVAILABLE = "Model temporarily unavailable"
    
    AGENT_NOT_FOUND = "Agent not found"
    AGENT_CREATION_FAILED = "Failed to create agent"
    
    WORKFLOW_NOT_FOUND = "Workflow not found"
    WORKFLOW_EXECUTION_FAILED = "Workflow execution failed"
    
    # Provider-specific errors
    PROVIDER_ERROR = "Provider error: {error}"
    PROVIDER_UNAVAILABLE = "Provider '{provider}' is not available"
    INVALID_PROVIDER = "Invalid provider: {provider}"
    API_KEY_MISSING = "API key not configured for provider '{provider}'"
    
    # Permission errors
    INSUFFICIENT_PERMISSIONS = "Insufficient permissions"
    RESOURCE_ACCESS_DENIED = "Access to this resource is denied"


class Z2HTTPException(HTTPException):
    """Enhanced HTTP Exception with structured error details"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        log_error: bool = True
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra_data = extra_data or {}
        
        if log_error:
            logger.error(
                "HTTP Exception raised",
                status_code=status_code,
                detail=detail,
                error_code=error_code,
                extra_data=extra_data
            )


def create_error_response(
    status_code: int,
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Z2HTTPException:
    """Create a standardized error response"""
    return Z2HTTPException(
        status_code=status_code,
        detail=message,
        error_code=error_code,
        extra_data=details
    )


# Common error response factories
def not_found_error(
    resource: str = "Resource",
    resource_id: Optional[str] = None
) -> Z2HTTPException:
    """Create a 404 Not Found error"""
    message = f"{resource} not found"
    if resource_id:
        message = f"{resource} '{resource_id}' not found"
    
    return create_error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        message=message,
        error_code="RESOURCE_NOT_FOUND",
        details={"resource": resource, "resource_id": resource_id}
    )


def validation_error(
    message: str = ErrorMessages.VALIDATION_ERROR,
    field: Optional[str] = None,
    value: Optional[Any] = None
) -> Z2HTTPException:
    """Create a 400 Validation Error"""
    details = {}
    if field:
        details["field"] = field
    if value is not None:
        details["value"] = str(value)
    
    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=message,
        error_code="VALIDATION_ERROR",
        details=details
    )


def unauthorized_error(
    message: str = ErrorMessages.UNAUTHORIZED
) -> Z2HTTPException:
    """Create a 401 Unauthorized error"""
    return create_error_response(
        status_code=status.HTTP_401_UNAUTHORIZED,
        message=message,
        error_code="UNAUTHORIZED"
    )


def forbidden_error(
    message: str = ErrorMessages.FORBIDDEN
) -> Z2HTTPException:
    """Create a 403 Forbidden error"""
    return create_error_response(
        status_code=status.HTTP_403_FORBIDDEN,
        message=message,
        error_code="FORBIDDEN"
    )


def conflict_error(
    resource: str = "Resource",
    message: Optional[str] = None
) -> Z2HTTPException:
    """Create a 409 Conflict error"""
    if not message:
        message = f"{resource} already exists"
    
    return create_error_response(
        status_code=status.HTTP_409_CONFLICT,
        message=message,
        error_code="RESOURCE_CONFLICT",
        details={"resource": resource}
    )


def internal_error(
    message: str = ErrorMessages.INTERNAL_ERROR,
    exception: Optional[Exception] = None
) -> Z2HTTPException:
    """Create a 500 Internal Server Error"""
    details = {}
    if exception:
        details["exception_type"] = type(exception).__name__
        details["exception_message"] = str(exception)
    
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message=message,
        error_code="INTERNAL_ERROR",
        details=details
    )


def provider_error(
    provider: str,
    error_message: str,
    status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE
) -> Z2HTTPException:
    """Create a provider-specific error"""
    return create_error_response(
        status_code=status_code,
        message=ErrorMessages.PROVIDER_ERROR.format(error=error_message),
        error_code="PROVIDER_ERROR",
        details={"provider": provider, "original_error": error_message}
    )


def model_not_found_error(model_id: str) -> Z2HTTPException:
    """Create a model not found error"""
    return create_error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        message=ErrorMessages.MODEL_NOT_FOUND.format(model_id=model_id),
        error_code="MODEL_NOT_FOUND",
        details={"model_id": model_id}
    )


def invalid_capability_error(capability: str) -> Z2HTTPException:
    """Create an invalid capability error"""
    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=f"Invalid capability: {capability}",
        error_code="INVALID_CAPABILITY",
        details={"capability": capability}
    )


# Decorator for exception handling
def handle_exceptions(
    default_message: str = ErrorMessages.INTERNAL_ERROR,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
):
    """Decorator to handle exceptions in endpoint functions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Z2HTTPException:
                # Re-raise our custom exceptions
                raise
            except HTTPException:
                # Re-raise FastAPI exceptions
                raise
            except Exception as e:
                logger.error(
                    "Unhandled exception in endpoint",
                    function=func.__name__,
                    exception=str(e),
                    exception_type=type(e).__name__
                )
                raise internal_error(default_message, e)
        return wrapper
    return decorator


# Context manager for error handling
class ErrorContext:
    """Context manager for structured error handling"""
    
    def __init__(
        self,
        operation: str,
        default_error: str = ErrorMessages.INTERNAL_ERROR,
        reraise_http_errors: bool = True
    ):
        self.operation = operation
        self.default_error = default_error
        self.reraise_http_errors = reraise_http_errors
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return True
        
        if isinstance(exc_val, (Z2HTTPException, HTTPException)) and self.reraise_http_errors:
            return False  # Re-raise HTTP exceptions
        
        if exc_type:
            logger.error(
                f"Error in {self.operation}",
                exception=str(exc_val),
                exception_type=exc_type.__name__
            )
            raise internal_error(self.default_error, exc_val)
        
        return True


# Utility functions for common validation patterns
def require_not_none(value: Any, field_name: str) -> Any:
    """Require a value to not be None"""
    if value is None:
        raise validation_error(f"{field_name} is required", field=field_name)
    return value


def require_not_empty(value: str, field_name: str) -> str:
    """Require a string value to not be empty"""
    if not value or not value.strip():
        raise validation_error(f"{field_name} cannot be empty", field=field_name)
    return value.strip()


def validate_in_choices(value: Any, choices: list, field_name: str) -> Any:
    """Validate that a value is in a list of choices"""
    if value not in choices:
        raise validation_error(
            f"{field_name} must be one of: {', '.join(map(str, choices))}",
            field=field_name,
            value=value
        )
    return value