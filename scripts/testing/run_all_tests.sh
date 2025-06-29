#!/bin/bash
# Run all tests with coverage

# Run the tests with coverage
pytest tests/test_database.py tests/test_database_additional.py tests/test_database_postgis.py \
      tests/test_logging.py tests/test_logging_additional.py tests/test_logging_extended.py \
      tests/test_models/test_link.py tests/test_models/test_link_extended.py \
      tests/test_models/test_speed_record.py tests/test_models/test_speed_record_extended.py \
      --cov=app --cov-report=html --cov-report=xml

# Open the coverage report
echo "Coverage report generated in htmlcov/index.html"
