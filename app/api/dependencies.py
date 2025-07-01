"""
FastAPI dependencies.
"""

from fastapi import Request

from app.core.database import get_db
from app.core.logging import ContextLogger


def get_request_logger(request: Request) -> ContextLogger:
    """
    Get the request-scoped logger with correlation ID.

    Args:
        request: The current request object

    Returns:
        Logger instance with correlation ID context
    """
    return request.state.logger


# Re-export dependencies
__all__ = ["get_db", "get_request_logger"]
