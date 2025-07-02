#!/usr/bin/env python3
"""
Manual testing script for FastAPI endpoints.

This script tests the FastAPI endpoints directly using TestClient
to verify they work correctly with the database.
"""
import json
import sys
import time
from datetime import datetime

# Configure Python path
sys.path.insert(0, "/workspace")


def test_api_startup():
    """Test if the API can initialize properly."""
    print("API Startup Test")
    print("-" * 50)

    try:
        print("Importing modules...")
        from app.main import app

        print("Modules imported successfully")
        print(f"   App: {app.title}")
        print(f"   Version: {app.version}")
        print(f"   Debug: {app.debug}")
        return True

    except Exception as e:
        print(f"Error importing modules: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_basic_routes():
    """Test basic API routes."""
    print("\nTesting basic routes...")

    try:
        from fastapi.testclient import TestClient

        from app.main import app

        client = TestClient(app)

        # Test root endpoint
        response = client.get("/")
        print(f"GET / - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")

        # Test health endpoint
        response = client.get("/health")
        print(f"GET /health - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")

        # Test docs endpoint
        response = client.get("/docs")
        print(f"GET /docs - Status: {response.status_code}")

        return True

    except Exception as e:
        print(f"Error testing basic routes: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_link_endpoint():
    """Test the link creation endpoint."""
    print("\nTesting POST /links/")
    print("-" * 50)

    try:
        from fastapi.testclient import TestClient

        from app.main import app

        client = TestClient(app)

        # Test data for creating a link (using unique ID)
        unique_id = int(time.time())

        link_data = {
            "link_id": unique_id,
            "road_name": "Test Street",
            "length": 1500.5,
            "road_type": "arterial",
            "speed_limit": 35,
            "geometry": {
                "type": "LineString",
                "coordinates": [[-74.0059, 40.7128], [-74.0058, 40.7129]],
            },
        }

        print("Test data:")
        print(json.dumps(link_data, indent=2))

        # Try to create the link
        print("\nSending POST request...")
        response = client.post("/links/", json=link_data)

        print(f"Status: {response.status_code}")

        if response.status_code == 201:
            print("Link created successfully!")
            print("Created link:")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print("Error creating link:")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"Error testing link endpoint: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_schema_validation():
    """Test Pydantic schema validation."""
    print("\nTesting Schema Validation")
    print("-" * 50)

    try:
        from fastapi.testclient import TestClient

        from app.main import app

        client = TestClient(app)

        # Test 1: Missing required field
        print("Test 1: Missing required field")
        invalid_data = {
            "road_name": "Test Road",
            "length": 1000.0,
            # Missing required link_id
        }

        response = client.post("/links/", json=invalid_data)
        print(f"   Status: {response.status_code} (expected: 422)")
        if response.status_code == 422:
            print("   Validation working - required field detected")

        # Test 2: Invalid value
        print("\nTest 2: Invalid value (negative length)")
        invalid_data = {
            "link_id": 99999,
            "road_name": "Test Road",
            "length": -100.0,  # Invalid negative length
        }

        response = client.post("/links/", json=invalid_data)
        print(f"   Status: {response.status_code} (expected: 422)")
        if response.status_code == 422:
            print("   Validation working - invalid value detected")
            print(f"   Details: {response.json()}")

        return True

    except Exception as e:
        print(f"Error testing schema validation: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all endpoint tests."""
    print("Complete FastAPI Endpoint Test")
    print("=" * 60)

    # Track test results
    results = {}

    # Test API startup
    results["startup"] = test_api_startup()

    # Test basic routes
    if results["startup"]:
        results["basic_routes"] = test_basic_routes()
    else:
        results["basic_routes"] = False

    # Test link endpoint
    if results["basic_routes"]:
        results["link_endpoint"] = test_link_endpoint()
    else:
        results["link_endpoint"] = False

    # Test schema validation
    if results["basic_routes"]:
        results["schema_validation"] = test_schema_validation()
    else:
        results["schema_validation"] = False

    # Print summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"API Startup: {'PASSED' if results['startup'] else 'FAILED'}")
    print(f"Basic Routes: {'PASSED' if results['basic_routes'] else 'FAILED'}")
    print(f"POST /links/: {'PASSED' if results['link_endpoint'] else 'FAILED'}")
    print(
        f"Schema Validation: {'PASSED' if results['schema_validation'] else 'FAILED'}"
    )

    all_passed = all(results.values())
    if all_passed:
        print("\nAll tests passed!")
        print("FastAPI endpoints working correctly!")
    else:
        print("\nSome tests failed.")
        print("Check errors above and fix before continuing.")


if __name__ == "__main__":
    main()
