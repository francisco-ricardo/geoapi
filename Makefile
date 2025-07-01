# GeoSpatial Links API - Development Makefile
# Commands for development using Docker containers from host

.PHONY: help setup start stop restart logs create-tables ingest-data run-api run-api-dev run-api-prod check-api stop-api restart-api api-status test test-all test-unit test-api health-check clean-db analyze-data validate-ingestion verify-db verify-postgis test-coverage test-models test-schemas test-core test-middleware test-database test-logging clean-pycache format format-check type-check type-check-strict sort-imports sort-imports-check quality-check clean-empty-files install-quality-tools

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
	@echo "  validate-ingestion - Validate data ingestion integrity"
	@echo "  verify-db   - Verify database state"
	@echo "  verify-postgis - Verify PostGIS spatial data"
	@echo "  run-api     - Start FastAPI with uvicorn"
	@echo "  run-api-dev - Start FastAPI in development mode"
	@echo "  run-api-prod- Start FastAPI in production mode"
	@echo "  check-api   - Quick check if API is responding (curl /health)"
	@echo "  api-status  - Show detailed API and container status"
	@echo "  health-check- Complete health check (API + endpoints + docs)"
	@echo "  stop-api    - Stop API process (uvicorn)"
	@echo "  restart-api - Restart API process"
	@echo "  test        - Run unit tests"
	@echo "  test-all    - Run all unit tests (comprehensive)"
	@echo "  test-unit   - Run unit tests only"
	@echo "  test-api    - Test API endpoints (using test script)"
	@echo "  test-coverage - Run tests with coverage reports"
	@echo "  test-models     - Run model tests only"
	@echo "  test-schemas    - Run schema tests only" 
	@echo "  test-core       - Run core functionality tests"
	@echo "  test-middleware - Run middleware tests only"
	@echo "  test-database   - Run database tests only"
	@echo "  test-logging    - Run logging system tests"
	@echo "  format          - Format code with Black"
	@echo "  format-check    - Check code formatting"
	@echo "  type-check      - Run mypy type checking"
	@echo "  type-check-strict - Run strict type checking"
	@echo "  sort-imports    - Sort imports with isort"
	@echo "  sort-imports-check - Check import sorting"
	@echo "  quality-check   - Run all quality checks"
	@echo "  clean-empty-files - Remove empty Python files"
	@echo ""
	@echo "API Health & Status Commands:"
	@echo "  check-api   - Quick API health check (fast)"
	@echo "  api-status  - Detailed container and API status"
	@echo "  health-check- Complete system health validation"
	@echo ""
	@echo "Database Commands:"
	@echo "  clean-db    - Clean database (drop all tables)"
	@echo "  clean-pycache - Clean Python cache files"
	@echo "  shell       - Open shell in API container"
	@echo ""
	@echo "Quick start for new users:"
	@echo "  make start"
	@echo "  make setup"
	@echo ""
	@echo "API Verification Commands (choose based on your need):"
	@echo "  check-api   - Fast ping test (just curl /health)"
	@echo "  api-status  - Container status + API info + endpoints"
	@echo "  health-check- Full validation (API + docs + all endpoints)"
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

# Test coverage with extended tests
test-extended-coverage: clean-pycache
	@echo "Running extended coverage tests..."
	@docker exec $(API_CONTAINER) bash scripts/testing/run_extended_coverage.sh

# Run all tests with full coverage
test-full-coverage: clean-pycache
	@echo "Running all tests with full coverage..."
	@docker exec $(API_CONTAINER) bash scripts/run_all_tests_clean.sh

# Create database tables
create-tables:
	@echo "Creating database tables..."
	@docker exec $(API_CONTAINER) python scripts/database/create_tables.py

# Ingest datasets into database
ingest-data:
	@echo "Ingesting Parquet datasets..."
	@docker exec $(API_CONTAINER) python scripts/data/ingest_datasets.py

# Start the FastAPI application with uvicorn
run-api:
	@echo "Starting FastAPI application with uvicorn..."
	@docker exec $(API_CONTAINER) uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start FastAPI in development mode (with auto-reload)
run-api-dev:
	@echo "Starting FastAPI in development mode..."
	@docker exec -it $(API_CONTAINER) uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

# Start FastAPI in production mode
run-api-prod:
	@echo "Starting FastAPI in production mode..."
	@docker exec $(API_CONTAINER) uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Check if API is running
check-api:
	@echo "Quick API health check..."
	@curl -f http://localhost:8000/health 2>/dev/null && echo "✅ API is running!" || echo "❌ API is not responding"

# Stop API process in container (kill uvicorn)
stop-api:
	@echo "Stopping API process..."
	@docker exec $(API_CONTAINER) pkill -f uvicorn || echo "No uvicorn process found"

# Restart API process
restart-api: stop-api run-api-dev

# Show API status and endpoints
api-status:
	@echo "=== DETAILED API STATUS ==="
	@echo "Container status:"
	@docker ps --filter "name=$(API_CONTAINER)" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "API Health Check:"
	@curl -s http://localhost:8000/health 2>/dev/null | head -c 200 || echo "API not responding"
	@echo ""
	@echo "=== Access Points ==="
	@echo "API Server: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Health Check: http://localhost:8000/health"

# Run tests
test: clean-pycache
	@echo "Running unit tests..."
	@docker exec $(API_CONTAINER) python -m pytest tests/unit/ -v

# Run all tests (unit only - no integration tests exist yet)
test-all: clean-pycache
	@echo "Running ALL unit tests..."
	@docker exec $(API_CONTAINER) python -m pytest tests/unit/ -v

# Run unit tests only
test-unit: clean-pycache
	@echo "Running unit tests..."
	@docker exec $(API_CONTAINER) python -m pytest tests/unit/ -v

# Run tests with coverage
test-coverage: clean-pycache
	@echo "Running tests with coverage..."
	@docker exec $(API_CONTAINER) python -m pytest tests/unit/ --cov=app --cov-report=html --cov-report=xml --cov-report=term

# Run model tests only
test-models: clean-pycache
	@echo "Running model tests..."
	@docker exec $(API_CONTAINER) python -m pytest tests/unit/models/ -v

# Run schema tests only
test-schemas: clean-pycache
	@echo "Running schema tests..."
	@docker exec $(API_CONTAINER) python -m pytest tests/unit/schemas/ -v

# Run core functionality tests
test-core: clean-pycache
	@echo "Running core functionality tests..."
	@docker exec $(API_CONTAINER) python -m pytest tests/unit/core/ -v

# Run middleware tests only
test-middleware: clean-pycache
	@echo "Running middleware tests..."
	@docker exec $(API_CONTAINER) python -m pytest tests/unit/middleware/ -v

# Test API endpoints using test script
test-api: clean-pycache
	@echo "Testing API endpoints..."
	@docker exec $(API_CONTAINER) python scripts/testing/test_endpoints.py

# Health check
health-check:
	@echo "Running comprehensive health checks..."
	@echo "(Tests API health, documentation, and main endpoints)"
	@docker exec $(API_CONTAINER) python scripts/health_check.py

# Clean database (drop all tables)
clean-db:
	@echo "Cleaning database..."
	@docker exec $(API_CONTAINER) python -c "from app.core.database import Base, get_engine; Base.metadata.drop_all(bind=get_engine()); print('All tables dropped')"

# Data analysis and verification commands
analyze-data:
	@echo "Analyzing original Parquet datasets..."
	@docker exec $(API_CONTAINER) python scripts/data/analyze_data.py

# Validate data ingestion integrit
validate-ingestion:
	@echo "Validating data ingestion integrity..."
	@docker exec $(API_CONTAINER) python scripts/data/validate_ingestion.py

# Verify database state
verify-db:
	@echo "..."
	@docker exec $(API_CONTAINER) python scripts/database/verify_database.py

# Verify PostGIS spatial data
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

# Test coverage commands - updated for new structure
test-coverage-detailed: clean-pycache
	@echo "Running detailed coverage analysis..."
	@docker exec $(API_CONTAINER) python -m pytest tests/unit/ --cov=app --cov-report=html --cov-report=xml --cov-report=term --cov-branch

# Database and API verification
test-database: clean-pycache
	@echo "Running database tests..."
	@docker exec $(API_CONTAINER) python -m pytest tests/unit/core/test_database.py -v

test-logging: clean-pycache
	@echo "Running logging system tests..."
	@docker exec $(API_CONTAINER) python -m pytest tests/unit/core/test_logging.py -v

# ==============================================================================
# CODE QUALITY COMMANDS
# ==============================================================================

# Code formatting with Black
format:
	@echo "Formatting code with Black..."
	@docker exec $(API_CONTAINER) python -m black app/ tests/ scripts/ --line-length 88

format-check:
	@echo "Checking code formatting..."
	@docker exec $(API_CONTAINER) python -m black app/ tests/ scripts/ --check --line-length 88

# Type checking with mypy
type-check:
	@echo "Running mypy type checking..."
	@docker exec $(API_CONTAINER) python -m mypy app/ --ignore-missing-imports

type-check-strict:
	@echo "Running strict mypy type checking..."
	@docker exec $(API_CONTAINER) python -m mypy app/ --strict --ignore-missing-imports

# Import sorting with isort
sort-imports:
	@echo "Sorting imports with isort..."
	@docker exec $(API_CONTAINER) python -m isort app/ tests/ scripts/ --profile black

sort-imports-check:
	@echo "Checking import sorting..."
	@docker exec $(API_CONTAINER) python -m isort app/ tests/ scripts/ --check-only --profile black

# Combined quality check
quality-check: format-check type-check sort-imports-check
	@echo "All quality checks passed! ✅"

# Install quality tools (if not already installed)
install-quality-tools:
	@echo "Installing quality tools..."
	@docker exec $(API_CONTAINER) pip install black mypy isort

# Clean empty files that VS Code might recreate
clean-empty-files:
	@echo "Cleaning empty Python files..."
	@bash scripts/clean_empty_files.sh
