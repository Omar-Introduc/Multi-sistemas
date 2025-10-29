# Makefile para el Proyecto Shibasito

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
	docker compose build

# Levanta todos los servicios (BDs, RabbitMQ, Banco, Reniec) en segundo plano (-d)
# y reconstruye las imágenes si es necesario (--build)
up:
	@echo "Lanzando todos los servicios (BD1, BD2, RabbitMQ, Banco, Reniec)..."
	docker compose up -d --build

# 2. "Validar plan"
# Revisa la sintaxis de tu docker-compose.yml
validate:
	@echo "Validando la configuración de docker-compose..."
	docker compose config

# 3. "Test"
# Ejecuta los tests DENTRO de un contenedor temporal del servicio
test: test-banco test-reniec

test-banco:
	@echo "Ejecutando tests para el servicio Banco (LP1)..."
	# Asume que LP1 (Java) usa Maven. --rm elimina el contenedor al terminar.
	docker compose run --rm $(BANCO_SERVICE) mvn test

test-reniec:
	@echo "Ejecutando tests para el servicio Reniec (LP2)..."
	# Asume que LP2 (Python) usa pytest.
	docker compose run --rm $(RENIEC_SERVICE) pytest

# 4. "Eliminar todos los servicios para mantener limpio el entorno"
# Opción A: Parar y eliminar contenedores
down:
	@echo "Deteniendo y eliminando contenedores..."
	docker compose down

# Opción B: "Limpieza profunda" (La que realmente quieres)
# Para, elimina contenedores, elimina volúmenes (-v) y elimina TODAS las imágenes del compose
clean:
	@echo "Limpieza profunda: Contenedores, Volúmenes e Imágenes..."
	docker compose down -v --rmi all

# Opción C: "Limpieza nuclear" (Limpia todo lo de Docker en tu sistema)
prune:
	@echo "Limpiando todo Docker no utilizado (contenedores, redes, imágenes)..."
	docker system prune -a --volumes

# Herramientas de utilidad
# -----------------------

# Para ver los logs de todos los servicios en tiempo real
logs:
	@echo "Mostrando logs de todos los servicios..."
	docker compose logs -f

# Para parar los servicios sin eliminarlos
stop:
	@echo "Deteniendo servicios..."
	docker compose stop
