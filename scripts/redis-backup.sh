#!/bin/bash

# =============================================================================
# SCRIPT DE BACKUP AUTOMÁTICO PARA REDIS
# Realiza backup del dataset de Redis con configuración de persistencia
# =============================================================================

set -euo pipefail

# Configuración
BACKUP_DIR="/backup"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASS="${REDIS_PASSWORD:-redispass123}"
RETENTION_DAYS=3
DUMP_FILE="dump.rdb"

# Función para logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$BACKUP_DIR/backup.log"
}

# Función para cleanup de backups antiguos
cleanup_old_backups() {
    log "Limpiando backups antiguos (retención: ${RETENTION_DAYS} días)"
    find "$BACKUP_DIR" -name "redis_backup_*.rdb*" -type f -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "redis_backup_*.aof" -type f -mtime +$RETENTION_DAYS -delete
}

# Función para verificar conectividad con Redis
check_connection() {
    if ! redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASS" ping > /dev/null 2>&1; then
        log "ERROR: No se puede conectar a Redis en $REDIS_HOST:$REDIS_PORT"
        exit 1
    fi
    log "Conexión a Redis verificada"
}

# Función para obtener información de Redis
get_redis_info() {
    local info=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASS" info all 2>/dev/null)
    local keys_count=$(echo "$info" | grep "^db0:keys=" | cut -d= -f2 | cut -d, -f1)
    local memory_used=$(echo "$info" | grep "^used_memory_human=" | cut -d= -f2)
    local uptime=$(echo "$info" | grep "^uptime_in_seconds=" | cut -d= -f2)
    
    echo "keys=$keys_count"
    echo "memory=$memory_used"
    echo "uptime=$uptime"
}

# Función para crear backup de RDB
create_rdb_backup() {
    local backup_file="${BACKUP_DIR}/redis_backup_${TIMESTAMP}.rdb"
    
    log "Iniciando backup de RDB de Redis"
    
    # Obtener información antes del backup
    local info_before=$(get_redis_info)
    log "Estado antes del backup - $info_before"
    
    # Forzar un checkpoint si AOF está habilitado
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASS" config get appendonly | grep -q "appendonly.*yes"; then
        log "Activando checkpoint para sincronizar AOF con RDB"
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASS" bgrewriteaof
        sleep 2
    fi
    
    # Crear snapshot RDB
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASS" --rdb "$backup_file" || {
        log "ERROR: Falló la creación del backup RDB"
        exit 1
    }
    
    # Verificar integridad del backup
    if [ ! -f "$backup_file" ] || [ ! -s "$backup_file" ]; then
        log "ERROR: El archivo de backup RDB está vacío o no existe"
        exit 1
    fi
    
    # Verificar que es un archivo RDB válido
    if ! file "$backup_file" | grep -q "data"; then
        log "ERROR: El archivo RDB no parece ser válido"
        exit 1
    fi
    
    # Obtener información después del backup
    local info_after=$(get_redis_info)
    log "Estado después del backup - $info_after"
    
    log "Backup RDB completado: $(du -h "$backup_file" | cut -f1)"
}

# Función para crear backup de AOF
create_aof_backup() {
    local aof_file="${BACKUP_DIR}/redis_backup_${TIMESTAMP}.aof"
    local latest_aof=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASS" config get appendfilename | tail -1)
    
    if [ -n "$latest_aof" ] && [ -f "$latest_aof" ]; then
        log "Creando backup de AOF: $latest_aof"
        cp "$latest_aof" "$aof_file"
        log "Backup AOF completado: $(du -h "$aof_file" | cut -f1)"
    else
        log "No se encontró archivo AOF para respaldar"
    fi
}

# Función para crear backup completo
create_full_backup() {
    log "=== Iniciando proceso de backup completo de Redis ==="
    check_connection
    
    # Crear backups
    create_rdb_backup
    create_aof_backup
    
    # Limpiar backups antiguos
    cleanup_old_backups
    
    log "=== Proceso de backup de Redis completado ==="
}

# Función para restaurar backup
restore_backup() {
    local backup_file="$1"
    if [ -z "$backup_file" ]; then
        log "ERROR: Debe especificar un archivo de backup para restaurar"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log "ERROR: El archivo de backup no existe: $backup_file"
        exit 1
    fi
    
    log "ADVERTENCIA: Restaurando backup desde: $backup_file"
    log "Esto reemplazará todos los datos actuales en Redis"
    read -p "¿Continuar? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        
        # Detener escritura temporalmente
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASS" config set save ""
        
        # Restaurar backup
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASS" --rdb "$backup_file" || {
            log "ERROR: Falló la restauración del backup"
            redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASS" config set save "900 1 300 10 60 10000"
            exit 1
        }
        
        # Reactivar configuración de save
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASS" config set save "900 1 300 10 60 10000"
        
        # Limpiar datos antiguos del cache
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASS" flushall 2>/dev/null || true
        
        log "Backup restaurado exitosamente"
    else
        log "Operación de restauración cancelada"
    fi
}

# Función para obtener información de backups
backup_info() {
    local backup_count=$(find "$BACKUP_DIR" -name "redis_backup_*.rdb*" | wc -l)
    local aof_count=$(find "$BACKUP_DIR" -name "redis_backup_*.aof" | wc -l)
    local total_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1 || echo "0B")
    local latest_rdb=$(find "$BACKUP_DIR" -name "redis_backup_*.rdb*" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    local latest_aof=$(find "$BACKUP_DIR" -name "redis_backup_*.aof" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    
    log "=== Información de backups Redis ==="
    log "Backups RDB: $backup_count"
    log "Backups AOF: $aof_count"
    log "Tamaño total: $total_size"
    if [ -n "$latest_rdb" ]; then
        log "RDB más reciente: $(basename "$latest_rdb") ($(du -h "$latest_rdb" 2>/dev/null | cut -f1 || echo "N/A"))"
    fi
    if [ -n "$latest_aof" ]; then
        log "AOF más reciente: $(basename "$latest_aof") ($(du -h "$latest_aof" 2>/dev/null | cut -f1 || echo "N/A"))"
    fi
    
    # Información de Redis actual
    local redis_info=$(get_redis_info)
    log "Estado actual de Redis - $redis_info"
}

# Main execution
case "${1:-backup}" in
    "backup")
        create_full_backup
        ;;
    "restore")
        restore_backup "$2"
        ;;
    "cleanup")
        cleanup_old_backups
        log "Limpieza completada"
        ;;
    "info")
        backup_info
        ;;
    *)
        echo "Uso: $0 {backup|restore|cleanup|info}"
        echo "  backup    - Crear backup completo (por defecto)"
        echo "  restore   - Restaurar desde backup"
        echo "  cleanup   - Limpiar backups antiguos"
        echo "  info      - Mostrar información de backups"
        exit 1
        ;;
esac
