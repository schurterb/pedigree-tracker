#!/bin/bash

# Run the Pedigree Tracker application (both backend and frontend)
# This script starts the Flask backend API and the frontend HTTP server

# Set script to exit on error
set -e

# Get the directory of this script
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Starting Pedigree Tracker application..."

# Start the Flask backend API server in the background
echo "Starting backend API server on port 5000..."
cd "$PROJECT_ROOT"

# Activate the virtual environment
source "$PROJECT_ROOT/venv/bin/activate"

# Start the backend server
export PYTHONPATH="$PROJECT_ROOT"
python3 -m src.app &
BACKEND_PID=$!

# Give the backend server a moment to start up
sleep 2

# Start the frontend server in the background
echo "Starting frontend server on port 8000..."
cd "$PROJECT_ROOT/www"
python3 -m http.server &
FRONTEND_PID=$!

echo "Pedigree Tracker is running!"
echo "Backend API: http://localhost:5000/api/v1"
echo "Frontend UI: http://localhost:8000"
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "Servers stopped."
    exit 0
}

# Register the cleanup function for when the script exits
trap cleanup INT TERM EXIT

# Wait for both processes
wait
