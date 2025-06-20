#!/bin/bash

# Start a Python HTTP server for the Pedigree Tracker application
echo "Starting Pedigree Tracker server..."
echo "Navigate to http://localhost:8000 to view the application"
cd "$(dirname "$0")/../www" && python3 -m http.server
