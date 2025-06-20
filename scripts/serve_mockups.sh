#!/bin/bash
# Starts a simple HTTP server to view the Pedigree Tracker mockups
# Run this script from the root of the pedigree-tracker workspace

PORT=8080
SERVER_ROOT="/home/schurterb/workspace/pedigree-tracker/docs/mockups"

# Check if a port was specified
if [ "$1" != "" ]; then
  PORT=$1
fi

echo "Starting server on port $PORT..."
echo "View mockups at: http://localhost:$PORT/docs/mockups/"
echo "View development version at: http://localhost:$PORT/www/"
echo "Press Ctrl+C to stop the server"
echo ""

# Start Python HTTP server
cd "$SERVER_ROOT" && python3 -m http.server $PORT
