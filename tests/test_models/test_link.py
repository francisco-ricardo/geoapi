"""
Tests for Link model.
"""
import pytest
from app.models.link import Link


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


class TestLinkDatabaseOperations:
    """Test Link model database operations."""
    
    def test_link_save_and_retrieve(self, test_db, sample_link_data):
        """Test saving and retrieving link from database."""
        # Create link instance (geometry will be None for SQLite)
        link = Link(
            link_id=sample_link_data['link_id'],
            road_name=sample_link_data['road_name'],
            length=sample_link_data['length'],
            road_type=sample_link_data['road_type'],
            speed_limit=sample_link_data['speed_limit']
        )
        
        # Add to session and commit
        test_db.add(link)
        test_db.commit()
        
        # Retrieve from database
        retrieved_link = test_db.query(Link).filter(Link.link_id == 1).first()
        
        assert retrieved_link is not None
        assert retrieved_link.link_id == 1
        assert retrieved_link.road_name == "Test Highway"
        assert retrieved_link.length == 1500.0
        assert retrieved_link.road_type == "Highway"
        assert retrieved_link.speed_limit == 65
    
    def test_link_repr_and_str(self, test_db, sample_link_data):
        """Test link string representations after database save."""
        link = Link(
            link_id=sample_link_data['link_id'],
            road_name=sample_link_data['road_name'],
            length=sample_link_data['length']
        )
        
        test_db.add(link)
        test_db.commit()
        
        # Test __repr__
        repr_str = repr(link)
        assert "Link" in repr_str
        assert "link_id=1" in repr_str
        assert "Test Highway" in repr_str
        
        # Test __str__
        str_repr = str(link)
        assert str_repr == "Link 1: Test Highway"
    
    def test_link_str_without_name(self, test_db):
        """Test link __str__ method without road name."""
        link = Link(link_id=2)
        test_db.add(link)
        test_db.commit()
        
        str_repr = str(link)
        assert str_repr == "Link 2: Unnamed Road"
    
    def test_link_update(self, test_db, sample_link_data):
        """Test updating link in database."""
        link = Link(
            link_id=sample_link_data['link_id'],
            road_name=sample_link_data['road_name'],
            speed_limit=sample_link_data['speed_limit']
        )
        test_db.add(link)
        test_db.commit()
        
        # Update the link
        retrieved_link = test_db.query(Link).filter(Link.link_id == 1).first()
        retrieved_link.road_name = "Updated Highway"
        retrieved_link.speed_limit = 70
        test_db.commit()
        
        # Retrieve and verify update
        updated_link = test_db.query(Link).filter(Link.link_id == 1).first()
        assert updated_link.road_name == "Updated Highway"
        assert updated_link.speed_limit == 70
    
    def test_link_delete(self, test_db, sample_link_data):
        """Test deleting link from database."""
        link = Link(
            link_id=sample_link_data['link_id'],
            road_name=sample_link_data['road_name']
        )
        test_db.add(link)
        test_db.commit()
        
        # Delete the link
        test_db.delete(link)
        test_db.commit()
        
        # Verify deletion
        deleted_link = test_db.query(Link).filter(Link.link_id == 1).first()
        assert deleted_link is None
    
    def test_multiple_links(self, test_db):
        """Test handling multiple links."""
        links = [
            Link(link_id=1, road_name="Highway 1", length=1000.0),
            Link(link_id=2, road_name="Highway 2", length=2000.0),
            Link(link_id=3, road_name="Highway 3", length=3000.0)
        ]
        
        # Add all links
        for link in links:
            test_db.add(link)
        test_db.commit()
        
        # Retrieve all links
        all_links = test_db.query(Link).all()
        assert len(all_links) == 3
        
        # Check ordering by link_id
        sorted_links = test_db.query(Link).order_by(Link.link_id).all()
        assert [link.link_id for link in sorted_links] == [1, 2, 3]
    
    def test_link_query_by_road_name(self, test_db):
        """Test querying links by road name."""
        links = [
            Link(link_id=1, road_name="Main Street"),
            Link(link_id=2, road_name="Highway 101"),
            Link(link_id=3, road_name="Main Street")
        ]
        
        for link in links:
            test_db.add(link)
        test_db.commit()
        
        # Query by road name
        main_street_links = test_db.query(Link).filter(
            Link.road_name == "Main Street"
        ).all()
        
        assert len(main_street_links) == 2
        assert all(link.road_name == "Main Street" for link in main_street_links)
    
    def test_link_creation_minimal(self, test_db):
        """Test link creation with minimal required fields."""
        link = Link(link_id=42)
        test_db.add(link)
        test_db.commit()
        
        retrieved_link = test_db.query(Link).filter(Link.link_id == 42).first()
        assert retrieved_link is not None
        assert retrieved_link.link_id == 42
        assert retrieved_link.road_name is None
        assert retrieved_link.length is None
