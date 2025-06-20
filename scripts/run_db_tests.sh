#!/bin/bash
# Run database tests with coverage reporting

# Set up environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)
export TESTING=1

# Run tests with coverage
coverage run -m pytest src/tests/unit/test_db_*.py src/tests/unit/models/test_*.py -v

# Generate coverage report
coverage report -m

# Generate HTML coverage report (optional)
# coverage html
# echo "HTML coverage report generated at htmlcov/index.html"
