#!/bin/bash

# Script para verificar conectividad a bases de datos
# Compatible con PostgreSQL, MySQL, MongoDB
# Autor: Sistema de Monitoreo
# Fecha: $(date +%Y-%m-%d)

set -e

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/logs/db-check-$(date +%Y%m%d).log"
TIMEOUT=10

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

# Configuraciones de base de datos (modificar según entorno)
declare -A DB_CONFIGS
DB_CONFIGS["postgresql_primary"]="host=localhost port=5432 dbname=app_db user=app_user connect_timeout=$TIMEOUT"
DB_CONFIGS["postgresql_replica"]="host=localhost port=5433 dbname=app_db user=app_user connect_timeout=$TIMEOUT"
DB_CONFIGS["mysql_primary"]="--host=localhost --port=3306 --user=app_user --connect-timeout=$TIMEOUT"
DB_CONFIGS["mysql_replica"]="--host=localhost --port=3307 --user=app_user --connect-timeout=$TIMEOUT"

# Verificar conectividad PostgreSQL
check_postgresql() {
    local config_name=$1
    local config="${DB_CONFIGS[$config_name]}"
    
    log "INFO" "Verificando PostgreSQL ($config_name)..."
    
    if ! command -v psql >/dev/null 2>&1; then
        log "WARN" "psql no encontrado - PostgreSQL puede no estar instalado"
        return 1
    fi
    
    # Extraer parámetros de conexión
    local host=$(echo "$config" | grep -o 'host=[^ ]*' | cut -d'=' -f2)
    local port=$(echo "$config" | grep -o 'port=[^ ]*' | cut -d'=' -f2)
    local dbname=$(echo "$config" | grep -o 'dbname=[^ ]*' | cut -d'=' -f2)
    local user=$(echo "$config" | grep -o 'user=[^ ]*' | cut -d'=' -f2)
    
    # Verificar puerto
    if ! timeout $TIMEOUT bash -c "echo >/dev/tcp/$host/$port" 2>/dev/null; then
        log "ERROR" "PostgreSQL ($config_name): Puerto $port no accesible"
        return 1
    fi
    
    # Probar conexión y ejecutar consulta de prueba
    local query_result
    query_result=$(PGPASSWORD=app_password psql -h "$host" -p "$port" -U "$user" -d "$dbname" -t -c "SELECT 1;" 2>&1)
    
    if [ $? -eq 0 ] && echo "$query_result" | grep -q "1"; then
        log "SUCCESS" "PostgreSQL ($config_name): Conectividad OK"
        
        # Verificar métricas adicionales
        check_postgresql_metrics "$host" "$port" "$dbname" "$user" "$config_name"
        return 0
    else
        log "ERROR" "PostgreSQL ($config_name): Error de conexión - $query_result"
        return 1
    fi
}

# Verificar métricas PostgreSQL
check_postgresql_metrics() {
    local host=$1
    local port=$2
    local dbname=$3
    local user=$4
    local config_name=$5
    
    # Obtener número de conexiones activas
    local active_connections
    active_connections=$(PGPASSWORD=app_password psql -h "$host" -p "$port" -U "$user" -d "$dbname" -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null | xargs)
    
    if [ -n "$active_connections" ] && [ "$active_connections" -lt 100 ]; then
        log "INFO" "PostgreSQL ($config_name): Conexiones activas: $active_connections"
    elif [ -n "$active_connections" ]; then
        log "WARN" "PostgreSQL ($config_name): Alto número de conexiones: $active_connections"
    fi
    
    # Verificar tamaño de base de datos
    local db_size
    db_size=$(PGPASSWORD=app_password psql -h "$host" -p "$port" -U "$user" -d "$dbname" -t -c "SELECT pg_size_pretty(pg_database_size('$dbname'));" 2>/dev/null | xargs)
    
    if [ -n "$db_size" ]; then
        log "INFO" "PostgreSQL ($config_name): Tamaño de BD: $db_size"
    fi
    
    # Verificar integridad
    local integrity_check
    integrity_check=$(PGPASSWORD=app_password psql -h "$host" -p "$port" -U "$user" -d "$dbname" -t -c "SELECT count(*) FROM pg_stat_user_tables WHERE n_dead_tup > 1000;" 2>/dev/null | xargs)
    
    if [ -n "$integrity_check" ] && [ "$integrity_check" -gt 0 ]; then
        log "WARN" "PostgreSQL ($config_name): $integrity_check tablas con many dead tuples - considerar VACUUM"
    fi
}

# Verificar conectividad MySQL
check_mysql() {
    local config_name=$1
    local config="${DB_CONFIGS[$config_name]}"
    
    log "INFO" "Verificando MySQL ($config_name)..."
    
    if ! command -v mysql >/dev/null 2>&1; then
        log "WARN" "mysql no encontrado - MySQL puede no estar instalado"
        return 1
    fi
    
    # Extraer parámetros de conexión
    local host=$(echo "$config" | grep -o 'host=[^ ]*' | cut -d'=' -f2)
    local port=$(echo "$config" | grep -o 'port=[^ ]*' | cut -d'=' -f2)
    local user=$(echo "$config" | grep -o 'user=[^ ]*' | cut -d'=' -f2)
    
    # Verificar puerto
    if ! timeout $TIMEOUT bash -c "echo >/dev/tcp/$host/$port" 2>/dev/null; then
        log "ERROR" "MySQL ($config_name): Puerto $port no accesible"
        return 1
    fi
    
    # Probar conexión
    local query_result
    query_result=$(mysql $config --execute="SELECT 1;" 2>&1)
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "MySQL ($config_name): Conectividad OK"
        
        # Verificar métricas adicionales
        check_mysql_metrics "$host" "$port" "$user" "$config_name"
        return 0
    else
        log "ERROR" "MySQL ($config_name): Error de conexión - $query_result"
        return 1
    fi
}

# Verificar métricas MySQL
check_mysql_metrics() {
    local host=$1
    local port=$2
    local user=$3
    local config_name=$4
    
    # Conexiones activas
    local threads_connected
    threads_connected=$(mysql --host="$host" --port="$port" --user="$user" --execute="SHOW STATUS LIKE 'Threads_connected';" 2>/dev/null | tail -1 | awk '{print $2}')
    
    if [ -n "$threads_connected" ] && [ "$threads_connected" -lt 150 ]; then
        log "INFO" "MySQL ($config_name): Conexiones activas: $threads_connected"
    elif [ -n "$threads_connected" ]; then
        log "WARN" "MySQL ($config_name): Alto número de conexiones: $threads_connected"
    fi
    
    # Queries por segundo
    local queries_per_sec
    queries_per_sec=$(mysql --host="$host" --port="$port" --user="$user" --execute="SHOW STATUS LIKE 'Queries';" 2>/dev/null | tail -1 | awk '{print $2}')
    
    if [ -n "$queries_per_sec" ]; then
        log "INFO" "MySQL ($config_name): Total queries: $queries_per_sec"
    fi
}

# Verificar conectividad MongoDB
check_mongodb() {
    local host=${1:-localhost}
    local port=${2:-27017}
    
    log "INFO" "Verificando MongoDB ($host:$port)..."
    
    if ! command -v mongosh >/dev/null 2>&1 && ! command -v mongo >/dev/null 2>&1; then
        log "WARN" "MongoDB client no encontrado"
        return 1
    fi
    
    # Verificar puerto
    if ! timeout $TIMEOUT bash -c "echo >/dev/tcp/$host/$port" 2>/dev/null; then
        log "ERROR" "MongoDB ($host:$port): Puerto no accesible"
        return 1
    fi
    
    # Probar conexión con mongosh o mongo
    local mongo_cmd="mongosh"
    if ! command -v mongosh >/dev/null 2>&1; then
        mongo_cmd="mongo"
    fi
    
    local query_result
    query_result=$($mongo_cmd --host="$host" --port="$port" --eval "db.adminCommand('ping')" 2>&1)
    
    if echo "$query_result" | grep -q "ok.*1"; then
        log "SUCCESS" "MongoDB ($host:$port): Conectividad OK"
        return 0
    else
        log "ERROR" "MongoDB ($host:$port): Error de conexión - $query_result"
        return 1
    fi
}

# Verificar archivos de log de bases de datos
check_db_logs() {
    log "INFO" "Verificando logs de bases de datos..."
    
    # PostgreSQL logs
    if ls /var/log/postgresql/postgresql-*.log >/dev/null 2>&1; then
        local pg_errors=$(find /var/log/postgresql/ -name "*.log" -newermt "5 minutes ago" -exec grep -i "error\|fatal\|panic" {} \; 2>/dev/null | wc -l)
        if [ "$pg_errors" -gt 0 ]; then
            log "WARN" "PostgreSQL: $pg_errors errores en logs recientes"
        fi
    fi
    
    # MySQL logs
    if [ -f /var/log/mysql/error.log ]; then
        local mysql_errors=$(find /var/log/mysql/ -name "error.log" -newermt "5 minutes ago" -exec grep -i "error\|warning" {} \; 2>/dev/null | wc -l)
        if [ "$mysql_errors" -gt 5 ]; then
            log "WARN" "MySQL: $mysql_errors errores/warnings en logs recientes"
        fi
    fi
    
    # MongoDB logs
    if ls /var/log/mongodb/mongod.log >/dev/null 2>&1; then
        local mongo_errors=$(find /var/log/mongodb/ -name "*.log" -newermt "5 minutes ago" -exec grep -i "error\|severe\|critical" {} \; 2>/dev/null | wc -l)
        if [ "$mongo_errors" -gt 0 ]; then
            log "WARN" "MongoDB: $mongo_errors errores críticos en logs recientes"
        fi
    fi
}

# Verificar backups recientes
check_db_backups() {
    log "INFO" "Verificando backups de bases de datos..."
    
    local backup_dirs=(
        "/backups/postgresql"
        "/backups/mysql"
        "/backups/mongodb"
    )
    
    for backup_dir in "${backup_dirs[@]}"; do
        if [ -d "$backup_dir" ]; then
            local latest_backup=$(find "$backup_dir" -type f -name "*.sql" -o -name "*.dump" | sort | tail -1)
            
            if [ -n "$latest_backup" ]; then
                local backup_age=$(stat -c %Y "$latest_backup")
                local current_time=$(date +%s)
                local age_hours=$(( (current_time - backup_age) / 3600 ))
                
                if [ "$age_hours" -lt 24 ]; then
                    log "SUCCESS" "Backup reciente encontrado: $(basename "$latest_backup") (${age_hours}h)"
                else
                    log "WARN" "Backup desactualizado: $(basename "$latest_backup") (${age_hours}h)"
                fi
            else
                log "WARN" "No se encontraron backups en $backup_dir"
            fi
        fi
    done
}

# Función principal
run_db_checks() {
    local overall_status=0
    
    log "INFO" "=== INICIANDO VERIFICACIÓN DE BASES DE DATOS $(date) ==="
    
    # Verificar PostgreSQL
    for config in "postgresql_primary" "postgresql_replica"; do
        if [ -n "${DB_CONFIGS[$config]}" ]; then
            check_postgresql "$config" || ((overall_status++))
        fi
    done
    
    # Verificar MySQL
    for config in "mysql_primary" "mysql_replica"; do
        if [ -n "${DB_CONFIGS[$config]}" ]; then
            check_mysql "$config" || ((overall_status++))
        fi
    done
    
    # Verificar MongoDB
    check_mongodb "localhost" "27017" || ((overall_status++))
    
    # Verificaciones adicionales
    check_db_logs
    check_db_backups
    
    # Reportar estado
    if [ $overall_status -eq 0 ]; then
        log "SUCCESS" "=== VERIFICACIÓN DB COMPLETADA: TODAS LAS CONEXIONES OK ==="
        exit 0
    else
        log "ERROR" "=== VERIFICACIÓN DB COMPLETADA: $overall_status FALLOS ==="
        exit 1
    fi
}

# Manejo de señales
trap 'log "ERROR" "DB check interrumpido"; exit 130' INT TERM

# Ejecutar verificación si el script es llamado directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_db_checks
fi
