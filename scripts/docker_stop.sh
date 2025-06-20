#!/bin/bash
#
# Docker Stop Script for Pedigree Tracker
# Gracefully stops the Pedigree Tracker Docker containers
#

# Exit on error
set -e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Navigate to project root (parent of scripts directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "=== Stopping Pedigree Tracker Docker containers ==="

# Check for Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed."
    exit 1
fi

# First try the Docker Compose plugin (newer Docker versions)
if docker compose version &> /dev/null; then
    echo "Using Docker Compose plugin..."
    DOCKER_COMPOSE="docker compose"
# Then check for the standalone docker-compose command
elif command -v docker-compose &> /dev/null; then
    echo "Using standalone docker-compose..."
    DOCKER_COMPOSE="docker-compose"
else
    echo "Error: Docker Compose is not installed. Please install Docker Compose:"
    echo "  - For Docker Desktop: It should be included by default"
    echo "  - For Linux: https://docs.docker.com/compose/install/linux/"
    exit 1
fi

# Check if we should remove volumes
REMOVE_VOLUMES=""
if [ "$1" = "--volumes" ] || [ "$1" = "-v" ]; then
    REMOVE_VOLUMES="--volumes"
    echo "Warning: Volumes will be removed. All data will be lost!"
    echo "Press Ctrl+C now to abort, or wait 5 seconds to continue..."
    sleep 5
fi

echo "=== Stopping containers ==="
$DOCKER_COMPOSE down $REMOVE_VOLUMES

echo "=== Container status ==="
docker ps | grep pedigree-tracker || echo "No Pedigree Tracker containers running"

echo -e "\n=== Pedigree Tracker stopped successfully ==="
echo "To start again: ./scripts/docker_start.sh"
echo "To completely reset Docker: ./scripts/docker_reset.sh"
