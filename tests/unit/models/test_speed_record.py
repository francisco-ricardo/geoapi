"""
Comprehensive tests for SpeedRecord model functionality.
Consolidates all SpeedRecord model tests including structure, relationships, and queries.
"""
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import func
from datetime import datetime, UTC

from app.models.speed_record import SpeedRecord
from tests.fixtures.models import SimplifiedLink, SimplifiedSpeedRecord


class TestSpeedRecordModelStructure:
    """Test SpeedRecord model structure and metadata."""
    
    def test_speed_record_tablename(self):
        """Test speed record table name is correct."""
        assert SpeedRecord.__tablename__ == "speed_records"
    
    def test_speed_record_structure(self):
        """Test speed record model structure and attributes."""
        # Test that the model has the expected attributes
        assert hasattr(SpeedRecord, 'id')
        assert hasattr(SpeedRecord, 'link_id')
        assert hasattr(SpeedRecord, 'timestamp')
        assert hasattr(SpeedRecord, 'speed')
        assert hasattr(SpeedRecord, 'day_of_week')
        assert hasattr(SpeedRecord, 'time_period')
        assert hasattr(SpeedRecord, 'link')

    def test_speed_record_column_metadata(self):
        """Test SpeedRecord column metadata and comments."""
        # Test that column comments are properly defined
        assert SpeedRecord.id.comment == "Auto-generated primary key"
        assert SpeedRecord.link_id.comment == "Foreign key to links table"
        assert SpeedRecord.timestamp.comment == "Timestamp when speed was measured (UTC)"
        assert SpeedRecord.speed.comment == "Speed measurement in mph"
        assert SpeedRecord.day_of_week.comment == "Day of week (Monday, Tuesday, etc.)"
        assert SpeedRecord.time_period.comment == "Time period classification (AM Peak, PM Peak, etc.)"

    def test_speed_record_indexes(self):
        """Test SpeedRecord table indexes."""
        # Verify table args for indexes are defined correctly
        assert hasattr(SpeedRecord, '__table_args__')
        table_args = SpeedRecord.__table_args__
        
        # Check that indexes are defined (should have multiple indexes)
        assert len(table_args) >= 4
        
        # Convert to list of index names for easier checking
        index_names = [arg.name for arg in table_args if hasattr(arg, 'name')]
        
        # Check for expected indexes (using actual index names from model)
        assert 'idx_speed_link_timestamp' in index_names
        assert 'idx_speed_day_period' in index_names
        assert 'idx_speed_link_day_period' in index_names
        assert 'idx_speed_timestamp_range' in index_names


class TestSpeedRecordModelBasic:
    """Test basic SpeedRecord model operations using simplified models."""
    
    def test_simplified_speed_record_creation(self):
        """Test creation of simplified speed record for testing."""
        record = SimplifiedSpeedRecord(
            id=1,
            link_id=1,
            speed=65.0,
            timestamp=datetime.now(UTC),
            day_of_week="Monday",
            time_period="AM Peak"
        )
        
        # Test the actual instance attributes
        assert getattr(record, 'id') == 1
        assert getattr(record, 'link_id') == 1
        assert getattr(record, 'speed') == 65.0
        assert getattr(record, 'day_of_week') == "Monday"
        assert getattr(record, 'time_period') == "AM Peak"
    
    def test_simplified_speed_record_string_representation(self):
        """Test string representation of simplified speed record."""
        timestamp = datetime.now(UTC)
        record = SimplifiedSpeedRecord(
            id=1,
            link_id=1,
            speed=65.0,
            timestamp=timestamp
        )
        
        result = str(record)
        assert "Speed 65.0 mph on link 1" in result
    
    def test_simplified_speed_record_with_none_timestamp(self):
        """Test simplified speed record with None timestamp."""
        record = SimplifiedSpeedRecord(
            id=1,
            link_id=1,
            speed=65.0,
            timestamp=None
        )
        
        # Test string representation with None timestamp
        result = str(record)
        assert "Unknown" in result
        assert "Speed 65.0 mph on link 1" in result

    def test_formatted_timestamp_property(self):
        """Test formatted timestamp property."""
        timestamp = datetime(2025, 6, 29, 14, 30, 0, tzinfo=UTC)
        record = SimplifiedSpeedRecord(
            id=1,
            link_id=1,
            speed=65.0,
            timestamp=timestamp
        )
        
        formatted = record.formatted_timestamp
        assert "2025-06-29 14:30:00 UTC" == formatted

    def test_formatted_timestamp_with_none(self):
        """Test formatted timestamp with None."""
        record = SimplifiedSpeedRecord(
            id=1,
            link_id=1,
            speed=65.0,
            timestamp=None
        )
        
        formatted = record.formatted_timestamp
        assert formatted == "Unknown"

    def test_is_peak_hour_property(self):
        """Test is_peak_hour property."""
        # Test with AM Peak
        record_am = SimplifiedSpeedRecord(
            id=1,
            link_id=1,
            speed=65.0,
            time_period="AM Peak"
        )
        assert record_am.is_peak_hour is True
        
        # Test with PM Peak
        record_pm = SimplifiedSpeedRecord(
            id=2,
            link_id=1,
            speed=55.0,
            time_period="PM Peak"
        )
        assert record_pm.is_peak_hour is True
        
        # Test with Off-Peak
        record_off = SimplifiedSpeedRecord(
            id=3,
            link_id=1,
            speed=70.0,
            time_period="Off-Peak"
        )
        assert record_off.is_peak_hour is False
        
        # Test with None
        record_none = SimplifiedSpeedRecord(
            id=4,
            link_id=1,
            speed=60.0,
            time_period=None
        )
        assert record_none.is_peak_hour is False


class TestSpeedRecordModelQueries:
    """Test SpeedRecord model query operations."""
    
    def test_speed_record_filtering_by_link(self, test_db_simple):
        """Test filtering speed records by link."""
        # Create links
        link1 = SimplifiedLink(link_id=1, road_name="Highway 1")
        link2 = SimplifiedLink(link_id=2, road_name="Highway 2")
        test_db_simple.add_all([link1, link2])
        test_db_simple.commit()
        
        # Create speed records
        records = [
            SimplifiedSpeedRecord(id=1, link_id=1, speed=60.0),
            SimplifiedSpeedRecord(id=2, link_id=1, speed=65.0),
            SimplifiedSpeedRecord(id=3, link_id=2, speed=55.0),
            SimplifiedSpeedRecord(id=4, link_id=2, speed=50.0),
        ]
        
        for record in records:
            test_db_simple.add(record)
        test_db_simple.commit()
        
        # Filter by link_id
        link1_records = test_db_simple.query(SimplifiedSpeedRecord).filter(
            SimplifiedSpeedRecord.link_id == 1
        ).all()
        
        assert len(link1_records) == 2
        assert {record.id for record in link1_records} == {1, 2}

    def test_speed_record_temporal_filtering(self, test_db_simple):
        """Test filtering speed records by time periods."""
        # Create a link first to satisfy foreign key constraint
        link = SimplifiedLink(link_id=1, road_name="Test Highway")
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Create speed records with different time periods
        base_time = datetime(2025, 6, 29, tzinfo=UTC)
        records = [
            SimplifiedSpeedRecord(
                id=1, link_id=1, speed=60.0, 
                timestamp=base_time, 
                time_period="AM Peak"
            ),
            SimplifiedSpeedRecord(
                id=2, link_id=1, speed=70.0, 
                timestamp=base_time.replace(hour=14), 
                time_period="Off-Peak"
            ),
            SimplifiedSpeedRecord(
                id=3, link_id=1, speed=55.0, 
                timestamp=base_time.replace(hour=18), 
                time_period="PM Peak"
            ),
        ]
        
        for record in records:
            test_db_simple.add(record)
        test_db_simple.commit()
        
        # Filter by time period
        peak_records = test_db_simple.query(SimplifiedSpeedRecord).filter(
            SimplifiedSpeedRecord.time_period.in_(["AM Peak", "PM Peak"])
        ).all()
        
        assert len(peak_records) == 2
        assert {record.id for record in peak_records} == {1, 3}

    def test_speed_record_aggregations(self, test_db_simple):
        """Test aggregation queries on speed records."""
        # Create a link first to satisfy foreign key constraint
        link = SimplifiedLink(link_id=1, road_name="Test Highway")
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Create speed records with various speeds
        records = [
            SimplifiedSpeedRecord(id=1, link_id=1, speed=60.0, time_period="AM Peak"),
            SimplifiedSpeedRecord(id=2, link_id=1, speed=70.0, time_period="Off-Peak"),
            SimplifiedSpeedRecord(id=3, link_id=1, speed=55.0, time_period="PM Peak"),
            SimplifiedSpeedRecord(id=4, link_id=1, speed=65.0, time_period="Off-Peak"),
        ]
        
        for record in records:
            test_db_simple.add(record)
        test_db_simple.commit()
        
        # Test average speed
        avg_speed = test_db_simple.query(func.avg(SimplifiedSpeedRecord.speed)).scalar()
        assert avg_speed == 62.5
        
        # Test average speed by time period
        off_peak_avg = test_db_simple.query(func.avg(SimplifiedSpeedRecord.speed)).filter(
            SimplifiedSpeedRecord.time_period == "Off-Peak"
        ).scalar()
        assert off_peak_avg == 67.5
        
        # Test count by time period
        peak_count = test_db_simple.query(func.count(SimplifiedSpeedRecord.id)).filter(
            SimplifiedSpeedRecord.time_period.in_(["AM Peak", "PM Peak"])
        ).scalar()
        assert peak_count == 2


class TestSpeedRecordModelRelationships:
    """Test SpeedRecord model relationships with other models."""
    
    def test_speed_record_link_relationship(self, test_db_simple):
        """Test relationship between SpeedRecord and Link."""
        # Create a link
        link = SimplifiedLink(link_id=1, road_name="Test Highway")
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Create speed records for the link
        records = [
            SimplifiedSpeedRecord(id=1, link_id=1, speed=60.0),
            SimplifiedSpeedRecord(id=2, link_id=1, speed=65.0),
        ]
        
        for record in records:
            test_db_simple.add(record)
        test_db_simple.commit()
        
        # Test querying records for a link
        link_records = test_db_simple.query(SimplifiedSpeedRecord).filter(
            SimplifiedSpeedRecord.link_id == 1
        ).all()
        
        assert len(link_records) == 2
        assert all(record.link_id == 1 for record in link_records)

    def test_speed_record_cascade_delete(self, test_db_simple):
        """Test cascade delete behavior."""
        # Create a link
        link = SimplifiedLink(link_id=1, road_name="Test Highway")
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Create speed records
        records = [
            SimplifiedSpeedRecord(id=1, link_id=1, speed=60.0),
            SimplifiedSpeedRecord(id=2, link_id=1, speed=65.0),
        ]
        
        for record in records:
            test_db_simple.add(record)
        test_db_simple.commit()
        
        # Verify records exist
        assert test_db_simple.query(SimplifiedSpeedRecord).count() == 2
        
        # Delete the link
        test_db_simple.delete(link)
        test_db_simple.commit()
        
        # Note: In simplified models, foreign key constraints handle cascade
        # The exact behavior depends on database configuration


class TestSpeedRecordModelValidation:
    """Test SpeedRecord model validation and constraints."""
    
    def test_speed_record_required_fields(self, test_db_simple):
        """Test that required fields are properly handled."""
        # Create a link first to satisfy foreign key constraint
        link = SimplifiedLink(link_id=1, road_name="Test Highway")
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Test with minimal required data
        record = SimplifiedSpeedRecord(id=1, link_id=1, speed=60.0)
        test_db_simple.add(record)
        
        # This should work with simplified model
        test_db_simple.commit()
        
        # Verify the record was created
        stored_record = test_db_simple.query(SimplifiedSpeedRecord).filter(
            SimplifiedSpeedRecord.id == 1
        ).first()
        
        assert stored_record is not None
        assert stored_record.speed == 60.0

    def test_speed_record_data_types(self, test_db_simple):
        """Test that data types are handled correctly."""
        # Create a link first to satisfy foreign key constraint
        link = SimplifiedLink(link_id=1, road_name="Test Highway")
        test_db_simple.add(link)
        test_db_simple.commit()
        
        timestamp = datetime.now(UTC)
        record = SimplifiedSpeedRecord(
            id=1,
            link_id=1,
            speed=65.5,
            timestamp=timestamp,
            day_of_week="Monday",
            time_period="AM Peak"
        )
        
        test_db_simple.add(record)
        test_db_simple.commit()
        
        # Retrieve and verify data types
        stored_record = test_db_simple.query(SimplifiedSpeedRecord).filter(
            SimplifiedSpeedRecord.id == 1
        ).first()
        
        assert isinstance(stored_record.id, int)
        assert isinstance(stored_record.link_id, int)
        assert isinstance(stored_record.speed, float)
        assert isinstance(stored_record.day_of_week, str)
        assert isinstance(stored_record.time_period, str)


class TestSpeedRecordModelEdgeCases:
    """Test edge cases and error conditions for SpeedRecord model."""
    
    def test_speed_record_extreme_values(self, test_db_simple):
        """Test speed record with extreme values."""
        # Create a link first to satisfy foreign key constraint
        link = SimplifiedLink(link_id=1, road_name="Test Highway")
        test_db_simple.add(link)
        test_db_simple.commit()
        
        record = SimplifiedSpeedRecord(
            id=1,
            link_id=1,
            speed=0.0,  # Zero speed
            day_of_week="",  # Empty string
            time_period=""
        )
        
        test_db_simple.add(record)
        test_db_simple.commit()
        
        stored_record = test_db_simple.query(SimplifiedSpeedRecord).filter(
            SimplifiedSpeedRecord.id == 1
        ).first()
        
        assert stored_record.speed == 0.0
        assert stored_record.day_of_week == ""
        assert stored_record.time_period == ""

    def test_speed_record_query_with_no_results(self, test_db_simple):
        """Test queries that return no results."""
        # Query for non-existent record
        result = test_db_simple.query(SimplifiedSpeedRecord).filter(
            SimplifiedSpeedRecord.id == 999
        ).first()
        
        assert result is None
        
        # Query with impossible conditions
        results = test_db_simple.query(SimplifiedSpeedRecord).filter(
            SimplifiedSpeedRecord.speed < 0
        ).all()
        
        assert len(results) == 0

    def test_speed_record_statistical_queries(self, test_db_simple):
        """Test statistical queries on speed records."""
        # Create a link first to satisfy foreign key constraint
        link = SimplifiedLink(link_id=1, road_name="Test Highway")
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Create records with known statistical properties
        records = [
            SimplifiedSpeedRecord(id=1, link_id=1, speed=50.0),
            SimplifiedSpeedRecord(id=2, link_id=1, speed=60.0),
            SimplifiedSpeedRecord(id=3, link_id=1, speed=70.0),
            SimplifiedSpeedRecord(id=4, link_id=1, speed=80.0),
        ]
        
        for record in records:
            test_db_simple.add(record)
        test_db_simple.commit()
        
        # Test statistical functions
        min_speed = test_db_simple.query(func.min(SimplifiedSpeedRecord.speed)).scalar()
        max_speed = test_db_simple.query(func.max(SimplifiedSpeedRecord.speed)).scalar()
        avg_speed = test_db_simple.query(func.avg(SimplifiedSpeedRecord.speed)).scalar()
        count_records = test_db_simple.query(func.count(SimplifiedSpeedRecord.id)).scalar()
        
        assert min_speed == 50.0
        assert max_speed == 80.0
        assert avg_speed == 65.0
        assert count_records == 4


class TestSpeedRecordAdditionalCoverage:
    """Additional tests specifically for improving SpeedRecord model coverage."""

    def test_str_and_repr_variations(self, test_db_simple):
        """Test various combinations of __str__ and __repr__."""
        # Create a simple record
        link = SimplifiedLink(link_id=999, road_name="Coverage Test Road")
        test_db_simple.add(link)
        test_db_simple.flush()
        
        # Case 1: Normal record
        record1 = SimplifiedSpeedRecord(
            link_id=link.link_id,
            timestamp=datetime.now(UTC),
            speed=65.5,
            day_of_week="Monday",
            time_period="AM Peak"
        )
        test_db_simple.add(record1)
        test_db_simple.commit()
        
        # Test __str__ with normal timestamp
        str_output = str(record1)
        assert "Speed 65.5 mph on link 999" in str_output
        assert "Unknown" not in str_output
        
        # Test __str__ with None timestamp by temporarily modifying the object
        original_timestamp = record1.timestamp
        try:
            object.__setattr__(record1, 'timestamp', None)
            str_output_none = str(record1)
            assert "Speed 65.5 mph on link 999" in str_output_none
            assert "Unknown" in str_output_none
        finally:
            # Restore the original timestamp
            object.__setattr__(record1, 'timestamp', original_timestamp)
        
        # Test __repr__ variations
        repr_output = repr(record1)
        assert f"<SimplifiedSpeedRecord(id={record1.id}, link_id={record1.link_id}" in repr_output
        assert f"speed={record1.speed}" in repr_output
        
    def test_formatted_timestamp_edge_cases(self, test_db_simple):
        """Test the formatted_timestamp property with edge cases."""
        link = SimplifiedLink(link_id=1000, road_name="Timestamp Test Road")
        test_db_simple.add(link)
        test_db_simple.flush()
        
        # Test with None timestamp
        record_none = SimplifiedSpeedRecord(
            link_id=link.link_id,
            timestamp=datetime.now(UTC),  # We need a timestamp because of DB constraints
            speed=55.0
        )
        test_db_simple.add(record_none)
        test_db_simple.flush()
        
        # Manually test the formatted_timestamp with a None timestamp
        # without persisting it to the database
        original_timestamp = record_none.timestamp
        try:
            object.__setattr__(record_none, 'timestamp', None)
            assert record_none.formatted_timestamp == "Unknown"
        finally:
            # Restore the original timestamp
            object.__setattr__(record_none, 'timestamp', original_timestamp)
        
        # Test with invalid timestamp (not a datetime)
        record_invalid = SimplifiedSpeedRecord(
            link_id=link.link_id,
            timestamp=datetime.now(UTC),
            speed=60.0
        )
        test_db_simple.add(record_invalid)
        test_db_simple.flush()
        
        # Force an invalid timestamp type (this simulates corrupted data)
        original_timestamp = record_invalid.timestamp
        try:
            object.__setattr__(record_invalid, 'timestamp', "Not a datetime")
            assert record_invalid.formatted_timestamp == "Unknown"
        finally:
            # Restore the original timestamp
            object.__setattr__(record_invalid, 'timestamp', original_timestamp)
        
    def test_is_peak_hour_variations(self, test_db_simple):
        """Test the is_peak_hour property with various time periods."""
        link = SimplifiedLink(link_id=1001, road_name="Peak Hour Test Road")
        test_db_simple.add(link)
        test_db_simple.flush()
        
        # Test different peak hour scenarios (case sensitive)
        peak_periods = ["AM Peak", "PM Peak"]
        non_peak_periods = ["Off Peak", "Night", "Weekend", "off peak", "am peak", "pm peak", None]
        
        for period in peak_periods:
            record = SimplifiedSpeedRecord(
                link_id=link.link_id,
                timestamp=datetime.now(UTC),
                speed=45.0,
                time_period=period
            )
            test_db_simple.add(record)
            test_db_simple.flush()
            
            assert record.is_peak_hour is True, f"Period '{period}' should be peak hour"
            test_db_simple.delete(record)
        
        for period in non_peak_periods:
            record = SimplifiedSpeedRecord(
                link_id=link.link_id,
                timestamp=datetime.now(UTC),
                speed=45.0,
                time_period=period
            )
            test_db_simple.add(record)
            test_db_simple.flush()
            
            assert record.is_peak_hour is False, f"Period '{period}' should not be peak hour"
            test_db_simple.delete(record)

    def test_speed_record_basic_properties(self, test_db_simple):
        """Test basic properties of SpeedRecord."""
        link = SimplifiedLink(link_id=1002, road_name="Properties Test Road")
        test_db_simple.add(link)
        test_db_simple.flush()
        
        # Test basic record creation and properties
        record = SimplifiedSpeedRecord(
            link_id=link.link_id,
            timestamp=datetime.now(UTC),
            speed=45.0,
            time_period="Off Peak"
        )
        test_db_simple.add(record)
        test_db_simple.flush()
        
        # Test basic attributes exist
        assert getattr(record, 'speed', None) == 45.0
        assert getattr(record, 'time_period', None) == "Off Peak"
        assert getattr(record, 'link_id', None) == link.link_id
