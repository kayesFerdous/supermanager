#!/bin/bash

# Get the directory where the script itself is located
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# Construct the full path to the pinned.txt file
PINNED_FILE="$SCRIPT_DIR/pinned.txt"

# Check if the file exists before trying to read it
if [ ! -f "$PINNED_FILE" ]; then
  exit 1
fi

while IFS= read -r line; do
  echo "$line"
done < "$PINNED_FILE"
