"""
Pydantic schemas for SpeedRecord model.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SpeedRecordBase(BaseModel):
    """Base schema for SpeedRecord with common fields."""

    timestamp: datetime = Field(
        description="Timestamp of the speed measurement",
        examples=["2024-01-15T14:30:00Z"],
    )
    speed: float = Field(
        ge=0, le=300, description="Speed in miles per hour", examples=[45.5]
    )
    day_of_week: Optional[str] = Field(
        default=None,
        description="Day of week (Monday, Tuesday, etc.)",
        examples=["Monday", "Tuesday", "Wednesday"],
    )
    time_period: Optional[str] = Field(
        default=None,
        description="Time period classification (AM Peak, PM Peak, etc.)",
        examples=["AM Peak", "PM Peak", "Off Peak", "Night"],
    )


class SpeedRecordCreate(SpeedRecordBase):
    """Schema for creating a new SpeedRecord."""

    link_id: int = Field(
        description="ID of the link this speed record belongs to", examples=[12345]
    )


class SpeedRecordUpdate(BaseModel):
    """Schema for updating an existing SpeedRecord."""

    timestamp: Optional[datetime] = Field(
        default=None,
        description="Timestamp of the speed measurement",
        examples=["2024-01-15T14:30:00Z"],
    )
    speed: Optional[float] = Field(
        default=None,
        ge=0,
        le=300,
        description="Speed in miles per hour",
        examples=[45.5],
    )
    day_of_week: Optional[str] = Field(
        default=None,
        description="Day of week (Monday, Tuesday, etc.)",
        examples=["Monday", "Tuesday", "Wednesday"],
    )
    time_period: Optional[str] = Field(
        default=None,
        description="Time period classification (AM Peak, PM Peak, etc.)",
        examples=["AM Peak", "PM Peak", "Off Peak", "Night"],
    )


class SpeedRecord(SpeedRecordBase):
    """Schema for returning SpeedRecord data."""

    id: int = Field(description="Unique identifier for the speed record")
    link_id: int = Field(description="ID of the link this speed record belongs to")

    model_config = ConfigDict(from_attributes=True)


class SpeedRecordList(BaseModel):
    """Schema for paginated list of SpeedRecords."""

    items: List[SpeedRecord] = Field(description="List of speed records")
    total: int = Field(ge=0, description="Total number of speed records")
    page: int = Field(ge=1, description="Current page number")
    size: int = Field(ge=1, le=100, description="Number of items per page")
    pages: int = Field(ge=0, description="Total number of pages")
