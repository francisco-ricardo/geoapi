"""
Test cases for SpeedRecord Pydantic schemas.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.speed_record import (
    SpeedRecordBase,
    SpeedRecordCreate,
    SpeedRecordUpdate,
    SpeedRecord,
    SpeedRecordList
)


class TestSpeedRecordSchemas:
    """Test SpeedRecord Pydantic schemas."""
    
    def test_speed_record_base_creation(self):
        """Test basic SpeedRecordBase creation."""
        timestamp = datetime.now()
        speed_record = SpeedRecordBase(
            timestamp=timestamp,
            speed_kph=45.5,
            period="morning"
        )
        
        assert speed_record.timestamp == timestamp
        assert speed_record.speed_kph == 45.5
        assert speed_record.period == "morning"
    
    def test_speed_record_base_optional_period(self):
        """Test SpeedRecordBase with optional period field."""
        timestamp = datetime.now()
        speed_record = SpeedRecordBase(
            timestamp=timestamp,
            speed_kph=60.0
        )
        
        assert speed_record.timestamp == timestamp
        assert speed_record.speed_kph == 60.0
        assert speed_record.period is None
    
    def test_speed_record_create_validation(self):
        """Test SpeedRecordCreate validation."""
        timestamp = datetime.now()
        speed_record = SpeedRecordCreate(
            link_id=12345,
            timestamp=timestamp,
            speed_kph=75.5,
            period="afternoon"
        )
        
        assert speed_record.link_id == 12345
        assert speed_record.timestamp == timestamp
        assert speed_record.speed_kph == 75.5
        assert speed_record.period == "afternoon"
    
    def test_speed_record_create_missing_required_field(self):
        """Test SpeedRecordCreate with missing required fields."""
        # Test missing link_id
        with pytest.raises(ValidationError) as exc_info:
            SpeedRecordCreate.model_validate({
                "timestamp": datetime.now(),
                "speed_kph": 50.0
            })
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('link_id',)
        assert errors[0]['type'] == 'missing'
        
        # Test missing timestamp
        with pytest.raises(ValidationError) as exc_info:
            SpeedRecordCreate.model_validate({
                "link_id": 12345,
                "speed_kph": 50.0
            })
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('timestamp',)
        assert errors[0]['type'] == 'missing'
        
        # Test missing speed_kph
        with pytest.raises(ValidationError) as exc_info:
            SpeedRecordCreate.model_validate({
                "link_id": 12345,
                "timestamp": datetime.now()
            })
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('speed_kph',)
        assert errors[0]['type'] == 'missing'
    
    def test_speed_record_create_invalid_speed(self):
        """Test SpeedRecordCreate with invalid speed values."""
        timestamp = datetime.now()
        
        # Negative speed
        with pytest.raises(ValidationError) as exc_info:
            SpeedRecordCreate(
                link_id=1,
                timestamp=timestamp,
                speed_kph=-10.0
            )
        
        errors = exc_info.value.errors()
        assert any(error['type'] == 'greater_than_equal' for error in errors)
        
        # Speed too high
        with pytest.raises(ValidationError) as exc_info:
            SpeedRecordCreate(
                link_id=1,
                timestamp=timestamp,
                speed_kph=400.0
            )
        
        errors = exc_info.value.errors()
        assert any(error['type'] == 'less_than_equal' for error in errors)
    
    def test_speed_record_create_boundary_values(self):
        """Test SpeedRecordCreate with boundary values."""
        timestamp = datetime.now()
        
        # Minimum valid speed
        speed_record = SpeedRecordCreate(
            link_id=1,
            timestamp=timestamp,
            speed_kph=0.0
        )
        assert speed_record.speed_kph == 0.0
        
        # Maximum valid speed
        speed_record = SpeedRecordCreate(
            link_id=1,
            timestamp=timestamp,
            speed_kph=300.0
        )
        assert speed_record.speed_kph == 300.0
    
    def test_speed_record_create_string_timestamp(self):
        """Test SpeedRecordCreate with string timestamp conversion."""
        timestamp_str = "2024-01-15T14:30:00Z"
        speed_record = SpeedRecordCreate(
            link_id=1,
            timestamp=timestamp_str,  # type: ignore  # Testando conversão Pydantic
            speed_kph=60.0
        )
        
        assert isinstance(speed_record.timestamp, datetime)
        assert speed_record.timestamp.year == 2024
        assert speed_record.timestamp.month == 1
        assert speed_record.timestamp.day == 15
    
    def test_speed_record_update_all_optional(self):
        """Test SpeedRecordUpdate with all optional fields."""
        # Can be created with no fields
        speed_record = SpeedRecordUpdate()
        assert speed_record.timestamp is None
        assert speed_record.speed_kph is None
        assert speed_record.period is None
        
        # Can be created with some fields
        timestamp = datetime.now()
        speed_record = SpeedRecordUpdate(
            speed_kph=80.0,
            period="evening"
        )
        assert speed_record.speed_kph == 80.0
        assert speed_record.period == "evening"
        assert speed_record.timestamp is None
    
    def test_speed_record_response_schema(self):
        """Test SpeedRecord response schema."""
        timestamp = datetime.now()
        speed_record = SpeedRecord(
            id=1,
            link_id=12345,
            timestamp=timestamp,
            speed_kph=55.0,
            period="morning"
        )
        
        assert speed_record.id == 1
        assert speed_record.link_id == 12345
        assert speed_record.timestamp == timestamp
        assert speed_record.speed_kph == 55.0
        assert speed_record.period == "morning"
    
    def test_speed_record_list_schema(self):
        """Test SpeedRecordList schema."""
        timestamp = datetime.now()
        speed_records = [
            SpeedRecord(
                id=i,
                link_id=12345,
                timestamp=timestamp,
                speed_kph=50.0 + i,
                period="morning"
            )
            for i in range(1, 4)
        ]
        
        speed_record_list = SpeedRecordList(
            items=speed_records,
            total=25,
            page=1,
            size=3,
            pages=9
        )
        
        assert len(speed_record_list.items) == 3
        assert speed_record_list.total == 25
        assert speed_record_list.page == 1
        assert speed_record_list.size == 3
        assert speed_record_list.pages == 9
        
        # Check first item
        first_record = speed_record_list.items[0]
        assert first_record.id == 1
        assert first_record.speed_kph == 51.0
    
    def test_speed_record_list_validation(self):
        """Test SpeedRecordList validation."""
        # Invalid page number
        with pytest.raises(ValidationError) as exc_info:
            SpeedRecordList(
                items=[],
                total=0,
                page=0,  # Must be >= 1
                size=10,
                pages=0
            )
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('page',) and error['type'] == 'greater_than_equal' for error in errors)
        
        # Invalid size
        with pytest.raises(ValidationError) as exc_info:
            SpeedRecordList(
                items=[],
                total=0,
                page=1,
                size=0,  # Must be >= 1
                pages=0
            )
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('size',) and error['type'] == 'greater_than_equal' for error in errors)
        
        # Size too large
        with pytest.raises(ValidationError) as exc_info:
            SpeedRecordList(
                items=[],
                total=0,
                page=1,
                size=200,  # Must be <= 100
                pages=0
            )
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('size',) and error['type'] == 'less_than_equal' for error in errors)
    
    def test_speed_record_list_empty(self):
        """Test SpeedRecordList with empty items."""
        speed_record_list = SpeedRecordList(
            items=[],
            total=0,
            page=1,
            size=10,
            pages=0
        )
        
        assert len(speed_record_list.items) == 0
        assert speed_record_list.total == 0
        assert speed_record_list.pages == 0
    
    def test_speed_record_serialization(self):
        """Test SpeedRecord serialization to JSON."""
        timestamp = datetime.now()
        speed_record = SpeedRecordCreate(
            link_id=12345,
            timestamp=timestamp,
            speed_kph=65.5,
            period="afternoon"
        )
        
        # Test dict serialization
        data = speed_record.model_dump()
        assert data['link_id'] == 12345
        assert data['speed_kph'] == 65.5
        assert data['period'] == "afternoon"
        assert isinstance(data['timestamp'], datetime)
        
        # Test JSON serialization
        json_str = speed_record.model_dump_json()
        assert '"link_id":12345' in json_str
        assert '"speed_kph":65.5' in json_str
        assert '"period":"afternoon"' in json_str
    
    def test_speed_record_type_conversion(self):
        """Test automatic type conversion in SpeedRecord schemas."""
        # String to int conversion for link_id
        speed_record = SpeedRecordCreate(
            link_id="12345",  # type: ignore  # Testando conversão Pydantic
            timestamp=datetime.now(),
            speed_kph="75.5"  # type: ignore  # Testando conversão Pydantic
        )
        
        assert isinstance(speed_record.link_id, int)
        assert speed_record.link_id == 12345
        assert isinstance(speed_record.speed_kph, float)
        assert speed_record.speed_kph == 75.5
    
    def test_speed_record_edge_cases(self):
        """Test SpeedRecord edge cases."""
        # Very precise speed
        speed_record = SpeedRecordCreate(
            link_id=1,
            timestamp=datetime.now(),
            speed_kph=123.456789
        )
        assert speed_record.speed_kph == 123.456789
        
        # Zero speed (valid)
        speed_record = SpeedRecordCreate(
            link_id=1,
            timestamp=datetime.now(),
            speed_kph=0.0
        )
        assert speed_record.speed_kph == 0.0
        
        # Maximum speed (valid)
        speed_record = SpeedRecordCreate(
            link_id=1,
            timestamp=datetime.now(),
            speed_kph=300.0
        )
        assert speed_record.speed_kph == 300.0
