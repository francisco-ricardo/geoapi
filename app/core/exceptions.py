"""
Custom exception handlers for FastAPI.

This module defines handlers for:
- Request validation errors
- Uncaught exceptions
- Custom domain exceptions
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

logger = get_logger(name="geoapi.errors")

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors and log them with appropriate context.
    
    Args:
        request: Request object
        exc: Validation exception
        
    Returns:
        JSONResponse with error details
    """
    # Get request-scoped logger if available, otherwise use default
    request_logger = getattr(request.state, "logger", logger)
    
    # Extract error details
    error_detail = []
    for error in exc.errors():
        error_detail.append({
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        })
    
    # Log the validation error
    request_logger.warning(
        "Request validation error",
        extra={
            "validation_errors": error_detail,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": error_detail,
            "message": "Validation error in request data"
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions and log them with appropriate context.
    
    Args:
        request: Request object
        exc: HTTP exception
        
    Returns:
        JSONResponse with error details
    """
    # Get request-scoped logger if available, otherwise use default
    request_logger = getattr(request.state, "logger", logger)
    
    # Log the HTTP exception
    if exc.status_code >= 500:
        log_method = request_logger.error
    elif exc.status_code >= 400:
        log_method = request_logger.warning
    else:
        log_method = request_logger.info
    
    log_method(
        f"HTTP exception: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "headers": dict(request.headers)
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "message": str(exc.detail)
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all uncaught exceptions and log them with appropriate context.
    
    Args:
        request: Request object
        exc: Any exception
        
    Returns:
        JSONResponse with error details
    """
    # Get request-scoped logger if available, otherwise use default
    request_logger = getattr(request.state, "logger", logger)
    
    # Log the exception with full traceback
    request_logger.exception(
        f"Unhandled exception: {str(exc)}",
        extra={
            "exception_type": exc.__class__.__name__,
            "path": request.url.path,
            "method": request.method,
            "query_params": str(request.query_params),
            "client": request.client.host if request.client else None
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
