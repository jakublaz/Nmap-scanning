#!/bin/bash
set -e

# --- Configuration ---
IMAGE_NAME="nmap-python"
CONTAINER_NAME="nmap-scanner"
MODE="auto"

# --- Execution ---

# Check if image exists
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
  echo "Image '$IMAGE_NAME' not found locally."

  # OPTION 1: Build from source (Best for your current setup)
  if [ -f "Makefile" ]; then
    echo "Makefile found. Building image..."
    make build

  # OPTION 2: Load from Tar (Backup for offline/production)
  elif [ -f "$IMAGE_NAME.tar" ]; then
    echo "Loading image from tar file..."
    docker load -i "$IMAGE_NAME.tar"

  # ERROR: Nothing works
  else
    echo "CRITICAL ERROR: Image missing. No Makefile to build it, and no .tar file to load it."
    exit 1
  fi
else
  # NEW: This tells you that it found the image
  echo "Image '$IMAGE_NAME' found locally. Skipping build."
fi

echo "Starting container: $CONTAINER_NAME in mode: $MODE..."

docker run --rm -it --net=host --env-file .env "$IMAGE_NAME" "$MODE"

echo "Execution finished."