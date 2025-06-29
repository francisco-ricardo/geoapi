"""
Simplified tests for Link model without PostGIS dependencies.
"""
import pytest
from datetime import datetime
from tests._models.simplified_models import SimplifiedLink, SimplifiedSpeedRecord


class TestSimplifiedLinkModel:
    """Test simplified Link model functionality."""
    
    def test_link_creation(self, test_db_simple):
        """Test basic link creation without geometry."""
        link = SimplifiedLink(
            link_id=1,
            road_name="Test Highway",
            length=1500.0,
            road_type="Highway",
            speed_limit=65
        )
        
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Verify the link was saved
        saved_link = test_db_simple.query(SimplifiedLink).filter_by(link_id=1).first()
        assert saved_link is not None
        assert saved_link.link_id == 1
        assert saved_link.road_name == "Test Highway"
        assert saved_link.length == 1500.0
        assert saved_link.road_type == "Highway"
        assert saved_link.speed_limit == 65
    
    def test_link_repr_and_str(self, test_db_simple):
        """Test link string representations."""
        link = SimplifiedLink(
            link_id=2,
            road_name="Main Street"
        )
        
        # Test representations
        repr_str = repr(link)
        str_repr = str(link)
        
        assert "SimplifiedLink" in repr_str
        assert "link_id=2" in repr_str
        assert "Main Street" in repr_str
        
        assert "Link 2:" in str_repr
        assert "Main Street" in str_repr
    
    def test_link_str_without_name(self):
        """Test link without road name."""
        link = SimplifiedLink(link_id=3)
        
        str_repr = str(link)
        assert "Unnamed Road" in str_repr
    
    def test_link_query_by_road_name(self, test_db_simple):
        """Test querying links by road name."""
        # Create multiple links
        link1 = SimplifiedLink(link_id=1, road_name="Highway 1")
        link2 = SimplifiedLink(link_id=2, road_name="Highway 2") 
        link3 = SimplifiedLink(link_id=3, road_name="Main Street")
        
        test_db_simple.add_all([link1, link2, link3])
        test_db_simple.commit()
        
        # Query by road name
        highway_links = test_db_simple.query(SimplifiedLink).filter(
            SimplifiedLink.road_name.like("Highway%")
        ).all()
        
        assert len(highway_links) == 2
        assert highway_links[0].road_name.startswith("Highway")
        assert highway_links[1].road_name.startswith("Highway")
    
    def test_link_relationship_with_speed_records(self, test_db_simple):
        """Test relationship between link and speed records."""
        # Create a link
        link = SimplifiedLink(
            link_id=1,
            road_name="Test Road"
        )
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Create speed records for the link
        speed1 = SimplifiedSpeedRecord(
            link_id=1,
            timestamp=datetime(2024, 1, 1, 8, 0, 0),
            speed=55.5,
            day_of_week="Monday",
            time_period="AM Peak"
        )
        
        speed2 = SimplifiedSpeedRecord(
            link_id=1,
            timestamp=datetime(2024, 1, 1, 17, 0, 0),
            speed=45.2,
            day_of_week="Monday", 
            time_period="PM Peak"
        )
        
        test_db_simple.add_all([speed1, speed2])
        test_db_simple.commit()
        
        # Test relationship
        saved_link = test_db_simple.query(SimplifiedLink).filter_by(link_id=1).first()
        speed_records = list(saved_link.speed_records)
        
        assert len(speed_records) == 2
        assert all(record.link_id == 1 for record in speed_records)
    
    def test_link_delete_cascade(self, test_db_simple):
        """Test that deleting a link cascades to speed records."""
        # Create link with speed records
        link = SimplifiedLink(link_id=1, road_name="Test Road")
        test_db_simple.add(link)
        test_db_simple.commit()
        
        speed = SimplifiedSpeedRecord(
            link_id=1,
            timestamp=datetime(2024, 1, 1, 8, 0, 0),
            speed=55.5
        )
        test_db_simple.add(speed)
        test_db_simple.commit()
        
        # Verify records exist
        assert test_db_simple.query(SimplifiedLink).count() == 1
        assert test_db_simple.query(SimplifiedSpeedRecord).count() == 1
        
        # Delete link
        test_db_simple.delete(link)
        test_db_simple.commit()
        
        # Verify cascade delete
        assert test_db_simple.query(SimplifiedLink).count() == 0
        assert test_db_simple.query(SimplifiedSpeedRecord).count() == 0


class TestSimplifiedSpeedRecordModel:
    """Test simplified SpeedRecord model functionality."""
    
    def test_speed_record_creation(self, test_db_simple):
        """Test basic speed record creation."""
        # Create a link first
        link = SimplifiedLink(link_id=1, road_name="Test Road")
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Create speed record
        speed_record = SimplifiedSpeedRecord(
            link_id=1,
            timestamp=datetime(2024, 1, 1, 8, 30, 0),
            speed=55.5,
            day_of_week="Monday",
            time_period="AM Peak"
        )
        
        test_db_simple.add(speed_record)
        test_db_simple.commit()
        
        # Verify the record was saved
        saved_record = test_db_simple.query(SimplifiedSpeedRecord).first()
        assert saved_record is not None
        assert saved_record.link_id == 1
        assert saved_record.speed == 55.5
        assert saved_record.day_of_week == "Monday"
        assert saved_record.time_period == "AM Peak"
    
    def test_speed_record_properties(self):
        """Test speed record properties."""
        speed_record = SimplifiedSpeedRecord(
            link_id=1,
            timestamp=datetime(2024, 1, 1, 8, 30, 0),
            speed=55.5,
            time_period="AM Peak"
        )
        
        # Test is_peak_hour property
        assert speed_record.is_peak_hour is True
        
        # Test formatted_timestamp property
        formatted = speed_record.formatted_timestamp
        assert "2024-01-01 08:30:00 UTC" == formatted
        
        # Test non-peak hour
        speed_record = SimplifiedSpeedRecord(
            link_id=1,
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            speed=55.5,
            time_period="Midday"
        )
        assert speed_record.is_peak_hour is False
    
    def test_speed_record_repr_and_str(self):
        """Test speed record string representations.""" 
        speed_record = SimplifiedSpeedRecord(
            id=1,
            link_id=1,
            timestamp=datetime(2024, 1, 1, 8, 30, 0),
            speed=55.5
        )
        
        repr_str = repr(speed_record)
        str_repr = str(speed_record)
        
        assert "SimplifiedSpeedRecord" in repr_str
        assert "id=1" in repr_str
        assert "link_id=1" in repr_str
        assert "speed=55.5" in repr_str
        
        assert "Speed 55.5 mph" in str_repr
        assert "link 1" in str_repr
