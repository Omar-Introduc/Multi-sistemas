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
	# Enable BuildKit for faster, cacheable Docker builds (used by Dockerfile to cache Maven repo)
	DOCKER_BUILDKIT=1 $(DOCKER_COMPOSE) build

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

# Run all tests across the repository (includes the default `test` behavior
# plus any additional test suites such as an extra banco folder and the
# end-to-end script). This is intentionally separate so callers can still
# use `make test` for the fast path.
.PHONY: test-all
test-all: test
	@echo "Checking for extra test suites..."
	# If there's a pom.xml in servicio--banco-lp1, run its Maven tests using the same offline image
	@if [ -f "$(PWD)/servicio--banco-lp1/pom.xml" ]; then \
	  echo "Running extra Maven tests for servicio--banco-lp1 (double-dash)"; \
	  docker run --rm -v $(PWD)/servicio--banco-lp1:/app -v "$$HOME/.m2":/root/.m2 -w /app $(MAVEN_OFFLINE_IMAGE) mvn -DtrimStackTrace=false test; \
	else \
	  echo "No pom.xml at servicio--banco-lp1, skipping extra Maven tests."; \
	fi

	# Run the end-to-end python test only if explicitly requested.
	# NOTE: test_e2e.py runs docker compose and may require sudo or starting/stopping containers.
	@echo "End-to-end tests are optional. Set RUN_E2E=1 to enable (may require sudo).";
	@if [ "$$RUN_E2E" = "1" ]; then \
	  echo "Running end-to-end pytest (test_e2e.py)"; \
	  pytest -q test_e2e.py || echo "test_e2e.py failed. Inspect it manually."; \
	else \
	  echo "Skipping end-to-end tests. To run them: RUN_E2E=1 make test-all"; \
	fi

push:
	@echo "Pushing images to Docker Hub..."
	$(DOCKER_COMPOSE) push

# Run the docker-run Maven profile which activates the io.fabric8 docker plugin.
# This will attempt to start/stop containers and therefore requires access to
# the Docker daemon. Run this on a host with Docker available. We mount the
# host Docker socket into the Maven container so the plugin can control Docker.
.PHONY: integration
integration:
	@echo "Running integration profile (docker-run). Requires Docker socket mounted."
	docker run --rm -v $(PWD)/servicio-banco-lp1:/app -v "$$HOME/.m2":/root/.m2 \
	  -v /var/run/docker.sock:/var/run/docker.sock -w /app $(MAVEN_OFFLINE_IMAGE) mvn -Pdocker-run verify
