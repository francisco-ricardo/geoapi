"""
Tests for SpeedRecord model using simplified models for SQLite testing.
"""
import pytest
from datetime import datetime

from app.models.speed_record import SpeedRecord
from tests._models.simplified_models import SimplifiedSpeedRecord as TestSpeedRecord
from tests._models.simplified_models import SimplifiedLink as TestLink


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
    """Test SpeedRecord model database operations using simplified models."""
    
    def test_speed_record_save_and_retrieve(self, test_db_simple, sample_speed_record_data):
        """Test saving and retrieving speed record from database."""
        # Create a link first (foreign key requirement)
        link = TestLink(link_id=1, road_name="Test Road")
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Create speed record
        speed_record = TestSpeedRecord(
            link_id=sample_speed_record_data['link_id'],
            timestamp=sample_speed_record_data['timestamp'],
            speed=sample_speed_record_data['speed'],
            day_of_week=sample_speed_record_data['day_of_week'],
            time_period=sample_speed_record_data['time_period']
        )
        
        # Add to session and commit
        test_db_simple.add(speed_record)
        test_db_simple.commit()
        
        # Retrieve from database
        retrieved_record = test_db_simple.query(TestSpeedRecord).filter(
            TestSpeedRecord.link_id == 1
        ).first()
        
        assert retrieved_record is not None
        assert retrieved_record.link_id == 1
        assert retrieved_record.speed == 55.5
        assert retrieved_record.day_of_week == "Monday"
        assert retrieved_record.time_period == "AM Peak"
        assert retrieved_record.timestamp == datetime(2024, 1, 1, 8, 30, 0)
    
    def test_speed_record_repr_and_str(self, test_db_simple, sample_speed_record_data):
        """Test speed record string representations."""
        # Create link and speed record
        link = TestLink(link_id=1, road_name="Test Road")
        test_db_simple.add(link)
        test_db_simple.commit()
        
        speed_record = TestSpeedRecord(
            link_id=sample_speed_record_data['link_id'],
            timestamp=sample_speed_record_data['timestamp'],
            speed=sample_speed_record_data['speed']
        )
        test_db_simple.add(speed_record)
        test_db_simple.commit()
        
        # Test __repr__
        repr_str = repr(speed_record)
        assert "SimplifiedSpeedRecord" in repr_str
        assert "link_id=1" in repr_str
        assert "speed=55.5" in repr_str
        
        # Test __str__
        str_repr = str(speed_record)
        assert "Speed 55.5 mph" in str_repr
        assert "link 1" in str_repr
    
    def test_speed_record_formatted_timestamp(self, test_db_simple, sample_speed_record_data):
        """Test formatted timestamp property."""
        link = TestLink(link_id=1)
        test_db_simple.add(link)
        test_db_simple.commit()
        
        speed_record = TestSpeedRecord(
            link_id=1,
            timestamp=datetime(2024, 1, 1, 8, 30, 0),
            speed=55.5
        )
        test_db_simple.add(speed_record)
        test_db_simple.commit()
        
        formatted = speed_record.formatted_timestamp
        assert "2024-01-01 08:30:00 UTC" == formatted
    
    def test_speed_record_is_peak_hour_property(self, test_db_simple):
        """Test is_peak_hour property."""
        link = TestLink(link_id=1)
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Test AM Peak
        am_peak_record = TestSpeedRecord(
            link_id=1,
            timestamp=datetime.now(),
            speed=50.0,
            time_period="AM Peak"
        )
        test_db_simple.add(am_peak_record)
        test_db_simple.commit()
        
        assert am_peak_record.is_peak_hour is True
        
        # Test non-peak
        midday_record = TestSpeedRecord(
            link_id=1,
            timestamp=datetime.now(),
            speed=60.0,
            time_period="Midday"
        )
        test_db_simple.add(midday_record)
        test_db_simple.commit()
        
        assert midday_record.is_peak_hour is False
        
        # Test PM Peak
        pm_peak_record = TestSpeedRecord(
            link_id=1,
            timestamp=datetime.now(),
            speed=45.0,
            time_period="PM Peak"
        )
        test_db_simple.add(pm_peak_record)
        test_db_simple.commit()
        
        assert pm_peak_record.is_peak_hour is True
    
    def test_speed_record_link_relationship(self, test_db_simple):
        """Test relationship between SpeedRecord and Link."""
        # Create link
        link = TestLink(link_id=1, road_name="Test Highway")
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Create speed record
        speed_record = TestSpeedRecord(
            link_id=1,
            timestamp=datetime.now(),
            speed=55.0
        )
        test_db_simple.add(speed_record)
        test_db_simple.commit()
        
        # Test relationship
        assert speed_record.link is not None
        assert speed_record.link.link_id == 1
        assert speed_record.link.road_name == "Test Highway"
    
    def test_multiple_speed_records_for_link(self, test_db_simple, multiple_speed_records_data):
        """Test multiple speed records for the same link."""
        # Create links
        link1 = TestLink(link_id=1, road_name="Highway 1")
        link2 = TestLink(link_id=2, road_name="Highway 2")
        test_db_simple.add(link1)
        test_db_simple.add(link2)
        test_db_simple.commit()
        
        # Create speed records
        for record_data in multiple_speed_records_data:
            speed_record = TestSpeedRecord(**record_data)
            test_db_simple.add(speed_record)
        test_db_simple.commit()
        
        # Query records for link 1
        link1_records = test_db_simple.query(TestSpeedRecord).filter(
            TestSpeedRecord.link_id == 1
        ).all()
        
        assert len(link1_records) == 2
        assert all(record.link_id == 1 for record in link1_records)
        
        # Query records for link 2
        link2_records = test_db_simple.query(TestSpeedRecord).filter(
            TestSpeedRecord.link_id == 2
        ).all()
        
        assert len(link2_records) == 1
        assert link2_records[0].link_id == 2
    
    def test_speed_record_update(self, test_db_simple, sample_speed_record_data):
        """Test updating speed record."""
        # Create link and speed record
        link = TestLink(link_id=1)
        test_db_simple.add(link)
        test_db_simple.commit()
        
        speed_record = TestSpeedRecord(**sample_speed_record_data)
        test_db_simple.add(speed_record)
        test_db_simple.commit()
        
        # Update the record
        retrieved_record = test_db_simple.query(TestSpeedRecord).filter(
            TestSpeedRecord.link_id == 1
        ).first()
        retrieved_record.speed = 60.0
        retrieved_record.time_period = "PM Peak"
        test_db_simple.commit()
        
        # Verify update
        updated_record = test_db_simple.query(TestSpeedRecord).filter(
            TestSpeedRecord.link_id == 1
        ).first()
        assert updated_record.speed == 60.0
        assert updated_record.time_period == "PM Peak"
    
    def test_speed_record_delete_cascade(self, test_db_simple):
        """Test that deleting a link cascades to speed records."""
        # Create link with speed records
        link = TestLink(link_id=1, road_name="Test Road")
        test_db_simple.add(link)
        test_db_simple.commit()
        
        speed_records = [
            TestSpeedRecord(link_id=1, timestamp=datetime.now(), speed=50.0),
            TestSpeedRecord(link_id=1, timestamp=datetime.now(), speed=55.0),
        ]
        
        for record in speed_records:
            test_db_simple.add(record)
        test_db_simple.commit()
        
        # Verify records exist
        assert test_db_simple.query(TestSpeedRecord).filter(TestSpeedRecord.link_id == 1).count() == 2
        
        # Delete the link
        test_db_simple.delete(link)
        test_db_simple.commit()
        
        # Verify speed records are also deleted (cascade)
        remaining_records = test_db_simple.query(TestSpeedRecord).filter(TestSpeedRecord.link_id == 1).count()
        assert remaining_records == 0
    
    def test_speed_record_table_args(self):
        """Test speed record table args for indexes."""
        # Verify table args for indexes are defined correctly
        assert hasattr(SpeedRecord, '__table_args__')
        table_args = SpeedRecord.__table_args__
        
        # Check that indexes are defined
        assert len(table_args) == 4
        
        # Check specific indexes
        index_names = [idx.name for idx in table_args]
        assert 'idx_speed_link_timestamp' in index_names
        assert 'idx_speed_day_period' in index_names
        assert 'idx_speed_link_day_period' in index_names
        assert 'idx_speed_timestamp_range' in index_names
    
    def test_speed_record_repr_complete(self, test_db_simple):
        """Test the complete __repr__ method."""
        link = TestLink(link_id=99)
        test_db_simple.add(link)
        test_db_simple.commit()
        
        speed_record = TestSpeedRecord(
            id=101,
            link_id=99,
            timestamp=datetime.now(),
            speed=65.0
        )
        test_db_simple.add(speed_record)
        test_db_simple.commit()
        
        # Test __repr__
        repr_str = repr(speed_record)
        assert "SimplifiedSpeedRecord" in repr_str
        assert "id=101" in repr_str
        assert "link_id=99" in repr_str
        assert "speed=65.0" in repr_str
        assert "timestamp=" in repr_str
    
    def test_speed_record_str_with_null_timestamp(self, test_db_simple):
        """Test __str__ method with null timestamp."""
        link = TestLink(link_id=100)
        test_db_simple.add(link)
        test_db_simple.commit()

        # Crie o speed record com timestamp válido (exigido pelo banco)
        speed_record = TestSpeedRecord(
            link_id=100,
            speed=70.0,
            timestamp=datetime.now()  # Timestamp obrigatório para o banco
        )
        test_db_simple.add(speed_record)
        test_db_simple.commit()

        # Simular timestamp nulo usando patch
        from unittest.mock import patch
        with patch.object(speed_record, 'timestamp', None):
            str_repr = str(speed_record)
            assert "Speed 70.0 mph" in str_repr
            assert "link 100" in str_repr
            assert "None" in str_repr

    def test_formatted_timestamp_edge_cases(self, test_db_simple):
        """Test edge cases for formatted_timestamp property."""
        link = TestLink(link_id=101)
        test_db_simple.add(link)
        test_db_simple.commit()

        # Crie o record com timestamp válido
        record = TestSpeedRecord(
            link_id=101,
            speed=55.0,
            timestamp=datetime.now()
        )
        test_db_simple.add(record)
        test_db_simple.commit()

        # Teste o caso de timestamp válido
        assert record.formatted_timestamp is not None
        assert "UTC" in record.formatted_timestamp

        # Simular timestamp nulo usando patch
        from unittest.mock import patch
        with patch.object(record, 'timestamp', None):
            assert record.formatted_timestamp == "Unknown"

        # Simular timestamp inválido usando patch
        with patch.object(record, 'timestamp', "not-a-datetime"):
            assert record.formatted_timestamp == "Unknown"
    
    def test_is_peak_hour_with_null_time_period(self, test_db_simple):
        """Test is_peak_hour property with null or invalid time_period."""
        link = TestLink(link_id=102)
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Case 1: None time_period
        record1 = TestSpeedRecord(
            link_id=102,
            timestamp=datetime.now(),
            speed=45.0,
            time_period=None
        )
        test_db_simple.add(record1)
        
        # Case 2: Non-peak time_period
        record2 = TestSpeedRecord(
            link_id=102,
            timestamp=datetime.now(),
            speed=50.0,
            time_period="Night"
        )
        test_db_simple.add(record2)
        test_db_simple.commit()
        
        # Test the properties
        assert record1.is_peak_hour is False
        assert record2.is_peak_hour is False
    
    def test_speed_record_composite_indexes(self, test_db_simple):
        """Test composite indexes for SpeedRecord."""
        assert hasattr(SpeedRecord, '__table_args__')
        table_args = SpeedRecord.__table_args__

        # Verificar que os índices compostos estão definidos corretamente
        index_names = [idx.name for idx in table_args]
        assert 'idx_speed_link_timestamp' in index_names
        assert 'idx_speed_day_period' in index_names
        assert 'idx_speed_link_day_period' in index_names
        assert 'idx_speed_timestamp_range' in index_names

    def test_speed_record_properties(self, test_db_simple):
        """Test derived properties for SpeedRecord."""
        link = TestLink(link_id=1)
        test_db_simple.add(link)
        test_db_simple.commit()

        # Criar SpeedRecord com atributos derivados
        record = TestSpeedRecord(
            link_id=1,
            timestamp=datetime(2024, 1, 1, 8, 30, 0),
            speed=55.5,
            day_of_week="Monday",
            time_period="AM Peak"
        )
        test_db_simple.add(record)
        test_db_simple.commit()

        # Recarregar o objeto do banco para garantir que é instância
        rec = test_db_simple.query(TestSpeedRecord).filter_by(link_id=1).first()
        assert rec.day_of_week == "Monday"
        assert rec.time_period == "AM Peak"
        assert rec.is_peak_hour is True

    def test_unique_link_id_constraint(self, test_db_simple):
        """Testa constraint de unicidade de link_id em Link."""
        link1 = TestLink(link_id=123, road_name="A")
        test_db_simple.add(link1)
        test_db_simple.commit()
        
        # Criar novo objeto com mesmo ID e verificar exceção
        link2 = TestLink(link_id=123, road_name="B")
        test_db_simple.add(link2)
        
        # Usar assertRaises em vez de capturar exceção no bloco with
        # pois SQLAlchemy lança warning antes da exceção
        try:
            test_db_simple.commit()
            pytest.fail("A exceção esperada não foi lançada")
        except Exception:
            # Rollback após exceção
            test_db_simple.rollback()

    def test_foreign_key_constraint_speedrecord(self, test_db_simple):
        """Testa constraint de integridade referencial em SpeedRecord."""
        # Não cria o link
        speed_record = TestSpeedRecord(
            link_id=9999,
            timestamp=datetime.now(),
            speed=10.0
        )
        test_db_simple.add(speed_record)
        with pytest.raises(Exception):
            test_db_simple.commit()
            test_db_simple.rollback()

    def test_extreme_and_invalid_values(self, test_db_simple):
        """Testa valores extremos e inválidos nos campos de SpeedRecord."""
        link = TestLink(link_id=321, road_name="Edge")
        test_db_simple.add(link)
        test_db_simple.commit()
        # speed negativo
        record_neg = TestSpeedRecord(link_id=321, timestamp=datetime.now(), speed=-100.0)
        test_db_simple.add(record_neg)
        test_db_simple.commit()
        rec = test_db_simple.query(TestSpeedRecord).filter_by(link_id=321).first()
        assert rec.speed == -100.0
        # string longa
        long_str = "x" * 300
        record_long = TestSpeedRecord(link_id=321, timestamp=datetime.now(), speed=1.0, day_of_week=long_str, time_period=long_str)
        test_db_simple.add(record_long)
        test_db_simple.commit()
        rec_long = test_db_simple.query(TestSpeedRecord).filter_by(id=record_long.id).first()
        assert rec_long.day_of_week == long_str
        assert rec_long.time_period == long_str

    def test_cascade_delete_link_speedrecords(self, test_db_simple):
        """Testa se ao deletar um Link, os SpeedRecords relacionados são deletados."""
        link = TestLink(link_id=555, road_name="Cascade")
        test_db_simple.add(link)
        test_db_simple.commit()
        rec1 = TestSpeedRecord(link_id=555, timestamp=datetime.now(), speed=1.0)
        rec2 = TestSpeedRecord(link_id=555, timestamp=datetime.now(), speed=2.0)
        test_db_simple.add(rec1)
        test_db_simple.add(rec2)
        test_db_simple.commit()
        assert test_db_simple.query(TestSpeedRecord).filter_by(link_id=555).count() == 2
        test_db_simple.delete(link)
        test_db_simple.commit()
        assert test_db_simple.query(TestSpeedRecord).filter_by(link_id=555).count() == 0
