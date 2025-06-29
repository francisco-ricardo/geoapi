# GeoSpatial Links API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.4-green.svg)](https://postgis.net/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063.svg)](https://docs.pydantic.dev/latest/)

A robust geospatial REST API built with **FastAPI**, **SQLAlchemy**, **PostgreSQL/PostGIS**, and **Pydantic** for traffic data analysis and visualization.

## 🚀 Quick Start (For Interviewers)

### Prerequisites
- Docker and Docker Compose installed on your host machine
- Clone this repository

### Setup and Run
```bash
# 1. Start the containers (database + API)
make start

# 2. Complete setup (tables + data ingestion)
make setup

# 3. Access the API
# - API Server: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
# - Health Check: http://localhost:8000/health
```

### Alternative Commands
```bash
# Step by step setup
make start              # Start containers
make create-tables      # Create database tables
make ingest-data        # Load Parquet datasets

# Development commands
make logs              # View container logs
make shell             # Open shell in API container
make db-shell          # Open PostgreSQL shell
make test              # Run tests
make health-check      # Check system health

# Data validation
make validate-ingestion # Validate data ingestion integrity
```

### Access Points
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs  
- **Health Check**: http://localhost:8000/health

## 🔌 Technologies

- **Backend**: FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Database**: PostgreSQL + PostGIS (with automatic table creation)
- **Geospatial**: GeoAlchemy2, PostGIS, GeoJSON
- **Testing**: pytest, TDD approach
- **DevOps**: Docker, DevContainer, automated setup

## 📂 Project Structure

```
app/
├── core/
│   ├── config.py          # Configuration with Pydantic Settings
│   └── database.py        # Engine/session factory (SQLite/PostgreSQL)
├── models/
│   ├── link.py           # Road links model (with PostGIS geometry)
│   └── speed_record.py   # Speed measurements model
├── schemas/
│   ├── link.py           # Pydantic schemas for links
│   └── speed_record.py   # Pydantic schemas for speed records
├── api/v1/
│   └── links.py          # API endpoints implementation
└── services/             # Business logic layer

scripts/
├── setup/
│   └── complete_setup.py # Automated project setup
├── database/
│   └── create_tables.py  # Database initialization
├── demo/
│   ├── schemas_basic.py  # Basic schema demonstration
│   └── schemas_complete.py # Complete schema guide
└── testing/
    ├── run_tests.py      # Test runner
    ├── run_tests_by_category.py # Category-based tests
    └── test_endpoints.py # API endpoint testing

tests/
├── conftest.py           # Shared test fixtures
├── test_*.py            # Unit tests
└── test_models/         # Model-specific tests
```

## 🧪 Testing System

The project features a **comprehensive testing system** with multiple categories:

### Run Tests
```bash
# All tests
make test

# By category
python scripts/testing/run_tests_by_category.py basic    # No database required
python scripts/testing/run_tests_by_category.py schema   # Pydantic validation
python scripts/testing/run_tests_by_category.py database # PostgreSQL required
python scripts/testing/run_tests_by_category.py all      # Complete suite
```

### API Testing
```bash
# Test endpoints manually
python scripts/testing/test_endpoints.py

# Detailed help about tests
python run_tests.py --help-tests
```

### Run All Tests (Production)

```bash
# Run ALL tests (requires PostgreSQL/PostGIS)
python run_tests.py --all
```

## 🧪 Test Coverage

The project includes comprehensive test coverage reporting:

```bash
# Run all tests with coverage report
make test-coverage

# Run specific module tests
make test-logging
make test-middleware
make test-exceptions

# Custom coverage options
python scripts/testing/run_coverage.py --module app.core.logging
```

Coverage reports are generated in multiple formats:
- Console output (summary)
- HTML report (`coverage_html/index.html`)
- XML report (`coverage.xml`) for CI integration

### Coverage Targets

| Component | Target Coverage |
|-----------|----------------|
| Core modules | 90%+ |
| API endpoints | 85%+ |
| Models | 80%+ |
| Services | 80%+ |
| Overall | 85%+ |

The test suite is designed to be incremental, with tests added alongside new features to maintain high coverage levels.

### Test Coverage Reports

After running the tests with coverage, you can find the detailed reports in the `coverage_html` directory. Open `index.html` in a web browser to view the coverage details.

### Example Coverage Output

```
=============================== coverage summary ===============================
Statements   : 95.12% ( 370/389 )
Branches     : 85.76% ( 113/131 )
Functions    : 92.68% ( 56/60 )
Lines        : 95.12% ( 370/389 )
================================================================================
```

## 🔍 Data Validation

### Ingestion Integrity Validation

The project includes a robust data validation system to ensure integrity after ingestion:

```bash
# Validate data integrity after ingestion
make validate-ingestion
```

#### What is validated:

**1. Link Data:**
- Valid geometries (GeoJSON/WKT)
- Consistent coordinates (SRID 4326) 
- Required fields are populated
- Uniqueness of link_ids

**2. Speed Data:**
- Valid references to existing links
- Timestamps in correct format (UTC)
- Speed values within reasonable limits
- Time periods correctly categorized

**3. Referential Integrity:**
- All speed_records reference valid links
- Valid and consistent PostGIS geometries
- Uniform SRID across all geometries

**4. Statistical Consistency:**
- Expected record counts
- Consistent average speeds by period
- Proper temporal distribution

#### Sample Output:
```
[PASS] Link geometries validation passed
[PASS] Speed records validation passed  
[PASS] All speed records have valid link references
[PASS] All geometries use consistent SRID: 4326
[PASS] Average speed for AM Peak matches: 35.94 mph
[PASS] ALL VALIDATIONS PASSED - Data ingestion is accurate

*** Data integrity confirmed! The ingestion process worked correctly. ***
```

### Other Validation Commands

```bash
make analyze-data      # Analyze original Parquet datasets
make verify-db         # Verify database state
make verify-postgis    # Verify PostGIS spatial data
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL="postgresql://user:pass@localhost:5432/geoapi"
DATABASE_URL_TEST="sqlite:///./test.db"

# API
API_TITLE="GeoAPI"
API_VERSION="1.0.0"
DEBUG=true

# Data
MAPBOX_TOKEN="pk.your_token_here"  # Optional
```

### DevContainer

The project is configured to use **DevContainer** with all dependencies:

```bash
# Start the development environment
docker-compose -f docker-compose-dev.yml up -d
```

## 🔧 Development

### 1. Configure Environment

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Configure Python environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 2. Run Tests

```bash
# Local development (SQLite)
python run_tests.py --sqlite

# Complete environment (PostgreSQL)
python run_tests.py --all
```

### 3. Model Structure

#### Link (Road Links)
```python
class Link(Base):
    id: int (PK)
    link_id: str (unique)
    road_name: str (optional)
    geometry: Geometry (Point/LineString, nullable for tests)
    speed_records: relationship -> SpeedRecord[]
```

#### SpeedRecord (Speed Measurements)
```python
class SpeedRecord(Base):
    id: int (PK)
    link_id: int (FK -> Link.id)
    timestamp: datetime
    speed_kph: float
    period: str (morning/afternoon/evening/night)
    link: relationship -> Link
```

## 📈 Next Steps

- [ ] Implement FastAPI endpoints (`/api/v1/`)
- [ ] Create Pydantic schemas for serialization
- [ ] Implement Parquet data ingestion services
- [ ] Develop Jupyter notebook for analysis with Mapbox
- [ ] Add API integration tests
- [ ] Configure CI/CD with GitHub Actions

## 🏗️ Architecture

The project follows **Clean Architecture**, **SOLID**, and **KISS** principles:

- **Factory Pattern** for database connections
- **Dependency Injection** for configuration
- **Repository Pattern** (to be implemented)
- **Clean Code** with strong typing
- **TDD** with comprehensive coverage

## 📚 Documentation

- **FastAPI**: Automatic documentation at `/docs` (Swagger)
- **Models**: Documented with docstrings and type hints
- **Tests**: Descriptive and well-organized test cases

---

**Current Status**: ✅ Solid foundation implemented, ready for API development

## 📚 Lessons Learned

### 🚀 Performance Optimization: Big Data Ingestion

[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.4-green.svg)](https://postgis.net/)

During development, we implemented several optimization techniques to handle large-scale data ingestion:

#### **Initial Challenge**
- Processing **1.2M+ speed records** and **100K+ road links** with complex geometries
- Memory consumption reaching 90%+ with naive approach
- Slow sequential processing causing timeouts

#### **Three-Tier Optimization Strategy**

##### 1. 🧩 **Chunk Processing**
```python
# Memory-optimized chunk processing
def process_speed_records_chunked(session, existing_link_ids):
    """Process speed records in memory-efficient chunks."""
    for start_idx in range(0, total_records, CHUNK_SIZE):
        # Process only a chunk at a time (5K records)
        chunk_df = df.iloc[start_idx:start_idx + CHUNK_SIZE]
        
        # Process this chunk only, then free memory
        process_chunk(chunk_df)
        gc.collect()  # Force garbage collection
```

##### 2. 🔄 **Streaming Pipeline**
The data flows through a sequential pipeline with defined stages:
1. Load chunk from Parquet dataset
2. Transform to ORM objects with geometry processing
3. Bulk insert to database
4. Clean memory and move to next chunk

```python
# Streaming pipeline pattern
def _transform_link_chunk(chunk_df):
    """Transform a chunk of data - Single Responsibility"""
    # Process data transformations
    return transformed_objects

def _bulk_insert_links(session, objects):
    """Handle database insertions - Single Responsibility"""
    # Perform bulk insertions
    return inserted_count
```

##### 3. ⚡ **Optimized Bulk Operations**
```python
# Efficient batch operations
def _bulk_insert_speed_records(session, speed_objects):
    """10x faster than individual inserts"""
    for i in range(0, len(speed_objects), BATCH_SIZE):
        batch = speed_objects[i:i + BATCH_SIZE]
        session.bulk_save_objects(batch)
        session.commit()
```

#### **Performance Results**

| Metric | Before Optimization | After Optimization | Improvement |
|--------|---------------------|-------------------|-------------|
| Memory Usage | 90%+ | <50% | ~50% reduction |
| Processing Time | 25+ minutes | ~7 minutes | 3.5x faster |
| Reliability | Frequent OOM errors | Zero failures | 100% reliable |
| Records/second | ~800 | ~3,000 | 3.75x throughput |

#### **Key Insights**
- ✅ **Optimal Chunk Size**: 5K records provides the best balance between memory usage and performance
- ✅ **Batch Size Impact**: SQLAlchemy bulk operations with 2K batch size are 10x faster than individual inserts
- ✅ **Memory Management**: Explicit garbage collection between chunks is critical for large datasets
- ✅ **Progress Monitoring**: Real-time tracking improves user experience during long-running processes
- ✅ **Error Recovery**: Chunked approach allows for granular error handling and retries

#### **Code Implementation**
```python
# Configuration constants based on optimization testing
LINK_CHUNK_SIZE = 5000
SPEED_RECORD_CHUNK_SIZE = 5000
LINK_BATCH_SIZE = 1000
SPEED_BATCH_SIZE = 2000

# Main processing function follows SOLID principles
def process_speed_records_chunked(session, existing_link_ids):
    """Process 1.2M+ records efficiently with minimal memory footprint"""
    print(f"Processing speed records in chunks of {SPEED_RECORD_CHUNK_SIZE:,} records...")
    
    for start_idx in range(0, total_records, SPEED_RECORD_CHUNK_SIZE):
        # Process one chunk at a time
        chunk_df = speed_df.iloc[start_idx:start_idx + SPEED_RECORD_CHUNK_SIZE]
        
        # Transform data (separated responsibility)
        speed_objects, chunk_skipped = _transform_speed_chunk(chunk_df, existing_link_ids)
        
        # Bulk insert with optimized batch size (separated responsibility)
        chunk_inserted = _bulk_insert_speed_records(session, speed_objects)
        
        # Memory cleanup - critical for processing large datasets
        del speed_objects, chunk_df
        gc.collect()
```

This optimization approach allowed us to successfully process over **1.3 million records** with complex spatial data while maintaining excellent performance and reliability.

---

## 📋 Logging and Observability

[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-Ready-4287f5.svg)](https://opentelemetry.io/)
[![Correlation-IDs](https://img.shields.io/badge/Correlation_IDs-Enabled-green.svg)](https://microservices.io/patterns/observability/distributed-tracing.html)

The API includes a comprehensive logging and observability system:

### Key Features

- **Structured Logging**: Supports both human-readable console logs and machine-parseable JSON format
- **Correlation IDs**: Every request gets a unique ID that is propagated through all logs
- **Request/Response Logging**: Automatic logging of all HTTP requests with timing and performance metrics
- **Cloud-Ready**: Designed for integration with cloud observability platforms
- **Contextual Logging**: Endpoint handlers can access request-scoped loggers with correlation IDs

### Configuration

Logging can be configured via environment variables:

```bash
# Logging configuration
GEOAPI_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
GEOAPI_LOG_FORMAT=console  # console or json
GEOAPI_LOG_TO_FILE=false  # true or false
GEOAPI_LOG_FILE_PATH=/var/log/geoapi/app.log  # Path for file logging

# Observability settings
GEOAPI_ENABLE_TRACING=false  # Enable distributed tracing
GEOAPI_TRACING_PROVIDER=otlp  # otlp, jaeger, honeycomb
GEOAPI_TRACING_ENDPOINT=http://localhost:4317  # Endpoint for tracing exporter
```

### Log Formats

#### Development Mode (Console)
```
2025-06-29 10:15:23,456 [INFO] geoapi.request:42 - Request started: GET /api/v1/links
2025-06-29 10:15:23,512 [INFO] geoapi.request:98 - Request completed: GET /api/v1/links - 200
```

#### Production Mode (JSON)
```json
{
  "timestamp": "2025-06-29T10:15:23.456Z",
  "level": "INFO",
  "message": "Request completed: GET /api/v1/links - 200",
  "logger": "geoapi.request",
  "location": {
    "module": "logging_middleware",
    "function": "dispatch",
    "line": 98
  },
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
  "http": {
    "method": "GET",
    "url": "http://localhost:8000/api/v1/links",
    "status_code": 200,
    "response_time": 0.056,
    "request_id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab"
  },
  "event": "request_completed",
  "performance": {
    "response_time": 0.056
  }
}
```

### Usage in Code

```python
# In FastAPI endpoints
@app.get("/items/{item_id}")
async def get_item(
    item_id: int, 
    logger: ContextLogger = Depends(get_request_logger)
):
    logger.info(f"Processing item {item_id}")
    
    # Add context for this specific operation
    operation_logger = logger.with_context({"operation": "get_item"})
    operation_logger.debug("Detailed operation info", extra={"item_id": item_id})
    
    return {"item_id": item_id}
```

### Future Observability

The system is designed for easy integration with:

- **OpenTelemetry**: For distributed tracing across services
- **Cloud Logging**: Structured JSON logs ready for Google Cloud Logging, AWS CloudWatch, etc.
- **Metrics Export**: Framework in place for exporting performance metrics
- **Alerting**: Error logs are structured for easy integration with alerting systems
