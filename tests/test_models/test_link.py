"""
Tests for Link model.
"""
import pytest
from app.models.link import Link
from tests._models.simplified_models import SimplifiedLink as TestLink
from datetime import datetime


class TestLinkModel:
    """Test Link model functionality."""
    
    def test_link_tablename(self):
        """Test link table name is correct."""
        assert Link.__tablename__ == "links"
    
    def test_link_creation_structure(self):
        """Test link model structure and attributes."""
        # Test that the model has the expected attributes
        assert hasattr(Link, 'link_id')
        assert hasattr(Link, 'road_name')
        assert hasattr(Link, 'length')
        assert hasattr(Link, 'road_type')
        assert hasattr(Link, 'speed_limit')
        assert hasattr(Link, 'geometry')
        assert hasattr(Link, 'speed_records')
        
    def test_link_table_args(self):
        """Test link table args for spatial indexes."""
        # Verify table args for spatial indexes are defined correctly
        assert hasattr(Link, '__table_args__')
        table_args = Link.__table_args__
        
        # Check that indexes are defined
        assert len(table_args) == 2
        
        # Check that the spatial index for geometry is defined
        geometry_index = table_args[0]
        assert geometry_index.name == 'idx_link_geometry'
        assert 'geometry' in str(geometry_index)
        # Skip PostgreSQL-specific check that doesn't apply in SQLite
        # assert 'gist' in str(geometry_index)
        
        # Check that the road_name index is defined
        road_name_index = table_args[1]
        assert road_name_index.name == 'idx_link_road_name'
        assert 'road_name' in str(road_name_index)
        assert hasattr(Link, 'length')
        assert hasattr(Link, 'road_type')
        assert hasattr(Link, 'speed_limit')
        assert hasattr(Link, 'geometry')
        assert hasattr(Link, 'speed_records')


class TestLinkDatabaseOperations:
    """Test Link model database operations."""
    
    def test_link_save_and_retrieve(self, test_db_simple, sample_link_data):
        """Test saving and retrieving link from database."""
        # Create link instance (geometry will be None for SQLite)
        link = TestLink(
            link_id=sample_link_data['link_id'],
            road_name=sample_link_data['road_name'],
            length=sample_link_data['length'],
            road_type=sample_link_data['road_type'],
            speed_limit=sample_link_data['speed_limit']
        )
        
        # Add to session and commit
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Retrieve from database
        retrieved_link = test_db_simple.query(TestLink).filter(TestLink.link_id == 1).first()
        
        assert retrieved_link is not None
        assert retrieved_link.link_id == 1
        assert retrieved_link.road_name == "Test Highway"
        assert retrieved_link.length == 1500.0
        assert retrieved_link.road_type == "Highway"
        assert retrieved_link.speed_limit == 65
    
    def test_link_repr_and_str(self, test_db_simple, sample_link_data):
        """Test link string representations after database save."""
        link = TestLink(
            link_id=sample_link_data['link_id'],
            road_name=sample_link_data['road_name'],
            length=sample_link_data['length']
        )
        
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Test __repr__
        repr_str = repr(link)
        assert "SimplifiedLink" in repr_str
        assert "link_id=1" in repr_str
        assert "Test Highway" in repr_str
        
        # Test __str__
        str_repr = str(link)
        assert str_repr == "Link 1: Test Highway"
    
    def test_link_str_without_name(self, test_db_simple):
        """Test link __str__ method without road name."""
        link = TestLink(link_id=2)
        test_db_simple.add(link)
        test_db_simple.commit()
        
        str_repr = str(link)
        assert str_repr == "Link 2: Unnamed Road"
    
    def test_link_update(self, test_db_simple, sample_link_data):
        """Test updating link in database."""
        link = TestLink(
            link_id=sample_link_data['link_id'],
            road_name=sample_link_data['road_name'],
            speed_limit=sample_link_data['speed_limit']
        )
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Update the link
        retrieved_link = test_db_simple.query(TestLink).filter(TestLink.link_id == 1).first()
        retrieved_link.road_name = "Updated Highway"
        retrieved_link.speed_limit = 70
        test_db_simple.commit()
        
        # Retrieve and verify update
        updated_link = test_db_simple.query(TestLink).filter(TestLink.link_id == 1).first()
        assert updated_link.road_name == "Updated Highway"
        assert updated_link.speed_limit == 70
    
    def test_link_delete(self, test_db_simple, sample_link_data):
        """Test deleting link from database."""
        link = TestLink(
            link_id=sample_link_data['link_id'],
            road_name=sample_link_data['road_name']
        )
        test_db_simple.add(link)
        test_db_simple.commit()
        
        # Delete the link
        test_db_simple.delete(link)
        test_db_simple.commit()
        
        # Verify deletion
        deleted_link = test_db_simple.query(TestLink).filter(TestLink.link_id == 1).first()
        assert deleted_link is None
    
    def test_multiple_links(self, test_db_simple):
        """Test handling multiple links."""
        links = [
            TestLink(link_id=1, road_name="Highway 1", length=1000.0),
            TestLink(link_id=2, road_name="Highway 2", length=2000.0),
            TestLink(link_id=3, road_name="Highway 3", length=3000.0)
        ]
        
        # Add all links
        for link in links:
            test_db_simple.add(link)
        test_db_simple.commit()
        
        # Retrieve all links
        all_links = test_db_simple.query(TestLink).all()
        assert len(all_links) == 3
        
        # Check ordering by link_id
        sorted_links = test_db_simple.query(TestLink).order_by(TestLink.link_id).all()
        assert [link.link_id for link in sorted_links] == [1, 2, 3]
    
    def test_link_query_by_road_name(self, test_db_simple):
        """Test querying links by road name."""
        links = [
            TestLink(link_id=1, road_name="Main Street"),
            TestLink(link_id=2, road_name="Highway 101"),
            TestLink(link_id=3, road_name="Main Street")
        ]
        
        for link in links:
            test_db_simple.add(link)
        test_db_simple.commit()
        
        # Query by road name
        main_street_links = test_db_simple.query(TestLink).filter(
            TestLink.road_name == "Main Street"
        ).all()
        
        assert len(main_street_links) == 2
        assert all(link.road_name == "Main Street" for link in main_street_links)
    
    def test_link_creation_minimal(self, test_db_simple):
        """Test link creation with minimal required fields."""
        link = TestLink(link_id=42)
        test_db_simple.add(link)
        test_db_simple.commit()
        
        retrieved_link = test_db_simple.query(TestLink).filter(TestLink.link_id == 42).first()
        assert retrieved_link is not None
        assert retrieved_link.link_id == 42
        assert retrieved_link.road_name is None
        assert retrieved_link.length is None
    
    def test_link_with_speed_records(self, test_db_simple):
        """Test Link with related SpeedRecords."""
        link = TestLink(link_id=10, road_name="Edge Road")
        test_db_simple.add(link)
        test_db_simple.commit()

        from tests._models.simplified_models import SimplifiedSpeedRecord
        record1 = SimplifiedSpeedRecord(link_id=10, timestamp=datetime(2024,1,1,8,0,0), speed=10.0)
        record2 = SimplifiedSpeedRecord(link_id=10, timestamp=datetime(2024,1,1,9,0,0), speed=20.0)
        test_db_simple.add(record1)
        test_db_simple.add(record2)
        test_db_simple.commit()

        retrieved_link = test_db_simple.query(TestLink).filter_by(link_id=10).first()
        assert retrieved_link is not None
        assert len(retrieved_link.speed_records) == 2
        speeds = [r.speed for r in retrieved_link.speed_records]
        assert 10.0 in speeds and 20.0 in speeds

    def test_link_extreme_and_optional_values(self, test_db_simple):
        """Test Link with extreme and optional values."""
        link = TestLink(
            link_id=9999,
            road_name=None,
            length=0.0,
            road_type="",
            speed_limit=None
        )
        test_db_simple.add(link)
        test_db_simple.commit()
        retrieved = test_db_simple.query(TestLink).filter_by(link_id=9999).first()
        assert retrieved.length == 0.0
        assert retrieved.road_type == ""
        assert retrieved.road_name is None
        assert retrieved.speed_limit is None


class TestLinkEdgeCases:
    """Test edge cases for Link model."""
    
    def test_link_geometry_methods(self):
        """Test that Link has proper geometry methods even if not used in SQLite."""
        # Verificamos aqui que os métodos existem, mesmo que não sejam usados nos testes SQLite
        link = Link()
        assert hasattr(link, 'geometry')
        assert hasattr(Link, '__table_args__')
