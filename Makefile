up:
	docker compose -f docker-compose.main.yml up -d

down:
	docker compose -f docker-compose.main.yml down

build:
	docker compose -f docker-compose.main.yml build

test:
	docker compose -f docker-compose.main.yml run --rm servicio-banco-lp1 mvn test
	docker compose -f docker-compose.main.yml run --rm servicio-reniec-lp2 pytest

test-e2e:
	pytest test_e2e.py

.PHONY: up down build test test-e2e
