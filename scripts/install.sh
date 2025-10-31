#!/bin/bash

# Script de instalación completa del sistema de Health Checks
# Autor: Sistema de Monitoreo
# Fecha: $(date +%Y-%m-%d)

set -e

# Configuración
INSTALL_DIR="/usr/local/bin/health-checks"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/health-checks-install.log"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Función para logging
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
    
    case $level in
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message" >&2
            ;;
        "WARN")
            echo -e "${YELLOW}[WARN]${NC} $message"
            ;;
        "INFO")
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
    esac
}

# Banner de inicio
show_banner() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║              SISTEMA DE HEALTH CHECKS AVANZADOS              ║
║                     Instalador Automático                    ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo ""
}

# Verificar si se ejecuta como root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log "ERROR" "Este script debe ejecutarse como root"
        log "INFO" "Ejecuta: sudo $0"
        exit 1
    fi
}

# Verificar dependencias del sistema
check_system_dependencies() {
    log "INFO" "Verificando dependencias del sistema..."
    
    local missing_deps=()
    local required_commands=("bash" "systemctl" "curl" "bc" "jq" "python3")
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log "WARN" "Dependencias faltantes: ${missing_deps[*]}"
        
        # Detectar distribución
        if [ -f /etc/debian_version ]; then
            log "INFO" "Detectado: Sistema Debian/Ubuntu"
            install_debian_deps
        elif [ -f /etc/redhat-release ]; then
            log "INFO" "Detectado: Sistema RedHat/CentOS"
            install_rhel_deps
        else
            log "ERROR" "Distribución no soportada. Instala manualmente: ${missing_deps[*]}"
            exit 1
        fi
    else
        log "SUCCESS" "Todas las dependencias están instaladas"
    fi
}

# Instalar dependencias para Debian/Ubuntu
install_debian_deps() {
    log "INFO" "Instalando dependencias para Debian/Ubuntu..."
    
    apt-get update -qq
    apt-get install -y \
        bash \
        systemctl \
        curl \
        bc \
        jq \
        python3 \
        postgresql-client \
        mysql-client \
        redis-tools \
        rabbitmq-tools \
        mailutils \
        logrotate \
        sudo
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Dependencias instaladas correctamente"
    else
        log "ERROR" "Error al instalar dependencias"
        exit 1
    fi
}

# Instalar dependencias para RedHat/CentOS
install_rhel_deps() {
    log "INFO" "Instalando dependencias para RedHat/CentOS..."
    
    yum install -y \
        bash \
        curl \
        bc \
        jq \
        python3 \
        postgresql \
        mysql \
        redis \
        rabbitmq-server \
        mailx \
        logrotate
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Dependencias instaladas correctamente"
    else
        log "ERROR" "Error al instalar dependencias"
        exit 1
    fi
}

# Crear estructura de directorios
create_directory_structure() {
    log "INFO" "Creando estructura de directorios..."
    
    local dirs=(
        "$INSTALL_DIR"
        "$INSTALL_DIR/logs"
        "$INSTALL_DIR/reports"
        "/var/log/health-checks"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log "SUCCESS" "Directorio creado: $dir"
        else
            log "INFO" "Directorio ya existe: $dir"
        fi
    done
    
    # Configurar permisos
    chmod 755 "$INSTALL_DIR"
    chmod 755 "$INSTALL_DIR/logs"
    chmod 755 "$INSTALL_DIR/reports"
    chmod 755 "/var/log/health-checks"
}

# Instalar scripts
install_scripts() {
    log "INFO" "Instalando scripts..."
    
    # Copiar scripts principales
    local scripts=(
        "health-check.sh"
        "check-db-connections.sh"
        "check-rabbitmq.sh"
        "check-redis.sh"
        "generate-health-report.sh"
        "setup-cron.sh"
    )
    
    for script in "${scripts[@]}"; do
        local src="$SCRIPT_DIR/$script"
        local dst="$INSTALL_DIR/$script"
        
        if [ -f "$src" ]; then
            cp "$src" "$dst"
            chmod +x "$dst"
            log "SUCCESS" "Script instalado: $script"
        else
            log "ERROR" "Script no encontrado: $script"
        fi
    done
    
    # Copiar documentación
    if [ -f "$SCRIPT_DIR/README.md" ]; then
        cp "$SCRIPT_DIR/README.md" "$INSTALL_DIR/README.md"
        log "SUCCESS" "Documentación instalada"
    fi
    
    # Crear enlace simbólico global
    ln -sf "$INSTALL_DIR" /usr/local/bin/health-checks
    
    log "SUCCESS" "Scripts instalados en: $INSTALL_DIR"
}

# Configurar servicios
configure_services() {
    log "INFO" "Configurando servicios del sistema..."
    
    # Habilitar servicios si existen
    local services=("redis-server" "rabbitmq-server" "postgresql" "nginx")
    
    for service in "${services[@]}"; do
        if systemctl list-unit-files --type=service | grep -q "^$service"; then
            systemctl enable "$service" 2>/dev/null || true
            log "INFO" "Servicio habilitado: $service"
        fi
    done
}

# Configurar archivos de configuración por defecto
create_default_configs() {
    log "INFO" "Creando configuraciones por defecto..."
    
    # Configuración de ejemplo para bases de datos
    cat > "$INSTALL_DIR/config.env.example" << 'EOF'
# Configuración de ejemplo para Health Checks
# Copia este archivo como config.env y modifica según tu entorno

# RabbitMQ
export RABBITMQ_USER="admin"
export RABBITMQ_PASSWORD="your_password"
export RABBITMQ_HOST="localhost"
export RABBITMQ_PORT="15672"

# Redis
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export REDIS_PASSWORD="your_redis_password"

# Bases de Datos
export DB_POSTGRES_HOST="localhost"
export DB_POSTGRES_PORT="5432"
export DB_POSTGRES_USER="app_user"
export DB_POSTGRES_PASSWORD="db_password"
export DB_POSTGRES_DB="app_db"

export DB_MYSQL_HOST="localhost"
export DB_MYSQL_PORT="3306"
export DB_MYSQL_USER="app_user"
export DB_MYSQL_PASSWORD="db_password"

# Notificaciones
export ALERT_EMAIL="admin@sistema.local"
export SLACK_WEBHOOK_URL=""
export PAGERDUTY_API_KEY=""
EOF
    
    log "SUCCESS" "Configuración de ejemplo creada: $INSTALL_DIR/config.env.example"
}

# Configurar logrotate
setup_logrotate() {
    log "INFO" "Configurando rotación de logs..."
    
    cat > /etc/logrotate.d/health-checks << 'EOF'
/var/log/health-checks/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 root root
    postrotate
        systemctl reload health-checks > /dev/null 2>&1 || true
    endscript
}

/usr/local/bin/health-checks/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 root root
}
EOF
    
    log "SUCCESS" "Logrotate configurado"
}

# Crear archivo de servicio systemd (opcional)
create_systemd_service() {
    log "INFO" "Creando servicio systemd..."
    
    cat > /etc/systemd/system/health-checks.service << 'EOF'
[Unit]
Description=Health Checks Monitoring Service
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/health-checks/generate-health-report.sh
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    log "SUCCESS" "Servicio systemd creado: health-checks.service"
}

# Ejecutar verificación inicial
run_initial_check() {
    log "INFO" "Ejecutando verificación inicial..."
    
    cd "$INSTALL_DIR"
    
    # Hacer ejecutables los scripts
    chmod +x *.sh
    
    # Ejecutar health check básico
    if ./health-check.sh > /tmp/initial-health-check.log 2>&1; then
        log "SUCCESS" "Verificación inicial: OK"
    else
        log "WARN" "Verificación inicial: Con advertencias (revisa log)"
        tail -20 /tmp/initial-health-check.log | tee -a "$LOG_FILE"
    fi
}

# Mostrar resumen final
show_summary() {
    log "INFO" "════════════════════════════════════════════════"
    log "INFO" "           INSTALACIÓN COMPLETADA"
    log "INFO" "════════════════════════════════════════════════"
    echo ""
    log "SUCCESS" "Sistema de Health Checks instalado exitosamente"
    echo ""
    log "INFO" "Directorio de instalación: $INSTALL_DIR"
    log "INFO" "Documentación: $INSTALL_DIR/README.md"
    log "INFO" "Log de instalación: $LOG_FILE"
    echo ""
    log "INFO" "Comandos disponibles:"
    echo "  • health-check: $INSTALL_DIR/health-check.sh"
    echo "  • db-check: $INSTALL_DIR/check-db-connections.sh"
    echo "  • rabbitmq-check: $INSTALL_DIR/check-rabbitmq.sh"
    echo "  • redis-check: $INSTALL_DIR/check-redis.sh"
    echo "  • health-report: $INSTALL_DIR/generate-health-report.sh"
    echo ""
    log "INFO" "Próximos pasos:"
    echo "  1. Configura las credenciales en config.env"
    echo "  2. Ejecuta: $INSTALL_DIR/setup-cron.sh"
    echo "  3. Personaliza las configuraciones según tu entorno"
    echo ""
    log "INFO" "Para obtener ayuda: cat $INSTALL_DIR/README.md"
}

# Función principal
main() {
    show_banner
    
    log "INFO" "Iniciando instalación del Sistema de Health Checks..."
    log "INFO" "Log de instalación: $LOG_FILE"
    echo ""
    
    # Verificaciones previas
    check_root
    check_system_dependencies
    
    # Instalación
    create_directory_structure
    install_scripts
    configure_services
    create_default_configs
    setup_logrotate
    create_systemd_service
    
    # Verificación inicial
    run_initial_check
    
    # Resumen
    show_summary
    
    log "SUCCESS" "¡Instalación completada!"
}

# Manejo de señales
trap 'log "ERROR" "Instalación interrumpida"; exit 130' INT TERM

# Ejecutar instalación
main "$@"
