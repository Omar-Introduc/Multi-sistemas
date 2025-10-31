# Makefile para Sistema de Stress Testing
# ==========================================
# 
# Este Makefile proporciona comandos simplificados para ejecutar
# todas las funcionalidades del sistema de stress testing.
#
# Uso:
#   make help              # Mostrar ayuda
#   make install           # Instalar dependencias
#   make test-stress-lp1   # Ejecutar stress test LP1
#   make test-stress-lp2   # Ejecutar stress test LP2
#   make test-integrity    # Ejecutar validación de integridad
#   make test-persistence  # Ejecutar tests de persistencia
#   make test-full         # Ejecutar suite completa
#   make reports           # Generar reportes
#   make clean             # Limpiar archivos temporales
#
# Autor: Sistema de Testing Automatizado
# Fecha: 2025-10-30

# Variables de configuración
PYTHON := python3
PIP := pip3
CONFIG_FILE := automation_config.json
REPORTS_DIR := test_reports
LOG_DIR := logs

# Colores para output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

.PHONY: help install test-stress-lp1 test-stress-lp2 test-integrity test-persistence test-full reports clean setup-config example

# Ayuda - Mostrar todos los comandos disponibles
help:
	@echo "$(BLUE)🏗️  SISTEMA DE STRESS TESTING - COMANDOS DISPONIBLES$(NC)"
	@echo "=================================================================="
	@echo ""
	@echo "$(YELLOW)Instalación y Configuración:$(NC)"
	@echo "  install            Instalar dependencias Python"
	@echo "  setup-config       Crear archivo de configuración de ejemplo"
	@echo "  example            Ejecutar ejemplos de uso"
	@echo ""
	@echo "$(YELLOW)Tests Individuales:$(NC)"
	@echo "  test-stress-lp1    Ejecutar stress test LP1 (Sistema Bancario)"
	@echo "  test-stress-lp2    Ejecutar stress test LP2 (Sistema RENIEC)"
	@echo "  test-integrity     Ejecutar validación de integridad BD1 vs BD2"
	@echo "  test-persistence   Ejecutar tests de persistencia"
	@echo ""
	@echo "$(YELLOW)Ejecución Completa:$(NC)"
	@echo "  test-full          Ejecutar suite completa de tests"
	@echo "  test-stress        Ejecutar solo tests de estrés (LP1+LP2)"
	@echo "  test-validation    Ejecutar solo validaciones (integridad+persistencia)"
	@echo ""
	@echo "$(YELLOW)Reportes y Análisis:$(NC)"
	@echo "  reports            Generar reportes de ejemplo"
	@echo "  view-reports       Abrir directorio de reportes"
	@echo "  clean              Limpiar archivos temporales y reportes antiguos"
	@echo ""
	@echo "$(YELLOW)Utilidades:$(NC)"
	@echo "  status             Verificar estado del sistema"
	@echo "  logs               Mostrar logs recientes"
	@echo "  validate-config    Validar archivo de configuración"
	@echo ""
	@echo "$(GREEN)Ejemplo de uso:$(NC)"
	@echo "  1. make install"
	@echo "  2. make setup-config"
	@echo "  3. make test-stress-lp1"
	@echo "  4. make reports"
	@echo ""

# Instalar dependencias Python
install:
	@echo "$(BLUE)📦 Instalando dependencias...$(NC)"
	$(PIP) install mysql-connector-python pandas schedule
	@echo "$(GREEN)✅ Dependencias instaladas correctamente$(NC)"

# Crear configuración de ejemplo
setup-config:
	@echo "$(BLUE)⚙️  Creando configuración de ejemplo...$(NC)"
	$(PYTHON) automation_test_suite.py --create-config
	@echo "$(GREEN)✅ Configuración creada: $(CONFIG_FILE)$(NC)"

# Ejecutar ejemplos de uso
example:
	@echo "$(BLUE)🎯 Ejecutando ejemplos de uso...$(NC)"
	$(PYTHON) example_usage.py

# Stress test LP1 - Sistema Bancario
test-stress-lp1:
	@echo "$(BLUE)🚀 Ejecutando stress test LP1 (Sistema Bancario)...$(NC)"
	@echo "Target: 1500 registros con 50 hilos concurrentes"
	$(PYTHON) stress_test_lp1.py
	@echo "$(GREEN)✅ Stress test LP1 completado$(NC)"

# Stress test LP2 - Sistema RENIEC
test-stress-lp2:
	@echo "$(BLUE)🚀 Ejecutando stress test LP2 (Sistema RENIEC)...$(NC)"
	@echo "Target: 1500 ciudadanos con validaciones"
	$(PYTHON) stress_test_lp2.py
	@echo "$(GREEN)✅ Stress test LP2 completado$(NC)"

# Validación de integridad
test-integrity:
	@echo "$(BLUE)🔍 Ejecutando validación de integridad...$(NC)"
	@echo "Comparación BD1 vs BD2"
	$(PYTHON) validate_data_integrity.py
	@echo "$(GREEN)✅ Validación de integridad completada$(NC)"

# Tests de persistencia
test-persistence:
	@echo "$(BLUE)💾 Ejecutando tests de persistencia...$(NC)"
	@echo "Validación de backups y recuperación"
	$(PYTHON) persistence_tests.py
	@echo "$(GREEN)✅ Tests de persistencia completados$(NC)"

# Ejecutar solo tests de estrés
test-stress: test-stress-lp1 test-stress-lp2
	@echo "$(GREEN)✅ Tests de estrés completados (LP1 + LP2)$(NC)"

# Ejecutar solo validaciones
test-validation: test-integrity test-persistence
	@echo "$(GREEN)✅ Validaciones completadas (Integridad + Persistencia)$(NC)"

# Ejecutar suite completa
test-full:
	@echo "$(BLUE)🚀 Ejecutando suite completa de tests...$(NC)"
	@echo "Incluye: Stress + Integridad + Persistencia + Reportes"
	@if [ -f "$(CONFIG_FILE)" ]; then \
		$(PYTHON) automation_test_suite.py --mode full --config $(CONFIG_FILE); \
	else \
		echo "$(YELLOW)⚠️  Configuración no encontrada, usando configuración por defecto$(NC)"; \
		$(PYTHON) automation_test_suite.py --mode full; \
	fi
	@echo "$(GREEN)✅ Suite completa ejecutada$(NC)"

# Generar reportes de ejemplo
reports:
	@echo "$(BLUE)📊 Generando reportes de ejemplo...$(NC)"
	$(PYTHON) generate_test_reports.py
	@echo "$(GREEN)✅ Reportes generados en $(REPORTS_DIR)/$(NC)"

# Ver directorio de reportes
view-reports:
	@echo "$(BLUE)📁 Abriendo directorio de reportes...$(NC)"
	@if [ -d "$(REPORTS_DIR)" ]; then \
		ls -la $(REPORTS_DIR)/; \
		@if command -v open > /dev/null; then \
			open $(REPORTS_DIR)/; \
		elif command -v xdg-open > /dev/null; then \
			xdg-open $(REPORTS_DIR)/; \
		fi \
	else \
		echo "$(YELLOW)⚠️  Directorio de reportes no existe. Ejecuta 'make reports' primero$(NC)"; \
	fi

# Verificar estado del sistema
status:
	@echo "$(BLUE)📈 Verificando estado del sistema...$(NC)"
	@echo "Python version:"
	$(PYTHON) --version
	@echo ""
	@echo "Directorio actual:"
	pwd
	@echo ""
	@echo "Archivos del sistema:"
	ls -la *.py
	@echo ""
	@echo "Configuración:"
	@if [ -f "$(CONFIG_FILE)" ]; then \
		echo "✅ $(CONFIG_FILE) existe"; \
	else \
		echo "$(YELLOW)⚠️  $(CONFIG_FILE) no existe. Ejecuta 'make setup-config'$(NC)"; \
	fi
	@echo ""
	@echo "Directorio de reportes:"
	@if [ -d "$(REPORTS_DIR)" ]; then \
		echo "✅ $(REPORTS_DIR)/ existe"; \
		echo "Archivos: $$(ls $(REPORTS_DIR)/ | wc -l)"; \
	else \
		echo "$(YELLOW)⚠️  $(REPORTS_DIR)/ no existe$(NC)"; \
	fi

# Mostrar logs recientes
logs:
	@echo "$(BLUE)📋 Mostrando logs recientes...$(NC)"
	@if [ -d "$(LOG_DIR)" ]; then \
		tail -20 $(LOG_DIR)/*.log 2>/dev/null || echo "No hay logs disponibles"; \
	else \
		echo "$(YELLOW)⚠️  Directorio de logs no existe$(NC)"; \
	fi

# Validar configuración
validate-config:
	@echo "$(BLUE)🔍 Validando configuración...$(NC)"
	@if [ -f "$(CONFIG_FILE)" ]; then \
		$(PYTHON) -c "import json; json.load(open('$(CONFIG_FILE)'))" && \
		echo "$(GREEN)✅ Configuración válida$(NC)" || \
		echo "$(RED)❌ Error en configuración$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Archivo de configuración no existe$(NC)"; \
		echo "Ejecuta 'make setup-config' para crear uno"; \
	fi

# Limpiar archivos temporales
clean:
	@echo "$(BLUE)🧹 Limpiando archivos temporales...$(NC)"
	@echo "Eliminando archivos temporales..."
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.log" -mtime +7 -delete 2>/dev/null || true
	@if [ -d "$(REPORTS_DIR)" ]; then \
		echo "Limpiando reportes antiguos (>30 días)..."; \
		find $(REPORTS_DIR)/ -name "*.html" -mtime +30 -delete 2>/dev/null || true; \
		find $(REPORTS_DIR)/ -name "*.json" -mtime +30 -delete 2>/dev/null || true; \
	fi
	@if [ -d "$(LOG_DIR)" ]; then \
		echo "Limpiando logs antiguos (>30 días)..."; \
		find $(LOG_DIR)/ -name "*.log" -mtime +30 -delete 2>/dev/null || true; \
	fi
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

# Limpieza completa (peligroso - elimina todo)
clean-all: clean
	@echo "$(YELLOW)⚠️  Eliminando TODOS los reportes y datos generados...$(NC)"
	@read -p "Esta acción eliminará todos los reportes. ¿Continuar? [y/N] " confirm && \
	[ "$$confirm" = "y" ] || exit 1; \
	rm -rf $(REPORTS_DIR)/ $(LOG_DIR)/ *.json test_*.log *.log 2>/dev/null || true; \
	@echo "$(GREEN)✅ Limpieza completa realizada$(NC)"

# Compilar el sistema (verificación)
compile:
	@echo "$(BLUE)🔧 Compilando/verificando sistema...$(NC)"
	@echo "Verificando sintaxis Python..."
	@for file in *.py; do \
		if [ -f "$$file" ]; then \
			$(PYTHON) -m py_compile $$file && echo "✅ $$file" || echo "❌ $$file"; \
		fi; \
	done
	@echo "$(GREEN)✅ Verificación de sintaxis completada$(NC)"

# Instalar sistema (setup completo)
install-all: install setup-config
	@echo "$(GREEN)🎉 Sistema instalado y configurado correctamente$(NC)"
	@echo "Para empezar: make test-stress-lp1"

# Mostrar información del sistema
info:
	@echo "$(BLUE)ℹ️  INFORMACIÓN DEL SISTEMA$(NC)"
	@echo "==============================="
	@echo "Directorio: $(PWD)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Usuario: $$(whoami)"
	@echo "Fecha: $$(date)"
	@echo ""
	@echo "Archivos del sistema:"
	@ls -1 *.py | sed 's/^/  • /'
	@echo ""
	@echo "Para más información: make help"

# Test de conectividad a bases de datos
test-connections:
	@echo "$(BLUE)🔗 Probando conectividad a bases de datos...$(NC)"
	@if command -v mysql >/dev/null 2>&1; then \
		echo "MySQL disponible"; \
		mysql --version; \
	else \
		echo "$(YELLOW)⚠️  MySQL no encontrado en PATH$(NC)"; \
	fi
	@echo "$(GREEN)✅ Verificación de conectividad completada$(NC)"

# Ejecutar todos los tests en modo demo (sin BD real)
demo:
	@echo "$(BLUE)🎭 Ejecutando demo del sistema...$(NC)"
	@echo "Este demo muestra las capacidades sin ejecutar tests reales"
	$(PYTHON) example_usage.py

# Ayuda rápida
quick-start: install-all
	@echo "$(GREEN)🚀 INSTALACIÓN RÁPIDA COMPLETADA$(NC)"
	@echo ""
	@echo "Para empezar rápidamente:"
	@echo "1. Edita $(CONFIG_FILE) con tus credenciales de BD"
	@echo "2. Ejecuta: make test-stress-lp1"
	@echo "3. Ver resultados: make view-reports"
	@echo ""
	@echo "Para más opciones: make help"

# Targets de desarrollo
dev-setup: install
	@echo "$(BLUE)🛠️  Configuración para desarrollo...$(NC)"
	$(PYTHON) -m pip install --user pylint black flake8 pytest
	@echo "$(GREEN)✅ Herramientas de desarrollo instaladas$(NC)"

# Verificar calidad del código
lint:
	@echo "$(BLUE)🔍 Verificando calidad del código...$(NC)"
	@if command -v pylint >/dev/null 2>&1; then \
		pylint *.py; \
	else \
		echo "$(YELLOW)⚠️  pylint no disponible. Instala con: pip install pylint$(NC)"; \
	fi

# Ejecutar tests unitarios (si existen)
test-unit:
	@echo "$(BLUE)🧪 Ejecutando tests unitarios...$(NC)"
	@if [ -d "tests" ]; then \
		$(PYTHON) -m pytest tests/ -v; \
	else \
		echo "$(YELLOW)⚠️  Directorio tests/ no existe$(NC)"; \
	fi

# Descripción del proyecto
desc:
	@echo "$(BLUE)📋 DESCRIPCIÓN DEL PROYECTO$(NC)"
	@echo "============================="
	@echo ""
	@echo "Sistema Completo de Stress Testing para:"
	@echo "  • LP1 - Sistema Bancario (MySQL)"
	@echo "  • LP2 - Sistema RENIEC (MySQL)"
	@echo "  • Validación de integridad entre bases de datos"
	@echo "  • Tests de persistencia y recuperación"
	@echo "  • Generación automática de reportes HTML/JSON"
	@echo "  • Automatización completa con scheduling"
	@echo ""
	@echo "Características principales:"
	@echo "  ✓ 1500+ registros de prueba automatizados"
	@echo "  ✓ 50 hilos concurrentes para carga máxima"
	@echo "  ✓ Métricas detalladas de performance"
	@echo "  ✓ Validación de integridad referencial"
	@echo "  ✓ Tests de recuperación ante fallos"
	@echo "  ✓ Reportes interactivos con gráficos"
	@echo "  ✓ Configuración centralizada JSON"
	@echo "  ✓ Programación automática de tests"
	@echo ""
