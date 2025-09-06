#!/bin/bash


# This Script should only be used as a backup if your machine dosen't support Docker
# The recommended way of deployment is running "docker compose up --build" on the project's root.
# For more info check the "Getting Started" Section in the README.md



# Exit immediately if a command exits with a non-zero status.
set -e

# --- Section 1: Load Environment Variables ---
# This ensures that all secrets and configuration from your .env file
# are available to this script and the application.
echo " sourcing .env file..."
set -a
source .env
set +a
echo "env sourced."


# --- Section 2: System & Python Installation ---
# We only perform this setup if Python 3.11 is not already installed.

if ! command -v python3.11 &> /dev/null
then
    echo "Python 3.11 not found. Starting installation..."

    # Install prerequisites for adding new repositories and for the database driver.
    apt-get update
    apt-get install -y software-properties-common postgresql-client

    # Add the trusted 'deadsnakes' PPA for modern Python versions.
    add-apt-repository ppa:deadsnakes/ppa

    # Update package lists again to include the new PPA.
    apt-get update

    # Install Python 3.11 and its virtual environment tool.
    apt-get install -y python3.11 python3.11-venv

    echo "Python 3.11 installation complete."
else
    echo "Python 3.11 is already installed. Skipping installation."
fi


# --- Section 3: Project Virtual Environment Setup ---
# We only create the virtual environment if it doesn't already exist.

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3.11 -m venv .venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment for the rest of the script.
source .venv/bin/activate
echo "Virtual environment activated."


# --- Section 4: Install Python Dependencies ---
# This ensures all required packages from requirements.txt are installed.
# Running this every time is fast and catches any new additions.
echo "Installing/updating Python dependencies..."
pip3 install -r backend/requirements.txt
echo "Dependencies are up to date."


# --- Section 5: Database Connectivity & Migrations ---
# Wait for the external Neon database to be ready before proceeding.
echo "Waiting for the external PostgreSQL database at $DB_HOST:$DB_PORT..."
# The -z flag tells nc to scan for a listening daemon without sending data.
# The -w 5 flag sets a timeout of 5 seconds for the connection attempt.
while ! nc -z -w 5 "$DB_HOST" "$DB_PORT"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL connection successful."


# Navigate into the backend directory to run Django commands.
cd backend

# Run the django-tenants migrations for the public schema.
echo "Running database migrations..."
python3 manage.py migrate_schemas --shared

# Collect static files for production serving (good practice).
# echo "Collecting static files..."
# python3 manage.py collectstatic --noinput --clear


# --- Section 6: Launch the Application ---
# This is the final step. It starts the Gunicorn server.
# This command runs in the foreground and will keep the script alive.
echo "Starting Gunicorn server..."
python3 -m gunicorn core.wsgi:application --bind 0.0.0.0:8000 --timeout 120