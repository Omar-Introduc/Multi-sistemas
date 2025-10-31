#!/bin/bash

# =============================================================================
# SCRIPT MAESTRO DE INICIALIZACIÓN DE BASES DE DATOS
# Sistema Distribuido Shibasito
# =============================================================================

set -euo pipefail

# =============================================================================
# CONFIGURACIÓN DE COLORES Y LOGGING
# =============================================================================
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="${SCRIPT_DIR}/../logs/database_init_$(date +%Y%m%d_%H%M%S).log"
readonly LOG_DIR="$(dirname "$LOG_FILE")"

# Crear directorio de logs si no existe
mkdir -p "$LOG_DIR"

# Colores para output
readonly COLOR_RESET='\033[0m'
readonly COLOR_RED='\033[0;31m'
readonly COLOR_GREEN='\033[0;32m'
readonly COLOR_YELLOW='\033[0;33m'
readonly COLOR_BLUE='\033[0;34m'
readonly COLOR_MAGENTA='\033[0;35m'
readonly COLOR_CYAN='\033[0;36m'
readonly COLOR_BOLD='\033[1m'

# =============================================================================
# FUNCIONES DE LOGGING Y OUTPUT
# =============================================================================
log_info() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${COLOR_CYAN}[INFO]${COLOR_RESET} ${COLOR_BOLD}${timestamp}${COLOR_RESET} - $1" | tee -a "$LOG_FILE"
}

log_success() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${COLOR_GREEN}[SUCCESS]${COLOR_RESET} ${COLOR_BOLD}${timestamp}${COLOR_RESET} - $1" | tee -a "$LOG_FILE"
}

log_warning() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${COLOR_YELLOW}[WARNING]${COLOR_RESET} ${COLOR_BOLD}${timestamp}${COLOR_RESET} - $1" | tee -a "$LOG_FILE"
}

log_error() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${COLOR_RED}[ERROR]${COLOR_RESET} ${COLOR_BOLD}${timestamp}${COLOR_RESET} - $1" | tee -a "$LOG_FILE"
}

log_step() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "\n${COLOR_MAGENTA}[STEP]${COLOR_RESET} ${COLOR_BOLD}${timestamp}${COLOR_RESET} - $1" | tee -a "$LOG_FILE"
}

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================
print_header() {
    clear
    echo -e "${COLOR_BOLD}${COLOR_BLUE}"
    echo "================================================================================"
    echo "🚀 SISTEMA DISTRIBUIDO SHIBASITO - INICIALIZACIÓN DE BASES DE DATOS"
    echo "================================================================================"
    echo -e "${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Script: ${COLOR_BOLD}${SCRIPT_NAME}${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Directorio: ${COLOR_BOLD}${SCRIPT_DIR}${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Log: ${COLOR_BOLD}${LOG_FILE}${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Fecha: ${COLOR_BOLD}$(date '+%Y-%m-%d %H:%M:%S')${COLOR_RESET}"
    echo ""
}

print_footer() {
    echo ""
    echo -e "${COLOR_BOLD}${COLOR_BLUE}================================================================================"
    echo -e "✅ INICIALIZACIÓN COMPLETADA EXITOSAMENTE"
    echo -e "================================================================================${COLOR_RESET}"
    echo ""
    echo -e "${COLOR_CYAN}📋 Resumen:${COLOR_RESET}"
    echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} PostgreSQL (BD1) - Banco LP1 inicializada"
    echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} MySQL (BD2) - RENIEC LP2 inicializada"
    echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} Índices y optimizaciones aplicados"
    echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} Datos de prueba insertados"
    echo -e "  ${COLOR_CYAN}📄 Log completo: ${COLOR_BOLD}${LOG_FILE}${COLOR_RESET}"
    echo ""
}

# =============================================================================
# CONFIGURACIÓN DE BASES DE DATOS
# =============================================================================
DB_CONFIG=(
    # PostgreSQL (BD1 - Servicio Banco)
    "POSTGRESQL:bd1_postgresql:5432:banco_db:banco_user:banco_pass123"
    
    # MySQL (BD2 - Servicio RENIEC)
    "MYSQL:bd2_mysql:3306:reniec_db:reniec_user:reniec_pass123"
)

# =============================================================================
# FUNCIONES DE INICIALIZACIÓN DE BASES DE DATOS
# =============================================================================
wait_for_database() {
    local db_type=$1
    local host=$2
    local port=$3
    local timeout=${4:-60}
    local count=0
    
    log_info "Esperando que $db_type esté disponible en $host:$port..."
    
    case "$db_type" in
        "POSTGRESQL")
            while [ $count -lt $timeout ]; do
                if docker exec "$host" pg_isready -U "${POSTGRES_USER:-banco_user}" -d banco_db >/dev/null 2>&1; then
                    log_success "$db_type está listo"
                    return 0
                fi
                count=$((count + 1))
                sleep 2
            done
            ;;
        "MYSQL")
            while [ $count -lt $timeout ]; do
                if docker exec "$host" mysqladmin ping -h localhost -u "${MYSQL_USER:-reniec_user}" -p"${MYSQL_PASSWORD:-reniec_pass123}" >/dev/null 2>&1; then
                    log_success "$db_TYPE está listo"
                    return 0
                fi
                count=$((count + 1))
                sleep 2
            done
            ;;
    esac
    
    log_error "$db_type no está disponible después de $timeout segundos"
    return 1
}

init_postgresql() {
    log_step "Inicializando PostgreSQL (BD1 - Servicio Banco)"
    
    local host="bd1_postgresql"
    local db="banco_db"
    local user="${POSTGRES_USER:-banco_user}"
    local schema_file="${SCRIPT_DIR}/schema_lp1_banco.sql"
    local indexes_file="${SCRIPT_DIR}/indexes_lp1.sql"
    local data_file="${SCRIPT_DIR}/seed_data_lp1.sql"
    local verify_file="${SCRIPT_DIR}/verification_lp1.sql"
    
    # Esperar que la base de datos esté disponible
    if ! wait_for_database "POSTGRESQL" "$host" "5432"; then
        log_error "No se pudo conectar a PostgreSQL"
        return 1
    fi
    
    # Verificar archivos SQL
    for file in "$schema_file" "$indexes_file" "$data_file" "$verify_file"; do
        if [[ ! -f "$file" ]]; then
            log_warning "Archivo SQL no encontrado: $file"
        fi
    done
    
    # Ejecutar esquema
    if [[ -f "$schema_file" ]]; then
        log_info "Aplicando esquema de base de datos..."
        if docker exec -i "$host" psql -U "$user" -d "$db" < "$schema_file" >> "$LOG_FILE" 2>&1; then
            log_success "Esquema aplicado correctamente"
        else
            log_error "Error al aplicar el esquema"
            return 1
        fi
    fi
    
    # Aplicar índices
    if [[ -f "$indexes_file" ]]; then
        log_info "Aplicando índices..."
        if docker exec -i "$host" psql -U "$user" -d "$db" < "$indexes_file" >> "$LOG_FILE" 2>&1; then
            log_success "Índices aplicados correctamente"
        else
            log_error "Error al aplicar índices"
            return 1
        fi
    fi
    
    # Insertar datos de prueba
    if [[ -f "$data_file" ]]; then
        log_info "Insertando datos de prueba..."
        if docker exec -i "$host" psql -U "$user" -d "$db" < "$data_file" >> "$LOG_FILE" 2>&1; then
            log_success "Datos de prueba insertados correctamente"
        else
            log_warning "Error al insertar datos de prueba (continuando...)"
        fi
    fi
    
    # Verificar inicialización
    if [[ -f "$verify_file" ]]; then
        log_info "Verificando inicialización..."
        if docker exec -i "$host" psql -U "$user" -d "$db" < "$verify_file" >> "$LOG_FILE" 2>&1; then
            log_success "Verificación completada"
        else
            log_warning "Error en verificación (continuando...)"
        fi
    fi
    
    log_success "PostgreSQL inicializado correctamente"
}

init_mysql() {
    log_step "Inicializando MySQL (BD2 - Servicio RENIEC)"
    
    local host="bd2_mysql"
    local db="reniec_db"
    local user="${MYSQL_USER:-reniec_user}"
    local password="${MYSQL_PASSWORD:-reniec_pass123}"
    local schema_file="${SCRIPT_DIR}/schema_lp2_reniec.sql"
    local indexes_file="${SCRIPT_DIR}/indexes_lp2.sql"
    local data_file="${SCRIPT_DIR}/seed_data_lp2.sql"
    
    # Esperar que la base de datos esté disponible
    if ! wait_for_database "MYSQL" "$host" "3306"; then
        log_error "No se pudo conectar a MySQL"
        return 1
    fi
    
    # Verificar archivos SQL
    for file in "$schema_file" "$indexes_file" "$data_file"; do
        if [[ ! -f "$file" ]]; then
            log_warning "Archivo SQL no encontrado: $file"
        fi
    done
    
    # Ejecutar esquema
    if [[ -f "$schema_file" ]]; then
        log_info "Aplicando esquema de base de datos..."
        if docker exec -i "$host" mysql -u "$user" -p"$password" "$db" < "$schema_file" >> "$LOG_FILE" 2>&1; then
            log_success "Esquema aplicado correctamente"
        else
            log_error "Error al aplicar el esquema"
            return 1
        fi
    fi
    
    # Aplicar índices
    if [[ -f "$indexes_file" ]]; then
        log_info "Aplicando índices..."
        if docker exec -i "$host" mysql -u "$user" -p"$password" "$db" < "$indexes_file" >> "$LOG_FILE" 2>&1; then
            log_success "Índices aplicados correctamente"
        else
            log_error "Error al aplicar índices"
            return 1
        fi
    fi
    
    # Insertar datos de prueba
    if [[ -f "$data_file" ]]; then
        log_info "Insertando datos de prueba..."
        if docker exec -i "$host" mysql -u "$user" -p"$password" "$db" < "$data_file" >> "$LOG_FILE" 2>&1; then
            log_success "Datos de prueba insertados correctamente"
        else
            log_warning "Error al insertar datos de prueba (continuando...)"
        fi
    fi
    
    log_success "MySQL inicializado correctamente"
}

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
main() {
    print_header
    
    log_step "Iniciando inicialización de bases de datos"
    
    # Verificar que Docker esté ejecutándose
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker no está ejecutándose. Por favor, inicie Docker primero."
        exit 1
    fi
    
    # Inicializar PostgreSQL (BD1)
    if ! init_postgresql; then
        log_error "Error en la inicialización de PostgreSQL"
        exit 1
    fi
    
    # Inicializar MySQL (BD2)
    if ! init_mysql; then
        log_error "Error en la inicialización de MySQL"
        exit 1
    fi
    
    print_footer
    
    log_info "🎉 Todas las bases de datos han sido inicializadas exitosamente"
}

# =============================================================================
# MANEJO DE SEÑALES Y LIMPIEZA
# =============================================================================
cleanup() {
    log_warning "Script interrumpido por señal"
    exit 130
}

trap cleanup SIGINT SIGTERM

# =============================================================================
# EJECUCIÓN
# =============================================================================
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi