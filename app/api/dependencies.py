"""
FastAPI dependencies.
"""
from app.core.database import get_db

# Re-export the database dependency
__all__ = ["get_db"]
