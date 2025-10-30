#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Run the database seeder
echo "Running database seeder..."
python seed.py

# Start the main application
echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 8000
