# Makefile para el Proyecto Shibasito

# Variable para la ubicación del docker-compose.yml
COMPOSE_FILE = -f proyecto-banco-shibasito/docker-compose.yml

# Variables para los nombres de los servicios (útil si cambian)
BANCO_SERVICE=servicio-banco-lp1
RENIEC_SERVICE=servicio-reniec-lp2

# .PHONY evita conflictos con nombres de archivos
.PHONY: all build up down stop clean prune logs test test-banco test-reniec validate

# Comando por defecto (si solo escribes 'make')
all: build up

# 1. "Lanzamiento de docker e imágenes y correr todo"
# Construye las imágenes Docker de tus servicios (Java y Python)
build:
	@echo "Construyendo imágenes de servicios..."
	sudo docker compose $(COMPOSE_FILE) build

# Levanta todos los servicios (BDs, RabbitMQ, Banco, Reniec) en segundo plano (-d)
# y reconstruye las imágenes si es necesario (--build)
up:
	@echo "Lanzando todos los servicios (BD1, BD2, RabbitMQ, Banco, Reniec)..."
	sudo docker compose $(COMPOSE_FILE) up -d --build

# 2. "Validar plan"
# Revisa la sintaxis de tu docker-compose.yml
validate:
	@echo "Validando la configuración de docker-compose..."
	sudo docker compose $(COMPOSE_FILE) config

# 3. "Test"
# Ejecuta los tests DENTRO de un contenedor temporal del servicio
test: test-banco test-reniec

test-banco:
	@echo "Ejecutando tests para el servicio Banco (LP1)..."
	# Asume que LP1 (Java) usa Maven. --rm elimina el contenedor al terminar.
	sudo docker compose $(COMPOSE_FILE) run --rm $(BANCO_SERVICE) mvn test

test-reniec:
	@echo "Ejecutando tests para el servicio Reniec (LP2)..."
	# Asume que LP2 (Python) usa pytest.
	sudo docker compose $(COMPOSE_FILE) run --rm $(RENIEC_SERVICE) pytest

# 4. "Eliminar todos los servicios para mantener limpio el entorno"
# Opción A: Parar y eliminar contenedores
down:
	@echo "Deteniendo y eliminando contenedores..."
	sudo docker compose $(COMPOSE_FILE) down

# Opción B: "Limpieza profunda" (La que realmente quieres)
# Para, elimina contenedores, elimina volúmenes (-v) y elimina TODAS las imágenes del compose
clean:
	@echo "Limpieza profunda: Contenedores, Volúmenes e Imágenes..."
	sudo docker compose $(COMPOSE_FILE) down -v --rmi all

# Opción C: "Limpieza nuclear" (Limpia todo lo de Docker en tu sistema)
prune:
	@echo "Limpiando todo Docker no utilizado (contenedores, redes, imágenes)..."
	sudo docker system prune -a --volumes

# Herramientas de utilidad
# -----------------------

# Para ver los logs de todos los servicios en tiempo real
logs:
	@echo "Mostrando logs de todos los servicios..."
	sudo docker compose $(COMPOSE_FILE) logs -f

# Para parar los servicios sin eliminarlos
stop:
	@echo "Deteniendo servicios..."
	sudo docker compose $(COMPOSE_FILE) stop

# Comandos de Terraform
# ---------------------

terraform-init:
	@echo "Inicializando Terraform..."
	sudo docker compose $(COMPOSE_FILE) run --rm terraform init

terraform-validate:
	@echo "Validando la configuración de Terraform..."
	sudo docker compose $(COMPOSE_FILE) run --rm terraform validate

terraform-plan:
	@echo "Creando el plan de Terraform..."
	sudo docker compose $(COMPOSE_FILE) run --rm terraform plan

terraform-apply:
	@echo "Aplicando la configuración de Terraform..."
	sudo docker compose $(COMPOSE_FILE) run --rm terraform apply
