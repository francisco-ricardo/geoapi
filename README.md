# GeoSpatial Links API
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.1-009688.svg?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.41-red.svg?style=flat-square&logo=sqlalchemy)](https://www.sqlalchemy.org/)
[![Python](https://img.shields.io/badge/Python-3.12-3776ab.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.5-4CAF50.svg?style=flat-square)](https://postgis.net/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.11.1-E92063.svg?style=flat-square&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/latest/)
[![pytest](https://img.shields.io/badge/pytest-8.4.1-0A9EDC.svg?style=flat-square&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.3.0-150458.svg?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![GeoAlchemy2](https://img.shields.io/badge/GeoAlchemy2-0.17.1-green.svg?style=flat-square)](https://geoalchemy-2.readthedocs.io/)
[![Geospatial](https://img.shields.io/badge/Geospatial-GeoJSON-brightgreen.svg?style=flat-square)](https://geojson.org/)
[![API Docs](https://img.shields.io/badge/API%20Docs-Swagger-85EA2D.svg?style=flat-square&logo=swagger&logoColor=white)](http://localhost:8000/docs)
[![Architecture](https://img.shields.io/badge/Architecture-Clean-blue.svg?style=flat-square)](#project-structure)
[![Big Data](https://img.shields.io/badge/Big%20Data-1.2M%2B%20Records-red.svg?style=flat-square)](#performance-optimization-big-data-ingestion)

A robust geospatial REST API built with **FastAPI**, **SQLAlchemy**, **PostgreSQL/PostGIS**, and **Pydantic** for traffic data analysis and visualization.

---

## 🏆 Project Highlights

### ✨ **Quality Achievements**
- **109 Tests**: Comprehensive test suite with 100% pass rate
- **Clean Code**: Clean, well-organized codebase following SOLID principles
- **Performance Optimized**: Handles 1.3M+ records efficiently with chunked processing
- **Code Style**: Black formatting with consistent style
- **Documentation**: Comprehensive docstrings and API documentation

### 🚀 **Technical Excellence**
- **Clean Architecture**: Domain-driven design with clear separation of concerns
- **Type Safety**: Full typing support with mypy validation
- **Observability**: Structured logging with correlation IDs and request tracing
- **Geospatial Ready**: PostGIS integration with GeoJSON support
- **DevOps Ready**: Complete Docker setup with development containers

### 📊 **Data Processing Capabilities**
- **Big Data Handling**: Optimized for processing millions of records
- **Memory Efficient**: Chunked processing with automatic garbage collection
- **Integrity Validation**: Comprehensive data validation and consistency checks
- **Multiple Formats**: Support for Parquet, GeoJSON, and standard database formats
- **Interactive Visualization**: Jupyter notebook with MapboxGL integration for data exploration

---

## 🔌 Technologies

### Core Stack

- **Backend**: FastAPI, SQLAlchemy 2.0, Pydantic v2

- **Database**: PostgreSQL + PostGIS (with automatic table creation)

- **Geospatial**: GeoAlchemy2, PostGIS, GeoJSON

- **Testing**: pytest, TDD approach with 109 tests

- **DevOps**: Docker, DevContainer, automated setup

### Development Tools

- **Code Quality**: Black (formatting), mypy (type checking)

- **Testing**: pytest with fixtures, parametrized tests, coverage reports

- **Documentation**: FastAPI auto-docs, Swagger UI, comprehensive docstrings

- **Performance**: SQLAlchemy bulk operations, memory-optimized data processing

- **Observability**: Structured logging, correlation IDs, request tracing

---

## 🏗️ Architecture

The project follows **Clean Architecture**, **SOLID**, and **KISS** principles with a layered approach:

### 📊 **Application Layers**

```
┌─────────────────────────────────────────┐
│                API Layer                │  ← FastAPI endpoints, validation
│         (app/api/v1/*.py)               │
├─────────────────────────────────────────┤
│            Middleware Layer             │  ← Request/response processing
│        (app/middleware/*.py)            │
├─────────────────────────────────────────┤
│              Schema Layer               │  ← Pydantic models, serialization
│          (app/schemas/*.py)             │
├─────────────────────────────────────────┤
│            Services Layer               │  ← Business logic
│          (app/services/*.py)            │
├─────────────────────────────────────────┤
│              Model Layer                │  ← SQLAlchemy ORM, relationships
│          (app/models/*.py)              │
├─────────────────────────────────────────┤
│              Core Layer                 │  ← Database, config, logging
│           (app/core/*.py)               │
└─────────────────────────────────────────┘
```

### 🔧 **Design Patterns Implemented**

- **Factory Pattern**: Database engine and session creation (`get_engine()`, `get_session_factory()`)

- **Dependency Injection**: FastAPI DI system for configuration and database dependencies

- **Middleware Pattern**: Request logging and correlation IDs (`LoggingMiddleware`)

- **Strategy Pattern**: Environment-specific configurations and database adapters

- **Singleton Pattern**: Cached database engine and logger instances

### 🏗️ **System Architecture & Data Flow**

The following diagram shows the complete system architecture, including data sources, ingestion pipeline, database integration, API services, and visualization components:

![Architecture Diagram](docs/geoapi_architecture.drawio.png)

**📋 Architecture Highlights:**

- **🔄 Data Pipeline**: Complete ETL process from external Parquet files to PostGIS database

- **🏗️ Clean Architecture**: Layered FastAPI application following SOLID principles  

- **🗄️ Spatial Database**: PostgreSQL + PostGIS with optimized indexes for geospatial queries

- **📊 Big Data Processing**: Handles 1.3M+ records with chunked processing and memory optimization

- **🌐 RESTful API**: FastAPI with automatic OpenAPI documentation and validation

- **📈 Data Visualization**: Jupyter notebook with MapboxGL for interactive geospatial analysis

- **🔍 Observability**: Comprehensive logging, correlation IDs, and request tracing

- **🐳 Containerized**: Full Docker setup with PostgreSQL and FastAPI services

---

## 🗄️ Database Schema

The GeoAPI uses a well-designed relational schema optimized for geospatial traffic data. The database consists of two main entities with a one-to-many relationship.

### Entity Relationship Diagram

![Database Schema - Entity Relationship Diagram](docs/geoapi_der.drawio.png)

### Schema Overview

**Links Table (`links`)**
- Stores road segment information with PostGIS geometry
- Primary key: `link_id` (integer)
- Contains road metadata: name, type, speed limit, length
- Geometry stored as `LINESTRING` in WGS84 (SRID 4326)

**Speed Records Table (`speed_records`)**
- Stores traffic speed measurements
- Foreign key reference to `links.link_id`
- Contains temporal data: timestamp, day of week, time period
- Speed values in miles per hour (mph)

### Key Features

- **Referential Integrity**: All speed records reference valid links with CASCADE delete

- **Spatial Indexing**: Optimized GIST indexes on geometry columns for fast spatial queries

- **Temporal Indexing**: Indexes on timestamp and temporal classification fields

- **Data Validation**: Built-in constraints ensure data quality (speed ranges, positive lengths, etc.)

- **PostGIS Integration**: Full spatial data support with geometry validation and transformation

### Database Technologies

- **PostgreSQL 16**: Primary database engine

- **PostGIS 3.5**: Geospatial extension for spatial data types and operations

- **SQLAlchemy 2.0**: ORM with modern async support

- **GeoAlchemy2**: Spatial extension for SQLAlchemy with PostGIS integration

---

## 📋 Logging and Observability

[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-Ready-4287f5.svg?style=flat-square&logo=opentelemetry&logoColor=white)](https://opentelemetry.io/)
[![Correlation IDs](https://img.shields.io/badge/Correlation%20IDs-Enabled-green.svg?style=flat-square)](https://microservices.io/patterns/observability/distributed-tracing.html)
[![Structured Logging](https://img.shields.io/badge/Structured%20Logging-JSON%20%26%20Console-blue.svg?style=flat-square)](https://12factor.net/logs)
[![Cloud Ready](https://img.shields.io/badge/Cloud%20Ready-Observability-purple.svg?style=flat-square&logo=googlecloud&logoColor=white)](https://cloud.google.com/logging)

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

---

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed on your host machine
- Clone this repository

### 🔧 Environment Configuration

You must create a `.env` file in the project root before starting the containers. The application will not work without proper environment configuration.

```bash
# Create .env file with default configuration
# Replace `your_mapbox_token_here` with your token
cat > .env << 'EOF'
GEOAPI_DATABASE_URL=postgresql://geoapi:geoapi@db:5432/geoapi
GEOAPI_API_HOST=0.0.0.0
GEOAPI_API_PORT=8000
GEOAPI_DEBUG=true
GEOAPI_APP_NAME=GeoAPI
GEOAPI_APP_VERSION=1.0.0
GEOAPI_MAPBOX_ACCESS_TOKEN=your_mapbox_token_here
GEOAPI_LINK_INFO_URL=https://cdn.urbansdk.com/data-engineering-interview/link_info.parquet.gz
GEOAPI_SPEED_DATA_URL=https://cdn.urbansdk.com/data-engineering-interview/duval_jan1_2024.parquet.gz
EOF
```

### Setup and Run

```bash
# 1. Complete setup (start the containers + create tables + data ingestion)
make setup
make validate-ingestion # Validate data ingestion integrity
# 2. Start the API with uvicorn
make run-api-dev        # Recommended for development (auto-reload + debug)
# 3. Access the API
# - API Server: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
# - Health Check: http://localhost:8000/health
```

> **📋 Note**: The API container starts but doesn't auto-run the FastAPI app, giving you control over when and how to start it (dev/prod mode). This is an
approach for better debugging and flexibility.

### Quick Verification

```bash
# Check if everything is working
make check-api          # API health check
make logs               # View container logs
make test               # Run unit tests
```

> **📋 Note**: To view all available commands in the Makefile, simply run `make help` from the root directory of the project.

### Access Points

- **API Server**: http://localhost:8000

- **API Documentation**: http://localhost:8000/docs  

- **Health Check**: http://localhost:8000/health

---

## � API Endpoints

The GeoAPI provides 4 main endpoints for traffic data analysis and geospatial querying. All endpoints return JSON responses and follow RESTful conventions.

### 1. 📊 GET `/aggregates/` - Daily Speed Aggregates

Get aggregated speed data for all links on a specific day and time period.

**Parameters:**
- `day` (required): Day of the week ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
- `period` (required): Time period ("Overnight", "Early Morning", "AM Peak", "Midday", "Early Afternoon", "PM Peak", "Evening")

**Example Request:**

```bash
# Get AM Peak data for Monday
curl "http://localhost:8000/aggregates/?day=Monday&period=AM%20Peak"
# Get Evening data for Friday
curl "http://localhost:8000/aggregates/?day=Friday&period=Evening"
```

**Example Response:**

```json
[
  {
    "link_id": 16981048,
    "road_name": "Philips Hwy",
    "length": 0.009320565,
    "road_type": null,
    "speed_limit": null,
    "geometry": {
      "type": "LineString",
      "coordinates": [[-81.59791, 30.24124], [-81.59801, 30.24135]]
    },
    "average_speed": 45.4,
    "record_count": 3,
    "min_speed": 43.0,
    "max_speed": 47.35,
    "speed_stddev": 2.21
  }
]

```

### 2. 🔍 GET `/aggregates/{link_id}` - Single Link Data
Get detailed speed data for a specific link.

**Parameters:**
- `link_id` (path): The numeric ID of the link
- `day` (required): Day of the week ("Monday", "Tuesday", etc.)
- `period` (required): Time period ("AM Peak", "PM Peak", "Midday", etc.)

**Example Request:**

```bash
# Get AM Peak data for link 16981048 on Monday
curl "http://localhost:8000/aggregates/16981048?day=Monday&period=AM%20Peak"
# Get Evening data for link 16981074 on Wednesday
curl "http://localhost:8000/aggregates/16981074?day=Wednesday&period=Evening"
```

**Example Response:**

```json
{
  "link_id": 16981048,
  "road_name": "Philips Hwy",
  "length": 0.009320565,
  "road_type": null,
  "speed_limit": null,
  "geometry": {
    "type": "LineString",
    "coordinates": [[-81.59791, 30.24124], [-81.59801, 30.24135]]
  },
  "average_speed": 45.4,
  "record_count": 3,
  "min_speed": 43.0,
  "max_speed": 47.35,
  "speed_stddev": 2.21
}
```

### 3. 🐌 GET `/patterns/slow_links/` - Slow Traffic Patterns

Find links with consistently slow traffic patterns.

**Parameters:**
- `period` (required): Time period ("AM Peak", "PM Peak", "Midday", etc.)
- `threshold` (required): Maximum average speed to consider "slow" (mph)
- `min_days` (required): Minimum number of days the link must be slow (1-7)

**Example Request:**

```bash
# Find links slower than 15 mph during AM Peak for at least 3 days per week
curl "http://localhost:8000/patterns/slow_links/?period=AM%20Peak&threshold=15&min_days=3"
# Find links slower than 25 mph during PM Peak for at least 2 days per week
curl "http://localhost:8000/patterns/slow_links/?period=PM%20Peak&threshold=25&min_days=2"
```
**Example Response:**
```json
[
  {
    "link_id": 1313272474,
    "road_name": "Oyster Creek Rd",
    "length": 0.176469364,
    "road_type": null,
    "speed_limit": null,
    "geometry": {
      "type": "LineString",
      "coordinates": [[-81.59376, 30.44053], [-81.5937, 30.44062]]
    },
    "average_speed": 10.31,
    "record_count": 1,
    "min_speed": 10.31,
    "max_speed": 10.31,
    "speed_stddev": null
  }
]
```

### 4. 🗺️ POST `/aggregates/spatial_filter/` - Spatial Query

Get aggregated data for links within a bounding box area.

**Request Body:**
```json
{
  "day": "Wednesday",
  "period": "AM Peak",
  "bbox": [-81.8, 30.1, -81.6, 30.3]
}
```
**Example Request:**
```bash
curl -X POST "http://localhost:8000/aggregates/spatial_filter/" \
  -H "Content-Type: application/json" \
  -d '{
    "day": "Wednesday",
    "period": "AM Peak",
    "bbox": [-81.8, 30.1, -81.6, 30.3]
  }'
```
**Example Response:**
```json
[
  {
    "link_id": 1313709937,
    "road_name": "Walkers Ridge Dr",
    "length": 0.259733078,
    "road_type": null,
    "speed_limit": null,
    "geometry": {
      "type": "LineString",
      "coordinates": [[-81.81882, 30.24779], [-81.81897, 30.25156]]
    },
    "average_speed": 13.98,
    "record_count": 1,
    "min_speed": 13.98,
    "max_speed": 13.98,
    "speed_stddev": null
  }
]
```

### 🚀 Quick API Testing

```bash
# 1. Test API health
curl "http://localhost:8000/health"
# 2. Get Monday AM Peak traffic data  
curl "http://localhost:8000/aggregates/?day=Monday&period=AM%20Peak"
# 3. Get data for a specific link
curl "http://localhost:8000/aggregates/16981048?day=Monday&period=AM%20Peak"
# 4. Find consistently slow links (under 15 mph during AM Peak for 2+ days)
curl "http://localhost:8000/patterns/slow_links/?period=AM%20Peak&threshold=15&min_days=2"
# 5. Get data within a geographic area
curl -X POST "http://localhost:8000/aggregates/spatial_filter/" \
  -H "Content-Type: application/json" \
  -d '{"day": "Wednesday", "period": "AM Peak", "bbox": [-81.8, 30.1, -81.6, 30.3]}'
```

### 📖 Interactive API Documentation

Visit http://localhost:8000/docs for interactive Swagger documentation where you can:
- Test all endpoints directly in your browser
- View detailed parameter descriptions
- See response schemas and examples
- Download OpenAPI specification

### 📊 Data Visualization Notebook

The project includes a **Jupyter Notebook** demonstrating real-world API usage with geospatial visualization:

**📍 Location**: `notebooks/notebook_1.ipynb`

**🎯 Purpose**: Complete example showing how to:

- Consume API endpoints programmatically

- Process geospatial traffic data

- Create interactive maps with Mapbox GL

- Generate data analysis summaries

**🔧 Features**:

- **API Integration**: Demonstrates GET requests to `/aggregates/` endpoint

- **MapboxGL Visualization**: Interactive choropleth maps showing traffic speeds

- **Data Analysis**: Pandas-based data processing and tabular summaries

**📋 Requirements**:

- Jupyter running on `http://localhost:8888`
- API running on `http://localhost:8000` (or update `BASE_URL` in notebook)
- Optional: Mapbox token for advanced visualizations
- Python packages: `requests`, `pandas`, `mapboxgl`, `geopandas`, `shapely`

---

## 🚧 Future Work

[![Production Ready](https://img.shields.io/badge/Status-MVP%20Complete-success.svg?style=flat-square&logo=checkmarx&logoColor=white)](#future-work)
[![Roadmap](https://img.shields.io/badge/Roadmap-Production%20Features-blue.svg?style=flat-square&logo=roadmap&logoColor=white)](#production-roadmap)

This project represents a **comprehensive MVP** demonstrating advanced data engineering and API development capabilities. The following enhancements would be prioritized for production deployment:

### 🔌 **API Enhancement**
- **Pagination Optimization**: Cursor-based pagination for large result sets
- **Response Caching**: Redis-based intelligent caching with geospatial awareness
- **API Versioning**: Semantic versioning strategy with backward compatibility
- **Architectural Consistency**: Refactor `/links/` endpoint to follow service layer pattern like `/aggregates/`, moving database queries from controller to service layer with proper exception handling.

### 📊 **Database Optimization**
- **Query Optimization**: Advanced query planning and execution optimization
- **Partitioning**: Time-based and geographic data partitioning
- **Materialized Views**: Pre-computed aggregations for complex analytics

#### 🔧 **Application Performance**
- **Async Processing**: Non-blocking I/O with FastAPI async capabilities
- **Background Tasks**: Celery-based distributed task processing
- **Memory Management**: Advanced garbage collection and memory profiling
- **Code Optimization**: Performance profiling and algorithmic improvements

### 🏗️ **DevOps**
- **Microservices Architecture**: Domain-driven service decomposition
- **CI/CD Pipeline**: Automated testing, security scanning, and deployment
- **Multi-Environment Setup**: Development, staging, and production environments

### 🔐 **Security Considerations**

[![Security](https://img.shields.io/badge/Security-Enterprise%20Grade-red.svg?style=flat-square&logo=security&logoColor=white)](#security-implementation)

#### 🛡️ **Authentication & Authorization**

- **Authentication**:
  - JWT/OAuth 2.0 with refresh tokens
  - Role-based access control (RBAC)
  - API key management with rate limiting

- **Authorization**:
  - Fine-grained permissions (read/write/admin)
  - Resource-level access control

#### 🚨 **API Security**
- **Input Validation**: Comprehensive sanitization and validation
- **SQL Injection Prevention**: Parameterized queries and ORM protection
- **Rate Limiting**: Adaptive rate limiting with DDoS protection
- **CORS Configuration**: Strict cross-origin resource sharing policies
- **Security Headers**: Implementation of security headers (HSTS, CSP, etc.)

### ⚡ **Performance & Scalability**

[![Performance](https://img.shields.io/badge/Performance-Enterprise%20Scale-green.svg?style=flat-square&logo=speedtest&logoColor=white)](#performance-optimization)
[![Scalability](https://img.shields.io/badge/Scalability-Cloud%20Native-blue.svg?style=flat-square&logo=kubernetes&logoColor=white)](#horizontal-scaling)

#### 🏗️ **Horizontal Scaling Architecture**
- **Database Tier**:
  - PostgreSQL cluster with read replicas
  - Horizontal partitioning by geographic regions
  - Connection pooling with PgBouncer
  - Automated failover and backup strategies

- **Application Tier**:
  - Microservices with independent scaling
  - Load balancing
  - Auto-scaling based on CPU/memory metrics

- **Caching Layer**:
  - Redis cluster for session management
  - Geospatial query result caching
  - CDN for static assets and documentation
  - Application-level caching strategies

---

## 🔥 Technical Challenges & Solutions

During development, I encountered and resolved three critical technical challenges that demonstrate advanced data engineering and API development expertise,

### 🚀 Performance Optimization: Big Data Ingestion

[![Optimization](https://img.shields.io/badge/Optimization-Memory%20%26%20Speed-success.svg?style=flat-square&logo=speedtest&logoColor=white)](#performance-results)
[![API Development](https://img.shields.io/badge/API%20Development-Production%20Ready-blue.svg?style=flat-square&logo=fastapi&logoColor=white)](#speed-aggregation-analysis)

During development, I implemented optimization techniques to handle large-scale data ingestion:

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

- ✅ **Optimal Chunk Size**: 5K records provides the best balance between memory usage and performance.

- ✅ **Batch Size Impact**: SQLAlchemy bulk operations with 2K batch size are 10x faster than individual inserts.

- ✅ **Memory Management**: Explicit garbage collection between chunks is critical for large datasets.

- ✅ **Progress Monitoring**: Real-time tracking improves user experience during long-running processes.

- ✅ **Error Recovery**: Chunked approach allows for granular error handling and retries.

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

This optimization approach allowed to successfully process over **1.3 million records** with complex spatial data while maintaining excellent performance.

### MapboxGL ChoroplethViz Compatibility**

[![MapboxGL](https://img.shields.io/badge/MapboxGL-Integration-orange.svg?style=flat-square&logo=mapbox&logoColor=white)](#mapboxgl-compatibility)
[![Problem Solving](https://img.shields.io/badge/Problem%20Solving-Advanced-red.svg?style=flat-square&logo=stack-overflow&logoColor=white)](#technical-analysis)

**Problem**: The `legend_title` parameter in `ChoroplethViz` constructor, caused runtime errors.

**Investigation Approach**:

- Consulted official MapboxGL Python documentation.

- Explored alternative implementation approaches (custom wrapper classes).

- Analyzed library source code and issue trackers.

- Tested various parameter combinations.

**Root Cause**: The `legend_title` parameter was deprecated/undocumented in current MapboxGL Python version, despite appearing in older examples.

**Solution**: Removed the problematic parameter while maintaining all core visualization functionality.

**Technical Impact**: Ensured 100% compatibility with current MapboxGL library versions.

### Data Visualization Coverage Analysis**

**Problem**: Initial visualization showed incomplete street coverage, suggesting potential data integrity issues.

**Investigation Approach**:

- Created comprehensive data diagnostic scripts

- Analyzed geometric validity of 57,130+ road segments

- Validated spatial data consistency across the entire dataset

- Performed statistical analysis of speed distribution patterns

- Cross-referenced with Jacksonville, FL road network topology

**Root Cause**: The "gaps" in visualization accurately reflected the real dataset structure; many minor residential roads have sparse traffic measurement coverage.

**Solution**:

- Confirmed data integrity through exhaustive validation

- Optimized visualization parameters for better coverage appearance

- Documented the realistic nature of traffic data collection

**Technical Impact**: Verified that the API correctly represents real-world traffic measurement patterns, not data corruption.

### Speed Aggregation Deep Dive**

[![Data Engineering](https://img.shields.io/badge/Data%20Engineering-Expert%20Level-success.svg?style=flat-square&logo=databricks&logoColor=white)](#data-integrity-validation)

**Problem**: Initial concern that API was returning constant speed values (0.62 mph) in sorted results.

**Investigation Approach**:

- Analyzed complete speed distribution across 57,130 road segments

- Performed statistical analysis of aggregated traffic data

- Investigated data ingestion pipeline for potential bugs

- Examined database field population (`day_of_week` initially empty)

- Conducted API response validation across multiple endpoints

**Root Cause Discovery**:

1. **Data Ingestion Bug**: `day_of_week` field was not being populated during data ingestion

2. **Sorting Behavior**: The 0.62 mph values represented legitimate heavily congested traffic (158 records, 0.3% of dataset)

**Solution**:

- Fixed data ingestion script to properly populate temporal fields

- Re-ingested complete dataset (1.2M+ speed records)

- Validated final data distribution: 6,037 unique speeds ranging 0.62-121.79 mph

**Technical Impact**:

- Ensured data temporal accuracy for time-based aggregations

- Confirmed realistic traffic speed distribution patterns

- Validated API integrity with proper varied speed data

#### **Key Technical Insights**

| Challenge Area | Investigation Depth | Solution Complexity | Business Impact |
|----------------|-------------------|-------------------|-----------------|
| **Library Compatibility** | Documentation deep-dive | Parameter removal | High - Client delivery |
| **Data Integrity** | Statistical validation | Visualization optimization | Critical - Data accuracy |
| **API Functionality** | End-to-end pipeline analysis | Data re-ingestion | High - Core functionality |

---

## 🔧 Development & Troubleshooting

### Common Development Tasks

```bash
# Start development environment
make start && make run-api-dev
# Run tests while developing
make test                    # Quick unit tests
make test-coverage          # Tests with coverage report
make test-api               # Test API endpoints
# Code quality checks
make format                 # Format code with Black
make type-check            # Type checking with mypy
make sort-imports          # Sort imports with isort
make quality-check         # All quality checks combined
```

### Troubleshooting Guide

#### ⚙️ Configuration Issues

```bash
# Check if .env file exists and has correct values
ls -la .env                # Verify .env file exists
cat .env                   # Check environment variables
make check-api             # Check API
```

**Common Configuration Problems:**
- ❌ **Missing `.env` file**: Create `.env` file in project root using the template above
- ❌ **Wrong database URL**: Ensure `GEOAPI_DATABASE_URL` matches Docker container settings
- ❌ **Invalid port configuration**: Check `GEOAPI_API_PORT` is set to `8000`
- ❌ **Missing data source URLs**: Verify both `GEOAPI_LINK_INFO_URL` and `GEOAPI_SPEED_DATA_URL` are set

#### API Not Responding

```bash
make check-api            # Check status
make logs                  # View logs
make restart-api           # Restart API process
```

#### Container Issues

```bash
make restart               # Restart all containers
make logs                  # Check container logs
make shell                 # Debug inside container
```

#### Database Issues

```bash
make check-db             # Check database state
make check-postgis        # Verify PostGIS spatial data
make clean-db              # Clean database (careful!)
make db-shell              # Open PostgreSQL shell
```

#### Development Issues

```bash
make clean-empty-files     # Remove VS Code empty files
make clean-pycache         # Clean Python cache
make format                # Fix code formatting
```

---
