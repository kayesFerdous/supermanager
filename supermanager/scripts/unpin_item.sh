#!/bin/bash

# The full path to unpin is passed as the first argument
FULL_PATH_TO_UNPIN="$1"
PINNED_FILE="$(dirname "$0")/pinned.txt"
TEMP_FILE="${PINNED_FILE}.tmp"

# Exit if the pinned file doesn't exist
if [ ! -f "$PINNED_FILE" ]; then
    exit 0
fi

grep -v -F "${FULL_PATH_TO_UNPIN}|" "$PINNED_FILE" > "$TEMP_FILE"

mv "$TEMP_FILE" "$PINNED_FILE"
