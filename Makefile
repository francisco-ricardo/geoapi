# GeoSpatial Links API - Development Makefile
# Simple commands for development environment setup and management

.PHONY: help setup start stop restart logs test clean

# Default target
help:
	@echo "GeoSpatial Links API - Development Commands"
	@echo "==========================================="
	@echo ""
	@echo "Available commands:"
	@echo "  setup     - Complete setup (containers + database + API)"
	@echo "  start     - Start all services"
	@echo "  stop      - Stop all services"
	@echo "  restart   - Restart all services"
	@echo "  logs      - View container logs"
	@echo "  test      - Run all tests"
	@echo "  test-api  - Test API endpoints"
	@echo "  clean     - Clean containers and volumes"
	@echo "  db-reset  - Reset database (recreate containers)"
	@echo ""
	@echo "Quick start for new users:"
	@echo "  make setup"
	@echo ""
	@echo "Access points after setup:"
	@echo "  API: http://localhost:8000"
	@echo "  Docs: http://localhost:8000/docs"

# Complete automated setup
setup:
	@echo "Starting complete setup..."
	@python scripts/setup/complete_setup.py

# Start services
start:
	@echo "Starting services..."
	@docker compose -f docker-compose-dev.yml up -d

# Stop services
stop:
	@echo "Stopping services..."
	@docker compose -f docker-compose-dev.yml down

# Restart services
restart: stop start
	@echo "Services restarted!"

# View logs
logs:
	@docker compose -f docker-compose-dev.yml logs -f

# Run tests
test:
	@echo "Running all tests..."
	@python scripts/testing/run_tests.py

# Test API endpoints
test-api:
	@echo "Testing API endpoints..."
	@python scripts/testing/test_endpoints.py

# Clean everything
clean:
	@echo "Cleaning containers and volumes..."
	@docker compose -f docker-compose-dev.yml down -v --remove-orphans
	@docker system prune -f

# Reset database (recreate containers)
db-reset:
	@echo "Resetting database..."
	@docker compose -f docker-compose-dev.yml down -v
	@docker compose -f docker-compose-dev.yml up -d db
	@echo "Waiting for database to be ready..."
	@sleep 10
	@docker compose -f docker-compose-dev.yml up -d api
	@echo "Database reset complete!"

# Quick development commands
dev-logs:
	@docker compose -f docker-compose-dev.yml logs -f api

dev-shell:
	@docker compose -f docker-compose-dev.yml exec api bash

db-shell:
	@docker compose -f docker-compose-dev.yml exec db psql -U geoapi -d geoapi
