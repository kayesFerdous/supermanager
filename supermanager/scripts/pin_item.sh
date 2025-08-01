#!/bin/bash

# The item data is passed as the first argument, e.g., "/path/to/dir|dirname|timestamp"
ITEM_DATA="$1"
PINNED_FILE="$(dirname "$0")/pinned.txt"

# Extract the full path from the item data. It's the part before the first '|'.
FULL_PATH=$(echo "$ITEM_DATA" | cut -d'|' -f1)

# Ensure the pinned file exists before trying to grep it
touch "$PINNED_FILE"

# Check if the full path already exists in the pinned.txt file, matching the beginning of the line.
# The pattern looks for the exact path followed by a pipe.
if ! grep -q -F -- "$FULL_PATH|" "$PINNED_FILE"; then
    # If it's not found, append the new item data to the file.
    echo "$ITEM_DATA" >> "$PINNED_FILE"
fi