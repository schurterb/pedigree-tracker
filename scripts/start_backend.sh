#!/bin/bash

# Start the Pedigree Tracker backend API server
# This script activates the virtual environment and starts the Flask API

# Set script to exit on error
set -e

# Get the directory of this script
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Starting Pedigree Tracker backend API server..."

# Go to the project root
cd "$PROJECT_ROOT"

# Activate the virtual environment
source "./venv/bin/activate"

# Run the application
python -m src.app
