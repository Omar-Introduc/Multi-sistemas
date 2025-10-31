#!/bin/bash

# =============================================================================
# SCRIPT DE CONFIGURACIÓN DE ESTRUCTURA DE DIRECTORIOS
# Crea la estructura necesaria para los servicios optimizados
# =============================================================================

set -euo pipefail

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Directorios base
BASE_DIR="/workspace/shibasito-sistema-distribuido"

# Función para crear directorio con permisos
create_directory() {
    local dir_path="$1"
    local description="$2"
    
    if [ -d "$dir_path" ]; then
        log_info "Directorio ya existe: $description ($dir_path)"
    else
        mkdir -p "$dir_path"
        log_success "Creado: $description ($dir_path)"
    fi
}

# Función para crear archivos .gitkeep
create_gitkeep() {
    local dir_path="$1"
    
    if [ ! -f "$dir_path/.gitkeep" ]; then
        touch "$dir_path/.gitkeep"
        echo "# Este archivo mantiene el directorio en el control de versiones" > "$dir_path/.gitkeep"
    fi
}

# Función principal
main() {
    echo "=============================================="
    echo "  CONFIGURACIÓN DE ESTRUCTURA DE DIRECTORIOS"
    echo "=============================================="
    echo ""
    
    log_info "Creando estructura de directorios para servicios optimizados..."
    echo ""
    
    # Directorios de datos
    log_info "Creando directorios de datos..."
    create_directory "$BASE_DIR/data/postgres/bd1" "PostgreSQL BD1 - Datos"
    create_directory "$BASE_DIR/data/mysql/bd2" "MySQL BD2 - Datos"
    create_directory "$BASE_DIR/data/rabbitmq" "RabbitMQ - Datos"
    create_directory "$BASE_DIR/data/redis" "Redis - Datos"
    create_directory "$BASE_DIR/data/prometheus" "Prometheus - Datos"
    create_directory "$BASE_DIR/data/grafana" "Grafana - Datos"
    
    # Directorios de logs
    log_info "Creando directorios de logs..."
    create_directory "$BASE_DIR/logs/postgres/bd1" "PostgreSQL BD1 - Logs"
    create_directory "$BASE_DIR/logs/mysql/bd2" "MySQL BD2 - Logs"
    create_directory "$BASE_DIR/logs/rabbitmq" "RabbitMQ - Logs"
    create_directory "$BASE_DIR/logs/redis" "Redis - Logs"
    create_directory "$BASE_DIR/logs/prometheus" "Prometheus - Logs"
    create_directory "$BASE_DIR/logs/grafana" "Grafana - Logs"
    create_directory "$BASE_DIR/logs/banco" "Servicio Banco - Logs"
    create_directory "$BASE_DIR/logs/reniec" "Servicio RENIEC - Logs"
    
    # Directorios de backup
    log_info "Creando directorios de backup..."
    create_directory "$BASE_DIR/backup/postgres/bd1" "PostgreSQL BD1 - Backup"
    create_directory "$BASE_DIR/backup/mysql/bd2" "MySQL BD2 - Backup"
    create_directory "$BASE_DIR/backup/redis" "Redis - Backup"
    
    # Archivos .gitkeep para mantener directorios en Git
    log_info "Creando archivos .gitkeep..."
    find "$BASE_DIR/data" -type d -exec create_gitkeep {} \;
    find "$BASE_DIR/logs" -type d -exec create_gitkeep {} \;
    find "$BASE_DIR/backup" -type d -exec create_gitkeep {} \;
    
    echo ""
    log_info "Estructura de directorios creada exitosamente"
    echo ""
    
    # Mostrar resumen
    log_info "Resumen de estructura creada:"
    echo "  📁 data/"
    echo "    📁 postgres/bd1/     (PostgreSQL BD1 - Datos)"
    echo "    📁 mysql/bd2/        (MySQL BD2 - Datos)"
    echo "    📁 rabbitmq/         (RabbitMQ - Datos)"
    echo "    📁 redis/            (Redis - Datos)"
    echo "    📁 prometheus/       (Prometheus - Datos)"
    echo "    📁 grafana/          (Grafana - Datos)"
    echo "  📁 logs/"
    echo "    📁 postgres/bd1/     (PostgreSQL BD1 - Logs)"
    echo "    📁 mysql/bd2/        (MySQL BD2 - Logs)"
    echo "    📁 rabbitmq/         (RabbitMQ - Logs)"
    echo "    📁 redis/            (Redis - Logs)"
    echo "    📁 prometheus/       (Prometheus - Logs)"
    echo "    📁 grafana/          (Grafana - Logs)"
    echo "    📁 banco/            (Servicio Banco - Logs)"
    echo "    📁 reniec/           (Servicio RENIEC - Logs)"
    echo "  📁 backup/"
    echo "    📁 postgres/bd1/     (PostgreSQL BD1 - Backup)"
    echo "    📁 mysql/bd2/        (MySQL BD2 - Backup)"
    echo "    📁 redis/            (Redis - Backup)"
    echo ""
    
    # Verificar permisos
    log_info "Verificando permisos de escritura..."
    local write_dirs=("$BASE_DIR/data" "$BASE_DIR/logs" "$BASE_DIR/backup")
    
    for dir in "${write_dirs[@]}"; do
        if [ -w "$dir" ]; then
            log_success "Permisos OK: $dir"
        else
            log_warning "Problema de permisos: $dir"
        fi
    done
    
    echo ""
    log_success "¡Configuración de estructura completada!"
    echo ""
    log_info "Ahora puedes ejecutar el docker-compose optimizado"
    echo "Comandos útiles:"
    echo "  - docker-compose -f docker-compose.main.yml up -d"
    echo "  - docker-compose -f docker-compose.main.yml ps"
    echo "  - ./scripts/postgres-backup.sh backup"
    echo ""
}

# Ejecutar script
main "$@"
