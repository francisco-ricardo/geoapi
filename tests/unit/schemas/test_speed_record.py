"""
Test Pydantic schemas for SpeedRecord model - Updated Version.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.speed_record import (
    SpeedRecord,
    SpeedRecordBase,
    SpeedRecordCreate,
    SpeedRecordList,
    SpeedRecordUpdate,
)


class TestSpeedRecordSchemasNew:
    """Test SpeedRecord Pydantic schemas with new field structure."""

    def test_speed_record_base_creation(self):
        """Test basic SpeedRecordBase creation."""
        timestamp = datetime.now()
        speed_record = SpeedRecordBase(
            timestamp=timestamp, speed=45.5, day_of_week="Monday", time_period="AM Peak"
        )

        assert speed_record.timestamp == timestamp
        assert speed_record.speed == 45.5
        assert speed_record.day_of_week == "Monday"
        assert speed_record.time_period == "AM Peak"

    def test_speed_record_base_optional_fields(self):
        """Test SpeedRecordBase with optional fields as None."""
        timestamp = datetime.now()
        speed_record = SpeedRecordBase(timestamp=timestamp, speed=60.0)

        assert speed_record.timestamp == timestamp
        assert speed_record.speed == 60.0
        assert speed_record.day_of_week is None
        assert speed_record.time_period is None

    def test_speed_record_create_validation(self):
        """Test SpeedRecordCreate validation."""
        timestamp = datetime.now()
        speed_record = SpeedRecordCreate(
            link_id=12345,
            timestamp=timestamp,
            speed=75.5,
            day_of_week="Tuesday",
            time_period="PM Peak",
        )

        assert speed_record.link_id == 12345
        assert speed_record.timestamp == timestamp
        assert speed_record.speed == 75.5
        assert speed_record.day_of_week == "Tuesday"
        assert speed_record.time_period == "PM Peak"

    def test_speed_record_model_validation(self):
        """Test SpeedRecord response schema."""
        timestamp = datetime.now()
        speed_record = SpeedRecord(
            id=1,
            link_id=12345,
            timestamp=timestamp,
            speed=45.5,
            day_of_week="Monday",
            time_period="AM Peak",
        )

        assert speed_record.id == 1
        assert speed_record.link_id == 12345
        assert speed_record.speed == 45.5
        assert speed_record.day_of_week == "Monday"
        assert speed_record.time_period == "AM Peak"

    def test_speed_record_invalid_speed(self):
        """Test validation with invalid speed values."""
        timestamp = datetime.now()

        # Test negative speed
        with pytest.raises(ValidationError) as exc_info:
            SpeedRecordCreate(link_id=12345, timestamp=timestamp, speed=-10.0)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("speed",)
        assert "greater_than_equal" in errors[0]["type"]

    def test_speed_record_boundary_values(self):
        """Test boundary speed values."""
        timestamp = datetime.now()

        # Test minimum speed (0)
        speed_record = SpeedRecordCreate(link_id=12345, timestamp=timestamp, speed=0.0)
        assert speed_record.speed == 0.0

        # Test maximum speed (300)
        speed_record = SpeedRecordCreate(
            link_id=12345, timestamp=timestamp, speed=300.0
        )
        assert speed_record.speed == 300.0
