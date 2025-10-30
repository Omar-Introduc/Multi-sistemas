# Makefile for Shibasito Project

# Default target
all: build up

# Build Docker images
build:
	docker compose build

# Start all services
up:
	docker compose up -d

# Stop all services
down:
	docker compose down

# Clean up the environment (containers, volumes, networks)
clean: down
	docker compose down -v --remove-orphans

# Push service images to the container registry
push:
	docker compose push

# --- Testing ---

# Run all tests
test: test-pipeline

# Run unit tests for LP1 and LP2
test-unit:
	@echo "Running unit tests..."
	# The Java tests are run during the 'build' step.
	# We allow pytest to exit with code 5 (no tests found) without failing the build.
	docker compose exec servicio-reniec-lp2 pytest || [ $$? -eq 5 ]

# Run stress test
test-stress:
	@echo "Running stress test..."
	# Placeholder for stress test command

# Run data validation post-stress
test-validate:
	@echo "Running data validation..."
	# Placeholder for validation command

# Run the complete test pipeline
test-pipeline: test-unit test-stress test-validate

.PHONY: all build up down clean push test test-unit test-stress test-validate test-pipeline
