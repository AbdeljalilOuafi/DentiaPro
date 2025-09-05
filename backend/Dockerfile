# Use an official Python runtime >= 3.10
FROM python:3.11-slim-bookworm

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
# postgresql-client is needed for the entrypoint script to check DB connection
RUN apt-get update && apt-get install -y postgresql-client

# Copy the requirements file into the container
COPY requirements.txt .

# 3. Use pip3 explicitly to install dependencies
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Copy the entrypoint script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Copy the rest of the application's code from the build context
COPY . .

# The command to run when the container starts
ENTRYPOINT ["/app/entrypoint.sh"]