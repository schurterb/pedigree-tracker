#!/bin/bash
#
# Docker Start Script for Pedigree Tracker
# Builds (if needed) and starts the application in a Docker container
#

# Exit on error
set -e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Navigate to project root (parent of scripts directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "=== Starting Pedigree Tracker in Docker ==="
echo "Project root: $PROJECT_ROOT"

# Check if docker and docker-compose are installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
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

echo "=== Pulling latest base images ==="
$DOCKER_COMPOSE pull || echo "Warning: Unable to pull images, will use local images"

echo "=== Building Pedigree Tracker container ==="
$DOCKER_COMPOSE build

echo "=== Starting Pedigree Tracker ==="
$DOCKER_COMPOSE up -d

echo "=== Container Status ==="
$DOCKER_COMPOSE ps

echo -e "\n=== Application started successfully! ==="
echo "Access the Pedigree Tracker at http://localhost:8000"
echo "To view logs: docker-compose logs -f"
echo "To stop: ./scripts/docker_stop.sh"
