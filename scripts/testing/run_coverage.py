#!/usr/bin/env python3
"""
Run tests with coverage reports.

This script allows running tests with detailed coverage reports for:
- Specific modules
- Different test categories
- Full test suite

Coverage results are available in:
- Terminal output (summary)
- HTML report (detailed, in coverage_html/)
- XML report (for CI integration, in coverage.xml)
"""
import subprocess
import sys
import argparse
from pathlib import Path
import os


def run_coverage_test(module=None, category=None):
    """
    Run tests with coverage for a specific module or category.
    
    Args:
        module: Optional module path to test (e.g., 'app.core.logging')
        category: Optional test category (basic, schema, database, api, logging)
    
    Returns:
        bool: True if tests passed, False otherwise
    """
    # Set up command
    cmd = ["python", "-m", "pytest"]
    
    # Add coverage options
    if module:
        cmd.extend([f"--cov={module}"])
    else:
        cmd.extend(["--cov=app"])
    
    # Add category if specified
    if category:
        if category == "basic":
            cmd.extend([
                "tests/test_config.py",
                "tests/test_schemas_link.py",
                "tests/test_schemas_speed_record.py",
                "tests/test_simplified_models.py",
            ])
        elif category == "schema":
            cmd.extend([
                "tests/test_schemas_link.py",
                "tests/test_schemas_speed_record.py",
            ])
        elif category == "database":
            cmd.extend([
                "tests/test_database.py",
                "tests/test_models/test_link.py",
                "tests/test_models/test_speed_record.py",
                "tests/test_models.py",
            ])
        elif category == "api":
            cmd.extend([
                "tests/test_api",
            ])
        elif category == "logging":
            cmd.extend([
                "tests/test_logging.py",
            ])
    
    # Add formatting options
    cmd.extend([
        "--cov-report=term",
        "--cov-report=html:coverage_html",
        "--cov-report=xml:coverage.xml",
        "-v",
    ])
    
    print(f"\nRunning tests with coverage: {' '.join(cmd)}")
    print("-" * 80)
    
    try:
        result = subprocess.run(cmd, check=True, cwd="/workspace")
        print("\nTests completed successfully!")
        
        # Display path to HTML report
        coverage_path = os.path.join(os.getcwd(), "coverage_html", "index.html")
        print(f"\nDetailed HTML coverage report available at:")
        print(f"  file://{coverage_path}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nSome tests failed (exit code: {e.returncode})")
        return False


def main():
    """Main entry point for the coverage test runner."""
    
    parser = argparse.ArgumentParser(
        description="Run tests with coverage reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests with coverage for all modules
  python scripts/testing/run_coverage.py

  # Run tests with coverage for a specific module
  python scripts/testing/run_coverage.py --module app.core.logging

  # Run specific category of tests
  python scripts/testing/run_coverage.py --category logging

  # Run database tests with coverage for database module
  python scripts/testing/run_coverage.py --category database --module app.core.database
        """
    )
    
    parser.add_argument(
        "--module",
        help="Specific module to measure coverage for (e.g., app.core.logging)"
    )
    
    parser.add_argument(
        "--category",
        choices=["basic", "schema", "database", "api", "logging", "all"],
        default="all",
        help="Category of tests to run (default: all)"
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("TEST COVERAGE RUNNER")
    print("=" * 80)
    
    # Check if we're in the right directory
    if not Path("/workspace/tests").exists():
        print("Error: Tests directory not found. Make sure you're in the project root.")
        sys.exit(1)
    
    # Run tests with coverage
    success = run_coverage_test(module=args.module, category=args.category if args.category != "all" else None)
    
    # Exit with appropriate code
    if success:
        print("\n" + "=" * 80)
        print("COVERAGE TEST RESULTS: PASSED")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("COVERAGE TEST RESULTS: FAILED")
        print("=" * 80)
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
