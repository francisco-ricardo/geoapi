# GeoSpatial Links API - Development Makefile
# Commands for development using Docker containers from host

.PHONY: help setup start stop restart logs create-tables ingest-data run-api test test-api health-check clean-db

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
	@echo "  test        - Run all tests"
	@echo "  test-api    - Test API endpoints"
	@echo "  health-check- Check database and API health"
	@echo "  clean-db    - Clean database (drop all tables)"
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
test:
	@echo "Running all tests..."
	@docker exec $(API_CONTAINER) python scripts/testing/run_tests.py

# Test API endpoints
test-api:
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

# Open shell in API container
shell:
	@echo "Opening shell in API container..."
	@docker exec -it $(API_CONTAINER) bash

# Database shell
db-shell:
	@echo "Opening database shell..."
	@docker exec -it $(DB_CONTAINER) psql -U geoapi -d geoapi
