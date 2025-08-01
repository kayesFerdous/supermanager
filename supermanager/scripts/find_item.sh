#!/bin/bash

# Check if both arguments are provided
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <directory> <search_fragment>"
    exit 1
fi

# Search for files and directories matching the fragment, sort in ascending order
find "$1" -maxdepth 1 -iname "*$2*" -print0 | sort -z | while IFS= read -r -d $'\0' item; do
    if [ -d "$item" ]; then
        echo "dir|$item"
    else
        echo "file|$item"
    fi
done