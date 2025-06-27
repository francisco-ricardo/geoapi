"""
Pydantic schemas for Link model.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class LinkBase(BaseModel):
    """Base schema for Link with common fields."""
    
    road_name: Optional[str] = Field(
        default=None, 
        description="Name or identifier of the road",
        examples=["Main Street"]
    )
    length: Optional[float] = Field(
        default=None, 
        ge=0,
        description="Road length in meters",
        examples=[1250.5]
    )
    road_type: Optional[str] = Field(
        default=None,
        description="Type or classification of road",
        examples=["arterial"]
    )
    speed_limit: Optional[int] = Field(
        default=None,
        ge=0,
        le=200,
        description="Speed limit in mph",
        examples=[35]
    )


class LinkCreate(LinkBase):
    """Schema for creating a new Link."""
    
    link_id: int = Field(
        description="Unique identifier for the road link",
        examples=[12345]
    )
    geometry: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Road segment geometry as GeoJSON LineString in WGS84"
    )


class LinkUpdate(LinkBase):
    """Schema for updating an existing Link."""
    
    geometry: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Road segment geometry as GeoJSON LineString in WGS84"
    )


class LinkResponse(LinkBase):
    """Schema for returning Link data."""
    
    link_id: int = Field(
        description="Unique identifier for the road link"
    )
    geometry: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Road segment geometry as GeoJSON LineString in WGS84"
    )
    
    # Computed fields
    speed_records_count: Optional[int] = Field(
        default=None,
        description="Number of speed records for this link"
    )
    
    model_config = ConfigDict(from_attributes=True)


class LinkList(BaseModel):
    """Schema for paginated list of Links."""
    
    items: List[LinkResponse] = Field(
        description="List of links"
    )
    total: int = Field(
        ge=0,
        description="Total number of links"
    )
    page: int = Field(
        ge=1,
        description="Current page number"
    )
    size: int = Field(
        ge=1,
        le=100,
        description="Number of items per page"
    )
    pages: int = Field(
        ge=0,
        description="Total number of pages"
    )
