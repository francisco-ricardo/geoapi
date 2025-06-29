#!/bin/bash
# Reset the Python environment to avoid SQLAlchemy errors
cd /workspace

# Remove any cached Python files
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# Run the tests with clean environment
PYTHONPATH=/workspace python -m pytest tests/test_database.py tests/test_logging.py tests/test_models/test_link.py tests/test_models/test_speed_record.py tests/test_database_postgis.py tests/test_logging_extended.py tests/test_models/test_link_extended.py tests/test_models/test_speed_record_extended.py tests/test_models/test_speed_record_additional.py -v --cov=app --cov-report=html
