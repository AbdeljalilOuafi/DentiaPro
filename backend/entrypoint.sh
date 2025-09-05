#!/bin/sh

# Fail on any error
set -e

# Wait for the PostgreSQL container to be ready
echo "Waiting for PostgreSQL..."
# CORRECTED: Use POSTGRES_... variables to match docker-compose.yml and settings.py
while ! PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL started"

# Use python3 explicitly for all Django management commands
# Run django-tenants migrations for the public schema
echo "Running migrate_schemas for the public schema..."
python3 manage.py migrate_schemas --shared

# # Collect static files
# echo "Collecting static files..."
# python3 manage.py collectstatic --noinput

# Start the Gunicorn server as a Python module
# This uses the gunicorn installed from requirements.txt
echo "Starting Gunicorn..."
python3 -m gunicorn core.wsgi:application --bind 0.0.0.0:8000