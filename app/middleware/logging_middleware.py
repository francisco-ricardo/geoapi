"""
Middleware for FastAPI request/response logging and correlation ID tracking.
"""

import time
import uuid

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import get_settings
from app.core.logging import ContextLogger, get_logger, logger

settings = get_settings()

# Configure logger with settings
app_logger = get_logger(name="geoapi", log_level=settings.log_level)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.

    Features:
    - Request/response logging with timing
    - Correlation ID generation and propagation
    - Performance metrics
    - Error tracking
    """

    async def dispatch(self, request: Request, call_next):
        """Process request, add correlation ID, and log request/response details."""
        # Generate correlation ID if not provided in headers
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())

        # Get request details
        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else None

        # Create request-scoped logger with correlation ID
        # We need to type cast to ContextLogger to access the with_correlation_id method
        request_logger = get_logger(name="geoapi.request", log_level=settings.log_level)
        if isinstance(request_logger, ContextLogger):
            request_logger = request_logger.with_correlation_id(correlation_id)

        # Log request
        request_logger.info(
            f"Request started: {method} {url}",
            extra={
                "http": {
                    "method": method,
                    "url": url,
                    "client_ip": client_host,
                    "request_id": correlation_id,
                },
                "event": "request_started",
            },
        )

        # Time the request processing
        start_time = time.time()

        try:
            # Add correlation ID to request state for access in endpoint handlers
            request.state.correlation_id = correlation_id
            request.state.logger = request_logger

            # Process the request
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id

            # Log response
            status_code = response.status_code
            request_logger.info(
                f"Request completed: {method} {url} - {status_code}",
                extra={
                    "http": {
                        "method": method,
                        "url": url,
                        "status_code": status_code,
                        "response_time": process_time,
                        "request_id": correlation_id,
                    },
                    "event": "request_completed",
                    "performance": {"response_time": process_time},
                },
            )

            return response

        except Exception as exc:
            # Calculate processing time for error case
            process_time = time.time() - start_time

            # Log the exception
            request_logger.exception(
                f"Request failed: {method} {url}",
                extra={
                    "http": {
                        "method": method,
                        "url": url,
                        "error": str(exc),
                        "response_time": process_time,
                        "request_id": correlation_id,
                    },
                    "event": "request_failed",
                    "performance": {"response_time": process_time},
                },
            )

            # Re-raise the exception
            raise


def setup_logging_middleware(app: FastAPI) -> None:
    """
    Configure logging middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Add the logging middleware
    app.add_middleware(LoggingMiddleware)

    # Log application startup
    logger.info(
        f"Application startup: {settings.app_name} v{settings.app_version}",
        extra={
            "app": {
                "name": settings.app_name,
                "version": settings.app_version,
                "environment": (
                    "production" if settings.log_format == "json" else "development"
                ),
            },
            "event": "application_startup",
        },
    )
