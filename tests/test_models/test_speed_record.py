"""
Tests for SpeedRecord model.
"""
import pytest
from datetime import datetime

from app.models.speed_record import SpeedRecord
from app.models.link import Link


class TestSpeedRecordModel:
    """Test SpeedRecord model functionality."""
    
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


class TestSpeedRecordDatabaseOperations:
    """Test SpeedRecord model database operations."""
    
    def test_speed_record_save_and_retrieve(self, test_db, sample_speed_record_data):
        """Test saving and retrieving speed record from database."""
        # Create a link first (foreign key requirement)
        link = Link(link_id=1, road_name="Test Road")
        test_db.add(link)
        test_db.commit()
        
        # Create speed record
        speed_record = SpeedRecord(
            link_id=sample_speed_record_data['link_id'],
            timestamp=sample_speed_record_data['timestamp'],
            speed=sample_speed_record_data['speed'],
            day_of_week=sample_speed_record_data['day_of_week'],
            time_period=sample_speed_record_data['time_period']
        )
        
        # Add to session and commit
        test_db.add(speed_record)
        test_db.commit()
        
        # Retrieve from database
        retrieved_record = test_db.query(SpeedRecord).filter(
            SpeedRecord.link_id == 1
        ).first()
        
        assert retrieved_record is not None
        assert retrieved_record.link_id == 1
        assert retrieved_record.speed == 55.5
        assert retrieved_record.day_of_week == "Monday"
        assert retrieved_record.time_period == "AM Peak"
        assert retrieved_record.timestamp == datetime(2024, 1, 1, 8, 30, 0)
    
    def test_speed_record_repr_and_str(self, test_db, sample_speed_record_data):
        """Test speed record string representations."""
        # Create link and speed record
        link = Link(link_id=1, road_name="Test Road")
        test_db.add(link)
        test_db.commit()
        
        speed_record = SpeedRecord(
            link_id=sample_speed_record_data['link_id'],
            timestamp=sample_speed_record_data['timestamp'],
            speed=sample_speed_record_data['speed']
        )
        test_db.add(speed_record)
        test_db.commit()
        
        # Test __repr__
        repr_str = repr(speed_record)
        assert "SpeedRecord" in repr_str
        assert "link_id=1" in repr_str
        assert "speed=55.5" in repr_str
        
        # Test __str__
        str_repr = str(speed_record)
        assert "Speed 55.5 mph" in str_repr
        assert "link 1" in str_repr
    
    def test_speed_record_formatted_timestamp(self, test_db, sample_speed_record_data):
        """Test formatted timestamp property."""
        link = Link(link_id=1)
        test_db.add(link)
        test_db.commit()
        
        speed_record = SpeedRecord(
            link_id=1,
            timestamp=datetime(2024, 1, 1, 8, 30, 0),
            speed=55.5
        )
        test_db.add(speed_record)
        test_db.commit()
        
        formatted = speed_record.formatted_timestamp
        assert "2024-01-01 08:30:00 UTC" == formatted
    
    def test_speed_record_is_peak_hour_property(self, test_db):
        """Test is_peak_hour property."""
        link = Link(link_id=1)
        test_db.add(link)
        test_db.commit()
        
        # Test AM Peak
        am_peak_record = SpeedRecord(
            link_id=1,
            timestamp=datetime.now(),
            speed=50.0,
            time_period="AM Peak"
        )
        test_db.add(am_peak_record)
        test_db.commit()
        
        assert am_peak_record.is_peak_hour is True
        
        # Test non-peak
        midday_record = SpeedRecord(
            link_id=1,
            timestamp=datetime.now(),
            speed=60.0,
            time_period="Midday"
        )
        test_db.add(midday_record)
        test_db.commit()
        
        assert midday_record.is_peak_hour is False
        
        # Test PM Peak
        pm_peak_record = SpeedRecord(
            link_id=1,
            timestamp=datetime.now(),
            speed=45.0,
            time_period="PM Peak"
        )
        test_db.add(pm_peak_record)
        test_db.commit()
        
        assert pm_peak_record.is_peak_hour is True
    
    def test_speed_record_link_relationship(self, test_db):
        """Test relationship between SpeedRecord and Link."""
        # Create link
        link = Link(link_id=1, road_name="Test Highway")
        test_db.add(link)
        test_db.commit()
        
        # Create speed record
        speed_record = SpeedRecord(
            link_id=1,
            timestamp=datetime.now(),
            speed=55.0
        )
        test_db.add(speed_record)
        test_db.commit()
        
        # Test relationship
        assert speed_record.link is not None
        assert speed_record.link.link_id == 1
        assert speed_record.link.road_name == "Test Highway"
    
    def test_multiple_speed_records_for_link(self, test_db, multiple_speed_records_data):
        """Test multiple speed records for the same link."""
        # Create links
        link1 = Link(link_id=1, road_name="Highway 1")
        link2 = Link(link_id=2, road_name="Highway 2")
        test_db.add(link1)
        test_db.add(link2)
        test_db.commit()
        
        # Create speed records
        for record_data in multiple_speed_records_data:
            speed_record = SpeedRecord(**record_data)
            test_db.add(speed_record)
        test_db.commit()
        
        # Query records for link 1
        link1_records = test_db.query(SpeedRecord).filter(
            SpeedRecord.link_id == 1
        ).all()
        
        assert len(link1_records) == 2
        assert all(record.link_id == 1 for record in link1_records)
        
        # Query records for link 2
        link2_records = test_db.query(SpeedRecord).filter(
            SpeedRecord.link_id == 2
        ).all()
        
        assert len(link2_records) == 1
        assert link2_records[0].link_id == 2
    
    def test_speed_record_update(self, test_db, sample_speed_record_data):
        """Test updating speed record."""
        # Create link and speed record
        link = Link(link_id=1)
        test_db.add(link)
        test_db.commit()
        
        speed_record = SpeedRecord(**sample_speed_record_data)
        test_db.add(speed_record)
        test_db.commit()
        
        # Update the record
        retrieved_record = test_db.query(SpeedRecord).filter(
            SpeedRecord.link_id == 1
        ).first()
        retrieved_record.speed = 60.0
        retrieved_record.time_period = "PM Peak"
        test_db.commit()
        
        # Verify update
        updated_record = test_db.query(SpeedRecord).filter(
            SpeedRecord.link_id == 1
        ).first()
        assert updated_record.speed == 60.0
        assert updated_record.time_period == "PM Peak"
    
    def test_speed_record_delete_cascade(self, test_db):
        """Test that deleting a link cascades to speed records."""
        # Create link with speed records
        link = Link(link_id=1, road_name="Test Road")
        test_db.add(link)
        test_db.commit()
        
        speed_records = [
            SpeedRecord(link_id=1, timestamp=datetime.now(), speed=50.0),
            SpeedRecord(link_id=1, timestamp=datetime.now(), speed=55.0),
        ]
        
        for record in speed_records:
            test_db.add(record)
        test_db.commit()
        
        # Verify records exist
        assert test_db.query(SpeedRecord).filter(SpeedRecord.link_id == 1).count() == 2
        
        # Delete the link
        test_db.delete(link)
        test_db.commit()
        
        # Verify speed records are also deleted (cascade)
        remaining_records = test_db.query(SpeedRecord).filter(SpeedRecord.link_id == 1).count()
        assert remaining_records == 0
