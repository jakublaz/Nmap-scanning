#!/bin/bash
set -e

# --- Configuration ---
IMAGE_NAME="nmap-python"
CONTAINER_NAME="nmap-scanner"
MODE="auto"

# --- Execution ---

# Check if image exists, otherwise load from tar
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
  if [ -f "$IMAGE_NAME.tar" ]; then
    echo "Loading image from tar file..."
    docker load -i "$IMAGE_NAME.tar"
  else
    echo "Image not found and .tar file is missing."
    exit 1
  fi
fi

echo "Starting container: $CONTAINER_NAME in mode: $MODE..."

docker run --rm -it --env-file .env "$IMAGE_NAME" "$MODE"

echo "Execution finished."