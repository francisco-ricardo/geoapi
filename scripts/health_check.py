#!/usr/bin/env python3
"""
Health check script for the GeoSpatial Links API.

Quick verification that all components are working correctly.
"""

import sys
from datetime import datetime

import requests


def main():
    """Run complete health check."""
    print("GeoSpatial Links API - Health Check")
    print("=" * 40)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    checks = [
        ("API Health", check_api_health),
        ("API Documentation", check_api_docs),
        ("Main Endpoints", check_endpoints),
    ]

    all_passed = True

    for check_name, check_func in checks:
        print(f"Checking {check_name}...")
        if not check_func():
            all_passed = False
        print()

    if all_passed:
        print("ALL CHECKS PASSED!")
        print("\nAPI is ready for testing!")
        print("Visit: http://localhost:8000/docs")
        sys.exit(0)
    else:
        print("SOME CHECKS FAILED!")
        print("\nTroubleshooting:")
        print("1. Make sure containers are running: make logs")
        print("2. Restart services: make restart")
        print("3. Check setup: python scripts/setup/complete_setup.py")
        sys.exit(1)


def check_api_health():
    """Check if API is responding."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("API Health: OK")
            print(f"  Database: {data.get('database', 'Unknown')}")
            print(f"  Timestamp: {data.get('timestamp', 'Unknown')}")
            return True
    except requests.RequestException as e:
        print(f"API Health: FAILED - {e}")
    return False


def check_api_docs():
    """Check if API documentation is accessible."""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("API Documentation: OK")
            return True
    except requests.RequestException as e:
        print(f"API Documentation: FAILED - {e}")
    return False


def check_endpoints():
    """Check main API endpoints."""
    endpoints = [
        ("GET /", "http://localhost:8000/"),
        ("GET /links/", "http://localhost:8000/links/"),
        ("GET /aggregates/summary/", "http://localhost:8000/aggregates/summary/"),
    ]

    all_ok = True

    for name, url in endpoints:
        try:
            # Use longer timeout for data endpoints
            timeout = 10 if "aggregates" in url else 5
            response = requests.get(url, timeout=timeout)
            if 200 <= response.status_code < 300:
                print(f"{name}: OK ({response.status_code})")
            else:
                print(f"{name}: FAILED ({response.status_code})")
                all_ok = False
        except requests.RequestException as e:
            print(f"{name}: FAILED - {e}")
            all_ok = False

    return all_ok


if __name__ == "__main__":
    main()
