#!/bin/bash

# Script principal de health check
# Verifica el estado de todos los servicios críticos
# Autor: Sistema de Monitoreo
# Fecha: $(date +%Y-%m-%d)

set -e

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/logs/health-check-$(date +%Y%m%d).log"
ERROR_LOG="${SCRIPT_DIR}/logs/health-errors-$(date +%Y%m%d).log"
ALERT_THRESHOLD=3
TIMEOUT=30

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Crear directorio de logs si no existe
mkdir -p "${SCRIPT_DIR}/logs"

# Función para logging
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
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
            echo -e "${GREEN}[OK]${NC} $message"
            ;;
    esac
}

# Función para verificar si un puerto está abierto
check_port() {
    local host=$1
    local port=$2
    local timeout=${3:-5}
    
    if timeout $timeout bash -c "echo >/dev/tcp/$host/$port" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Función para verificar uso de recursos del sistema
check_system_resources() {
    log "INFO" "Verificando recursos del sistema..."
    
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    local mem_usage=$(free | grep Mem | awk '{printf("%.2f"), $3/$2 * 100.0}')
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    log "INFO" "CPU: ${cpu_usage}% | Memoria: ${mem_usage}% | Disco: ${disk_usage}%"
    
    # Alertas por uso excesivo
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        log "WARN" "Alto uso de CPU: ${cpu_usage}%"
        return 1
    fi
    
    if (( $(echo "$mem_usage > 85" | bc -l) )); then
        log "WARN" "Alto uso de memoria: ${mem_usage}%"
        return 1
    fi
    
    if [ "$disk_usage" -gt 90 ]; then
        log "WARN" "Alto uso de disco: ${disk_usage}%"
        return 1
    fi
    
    log "SUCCESS" "Recursos del sistema dentro de parámetros normales"
    return 0
}

# Función para verificar servicios críticos
check_critical_services() {
    log "INFO" "Verificando servicios críticos..."
    
    local services=("nginx" "postgresql" "redis" "rabbitmq-server")
    local failed_services=()
    
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            log "SUCCESS" "Servicio $service: ACTIVO"
        else
            log "ERROR" "Servicio $service: INACTIVO"
            failed_services+=("$service")
        fi
    done
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        log "ERROR" "Servicios fallidos: ${failed_services[*]}"
        return 1
    fi
    
    return 0
}

# Función para verificar conectividad de red
check_network_connectivity() {
    log "INFO" "Verificando conectividad de red..."
    
    local endpoints=("8.8.8.8" "1.1.1.1")
    
    for endpoint in "${endpoints[@]}"; do
        if ping -c 1 -W 3 "$endpoint" >/dev/null 2>&1; then
            log "SUCCESS" "Conectividad a $endpoint: OK"
        else
            log "ERROR" "Conectividad a $endpoint: FALLO"
            return 1
        fi
    done
    
    return 0
}

# Función para verificar archivos de log críticos
check_log_files() {
    log "INFO" "Verificando archivos de log críticos..."
    
    local log_paths=(
        "/var/log/nginx/error.log"
        "/var/log/postgresql/postgresql-*.log"
        "/var/log/redis/redis-server.log"
        "/var/log/rabbitmq/rabbit@*.log"
    )
    
    local recent_errors=0
    
    for log_pattern in "${log_paths[@]}"; do
        for log_file in $log_pattern; do
            if [ -f "$log_file" ]; then
                # Verificar errores en los últimos 5 minutos
                local errors=$(find "$log_file" -newermt "5 minutes ago" -exec grep -i "error\|exception\|failed" {} \; 2>/dev/null | wc -l)
                if [ "$errors" -gt 10 ]; then
                    log "WARN" "Múltiples errores recientes en $log_file: $errors"
                    ((recent_errors++))
                fi
            fi
        done
    done
    
    if [ $recent_errors -gt 0 ]; then
        log "WARN" "Se encontraron errores en $recent_errors archivos de log"
        return 1
    fi
    
    log "SUCCESS" "No se detectaron errores críticos en logs recientes"
    return 0
}

# Función para verificar configuraciones críticas
check_configurations() {
    log "INFO" "Verificando configuraciones críticas..."
    
    local configs=(
        "/etc/nginx/nginx.conf"
        "/etc/postgresql/postgresql.conf"
        "/etc/redis/redis.conf"
        "/etc/rabbitmq/rabbitmq.conf"
    )
    
    for config in "${configs[@]}"; do
        if [ -f "$config" ]; then
            if [ -r "$config" ]; then
                log "SUCCESS" "Configuración $config: legible"
            else
                log "ERROR" "Configuración $config: no legible"
                return 1
            fi
        else
            log "WARN" "Configuración $config: no encontrada"
        fi
    done
    
    return 0
}

# Función para generar alerta
generate_alert() {
    local severity=$1
    local message=$2
    
    log "ERROR" "ALERTA [$severity]: $message"
    
    # Aquí se pueden agregar integraciones con sistemas de alertas
    # Por ejemplo: Slack, email, PagerDuty, etc.
    
    # Enviar alerta por email (opcional)
    if command -v mail >/dev/null 2>&1; then
        echo "$message" | mail -s "ALERTA $severity - Health Check" admin@sistema.local 2>/dev/null || true
    fi
    
    # Escribir a archivo de alertas
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$severity] $message" >> "${SCRIPT_DIR}/logs/alerts.log"
}

# Función principal de verificación
run_health_checks() {
    local overall_status=0
    
    log "INFO" "=== INICIANDO HEALTH CHECK $(date) ==="
    
    # Ejecutar verificaciones
    check_system_resources || ((overall_status++))
    check_critical_services || ((overall_status++))
    check_network_connectivity || ((overall_status++))
    check_log_files || ((overall_status++))
    check_configurations || ((overall_status++))
    
    # Ejecutar verificaciones específicas de componentes
    if [ -f "${SCRIPT_DIR}/check-db-connections.sh" ]; then
        "${SCRIPT_DIR}/check-db-connections.sh" || ((overall_status++))
    fi
    
    if [ -f "${SCRIPT_DIR}/check-rabbitmq.sh" ]; then
        "${SCRIPT_DIR}/check-rabbitmq.sh" || ((overall_status++))
    fi
    
    if [ -f "${SCRIPT_DIR}/check-redis.sh" ]; then
        "${SCRIPT_DIR}/check-redis.sh" || ((overall_status++))
    fi
    
    # Reportar estado general
    if [ $overall_status -eq 0 ]; then
        log "SUCCESS" "=== HEALTH CHECK COMPLETADO: TODOS LOS SISTEMAS OPERATIVOS ==="
        exit 0
    elif [ $overall_status -lt $ALERT_THRESHOLD ]; then
        log "WARN" "=== HEALTH CHECK COMPLETADO: $overall_status ADVERTENCIAS ==="
        exit 1
    else
        generate_alert "CRÍTICO" "Health check fallido: $overall_status verificaciones fallaron"
        log "ERROR" "=== HEALTH CHECK COMPLETADO: SISTEMA EN ESTADO CRÍTICO ==="
        exit 2
    fi
}

# Manejo de señales
trap 'log "ERROR" "Health check interrumpido por señal"; exit 130' INT TERM

# Verificar dependencias
command -v systemctl >/dev/null 2>&1 || { log "ERROR" "systemctl no encontrado"; exit 127; }
command -v bc >/dev/null 2>&1 || { log "ERROR" "bc no encontrado - instalado para cálculos"; exit 127; }

# Ejecutar health check si el script es llamado directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_health_checks
fi
