# Model Testing Strategy

## Overview

This project uses simplified models for testing database operations in an SQLite environment. The approach avoids GeoAlchemy2/PostGIS dependencies which are difficult to configure in a test environment without a full PostGIS database.

## Key Components

1. **Simplified Models** (`tests/simplified_models.py`):
   - `SimplifiedLink`: A version of the Link model without geometry columns
   - `SimplifiedSpeedRecord`: A simplified version of the SpeedRecord model

2. **Test Database Fixtures** (`tests/conftest.py`):
   - `test_db_simple`: Creates a database session using the simplified models
   - `test_db`: Attempts to create a session with actual models but has issues with GeoAlchemy2 in SQLite

## Testing Strategy

All model tests use the simplified models and the `test_db_simple` fixture. This allows us to:

1. Test model structure and relationships
2. Test database operations (CRUD)
3. Test model methods and properties

The simplified models have the same interfaces as the real models but can run in SQLite without PostGIS dependencies.

## Test Coverage

Model tests currently cover:
- Basic model structure
- Database operations (create, read, update, delete)
- Relationships between models
- Custom methods and properties
- String representations

## Notes

The warnings about "cannot collect test class" for SimplifiedLink and SimplifiedSpeedRecord can be ignored. These occur because pytest tries to collect these classes as test classes, but they are meant to be model classes used by the tests.
