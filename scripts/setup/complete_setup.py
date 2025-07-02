#!/usr/bin/env python3
"""
Complete project setup script for development environment.

This script handles the complete setup process:
1. Environment verification
2. Docker containers setup
3. Database initialization
4. API testing
5. Sample data validation

Designed to make it easy for interviewers to test the API after cloning the repo.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_step(step_num, title):
    """Print a formatted step."""
    print(f"\n[{step_num}] {title}")
    print("-" * 60)


def run_command(command, description, check_output=False):
    """Run a command with proper error handling."""
    print(f"Running: {description}")
    print(f"Command: {command}")

    try:
        if check_output:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                cwd="/workspace",
            )
            return result.stdout.strip()
        else:
            result = subprocess.run(command, shell=True, check=True, cwd="/workspace")
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if check_output and e.stdout:
            print(f"Output: {e.stdout}")
        if check_output and e.stderr:
            print(f"Error output: {e.stderr}")
        return False


def check_prerequisites():
    """Check if required tools are installed."""
    print_step(1, "CHECKING PREREQUISITES")

    tools = {"docker": "docker --version", "docker-compose": "docker compose version"}

    missing_tools = []

    for tool, command in tools.items():
        print(f"Checking {tool}...")
        result = run_command(command, f"Check {tool}", check_output=True)
        if result:
            print(f"  {tool}: OK")
        else:
            missing_tools.append(tool)
            print(f"  {tool}: MISSING")

    if missing_tools:
        print(f"\nERROR: Missing required tools: {', '.join(missing_tools)}")
        print("Please install Docker and Docker Compose before continuing.")
        return False

    print("\nAll prerequisites satisfied!")
    return True


def setup_environment():
    """Setup environment files."""
    print_step(2, "SETTING UP ENVIRONMENT")

    env_file = Path("/workspace/.env")
    env_example = Path("/workspace/.env.example")

    if not env_file.exists():
        if env_example.exists():
            print("Copying .env.example to .env...")
            run_command("cp .env.example .env", "Copy environment file")
        else:
            print("Creating default .env file...")
            default_env = """# Database Configuration
DATABASE_URL=postgresql://geoapi:geoapi@localhost:5432/geoapi
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=geoapi
DATABASE_USER=geoapi
DATABASE_PASSWORD=geoapi

# Application Configuration
DEBUG=true
LOG_LEVEL=INFO
API_TITLE=GeoSpatial Links API
API_VERSION=1.0.0
"""
            with open(env_file, "w") as f:
                f.write(default_env)

    print("Environment file ready!")
    return True


def start_containers():
    """Start Docker containers."""
    print_step(3, "STARTING DOCKER CONTAINERS")

    print("Stopping any existing containers...")
    run_command("docker compose -f docker-compose-dev.yml down", "Stop containers")

    print("Starting containers...")
    result = run_command(
        "docker compose -f docker-compose-dev.yml up -d db", "Start database container"
    )

    if not result:
        print("Failed to start containers!")
        return False

    print("Containers started successfully!")
    return True


def wait_for_database():
    """Wait for database to be ready."""
    print_step(4, "WAITING FOR DATABASE")

    max_attempts = 30
    attempt = 0

    print("Waiting for PostgreSQL/PostGIS to be ready...")

    while attempt < max_attempts:
        attempt += 1
        print(f"Attempt {attempt}/{max_attempts}...")

        # Check if database container is healthy
        result = run_command(
            "docker compose -f docker-compose-dev.yml exec db pg_isready -U geoapi -d geoapi",
            "Check database readiness",
            check_output=True,
        )

        if result and isinstance(result, str) and "accepting connections" in result:
            print("Database is ready!")
            return True

        time.sleep(2)

    print("Database failed to start within timeout!")
    return False


def verify_database_setup():
    """Verify database tables and data."""
    print_step(5, "VERIFYING DATABASE SETUP")

    # Check if tables exist
    check_tables_sql = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name;
    """

    result = run_command(
        f'docker compose -f docker-compose-dev.yml exec db psql -U geoapi -d geoapi -c "{check_tables_sql}"',
        "Check database tables",
        check_output=True,
    )

    if (
        result
        and isinstance(result, str)
        and "links" in result
        and "speed_records" in result
    ):
        print("Database tables created successfully!")

        # Check sample data
        count_sql = "SELECT COUNT(*) FROM links;"
        result = run_command(
            f'docker compose -f docker-compose-dev.yml exec db psql -U geoapi -d geoapi -c "{count_sql}"',
            "Check sample data",
            check_output=True,
        )

        if (
            result
            and isinstance(result, str)
            and any(char.isdigit() for char in result)
        ):
            print("Sample data loaded successfully!")
            return True

    print("Database verification failed!")
    return False


def start_api():
    """Start the API server."""
    print_step(6, "STARTING API SERVER")

    print("Starting API container...")
    result = run_command(
        "docker compose -f docker-compose-dev.yml up -d api", "Start API container"
    )

    if not result:
        print("Failed to start API container!")
        return False

    # Wait for API to be ready
    max_attempts = 20
    attempt = 0

    print("Waiting for API to be ready...")

    while attempt < max_attempts:
        attempt += 1
        print(f"Attempt {attempt}/{max_attempts}...")

        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("API is ready!")
                return True
        except requests.RequestException:
            pass

        time.sleep(2)

    print("API failed to start within timeout!")
    return False


def test_api_endpoints():
    """Test key API endpoints."""
    print_step(7, "TESTING API ENDPOINTS")

    tests = [
        {
            "name": "Health Check",
            "method": "GET",
            "url": "http://localhost:8000/health",
            "expected_status": 200,
        },
        {
            "name": "API Root",
            "method": "GET",
            "url": "http://localhost:8000/",
            "expected_status": 200,
        },
        {
            "name": "OpenAPI Docs",
            "method": "GET",
            "url": "http://localhost:8000/docs",
            "expected_status": 200,
        },
        {
            "name": "Get Links",
            "method": "GET",
            "url": "http://localhost:8000/api/v1/links/",
            "expected_status": 200,
        },
    ]

    all_passed = True

    for test in tests:
        print(f"\nTesting: {test['name']}")
        response = None
        try:
            if test["method"] == "GET":
                response = requests.get(test["url"], timeout=10)

            if response and response.status_code == test["expected_status"]:
                print(f"  PASS: {response.status_code}")
                if response.headers.get("content-type", "").startswith(
                    "application/json"
                ):
                    try:
                        data = response.json()
                        print(f"  Response: {json.dumps(data, indent=2)[:200]}...")
                    except:
                        pass
            elif response:
                print(
                    f"  FAIL: Expected {test['expected_status']}, got {response.status_code}"
                )
                all_passed = False
            else:
                print(f"  FAIL: No response received")
                all_passed = False

        except requests.RequestException as e:
            print(f"  ERROR: {e}")
            all_passed = False

    return all_passed


def print_success_info():
    """Print success information and next steps."""
    print_header("SETUP COMPLETED SUCCESSFULLY!")

    print(
        """
The GeoSpatial Links API is now running and ready for testing!

ACCESS POINTS:
- API Server: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Database: localhost:5432 (user: geoapi, db: geoapi)

SAMPLE API CALLS:
- GET http://localhost:8000/api/v1/links/
- POST http://localhost:8000/api/v1/links/ (with GeoJSON data)

TESTING COMMANDS:
- Run all tests: python scripts/testing/run_tests.py
- Test schemas: python scripts/testing/run_tests_by_category.py schema
- Test endpoints: python scripts/testing/test_endpoints.py
- Demo schemas: python scripts/demo/schemas_basic.py

CONTAINER MANAGEMENT:
- View logs: docker compose -f docker-compose-dev.yml logs -f
- Stop services: docker compose -f docker-compose-dev.yml down
- Restart: docker compose -f docker-compose-dev.yml restart

The database includes sample data for immediate testing.
"""
    )


def main():
    """Main setup function."""
    print_header("GEOSPATIAL LINKS API - DEVELOPMENT SETUP")
    print("Automated setup for easy testing after cloning the repository")

    # Check if we're in the right directory
    if (
        not Path("/workspace/app").exists()
        or not Path("/workspace/docker-compose-dev.yml").exists()
    ):
        print("ERROR: This script must be run from the project root directory.")
        print("Current directory should contain 'app/' and 'docker-compose-dev.yml'")
        sys.exit(1)

    # Run setup steps
    steps = [
        ("Prerequisites", check_prerequisites),
        ("Environment", setup_environment),
        ("Docker Containers", start_containers),
        ("Database Ready", wait_for_database),
        ("Database Setup", verify_database_setup),
        ("API Server", start_api),
        ("API Testing", test_api_endpoints),
    ]

    for step_name, step_func in steps:
        if not step_func():
            print(f"\nSETUP FAILED at step: {step_name}")
            print("\nTroubleshooting:")
            print("1. Check Docker is running: docker info")
            print(
                "2. Check container logs: docker compose -f docker-compose-dev.yml logs"
            )
            print(
                "3. Reset containers: docker compose -f docker-compose-dev.yml down -v"
            )
            sys.exit(1)

    print_success_info()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during setup: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
