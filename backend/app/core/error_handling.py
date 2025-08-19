"""
Enhanced Error Handling System for Z2

Provides comprehensive error handling, error chaining, logging, and
user-friendly error responses while maintaining security.
"""

import traceback
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import structlog
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


class ErrorCategory(str, Enum):
    """Categories of errors for better classification and handling."""
    
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    DATABASE = "database"
    CONFIGURATION = "configuration"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class ErrorSeverity(str, Enum):
    """Error severity levels for logging and alerting."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Z2Error(Exception):
    """Base exception class for Z2 application errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = None,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Dict[str, Any] = None,
        user_message: str = None,
        suggestions: List[str] = None,
        cause: Exception = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.user_message = user_message or message
        self.suggestions = suggestions or []
        self.cause = cause
        self.timestamp = datetime.now(UTC)
        self.trace_id = None  # Will be set by middleware


class AuthenticationError(Z2Error):
    """Authentication-related errors."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        kwargs.setdefault("category", ErrorCategory.AUTHENTICATION)
        kwargs.setdefault("error_code", "AUTH_FAILED")
        kwargs.setdefault("user_message", "Authentication is required to access this resource")
        super().__init__(message, **kwargs)


class AuthorizationError(Z2Error):
    """Authorization-related errors."""
    
    def __init__(self, message: str = "Access denied", **kwargs):
        kwargs.setdefault("category", ErrorCategory.AUTHORIZATION)
        kwargs.setdefault("error_code", "ACCESS_DENIED")
        kwargs.setdefault("user_message", "You don't have permission to access this resource")
        super().__init__(message, **kwargs)


class ValidationError(Z2Error):
    """Data validation errors."""
    
    def __init__(self, message: str = "Validation failed", **kwargs):
        kwargs.setdefault("category", ErrorCategory.VALIDATION)
        kwargs.setdefault("error_code", "VALIDATION_FAILED")
        kwargs.setdefault("severity", ErrorSeverity.LOW)
        super().__init__(message, **kwargs)


class BusinessLogicError(Z2Error):
    """Business logic and domain-specific errors."""
    
    def __init__(self, message: str = "Business logic error", **kwargs):
        kwargs.setdefault("category", ErrorCategory.BUSINESS_LOGIC)
        kwargs.setdefault("error_code", "BUSINESS_LOGIC_ERROR")
        super().__init__(message, **kwargs)


class ExternalServiceError(Z2Error):
    """Errors from external services (OpenAI, Anthropic, etc.)."""
    
    def __init__(self, message: str = "External service error", **kwargs):
        kwargs.setdefault("category", ErrorCategory.EXTERNAL_SERVICE)
        kwargs.setdefault("error_code", "EXTERNAL_SERVICE_ERROR")
        kwargs.setdefault("severity", ErrorSeverity.HIGH)
        super().__init__(message, **kwargs)


class DatabaseError(Z2Error):
    """Database-related errors."""
    
    def __init__(self, message: str = "Database error", **kwargs):
        kwargs.setdefault("category", ErrorCategory.DATABASE)
        kwargs.setdefault("error_code", "DATABASE_ERROR")
        kwargs.setdefault("severity", ErrorSeverity.HIGH)
        kwargs.setdefault("user_message", "A database error occurred. Please try again later.")
        super().__init__(message, **kwargs)


class ConfigurationError(Z2Error):
    """Configuration and setup errors."""
    
    def __init__(self, message: str = "Configuration error", **kwargs):
        kwargs.setdefault("category", ErrorCategory.CONFIGURATION)
        kwargs.setdefault("error_code", "CONFIG_ERROR")
        kwargs.setdefault("severity", ErrorSeverity.CRITICAL)
        super().__init__(message, **kwargs)


class SystemError(Z2Error):
    """System-level errors."""
    
    def __init__(self, message: str = "System error", **kwargs):
        kwargs.setdefault("category", ErrorCategory.SYSTEM)
        kwargs.setdefault("error_code", "SYSTEM_ERROR")
        kwargs.setdefault("severity", ErrorSeverity.CRITICAL)
        kwargs.setdefault("user_message", "A system error occurred. Please try again later.")
        super().__init__(message, **kwargs)


class ErrorResponse(BaseModel):
    """Standardized error response model."""
    
    error: bool = True
    error_code: str
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    timestamp: datetime
    trace_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorHandler:
    """Centralized error handling and logging system."""
    
    def __init__(self):
        self.error_counters: Dict[str, int] = {}
    
    def handle_error(
        self,
        error: Exception,
        request: Request = None,
        include_traceback: bool = False
    ) -> JSONResponse:
        """Handle an error and return appropriate JSON response."""
        
        # Generate trace ID for error tracking
        trace_id = self._generate_trace_id()
        
        if isinstance(error, Z2Error):
            return self._handle_z2_error(error, trace_id, include_traceback)
        elif isinstance(error, HTTPException):
            return self._handle_http_exception(error, trace_id)
        else:
            return self._handle_generic_error(error, trace_id, include_traceback)
    
    def _handle_z2_error(self, error: Z2Error, trace_id: str, include_traceback: bool) -> JSONResponse:
        """Handle Z2-specific errors."""
        error.trace_id = trace_id
        
        # Log the error with appropriate level
        log_data = {
            "error_code": error.error_code,
            "category": error.category,
            "severity": error.severity,
            "trace_id": trace_id,
            "details": error.details
        }
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(error.message, **log_data)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(error.message, **log_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(error.message, **log_data)
        else:
            logger.info(error.message, **log_data)
        
        # Determine HTTP status code based on category
        status_code = self._get_status_code_for_category(error.category)
        
        # Create error response
        response_data = ErrorResponse(
            error_code=error.error_code,
            message=error.user_message,
            category=error.category,
            severity=error.severity,
            timestamp=error.timestamp,
            trace_id=trace_id,
            details=error.details if include_traceback else None,
            suggestions=error.suggestions
        )
        
        return JSONResponse(
            status_code=status_code,
            content=response_data.dict()
        )
    
    def _handle_http_exception(self, error: HTTPException, trace_id: str) -> JSONResponse:
        """Handle FastAPI HTTP exceptions."""
        logger.warning(
            "HTTP exception occurred",
            status_code=error.status_code,
            detail=error.detail,
            trace_id=trace_id
        )
        
        # Convert to Z2Error format for consistency
        response_data = ErrorResponse(
            error_code="HTTP_EXCEPTION",
            message=str(error.detail),
            category=self._categorize_http_error(error.status_code),
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now(UTC),
            trace_id=trace_id
        )
        
        return JSONResponse(
            status_code=error.status_code,
            content=response_data.dict()
        )
    
    def _handle_generic_error(self, error: Exception, trace_id: str, include_traceback: bool) -> JSONResponse:
        """Handle generic Python exceptions."""
        logger.error(
            "Unhandled exception occurred",
            error_type=type(error).__name__,
            error_message=str(error),
            trace_id=trace_id,
            traceback=traceback.format_exc() if include_traceback else None
        )
        
        response_data = ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="An internal error occurred. Please try again later.",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            timestamp=datetime.now(UTC),
            trace_id=trace_id,
            details={"traceback": traceback.format_exc()} if include_traceback else None
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_data.dict()
        )
    
    def _get_status_code_for_category(self, category: ErrorCategory) -> int:
        """Map error categories to appropriate HTTP status codes."""
        mapping = {
            ErrorCategory.AUTHENTICATION: status.HTTP_401_UNAUTHORIZED,
            ErrorCategory.AUTHORIZATION: status.HTTP_403_FORBIDDEN,
            ErrorCategory.VALIDATION: status.HTTP_422_UNPROCESSABLE_ENTITY,
            ErrorCategory.BUSINESS_LOGIC: status.HTTP_409_CONFLICT,
            ErrorCategory.EXTERNAL_SERVICE: status.HTTP_502_BAD_GATEWAY,
            ErrorCategory.DATABASE: status.HTTP_500_INTERNAL_SERVER_ERROR,
            ErrorCategory.CONFIGURATION: status.HTTP_500_INTERNAL_SERVER_ERROR,
            ErrorCategory.SYSTEM: status.HTTP_500_INTERNAL_SERVER_ERROR,
            ErrorCategory.UNKNOWN: status.HTTP_500_INTERNAL_SERVER_ERROR
        }
        return mapping.get(category, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _categorize_http_error(self, status_code: int) -> ErrorCategory:
        """Categorize HTTP errors by status code."""
        if status_code == 401:
            return ErrorCategory.AUTHENTICATION
        elif status_code == 403:
            return ErrorCategory.AUTHORIZATION
        elif 400 <= status_code < 500:
            return ErrorCategory.VALIDATION
        else:
            return ErrorCategory.SYSTEM
    
    def _generate_trace_id(self) -> str:
        """Generate a unique trace ID for error tracking."""
        import uuid
        return str(uuid.uuid4())[:8]


# Global error handler instance
error_handler = ErrorHandler()


def handle_errors_with_context(include_traceback: bool = False):
    """Decorator to handle errors with proper context and logging."""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Try to find request in args/kwargs for context
                request = None
                for arg in list(args) + list(kwargs.values()):
                    if isinstance(arg, Request):
                        request = arg
                        break
                
                # Handle the error and return appropriate response
                return error_handler.handle_error(e, request, include_traceback)
        
        return wrapper
    return decorator


def chain_error(new_error: Z2Error, cause: Exception) -> Z2Error:
    """Chain errors to preserve the original cause while adding context."""
    new_error.cause = cause
    
    # Add cause information to details
    if "cause" not in new_error.details:
        new_error.details["cause"] = {
            "type": type(cause).__name__,
            "message": str(cause)
        }
    
    return new_error


def create_validation_error(field_errors: List[Dict[str, Any]]) -> ValidationError:
    """Create a validation error with detailed field information."""
    return ValidationError(
        message="Validation failed for one or more fields",
        details={"field_errors": field_errors},
        suggestions=["Check the field requirements and try again"]
    )


def create_external_service_error(service_name: str, original_error: Exception) -> ExternalServiceError:
    """Create an external service error with proper context."""
    return chain_error(
        ExternalServiceError(
            message=f"Error communicating with {service_name}",
            details={"service": service_name},
            suggestions=[
                "Check your API keys and configuration",
                "Verify the service is available",
                "Try again in a few moments"
            ]
        ),
        original_error
    )