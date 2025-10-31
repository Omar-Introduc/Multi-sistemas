#!/bin/bash

# =============================================================================
# SCRIPT DE CONFIGURACIÓN DE VARIABLES DE ENTORNO
# Sistema Distribuido Shibasito
# =============================================================================

set -euo pipefail

# =============================================================================
# CONFIGURACIÓN DE COLORES Y LOGGING
# =============================================================================
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="${SCRIPT_DIR}/../logs/environment_setup_$(date +%Y%m%d_%H%M%S).log"
readonly LOG_DIR="$(dirname "$LOG_FILE")"
readonly ENV_FILE="${SCRIPT_DIR}/.env"
readonly ENV_TEMPLATE="${SCRIPT_DIR}/.env.template"

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
    echo "🔧 SISTEMA DISTRIBUIDO SHIBASITO - CONFIGURACIÓN DE ENTORNO"
    echo "================================================================================"
    echo -e "${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Script: ${COLOR_BOLD}${SCRIPT_NAME}${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Directorio: ${COLOR_BOLD}${SCRIPT_DIR}${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Log: ${COLOR_BOLD}${LOG_FILE}${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Archivo de entorno: ${COLOR_BOLD}${ENV_FILE}${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Fecha: ${COLOR_BOLD}$(date '+%Y-%m-%d %H:%M:%S')${COLOR_RESET}"
    echo ""
}

print_footer() {
    echo ""
    echo -e "${COLOR_BOLD}${COLOR_BLUE}================================================================================"
    echo -e "✅ CONFIGURACIÓN DE ENTORNO COMPLETADA"
    echo -e "================================================================================${COLOR_RESET}"
    echo ""
    echo -e "${COLOR_CYAN}📋 Variables configuradas:${COLOR_RESET}"
    echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} Base de datos PostgreSQL"
    echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} Base de datos MySQL"
    echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} RabbitMQ"
    echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} Redis"
    echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} Servicios de aplicaciones"
    echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} Monitoreo (Prometheus/Grafana)"
    echo -e "  ${COLOR_CYAN}📄 Archivo de entorno: ${COLOR_BOLD}${ENV_FILE}${COLOR_RESET}"
    echo -e "  ${COLOR_CYAN}📄 Log completo: ${COLOR_BOLD}${LOG_FILE}${COLOR_RESET}"
    echo ""
}

# =============================================================================
# FUNCIONES DE CONFIGURACIÓN
# =============================================================================
generate_password() {
    local length=${1:-16}
    openssl rand -base64 "$length" | tr -d "=+/" | cut -c1-"$length"
}

prompt_user_input() {
    local prompt="$1"
    local default_value="$2"
    local input_value
    
    echo -ne "${COLOR_YELLOW}$prompt${COLOR_RESET}"
    if [[ -n "$default_value" ]]; then
        echo -ne " ${COLOR_CYAN}(Default: $default_value)${COLOR_RESET}"
    fi
    echo -ne ": "
    
    read -r input_value
    
    if [[ -z "$input_value" && -n "$default_value" ]]; then
        echo "$default_value"
    else
        echo "$input_value"
    fi
}

validate_environment() {
    local env_var="$1"
    local value="$2"
    
    case "$env_var" in
        POSTGRES_PORT|MYSQL_PORT|RABBITMQ_PORT|REDIS_PORT)
            if ! [[ "$value" =~ ^[0-9]+$ ]] || [[ "$value" -lt 1 ]] || [[ "$value" -gt 65535 ]]; then
                log_error "Puerto inválido para $env_var: $value"
                return 1
            fi
            ;;
        REDIS_DB)
            if ! [[ "$value" =~ ^[0-9]+$ ]] || [[ "$value" -lt 0 ]] || [[ "$value" -gt 15 ]]; then
                log_error "Número de base de datos Redis inválido: $value (debe ser 0-15)"
                return 1
            fi
            ;;
    esac
    
    return 0
}

create_env_template() {
    cat > "$ENV_TEMPLATE" << 'EOF'
# =============================================================================
# CONFIGURACIÓN DE VARIABLES DE ENTORNO - SISTEMA SHIBASITO
# =============================================================================
# Este archivo contiene todas las variables necesarias para el sistema
# Copie este archivo a .env y configure los valores según su entorno
# =============================================================================

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS POSTGRESQL (BD1)
# =============================================================================
POSTGRES_USER=banco_user
POSTGRES_PASSWORD=banco_pass123
POSTGRES_DB=banco_db
POSTGRES_HOST=bd1_postgresql
POSTGRES_PORT=5432

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS MYSQL (BD2)
# =============================================================================
MYSQL_USER=reniec_user
MYSQL_PASSWORD=reniec_pass123
MYSQL_DATABASE=reniec_db
MYSQL_HOST=bd2_mysql
MYSQL_PORT=3306
MYSQL_ROOT_PASSWORD=rootpass123

# =============================================================================
# CONFIGURACIÓN DE RABBITMQ
# =============================================================================
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin123
RABBITMQ_VHOST_BANCO=/banco
RABBITMQ_VHOST_RENIEC=/reniec

# =============================================================================
# CONFIGURACIÓN DE REDIS
# =============================================================================
REDIS_PASSWORD=redispass123
REDIS_HOST=redis
REDIS_PORT=6379

# =============================================================================
# CONFIGURACIÓN DE SERVICIOS DE APLICACIÓN
# =============================================================================

# Servicio Banco LP1 (Java/Spring Boot)
BANCO_API_PORT=8080
BANCO_MANAGEMENT_PORT=8081
BANCO_DEBUG=false
BANCO_LOG_LEVEL=INFO

# Servicio RENIEC LP2 (Python/FastAPI)
RENIEC_API_PORT=8000
RENIEC_METRICS_PORT=8001
RENIEC_DEBUG=false
RENIEC_LOG_LEVEL=INFO

# =============================================================================
# CONFIGURACIÓN DE MONITOREO
# =============================================================================

# Prometheus
PROMETHEUS_PORT=9090
PROMETHEUS_RETENTION=30d

# Grafana
GRAFANA_PORT=3000
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin123

# =============================================================================
# CONFIGURACIÓN DE REDES
# =============================================================================
NETWORK_SUBNET_BASE=172.20
DATABASE_NETWORK_SUBNET_BASE=172.21
MONITORING_NETWORK_SUBNET_BASE=172.22

# =============================================================================
# CONFIGURACIÓN DE VOLÚMENES
# =============================================================================
VOLUME_DRIVER=local

# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_RETENTION_DAYS=30
EOF
    log_success "Archivo template creado: $ENV_TEMPLATE"
}

setup_interactive() {
    log_step "Configuración interactiva de variables de entorno"
    
    echo -e "${COLOR_YELLOW}📝 Se configurarán las variables de entorno. Presione Enter para usar valores por defecto.${COLOR_RESET}\n"
    
    # Variables de PostgreSQL
    log_info "Configurando PostgreSQL (BD1 - Servicio Banco)"
    POSTGRES_USER=$(prompt_user_input "Usuario de PostgreSQL" "banco_user")
    POSTGRES_PASSWORD=$(prompt_user_input "Contraseña de PostgreSQL" "banco_pass123")
    POSTGRES_DB=$(prompt_user_input "Base de datos de PostgreSQL" "banco_db")
    
    # Variables de MySQL
    log_info "Configurando MySQL (BD2 - Servicio RENIEC)"
    MYSQL_USER=$(prompt_user_input "Usuario de MySQL" "reniec_user")
    MYSQL_PASSWORD=$(prompt_user_input "Contraseña de MySQL" "reniec_pass123")
    MYSQL_DATABASE=$(prompt_user_input "Base de datos de MySQL" "reniec_db")
    MYSQL_ROOT_PASSWORD=$(prompt_user_input "Contraseña root de MySQL" "rootpass123")
    
    # Variables de RabbitMQ
    log_info "Configurando RabbitMQ"
    RABBITMQ_USER=$(prompt_user_input "Usuario de RabbitMQ" "admin")
    RABBITMQ_PASSWORD=$(prompt_user_input "Contraseña de RabbitMQ" "admin123")
    
    # Variables de Redis
    log_info "Configurando Redis"
    REDIS_PASSWORD=$(prompt_user_input "Contraseña de Redis" "redispass123")
    
    # Variables de monitoreo
    log_info "Configurando servicios de monitoreo"
    GRAFANA_USER=$(prompt_user_input "Usuario de Grafana" "admin")
    GRAFANA_PASSWORD=$(prompt_user_input "Contraseña de Grafana" "admin123")
}

setup_default() {
    log_step "Configuración con valores por defecto"
    
    # Usar valores por defecto generados o seguros
    POSTGRES_USER="banco_user"
    POSTGRES_PASSWORD="banco_pass123"
    POSTGRES_DB="banco_db"
    POSTGRES_HOST="bd1_postgresql"
    POSTGRES_PORT=5432
    
    MYSQL_USER="reniec_user"
    MYSQL_PASSWORD="reniec_pass123"
    MYSQL_DATABASE="reniec_db"
    MYSQL_ROOT_PASSWORD="rootpass123"
    MYSQL_HOST="bd2_mysql"
    MYSQL_PORT=3306
    
    RABBITMQ_USER="admin"
    RABBITMQ_PASSWORD="admin123"
    
    REDIS_PASSWORD="redispass123"
    REDIS_HOST="redis"
    REDIS_PORT=6379
    
    GRAFANA_USER="admin"
    GRAFANA_PASSWORD="admin123"
    
    log_success "Configuración por defecto aplicada"
}

setup_production() {
    log_step "Configuración de entorno de producción"
    
    # Generar contraseñas seguras
    local secure_password=$(generate_password 20)
    local redis_password=$(generate_password 16)
    local grafana_password=$(generate_password 16)
    
    # Variables de PostgreSQL
    POSTGRES_USER="banco_prod_user"
    POSTGRES_PASSWORD="$secure_password"
    POSTGRES_DB="banco_production_db"
    POSTGRES_HOST="bd1_postgresql"
    POSTGRES_PORT=5432
    
    # Variables de MySQL
    MYSQL_USER="reniec_prod_user"
    MYSQL_PASSWORD="$secure_password"
    MYSQL_DATABASE="reniec_production_db"
    MYSQL_ROOT_PASSWORD="$(generate_password 24)"
    MYSQL_HOST="bd2_mysql"
    MYSQL_PORT=3306
    
    # Variables de RabbitMQ
    RABBITMQ_USER="prod_admin"
    RABBITMQ_PASSWORD="$(generate_password 18)"
    
    # Variables de Redis
    REDIS_PASSWORD="$redis_password"
    REDIS_HOST="redis"
    REDIS_PORT=6379
    
    # Variables de monitoreo
    GRAFANA_USER="prod_admin"
    GRAFANA_PASSWORD="$grafana_password"
    
    log_warning "⚠️  IMPORTANTE: Guarde estas contraseñas en un lugar seguro"
    log_warning "⚠️  PostgreSQL: $POSTGRES_PASSWORD"
    log_warning "⚠️  MySQL: $MYSQL_PASSWORD"
    log_warning "⚠️  RabbitMQ: $RABBITMQ_PASSWORD"
    log_warning "⚠️  Redis: $REDIS_PASSWORD"
    log_warning "⚠️  Grafana: $GRAFANA_PASSWORD"
    
    # Pequeña pausa para que el usuario pueda ver las contraseñas
    sleep 5
}

generate_env_file() {
    log_step "Generando archivo de configuración"
    
    cat > "$ENV_FILE" << EOF
# =============================================================================
# CONFIGURACIÓN DE VARIABLES DE ENTORNO - SISTEMA SHIBASITO
# Generado automáticamente el $(date '+%Y-%m-%d %H:%M:%S')
# =============================================================================

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS POSTGRESQL (BD1)
# =============================================================================
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=$POSTGRES_DB
POSTGRES_HOST=$POSTGRES_HOST
POSTGRES_PORT=$POSTGRES_PORT

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS MYSQL (BD2)
# =============================================================================
MYSQL_USER=$MYSQL_USER
MYSQL_PASSWORD=$MYSQL_PASSWORD
MYSQL_DATABASE=$MYSQL_DATABASE
MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD
MYSQL_HOST=$MYSQL_HOST
MYSQL_PORT=$MYSQL_PORT

# =============================================================================
# CONFIGURACIÓN DE RABBITMQ
# =============================================================================
RABBITMQ_USER=$RABBITMQ_USER
RABBITMQ_PASSWORD=$RABBITMQ_PASSWORD
RABBITMQ_VHOST_BANCO=/banco
RABBITMQ_VHOST_RENIEC=/reniec

# =============================================================================
# CONFIGURACIÓN DE REDIS
# =============================================================================
REDIS_PASSWORD=$REDIS_PASSWORD
REDIS_HOST=$REDIS_HOST
REDIS_PORT=$REDIS_PORT

# =============================================================================
# CONFIGURACIÓN DE SERVICIOS DE APLICACIÓN
# =============================================================================

# Servicio Banco LP1 (Java/Spring Boot)
BANCO_API_PORT=8080
BANCO_MANAGEMENT_PORT=8081
BANCO_DEBUG=false
BANCO_LOG_LEVEL=INFO

# Servicio RENIEC LP2 (Python/FastAPI)
RENIEC_API_PORT=8000
RENIEC_METRICS_PORT=8001
RENIEC_DEBUG=false
RENIEC_LOG_LEVEL=INFO

# =============================================================================
# CONFIGURACIÓN DE MONITOREO
# =============================================================================

# Prometheus
PROMETHEUS_PORT=9090
PROMETHEUS_RETENTION=30d

# Grafana
GRAFANA_PORT=3000
GRAFANA_USER=$GRAFANA_USER
GRAFANA_PASSWORD=$GRAFANA_PASSWORD

# =============================================================================
# CONFIGURACIÓN DE REDES
# =============================================================================
NETWORK_SUBNET_BASE=172.20
DATABASE_NETWORK_SUBNET_BASE=172.21
MONITORING_NETWORK_SUBNET_BASE=172.22

# =============================================================================
# CONFIGURACIÓN DE VOLÚMENES
# =============================================================================
VOLUME_DRIVER=local

# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_RETENTION_DAYS=30
EOF
    
    # Hacer el archivo legible solo por el usuario
    chmod 600 "$ENV_FILE"
    
    log_success "Archivo de entorno generado: $ENV_FILE"
}

validate_env_file() {
    log_step "Validando archivo de configuración"
    
    local errors=0
    
    # Verificar que el archivo existe
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "Archivo de entorno no encontrado: $ENV_FILE"
        return 1
    fi
    
    # Verificar variables críticas
    local required_vars=(
        "POSTGRES_USER"
        "POSTGRES_PASSWORD"
        "MYSQL_USER"
        "MYSQL_PASSWORD"
        "RABBITMQ_USER"
        "RABBITMQ_PASSWORD"
        "REDIS_PASSWORD"
        "GRAFANA_USER"
        "GRAFANA_PASSWORD"
    )
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" "$ENV_FILE"; then
            log_error "Variable requerida no encontrada: $var"
            errors=$((errors + 1))
        fi
    done
    
    if [[ $errors -eq 0 ]]; then
        log_success "Validación completada sin errores"
    else
        log_error "Se encontraron $errors errores en la validación"
        return 1
    fi
}

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
main() {
    print_header
    
    # Crear template si no existe
    if [[ ! -f "$ENV_TEMPLATE" ]]; then
        create_env_template
    fi
    
    # Determinar tipo de configuración
    local env_type="${1:-default}"
    
    case "$env_type" in
        "interactive")
            setup_interactive
            ;;
        "production")
            setup_production
            ;;
        "default")
            setup_default
            ;;
        *)
            log_error "Tipo de entorno no válido: $env_type"
            log_info "Usos válidos: interactive, production, default"
            exit 1
            ;;
    esac
    
    # Validar configuración
    if ! validate_environment "POSTGRES_PORT" "5432" || \
       ! validate_environment "MYSQL_PORT" "3306" || \
       ! validate_environment "REDIS_PORT" "6379"; then
        log_error "Error en validación de configuración"
        exit 1
    fi
    
    # Generar archivo de entorno
    generate_env_file
    
    # Validar archivo generado
    validate_env_file
    
    print_footer
    
    log_info "🎉 Configuración de entorno completada exitosamente"
    log_info "💡 Para usar este archivo, ejecute: source $ENV_FILE"
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