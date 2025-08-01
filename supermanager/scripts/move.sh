#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

DESTINATION_DIR="$1"
shift
SOURCE_ITEMS=("$@")  # All remaining arguments are source files/folders

# Exit if destination is empty
if [ -z "$DESTINATION_DIR" ]; then
    exit 1
fi

# Create destination directory if it doesn't exist
mkdir -p "$DESTINATION_DIR" || exit 1

# Exit if no source items provided
if [ ${#SOURCE_ITEMS[@]} -eq 0 ]; then
    > "$SCRIPT_DIR/selected_items.txt"
    exit 0
fi

# Move each item
for item in "${SOURCE_ITEMS[@]}"; do
    # Skip if source doesn't exist
    [ ! -e "$item" ] && continue

    item_basename=$(basename "$item")
    potential_destination_path="${DESTINATION_DIR}/${item_basename}"

    if [ -e "$potential_destination_path" ]; then
        # Separate filename and extension
        filename="${item_basename%.*}"
        extension="${item_basename##*.}"
        if [ "$filename" = "$extension" ]; then
            # No extension case
            renamed_destination_path="${DESTINATION_DIR}/${filename}(1)"
        else
            renamed_destination_path="${DESTINATION_DIR}/${filename}(1).${extension}"
        fi

        mv "$item" "$renamed_destination_path"
    else
        mv "$item" "$DESTINATION_DIR/"
    fi
done

# Empty the selected_items.txt file
> "$SCRIPT_DIR/selected_items.txt"

exit 0