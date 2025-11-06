# Makefile for Shibasito Distributed System

# Variables
DOCKER_COMPOSE = docker compose -f docker-compose.main.yml
MAVEN_OFFLINE_IMAGE = shibasito/maven-offline:3.9.6

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
	@echo "Running servicio-banco-lp1 tests using a local Maven image (reuse cache)..."
	@echo "Ensuring Maven offline image exists ($(MAVEN_OFFLINE_IMAGE))..."
	@if [ -z "$$(docker images -q $(MAVEN_OFFLINE_IMAGE))" ]; then \
	  echo "Maven offline image not found locally — building it (one-time)."; \
	  docker build -t $(MAVEN_OFFLINE_IMAGE) -f docker/maven-offline.Dockerfile .; \
	else \
	  echo "Found local Maven offline image: $(MAVEN_OFFLINE_IMAGE)"; \
	fi
	# Run tests mounting the local maven repo so downloads are persisted between runs
	docker run --rm -v $(PWD)/servicio-banco-lp1:/app \
	  -v "$$HOME/.m2":/root/.m2 \
	  -w /app $(MAVEN_OFFLINE_IMAGE) mvn -DtrimStackTrace=false test
	@echo "Running servicio-reniec-lp2 pytest via docker-compose (override entrypoint)..."
	# Override the image entrypoint so we run pytest directly (avoid start.sh running consumer/uvicorn)
	$(DOCKER_COMPOSE) run --rm --entrypoint pytest servicio-reniec-lp2 -q

push:
	@echo "Pushing images to Docker Hub..."
	$(DOCKER_COMPOSE) push
