#!/usr/bin/env python3
"""
Test runner for specific test categories.

This script allows running different categories of tests:
- Basic tests (no database dependencies)
- Schema tests (Pydantic validation)
- Database tests (PostgreSQL/PostGIS required)
- All tests
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run_basic_tests():
    """Run tests that don't require database connection."""

    basic_tests = [
        # Configuration tests
        "tests/test_config.py",
        # Schema validation tests
        "tests/test_schemas_link.py",
        "tests/test_schemas_speed_record.py",
        # Simplified model tests (no database)
        "tests/test_simplified_models.py",
    ]

    print("Running basic tests (no database required)...")
    print(f"Test files: {len(basic_tests)}")
    for test in basic_tests:
        print(f"  - {test}")

    return run_pytest_command(basic_tests)


def run_schema_tests():
    """Run Pydantic schema validation tests."""

    schema_tests = [
        "tests/test_schemas_link.py",
        "tests/test_schemas_speed_record.py",
    ]

    print("Running schema validation tests...")
    print(f"Test files: {len(schema_tests)}")
    for test in schema_tests:
        print(f"  - {test}")

    return run_pytest_command(schema_tests)


def run_database_tests():
    """Run tests that require database connection."""

    database_tests = [
        # Database connection tests
        "tests/test_database.py",
        # Model tests (with database)
        "tests/test_models/test_link.py",
        "tests/test_models/test_speed_record.py",
        # Full model tests
        "tests/test_models.py",
    ]

    print("Running database tests (PostgreSQL/PostGIS required)...")
    print(f"Test files: {len(database_tests)}")
    for test in database_tests:
        print(f"  - {test}")

    return run_pytest_command(database_tests)


def run_all_tests():
    """Run all available tests."""

    print("Running all tests...")

    # Run pytest on the entire tests directory
    cmd = ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]

    try:
        result = subprocess.run(cmd, check=True, cwd="/workspace")
        print("\nAll tests completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nSome tests failed (exit code: {e.returncode})")
        return False


def run_pytest_command(test_files):
    """Run pytest with specified test files."""

    cmd = ["python", "-m", "pytest"] + test_files + ["-v", "--tb=short"]

    print(f"\nRunning command: {' '.join(cmd)}")
    print("-" * 60)

    try:
        result = subprocess.run(cmd, check=True, cwd="/workspace")
        print(f"\nTests completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nSome tests failed (exit code: {e.returncode})")
        return False


def main():
    """Main entry point for the test runner."""

    parser = argparse.ArgumentParser(
        description="Run specific categories of tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Categories:
  basic     - Tests that don't require database (config, schemas, simplified models)
  schema    - Pydantic schema validation tests only
  database  - Tests that require PostgreSQL/PostGIS connection
  all       - All available tests

Examples:
  python scripts/testing/run_tests.py basic
  python scripts/testing/run_tests.py schema
  python scripts/testing/run_tests.py database
  python scripts/testing/run_tests.py all
        """,
    )

    parser.add_argument(
        "category",
        choices=["basic", "schema", "database", "all"],
        help="Category of tests to run",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("TEST RUNNER")
    print("=" * 60)

    # Check if we're in the right directory
    if not Path("/workspace/tests").exists():
        print("Error: Tests directory not found. Make sure you're in the project root.")
        sys.exit(1)

    # Run the selected test category
    success = False

    if args.category == "basic":
        success = run_basic_tests()
    elif args.category == "schema":
        success = run_schema_tests()
    elif args.category == "database":
        success = run_database_tests()
    elif args.category == "all":
        success = run_all_tests()

    # Exit with appropriate code
    if success:
        print("\n" + "=" * 60)
        print("TEST RESULTS: PASSED")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("TEST RESULTS: FAILED")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest run interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
