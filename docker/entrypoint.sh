#!/bin/sh
set -e

cd /app

# Apply database migrations before starting the server.
alembic -c /app/alembic.ini upgrade head

GRANIAN_HOST="${GRANIAN_HOST:-0.0.0.0}"
GRANIAN_PORT="${GRANIAN_PORT:-8000}"
GRANIAN_WORKERS="${GRANIAN_WORKERS:-2}"
GRANIAN_LOOP="${GRANIAN_LOOP:-uvloop}"
GRANIAN_HTTP="${GRANIAN_HTTP:-auto}"

exec granian \
    --interface rsgi \
    --host "${GRANIAN_HOST}" \
    --port "${GRANIAN_PORT}" \
    --workers "${GRANIAN_WORKERS}" \
    --loop "${GRANIAN_LOOP}" \
    --http "${GRANIAN_HTTP}" \
    src.main:app
