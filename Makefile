# GeoSpatial Links API - Development Makefile
# Commands for development using Docker containers from host

.PHONY: help setup start stop restart logs create-tables ingest-data run-api test test-all test-api health-check clean-db analyze-data verify-db verify-postgis test-coverage test-logging test-middleware test-exceptions clean-pycache

# Container names from docker-compose-dev.yml
API_CONTAINER = geoapi_api_dev
DB_CONTAINER = geoapi_db_dev

# Default target
help:
	@echo "GeoSpatial Links API - Development Commands"
	@echo "==========================================="
	@echo ""
	@echo "Available commands:"
	@echo "  start       - Start all services (database + API)"
	@echo "  stop        - Stop all services"
	@echo "  restart     - Restart all services"
	@echo "  logs        - View container logs"
	@echo "  setup       - Complete setup (start + tables + ingest)"
	@echo "  create-tables - Create database tables"
	@echo "  ingest-data - Ingest Parquet datasets into database"
	@echo "  run-api     - Start the FastAPI application"
	@echo "  test        - Run SQLite-compatible tests"
	@echo "  test-all    - Run all tests (requires PostgreSQL)"
	@echo "  test-api    - Test API endpoints"
	@echo "  test-coverage - Run tests with coverage reports"
	@echo "  test-logging - Run logging system tests"
	@echo "  test-middleware - Run middleware tests"
	@echo "  test-exceptions - Run exception handler tests"
	@echo "  health-check- Check database and API health"
	@echo "  clean-db    - Clean database (drop all tables)"
	@echo "  clean-pycache - Clean Python cache files"
	@echo "  shell       - Open shell in API container"
	@echo ""
	@echo "Quick start for new users:"
	@echo "  make start"
	@echo "  make setup"
	@echo ""
	@echo "Access points after setup:"
	@echo "  API: http://localhost:8000"
	@echo "  Docs: http://localhost:8000/docs"

# Start all services
start:
	@echo "Starting all services..."
	@docker-compose -f docker-compose-dev.yml up -d

# Stop all services
stop:
	@echo "Stopping all services..."
	@docker-compose -f docker-compose-dev.yml down

# Restart all services
restart: stop start
	@echo "Services restarted!"

# View logs
logs:
	@docker-compose -f docker-compose-dev.yml logs -f

# Complete automated setup
setup: start
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Creating database tables..."
	@docker exec $(API_CONTAINER) python scripts/database/create_tables.py
	@echo "Ingesting datasets..."
	@docker exec $(API_CONTAINER) python scripts/data/ingest_datasets.py
	@echo "Setup complete!"

# Create database tables
create-tables:
	@echo "Creating database tables..."
	@docker exec $(API_CONTAINER) python scripts/database/create_tables.py

# Ingest datasets into database
ingest-data:
	@echo "Ingesting Parquet datasets..."
	@docker exec $(API_CONTAINER) python scripts/data/ingest_datasets.py

# Start the FastAPI application (already running in container)
run-api:
	@echo "FastAPI is already running in container $(API_CONTAINER)"
	@echo "Access at: http://localhost:8000"
	@echo "Docs at: http://localhost:8000/docs"

# Run tests
test: clean-pycache
	@echo "Running all tests..."
	@docker exec $(API_CONTAINER) python scripts/testing/run_tests.py --sqlite

# Run all tests (including PostGIS)
test-all: clean-pycache
	@echo "Running ALL tests (requires PostgreSQL/PostGIS)..."
	@docker exec $(API_CONTAINER) python scripts/testing/run_tests.py --all

# Test API endpoints
test-api: clean-pycache
	@echo "Testing API endpoints..."
	@docker exec $(API_CONTAINER) python scripts/testing/test_endpoints.py

# Health check
health-check:
	@echo "Running health checks..."
	@docker exec $(API_CONTAINER) python scripts/health_check.py

# Clean database (drop all tables)
clean-db:
	@echo "Cleaning database..."
	@docker exec $(API_CONTAINER) python -c "from app.core.database import Base, get_engine; Base.metadata.drop_all(bind=get_engine()); print('All tables dropped')"

# Data analysis and verification commands
analyze-data:
	@echo "Analyzing original Parquet datasets..."
	@docker exec $(API_CONTAINER) python scripts/data/analyze_data.py

validate-ingestion:
	@echo "Validating data ingestion integrity..."
	@docker exec $(API_CONTAINER) python scripts/data/validate_ingestion.py

verify-db:
	@echo "Verifying database state..."
	@docker exec $(API_CONTAINER) python scripts/database/verify_database.py

verify-postgis:
	@echo "Verifying PostGIS spatial data..."
	@docker exec $(API_CONTAINER) python scripts/database/verify_postgis.py

# Open shell in API container
shell:
	@echo "Opening shell in API container..."
	@docker exec -it $(API_CONTAINER) bash

# Database shell
db-shell:
	@echo "Opening database shell..."
	@docker exec -it $(DB_CONTAINER) psql -U geoapi -d geoapi

# Test coverage commands
test-coverage: clean-pycache
	@echo "Running tests with coverage reports..."
	@docker exec $(API_CONTAINER) python scripts/testing/run_coverage.py

test-logging: clean-pycache
	@echo "Running logging system tests..."
	@docker exec $(API_CONTAINER) python scripts/testing/run_coverage.py --category logging --module app.core.logging

test-middleware: clean-pycache
	@echo "Running middleware tests..."
	@docker exec $(API_CONTAINER) python scripts/testing/run_coverage.py --category logging --module app.middleware.logging_middleware

test-exceptions: clean-pycache
	@echo "Running exception handler tests..."
	@docker exec $(API_CONTAINER) python scripts/testing/run_coverage.py --category logging --module app.core.exceptions

# Clean Python cache
clean-pycache:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache .mypy_cache .pylint.d
