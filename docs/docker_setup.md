# 🐳 Docker Development Environment

## Overview

This project uses a multi-container Docker setup for development with PostgreSQL + PostGIS and FastAPI.

## Services

### 🗄️ Database (`db`)
- **Image**: `postgis/postgis:16-3.5`
- **Container**: `geoapi_db_dev`
- **Port**: `5432`
- **Features**:
  - PostgreSQL 16 with PostGIS 3.5
  - Automatic health checks
  - Persistent data volume
  - Database initialization script

### 🚀 API (`api`)
- **Image**: `geoapi_api_dev` (built from Dockerfile.dev)
- **Container**: `geoapi_api_dev`
- **Port**: `8000`
- **Features**:
  - Python 3.12 development environment
  - **Manual API startup** for developer control
  - Interactive terminal access (stdin_open + tty)
  - No automatic startup - use `make run-api-dev`
  - Depends on database health

### 📓 Jupyter Notebook (`notebook`)
- **Image**: `python:3.12-slim`
- **Container**: `geoapi_notebook_dev`
- **Port**: `8888`
- **Features**:
  - JupyterLab with geospatial libraries
  - Pre-installed: pandas, geopandas, mapboxgl
  - Access without token for development

## 🚀 Quick Start

### 1. Start Services
```bash
# Start database and API container (API not running yet)
make start

# Alternative: docker-compose up
docker-compose -f docker-compose-dev.yml up -d
```

### 2. Setup Database and Data
```bash
# Complete setup (creates tables and ingests data)
make setup

# Or step by step:
make create-tables
make ingest-data
```

### 3. Start API
```bash
# Start API in development mode (with auto-reload)
make run-api-dev

# Or production mode:
make run-api-prod
```

### 4. Access Services
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432 (geoapi/geoapi/geoapi)
- **Jupyter**: http://localhost:8888

## 🔧 Development Workflow

### Recommended Development Flow:
```bash
# 1. Start infrastructure
make start

# 2. Setup data (first time only)
make setup

# 3. Start API for development
make run-api-dev

# 4. In another terminal - run tests
make test

# 5. Check API status
make api-status

# 6. Stop API (when needed)
make stop-api

# 7. Stop all services
make stop
```

### Why Manual API Start?

The API container doesn't auto-start the FastAPI application for several professional reasons:

1. **🔧 Flexibility**: Developers can start API in different modes (dev/prod)
2. **🐛 Debugging**: Easier to debug startup issues
3. **🧪 Testing**: Can run tests without API interference
4. **📊 Data Setup**: Allows database setup before API starts
5. **🔄 Restart Control**: Quick restart during development

## 📋 Service Management Commands

```bash
# Service lifecycle
make start          # Start database and containers
make stop           # Stop all services
make restart        # Restart all services
make logs           # View container logs

# API management
make run-api-dev     # Start API in development mode
make run-api-prod    # Start API in production mode
make stop-api        # Stop API process
make restart-api     # Restart API
make api-status      # Check API status

# Database operations
make create-tables   # Create database tables
make ingest-data     # Ingest Parquet datasets
make clean-db        # Clean database
make verify-db       # Verify database state

# Development tools
make test            # Run tests
make quality-check   # Code quality checks
make health-check    # Full health check
```

## 🏥 Health Checks

### Database Health
- **Check**: `pg_isready -U geoapi -d geoapi`
- **Interval**: 10s
- **Used by**: API container waits for DB health

### API Health  
- **Check**: `curl -f http://localhost:8000/health`
- **Interval**: 30s
- **Note**: Only works when API is manually started

## 🗂️ Data Persistence

- **Database data**: Stored in Docker volume `db_data`
- **Code changes**: Live-mounted from host (`./:/workspace`)
- **Configuration**: Environment files (`.env`)

## 🔍 Troubleshooting

### Database Issues
```bash
# Check database logs
docker logs geoapi_db_dev

# Connect to database
make db-shell

# Verify database state
make verify-db
```

### API Issues
```bash
# Check API container status
docker ps --filter "name=geoapi_api_dev"

# Access API container
make shell

# Check API logs (when running)
docker logs geoapi_api_dev
```

### Network Issues
```bash
# Check if services can communicate
docker exec geoapi_api_dev ping db

# Check port bindings
docker port geoapi_api_dev
docker port geoapi_db_dev
```

## 🎯 Professional Features

- ✅ Health checks for service readiness
- ✅ Dependent service startup ordering
- ✅ Persistent data volumes
- ✅ Live code reloading
- ✅ Environment-based configuration
- ✅ Comprehensive logging
- ✅ Easy debugging access
- ✅ Production-ready commands
- ✅ Automated database initialization

## 📚 Additional Resources

- [Makefile Commands](../README.md#-commands)
- [API Documentation](http://localhost:8000/docs)
- [Database Schema](../docs/database_schema.md)
- [Development Guide](../docs/development_guide.md)
