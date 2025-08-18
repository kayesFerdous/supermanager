#!/bin/bash

# rename.sh <old_path> <new_name>
# Renames a file or directory. If target exists, append (1), (2), ... automatically.

OLD_PATH="$1"
NEW_NAME="$2"

if [ -z "$OLD_PATH" ] || [ -z "$NEW_NAME" ]; then
    echo "Usage: $0 <old_path> <new_name>" >&2
    exit 1
fi

if [ ! -e "$OLD_PATH" ]; then
    echo "Error: '$OLD_PATH' does not exist" >&2
    exit 1
fi

DIRNAME=$(dirname "$OLD_PATH")
BASENAME="$NEW_NAME"
TARGET_PATH="$DIRNAME/$BASENAME"

# Auto disambiguate
if [ -e "$TARGET_PATH" ]; then
    base_no_ext="${BASENAME%.*}"
    ext="${BASENAME##*.}"
    if [ "$base_no_ext" = "$ext" ]; then
        # no extension
        base_no_ext="$BASENAME"
        ext=""
    else
        ext=".$ext"
    fi
    i=1
    while true; do
        candidate="$DIRNAME/${base_no_ext}(${i})${ext}"
        if [ ! -e "$candidate" ]; then
            TARGET_PATH="$candidate"
            break
        fi
        i=$((i+1))
    done
fi

mv "$OLD_PATH" "$TARGET_PATH"
exit $?
