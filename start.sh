#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "$SCRIPT_DIR/config.ini" ]; then
    echo "Missing config.ini in $SCRIPT_DIR (required for sync_compose_from_config.sh)" >&2
    exit 1
fi

cd "$SCRIPT_DIR/docker" || exit 1
./sync_compose_from_config.sh
exec docker compose up --build "$@"
