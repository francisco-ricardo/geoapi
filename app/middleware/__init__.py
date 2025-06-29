"""
Middleware package for the FastAPI application.
"""

from app.middleware.logging_middleware import setup_logging_middleware

__all__ = ["setup_logging_middleware"]
