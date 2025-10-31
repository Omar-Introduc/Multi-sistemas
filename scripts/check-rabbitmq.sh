#!/bin/bash

# Script para verificar RabbitMQ y estado de colas
# Autor: Sistema de Monitoreo
# Fecha: $(date +%Y-%m-%d)

set -e

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/logs/rabbitmq-check-$(date +%Y%m%d).log"
TIMEOUT=15
RABBITMQ_USER=${RABBITMQ_USER:-"admin"}
RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD:-"password"}
RABBITMQ_HOST=${RABBITMQ_HOST:-"localhost"}
RABBITMQ_PORT=${RABBITMQ_PORT:-"15672"}

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Verificar si RabbitMQ está corriendo
check_rabbitmq_service() {
    log "INFO" "Verificando servicio RabbitMQ..."
    
    if systemctl is-active --quiet rabbitmq-server; then
        log "SUCCESS" "Servicio RabbitMQ: ACTIVO"
    else
        log "ERROR" "Servicio RabbitMQ: INACTIVO"
        return 1
    fi
    
    # Verificar proceso
    if pgrep -x beam.smp >/dev/null; then
        log "SUCCESS" "Proceso Erlang VM: CORRIENDO"
    else
        log "ERROR" "Proceso Erlang VM: NO CORRIENDO"
        return 1
    fi
    
    return 0
}

# Verificar puertos de RabbitMQ
check_rabbitmq_ports() {
    log "INFO" "Verificando puertos RabbitMQ..."
    
    # Puerto AMQP (5672)
    if timeout 5 bash -c "echo >/dev/tcp/$RABBITMQ_HOST/5672" 2>/dev/null; then
        log "SUCCESS" "Puerto AMQP (5672): ACCESIBLE"
    else
        log "ERROR" "Puerto AMQP (5672): NO ACCESIBLE"
        return 1
    fi
    
    # Puerto de gestión (15672)
    if timeout 5 bash -c "echo >/dev/tcp/$RABBITMQ_HOST/15672" 2>/dev/null; then
        log "SUCCESS" "Puerto de gestión (15672): ACCESIBLE"
    else
        log "WARN" "Puerto de gestión (15672): NO ACCESIBLE"
    fi
    
    return 0
}

# Verificar conectividad HTTP API
check_rabbitmq_api() {
    log "INFO" "Verificando API HTTP de RabbitMQ..."
    
    if ! command -v curl >/dev/null 2>&1; then
        log "WARN" "curl no encontrado - no se puede verificar API"
        return 1
    fi
    
    local api_url="http://$RABBITMQ_HOST:$RABBITMQ_PORT/api/overview"
    local auth="$RABBITMQ_USER:$RABBITMQ_PASSWORD"
    
    local response
    response=$(curl -s -u "$auth" --max-time $TIMEOUT "$api_url" 2>&1)
    
    if [ $? -eq 0 ]; then
        if echo "$response" | grep -q "RabbitMQ version"; then
            log "SUCCESS" "API HTTP: ACCESIBLE"
            
            # Extraer versión y estadísticas
            local version=$(echo "$response" | grep -o '"RabbitMQ version":"[^"]*"' | cut -d'"' -f4)
            local erlang_version=$(echo "$response" | grep -o '"Erlang version":"[^"]*"' | cut -d'"' -f4)
            local listeners=$(echo "$response" | grep -o '"listeners":\[[^]]*\]' | grep -o '"port":[0-9]*' | wc -l)
            
            log "INFO" "RabbitMQ versión: $version | Erlang: $erlang_version | Listeners: $listeners"
            return 0
        else
            log "ERROR" "API HTTP: Respuesta inesperada"
            return 1
        fi
    else
        log "ERROR" "API HTTP: Error de conexión - $response"
        return 1
    fi
}

# Verificar colas y sus métricas
check_rabbitmq_queues() {
    log "INFO" "Verificando colas de RabbitMQ..."
    
    if ! command -v curl >/dev/null 2>&1; then
        log "WARN" "curl no encontrado - saltando verificación de colas"
        return 1
    fi
    
    local api_url="http://$RABBITMQ_HOST:$RABBITMQ_PORT/api/queues"
    local auth="$RABBITMQ_USER:$RABBITMQ_PASSWORD"
    
    local response
    response=$(curl -s -u "$auth" --max-time $TIMEOUT "$api_url" 2>&1)
    
    if [ $? -ne 0 ]; then
        log "ERROR" "Error al obtener información de colas"
        return 1
    fi
    
    # Contar total de colas
    local total_queues=$(echo "$response" | grep -o '"name":"[^"]*"' | wc -l)
    log "INFO" "Total de colas: $total_queues"
    
    # Verificar cola con más mensajes (problemas potenciales)
    local high_queue=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data:
        max_queue = max(data, key=lambda x: x.get('messages', 0))
        print(f\"{max_queue['name']}:{max_queue['messages']}\")
except:
    print('error')
" 2>/dev/null)
    
    if [ "$high_queue" != "error" ] && [ -n "$high_queue" ]; then
        local queue_name=$(echo "$high_queue" | cut -d':' -f1)
        local messages=$(echo "$high_queue" | cut -d':' -f2)
        
        log "INFO" "Cola con más mensajes: $queue_name ($messages mensajes)"
        
        # Alerta si hay demasiados mensajes
        if [ "$messages" -gt 1000 ]; then
            log "WARN" "Cola $queue_name tiene muchos mensajes pendientes ($messages)"
        fi
    fi
    
    # Verificar colas en estado problemático
    local problematic_queues=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    problematic = []
    for queue in data:
        messages = queue.get('messages', 0)
        durable = queue.get('durable', True)
        state = queue.get('state', 'running')
        
        # Criterios de alerta
        if messages > 500:
            problematic.append(f\"{queue['name']}:{messages}msgs (alta)\")
        elif messages > 100 and messages > 0:
            problematic.append(f\"{queue['name']}:{messages}msgs (media)\")
        elif state != 'running':
            problematic.append(f\"{queue['name']}:{state}\")
    
    if problematic:
        print('\n'.join(problematic))
except:
    print('')
" 2>/dev/null)
    
    if [ -n "$problematic_queues" ]; then
        log "WARN" "Colas con problemas detectadas:"
        while IFS= read -r queue; do
            log "WARN" "  - $queue"
        done <<< "$problematic_queues"
    else
        log "SUCCESS" "Todas las colas en estado normal"
    fi
    
    return 0
}

# Verificar exchanges
check_rabbitmq_exchanges() {
    log "INFO" "Verificando exchanges de RabbitMQ..."
    
    if ! command -v curl >/dev/null 2>&1; then
        return 0
    fi
    
    local api_url="http://$RABBITMQ_HOST:$RABBITMQ_PORT/api/exchanges"
    local auth="$RABBITMQ_USER:$RABBITMQ_PASSWORD"
    
    local response
    response=$(curl -s -u "$auth" --max-time $TIMEOUT "$api_url" 2>&1)
    
    if [ $? -eq 0 ]; then
        local total_exchanges=$(echo "$response" | grep -o '"name":"[^"]*"' | wc -l)
        log "INFO" "Total de exchanges: $total_exchanges"
        
        # Verificar exchanges en uso
        local used_exchanges=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    used = sum(1 for x in data if x.get('message_stats', {}).get('publish_in', 0) > 0)
    print(used)
except:
    print(0)
" 2>/dev/null)
        
        log "INFO" "Exchanges activos: $used_exchanges"
        log "SUCCESS" "Exchanges verificados correctamente"
    fi
    
    return 0
}

# Verificar conexiones y canales
check_rabbitmq_connections() {
    log "INFO" "Verificando conexiones de RabbitMQ..."
    
    if ! command -v curl >/dev/null 2>&1; then
        return 0
    fi
    
    local api_url="http://$RABBITMQ_HOST:$RABBITMQ_PORT/api/connections"
    local auth="$RABBITMQ_USER:$RABBITMQ_PASSWORD"
    
    local response
    response=$(curl -s -u "$auth" --max-time $TIMEOUT "$api_url" 2>&1)
    
    if [ $? -eq 0 ]; then
        local total_connections=$(echo "$response" | grep -o '"user":"[^"]*"' | wc -l)
        log "INFO" "Total de conexiones: $total_connections"
        
        # Verificar conexiones創業
        local创业_connections=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
   创业 = sum(1 for x in data if x.get('state') == '创业')
    print(创业)
except:
    print(0)
" 2>/dev/null)
        
        if [ "$創業_connections" -gt 0 ]; then
            log "WARN" "Conexiones en estado創業: $創業_connections"
        else
            log "SUCCESS" "Todas las conexiones estables"
        fi
        
        # Verificar número de canales
        local total_channels=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    channels = sum(x.get('channels', 0) for x in data)
    print(channels)
except:
    print(0)
" 2>/dev/null)
        
        log "INFO" "Total de canales: $total_channels"
    fi
    
    return 0
}

# Verificar estadísticas de performance
check_rabbitmq_performance() {
    log "INFO" "Verificando performance de RabbitMQ..."
    
    if ! command -v curl >/dev/null 2>&1; then
        return 0
    fi
    
    local api_url="http://$RABBITMQ_HOST:$RABBITMQ_PORT/api/overview"
    local auth="$RABBITMQ_USER:$RABBITMQ_PASSWORD"
    
    local response
    response=$(curl -s -u "$auth" --max-time $TIMEOUT "$api_url" 2>&1)
    
    if [ $? -eq 0 ]; then
        # Extraer estadísticas de mensajes
        local msg_stats=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    publish_stats = data.get('message_stats', {})
    print(f\"publish:{publish_stats.get('publish', 0)},deliver_get:{publish_stats.get('deliver_get', 0)},ack:{publish_stats.get('ack', 0)}\")
except:
    print('error')
" 2>/dev/null)
        
        if [ "$msg_stats" != "error" ] && [ -n "$msg_stats" ]; then
            log "INFO" "Estadísticas de mensajes: $msg_stats"
        fi
        
        # Verificar memoria
        local memory_usage=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    memory = data.get('memory', {})
    total = memory.get('total', 0)
    print(total)
except:
    print(0)
" 2>/dev/null)
        
        if [ "$memory_usage" -gt 0 ]; then
            local memory_mb=$((memory_usage / 1024 / 1024))
            log "INFO" "Uso de memoria: ${memory_mb}MB"
            
            # Alerta si uso de memoria es muy alto (>80% de RAM disponible)
            local total_ram_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
            local memory_percent=$((memory_usage / 1024 / total_ram_kb * 100))
            
            if [ "$memory_percent" -gt 80 ]; then
                log "WARN" "Alto uso de memoria: ${memory_percent}%"
            fi
        fi
    fi
    
    return 0
}

# Verificar logs de RabbitMQ
check_rabbitmq_logs() {
    log "INFO" "Verificando logs de RabbitMQ..."
    
    local log_files=(
        "/var/log/rabbitmq/rabbit@*.log"
        "/var/log/rabbitmq/rabbit*.log"
    )
    
    local total_errors=0
    
    for log_pattern in "${log_files[@]}"; do
        for log_file in $log_pattern; do
            if [ -f "$log_file" ]; then
                # Verificar errores recientes (últimos 5 minutos)
                local errors=$(find "$log_file" -newermt "5 minutes ago" -exec grep -i "error\|exception\|failed\|crash" {} \; 2>/dev/null | wc -l)
                
                if [ "$errors" -gt 0 ]; then
                    log "WARN" "Errores en $log_file (últimos 5 min): $errors"
                    ((total_errors += errors))
                fi
            fi
        done
    done
    
    if [ $total_errors -eq 0 ]; then
        log "SUCCESS" "No se encontraron errores críticos en logs recientes"
    fi
    
    return 0
}

# Verificar configuración
check_rabbitmq_config() {
    log "INFO" "Verificando configuración de RabbitMQ..."
    
    local config_files=(
        "/etc/rabbitmq/rabbitmq.conf"
        "/etc/rabbitmq/advanced.config"
        "/etc/rabbitmq/enabled_plugins"
    )
    
    for config_file in "${config_files[@]}"; do
        if [ -f "$config_file" ]; then
            if [ -r "$config_file" ]; then
                log "SUCCESS" "Configuración legible: $(basename "$config_file")"
            else
                log "ERROR" "Configuración no legible: $(basename "$config_file")"
                return 1
            fi
        fi
    done
    
    # Verificar límites de descriptores de archivos
    local max_fds=$(rabbitmqctl environment 2>/dev/null | grep "RABBITMQ_MAX_FILE_DESCRIPTORS" | awk '{print $3}')
    if [ -n "$max_fds" ]; then
        log "INFO" "Límite de file descriptors: $max_fds"
    fi
    
    return 0
}

# Función principal
run_rabbitmq_checks() {
    local overall_status=0
    
    log "INFO" "=== INICIANDO VERIFICACIÓN RABBITMQ $(date) ==="
    
    # Verificaciones básicas
    check_rabbitmq_service || ((overall_status++))
    check_rabbitmq_ports || ((overall_status++))
    check_rabbitmq_api || ((overall_status++))
    
    # Verificaciones de colas y exchanges
    check_rabbitmq_queues || ((overall_status++))
    check_rabbitmq_exchanges
    check_rabbitmq_connections
    check_rabbitmq_performance
    
    # Verificaciones adicionales
    check_rabbitmq_logs
    check_rabbitmq_config
    
    # Reportar estado
    if [ $overall_status -eq 0 ]; then
        log "SUCCESS" "=== VERIFICACIÓN RABBITMQ COMPLETADA: SISTEMA SALUDABLE ==="
        exit 0
    else
        log "ERROR" "=== VERIFICACIÓN RABBITMQ COMPLETADA: $overall_status PROBLEMAS ENCONTRADOS ==="
        exit 1
    fi
}

# Manejo de señales
trap 'log "ERROR" "RabbitMQ check interrumpido"; exit 130' INT TERM

# Verificar dependencias
command -v rabbitmqctl >/dev/null 2>&1 || { log "ERROR" "rabbitmqctl no encontrado"; exit 127; }

# Ejecutar verificación si el script es llamado directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_rabbitmq_checks
fi
