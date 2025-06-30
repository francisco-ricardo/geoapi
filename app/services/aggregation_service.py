"""
Service layer for aggregation operations.
"""

import json
from typing import Any, Dict, List, Optional

from geoalchemy2.functions import ST_AsGeoJSON
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.time_periods import DayOfWeek, TimePeriod, validate_day_period_params
from app.models.link import Link
from app.models.speed_record import SpeedRecord

logger = get_logger(__name__)


class AggregationService:
    """Service for performing speed data aggregations."""

    def __init__(self, db: Session):
        self.db = db

    def get_aggregated_speeds(
        self, day: str, period: str, link_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get aggregated speed data for a specific day and period.

        Args:
            day: Day of week (e.g., "Monday")
            period: Time period (e.g., "AM Peak")
            link_id: Optional specific link ID to filter by

        Returns:
            List of aggregated speed data with geometry

        Raises:
            ValueError: If day or period is invalid
        """
        # Validate parameters
        day_obj, period_obj = validate_day_period_params(day, period)

        logger.info(
            f"Getting aggregated speeds for {day} {period}"
            + (f" (link_id={link_id})" if link_id else "")
        )

        # Build query
        query = (
            self.db.query(
                Link.link_id,
                Link.road_name,
                Link.length,
                Link.road_type,
                Link.speed_limit,
                Link.geometry,
                func.avg(SpeedRecord.speed).label("average_speed"),
                func.count(SpeedRecord.id).label("record_count"),
                func.min(SpeedRecord.speed).label("min_speed"),
                func.max(SpeedRecord.speed).label("max_speed"),
                func.stddev(SpeedRecord.speed).label("speed_stddev"),
            )
            .join(SpeedRecord, Link.link_id == SpeedRecord.link_id)
            .filter(
                and_(
                    SpeedRecord.time_period == period_obj.period_name,
                    # Note: day_of_week field is empty in current data,
                    # so we'll skip this filter for now
                    # SpeedRecord.day_of_week == day_obj.day_name
                )
            )
        )

        # Add link_id filter if specified
        if link_id:
            query = query.filter(Link.link_id == link_id)

        # Group by link attributes
        query = query.group_by(
            Link.link_id,
            Link.road_name,
            Link.length,
            Link.road_type,
            Link.speed_limit,
            Link.geometry,
        )

        # Execute query
        results = query.all()

        logger.info(f"Found {len(results)} aggregated records")

        # Process results
        aggregated_data = []
        for result in results:
            # Convert geometry to GeoJSON
            geometry_dict = None
            if result.geometry is not None:
                try:
                    geojson_str = self.db.scalar(ST_AsGeoJSON(result.geometry))
                    if geojson_str:
                        geometry_dict = json.loads(geojson_str)
                except Exception as e:
                    logger.error(
                        f"Error converting geometry for link_id={result.link_id}",
                        extra={"error": str(e), "link_id": result.link_id},
                    )
                    geometry_dict = None

            # Build result dict
            link_data = {
                "link_id": result.link_id,
                "road_name": result.road_name,
                "length": result.length,
                "road_type": result.road_type,
                "speed_limit": result.speed_limit,
                "geometry": geometry_dict,
                "average_speed": (
                    round(float(result.average_speed), 2)
                    if result.average_speed
                    else None
                ),
                "record_count": result.record_count,
                "min_speed": (
                    round(float(result.min_speed), 2) if result.min_speed else None
                ),
                "max_speed": (
                    round(float(result.max_speed), 2) if result.max_speed else None
                ),
                "speed_stddev": (
                    round(float(result.speed_stddev), 2)
                    if result.speed_stddev
                    else None
                ),
                "day": day,
                "period": period,
            }

            aggregated_data.append(link_data)

        return aggregated_data

    def get_single_link_aggregate(
        self, link_id: int, day: str, period: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get aggregated data for a single link.

        Args:
            link_id: ID of the link
            day: Day of week
            period: Time period

        Returns:
            Aggregated data for the link or None if not found
        """
        results = self.get_aggregated_speeds(day, period, link_id=link_id)
        return results[0] if results else None

    def get_available_periods(self) -> List[str]:
        """Get list of available time periods in the data."""
        periods = (
            self.db.query(SpeedRecord.time_period)
            .distinct()
            .filter(SpeedRecord.time_period.isnot(None))
            .all()
        )
        return sorted([p[0] for p in periods])

    def get_available_days(self) -> List[str]:
        """Get list of available days in the data."""
        days = (
            self.db.query(SpeedRecord.day_of_week)
            .distinct()
            .filter(SpeedRecord.day_of_week.isnot(None))
            .all()
        )
        return sorted([d[0] for d in days if d[0]])

    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the data."""
        total_records = self.db.query(SpeedRecord).count()
        total_links = self.db.query(Link).count()
        links_with_data = self.db.query(SpeedRecord.link_id).distinct().count()

        avg_speed = self.db.query(func.avg(SpeedRecord.speed)).scalar()
        min_speed = self.db.query(func.min(SpeedRecord.speed)).scalar()
        max_speed = self.db.query(func.max(SpeedRecord.speed)).scalar()

        return {
            "total_speed_records": total_records,
            "total_links": total_links,
            "links_with_speed_data": links_with_data,
            "average_speed_overall": round(float(avg_speed), 2) if avg_speed else None,
            "min_speed_overall": round(float(min_speed), 2) if min_speed else None,
            "max_speed_overall": round(float(max_speed), 2) if max_speed else None,
            "available_periods": self.get_available_periods(),
            "available_days": self.get_available_days()
            or ["Data missing - using Monday as default"],
        }
