# Sistema de Testing Final - Makefile
# ==================================

.PHONY: help setup test-all test-unit test-integration test-e2e test-performance test-security validate generate-reports clean install-deps docker-build docker-run

# Variables
PYTHON := python3
PIP := pip3
DOCKER := docker
DOCKER_COMPOSE := docker-compose
REPORTS_DIR := reports
LOGS_DIR := execution_logs

# Colores para output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Help target
help: ## Mostrar ayuda con todos los comandos disponibles
	@echo "$(BLUE)🎯 Sistema de Testing Final v2.0 - Comandos Disponibles$(RESET)"
	@echo "$(YELLOW)=====================================================$(RESET)"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(GREEN)%-25s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# Setup
setup: ## Configuración completa del entorno de testing
	@echo "$(BLUE)🚀 Configurando entorno de testing...$(RESET)"
	$(MAKE) install-deps
	$(MAKE) create-dirs
	$(MAKE) setup-playwright
	$(MAKE) validate
	@echo "$(GREEN)✅ Setup completado exitosamente!$(RESET)"

install-deps: ## Instalar dependencias Python
	@echo "$(YELLOW)📦 Instalando dependencias...$(RESET)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-test.txt
	@echo "$(GREEN)✅ Dependencias instaladas$(RESET)"

create-dirs: ## Crear directorios necesarios
	@echo "$(YELLOW)📁 Creando directorios...$(RESET)"
	mkdir -p $(REPORTS_DIR) $(LOGS_DIR)
	mkdir -p unit_tests integration_tests e2e_tests performance_tests security_tests
	@echo "$(GREEN)✅ Directorios creados$(RESET)"

setup-playwright: ## Instalar navegadores para Playwright
	@echo "$(YELLOW)🎭 Configurando Playwright...$(RESET)"
	playwright install chromium
	@echo "$(GREEN)✅ Playwright configurado$(RESET)"

# Testing targets
test-all: ## Ejecutar todos los tests
	@echo "$(BLUE)🧪 Ejecutando todos los tests...$(RESET)"
	$(PYTHON) run_all_tests.py --generate-report
	@echo "$(GREEN)✅ Tests completados$(RESET)"

test-unit: ## Ejecutar solo tests unitarios
	@echo "$(BLUE)🧪 Tests unitarios...$(RESET)"
	pytest unit_tests/ --cov=src --cov-report=html:$(REPORTS_DIR)/coverage_unit_html --html=$(REPORTS_DIR)/unit_tests_report.html --self-contained-html -v

test-integration: ## Ejecutar tests de integración
	@echo "$(BLUE)🔗 Tests de integración...$(RESET)"
	pytest integration_tests/ --html=$(REPORTS_DIR)/integration_tests_report.html --self-contained-html -v

test-e2e: ## Ejecutar tests end-to-end
	@echo "$(BLUE)🌐 Tests E2E...$(RESET)"
	playwright test e2e_tests/ --reporter=html --output-dir=$(REPORTS_DIR)/e2e-results

test-performance: ## Ejecutar tests de performance
	@echo "$(BLUE)⚡ Tests de performance...$(RESET)"
	locust -f performance_tests/load_test.py --headless --users 50 --spawn-rate 10 --run-time 300s --csv=$(REPORTS_DIR)/performance_50_users --html=$(REPORTS_DIR)/performance_report.html

test-security: ## Ejecutar tests de seguridad
	@echo "$(BLUE)🔒 Tests de seguridad...$(RESET)"
	bandit -r src/ -f json -o $(REPORTS_DIR)/security_bandit.json || true
	safety check --json --output $(REPORTS_DIR)/security_safety.json || true

# Validation
validate: ## Validar sistema completo
	@echo "$(BLUE)🔍 Validando sistema...$(RESET)"
	$(PYTHON) validate_system.py --verbose

validate-quick: ## Validación rápida del sistema
	@echo "$(BLUE)⚡ Validación rápida...$(RESET)"
	$(PYTHON) validate_system.py

# Reports
generate-reports: ## Generar reportes finales
	@echo "$(BLUE)📊 Generando reportes...$(RESET)"
	$(PYTHON) generate_final_report.py --input $(REPORTS_DIR)/test_results.json --output-dir $(REPORTS_DIR)

# CI/CD targets
ci-test: ## Testing para CI/CD
	@echo "$(BLUE)🔄 Testing para CI/CD...$(RESET)"
	$(MAKE) validate-quick
	$(MAKE) test-unit
	$(MAKE) test-integration
	$(MAKE) test-security
	@echo "$(GREEN)✅ CI Testing completado$(RESET)"

ci-full: ## Testing completo para CI/CD
	@echo "$(BLUE)🔄 Testing completo para CI/CD...$(RESET)"
	$(MAKE) validate
	$(MAKE) test-all
	$(MAKE) generate-reports
	@echo "$(GREEN)✅ CI Full Testing completado$(RESET)"

# Docker targets
docker-build: ## Construir imagen Docker para testing
	@echo "$(BLUE)🐳 Construyendo imagen Docker...$(RESET)"
	$(DOCKER) build -t shibasito-testing .

docker-run: ## Ejecutar testing en Docker
	@echo "$(BLUE)🐳 Ejecutando testing en Docker...$(RESET)"
	$(DOCKER) run -v $(PWD)/$(REPORTS_DIR):/app/$(REPORTS_DIR) -v $(PWD)/$(LOGS_DIR):/app/$(LOGS_DIR) shibasito-testing

docker-compose-test: ## Ejecutar testing con docker-compose
	@echo "$(BLUE)🐳 Testing con docker-compose...$(RESET)"
	$(DOCKER_COMPOSE) -f docker-compose.testing.yml up --build --abort-on-container-exit

# Cleanup
clean: ## Limpiar archivos temporales y reportes antiguos
	@echo "$(YELLOW)🧹 Limpiando archivos...$(RESET)"
	find $(LOGS_DIR) -name "*.log" -mtime +7 -delete 2>/dev/null || true
	find $(REPORTS_DIR) -name "*.html" -mtime +30 -delete 2>/dev/null || true
	find $(REPORTS_DIR) -name "*.json" -mtime +30 -delete 2>/dev/null || true
	rm -f temp_*.py
	rm -f .coverage
	@echo "$(GREEN)✅ Limpieza completada$(RESET)"

clean-all: ## Limpiar todo (incluyendo dependencias)
	@echo "$(YELLOW)🧹 Limpieza completa...$(RESET)"
	$(MAKE) clean
	$(DOCKER) system prune -f 2>/dev/null || true
	@echo "$(GREEN)✅ Limpieza completa terminada$(RESET)"

# Development
dev-install: ## Instalación para desarrollo
	@echo "$(BLUE)👨‍💻 Configuración para desarrollo...$(RESET)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-test.txt
	$(PIP) install -e .
	@echo "$(GREEN)✅ Desarrollo configurado$(RESET)"

dev-test: ## Ejecutar tests en modo desarrollo
	@echo "$(BLUE)🧪 Tests en modo desarrollo...$(RESET)"
	pytest unit_tests/ -v --tb=short -x

dev-watch: ## Ejecutar tests en modo watch
	@echo "$(BLUE)👀 Tests en modo watch...$(RESET)"
	ptw unit_tests/ integration_tests/ -- -v

# Monitoring
logs: ## Mostrar logs de testing
	@echo "$(BLUE)📄 Mostrando logs recientes...$(RESET)"
	tail -n 50 $(LOGS_DIR)/test_execution_*.log 2>/dev/null | head -20 || echo "No hay logs disponibles"

logs-follow: ## Seguir logs en tiempo real
	@echo "$(BLUE)👁️ Siguiendo logs...$(RESET)"
	tail -f $(LOGS_DIR)/test_execution_*.log

monitor: ## Monitorear recursos del sistema
	@echo "$(BLUE)📊 Monitoreando recursos...$(RESET)"
	@echo "$(YELLOW)CPU y Memoria:$(RESET)"
	top -bn1 | grep "Cpu(s)" && free -h
	@echo "$(YELLOW)Espacio en disco:$(RESET)"
	df -h . | tail -1

# Documentation
docs: ## Generar documentación
	@echo "$(BLUE)📚 Generando documentación...$(RESET)"
	@echo "$(GREEN)Documentación disponible en README.md$(RESET)"

# Health check
health: ## Verificar salud del sistema de testing
	@echo "$(BLUE)💊 Verificando salud del sistema...$(RESET)"
	$(MAKE) validate-quick
	@echo "$(YELLOW)Archivos del sistema:$(RESET)"
	@ls -la $(REPORTS_DIR)/ 2>/dev/null | head -10 || echo "Directorio de reportes vacío"

# Debug
debug-config: ## Mostrar configuración actual
	@echo "$(BLUE)🔧 Configuración actual:$(RESET)"
	@echo "$(YELLOW)Python: $(shell $(PYTHON) --version)$(RESET)"
	@echo "$(YELLOW)Pip: $(shell $(PIP) --version)$(RESET)"
	@echo "$(YELLOW)Docker: $(shell $(DOCKER) --version 2>/dev/null || echo "No instalado")$(RESET)"
	@echo "$(YELLOW)Python path: $(shell which $(PYTHON))$(RESET)"

# Quality
lint: ## Ejecutar linters de código
	@echo "$(BLUE)🔍 Ejecutando linters...$(RESET)"
	flake8 *.py unit_tests/ integration_tests/ --max-line-length=100 || true
	black --check *.py unit_tests/ integration_tests/ || true

format: ## Formatear código
	@echo "$(BLUE)✨ Formateando código...$(RESET)"
	black *.py unit_tests/ integration_tests/

security-scan: ## Escaneo rápido de seguridad
	@echo "$(BLUE)🔒 Escaneo de seguridad...$(RESET)"
	bandit -r . -f json -o $(REPORTS_DIR)/quick_security_scan.json || true

# Backup y restore
backup-reports: ## Respaldar reportes importantes
	@echo "$(BLUE)💾 Respaldando reportes...$(RESET)"
	tar -czf $(REPORTS_DIR)/reports_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz $(REPORTS_DIR)/$(shell date +%Y%m%d)*
	@echo "$(GREEN)✅ Respaldo completado$(RESET)"

# Environment specific
staging-test: ## Ejecutar tests en ambiente staging
	@echo "$(BLUE)🎭 Testing en staging...$(RESET)"
	TEST_ENV=staging $(MAKE) test-all

production-test: ## Ejecutar tests en ambiente production
	@echo "$(BLUE)🚀 Testing en production...$(RESET)"
	TEST_ENV=production $(MAKE) test-all

# Performance monitoring
performance-monitor: ## Monitoreo de performance durante testing
	@echo "$(BLUE)📊 Monitoreando performance...$(RESET)"
	@echo "$(YELLOW)Iniciando monitoreo en background...$(RESET)"
	nohup htop > $(LOGS_DIR)/system_performance.log 2>&1 &
	@echo "$(GREEN)✅ Monitoreo iniciado - revisar $(LOGS_DIR)/system_performance.log$(RESET)"

# Quick commands
quick: ## Validación y tests unitarios rápidos
	@echo "$(BLUE)⚡ Ejecución rápida...$(RESET)"
	$(MAKE) validate-quick
	$(MAKE) test-unit

full: ## Ejecución completa con todo incluido
	@echo "$(BLUE)🎯 Ejecución completa del sistema...$(RESET)"
	$(MAKE) setup
	$(MAKE) test-all
	$(MAKE) generate-reports
	@echo "$(GREEN)🎉 Ejecución completa terminada!$(RESET)"

# Show status
status: ## Mostrar estado del sistema
	@echo "$(BLUE)📊 Estado del Sistema de Testing$(RESET)"
	@echo "$(YELLOW)=========================$(RESET)"
	@echo "📁 Directorio actual: $(PWD)"
	@echo "🐍 Python: $(shell $(PYTHON) --version 2>/dev/null || echo "No instalado")"
	@echo "🐳 Docker: $(shell $(DOCKER) --version 2>/dev/null || echo "No instalado")"
	@echo "📋 Configuración: $(shell test -f test_suite_config.yml && echo "✅ Encontrada" || echo "❌ No encontrada")"
	@echo "📦 Dependencies: $(shell test -f requirements-test.txt && echo "✅ Encontradas" || echo "❌ No encontradas")"
	@echo "📁 Reportes: $(shell ls -d $(REPORTS_DIR) 2>/dev/null && echo "✅ Creados" || echo "❌ No creados")"
	@echo "📄 Logs: $(shell ls -d $(LOGS_DIR) 2>/dev/null && echo "✅ Creados" || echo "❌ No creados")"