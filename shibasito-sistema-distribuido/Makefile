# =============================================================================
# MAKEFILE - SISTEMA DISTRIBUIDO SHIBASITO
# Sistema completo de gestión y automatización para desarrollo distribuido
# =============================================================================

.PHONY: help build up down stop restart logs status clean test test-all stress-test validate-data health-check scale shell-banco shell-reniec shell-db

# Variables
COMPOSE_FILE = docker-compose.main.yml
COMPOSE_OVERRIDE = docker-compose.override.yml
ENV_FILE = .env
COMPOSE = docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE)

# Colores para output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
BLUE = \033[0;34m
CYAN = \033[0;36m
NC = \033[0m # No Color

# =============================================================================
# COMANDO PRINCIPAL - AYUDA
# =============================================================================
help: ## Mostrar ayuda completa con todos los comandos disponibles
	@echo "$(CYAN)╔═══════════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║                  🚀 SISTEMA DISTRIBUIDO SHIBASITO 🚀                    ║$(NC)"
	@echo "$(CYAN)║                     Comandos de Gestión y Automatización                ║$(NC)"
	@echo "$(CYAN)╚═══════════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)📋 COMANDOS PRINCIPALES:$(NC)"
	@echo "  $(GREEN)make build$(NC)          Construir/compilar todos los servicios desde cero"
	@echo "  $(GREEN)make up$(NC)             Iniciar todos los servicios del sistema"
	@echo "  $(GREEN)make down$(NC)           Detener y eliminar contenedores"
	@echo "  $(GREEN)make stop$(NC)           Detener contenedores sin eliminar"
	@echo "  $(GREEN)make restart$(NC)        Reiniciar todos los servicios"
	@echo "  $(GREEN)make logs$(NC)           Ver logs en tiempo real de todos los servicios"
	@echo "  $(GREEN)make status$(NC)         Ver estado completo de todos los servicios"
	@echo "  $(GREEN)make clean$(NC)          Limpiar contenedores, redes y volúmenes (⚠️ ELIMINA DATOS)"
	@echo ""
	@echo "$(YELLOW)🧪 COMANDOS DE TESTING:$(NC)"
	@echo "  $(GREEN)make test$(NC)           Ejecutar tests básicos del sistema"
	@echo "  $(GREEN)make test-all$(NC)       Ejecutar todos los tests disponibles"
	@echo "  $(GREEN)make stress-test$(NC)    Ejecutar tests de estrés y rendimiento"
	@echo "  $(GREEN)make validate-data$(NC)  Validar integridad de datos en bases de datos"
	@echo ""
	@echo "$(YELLOW)🏥 COMANDOS DE SALUD:$(NC)"
	@echo "  $(GREEN)make health-check$(NC)   Verificar estado de salud de todos los servicios"
	@echo ""
	@echo "$(YELLOW)🔧 COMANDOS DE DESARROLLO:$(NC)"
	@echo "  $(GREEN)make shell-banco$(NC)    Acceder al shell del servicio Banco (LP1)"
	@echo "  $(GREEN)make shell-reniec$(NC)   Acceder al shell del servicio RENIEC (LP2)"
	@echo "  $(GREEN)make shell-db$(NC)       Acceder al shell de la base de datos"
	@echo "  $(GREEN)make monitor$(NC)        Abrir dashboards de monitoreo"
	@echo ""
	@echo "$(YELLOW)🔄 COMANDOS DE ESCALADO:$(NC)"
	@echo "  $(GREEN)make scale$(NC)          Mostrar opciones de escalado disponibles"
	@echo "  $(GREEN)make scale-banco$(NC)    Escalar servicio Banco a 3 instancias"
	@echo "  $(GREEN)make scale-reniec$(NC)   Escalar servicio RENIEC a 2 instancias"
	@echo "  $(GREEN)make scale-all$(NC)      Escalar todos los servicios escalables"
	@echo ""
	@echo "$(YELLOW)💾 COMANDOS DE BACKUP:$(NC)"
	@echo "  $(GREEN)make backup$(NC)         Crear backup completo de todas las bases de datos"
	@echo "  $(GREEN)make restore$(NC)        Restaurar backup de bases de datos"
	@echo ""
	@echo "$(YELLOW)🔍 COMANDOS DE DEBUG:$(NC)"
	@echo "  $(GREEN)make debug$(NC)          Mostrar información completa de debug"
	@echo "  $(GREEN)make check$(NC)          Verificar configuración del docker-compose"
	@echo ""
	@echo "$(YELLOW)📋 COMANDOS DE LOGS ESPECÍFICOS:$(NC)"
	@echo "  $(GREEN)make logs-banco$(NC)     Ver logs del servicio Banco"
	@echo "  $(GREEN)make logs-reniec$(NC)    Ver logs del servicio RENIEC"
	@echo "  $(GREEN)make logs-db$(NC)        Ver logs de las bases de datos"
	@echo "  $(GREEN)make logs-rabbitmq$(NC)  Ver logs de RabbitMQ"
	@echo "  $(GREEN)make logs-prometheus$(NC) Ver logs de Prometheus"
	@echo "  $(GREEN)make logs-grafana$(NC)   Ver logs de Grafana"
	@echo ""
	@echo "$(YELLOW)🐚 COMANDOS DE SHELL ESPECÍFICOS:$(NC)"
	@echo "  $(GREEN)make shell-banco$(NC)    Shell del servicio Banco"
	@echo "  $(GREEN)make shell-reniec$(NC)   Shell del servicio RENIEC"
	@echo "  $(GREEN)make shell-db$(NC)       Shell de PostgreSQL"
	@echo "  $(GREEN)make shell-mysql$(NC)    Shell de MySQL"
	@echo "  $(GREEN)make shell-redis$(NC)    Shell de Redis"
	@echo "  $(GREEN)make shell-rabbitmq$(NC) Shell de RabbitMQ"
	@echo ""
	@echo "$(YELLOW)🛠️  COMANDOS ADICIONALES:$(NC)"
	@echo "  $(GREEN)make info$(NC)           Mostrar información completa del sistema"
	@echo "  $(GREEN)make system-resources$(NC) Mostrar uso de recursos del sistema"
	@echo "  $(GREEN)make clean-logs$(NC)     Limpiar logs de contenedores"
	@echo "  $(GREEN)make quick-health$(NC)   Health check rápido sin detalles"
	@echo "  $(GREEN)make update$(NC)         Actualizar imágenes Docker"
	@echo ""
	@echo "$(YELLOW)🚀 ACCESOS RÁPIDOS:$(NC)"
	@echo "  • $(CYAN)Grafana Dashboard:$(NC)    http://localhost:3000 (admin/admin123_secure_2024)"
	@echo "  • $(CYAN)RabbitMQ Management:$(NC)  http://localhost:15672 (admin/admin123_secure_2024)"
	@echo "  • $(CYAN)Prometheus Metrics:$(NC)   http://localhost:9090"
	@echo "  • $(CYAN)API Banco (LP1):$(NC)      http://localhost:8080"
	@echo "  • $(CYAN)API RENIEC (LP2):$(NC)     http://localhost:8000"
	@echo ""
	@echo "$(YELLOW)💡 EJEMPLOS DE USO:$(NC)"
	@echo "  $(GREEN)make up && make test$(NC)    - Iniciar sistema y ejecutar tests"
	@echo "  $(GREEN)make logs banco$(NC)         - Ver logs específicos del servicio banco"
	@echo "  $(GREEN)make restart banco$(NC)      - Reiniciar solo el servicio banco"
	@echo "  $(GREEN)make clean CONFIRM$(NC)      - Limpiar todo (requiere confirmar)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-25s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# =============================================================================
# COMANDOS PRINCIPALES - GESTIÓN DEL SISTEMA
# =============================================================================

build: ## Construir/compilar todas las imágenes desde cero
	@echo "$(CYAN)🔨 Construyendo imágenes del sistema...$(NC)"
	@echo "Verificando configuración..."
	@make check
	@echo "$(CYAN)🏗️  Construyendo servicios...$(NC)"
	@$(COMPOSE) build --no-cache --parallel
	@echo "$(GREEN)✅ Construcción completada exitosamente$(NC)"

up: ## Iniciar todos los servicios del sistema distribuido
	@echo "$(CYAN)🚀 Iniciando Sistema Distribuido Shibasito...$(NC)"
	@echo "Verificando configuración..."
	@make check
	@echo "$(CYAN)🐳 Levantando servicios...$(NC)"
	@$(COMPOSE) up -d
	@echo ""
	@echo "$(GREEN)✅ Servicios iniciados correctamente!$(NC)"
	@echo ""
	@echo "$(YELLOW)🔗 URLs de Acceso:$(NC)"
	@echo "  • $(CYAN)Grafana:$(NC)          http://localhost:3000 (admin/admin123_secure_2024)"
	@echo "  • $(CYAN)RabbitMQ:$(NC)         http://localhost:15672 (admin/admin123_secure_2024)"
	@echo "  • $(CYAN)Prometheus:$(NC)       http://localhost:9090"
	@echo "  • $(CYAN)API Banco (LP1):$(NC)  http://localhost:8080"
	@echo "  • $(CYAN)API RENIEC (LP2):$(NC) http://localhost:8000"
	@echo ""
	@echo "$(YELLOW)💡 Usa 'make status' para verificar el estado de los servicios$(NC)"

down: ## Detener y eliminar todos los contenedores y redes
	@echo "$(YELLOW)🛑 Deteniendo y eliminando servicios...$(NC)"
	@$(COMPOSE) down
	@echo "$(GREEN)✅ Servicios detenidos y eliminados$(NC)"

stop: ## Detener contenedores sin eliminar (mantiene estado)
	@echo "$(YELLOW)⏸️  Deteniendo servicios (manteniendo estado)...$(NC)"
	@$(COMPOSE) stop
	@echo "$(GREEN)✅ Servicios detenidos. Usa 'make up' para reanudar$(NC)"

restart: ## Reiniciar todos los servicios del sistema
	@echo "$(YELLOW)🔄 Reiniciando servicios...$(NC)"
	@$(COMPOSE) restart
	@echo "$(GREEN)✅ Servicios reiniciados correctamente$(NC)"

logs: ## Ver logs en tiempo real de todos los servicios
	@echo "$(YELLOW)📋 Mostrando logs en tiempo real (Ctrl+C para salir)...$(NC)"
	@$(COMPOSE) logs -f --tail=100

status: ## Ver estado completo de todos los servicios
	@echo "$(CYAN)📊 Estado completo del Sistema Distribuido:$(NC)"
	@echo "=================================================================="
	@$(COMPOSE) ps
	@echo ""
	@echo "$(YELLOW)🔍 Health Checks:$(NC)"
	@make health-check
	@echo ""
	@echo "$(YELLOW)📈 Estadísticas de Recursos:$(NC)"
	@docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" | head -20

scale: ## Escalar servicios del sistema (escala automáticamente LP1 y LP2)
	@echo "$(CYAN)🔄 Escalando servicios del sistema...$(NC)"
	@echo "=================================================================="
	@echo "$(YELLOW)🔢 Servicios escalables disponibles:$(NC)"
	@echo "  • $(GREEN)servicio-banco-lp1$(NC) - Servicio de Banco (LP1)"
	@echo "  • $(GREEN)servicio-reniec-lp2$(NC) - Servicio de RENIEC (LP2)"
	@echo ""
	@echo "Ejemplo de uso:"
	@echo "  $(GREEN)make scale-banco$(NC) - Escalar servicio banco a 3 instancias"
	@echo "  $(GREEN)make scale-reniec$(NC) - Escalar servicio RENIEC a 2 instancias"
	@echo "  $(GREEN)make scale-all$(NC) - Escalar todos los servicios escalables"
	@echo ""
	@echo "$(YELLOW)⚠️  Nota:$(NC) Los servicios deben estar corriendo para escalar"

scale-banco: ## Escalar servicio Banco a 3 instancias
	@echo "$(CYAN)🐳 Escalando servicio Banco (LP1) a 3 instancias...$(NC)"
	@$(COMPOSE) up -d --scale servicio-banco-lp1=3
	@echo "$(GREEN)✅ Servicio Banco escalado exitosamente$(NC)"
	@$(COMPOSE) ps servicio-banco-lp1

scale-reniec: ## Escalar servicio RENIEC a 2 instancias
	@echo "$(CYAN)🐍 Escalando servicio RENIEC (LP2) a 2 instancias...$(NC)"
	@$(COMPOSE) up -d --scale servicio-reniec-lp2=2
	@echo "$(GREEN)✅ Servicio RENIEC escalado exitosamente$(NC)"
	@$(COMPOSE) ps servicio-reniec-lp2

scale-all: ## Escalar todos los servicios escalables
	@echo "$(CYAN)🚀 Escalando todos los servicios escalables...$(NC)"
	@$(COMPOSE) up -d --scale servicio-banco-lp1=3 --scale servicio-reniec-lp2=2
	@echo "$(GREEN)✅ Todos los servicios escalados exitosamente$(NC)"
	@echo "$(YELLOW)Estado actual:$(NC)"
	@$(COMPOSE) ps | grep -E "(servicio-banco-lp1|servicio-reniec-lp2)"

# =============================================================================
# COMANDOS DE TESTING Y VALIDACIÓN
# =============================================================================

test: ## Ejecutar tests básicos del sistema
	@echo "$(CYAN)🧪 Ejecutando tests básicos del sistema...$(NC)"
	@echo "=================================================================="
	@echo "$(YELLOW)1. Verificando conectividad entre servicios...$(NC)"
	@make health-check
	@echo ""
	@echo "$(YELLOW)2. Probando endpoints de servicios...$(NC)"
	@echo "Probando API Banco..."
	-@curl -f -s http://localhost:8080/health > /dev/null && echo "$(GREEN)✅ API Banco: OK$(NC)" || echo "$(RED)❌ API Banco: FALLA$(NC)"
	@echo "Probando API RENIEC..."
	-@curl -f -s http://localhost:8000/health > /dev/null && echo "$(GREEN)✅ API RENIEC: OK$(NC)" || echo "$(RED)❌ API RENIEC: FALLA$(NC)"
	@echo ""
	@echo "$(YELLOW)3. Verificando bases de datos...$(NC)"
	@echo "PostgreSQL (Banco):"
	-@$(COMPOSE) exec -T bd1_postgresql pg_isready -U banco_user > /dev/null && echo "$(GREEN)✅ PostgreSQL: OK$(NC)" || echo "$(RED)❌ PostgreSQL: FALLA$(NC)"
	@echo "MySQL (RENIEC):"
	-@$(COMPOSE) exec -T bd2_mysql mysqladmin ping -h localhost -u reniec_user -p'$$MYSQL_PASSWORD' > /dev/null && echo "$(GREEN)✅ MySQL: OK$(NC)" || echo "$(RED)❌ MySQL: FALLA$(NC)"
	@echo ""
	@echo "$(YELLOW)4. Verificando RabbitMQ...$(NC)"
	-@$(COMPOSE) exec -T rabbitmq rabbitmq-diagnostics ping > /dev/null && echo "$(GREEN)✅ RabbitMQ: OK$(NC)" || echo "$(RED)❌ RabbitMQ: FALLA$(NC)"
	@echo ""
	@echo "$(GREEN)✅ Tests básicos completados$(NC)"

test-all: ## Ejecutar todos los tests disponibles del sistema
	@echo "$(CYAN)🧪 Ejecutando suite completa de tests...$(NC)"
	@echo "=================================================================="
	@echo "$(YELLOW)🔄 Ejecutando tests básicos...$(NC)"
	@make test
	@echo ""
	@echo "$(YELLOW)🔄 Ejecutando tests de integración...$(NC)"
	@echo "Test 1: Comunicación Banco -> RENIEC"
	-@$(COMPOSE) exec -T servicio-banco-lp1 python3 -c "import requests; r = requests.get('http://servicio-reniec-lp2:8000/health'); print('OK' if r.status_code == 200 else 'FALLA')" 2>/dev/null && echo "$(GREEN)✅ Comunicación BANCO->RENIEC: OK$(NC)" || echo "$(RED)❌ Comunicación BANCO->RENIEC: FALLA$(NC)"
	@echo "Test 2: Comunicación RENIEC -> Banco"
	-@$(COMPOSE) exec -T servicio-reniec-lp2 python3 -c "import requests; r = requests.get('http://servicio-banco-lp1:8080/health'); print('OK' if r.status_code == 200 else 'FALLA')" 2>/dev/null && echo "$(GREEN)✅ Comunicación RENIEC->BANCO: OK$(NC)" || echo "$(RED)❌ Comunicación RENIEC->BANCO: FALLA$(NC)"
	@echo ""
	@echo "$(YELLOW)🔄 Ejecutando tests de mensaje con RabbitMQ...$(NC)"
	@$(COMPOSE) exec -T rabbitmq rabbitmqctl list_queues > /dev/null 2>&1 && echo "$(GREEN)✅ RabbitMQ Queue Management: OK$(NC)" || echo "$(RED)❌ RabbitMQ Queue Management: FALLA$(NC)"
	@echo ""
	@echo "$(YELLOW)🔄 Ejecutando tests de monitoreo...$(NC)"
	-@curl -f -s http://localhost:9090/api/v1/query?query=up > /dev/null && echo "$(GREEN)✅ Prometheus Metrics: OK$(NC)" || echo "$(RED)❌ Prometheus Metrics: FALLA$(NC)"
	-@curl -f -s http://localhost:3000/api/health > /dev/null && echo "$(GREEN)✅ Grafana API: OK$(NC)" || echo "$(RED)❌ Grafana API: FALLA$(NC)"
	@echo ""
	@echo "$(GREEN)✅ Suite completa de tests finalizada$(NC)"

stress-test: ## Ejecutar tests de estrés y rendimiento
	@echo "$(CYAN)⚡ Iniciando tests de estrés y rendimiento...$(NC)"
	@echo "=================================================================="
	@echo "$(YELLOW)🔄 Test de carga en API Banco...$(NC)"
	-@for i in {1..10}; do curl -f -s http://localhost:8080/health > /dev/null && echo "Request $$i: OK" || echo "Request $$i: FALLA"; done
	@echo ""
	@echo "$(YELLOW)🔄 Test de carga en API RENIEC...$(NC)"
	-@for i in {1..10}; do curl -f -s http://localhost:8000/health > /dev/null && echo "Request $$i: OK" || echo "Request $$i: FALLA"; done
	@echo ""
	@echo "$(YELLOW)🔄 Test de memoria y CPU...$(NC)"
	@echo "Estadísticas actuales:"
	@docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
	@echo ""
	@echo "$(YELLOW)🔄 Test de Redis...$(NC)"
	@$(COMPOSE) exec -T redis redis-cli ping > /dev/null 2>&1 && echo "$(GREEN)✅ Redis: OK$(NC)" || echo "$(RED)❌ Redis: FALLA$(NC)"
	@echo ""
	@echo "$(GREEN)✅ Tests de estrés completados$(NC)"

validate-data: ## Validar integridad de datos en bases de datos
	@echo "$(CYAN)🔍 Validando integridad de datos en bases de datos...$(NC)"
	@echo "=================================================================="
	@echo "$(YELLOW)🗄️  Validando PostgreSQL (Banco)...$(NC)"
	@echo "Verificando conexión:"
	@$(COMPOSE) exec -T bd1_postgresql pg_isready -U banco_user
	@echo "Contando registros en tabla cuentas:"
	-@$(COMPOSE) exec -T bd1_postgresql psql -U banco_user -d banco_db -c "SELECT COUNT(*) as total_cuentas FROM cuentas;" 2>/dev/null || echo "No se puede acceder a la tabla cuentas"
	@echo ""
	@echo "$(YELLOW)🗄️  Validando MySQL (RENIEC)...$(NC)"
	@echo "Verificando conexión:"
	@$(COMPOSE) exec -T bd2_mysql mysqladmin ping -h localhost -u reniec_user -p'$$MYSQL_PASSWORD'
	@echo "Verificando tablas:"
	-@$(COMPOSE) exec -T bd2_mysql mysql -u reniec_user -p'$$MYSQL_PASSWORD' -e "USE reniec_db; SHOW TABLES;" 2>/dev/null || echo "No se puede acceder a la base de datos"
	@echo ""
	@echo "$(YELLOW)🗄️  Validando Redis...$(NC)"
	@$(COMPOSE) exec -T redis redis-cli INFO keyspace
	@echo ""
	@echo "$(GREEN)✅ Validación de datos completada$(NC)"

# =============================================================================
# COMANDOS DE SALUD Y MONITOREO
# =============================================================================

health-check: ## Verificar estado de salud de todos los servicios
	@echo "$(CYAN)🏥 Health Check - Estado de Salud de Servicios$(NC)"
	@echo "=================================================================="
	@$(COMPOSE) ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "$(YELLOW)🔍 Verificando servicios críticos:$(NC)"
	@echo "PostgreSQL:"
	@$(COMPOSE) exec -T bd1_postgresql pg_isready -U banco_user && echo "$(GREEN)✅ OK$(NC)" || echo "$(RED)❌ FALLA$(NC)"
	@echo "MySQL:"
	@$(COMPOSE) exec -T bd2_mysql mysqladmin ping -h localhost -u reniec_user -p'$$MYSQL_PASSWORD' && echo "$(GREEN)✅ OK$(NC)" || echo "$(RED)❌ FALLA$(NC)"
	@echo "RabbitMQ:"
	@$(COMPOSE) exec -T rabbitmq rabbitmq-diagnostics ping && echo "$(GREEN)✅ OK$(NC)" || echo "$(RED)❌ FALLA$(NC)"
	@echo "Redis:"
	@$(COMPOSE) exec -T redis redis-cli ping && echo "$(GREEN)✅ OK$(NC)" || echo "$(RED)❌ FALLA$(NC)"
	@echo "Servicio Banco:"
	-@curl -f -s http://localhost:8080/health > /dev/null && echo "$(GREEN)✅ OK$(NC)" || echo "$(RED)❌ FALLA$(NC)"
	@echo "Servicio RENIEC:"
	-@curl -f -s http://localhost:8000/health > /dev/null && echo "$(GREEN)✅ OK$(NC)" || echo "$(RED)❌ FALLA$(NC)"
	@echo ""
	@echo "$(GREEN)✅ Health check completado$(NC)"

# =============================================================================
# COMANDOS DE DESARROLLO Y DEBUG
# =============================================================================

shell-banco: ## Acceder al shell del servicio Banco (LP1)
	@echo "$(CYAN)🐳 Accediendo al shell del servicio Banco...$(NC)"
	@$(COMPOSE) exec servicio-banco-lp1 /bin/bash

shell-reniec: ## Acceder al shell del servicio RENIEC (LP2)
	@echo "$(CYAN)🐍 Accediendo al shell del servicio RENIEC...$(NC)"
	@$(COMPOSE) exec servicio-reniec-lp2 /bin/sh

shell-db: ## Acceder al shell de PostgreSQL (bd1_postgresql)
	@echo "$(CYAN)🗄️  Accediendo al shell de PostgreSQL...$(NC)"
	@$(COMPOSE) exec bd1_postgresql psql -U banco_user -d banco_db

shell-mysql: ## Acceder al shell de MySQL (bd2_mysql)
	@echo "$(CYAN)🗄️  Accediendo al shell de MySQL...$(NC)"
	@$(COMPOSE) exec bd2_mysql mysql -u reniec_user -p'$$MYSQL_PASSWORD' reniec_db

shell-redis: ## Acceder al shell de Redis
	@echo "$(CYAN)💾 Accediendo al shell de Redis...$(NC)"
	@$(COMPOSE) exec redis redis-cli

shell-rabbitmq: ## Acceder al shell de RabbitMQ
	@echo "$(CYAN)🐰 Accediendo al shell de RabbitMQ...$(NC)"
	@$(COMPOSE) exec rabbitmq /bin/bash

monitor: ## Abrir dashboards de monitoreo en navegador
	@echo "$(CYAN)📊 Abriendo dashboards de monitoreo...$(NC)"
	@echo "$(YELLOW)Grafana Dashboard:$(NC) http://localhost:3000"
	@echo "$(YELLOW)Prometheus:$(NC) http://localhost:9090"
	@echo "$(YELLOW)RabbitMQ Management:$(NC) http://localhost:15672"
	@which xdg-open > /dev/null && (xdg-open http://localhost:3000 & xdg-open http://localhost:9090 & xdg-open http://localhost:15672) || echo "Abre manualmente las URLs en tu navegador"

debug: ## Mostrar información completa de debug
	@echo "$(CYAN)🐛 Información de Debug Completa$(NC)"
	@echo "=================================================================="
	@echo "$(YELLOW)📁 Configuración:$(NC)"
	@echo "  Docker Compose File: $(COMPOSE_FILE)"
	@echo "  Environment File: $(ENV_FILE)"
	@echo ""
	@echo "$(YELLOW)🌐 Redes Docker:$(NC)"
	@docker network ls | grep shibasito || echo "No se encontraron redes de shibasito"
	@echo ""
	@echo "$(YELLOW)💾 Volúmenes Docker:$(NC)"
	@docker volume ls | grep shibasito || echo "No se encontraron volúmenes de shibasito"
	@echo ""
	@echo "$(YELLOW)🖼️  Imágenes Docker:$(NC)"
	@docker images | grep shibasito || echo "No se encontraron imágenes de shibasito"
	@echo ""
	@echo "$(YELLOW)📊 Estado Actual:$(NC)"
	@make status

check: ## Verificar configuración del docker-compose
	@echo "$(CYAN)🔍 Verificando configuración del docker-compose...$(NC)"
	@$(COMPOSE) config
	@echo "$(GREEN)✅ Configuración válida$(NC)"

# =============================================================================
# COMANDOS DE BACKUP Y RESTAURACIÓN
# =============================================================================

backup: ## Crear backup completo de todas las bases de datos
	@echo "$(CYAN)💾 Creando backup completo de bases de datos...$(NC)"
	@mkdir -p backups
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	echo "Creando backup PostgreSQL..."; \
	$(COMPOSE) exec -T bd1_postgresql pg_dump -U banco_user banco_db > backups/postgres_banco_$$timestamp.sql; \
	echo "Creando backup MySQL..."; \
	$(COMPOSE) exec -T bd2_mysql mysqldump -u reniec_user -p'$$MYSQL_PASSWORD' reniec_db > backups/mysql_reniec_$$timestamp.sql; \
	echo "$(GREEN)✅ Backup completado en directorio backups/$(NC)"
	@ls -la backups/

restore: ## Restaurar backup de bases de datos
	@echo "$(YELLOW)⚠️  Restauración de backup - Esto sobrescribirá los datos actuales$(NC)"
	@echo "Últimos backups disponibles:"
	@ls -t backups/ | head -5
	@echo ""
	@echo "Escribe el nombre del archivo de backup de PostgreSQL:"
	@read -r POSTGRES_BACKUP && \
	echo "Escribe el nombre del archivo de backup de MySQL:" && \
	read -r MYSQL_BACKUP && \
	if [ -f "backups/$$POSTGRES_BACKUP" ] && [ -f "backups/$$MYSQL_BACKUP" ]; then \
		echo "Restaurando PostgreSQL..."; \
		$(COMPOSE) exec -T bd1_postgresql psql -U banco_user -d banco_db < backups/$$POSTGRES_BACKUP; \
		echo "Restaurando MySQL..."; \
		$(COMPOSE) exec -T bd2_mysql mysql -u reniec_user -p'$$MYSQL_PASSWORD' reniec_db < backups/$$MYSQL_BACKUP; \
		echo "$(GREEN)✅ Restauración completada$(NC)"; \
	else \
		echo "$(RED)❌ Archivos de backup no encontrados$(NC)"; \
	fi

# =============================================================================
# COMANDOS DE MANTENIMIENTO Y LIMPIEZA
# =============================================================================

clean: ## Limpiar contenedores, redes y volúmenes (⚠️ ELIMINA TODOS LOS DATOS)
	@echo "$(RED)⚠️  ADVERTENCIA: Esto eliminará TODOS los datos del sistema!$(NC)"
	@echo "Esta operación eliminará:"
	@echo "  • Todos los contenedores"
	@echo "  • Todas las redes"
	@echo "  • Todos los volúmenes (PERDERÁS TODOS LOS DATOS)"
	@echo "  • Caché de Docker"
	@echo ""
	@echo "Para confirmar, escribe 'CONFIRM' (sin comillas):"
	@read -r CONFIRM && [ "$$CONFIRM" = "CONFIRM" ] || (echo "$(RED)Operación cancelada$(NC)" && exit 1)
	@echo "$(YELLOW)🧹 Procediendo con la limpieza...$(NC)"
	@$(COMPOSE) down -v --remove-orphans
	@docker system prune -f --volumes
	@echo "$(GREEN)✅ Limpieza completada - Sistema reseteado$(NC)"

# =============================================================================
# COMANDOS ESPECÍFICOS DE SERVICIOS
# =============================================================================

# Logs específicos
logs-banco: ## Ver logs específicos del servicio Banco
	@echo "$(YELLOW)📋 Mostrando logs del servicio Banco (Ctrl+C para salir)...$(NC)"
	@$(COMPOSE) logs -f --tail=50 servicio-banco-lp1

logs-reniec: ## Ver logs específicos del servicio RENIEC
	@echo "$(YELLOW)📋 Mostrando logs del servicio RENIEC (Ctrl+C para salir)...$(NC)"
	@$(COMPOSE) logs -f --tail=50 servicio-reniec-lp2

logs-db: ## Ver logs específicos de las bases de datos
	@echo "$(YELLOW)📋 Mostrando logs de bases de datos (Ctrl+C para salir)...$(NC)"
	@$(COMPOSE) logs -f --tail=50 bd1_postgresql bd2_mysql redis

logs-rabbitmq: ## Ver logs específicos de RabbitMQ
	@echo "$(YELLOW)📋 Mostrando logs de RabbitMQ (Ctrl+C para salir)...$(NC)"
	@$(COMPOSE) logs -f --tail=50 rabbitmq

logs-prometheus: ## Ver logs específicos de Prometheus
	@echo "$(YELLOW)📋 Mostrando logs de Prometheus (Ctrl+C para salir)...$(NC)"
	@$(COMPOSE) logs -f --tail=50 prometheus

logs-grafana: ## Ver logs específicos de Grafana
	@echo "$(YELLOW)📋 Mostrando logs de Grafana (Ctrl+C para salir)...$(NC)"
	@$(COMPOSE) logs -f --tail=50 grafana

# Reinicio específico
restart-banco: ## Reiniciar solo el servicio Banco
	@$(COMPOSE) restart servicio-banco-lp1

restart-reniec: ## Reiniciar solo el servicio RENIEC
	@$(COMPOSE) restart servicio-reniec-lp2

restart-db: ## Reiniciar solo las bases de datos
	@$(COMPOSE) restart bd1_postgresql bd2_mysql redis

# =============================================================================
# COMANDOS DE ACTUALIZACIÓN
# =============================================================================

update: ## Actualizar imágenes Docker y reiniciar servicios
	@echo "$(YELLOW)🔄 Actualizando imágenes Docker...$(NC)"
	@$(COMPOSE) pull
	@echo "$(YELLOW)🔄 Reiniciando servicios con nuevas imágenes...$(NC)"
	@$(COMPOSE) up -d
	@echo "$(GREEN)✅ Actualización completada$(NC)"

# =============================================================================
# COMANDOS ADICIONALES DE UTILIDAD
# =============================================================================

info: ## Mostrar información completa del sistema
	@echo "$(CYAN)📊 Información Completa del Sistema Distribuido$(NC)"
	@echo "=================================================================="
	@echo "$(YELLOW)🐳 Docker Info:$(NC)"
	@docker --version
	@docker-compose --version
	@echo ""
	@echo "$(YELLOW)🗂️  Archivos de Configuración:$(NC)"
	@echo "  Docker Compose: $(COMPOSE_FILE)"
	@echo "  Environment: $(ENV_FILE)"
	@echo "  Override: $(COMPOSE_OVERRIDE)"
	@echo ""
	@echo "$(YELLOW)🌐 URLs del Sistema:$(NC)"
	@echo "  • Grafana: http://localhost:3000 (admin/admin123_secure_2024)"
	@echo "  • RabbitMQ: http://localhost:15672 (admin/admin123_secure_2024)"
	@echo "  • Prometheus: http://localhost:9090"
	@echo "  • API Banco (LP1): http://localhost:8080"
	@echo "  • API RENIEC (LP2): http://localhost:8000"
	@echo ""
	@echo "$(YELLOW)📈 Estado Actual:$(NC)"
	@$(COMPOSE) ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}"

system-resources: ## Mostrar uso de recursos del sistema
	@echo "$(CYAN)💻 Uso de Recursos del Sistema$(NC)"
	@echo "=================================================================="
	@echo "$(YELLOW)🖥️  Información del Host:$(NC)"
	@uname -a
	@echo ""
	@echo "$(YELLOW)💾 Memoria:$(NC)"
	@free -h
	@echo ""
	@echo "$(YELLOW)💿 Disco:$(NC)"
	@df -h | head -10
	@echo ""
	@echo "$(YELLOW)🔥 CPU:$(NC)"
	@top -bn1 | grep "Cpu(s)" | head -1 || htop --version 2>/dev/null || echo "htop no disponible"
	@echo ""
	@echo "$(YELLOW)🐳 Containers:$(NC)"
	@docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

clean-logs: ## Limpiar logs de contenedores (mantener logs recientes)
	@echo "$(YELLOW)🧹 Limpiando logs antiguos de contenedores...$(NC)"
	@for container in $$(docker ps -aq); do \
		echo "Limpiando logs de $$container..."; \
		docker logs --details $$container 2>/dev/null | head -50 > /tmp/recent_logs_$$container; \
		echo "" > $$(docker inspect --format='{{.LogPath}}' $$container); \
		cp /tmp/recent_logs_$$container $$(docker inspect --format='{{.LogPath}}' $$container) 2>/dev/null || true; \
		rm -f /tmp/recent_logs_$$container; \
	done
	@echo "$(GREEN)✅ Logs limpiados exitosamente$(NC)"

quick-health: ## Health check rápido sin detalles
	@echo "$(CYAN)⚡ Health Check Rápido$(NC)"
	@echo "=================================================================="
	-@curl -f -s http://localhost:8080/health > /dev/null && echo "$(GREEN)✅ API Banco: OK$(NC)" || echo "$(RED)❌ API Banco: FALLA$(NC)"
	-@curl -f -s http://localhost:8000/health > /dev/null && echo "$(GREEN)✅ API RENIEC: OK$(NC)" || echo "$(RED)❌ API RENIEC: FALLA$(NC)"
	-@curl -f -s http://localhost:9090/api/v1/query?query=up > /dev/null && echo "$(GREEN)✅ Prometheus: OK$(NC)" || echo "$(RED)❌ Prometheus: FALLA$(NC)"
	-@curl -f -s http://localhost:3000/api/health > /dev/null && echo "$(GREEN)✅ Grafana: OK$(NC)" || echo "$(RED)❌ Grafana: FALLA$(NC)"