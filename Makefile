# Makefile for Shibasito Distributed System

# Variables
DOCKER_COMPOSE = docker compose -f docker-compose.main.yml

# Commands
.PHONY: up down build logs test push

up:
	@echo "Starting up services..."
	$(DOCKER_COMPOSE) up -d

down:
	@echo "Stopping services..."
	$(DOCKER_COMPOSE) down

build:
	@echo "Building services..."
	$(DOCKER_COMPOSE) build

logs:
	@echo "Tailing logs..."
	$(DOCKER_COMPOSE) logs -f

test:
	@echo "Running tests..."
	$(DOCKER_COMPOSE) run --rm servicio-banco-lp1 mvn test
	$(DOCKER_COMPOSE) run --rm servicio-reniec-lp2 pytest

push:
	@echo "Pushing images to Docker Hub..."
	$(DOCKER_COMPOSE) push
