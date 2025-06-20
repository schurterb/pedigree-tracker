#!/bin/bash
#
# Docker Reset Script for Pedigree Tracker
# Safely cleans up Docker resources
#

# Exit on error
set -e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Navigate to project root (parent of scripts directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "=== Docker Reset Script for Pedigree Tracker ==="

# Check for Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Warning: docker-compose not found, trying Docker Compose plugin..."
    if ! command -v "docker compose" &> /dev/null; then
        echo "Error: Neither docker-compose nor Docker Compose plugin found."
        exit 1
    fi
    # Use Docker Compose plugin syntax
    DOCKER_COMPOSE="docker compose"
else
    # Use traditional docker-compose syntax
    DOCKER_COMPOSE="docker-compose"
fi

# Process command line arguments
PROJECT_ONLY=true # Default to project only mode

while [[ $# -gt 0 ]]; do
  case $1 in
    --all)
      REMOVE_ALL=true
      REMOVE_PROJECT=true
      echo "WARNING: Will remove ALL Docker containers, images, and volumes on the system!"
      ;;
    --prune)
      REMOVE_PROJECT=true
      echo "Will remove Pedigree Tracker containers, images, and volumes"
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--prune] [--all]"
      echo "  --prune  : Remove all project containers, images, and volumes"
      echo "  --all    : Remove ALL Docker resources (use with caution!)"
      exit 1
      ;;
  esac
  shift
done

# If no arguments, default to safe mode (just stop containers)
if [[ -z "$REMOVE_PROJECT" && -z "$REMOVE_ALL" ]]; then
  echo "Running in safe mode: Will stop and remove Pedigree Tracker containers only"
  echo "Use --prune to remove project images and volumes"
  echo "Use --all to remove ALL Docker resources on the system"
 fi

echo "\nPress Ctrl+C now to abort, or wait 5 seconds to continue..."
sleep 5

echo -e "\n=== Stopping Pedigree Tracker containers ==="
$DOCKER_COMPOSE down

# If prune flag is set, remove project volumes
if [[ "$REMOVE_PROJECT" == true ]]; then
  echo -e "\n=== Removing Pedigree Tracker volumes ==="
  $DOCKER_COMPOSE down --volumes --remove-orphans
  echo -e "\n=== Removing Pedigree Tracker images ==="
  $DOCKER_COMPOSE down --rmi all
  docker image prune -f --filter label=com.docker.compose.project=pedigree-tracker
fi

# If all flag is set, remove everything
if [[ "$REMOVE_ALL" == true ]]; then
  echo -e "\n=== WARNING: Removing ALL Docker containers, images, and volumes ==="
  echo "Stopping all containers..."
  docker stop $(docker ps -aq) || echo "No running containers to stop"
  
  echo "Removing all containers..."
  docker rm $(docker ps -aq) || echo "No containers to remove"
  
  echo "Removing all images..."
  docker rmi -f $(docker images -aq) || echo "No images to remove"
  
  echo "Removing all volumes..."
  docker volume prune -f
  
  # Check for any remaining volumes and remove them individually
  if [ "$(docker volume ls -q | wc -l)" -gt 0 ]; then
    echo -e "\n=== Removing remaining volumes individually ==="
    for vol in $(docker volume ls -q); do
      echo "Removing volume: $vol"
      docker volume rm "$vol"
    done
  fi
fi

echo -e "\n=== Verification ==="
echo "Containers:"
docker ps -a | grep pedigree-tracker || echo "No Pedigree Tracker containers found"

echo -e "\nDone! Docker environment has been reset."
echo "To start Pedigree Tracker again, run: ./scripts/docker_start.sh"
