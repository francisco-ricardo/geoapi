"""
Schemas for aggregation endpoints.

These schemas define the data structures used for aggregating speed data,
filtering by spatial bounding box, and summarizing speed records.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AggregatedSpeedData(BaseModel):
    """
    Individual aggregated speed data item.
    - geometry: GeoJSON geometry for MapboxGL
    - average_speed: Average speed for visualization
    - road_name: Road name for display
    - link_id: Unique identifier
    - length: Road segment length
    """

    link_id: int = Field(..., description="Unique identifier for the road link")
    road_name: Optional[str] = Field(None, description="Name of the road")
    length: Optional[float] = Field(None, description="Length of the road segment")
    road_type: Optional[str] = Field(
        None, description="Type/classification of the road"
    )
    speed_limit: Optional[int] = Field(None, description="Speed limit in mph")
    geometry: Optional[Dict[str, Any]] = Field(None, description="GeoJSON geometry")
    average_speed: Optional[float] = Field(
        None, description="Average speed for the period in mph"
    )
    record_count: int = Field(
        ..., description="Number of speed records used in aggregation"
    )
    min_speed: Optional[float] = Field(
        None, description="Minimum speed recorded in mph"
    )
    max_speed: Optional[float] = Field(
        None, description="Maximum speed recorded in mph"
    )
    speed_stddev: Optional[float] = Field(
        None, description="Standard deviation of speeds"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "link_id": 1148855686,
                "road_name": "Main St",
                "length": 0.027340324,
                "road_type": "arterial",
                "speed_limit": 35,
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[-81.51023, 30.16599], [-81.51038, 30.16637]],
                },
                "average_speed": 28.45,
                "record_count": 15,
                "min_speed": 22.3,
                "max_speed": 35.1,
                "speed_stddev": 4.2,
            }
        }
    )


# Response types - Direct list/item for client compatibility
AggregationListResponse = List[AggregatedSpeedData]  # Direct list for /aggregates/
SingleLinkAggregateResponse = (
    AggregatedSpeedData  # Single item for /aggregates/{link_id}
)


class DataSummaryResponse(BaseModel):
    """Response schema for data summary statistics."""

    total_speed_records: int = Field(..., description="Total number of speed records")
    total_links: int = Field(..., description="Total number of links")
    links_with_speed_data: int = Field(
        ..., description="Number of links with speed data"
    )
    average_speed_overall: Optional[float] = Field(
        None, description="Overall average speed"
    )
    min_speed_overall: Optional[float] = Field(
        None, description="Overall minimum speed"
    )
    max_speed_overall: Optional[float] = Field(
        None, description="Overall maximum speed"
    )
    available_periods: List[str] = Field(..., description="Available time periods")
    available_days: List[str] = Field(..., description="Available days of week")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_speed_records": 1239946,
                "total_links": 100927,
                "links_with_speed_data": 88680,
                "average_speed_overall": 32.41,
                "min_speed_overall": 0.62,
                "max_speed_overall": 154.72,
                "available_periods": [
                    "AM Peak",
                    "Early Afternoon",
                    "Early Morning",
                    "Evening",
                    "Midday",
                    "Overnight",
                    "PM Peak",
                ],
                "available_days": ["Monday"],
            }
        }
    )


# Request schemas for validation
class AggregateQueryParams(BaseModel):
    """Query parameters for aggregate endpoints."""

    day: str = Field(..., description="Day of week (Monday, Tuesday, etc.)")
    period: str = Field(..., description="Time period (AM Peak, PM Peak, etc.)")

    model_config = ConfigDict(
        json_schema_extra={"example": {"day": "Monday", "period": "AM Peak"}}
    )


class SpatialFilterRequest(BaseModel):
    """
    Request body for spatial filtering endpoint.
    """

    day: str = Field(..., description="Day of week (Monday, Tuesday, etc.)")
    period: str = Field(..., description="Time period (AM Peak, PM Peak, etc.)")
    bbox: List[float] = Field(
        ..., description="Bounding box as [min_lon, min_lat, max_lon, max_lat]"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "day": "Wednesday",
                "period": "AM Peak",
                "bbox": [-81.8, 30.1, -81.6, 30.3],
            }
        }
    )
