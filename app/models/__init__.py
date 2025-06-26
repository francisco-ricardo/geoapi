"""
Database models package.

This package contains all SQLAlchemy ORM models for the GeoAPI application.
Models represent the database schema and provide the interface for
data operations.

Available models:
- Link: Road segments with spatial geometry
- SpeedRecord: Traffic speed measurements
"""
from app.models.link import Link
from app.models.speed_record import SpeedRecord

__all__ = ["Link", "SpeedRecord"]
