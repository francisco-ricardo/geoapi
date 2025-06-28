# Scripts Organization

This document describes the purpose and organization of utility scripts in the project.

## Directory Structure

```
scripts/
├── data/
│   ├── analyze_data.py          # Analyze original Parquet datasets
│   ├── explore_datasets.py     # Dataset exploration utilities
│   └── ingest_datasets.py      # Main data ingestion script
├── database/
│   ├── create_tables.py         # Database setup and table creation
│   ├── postgis_queries.sql     # PostGIS spatial query examples
│   ├── verify_database.py      # Database state verification
│   └── verify_postgis.py       # PostGIS-specific verification
├── demo/
│   ├── schemas_basic.py         # Basic schema demonstration
│   └── schemas_complete.py     # Complete schema guide and examples
├── setup/
│   └── complete_setup.py       # Complete project setup
└── testing/
    ├── run_tests.py             # Simple test runner (all tests)
    ├── run_tests_by_category.py # Category-based test runner
    └── test_endpoints.py        # Manual endpoint testing
```

## Script Descriptions

### Data Scripts (`scripts/data/`)

#### `analyze_data.py`
- **Purpose**: Analyze original Parquet datasets before ingestion
- **Features**:
  - Examines link_info.parquet.gz structure and content
  - Analyzes speed data patterns and statistics
  - Validates GeoJSON geometry format
  - Checks data compatibility between datasets
- **Usage**: `python scripts/data/analyze_data.py`
- **When to use**: Before data ingestion, debugging data issues

#### `explore_datasets.py`
- **Purpose**: Interactive dataset exploration utilities
- **Features**: Basic exploration functions and utilities

#### `ingest_datasets.py`
- **Purpose**: Main data ingestion script for Parquet → PostgreSQL
- **Features**:
  - Loads and processes Parquet files
  - Converts GeoJSON to PostGIS geometry
  - Bulk inserts with SQLAlchemy ORM
  - Data validation and integrity checks
- **Usage**: `python scripts/data/ingest_datasets.py`

### Database Scripts (`scripts/database/`)

#### `create_tables.py`
- **Purpose**: Creates all database tables defined in SQLAlchemy models
- **Features**:
  - Connects to PostgreSQL/PostGIS database
  - Creates tables for Link and SpeedRecord models
  - Verifies table creation and structure
  - Provides detailed logging and error handling
- **Usage**: `python scripts/database/create_tables.py`
- **Requirements**: PostgreSQL/PostGIS database connection configured

#### `verify_database.py`
- **Purpose**: Verify database state after data ingestion
- **Features**:
  - Checks record counts and data integrity
  - Validates relationships between tables
  - Tests basic geometry functionality
  - Provides data quality metrics
- **Usage**: `python scripts/database/verify_database.py`
- **When to use**: After data ingestion, for health checks

#### `verify_postgis.py`
- **Purpose**: Comprehensive PostGIS spatial data verification
- **Features**:
  - Advanced spatial queries and analysis
  - Geometry format demonstrations (WKT, GeoJSON)
  - PostGIS function examples
  - Detailed spatial statistics
- **Usage**: `python scripts/database/verify_postgis.py`
- **When to use**: For spatial data validation and examples

#### `postgis_queries.sql`
- **Purpose**: Collection of useful PostGIS SQL queries
- **Features**: Ready-to-use spatial queries for manual database inspection

#### `create_tables.py`
- **Purpose**: Creates all database tables defined in SQLAlchemy models
- **Features**:
  - Connects to PostgreSQL/PostGIS database
  - Creates tables for Link and SpeedRecord models
  - Verifies table creation and structure
  - Provides detailed logging and error handling
- **Usage**: `python scripts/database/create_tables.py`
- **Requirements**: PostgreSQL/PostGIS database connection configured

### Demo Scripts (`scripts/demo/`)

#### `schemas_basic.py`
- **Purpose**: Simple demonstration of Pydantic schema basics
- **Features**:
  - Shows basic schema creation and validation
  - Demonstrates common use cases
  - Interactive examples with clear output
- **Usage**: `python scripts/demo/schemas_basic.py`
- **Target**: Developers learning schema fundamentals

#### `schemas_complete.py`
- **Purpose**: Comprehensive guide to all Pydantic schemas in the project
- **Features**:
  - Complete schema hierarchy explanation
  - Validation examples (success and failure cases)
  - Geospatial data handling demonstration
  - JSON serialization examples
  - Real-world usage patterns
- **Usage**: `python scripts/demo/schemas_complete.py`
- **Target**: Complete understanding of project schemas

### Testing Scripts (`scripts/testing/`)

#### `run_tests.py`
- **Purpose**: Simple test runner for all project tests
- **Features**:
  - Runs all tests with proper configuration
  - Provides clear output and results summary
  - Handles test failures gracefully
- **Usage**: `python scripts/testing/run_tests.py`
- **Requirements**: All test dependencies installed

#### `run_tests_by_category.py`
- **Purpose**: Category-based test execution for different scenarios
- **Features**:
  - **Basic tests**: No database required (config, schemas)
  - **Schema tests**: Pydantic validation only
  - **Database tests**: PostgreSQL/PostGIS required
  - **All tests**: Complete test suite
- **Usage**: 
  ```bash
  python scripts/testing/run_tests_by_category.py basic
  python scripts/testing/run_tests_by_category.py schema
  python scripts/testing/run_tests_by_category.py database
  python scripts/testing/run_tests_by_category.py all
  ```
- **Benefits**: Allows testing in different environments (with/without database)

#### `test_endpoints.py`
- **Purpose**: Manual testing of FastAPI endpoints
- **Features**:
  - Tests API startup and basic functionality
  - Tests individual endpoints with real data
  - Provides detailed request/response logging
  - Validates endpoint behavior and error handling
- **Usage**: `python scripts/testing/test_endpoints.py`
- **Requirements**: API server running or test client setup

## Usage Guidelines

### For Development Setup
1. **Database Setup**: `python scripts/database/create_tables.py`
2. **Verify Schemas**: `python scripts/demo/schemas_basic.py`
3. **Run Basic Tests**: `python scripts/testing/run_tests_by_category.py basic`

### For Learning/Understanding
1. **Schema Basics**: `python scripts/demo/schemas_basic.py`
2. **Complete Guide**: `python scripts/demo/schemas_complete.py`

### For Testing
1. **Quick Tests**: `python scripts/testing/run_tests_by_category.py basic`
2. **Schema Validation**: `python scripts/testing/run_tests_by_category.py schema`
3. **Full Test Suite**: `python scripts/testing/run_tests.py`
4. **Manual API Testing**: `python scripts/testing/test_endpoints.py`

### For Production Deployment
1. **Database Setup**: `python scripts/database/create_tables.py`
2. **Full Validation**: `python scripts/testing/run_tests.py`

## Design Principles

All scripts follow these principles:

1. **English Only**: All comments, docstrings, and output in English
2. **ASCII Characters**: No emojis or special Unicode characters
3. **Clear Purpose**: Each script has a specific, well-defined purpose
4. **Error Handling**: Robust error handling with clear messages
5. **Documentation**: Comprehensive docstrings and usage examples
6. **Modularity**: Scripts can be run independently
7. **Standards Compliance**: Follow Python and project coding standards

## Migration Notes

The following old scripts were removed from the project root and their functionality integrated:

- `create_tables.py` → `scripts/database/create_tables.py` (improved)
- `demo_schemas.py` → `scripts/demo/schemas_basic.py` (simplified)
- `explain_schemas.py` → `scripts/demo/schemas_complete.py` (enhanced)
- `run_tests.py` → `scripts/testing/run_tests.py` (maintained)
- `test_endpoint.py` → `scripts/testing/test_endpoints.py` (improved)
- `test_working.py` → `scripts/testing/run_tests_by_category.py` (enhanced)

All functionality has been preserved and improved with better organization, documentation, and error handling.
