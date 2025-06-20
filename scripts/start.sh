#!/bin/bash

# Unified script to start the Pedigree Tracker application
# Usage: ./scripts/start.sh

# Default port for the unified server
APP_PORT=8000

# Get the directory of this script
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
APP_PID=""

# # Set environment variable to enable default data creation
# export PEDIGREE_CREATE_DEFAULT_DATA=1

# Function to clean up when script is terminated
cleanup() {
  echo -e "\nShutting down Pedigree Tracker..."
  
  # Kill the application process if it's running
  if [ -n "$APP_PID" ]; then
    echo "Stopping Pedigree Tracker server (PID: $APP_PID)..."
    kill "$APP_PID" 2>/dev/null || true
  fi
  
  echo "Pedigree Tracker stopped successfully."
  exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM signals
trap cleanup SIGINT SIGTERM

# Start the unified server (serving both API and frontend)
echo "Starting Pedigree Tracker server on port $APP_PORT..."
cd "$PROJECT_ROOT"
source "./venv/bin/activate"

# Start the Flask app with the correct port
python -m src.app &
APP_PID=$!

# Wait for the server to start and become available
echo "Waiting for server to become available..."

MAX_RETRIES=10
RETRY_COUNT=0
APP_READY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  # Check if the process is still running
  if ! ps -p $APP_PID > /dev/null; then
    echo "Error: Server process failed to start or terminated unexpectedly. Exiting."
    exit 1
  fi
  
  # Try to connect to the health endpoint
  if curl -s "http://localhost:$APP_PORT/health" > /dev/null; then
    APP_READY=true
    break
  fi
  
  RETRY_COUNT=$((RETRY_COUNT + 1))
  echo "Waiting for server to start... ($RETRY_COUNT/$MAX_RETRIES)"
  sleep 1
done

if [ "$APP_READY" = false ]; then
  echo "Error: Server failed to become available after $MAX_RETRIES attempts. Exiting."
  cleanup
  exit 1
fi

# Wait for user interrupt
echo "Pedigree Tracker is now running!"
echo "Application available at: http://localhost:$APP_PORT"
echo "API endpoints available at: http://localhost:$APP_PORT/api/v1"
echo "Press Ctrl+C to stop the server."
wait

# This should not be reached unless all background processes exit unexpectedly
cleanup
