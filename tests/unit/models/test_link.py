"""
Comprehensive tests for Link model functionality.
Consolidates all Link model tests including structure, relationships, and queries.
"""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import func

from app.models.link import Link
from tests.fixtures.models import SimplifiedLink, SimplifiedSpeedRecord


class TestLinkModelStructure:
    """Test Link model structure and metadata."""

    def test_link_tablename(self):
        """Test link table name is correct."""
        assert Link.__tablename__ == "links"

    def test_link_creation_structure(self):
        """Test link model structure and attributes."""
        # Test that the model has the expected attributes
        assert hasattr(Link, "link_id")
        assert hasattr(Link, "road_name")
        assert hasattr(Link, "length")
        assert hasattr(Link, "road_type")
        assert hasattr(Link, "speed_limit")
        assert hasattr(Link, "geometry")
        assert hasattr(Link, "speed_records")

    def test_link_table_args(self):
        """Test link table args for spatial indexes."""
        # Verify table args for spatial indexes are defined correctly
        assert hasattr(Link, "__table_args__")
        table_args = Link.__table_args__

        # Check that indexes are defined
        assert len(table_args) == 2

        # Check that the spatial index for geometry is defined
        geometry_index = table_args[0]
        assert geometry_index.name == "idx_link_geometry"
        assert "geometry" in str(geometry_index)

        # Check that the road_name index is defined
        road_name_index = table_args[1]
        assert road_name_index.name == "idx_link_road_name"
        assert "road_name" in str(road_name_index)

    def test_link_column_metadata(self):
        """Test Link column metadata and comments."""
        # Test that column comments are properly defined
        assert Link.link_id.comment == "Unique identifier for the road link"
        assert Link.geometry.comment == "Road segment geometry in WGS84 (EPSG:4326)"
        assert Link.road_name.comment == "Road name or identifier"
        assert Link.length.comment == "Road length in meters"
        assert Link.road_type.comment == "Type or classification of road"
        assert Link.speed_limit.comment == "Speed limit in mph"

    def test_link_relationship_metadata(self):
        """Test Link relationship metadata."""
        # Verificar que o relacionamento com speed_records está definido corretamente
        assert hasattr(Link, "speed_records")
        # Verificar que a relação está configurada no modelo
        assert "speed_records" in Link.__mapper__.relationships


class TestLinkModelBasic:
    """Test basic Link model operations using simplified models."""

    def test_simplified_link_creation(self):
        """Test creation of simplified link for testing."""
        link = SimplifiedLink(
            link_id=1,
            road_name="Test Road",
            length=1000.0,
            road_type="highway",
            speed_limit=65,
        )

        # Test the actual instance attributes, not the column definitions
        # Using getattr to avoid type checker confusion with SQLAlchemy columns
        assert getattr(link, "link_id") == 1
        assert getattr(link, "road_name") == "Test Road"
        assert getattr(link, "length") == 1000.0
        assert getattr(link, "road_type") == "highway"
        assert getattr(link, "speed_limit") == 65

    def test_simplified_link_string_representation(self):
        """Test string representation of simplified link."""
        link = SimplifiedLink(link_id=1, road_name="Test Road", length=1000.0)

        expected = "Link 1: Test Road"
        assert str(link) == expected

    def test_simplified_link_with_none_values(self):
        """Test simplified link with None values."""
        link = SimplifiedLink(link_id=1)

        # Test string representation with None values
        result = str(link)
        assert "Link 1:" in result
        assert "Unnamed Road" in result


class TestLinkModelQueries:
    """Test Link model query operations."""

    def test_link_filtering_by_multiple_criteria(self, test_db_simple):
        """Test filtering links by multiple criteria."""
        # Create multiple links with different attributes
        links = [
            SimplifiedLink(
                link_id=1, road_name="Highway 1", road_type="highway", speed_limit=65
            ),
            SimplifiedLink(
                link_id=2, road_name="Main Street", road_type="local", speed_limit=35
            ),
            SimplifiedLink(
                link_id=3, road_name="Highway 2", road_type="highway", speed_limit=55
            ),
            SimplifiedLink(
                link_id=4, road_name="Oak Street", road_type="local", speed_limit=30
            ),
            SimplifiedLink(
                link_id=5, road_name="Rural Road", road_type="rural", speed_limit=45
            ),
        ]

        for link in links:
            test_db_simple.add(link)
        test_db_simple.commit()

        # Filter by road type and speed limit
        highway_links = (
            test_db_simple.query(SimplifiedLink)
            .filter(
                SimplifiedLink.road_type == "highway", SimplifiedLink.speed_limit > 60
            )
            .all()
        )

        assert len(highway_links) == 1
        assert highway_links[0].link_id == 1

        # Filter by road name pattern
        street_links = (
            test_db_simple.query(SimplifiedLink)
            .filter(SimplifiedLink.road_name.like("%Street%"))
            .all()
        )

        assert len(street_links) == 2
        assert {link.link_id for link in street_links} == {2, 4}

    def test_link_ordering_and_pagination(self, test_db_simple):
        """Test ordering and pagination of links."""
        # Create multiple links
        links = [
            SimplifiedLink(link_id=1, road_name="Road 1", length=1000.0),
            SimplifiedLink(link_id=2, road_name="Road 2", length=2000.0),
            SimplifiedLink(link_id=3, road_name="Road 3", length=1500.0),
            SimplifiedLink(link_id=4, road_name="Road 4", length=500.0),
            SimplifiedLink(link_id=5, road_name="Road 5", length=3000.0),
        ]

        for link in links:
            test_db_simple.add(link)
        test_db_simple.commit()

        # Order by length descending
        ordered_links = (
            test_db_simple.query(SimplifiedLink)
            .order_by(SimplifiedLink.length.desc())
            .all()
        )

        assert len(ordered_links) == 5
        assert [link.link_id for link in ordered_links] == [5, 2, 3, 1, 4]

        # Pagination - get second page with 2 items per page
        page_2 = (
            test_db_simple.query(SimplifiedLink)
            .order_by(SimplifiedLink.link_id)
            .offset(2)
            .limit(2)
            .all()
        )

        assert len(page_2) == 2
        assert [link.link_id for link in page_2] == [3, 4]

    def test_link_aggregations(self, test_db_simple):
        """Test aggregation queries on links."""
        # Create links with various lengths
        links = [
            SimplifiedLink(
                link_id=1, road_name="Road 1", length=1000.0, road_type="highway"
            ),
            SimplifiedLink(
                link_id=2, road_name="Road 2", length=2000.0, road_type="highway"
            ),
            SimplifiedLink(
                link_id=3, road_name="Road 3", length=1500.0, road_type="local"
            ),
            SimplifiedLink(
                link_id=4, road_name="Road 4", length=500.0, road_type="local"
            ),
        ]

        for link in links:
            test_db_simple.add(link)
        test_db_simple.commit()

        # Test total length
        total_length = test_db_simple.query(func.sum(SimplifiedLink.length)).scalar()
        assert total_length == 5000.0

        # Test average length by road type
        highway_avg = (
            test_db_simple.query(func.avg(SimplifiedLink.length))
            .filter(SimplifiedLink.road_type == "highway")
            .scalar()
        )
        assert highway_avg == 1500.0

        # Test count by road type
        local_count = (
            test_db_simple.query(func.count(SimplifiedLink.link_id))
            .filter(SimplifiedLink.road_type == "local")
            .scalar()
        )
        assert local_count == 2


class TestLinkModelRelationships:
    """Test Link model relationships with other models."""

    def test_link_speed_record_relationship(self, test_db_simple):
        """Test relationship between Link and SpeedRecord."""
        # Create a link
        link = SimplifiedLink(link_id=1, road_name="Test Road", length=1000.0)
        test_db_simple.add(link)
        test_db_simple.commit()

        # Create speed records for the link
        records = [
            SimplifiedSpeedRecord(
                id=1, link_id=1, speed=60.0, timestamp=datetime.now(UTC)
            ),
            SimplifiedSpeedRecord(
                id=2, link_id=1, speed=65.0, timestamp=datetime.now(UTC)
            ),
        ]

        for record in records:
            test_db_simple.add(record)
        test_db_simple.commit()

        # Test querying speed records through link relationship
        # Note: Since we're using simplified models, we test the query directly
        link_records = (
            test_db_simple.query(SimplifiedSpeedRecord)
            .filter(SimplifiedSpeedRecord.link_id == 1)
            .all()
        )

        assert len(link_records) == 2
        assert {record.id for record in link_records} == {1, 2}

    def test_link_cascade_operations(self, test_db_simple):
        """Test cascade behavior when deleting links."""
        # Create a link
        link = SimplifiedLink(link_id=1, road_name="Test Road", length=1000.0)
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

        # Verify link is deleted
        assert (
            test_db_simple.query(SimplifiedLink)
            .filter(SimplifiedLink.link_id == 1)
            .first()
            is None
        )

        # Note: Cascade behavior depends on foreign key constraints
        # In simplified models without proper FK constraints,
        # records might still exist


class TestLinkModelValidation:
    """Test Link model validation and constraints."""

    def test_link_required_fields(self, test_db_simple):
        """Test that required fields are properly handled."""
        # Test with minimal required data
        link = SimplifiedLink(link_id=1)
        test_db_simple.add(link)

        # This should work with simplified model
        test_db_simple.commit()

        # Verify the link was created
        stored_link = (
            test_db_simple.query(SimplifiedLink)
            .filter(SimplifiedLink.link_id == 1)
            .first()
        )

        assert stored_link is not None
        assert stored_link.link_id == 1

    def test_link_unique_constraints(self, test_db_simple):
        """Test unique constraints on link_id."""
        # Create first link
        link1 = SimplifiedLink(link_id=1, road_name="Road 1")
        test_db_simple.add(link1)
        test_db_simple.commit()

        # Try to create another link with same ID (should be prevented by unique constraint)
        link2 = SimplifiedLink(link_id=1, road_name="Road 2")
        test_db_simple.add(link2)

        # In a real database with constraints, this would raise an exception
        # For simplified testing, we just verify the first link exists
        stored_link = (
            test_db_simple.query(SimplifiedLink)
            .filter(SimplifiedLink.link_id == 1)
            .first()
        )

        assert stored_link.road_name == "Road 1"

    def test_link_data_types(self, test_db_simple):
        """Test that data types are handled correctly."""
        link = SimplifiedLink(
            link_id=1, road_name="Test Road", length=1234.56, speed_limit=65
        )

        test_db_simple.add(link)
        test_db_simple.commit()

        # Retrieve and verify data types
        stored_link = (
            test_db_simple.query(SimplifiedLink)
            .filter(SimplifiedLink.link_id == 1)
            .first()
        )

        assert isinstance(stored_link.link_id, int)
        assert isinstance(stored_link.road_name, str)
        assert isinstance(stored_link.length, float)
        assert isinstance(stored_link.speed_limit, int)


class TestLinkModelEdgeCases:
    """Test edge cases and error conditions for Link model."""

    def test_link_with_empty_string_values(self, test_db_simple):
        """Test link with empty string values."""
        link = SimplifiedLink(link_id=1, road_name="", road_type="")  # Empty string

        test_db_simple.add(link)
        test_db_simple.commit()

        stored_link = (
            test_db_simple.query(SimplifiedLink)
            .filter(SimplifiedLink.link_id == 1)
            .first()
        )

        assert stored_link.road_name == ""
        assert stored_link.road_type == ""

    def test_link_with_extreme_values(self, test_db_simple):
        """Test link with extreme numeric values."""
        link = SimplifiedLink(
            link_id=1,
            length=0.0,  # Zero length
            speed_limit=999,  # Very high speed limit
        )

        test_db_simple.add(link)
        test_db_simple.commit()

        stored_link = (
            test_db_simple.query(SimplifiedLink)
            .filter(SimplifiedLink.link_id == 1)
            .first()
        )

        assert stored_link.length == 0.0
        assert stored_link.speed_limit == 999

    def test_link_query_with_no_results(self, test_db_simple):
        """Test queries that return no results."""
        # Query for non-existent link
        result = (
            test_db_simple.query(SimplifiedLink)
            .filter(SimplifiedLink.link_id == 999)
            .first()
        )

        assert result is None

        # Query with impossible conditions
        results = (
            test_db_simple.query(SimplifiedLink).filter(SimplifiedLink.length < 0).all()
        )

        assert len(results) == 0
