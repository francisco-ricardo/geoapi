"""
Link model representing road segments with spatial geometry.
"""

from geoalchemy2 import Geometry
from sqlalchemy import Column, Float, Index, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Link(Base):
    """
    Road link/segment model with spatial geometry.

    Represents a road segment with LINESTRING geometry and metadata.
    Each link corresponds to a road segment that has traffic speed data.

    Attributes:
        link_id: Unique identifier for the road link
        geometry: Road segment geometry as LINESTRING in WGS84
        road_name: Name or identifier of the road
        length: Length of the road segment in meters
        road_type: Type/classification of the road
        speed_limit: Speed limit for this road segment in mph
        speed_records: Related speed measurements for this link
    """

    __tablename__ = "links"

    # Primary key
    link_id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Unique identifier for the road link",
    )

    # Spatial geometry (LINESTRING in WGS84)
    geometry = Column(
        Geometry("LINESTRING", srid=4326),
        nullable=True,  # Allow null for testing with SQLite
        comment="Road segment geometry in WGS84 (EPSG:4326)",
    )

    # Road metadata
    road_name = Column(
        String, nullable=True, index=True, comment="Road name or identifier"
    )

    length = Column(Float, nullable=True, comment="Road length in meters")

    road_type = Column(String, nullable=True, comment="Type or classification of road")

    speed_limit = Column(Integer, nullable=True, comment="Speed limit in mph")

    # Relationship with speed records
    speed_records = relationship(
        "SpeedRecord",
        back_populates="link",
        cascade="all, delete-orphan",
        lazy="dynamic",  # For better performance with large datasets
    )

    # Indexes for spatial queries
    __table_args__ = (
        Index("idx_link_geometry", "geometry", postgresql_using="gist"),
        Index("idx_link_road_name", "road_name"),
    )

    def __repr__(self) -> str:
        """String representation of Link."""
        return f"<Link(link_id={self.link_id}, road_name='{self.road_name}')>"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Link {self.link_id}: {self.road_name or 'Unnamed Road'}"
