#!/usr/bin/env python3
"""
Test coverage runner that works both from host and within container.

This script detects whether it's being run from the host or from within
the container and executes the appropriate command for running test coverage.

When run from the host, it uses docker exec to run the tests inside the container.
When run from within the container, it directly executes the coverage tests.
"""
import subprocess
import sys
import os
import argparse


def is_running_in_container():
    """
    Detect if we're running inside a Docker container.
    
    Returns:
        bool: True if running in a container, False otherwise
    """
    # Method 1: Check for .dockerenv file
    if os.path.exists('/.dockerenv'):
        return True
    
    # Method 2: Check container cgroup
    try:
        with open('/proc/1/cgroup', 'r') as f:
            return 'docker' in f.read() or 'kubepods' in f.read()
    except (FileNotFoundError, IOError):
        pass
    
    # Method 3: Check hostname for container ID format
    try:
        with open('/etc/hostname', 'r') as f:
            hostname = f.read().strip()
            if len(hostname) == 12 and all(c in '0123456789abcdef' for c in hostname):
                return True
    except (FileNotFoundError, IOError):
        pass
    
    return False


def run_coverage_in_container(module=None, category=None):
    """
    Run the coverage tests directly (when inside the container).
    
    Args:
        module: Optional module to test coverage for
        category: Optional test category
    
    Returns:
        int: Return code from the process
    """
    cmd = [sys.executable, "scripts/testing/run_coverage.py"]
    
    if module:
        cmd.extend(["--module", module])
    
    if category:
        cmd.extend(["--category", category])
    
    print(f"Running coverage tests directly: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True, cwd="/workspace")
        return 0
    except subprocess.CalledProcessError as e:
        return e.returncode


def run_coverage_from_host(module=None, category=None):
    """
    Run the coverage tests via docker exec (when on the host).
    
    Args:
        module: Optional module to test coverage for
        category: Optional test category
    
    Returns:
        int: Return code from the process
    """
    container_name = "geoapi_api_dev"
    cmd = ["docker", "exec", container_name, "python", "scripts/testing/run_coverage.py"]
    
    if module:
        cmd.extend(["--module", module])
    
    if category:
        cmd.extend(["--category", category])
    
    print(f"Running coverage tests via docker exec: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        return 0
    except subprocess.CalledProcessError as e:
        return e.returncode


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Run test coverage from host or container"
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
    print("SMART TEST COVERAGE RUNNER")
    print("=" * 80)
    
    # Detect if we're in a container or on the host
    in_container = is_running_in_container()
    
    if in_container:
        print("Detected: Running inside container")
        return run_coverage_in_container(args.module, args.category)
    else:
        print("Detected: Running on host")
        return run_coverage_from_host(args.module, args.category)


if __name__ == "__main__":
    sys.exit(main())
