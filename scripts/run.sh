#!/bin/bash
set -e

# --- Configuration ---
IMAGE_NAME="nmap-python"
CONTAINER_NAME="nmap-scanner"

# --- Argument Parsing ---
# 1. Use command line arguments if provided (e.g., ./run.sh auto --preset fast)
if [ ! -z "$1" ]; then
    FINAL_ARGS="$@"

# 2. If no arguments, start INTERACTIVE WIZARD
else
    # --- Step 1: Select Mode ---
    echo "------------------------------------------------"
    echo "STEP 1: Select Scanning Mode"
    echo "  1) auto        (Full subnet scan using .env)"
    echo "  2) ping        (Ping sweep only - finds live hosts)"
    echo "  3) router-arp  (Scan only devices found in Router ARP)"
    echo "  4) custom      (Manual input)"
    echo "------------------------------------------------"
    read -p "Enter mode [default: auto]: " MODE_INPUT

    # Default to 'auto' if user hits Enter
    if [ -z "$MODE_INPUT" ]; then
        MODE="auto"
    else
        MODE="$MODE_INPUT"
    fi

    # --- Step 2: Select Preset (If not using custom mode) ---
    if [ "$MODE" == "custom" ]; then
        # If custom, just ask for the raw arguments
        read -p "Enter your custom Nmap/Python arguments: " CUSTOM_ARGS
        FINAL_ARGS="custom $CUSTOM_ARGS"
    else
        echo ""
        echo "------------------------------------------------"
        echo "STEP 2: Select Scan Intensity (Preset)"
        echo "  1) normal      (Default: -sV)"
        echo "  2) fast        (-T4 -F)"
        echo "  3) deep        (-A -p-)"
        echo "  4) vuln        (--script vuln)"
        echo "------------------------------------------------"
        read -p "Enter preset [default: normal]: " PRESET_INPUT

        # Default to 'normal'
        if [ -z "$PRESET_INPUT" ]; then
            PRESET="normal"
        else
            PRESET="$PRESET_INPUT"
        fi
        
        # Combine Mode and Preset for the final command
        # Result looks like: auto --preset fast
        FINAL_ARGS="$MODE --preset $PRESET"
    fi
fi

# --- Execution ---
cd ..

# Check if image exists
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
  echo "Image '$IMAGE_NAME' not found locally."
  if [ -f "Makefile" ]; then
    echo "Makefile found. Building image..."
    make build
  elif [ -f "$IMAGE_NAME.tar" ]; then
    echo "Loading image from tar file..."
    docker load -i "$IMAGE_NAME.tar"
  else
    echo "CRITICAL ERROR: Image missing. No Makefile or .tar file found."
    exit 1
  fi
else
  echo "Image '$IMAGE_NAME' found locally. Skipping build."
fi

echo "------------------------------------------------"
echo "Starting container: $CONTAINER_NAME"
echo "Command: $IMAGE_NAME $FINAL_ARGS"
echo "------------------------------------------------"

# Pass FINAL_ARGS to the container
docker run --rm -it --net=host --env-file .env "$IMAGE_NAME" $FINAL_ARGS

echo "Execution finished."