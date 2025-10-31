#!/bin/bash

# =============================================================================
# SCRIPT DE BACKUP AUTOMÁTICO PARA MYSQL
# Realiza backup completo de la base de datos con compresión y retención
# =============================================================================

set -euo pipefail

# Configuración
BACKUP_DIR="/backup"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="reniec_db"
DB_USER="${MYSQL_USER:-reniec_user}"
DB_PASS="${MYSQL_PASSWORD:-reniec_pass123}"
DB_HOST="localhost"
DB_PORT="3306"
RETENTION_DAYS=7
COMPRESSION_LEVEL=6

# Función para logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$BACKUP_DIR/backup.log"
}

# Función para cleanup de backups antiguos
cleanup_old_backups() {
    log "Limpiando backups antiguos (retención: ${RETENTION_DAYS} días)"
    find "$BACKUP_DIR" -name "mysql_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "mysql_backup_*.sql" -type f -mtime +$RETENTION_DAYS -delete
}

# Función para verificar conectividad
check_connection() {
    if ! mysqladmin ping -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" > /dev/null 2>&1; then
        log "ERROR: No se puede conectar a la base de datos MySQL"
        exit 1
    fi
    log "Conexión a la base de datos MySQL verificada"
}

# Función para crear backup
create_backup() {
    local backup_file="${BACKUP_DIR}/mysql_backup_${DB_NAME}_${TIMESTAMP}.sql"
    local compressed_file="${backup_file}.gz"
    
    log "Iniciando backup de la base de datos MySQL: $DB_NAME"
    
    # Crear backup con compresión
    mysqldump \
        --host="$DB_HOST" \
        --port="$DB_PORT" \
        --user="$DB_USER" \
        --password="$DB_PASS" \
        --single-transaction \
        --routines \
        --triggers \
        --events \
        --add-drop-database \
        --databases "$DB_NAME" \
        --verbose \
        --compress \
        > "$backup_file" 2>/dev/null || {
            log "ERROR: Falló la creación del backup"
            # Limpiar archivo parcial
            rm -f "$backup_file"
            exit 1
        }
    
    # Verificar integridad del backup
    if [ ! -f "$backup_file" ] || [ ! -s "$backup_file" ]; then
        log "ERROR: El archivo de backup está vacío o no existe"
        exit 1
    fi
    
    # Verificar que el backup contiene datos
    if ! grep -q "CREATE TABLE" "$backup_file"; then
        log "WARNING: El backup no contiene tablas"
    fi
    
    # Comprimir backup
    gzip "$backup_file"
    log "Backup completado y comprimido: $(du -h "$compressed_file" | cut -f1)"
}

# Función para verificar integridad del backup
verify_backup() {
    local backup_file="$1"
    
    if ! gzip -t "$backup_file" 2>/dev/null; then
        log "ERROR: El archivo de backup está corrupto"
        return 1
    fi
    
    log "Verificación de integridad: OK"
    return 0
}

# Función para restaurar backup (solo para testing)
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
    read -p "¿Continuar? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Verificar integridad antes de restaurar
        if ! verify_backup "$backup_file"; then
            log "ERROR: No se puede restaurar backup corrupto"
            exit 1
        fi
        
        # Restaurar backup
        gunzip -c "$backup_file" | mysql \
            --host="$DB_HOST" \
            --port="$DB_PORT" \
            --user="$DB_USER" \
            --password="$DB_PASS" \
            --verbose 2>/dev/null || {
                log "ERROR: Falló la restauración del backup"
                exit 1
            }
        
        log "Backup restaurado exitosamente"
    else
        log "Operación de restauración cancelada"
    fi
}

# Función para obtener información de backup
backup_info() {
    local backup_count=$(find "$BACKUP_DIR" -name "mysql_backup_*.sql.gz" | wc -l)
    local total_size=$(du -sh "$BACKUP_DIR" | cut -f1)
    local latest_backup=$(find "$BACKUP_DIR" -name "mysql_backup_*.sql.gz" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    
    log "=== Información de backups MySQL ==="
    log "Total de backups: $backup_count"
    log "Tamaño total: $total_size"
    if [ -n "$latest_backup" ]; then
        log "Backup más reciente: $(basename "$latest_backup") ($(du -h "$latest_backup" | cut -f1))"
    fi
}

# Main execution
case "${1:-backup}" in
    "backup")
        log "=== Iniciando proceso de backup de MySQL ==="
        check_connection
        create_backup
        cleanup_old_backups
        log "=== Proceso de backup completado ==="
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
