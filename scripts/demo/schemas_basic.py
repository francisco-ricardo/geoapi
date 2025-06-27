#!/usr/bin/env python3
"""
Interactive demonstration of Pydantic schemas.

This script shows basic usage of the Link schemas including
validation, serialization, and common patterns.
"""
import sys
import json

sys.path.insert(0, '/workspace')

from app.schemas.link import LinkBase, LinkCreate, LinkResponse, LinkList
from pydantic import ValidationError


def demo_schema_basics():
    """Demonstrate basic schema concepts."""
    print("Schema Basics Demo")
    print("=" * 50)
    
    # Basic creation
    print("\n1. Basic Creation:")
    print("LinkBase() - no data")
    link_empty = LinkBase()
    print(f"   Result: {link_empty}")
    print(f"   road_name: {link_empty.road_name}")
    print(f"   speed_limit: {link_empty.speed_limit}")
    
    # Creation with data
    print("\n2. Creation with Data:")
    print("LinkBase(road_name='Main St', speed_limit=35)")
    link_with_data = LinkBase(road_name="Main St", speed_limit=35)
    print(f"   Result: {link_with_data}")
    print(f"   road_name: {link_with_data.road_name}")
    print(f"   speed_limit: {link_with_data.speed_limit}")
    
    # JSON serialization
    print("\n3. JSON Serialization:")
    json_data = link_with_data.model_dump()
    print(f"   .model_dump(): {json_data}")
    json_string = link_with_data.model_dump_json()
    print(f"   .model_dump_json(): {json_string}")


def demo_validation():
    """Demonstrate automatic validation."""
    print("\n\nValidation Demo")
    print("=" * 50)
    
    # Type validation
    print("\n1. Type Validation:")
    try:
        print("LinkBase(speed_limit='invalid_text')")
        LinkBase(speed_limit="invalid_text")  # type: ignore
    except ValidationError as e:
        print(f"   Error: {e}")
    
    # Range validation
    print("\n2. Range Validation:")
    try:
        print("LinkBase(speed_limit=300)  # Max is 200")
        LinkBase(speed_limit=300)
    except ValidationError as e:
        print(f"   Error: {e}")
    
    try:
        print("LinkBase(length=-50)  # Must be >= 0")
        LinkBase(length=-50)
    except ValidationError as e:
        print(f"   Error: {e}")
    
    # Successful validation
    print("\n3. Successful Validation:")
    print("LinkBase(speed_limit=65, length=1500.5)")
    valid_link = LinkBase(speed_limit=65, length=1500.5)
    print(f"   Success: {valid_link}")


def demo_inheritance():
    """Demonstrate schema inheritance."""
    print("\n\nSchema Inheritance Demo")
    print("=" * 50)
    
    print("\n1. LinkCreate inherits from LinkBase:")
    print("   LinkBase: road_name, length, road_type, speed_limit")
    print("   LinkCreate: + link_id, + geometry")
    
    link_create = LinkCreate(
        link_id=12345,
        road_name="Highway 101",
        length=2500.0,
        speed_limit=70
    )
    print(f"   Result: {link_create}")
    print(f"   link_id (new): {link_create.link_id}")
    print(f"   road_name (inherited): {link_create.road_name}")
    
    print("\n2. Required vs Optional Fields:")
    try:
        print("LinkCreate(road_name='Test') # Missing required link_id")
        LinkCreate.model_validate({"road_name": "Test"})
    except ValidationError as e:
        print(f"   Error: {e}")


def demo_sqlalchemy_integration():
    """Demonstrate SQLAlchemy integration."""
    print("\n\nSQLAlchemy Integration Demo")
    print("=" * 50)
    
    # Mock SQLAlchemy model
    class MockSQLAlchemyLink:
        def __init__(self):
            self.link_id = 54321
            self.road_name = "Database Road"
            self.length = 3000.0
            self.road_type = "highway"
            self.speed_limit = 80
            self.geometry = None
            self.speed_records_count = 2500
    
    mock_db_record = MockSQLAlchemyLink()
    
    print("1. Converting SQLAlchemy Model:")
    print(f"   DB Model: link_id={mock_db_record.link_id}")
    print(f"             road_name={mock_db_record.road_name}")
    print(f"             speed_records_count={mock_db_record.speed_records_count}")
    
    # Convert to Pydantic schema
    print("\n2. Automatic Conversion:")
    print("LinkResponse.model_validate(mock_db_record)")
    link_response = LinkResponse.model_validate(mock_db_record)
    print(f"   Schema: {link_response}")
    print(f"   JSON: {link_response.model_dump_json()}")


def demo_api_usage():
    """Demonstrate API usage patterns."""
    print("\n\nAPI Usage Demo")
    print("=" * 50)
    
    print("1. API Request Input:")
    # Simulate JSON input from API
    json_input = {
        "link_id": 99999,
        "road_name": "API Street",
        "length": 800.0,
        "speed_limit": 45,
        "geometry": {
            "type": "LineString",
            "coordinates": [[-81.3792, 30.3322], [-81.3790, 30.3328]]
        }
    }
    print(f"   JSON received: {json_input}")
    
    # Validate automatically
    link_create = LinkCreate(**json_input)
    print(f"   Validated: {link_create}")
    
    print("\n2. API Response Output:")
    # Simulate API response
    response_data = LinkResponse(
        link_id=99999,
        road_name="API Street", 
        length=800.0,
        speed_limit=45,
        speed_records_count=150
    )
    print(f"   Schema response: {response_data}")
    print(f"   JSON to client: {response_data.model_dump_json()}")
    
    print("\n3. Paginated List:")
    # List with multiple items
    links = [
        LinkResponse(link_id=1, road_name="Road 1"),
        LinkResponse(link_id=2, road_name="Road 2"),
        LinkResponse(link_id=3, road_name="Road 3")
    ]
    
    link_list = LinkList(
        items=links,
        total=150,
        page=1,
        size=3,
        pages=50
    )
    print(f"   List: {len(link_list.items)} items")
    print(f"   Pagination: page {link_list.page} of {link_list.pages}")
    print(f"   Total: {link_list.total} records")


def demo_field_features():
    """Demonstrate advanced Field features."""
    print("\n\nAdvanced Field Features Demo")
    print("=" * 50)
    
    print("1. Validation Constraints:")
    print("   speed_limit: ge=0, le=200  # Between 0 and 200")
    print("   length: ge=0              # >= 0")
    
    print("\n2. Documentation Features:")
    print("   description: Used for automatic API documentation")
    print("   examples: Appear in Swagger/OpenAPI")
    
    print("\n3. Default Values:")
    print("   default=None: Optional field")
    print("   default=0: Field with default value")
    
    print("\n4. ConfigDict:")
    print("   from_attributes=True: Allows SQLAlchemy conversion")
    print("   ConfigDict configures model behavior")


if __name__ == "__main__":
    demo_schema_basics()
    demo_validation()
    demo_inheritance()
    demo_sqlalchemy_integration()
    demo_api_usage()
    demo_field_features()
    
    print("\n\n" + "=" * 50)
    print("Schema Summary")
    print("=" * 50)
    print("LinkBase: Common fields (inheritance)")
    print("LinkCreate: For creating via API (+ required link_id)")
    print("LinkUpdate: For updating via API (all optional)")
    print("LinkResponse: For returning from API (+ computed fields)")
    print("LinkList: For paginated listing")
    print("\nReady to use in FastAPI endpoints!")
