#!/bin/bash

# Docker entrypoint script para health checks
# Configura el entorno y ejecuta los health checks

set -e

SCRIPT_DIR="/app"
LOG_DIR="$SCRIPT_DIR/logs"
REPORT_DIR="$SCRIPT_DIR/reports"

# Función para logging en docker
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >&2
}

# Crear directorios necesarios
mkdir -p "$LOG_DIR" "$REPORT_DIR"

# Cargar configuración si existe
if [ -f "$SCRIPT_DIR/config.env" ]; then
    log "Cargando configuración desde config.env..."
    source "$SCRIPT_DIR/config.env"
elif [ -f "$SCRIPT_DIR/config/config.env" ]; then
    log "Cargando configuración desde config/config.env..."
    source "$SCRIPT_DIR/config/config.env"
else
    log "ADVERTENCIA: No se encontró archivo de configuración"
fi

# Verificar dependencias en el contenedor
log "Verificando dependencias del contenedor..."

required_commands=("psql" "mysql" "redis-cli" "rabbitmqctl" "curl" "bc")
missing_commands=()

for cmd in "${required_commands[@]}"; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        missing_commands+=("$cmd")
    fi
done

if [ ${#missing_commands[@]} -gt 0 ]; then
    log "ERROR: Comandos faltantes: ${missing_commands[*]}"
    log "Instala las dependencias antes de ejecutar health checks"
    exit 1
fi

# Configurar timezone
if [ -n "$TZ" ]; then
    ln -sf "/usr/share/zoneinfo/$TZ" /etc/localtime 2>/dev/null || true
fi

# Función para ejecutar health check
run_health_check() {
    log "Ejecutando health check..."
    
    cd "$SCRIPT_DIR"
    
    case "$1" in
        "health")
            exec ./health-check.sh
            ;;
        "db")
            exec ./check-db-connections.sh
            ;;
        "rabbitmq")
            exec ./check-rabbitmq.sh
            ;;
        "redis")
            exec ./check-redis.sh
            ;;
        "report")
            exec ./generate-health-report.sh
            ;;
        "all")
            log "Ejecutando todos los health checks..."
            
            # Ejecutar en secuencia
            ./health-check.sh || log "Health check general falló"
            ./check-db-connections.sh || log "DB check falló"
            ./check-rabbitmq.sh || log "RabbitMQ check falló"
            ./check-redis.sh || log "Redis check falló"
            ./generate-health-report.sh || log "Reporte falló"
            
            log "Todos los health checks completados"
            ;;
        *)
            log "Uso: $0 [health|db|rabbitmq|redis|report|all]"
            log "Si no se especifica argumento, ejecuta health check general"
            exec ./health-check.sh
            ;;
    esac
}

# Configurar cron si está habilitado
if [ "$ENABLE_CRON" = "true" ]; then
    log "Configurando cron para health checks automáticos..."
    
    # Crear crontab dinámico
    cat > /tmp/health-checks-cron << EOF
# Health checks automáticos (Docker)
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

*/${CRON_HEALTH_INTERVAL:-5} * * * * /bin/bash $SCRIPT_DIR/health-check.sh >> $LOG_DIR/cron-health.log 2>&1
*/${CRON_DB_INTERVAL:-15} * * * * /bin/bash $SCRIPT_DIR/check-db-connections.sh >> $LOG_DIR/cron-db.log 2>&1
*/${CRON_RABBITMQ_INTERVAL:-10} * * * * /bin/bash $SCRIPT_DIR/check-rabbitmq.sh >> $LOG_DIR/cron-rabbitmq.log 2>&1
*/${CRON_REDIS_INTERVAL:-10} * * * * /bin/bash $SCRIPT_DIR/check-redis.sh >> $LOG_DIR/cron-redis.log 2>&1
0 * * * * /bin/bash $SCRIPT_DIR/generate-health-report.sh >> $LOG_DIR/cron-report.log 2>&1

EOF
    
    crontab /tmp/health-checks-cron
    
    # Iniciar cron en background
    log "Iniciando servicio cron..."
    cron
fi

# Configurar señales para shutdown graceful
shutdown() {
    log "Recibida señal de shutdown, cerrando gracefully..."
    pkill -f health-check || true
    exit 0
}

trap shutdown SIGTERM SIGINT

# Mostrar información del contenedor
log "=== HEALTH CHECKS DOCKER CONTAINER ==="
log "Directorio de scripts: $SCRIPT_DIR"
log "Directorio de logs: $LOG_DIR"
log "Directorio de reportes: $REPORT_DIR"
log "Ambiente: ${ENVIRONMENT:-unknown}"
log "Timezone: $(cat /etc/timezone 2>/dev/null || echo 'unknown')"
log "========================================"

# Ejecutar modo interactivo si no hay argumentos
if [ $# -eq 0 ]; then
    log "Sin argumentos, ejecutando health check general..."
    run_health_check "health"
else
    run_health_check "$1"
fi
