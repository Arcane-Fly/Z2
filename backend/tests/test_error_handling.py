"""
Tests for error handling system.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from app.core.error_handling import (
    ErrorCategory,
    ErrorSeverity,
    Z2Error,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    BusinessLogicError,
    ExternalServiceError,
    DatabaseError,
    ConfigurationError,
    SystemError,
    ErrorResponse,
    ErrorHandler,
    handle_errors_with_context,
    chain_error,
    create_validation_error,
    create_external_service_error
)


class TestErrorEnums:
    """Test error enumeration classes."""

    def test_error_category_values(self):
        """Test ErrorCategory enum values."""
        assert ErrorCategory.AUTHENTICATION == "authentication"
        assert ErrorCategory.AUTHORIZATION == "authorization"
        assert ErrorCategory.VALIDATION == "validation"
        assert ErrorCategory.BUSINESS_LOGIC == "business_logic"
        assert ErrorCategory.EXTERNAL_SERVICE == "external_service"
        assert ErrorCategory.DATABASE == "database"
        assert ErrorCategory.CONFIGURATION == "configuration"
        assert ErrorCategory.SYSTEM == "system"
        assert ErrorCategory.UNKNOWN == "unknown"

    def test_error_severity_values(self):
        """Test ErrorSeverity enum values."""
        assert ErrorSeverity.LOW == "low"
        assert ErrorSeverity.MEDIUM == "medium"
        assert ErrorSeverity.HIGH == "high"
        assert ErrorSeverity.CRITICAL == "critical"


class TestZ2Error:
    """Test base Z2Error class."""

    def test_z2_error_basic(self):
        """Test basic Z2Error creation."""
        error = Z2Error("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code == "Z2Error"
        assert error.category == ErrorCategory.UNKNOWN
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.details == {}
        assert error.user_message == "Test error message"
        assert error.suggestions == []
        assert error.cause is None
        assert isinstance(error.timestamp, datetime)

    def test_z2_error_with_all_params(self):
        """Test Z2Error with all parameters."""
        details = {"field": "value"}
        suggestions = ["Try this", "Or this"]
        cause = ValueError("Original error")
        
        error = Z2Error(
            message="Detailed error",
            error_code="CUSTOM_ERROR",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.HIGH,
            details=details,
            user_message="User-friendly message",
            suggestions=suggestions,
            cause=cause
        )
        
        assert error.message == "Detailed error"
        assert error.error_code == "CUSTOM_ERROR"
        assert error.category == ErrorCategory.VALIDATION
        assert error.severity == ErrorSeverity.HIGH
        assert error.details == details
        assert error.user_message == "User-friendly message"
        assert error.suggestions == suggestions
        assert error.cause == cause


class TestSpecificErrors:
    """Test specific error subclasses."""

    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError()
        assert error.category == ErrorCategory.AUTHENTICATION
        assert error.error_code == "AUTH_FAILED"
        assert "Authentication is required" in error.user_message

    def test_authentication_error_custom(self):
        """Test AuthenticationError with custom message."""
        error = AuthenticationError("Invalid token")
        assert error.message == "Invalid token"
        assert error.category == ErrorCategory.AUTHENTICATION

    def test_authorization_error(self):
        """Test AuthorizationError."""
        error = AuthorizationError()
        assert error.category == ErrorCategory.AUTHORIZATION
        assert error.error_code == "ACCESS_DENIED"
        assert "permission" in error.user_message.lower()

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError()
        assert error.category == ErrorCategory.VALIDATION
        assert error.error_code == "VALIDATION_FAILED"
        assert error.severity == ErrorSeverity.LOW

    def test_business_logic_error(self):
        """Test BusinessLogicError."""
        error = BusinessLogicError("Invalid business rule")
        assert error.category == ErrorCategory.BUSINESS_LOGIC
        assert error.error_code == "BUSINESS_LOGIC_ERROR"
        assert error.message == "Invalid business rule"

    def test_external_service_error(self):
        """Test ExternalServiceError."""
        error = ExternalServiceError()
        assert error.category == ErrorCategory.EXTERNAL_SERVICE
        assert error.error_code == "EXTERNAL_SERVICE_ERROR"
        assert error.severity == ErrorSeverity.HIGH

    def test_database_error(self):
        """Test DatabaseError."""
        error = DatabaseError("Connection failed")
        assert error.category == ErrorCategory.DATABASE
        assert error.message == "Connection failed"

    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("Missing config")
        assert error.category == ErrorCategory.CONFIGURATION
        assert error.message == "Missing config"

    def test_system_error(self):
        """Test SystemError."""
        error = SystemError("System failure")
        assert error.category == ErrorCategory.SYSTEM
        assert error.severity == ErrorSeverity.CRITICAL
        assert error.message == "System failure"


class TestErrorResponse:
    """Test ErrorResponse model."""

    def test_error_response_initialization(self):
        """Test ErrorResponse model initialization."""
        response = ErrorResponse(
            error_code="TEST_ERROR",
            message="Test message",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            details={"field": "value"},
            suggestions=["Try again"],
            user_message="User message",
            timestamp=datetime.now(),
            trace_id="trace-123"
        )
        
        assert response.error_code == "TEST_ERROR"
        assert response.message == "Test message"
        assert response.category == ErrorCategory.VALIDATION
        assert response.severity == ErrorSeverity.MEDIUM
        assert response.details == {"field": "value"}
        assert response.suggestions == ["Try again"]
        assert response.user_message == "User message"
        assert response.trace_id == "trace-123"


class TestErrorHandler:
    """Test ErrorHandler class."""

    def test_error_handler_initialization(self):
        """Test ErrorHandler initialization."""
        handler = ErrorHandler()
        assert hasattr(handler, 'error_counters')
        assert hasattr(handler, 'handle_error')
        assert isinstance(handler.error_counters, dict)

    def test_handle_error_z2_error(self):
        """Test handling Z2Error."""
        handler = ErrorHandler()
        error = ValidationError("Test validation error")
        
        response = handler.handle_error(error)
        
        assert response.status_code == 400  # Validation errors are 400
        response_data = eval(response.body.decode())  # Parse JSON
        assert response_data["category"] == ErrorCategory.VALIDATION

    def test_handle_error_http_exception(self):
        """Test handling HTTP exceptions."""
        handler = ErrorHandler()
        from fastapi import HTTPException
        
        http_error = HTTPException(status_code=404, detail="Not found")
        response = handler.handle_error(http_error)
        
        assert response.status_code == 404

    def test_handle_error_generic_exception(self):
        """Test handling generic exceptions."""
        handler = ErrorHandler()
        error = ValueError("Generic error")
        
        response = handler.handle_error(error)
        
        assert response.status_code == 500  # Generic errors are 500


class TestUtilityFunctions:
    """Test utility functions."""

    def test_chain_error(self):
        """Test error chaining."""
        original = ValueError("Original error")
        new_error = BusinessLogicError("Business error")
        
        chained = chain_error(new_error, original)
        
        assert chained.cause == original
        assert chained.message == "Business error"

    def test_create_validation_error(self):
        """Test creating validation error from field errors."""
        field_errors = [
            {"field": "email", "message": "Invalid email format"},
            {"field": "age", "message": "Must be positive"}
        ]
        
        error = create_validation_error(field_errors)
        
        assert isinstance(error, ValidationError)
        assert error.details["field_errors"] == field_errors
        assert "Validation failed" in error.message

    def test_create_external_service_error(self):
        """Test creating external service error."""
        original = ConnectionError("Network timeout")
        
        error = create_external_service_error("OpenAI", original)
        
        assert isinstance(error, ExternalServiceError)
        assert error.cause == original
        assert "OpenAI" in error.message
        assert error.details["service"] == "OpenAI"

    def test_handle_errors_with_context_decorator(self):
        """Test error handling decorator."""
        # Test that the decorator function exists and can be called
        decorator = handle_errors_with_context()
        assert callable(decorator)


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_error_with_none_values(self):
        """Test error handling with None values."""
        error = Z2Error(
            message="Test",
            details=None,
            suggestions=None,
            cause=None
        )
        
        assert error.details == {}
        assert error.suggestions == []
        assert error.cause is None

    def test_error_response_serialization(self):
        """Test ErrorResponse can be serialized."""
        response = ErrorResponse(
            error_code="TEST_ERROR",
            message="Test message",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            details={},
            suggestions=[],
            user_message="Test message",
            timestamp=datetime.now(),
            trace_id="trace-123"
        )
        
        # Should be able to convert to dict
        response_dict = response.model_dump()
        assert isinstance(response_dict, dict)
        assert "error_code" in response_dict
        assert "timestamp" in response_dict

    def test_empty_field_errors(self):
        """Test validation error with empty field errors."""
        error = create_validation_error([])
        assert error.details["field_errors"] == []
        assert "Validation failed" in error.message

    def test_error_handler_handle_error_basic(self):
        """Test error handler basic functionality."""
        handler = ErrorHandler()
        error = SystemError("Test error")
        
        # Should not raise exception
        response = handler.handle_error(error)
        assert response is not None
        assert hasattr(response, 'status_code')