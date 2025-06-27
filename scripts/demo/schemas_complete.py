#!/usr/bin/env python3
"""
Complete demonstration of Pydantic schemas used in the project.

This script provides an interactive and comprehensive guide to understand
how Pydantic schemas work, including validation, serialization, and 
integration with FastAPI and SQLAlchemy.
"""

import sys
import json
from datetime import datetime
from typing import Dict, Any

# Add project root to Python path
sys.path.insert(0, '/workspace')

from app.schemas.link import LinkBase, LinkCreate, LinkUpdate, LinkResponse, LinkList
from app.schemas.speed_record import SpeedRecordBase, SpeedRecordCreate, SpeedRecordUpdate, SpeedRecord, SpeedRecordList
from pydantic import ValidationError


def demo_schema_basics():
    """Demonstrate basic schema concepts."""
    print("=" * 60)
    print("Basic Schema Concepts")
    print("=" * 60)
    
    # 1. Basic creation
    print("\n1. BASIC CREATION:")
    print("LinkBase() - without data")
    link_empty = LinkBase()
    print(f"   Result: {link_empty}")
    print(f"   road_name: {link_empty.road_name}")
    print(f"   speed_limit: {link_empty.speed_limit}")
    
    # 2. Creation with data
    print("\n2. CREATION WITH DATA:")
    print("LinkBase(road_name='Main St', speed_limit=35)")
    link_with_data = LinkBase(road_name="Main St", speed_limit=35)
    print(f"   Result: {link_with_data}")
    print(f"   road_name: {link_with_data.road_name}")
    print(f"   speed_limit: {link_with_data.speed_limit}")
    
    # 3. JSON serialization
    print("\n3. JSON SERIALIZATION:")
    json_data = link_with_data.model_dump()
    print(f"   .model_dump(): {json_data}")
    json_string = link_with_data.model_dump_json()
    print(f"   .model_dump_json(): {json_string}")


def demo_validation():
    """Demonstrate automatic validation."""
    print("\n\n" + "=" * 60)
    print("Automatic Validation")
    print("=" * 60)
    
    # 1. Type validation
    print("\n1. TYPE VALIDATION:")
    try:
        print("Attempting to create LinkBase with invalid speed_limit type...")
        # This will fail due to type validation - speed_limit expects int, not str
        LinkBase(speed_limit="invalid_text")  # type: ignore
    except ValidationError as e:
        print(f"   ValidationError: {e.errors()[0]['msg']}")
        print(f"   Field: {e.errors()[0]['loc']}")
        print("   This is expected - speed_limit must be numeric")
    
    # 2. Required fields
    print("\n2. REQUIRED FIELDS:")
    try:
        print("LinkCreate() - missing required fields")
        # This will fail because link_id is required
        test_data = {}
        LinkCreate(**test_data)
    except ValidationError as e:
        print(f"   ValidationError: Missing required fields")
        for error in e.errors():
            print(f"   - {error['loc'][0]}: {error['msg']}")
    
    # 3. Valid creation
    print("\n3. VALID CREATION:")
    valid_link = LinkCreate(
        link_id=12345,
        road_name="Highway 101",
        length=2500.0,
        speed_limit=65,
        road_type="highway",
        geometry={
            "type": "LineString",
            "coordinates": [[-122.4, 37.8], [-122.3, 37.9]]
        }
    )
    print(f"   Created successfully: {valid_link.road_name}")
    print(f"   Length: {valid_link.length} meters")
    print(f"   Speed limit: {valid_link.speed_limit} km/h")


def demo_schema_hierarchy():
    """Demonstrate schema inheritance hierarchy."""
    print("\n\n" + "=" * 60)
    print("Schema Inheritance Hierarchy")
    print("=" * 60)
    
    print("\nLINK SCHEMAS:")
    print("   LinkBase (base fields)")
    print("   ├── LinkCreate (for POST requests)")
    print("   ├── LinkUpdate (for PUT/PATCH requests)")
    print("   └── LinkResponse (for API responses)")
    
    print("\nSPEED RECORD SCHEMAS:")
    print("   SpeedRecordBase (base fields)")
    print("   ├── SpeedRecordCreate (for POST requests)")
    print("   ├── SpeedRecordUpdate (for PUT/PATCH requests)")
    print("   └── SpeedRecord (for API responses)")
    
    # Show differences
    print("\n1. BASE SCHEMA (LinkBase):")
    base_fields = list(LinkBase.model_fields.keys())
    print(f"   Fields: {base_fields}")
    
    print("\n2. CREATE SCHEMA (LinkCreate):")
    create_fields = list(LinkCreate.model_fields.keys())
    print(f"   Fields: {create_fields}")
    print("   Note: Includes 'geometry' field required for creation")
    
    print("\n3. RESPONSE SCHEMA (LinkResponse):")
    response_fields = list(LinkResponse.model_fields.keys())
    print(f"   Fields: {response_fields}")
    print("   Note: Includes 'id' and timestamps for responses")


def demo_geospatial_features():
    """Demonstrate geospatial data handling."""
    print("\n\n" + "=" * 60)
    print("Geospatial Data Handling")
    print("=" * 60)
    
    # 1. Valid GeoJSON geometry
    print("\n1. VALID GEOJSON GEOMETRY:")
    geojson_geometry = {
        "type": "LineString",
        "coordinates": [
            [-122.48369693756104, 37.83381888486939],
            [-122.48348236083984, 37.83317489144141],
            [-122.48339653015138, 37.832056363179625]
        ]
    }
    
    link_with_geometry = LinkCreate(
        link_id=12345,
        road_name="Lombard Street",
        length=180.5,
        speed_limit=25,
        road_type="residential",
        geometry=geojson_geometry
    )
    
    print(f"   Road: {link_with_geometry.road_name}")
    print(f"   Link ID: {link_with_geometry.link_id}")
    if link_with_geometry.geometry:
        print(f"   Geometry type: {link_with_geometry.geometry['type']}")
        print(f"   Coordinates: {len(link_with_geometry.geometry['coordinates'])} points")
    
    # 2. Geometry validation
    print("\n2. GEOMETRY VALIDATION:")
    try:
        print("Invalid geometry (missing coordinates)")
        LinkCreate(
            link_id=54321,
            road_name="Test Road",
            geometry={"type": "LineString"}  # Missing coordinates
        )
    except ValidationError as e:
        print(f"   ValidationError: Geometry validation failed")
        print(f"   Details: {e.errors()[0]['msg']}")


def demo_speed_records():
    """Demonstrate speed record schemas."""
    print("\n\n" + "=" * 60)
    print("Speed Record Schemas")
    print("=" * 60)
    
    # 1. Basic speed record
    print("\n1. BASIC SPEED RECORD:")
    speed_record = SpeedRecordCreate(
        link_id=1,
        timestamp=datetime.now(),
        speed_kph=45.5,
        period="afternoon"
    )
    
    print(f"   Link ID: {speed_record.link_id}")
    print(f"   Speed: {speed_record.speed_kph} km/h")
    print(f"   Timestamp: {speed_record.timestamp}")
    print(f"   Period: {speed_record.period}")
    
    # 2. Validation of speed values
    print("\n2. SPEED VALIDATION:")
    try:
        print("Negative speed (should fail)")
        SpeedRecordCreate(
            link_id=1,
            timestamp=datetime.now(),
            speed_kph=-10.0  # Invalid negative speed
        )
    except ValidationError as e:
        print(f"   ValidationError: {e.errors()[0]['msg']}")
    
    try:
        print("Extremely high speed (should fail)")
        SpeedRecordCreate(
            link_id=1,
            timestamp=datetime.now(),
            speed_kph=500.0  # Unrealistic speed
        )
    except ValidationError as e:
        print(f"   ValidationError: {e.errors()[0]['msg']}")


def demo_json_serialization():
    """Demonstrate JSON serialization capabilities."""
    print("\n\n" + "=" * 60)
    print("JSON Serialization")
    print("=" * 60)
    
    # Create a complete link
    link = LinkResponse(
        link_id=1,
        road_name="Pacific Coast Highway",
        length=3200.0,
        speed_limit=55,
        road_type="highway",
        speed_records_count=150
    )
    
    print("\n1. MODEL DUMP (Python dict):")
    dict_data = link.model_dump()
    print(json.dumps(dict_data, indent=2, default=str))
    
    print("\n2. MODEL DUMP JSON (JSON string):")
    json_string = link.model_dump_json(indent=2)
    print(json_string)
    
    print("\n3. EXCLUDE FIELDS:")
    dict_without_timestamps = link.model_dump(exclude={'created_at', 'updated_at'})
    print(json.dumps(dict_without_timestamps, indent=2, default=str))


def interactive_demo():
    """Run the complete interactive demonstration."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PYDANTIC SCHEMAS - COMPLETE GUIDE                        ║
║                                                                              ║
║ Pydantic schemas are the "bridge" between your API and database.            ║
║ They ensure data is in the correct format and valid.                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    print("\nWhat are Pydantic Schemas?")
    print("-" * 50)
    print("""
Pydantic schemas are Python classes that define:
- Data structure (which fields exist)
- Data types (int, str, float, datetime, etc.)
- Validation (rules data must follow)
- Serialization (conversion to JSON)
- Documentation (descriptions and examples)
""")
    
    # Run all demonstrations
    demo_schema_basics()
    demo_validation()
    demo_schema_hierarchy()
    demo_geospatial_features()
    demo_speed_records()
    demo_json_serialization()
    
    print("\n\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("""
The schemas in this project provide:

1. LINK Management:
   - LinkBase: Core fields for road links (road_name, length, speed_limit, etc.)
   - LinkCreate: Data validation for new links (includes link_id and geometry)
   - LinkUpdate: Partial updates for existing links
   - LinkResponse: Complete data for API responses (includes computed fields)

2. SPEED RECORD Management:
   - SpeedRecordBase: Core speed measurement fields (timestamp, speed_kph, period)
   - SpeedRecordCreate: Validation for new records (includes link_id)
   - SpeedRecordUpdate: Partial updates for existing records
   - SpeedRecord: Complete data for API responses

3. VALIDATION Features:
   - Automatic type checking (int, float, str validation)
   - GeoJSON geometry validation (LineString format)
   - Speed limit validation (0-200 mph for links, 0-300 km/h for records)
   - Required field enforcement (link_id, timestamp, speed_kph)

4. API INTEGRATION:
   - Seamless FastAPI integration
   - Automatic OpenAPI documentation
   - Request/response validation
   - Error handling with clear messages
    """)
    
    print("\nNext steps:")
    print("- Run the API server: uvicorn app.main:app --reload")
    print("- Test endpoints: python scripts/testing/test_endpoints.py")
    print("- View API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    try:
        interactive_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()
