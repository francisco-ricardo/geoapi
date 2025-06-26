"""
Simplified models for testing without PostGIS dependencies.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

# Create a separate base for test models
TestBase = declarative_base()


class SimplifiedLink(TestBase):
    """Simplified Link model for testing without geometry."""
    __tablename__ = "test_links"

    link_id = Column(Integer, primary_key=True, index=True)
    road_name = Column(String, nullable=True, index=True)
    length = Column(Float, nullable=True)
    road_type = Column(String, nullable=True)
    speed_limit = Column(Integer, nullable=True)
    
    # Relationship with speed records
    speed_records = relationship(
        "SimplifiedSpeedRecord", 
        back_populates="link",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SimplifiedLink(link_id={self.link_id}, road_name='{self.road_name}')>"

    def __str__(self) -> str:
        return f"Link {self.link_id}: {self.road_name or 'Unnamed Road'}"


class SimplifiedSpeedRecord(TestBase):
    """Simplified SpeedRecord model for testing."""
    __tablename__ = "test_speed_records"

    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(
        Integer, 
        ForeignKey("test_links.link_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    timestamp = Column(DateTime, nullable=False, index=True)
    speed = Column(Float, nullable=False)
    day_of_week = Column(String, nullable=True, index=True)
    time_period = Column(String, nullable=True, index=True)
    
    # Relationship with Link
    link = relationship("SimplifiedLink", back_populates="speed_records")

    def __repr__(self) -> str:
        return (
            f"<SimplifiedSpeedRecord(id={self.id}, link_id={self.link_id}, "
            f"speed={self.speed}, timestamp={self.timestamp})>"
        )

    def __str__(self) -> str:
        timestamp_str = getattr(self, 'timestamp', 'Unknown')
        return f"Speed {self.speed} mph on link {self.link_id} at {timestamp_str}"

    @property
    def formatted_timestamp(self) -> str:
        """Get formatted timestamp string."""
        timestamp = getattr(self, 'timestamp', None)
        if timestamp and isinstance(timestamp, datetime):
            return timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')
        return "Unknown"

    @property
    def is_peak_hour(self) -> bool:
        """Check if this record is from peak hours."""
        return getattr(self, 'time_period', '') in ["AM Peak", "PM Peak"]
