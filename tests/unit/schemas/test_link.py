"""
Tests for Link Pydantic schemas.
"""

import pytest
from pydantic import ValidationError

from app.schemas.link import LinkBase, LinkCreate, LinkList, LinkResponse, LinkUpdate


class TestLinkSchemas:
    """Test Link Pydantic schemas."""

    def test_link_base_creation(self):
        """Test basic LinkBase schema creation."""
        link_data = {
            "road_name": "Main Street",
            "length": 1250.5,
            "road_type": "arterial",
            "speed_limit": 35,
        }

        link = LinkBase(**link_data)

        assert link.road_name == "Main Street"
        assert link.length == 1250.5
        assert link.road_type == "arterial"
        assert link.speed_limit == 35

    def test_link_base_optional_fields(self):
        """Test LinkBase with optional fields."""
        link = LinkBase()

        assert link.road_name is None
        assert link.length is None
        assert link.road_type is None
        assert link.speed_limit is None

    def test_link_create_validation(self):
        """Test LinkCreate schema validation."""
        link_data = {
            "link_id": 12345,
            "road_name": "Test Road",
            "length": 500.0,
            "speed_limit": 25,
        }

        link = LinkCreate(**link_data)

        assert link.link_id == 12345
        assert link.road_name == "Test Road"
        assert link.length == 500.0
        assert link.speed_limit == 25

    def test_link_create_missing_required_field(self):
        """Test LinkCreate fails without required link_id."""
        # Missing required link_id should be rejected
        with pytest.raises(ValidationError, match="Field required"):
            # Using model_validate to test missing required fields
            LinkCreate.model_validate({"road_name": "Test Road"})

    def test_link_create_invalid_length(self):
        """Test LinkCreate validation with negative length."""
        # Negative length should be rejected
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            LinkCreate(link_id=12345, length=-100.0)  # Invalid negative length

    def test_link_create_invalid_speed_limit(self):
        """Test LinkCreate validation with invalid speed limit."""
        # Speed limit above 200 should be rejected
        with pytest.raises(ValidationError, match="less than or equal to 200"):
            LinkCreate(link_id=12345, speed_limit=250)  # Too high

    def test_link_response_from_attributes(self):
        """Test LinkResponse schema with from_attributes."""

        # Simulate SQLAlchemy model data
        class MockLink:
            link_id = 12345
            road_name = "Mock Road"
            length = 750.0
            road_type = "residential"
            speed_limit = 30
            geometry = None
            speed_records_count = 0

        mock_link = MockLink()
        link_response = LinkResponse.model_validate(mock_link)

        assert link_response.link_id == 12345
        assert link_response.road_name == "Mock Road"
        assert link_response.length == 750.0
        assert link_response.road_type == "residential"
        assert link_response.speed_limit == 30

    def test_link_response_with_computed_fields(self):
        """Test LinkResponse schema with computed fields."""

        # Simulate SQLAlchemy model data with computed fields
        class MockLinkWithStats:
            link_id = 54321
            road_name = "Highway 101"
            length = 2500.0
            road_type = "highway"
            speed_limit = 65
            geometry = {
                "type": "LineString",
                "coordinates": [[-81.1, 30.1], [-81.2, 30.2]],
            }
            speed_records_count = 1500

        mock_link = MockLinkWithStats()
        link_response = LinkResponse.model_validate(mock_link)

        assert link_response.link_id == 54321
        assert link_response.road_name == "Highway 101"
        assert link_response.speed_records_count == 1500
        assert link_response.geometry is not None
        assert link_response.geometry["type"] == "LineString"

    def test_link_response_minimal_data(self):
        """Test LinkResponse schema with minimal required data."""

        class MinimalMockLink:
            link_id = 99999
            road_name = None
            length = None
            road_type = None
            speed_limit = None
            geometry = None
            speed_records_count = None

        mock_link = MinimalMockLink()
        link_response = LinkResponse.model_validate(mock_link)

        assert link_response.link_id == 99999
        assert link_response.road_name is None
        assert link_response.length is None
        assert link_response.road_type is None
        assert link_response.speed_limit is None
        assert link_response.geometry is None
        assert link_response.speed_records_count is None

    def test_link_update_all_optional(self):
        """Test LinkUpdate schema with all optional fields."""
        # Should work with no fields
        link_update = LinkUpdate()
        assert link_update.road_name is None

        # Should work with some fields
        link_update = LinkUpdate(road_name="Updated Road")
        assert link_update.road_name == "Updated Road"

    def test_link_list_schema(self):
        """Test LinkList schema."""
        link_data = LinkResponse(link_id=12345, road_name="Test Road", length=500.0)

        link_list = LinkList(items=[link_data], total=1, page=1, size=10, pages=1)

        assert len(link_list.items) == 1
        assert link_list.total == 1
        assert link_list.page == 1
        assert link_list.size == 10
        assert link_list.pages == 1

    def test_link_list_validation(self):
        """Test LinkList validation rules."""
        link_data = LinkResponse(link_id=12345)

        # Valid data
        link_list = LinkList(items=[link_data], total=1, page=1, size=10, pages=1)
        assert link_list.total == 1

        # Invalid page (must be >= 1)
        with pytest.raises(ValidationError):
            LinkList(items=[link_data], total=1, page=0, size=10, pages=1)  # Invalid

        # Invalid size (must be <= 100)
        with pytest.raises(ValidationError):
            LinkList(items=[link_data], total=1, page=1, size=150, pages=1)  # Too large

    def test_link_list_empty(self):
        """Test LinkList with empty items."""
        link_list = LinkList(items=[], total=0, page=1, size=10, pages=0)

        assert len(link_list.items) == 0
        assert link_list.total == 0
        assert link_list.pages == 0

    def test_link_list_with_multiple_items(self):
        """Test LinkList with multiple items."""
        links = [
            LinkResponse(link_id=1, road_name="Road 1"),
            LinkResponse(link_id=2, road_name="Road 2"),
            LinkResponse(link_id=3, road_name="Road 3"),
        ]

        link_list = LinkList(
            items=links,
            total=100,  # More than current page
            page=1,
            size=3,
            pages=34,  # 100/3 = 33.33 -> 34 pages
        )

        assert len(link_list.items) == 3
        assert link_list.total == 100
        assert link_list.pages == 34
        assert all(isinstance(item, LinkResponse) for item in link_list.items)

    def test_geometry_field(self):
        """Test geometry field accepts dict."""
        geometry_data = {
            "type": "LineString",
            "coordinates": [[-81.3792, 30.3322], [-81.3791, 30.3325]],
        }

        link = LinkCreate(link_id=12345, geometry=geometry_data)

        assert link.geometry == geometry_data
        assert link.geometry is not None
        assert link.geometry["type"] == "LineString"

    def test_link_create_with_invalid_geometry(self):
        """Test LinkCreate with invalid geometry format."""
        # Test with invalid geometry structure
        invalid_geometry = {
            "type": "InvalidType",  # Not a valid GeoJSON type
            "coordinates": "not_a_list",
        }

        link = LinkCreate(link_id=12345, geometry=invalid_geometry)

        # Should still create the object (validation is at API level)
        assert link.geometry is not None
        assert link.geometry["type"] == "InvalidType"

    def test_link_create_boundary_values(self):
        """Test LinkCreate with boundary values."""
        # Test minimum valid values
        link_min = LinkCreate(
            link_id=1, length=0.0, speed_limit=0  # Minimum length  # Minimum speed
        )

        assert link_min.link_id == 1
        assert link_min.length == 0.0
        assert link_min.speed_limit == 0

        # Test maximum valid values
        link_max = LinkCreate(
            link_id=999999,
            length=50000.0,  # Large length
            speed_limit=200,  # Maximum speed
        )

        assert link_max.link_id == 999999
        assert link_max.length == 50000.0
        assert link_max.speed_limit == 200

    def test_link_create_edge_cases(self):
        """Test LinkCreate with edge cases."""
        # Test with zero-length string
        link = LinkCreate(link_id=12345, road_name="", road_type="")  # Empty string

        assert link.road_name == ""
        assert link.road_type == ""

        # Test with very long strings
        long_name = "A" * 1000
        link_long = LinkCreate(link_id=12345, road_name=long_name)

        assert link_long.road_name == long_name
