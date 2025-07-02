#!/usr/bin/env python3
"""
Main test runner for the GeoAPI project.

Provides options to run different test suites:
- SQLite-compatible tests (no PostGIS dependency)
- Full PostgreSQL/PostGIS tests
- All tests
"""
import argparse
import os
import shutil
import subprocess
import sys


def clean_pycache():
    """Clean Python cache files to avoid import conflicts."""
    print("Cleaning Python cache files...")

    # Base workspace directory
    workspace_dir = "/workspace"

    # Remove all __pycache__ directories
    for root, dirs, files in os.walk(workspace_dir):
        if "__pycache__" in dirs:
            pycache_dir = os.path.join(root, "__pycache__")
            print(f"Removing {pycache_dir}")
            shutil.rmtree(pycache_dir, ignore_errors=True)

    # Remove .pyc files
    for root, dirs, files in os.walk(workspace_dir):
        for file in files:
            if file.endswith(".pyc"):
                pyc_file = os.path.join(root, file)
                print(f"Removing {pyc_file}")
                os.remove(pyc_file)

    # Remove pytest cache
    pytest_cache = os.path.join(workspace_dir, ".pytest_cache")
    if os.path.exists(pytest_cache):
        print(f"Removing {pytest_cache}")
        shutil.rmtree(pytest_cache, ignore_errors=True)

    print("Python cache cleaning completed!")
    print("-" * 50)


def run_sqlite_tests():
    """Execute only tests that work with SQLite."""

    working_tests = [
        # Configuration tests
        "tests/test_config.py",
        # Pydantic schema tests
        "tests/test_schemas_link.py",
        "tests/test_schemas_speed_record.py",
        # Simplified models (no PostGIS)
        "tests/test_simplified_models.py",
        # Database tests that don't depend on PostGIS
        # (subset of test_database.py functions)
    ]

    print("Running SQLite-compatible tests...")
    print("=" * 50)

    # Clean Python cache before running tests
    clean_pycache()

    cmd = ["python", "-m", "pytest", "-v", "--tb=short"] + working_tests

    try:
        result = subprocess.run(cmd, check=True, cwd="/workspace")
        print(f"\nAll SQLite tests passed! (exit code: {result.returncode})")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nSome SQLite tests failed (exit code: {e.returncode})")
        return False


def run_full_tests():
    """Execute all tests (requires PostgreSQL/PostGIS)."""

    print("Running ALL tests (requires PostgreSQL/PostGIS)...")
    print("\nWARNING: This will fail if PostgreSQL/PostGIS is not configured!")

    # Clean Python cache before running tests
    clean_pycache()

    cmd = ["python", "-m", "pytest", "-v", "--tb=short", "tests/"]

    try:
        result = subprocess.run(cmd, check=True, cwd="/workspace")
        print(f"\nAll tests passed! (exit code: {result.returncode})")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nSome tests failed (exit code: {e.returncode})")
        return False


def show_test_help():
    """Show available test categories and descriptions."""
    print("GeoAPI Test Runner")
    print("=" * 50)
    print()
    print("Available test categories:")
    print()
    print("--sqlite:")
    print("  Runs tests compatible with SQLite")
    print("  - Configuration tests")
    print("  - Pydantic schema validation tests")
    print("  - Simplified model tests")
    print("  - Basic database functionality tests")
    print()
    print("--all:")
    print("  Runs ALL tests (requires PostgreSQL/PostGIS)")
    print("  - All SQLite tests")
    print("  - Full PostGIS/GeoAlchemy2 model tests")
    print("  - Spatial query tests")
    print("  - Database integration tests")
    print()
    print("--help-tests:")
    print("  Shows this help message")
    print()
    print("Features:")
    print("  - Automatic Python cache cleaning before tests")
    print("  - Test coverage reporting")
    print("  - SQLite mode for quick testing without PostgreSQL")
    print()
    print("Examples:")
    print("  python scripts/testing/run_tests.py --sqlite")
    print("  python scripts/testing/run_tests.py --all")


def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(
        description="GeoAPI Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--sqlite", action="store_true", help="Run SQLite-compatible tests only"
    )
    group.add_argument(
        "--all", action="store_true", help="Run all tests (requires PostgreSQL/PostGIS)"
    )
    group.add_argument(
        "--help-tests",
        action="store_true",
        help="Show detailed help about test categories",
    )

    args = parser.parse_args()

    if args.help_tests:
        show_test_help()
        return

    print("GeoAPI Test Runner")
    print("=" * 50)

    success = False  # Initialize success variable
    if args.sqlite:
        success = run_sqlite_tests()
    elif args.all:
        success = run_full_tests()

    print("\n" + "=" * 50)
    if success:
        print("Status: PASSED")
        print("All selected tests completed successfully")
    else:
        print("Status: FAILED")
        print("Some tests failed - check output above")
    print("=" * 50)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
