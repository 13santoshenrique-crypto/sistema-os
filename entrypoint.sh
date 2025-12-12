#!/usr/bin/env bash
set -e

echo "Waiting for DB..."
# Simple wait loop (best-effort) in case database not ready
sleep 1

echo "Running migrations..."
python manage.py migrate --noinput
echo "Collect static files..."
python manage.py collectstatic --noinput

echo "Starting gunicorn..."
exec "$@"
