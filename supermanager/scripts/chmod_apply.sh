#!/bin/bash
# chmod_apply.sh <mode|+x|a+x> <path1> [path2 ...]
# Applies a chmod mode or +x style to given paths.

MODE="$1"
shift

if [ -z "$MODE" ] || [ $# -eq 0 ]; then
  echo "Usage: $0 <mode|+x|a+x> <path1> [path2 ...]" >&2
  exit 1
fi

is_numeric() {
  [[ "$1" =~ ^[0-7]{3,4}$ ]]
}

apply() {
  local target="$1"
  if [ ! -e "$target" ]; then
    echo "Skip (missing): $target" >&2
    return
  fi
  if [ "$MODE" = "+x" ]; then
    chmod u+x "$target" 2>>/dev/null || echo "Failed: $target" >&2
  elif [ "$MODE" = "a+x" ]; then
    chmod a+x "$target" 2>>/dev/null || echo "Failed: $target" >&2
  elif is_numeric "$MODE"; then
    chmod "$MODE" "$target" 2>>/dev/null || echo "Failed: $target" >&2
  else
    echo "Invalid mode: $MODE" >&2
    exit 2
  fi
}

for p in "$@"; do
  apply "$p"
done

exit 0
