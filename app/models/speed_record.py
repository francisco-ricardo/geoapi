"""
Speed record model for temporal traffic data.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Index
from sqlalchemy.orm import relationship

from app.core.database import Base


class SpeedRecord(Base):
    """
    Speed record model for temporal traffic data.
    
    Stores speed measurements for road links at specific timestamps.
    Each record represents a single speed measurement for a road segment
    at a particular point in time.
    
    Attributes:
        id: Auto-generated primary key
        link_id: Foreign key to the related Link
        timestamp: When the speed measurement was taken
        speed: Speed measurement in mph
        day_of_week: Day of week (Monday, Tuesday, etc.)
        time_period: Time period classification (AM Peak, PM Peak, etc.)
        link: Related Link object
    """
    __tablename__ = "speed_records"

    # Primary key (auto-generated)
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        comment="Auto-generated primary key"
    )
    
    # Foreign key to Link
    link_id = Column(
        Integer, 
        ForeignKey("links.link_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to links table"
    )
    
    # Temporal data
    timestamp = Column(
        DateTime, 
        nullable=False, 
        index=True,
        comment="Timestamp when speed was measured (UTC)"
    )
    
    # Speed measurement
    speed = Column(
        Float, 
        nullable=False,
        comment="Speed measurement in mph"
    )
    
    # Derived temporal attributes for efficient querying
    day_of_week = Column(
        String, 
        nullable=True, 
        index=True,
        comment="Day of week (Monday, Tuesday, etc.)"
    )
    
    time_period = Column(
        String, 
        nullable=True, 
        index=True,
        comment="Time period classification (AM Peak, PM Peak, etc.)"
    )
    
    # Relationship with Link
    link = relationship(
        "Link", 
        back_populates="speed_records"
    )

    # Composite indexes for efficient queries
    __table_args__ = (
        Index('idx_speed_link_timestamp', 'link_id', 'timestamp'),
        Index('idx_speed_day_period', 'day_of_week', 'time_period'),
        Index('idx_speed_link_day_period', 'link_id', 'day_of_week', 'time_period'),
        Index('idx_speed_timestamp_range', 'timestamp'),
    )

    def __repr__(self) -> str:
        """String representation of SpeedRecord."""
        return (
            f"<SpeedRecord(id={self.id}, link_id={self.link_id}, "
            f"speed={self.speed}, timestamp={self.timestamp})>"
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"Speed {self.speed} mph on link {self.link_id} "
            f"at {getattr(self, 'timestamp', 'Unknown')}"
        )

    @property
    def formatted_timestamp(self) -> str:
        """Get formatted timestamp string."""
        timestamp = getattr(self, 'timestamp', None)
        if timestamp and isinstance(timestamp, datetime):
            return timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')
        return "Unknown"

    @property
    def is_peak_hour(self) -> bool:
        """Check if this record is from peak hours (AM or PM Peak)."""
        return self.time_period in ["AM Peak", "PM Peak"]
