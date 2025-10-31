#!/bin/bash

# =============================================================================
# SCRIPT DE BACKUP AUTOMÁTICO PARA POSTGRESQL
# Realiza backup completo de la base de datos con compresión y retención
# =============================================================================

set -euo pipefail

# Configuración
BACKUP_DIR="/backup"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="banco_db"
DB_USER="${POSTGRES_USER:-banco_user}"
DB_HOST="localhost"
DB_PORT="5432"
RETENTION_DAYS=7
COMPRESSION_LEVEL=6

# Función para logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$BACKUP_DIR/backup.log"
}

# Función para cleanup de backups antiguos
cleanup_old_backups() {
    log "Limpiando backups antiguos (retención: ${RETENTION_DAYS} días)"
    find "$BACKUP_DIR" -name "postgres_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "postgres_backup_*.sql" -type f -mtime +$RETENTION_DAYS -delete
}

# Función para verificar conectividad
check_connection() {
    if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; then
        log "ERROR: No se puede conectar a la base de datos"
        exit 1
    fi
    log "Conexión a la base de datos verificada"
}

# Función para crear backup
create_backup() {
    local backup_file="${BACKUP_DIR}/postgres_backup_${DB_NAME}_${TIMESTAMP}.sql"
    local compressed_file="${backup_file}.gz"
    
    log "Iniciando backup de la base de datos: $DB_NAME"
    
    # Crear backup con compresión
    PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --no-password \
        --format=custom \
        --compress="$COMPRESSION_LEVEL" \
        --file="$backup_file" || {
            log "ERROR: Falló la creación del backup"
            exit 1
        }
    
    # Verificar integridad del backup
    if [ ! -f "$backup_file" ] || [ ! -s "$backup_file" ]; then
        log "ERROR: El archivo de backup está vacío o no existe"
        exit 1
    fi
    
    log "Backup completado exitosamente: $(du -h "$backup_file" | cut -f1)"
    
    # Comprimir si no está ya en formato comprimido
    if [[ "$backup_file" != *.gz ]]; then
        gzip "$backup_file"
        log "Backup comprimido: $(du -h "$compressed_file" | cut -f1)"
    fi
}

# Función para restaurar backup (solo para testing)
restore_backup() {
    local backup_file="$1"
    if [ -z "$backup_file" ]; then
        log "ERROR: Debe especificar un archivo de backup para restaurar"
        exit 1
    fi
    
    log "ADVERTENCIA: Restaurando backup desde: $backup_file"
    read -p "¿Continuar? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PGPASSWORD="$POSTGRES_PASSWORD" pg_restore \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            --clean \
            --if-exists \
            --verbose \
            "$backup_file"
        log "Backup restaurado exitosamente"
    else
        log "Operación de restauración cancelada"
    fi
}

# Main execution
case "${1:-backup}" in
    "backup")
        log "=== Iniciando proceso de backup de PostgreSQL ==="
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
    *)
        echo "Uso: $0 {backup|restore|cleanup}"
        echo "  backup    - Crear backup completo (por defecto)"
        echo "  restore   - Restaurar desde backup"
        echo "  cleanup   - Limpiar backups antiguos"
        exit 1
        ;;
esac
