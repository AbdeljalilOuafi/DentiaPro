#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Environment Detection ---
# This is a two-part check:
# 1. 'command -v docker &> /dev/null' checks if the Docker command exists without crashing.
# 2. '&&' means the second part only runs if the first part was successful.
# 3. 'docker container inspect drf_backend > /dev/null 2>&1' checks for our container.

if command -v docker &> /dev/null && docker container inspect drf_backend > /dev/null 2>&1; then
    # --- Docker Compose Mode ---
    echo "Docker Compose environment detected. Restarting services..."

    # Navigate to the project root where the docker-compose.yml file lives.
    cd ..

    # Stop and remove the old containers, then create and start new ones.
    docker compose down
    docker compose up -d

    echo "Docker Compose services have been restarted successfully."
    echo "You can view logs with: docker compose logs -f"

else
    # --- Manual Gunicorn Mode ---
    # This block will now run if Docker is not installed OR if the container doesn't exist.
    echo "Manual Gunicorn deployment detected. Restarting process..."

    # Stop any running Gunicorn server.
    pkill -f gunicorn || true
    echo "Processes stopped."

    # Activate the virtual environment.
    echo "Activating virtual environment..."
    source ../.venv/bin/activate
    echo "Virtual environment activated."

    # Start the Gunicorn server in the foreground.
    echo "Starting Gunicorn server..."
    python3 -m gunicorn core.wsgi:application --bind 0.0.0.0:8000 --timeout 120
fi