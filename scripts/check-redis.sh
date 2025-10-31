#!/bin/bash

# Script para verificar conectividad y estado de Redis
# Autor: Sistema de Monitoreo
# Fecha: $(date +%Y-%m-%d)

set -e

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/logs/redis-check-$(date +%Y%m%d).log"
TIMEOUT=10
REDIS_HOST=${REDIS_HOST:-"localhost"}
REDIS_PORT=${REDIS_PORT:-"6379"}
REDIS_PASSWORD=${REDIS_PASSWORD:-""}

# Colores para output
RED='\033[0;31m'
GREEN='\033[033[0;32m'
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

# Verificar si Redis está corriendo
check_redis_service() {
    log "INFO" "Verificando servicio Redis..."
    
    if systemctl is-active --quiet redis-server || systemctl is-active --quiet redis; then
        log "SUCCESS" "Servicio Redis: ACTIVO"
    else
        log "ERROR" "Servicio Redis: INACTIVO"
        return 1
    fi
    
    # Verificar proceso
    if pgrep -x redis-server >/dev/null; then
        log "SUCCESS" "Proceso redis-server: CORRIENDO"
    else
        log "ERROR" "Proceso redis-server: NO CORRIENDO"
        return 1
    fi
    
    return 0
}

# Verificar puerto de Redis
check_redis_port() {
    log "INFO" "Verificando puerto Redis..."
    
    if timeout 5 bash -c "echo >/dev/tcp/$REDIS_HOST/$REDIS_PORT" 2>/dev/null; then
        log "SUCCESS" "Puerto Redis ($REDIS_PORT): ACCESIBLE"
    else
        log "ERROR" "Puerto Redis ($REDIS_PORT): NO ACCESIBLE"
        return 1
    fi
    
    return 0
}

# Función para ejecutar comandos Redis
redis_cmd() {
    local cmd="$1"
    
    if [ -n "$REDIS_PASSWORD" ]; then
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" --raw "$cmd" 2>/dev/null
    else
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" --raw "$cmd" 2>/dev/null
    fi
}

# Verificar conectividad básica
check_redis_connectivity() {
    log "INFO" "Verificando conectividad básica de Redis..."
    
    if ! command -v redis-cli >/dev/null 2>&1; then
        log "ERROR" "redis-cli no encontrado"
        return 1
    fi
    
    # Probar conexión PING
    local ping_result
    ping_result=$(redis_cmd "PING")
    
    if [ "$ping_result" = "PONG" ]; then
        log "SUCCESS" "Conexión Redis: PING/PONG OK"
    else
        log "ERROR" "Conexión Redis: FALLO - $ping_result"
        return 1
    fi
    
    # Verificar autenticación si es necesario
    if [ -n "$REDIS_PASSWORD" ]; then
        local auth_test
        auth_test=$(redis_cmd "SELECT 0")
        
        if echo "$auth_test" | grep -q "NOAUTH"; then
            log "ERROR" "Redis: Error de autenticación"
            return 1
        else
            log "SUCCESS" "Redis: Autenticación OK"
        fi
    fi
    
    return 0
}

# Verificar información del servidor
check_redis_info() {
    log "INFO" "Verificando información del servidor Redis..."
    
    local redis_version
    redis_version=$(redis_cmd "INFO server" | grep "redis_version" | cut -d':' -f2 | tr -d '\r')
    
    local uptime_seconds
    uptime_seconds=$(redis_cmd "INFO server" | grep "uptime_in_seconds" | cut -d':' -f2 | tr -d '\r')
    
    local uptime_days=$((uptime_seconds / 86400))
    
    local process_id
    process_id=$(redis_cmd "INFO server" | grep "process_id" | cut -d':' -f2 | tr -d '\r')
    
    local os_info
    os_info=$(redis_cmd "INFO server" | grep "os" | cut -d':' -f2 | tr -d '\r')
    
    log "INFO" "Redis versión: $redis_version | Uptime: ${uptime_days}d | PID: $process_id | OS: $os_info"
    
    # Verificar uptime crítico
    if [ "$uptime_seconds" -lt 300 ]; then
        log "WARN" "Redis recién iniciado (${uptime_seconds}s)"
    else
        log "SUCCESS" "Redis estable (${uptime_days}d)"
    fi
    
    return 0
}

# Verificar uso de memoria
check_redis_memory() {
    log "INFO" "Verificando uso de memoria Redis..."
    
    local used_memory
    used_memory=$(redis_cmd "INFO memory" | grep "used_memory" | cut -d':' -f2 | tr -d '\r')
    
    local used_memory_human
    used_memory_human=$(redis_cmd "INFO memory" | grep "used_memory_human" | cut -d':' -f2 | tr -d '\r')
    
    local used_memory_rss
    used_memory_rss=$(redis_cmd "INFO memory" | grep "used_memory_rss" | cut -d':' -f2 | tr -d '\r')
    
    local maxmemory
    maxmemory=$(redis_cmd "INFO memory" | grep "maxmemory" | cut -d':' -f2 | tr -d '\r')
    
    local mem_fragmentation_ratio
    mem_fragmentation_ratio=$(redis_cmd "INFO memory" | grep "mem_fragmentation_ratio" | cut -d':' -f2 | tr -d '\r')
    
    # Convertir bytes a MB para uso de memoria
    local used_memory_mb=$((used_memory / 1024 / 1024))
    local used_memory_rss_mb=$((used_memory_rss / 1024 / 1024))
    
    log "INFO" "Memoria usada: ${used_memory_human} (RSS: ${used_memory_rss_mb}MB)"
    
    if [ "$maxmemory" -gt 0 ]; then
        local maxmemory_mb=$((maxmemory / 1024 / 1024))
        local memory_percent=$((used_memory * 100 / maxmemory))
        log "INFO" "Límite de memoria: ${maxmemory_mb}MB | Uso: ${memory_percent}%"
        
        # Alertas por uso excesivo
        if [ "$memory_percent" -gt 90 ]; then
            log "ERROR" "Redis: Uso crítico de memoria (${memory_percent}%)"
            return 1
        elif [ "$memory_percent" -gt 80 ]; then
            log "WARN" "Redis: Alto uso de memoria (${memory_percent}%)"
        fi
    fi
    
    # Verificar fragmentación de memoria
    local fragmentation_float=$(echo "$mem_fragmentation_ratio" | head -c 6)
    if (( $(echo "$fragmentation_float > 1.5" | bc -l) )); then
        log "WARN" "Redis: Alta fragmentación de memoria (${fragmentation_float})"
    elif (( $(echo "$fragmentation_float < 1.0" | bc -l) )); then
        log "WARN" "Redis: Fragmentación inusual (${fragmentation_float})"
    fi
    
    return 0
}

# Verificar conexiones y clientes
check_redis_clients() {
    log "INFO" "Verificando clientes conectados..."
    
    local connected_clients
    connected_clients=$(redis_cmd "INFO clients" | grep "connected_clients" | cut -d':' -f2 | tr -d '\r')
    
    local client_recent_max_input_buffer
    client_recent_max_input_buffer=$(redis_cmd "INFO clients" | grep "client_recent_max_input_buffer" | cut -d':' -f2 | tr -d '\r')
    
    local client_recent_max_output_buffer
    client_recent_max_output_buffer=$(redis_cmd "INFO clients" | grep "client_recent_max_output_buffer" | cut -d':' -f2 | tr -d '\r')
    
    log "INFO" "Clientes conectados: $connected_clients"
    
    # Alertas por demasiados clientes
    if [ "$connected_clients" -gt 100 ]; then
        log "WARN" "Redis: Muchos clientes conectados ($connected_clients)"
    elif [ "$connected_clients" -eq 0 ]; then
        log "WARN" "Redis: Sin clientes conectados (inusual)"
    else
        log "SUCCESS" "Número de clientes normal"
    fi
    
    # Verificar buffers de clientes
    if [ "$client_recent_max_input_buffer" -gt 2000000 ]; then
        log "WARN" "Redis: Buffer de entrada alto (${client_recent_max_input_buffer} bytes)"
    fi
    
    if [ "$client_recent_max_output_buffer" -gt 2000000 ]; then
        log "WARN" "Redis: Buffer de salida alto (${client_recent_max_output_buffer} bytes)"
    fi
    
    return 0
}

# Verificar estadísticas de comandos
check_redis_commands() {
    log "INFO" "Verificando estadísticas de comandos..."
    
    local total_commands_processed
    total_commands_processed=$(redis_cmd "INFO stats" | grep "total_commands_processed" | cut -d':' -f2 | tr -d '\r')
    
    local instantaneous_ops_per_sec
    instantaneous_ops_per_sec=$(redis_cmd "INFO stats" | grep "instantaneous_ops_per_sec" | cut -d':' -f2 | tr -d '\r')
    
    local keyspace_hits
    keyspace_hits=$(redis_cmd "INFO stats" | grep "keyspace_hits" | cut -d':' -f2 | tr -d '\r')
    
    local keyspace_misses
    keyspace_misses=$(redis_cmd "INFO stats" | grep "keyspace_misses" | cut -d':' -f2 | tr -d '\r')
    
    log "INFO" "Comandos procesados: $total_commands_processed"
    log "INFO" "Operaciones/segundo: $instantaneous_ops_per_sec"
    
    # Calcular ratio de hits
    local total_requests=$((keyspace_hits + keyspace_misses))
    if [ "$total_requests" -gt 0 ]; then
        local hit_ratio=$((keyspace_hits * 100 / total_requests))
        log "INFO" "Hit ratio: ${hit_ratio}% ($keyspace_hits/$total_requests)"
        
        if [ "$hit_ratio" -lt 70 ]; then
            log "WARN" "Redis: Bajo hit ratio (${hit_ratio}%) - posible problema de cache"
        fi
    fi
    
    return 0
}

# Verificar persistencia
check_redis_persistence() {
    log "INFO" "Verificando persistencia de Redis..."
    
    local rdb_last_save_time
    rdb_last_save_time=$(redis_cmd "INFO persistence" | grep "rdb_last_save_time" | cut -d':' -f2 | tr -d '\r')
    
    local rdb_last_bgsave_status
    rdb_last_bgsave_status=$(redis_cmd "INFO persistence" | grep "rdb_last_bgsave_status" | cut -d':' -f2 | tr -d '\r')
    
    local rdb_changes_since_last_save
    rdb_changes_since_last_save=$(redis_cmd "INFO persistence" | grep "rdb_changes_since_last_save" | cut -d':' -f2 | tr -d '\r')
    
    # Calcular tiempo desde último save
    local current_time=$(date +%s)
    local time_since_save=$((current_time - rdb_last_save_time))
    local time_since_save_min=$((time_since_save / 60))
    
    log "INFO" "Último RDB save: hace ${time_since_save_min}min | Status: $rdb_last_bgsave_status"
    log "INFO" "Cambios desde último save: $rdb_changes_since_last_save"
    
    # Verificar si el último save fue exitoso
    if [ "$rdb_last_bgsave_status" != "ok" ]; then
        log "ERROR" "Redis: Último RDB save falló"
        return 1
    fi
    
    # Verificar tiempo excesivo sin save
    if [ "$time_since_save" -gt 3600 ]; then
        log "WARN" "Redis: Más de 1 hora sin RDB save"
    fi
    
    # Verificar muchas transacciones pendientes
    if [ "$rdb_changes_since_last_save" -gt 100000 ]; then
        log "WARN" "Redis: Muchas transacciones pendientes ($rdb_changes_since_last_save)"
    fi
    
    return 0
}

# Verificar base de datos y claves
check_redis_databases() {
    log "INFO" "Verificando bases de datos Redis..."
    
    # Verificar cada base de datos
    for db in 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
        local db_keys
        db_keys=$(redis_cmd "SELECT $db; DBSIZE" 2>/dev/null | tail -1)
        
        if [ "$db_keys" -gt 0 ]; then
            log "INFO" "DB $db: $db_keys claves"
            
            # Verificar keys con TTL
            local keys_with_ttl
            keys_with_ttl=$(redis_cmd "SELECT $db; INFO keyspace" | grep "db$db" | grep -o "keys=[0-9]*" | cut -d'=' -f2)
            
            if [ "$keys_with_ttl" -gt 0 ]; then
                log "INFO" "DB $db: $keys_with_ttl claves con TTL"
            fi
        fi
    done
    
    return 0
}

# Verificar replicación (si está configurada)
check_redis_replication() {
    log "INFO" "Verificando replicación Redis..."
    
    local role
    role=$(redis_cmd "INFO replication" | grep "^role:" | cut -d':' -f2 | tr -d '\r')
    
    log "INFO" "Rol Redis: $role"
    
    if [ "$role" = "master" ]; then
        local connected_slaves
        connected_slaves=$(redis_cmd "INFO replication" | grep "connected_slaves" | cut -d':' -f2 | tr -d '\r')
        
        log "INFO" "Slaves conectados: $connected_slaves"
        
        if [ "$connected_slaves" -gt 0 ]; then
            # Verificar estado de cada slave
            redis_cmd "INFO replication" | grep "slave" | while read -r line; do
                if [[ $line == *"master_last_io_seconds_ago"* ]]; then
                    log "INFO" "Slave: $line"
                fi
            done
        fi
    elif [ "$role" = "slave" ]; then
        local master_host
        master_host=$(redis_cmd "INFO replication" | grep "master_host" | cut -d':' -f2 | tr -d '\r')
        
        local master_link_status
        master_link_status=$(redis_cmd "INFO replication" | grep "master_link_status" | cut -d':' -f2 | tr -d '\r')
        
        log "INFO" "Master: $master_host | Status: $master_link_status"
        
        if [ "$master_link_status" != "up" ]; then
            log "ERROR" "Redis: Link con master caído"
            return 1
        fi
    fi
    
    return 0
}

# Verificar latencia
check_redis_latency() {
    log "INFO" "Verificando latencia Redis..."
    
    # Verificar latencia simple
    local start_time=$(date +%s%3N)
    redis_cmd "PING" > /dev/null
    local end_time=$(date +%s%3N)
    local latency=$((end_time - start_time))
    
    log "INFO" "Latencia PING: ${latency}ms"
    
    if [ "$latency" -gt 100 ]; then
        log "WARN" "Redis: Alta latencia (${latency}ms)"
    elif [ "$latency" -gt 50 ]; then
        log "INFO" "Redis: Latencia moderada (${latency}ms)"
    else
        log "SUCCESS" "Redis: Latencia baja (${latency}ms)"
    fi
    
    return 0
}

# Verificar logs de Redis
check_redis_logs() {
    log "INFO" "Verificando logs de Redis..."
    
    local log_files=(
        "/var/log/redis/redis-server.log"
        "/var/log/redis*.log"
        "/var/log/redis/redis.log"
    )
    
    local total_errors=0
    
    for log_pattern in "${log_files[@]}"; do
        for log_file in $log_pattern; do
            if [ -f "$log_file" ]; then
                # Verificar errores recientes (últimos 5 minutos)
                local errors=$(find "$log_file" -newermt "5 minutes ago" -exec grep -i "error\|warning\|exception\|failed" {} \; 2>/dev/null | wc -l)
                
                if [ "$errors" -gt 0 ]; then
                    log "WARN" "Errores/warnings en $log_file (últimos 5 min): $errors"
                    ((total_errors += errors))
                    
                    # Mostrar últimos errores
                    echo "$errors" | head -3 | while read -r line; do
                        log "WARN" "  - $line"
                    done
                fi
            fi
        done
    done
    
    if [ $total_errors -eq 0 ]; then
        log "SUCCESS" "No se encontraron errores/warnings en logs recientes"
    fi
    
    return 0
}

# Verificar configuración
check_redis_config() {
    log "INFO" "Verificando configuración Redis..."
    
    local config_file="/etc/redis/redis.conf"
    
    if [ -f "$config_file" ]; then
        if [ -r "$config_file" ]; then
            log "SUCCESS" "Configuración legible: $config_file"
        else
            log "ERROR" "Configuración no legible: $config_file"
            return 1
        fi
        
        # Verificar parámetros importantes
        local maxmemory=$(grep "^maxmemory" "$config_file" | awk '{print $2}')
        local save_config=$(grep "^save" "$config_file" | head -1)
        
        if [ -n "$maxmemory" ]; then
            log "INFO" "Configuración maxmemory: $maxmemory"
        fi
        
        if [ -n "$save_config" ]; then
            log "INFO" "Configuración de persistencia: $save_config"
        fi
    else
        log "WARN" "Archivo de configuración no encontrado: $config_file"
    fi
    
    return 0
}

# Función principal
run_redis_checks() {
    local overall_status=0
    
    log "INFO" "=== INICIANDO VERIFICACIÓN REDIS $(date) ==="
    
    # Verificaciones básicas
    check_redis_service || ((overall_status++))
    check_redis_port || ((overall_status++))
    check_redis_connectivity || ((overall_status++))
    
    # Verificaciones de rendimiento y uso
    check_redis_info
    check_redis_memory || ((overall_status++))
    check_redis_clients
    check_redis_commands
    check_redis_persistence || ((overall_status++))
    check_redis_latency
    check_redis_databases
    check_redis_replication
    
    # Verificaciones adicionales
    check_redis_logs || ((overall_status++))
    check_redis_config
    
    # Reportar estado
    if [ $overall_status -eq 0 ]; then
        log "SUCCESS" "=== VERIFICACIÓN REDIS COMPLETADA: SISTEMA SALUDABLE ==="
        exit 0
    else
        log "ERROR" "=== VERIFICACIÓN REDIS COMPLETADA: $overall_status PROBLEMAS ENCONTRADOS ==="
        exit 1
    fi
}

# Manejo de señales
trap 'log "ERROR" "Redis check interrumpido"; exit 130' INT TERM

# Verificar dependencias
command -v redis-cli >/dev/null 2>&1 || { log "ERROR" "redis-cli no encontrado"; exit 127; }

# Ejecutar verificación si el script es llamado directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_redis_checks
fi
