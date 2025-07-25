"""
Logging utilities for the Z2 platform.
"""

from typing import Any

import structlog


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def log_request(
    logger: structlog.stdlib.BoundLogger, method: str, path: str, **kwargs
) -> None:
    """Log API request information.

    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        **kwargs: Additional context
    """
    logger.info("API request", method=method, path=path, **kwargs)


def log_response(
    logger: structlog.stdlib.BoundLogger, status_code: int, duration_ms: float, **kwargs
) -> None:
    """Log API response information.

    Args:
        logger: Logger instance
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        **kwargs: Additional context
    """
    logger.info(
        "API response", status_code=status_code, duration_ms=duration_ms, **kwargs
    )


def log_error(
    logger: structlog.stdlib.BoundLogger,
    error: Exception,
    context: dict[str, Any] = None,
) -> None:
    """Log error with structured context.

    Args:
        logger: Logger instance
        error: Exception instance
        context: Additional error context
    """
    context = context or {}
    logger.error(
        "Error occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        **context,
    )
