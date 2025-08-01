#!/bin/bash

path="$1"

if [ -z "$path" ]; then
    echo "Usage: $0 <path>" >&2
    exit 1
fi

rm -rf "$path"
