#!/bin/sh

# Run the database seeder
python -m app.seed

# Start the main application
python -m app.main
