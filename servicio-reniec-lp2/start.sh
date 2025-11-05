#!/bin/bash
set -e

# Run seed script
python seed.py

# Start the consumer in the background
python consumer.py &

# Start the FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000
