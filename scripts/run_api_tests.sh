#!/bin/bash
# Run API tests with coverage reporting

# Set up environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)
export TESTING=1

# Run tests with coverage
coverage run -m pytest src/tests/api/ -v

# Generate coverage report
coverage report -m

# Optional: Generate HTML coverage report
# coverage html
# echo "HTML coverage report generated at htmlcov/index.html"
