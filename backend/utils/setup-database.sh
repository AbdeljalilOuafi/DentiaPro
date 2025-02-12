#!/usr/bin/env bash
sudo apt update && sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql  # Start service
sudo systemctl enable postgresql  # Enable on startup

# Run the following command on your shell
# sudo -u postgres psql

# Create a database and a User
# CREATE DATABASE dentiapro;
# CREATE USER ouafidev WITH PASSWORD 'dentiapro_dev';
# ALTER ROLE ouafidev SET client_encoding TO 'utf8';
# ALTER ROLE ouafidev SET default_transaction_isolation TO 'read committed';
# ALTER ROLE ouafidev SET timezone TO 'UTC';
# GRANT ALL PRIVILEGES ON DATABASE dentiapro TO ouafidev;


#Add to .env

# Database settings
# DB_NAME=dentiapro
# DB_USER=ouafidev
# DB_PASSWORD=dentiapro_dev
# DB_HOST=localhost
# DB_PORT=5432