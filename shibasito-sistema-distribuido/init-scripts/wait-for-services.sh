#!/bin/bash

# =============================================================================
# SCRIPT DE ESPERA PARA SERVICIOS
# Sistema Distribuido Shibasito
# =============================================================================

set -euo pipefail

# =============================================================================
# CONFIGURACIÓN DE COLORES Y LOGGING
# =============================================================================
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="${SCRIPT_DIR}/../logs/wait_for_services_$(date +%Y%m%d_%H%M%S).log"
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
readonly COLOR_WHITE='\033[1;37m'

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

print_progress() {
    local current=$1
    local total=$2
    local service=$3
    local percent=$((current * 100 / total))
    local filled=$((percent / 2))
    local empty=$((50 - filled))
    
    printf "\r${COLOR_BOLD}%s${COLOR_RESET} " "$service"
    printf "${COLOR_GREEN}"
    printf "%*s" $filled | tr ' ' '█'
    printf "${COLOR_YELLOW}"
    printf "%*s" $empty | tr ' ' '░'
    printf "${COLOR_RESET}"
    printf " ${COLOR_BOLD}%3d%%${COLOR_RESET}" $percent
}

print_service_status() {
    local service=$1
    local status=$2
    local details=$3
    
    case "$status" in
        "waiting")
            echo -e "  ${COLOR_YELLOW}⏳${COLOR_RESET} ${COLOR_CYAN}$service${COLOR_RESET} - Esperando..."
            ;;
        "starting")
            echo -e "  ${COLOR_BLUE}🚀${COLOR_RESET} ${COLOR_CYAN}$service${COLOR_RESET} - Iniciando..."
            ;;
        "ready")
            echo -e "  ${COLOR_GREEN}✅${COLOR_RESET} ${COLOR_CYAN}$service${COLOR_RESET} - ${COLOR_GREEN}Listo${COLOR_RESET}"
            ;;
        "error")
            echo -e "  ${COLOR_RED}❌${COLOR_RESET} ${COLOR_CYAN}$service${COLOR_RESET} - ${COLOR_RED}Error${COLOR_RESET}"
            ;;
        "timeout")
            echo -e "  ${COLOR_RED}⏰${COLOR_RESET} ${COLOR_CYAN}$service${COLOR_RESET} - ${COLOR_RED}Timeout${COLOR_RESET}"
            ;;
    esac
    
    if [[ -n "$details" ]]; then
        echo -e "     ${COLOR_WHITE}$details${COLOR_RESET}"
    fi
}

# =============================================================================
# CONFIGURACIÓN DE SERVICIOS
# =============================================================================
declare -A SERVICES
SERVICES=(
    # Servicios de base de datos
    ["bd1_postgresql"]="postgresql:5432"
    ["bd2_mysql"]="mysql:3306"
    
    # Servicios de mensajería y caché
    ["rabbitmq"]="rabbitmq:5672"
    ["redis"]="redis:6379"
    
    # Servicios de aplicación
    ["servicio-banco-lp1"]="banco:8080"
    ["servicio-reniec-lp2"]="reniec:8000"
    
    # Servicios de monitoreo
    ["prometheus"]="prometheus:9090"
    ["grafana"]="grafana:3000"
)

declare -A SERVICE_TIMEOUTS
SERVICE_TIMEOUTS=(
    ["bd1_postgresql"]=90
    ["bd2_mysql"]=90
    ["rabbitmq"]=120
    ["redis"]=60
    ["servicio-banco-lp1"]=180
    ["servicio-reniec-lp2"]=150
    ["prometheus"]=90
    ["grafana"]=90
)

declare -A SERVICE_TYPES
SERVICE_TYPES=(
    ["bd1_postgresql"]="database"
    ["bd2_mysql"]="database"
    ["rabbitmq"]="message_broker"
    ["redis"]="cache"
    ["servicio-banco-lp1"]="application"
    ["servicio-reniec-lp2"]="application"
    ["prometheus"]="monitoring"
    ["grafana"]="monitoring"
)

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================
print_header() {
    clear
    echo -e "${COLOR_BOLD}${COLOR_BLUE}"
    echo "================================================================================"
    echo "⏳ SISTEMA DISTRIBUIDO SHIBASITO - ESPERA DE SERVICIOS"
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
    echo -e "✅ TODOS LOS SERVICIOS ESTÁN LISTOS"
    echo -e "================================================================================${COLOR_RESET}"
    echo ""
    echo -e "${COLOR_CYAN}📋 Servicios verificados:${COLOR_RESET}"
    
    local total_services=${#SERVICES[@]}
    local ready_count=0
    
    for service in "${!SERVICES[@]}"; do
        if [[ "${SERVICE_STATUS[$service]:-}" == "ready" ]]; then
            ready_count=$((ready_count + 1))
            echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} ${COLOR_CYAN}$service${COLOR_RESET} (${SERVICE_TYPES[$service]})"
        fi
    done
    
    echo ""
    echo -e "${COLOR_CYAN}📊 Estadísticas:${COLOR_RESET}"
    echo -e "  ${COLOR_BOLD}Total servicios:${COLOR_RESET} $total_services"
    echo -e "  ${COLOR_GREEN}Servicios listos:${COLOR_RESET} $ready_count"
    echo -e "  ${COLOR_GREEN}Servicios en espera:${COLOR_RESET} $((total_services - ready_count))"
    echo -e "  ${COLOR_CYAN}⏱️  Tiempo total:${COLOR_RESET} ${TOTAL_TIME}s"
    echo -e "  ${COLOR_CYAN}📄 Log completo: ${COLOR_BOLD}${LOG_FILE}${COLOR_RESET}"
    echo ""
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker no está instalado"
        return 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker no está ejecutándose"
        return 1
    fi
    
    return 0
}

container_exists() {
    local container_name=$1
    docker ps -a --format '{{.Names}}' | grep -q "^${container_name}$"
}

container_running() {
    local container_name=$1
    docker ps --format '{{.Names}}' | grep -q "^${container_name}$"
}

# =============================================================================
# FUNCIONES DE VERIFICACIÓN DE SERVICIOS
# =============================================================================
wait_for_postgres() {
    local container=$1
    local timeout=$2
    
    log_info "Esperando PostgreSQL en $container..."
    
    local count=0
    while [[ $count -lt $timeout ]]; do
        if container_running "$container" && \
           docker exec "$container" pg_isready -U banco_user -d banco_db >/dev/null 2>&1; then
            log_success "PostgreSQL está listo"
            return 0
        fi
        
        if [[ $((count % 10)) -eq 0 ]]; then
            print_progress $count $timeout "PostgreSQL"
        fi
        
        sleep 2
        count=$((count + 2))
    done
    
    log_error "PostgreSQL no está disponible después de $timeout segundos"
    return 1
}

wait_for_mysql() {
    local container=$1
    local timeout=$2
    
    log_info "Esperando MySQL en $container..."
    
    local count=0
    while [[ $count -lt $timeout ]]; do
        if container_running "$container" && \
           docker exec "$container" mysqladmin ping -h localhost -u reniec_user -preniec_pass123 >/dev/null 2>&1; then
            log_success "MySQL está listo"
            return 0
        fi
        
        if [[ $((count % 10)) -eq 0 ]]; then
            print_progress $count $timeout "MySQL"
        fi
        
        sleep 2
        count=$((count + 2))
    done
    
    log_error "MySQL no está disponible después de $timeout segundos"
    return 1
}

wait_for_rabbitmq() {
    local container=$1
    local timeout=$2
    
    log_info "Esperando RabbitMQ en $container..."
    
    local count=0
    while [[ $count -lt $timeout ]]; do
        if container_running "$container" && \
           docker exec "$container" rabbitmq-diagnostics ping >/dev/null 2>&1; then
            log_success "RabbitMQ está listo"
            return 0
        fi
        
        if [[ $((count % 10)) -eq 0 ]]; then
            print_progress $count $timeout "RabbitMQ"
        fi
        
        sleep 2
        count=$((count + 2))
    done
    
    log_error "RabbitMQ no está disponible después de $timeout segundos"
    return 1
}

wait_for_redis() {
    local container=$1
    local timeout=$2
    
    log_info "Esperando Redis en $container..."
    
    local count=0
    while [[ $count -lt $timeout ]]; do
        if container_running "$container" && \
           docker exec "$container" redis-cli --raw incr ping >/dev/null 2>&1; then
            log_success "Redis está listo"
            return 0
        fi
        
        if [[ $((count % 10)) -eq 0 ]]; then
            print_progress $count $timeout "Redis"
        fi
        
        sleep 2
        count=$((count + 2))
    done
    
    log_error "Redis no está disponible después de $timeout segundos"
    return 1
}

wait_for_http_service() {
    local container=$1
    local port=$2
    local path=$3
    local timeout=$4
    local name=$5
    
    log_info "Esperando $name en $container:$port..."
    
    local count=0
    while [[ $count -lt $timeout ]]; do
        if container_running "$container" && \
           docker exec "$container" curl -f -s "http://localhost:${port}${path}" >/dev/null 2>&1; then
            log_success "$name está listo"
            return 0
        fi
        
        if [[ $((count % 10)) -eq 0 ]]; then
            print_progress $count $timeout "$name"
        fi
        
        sleep 2
        count=$((count + 2))
    done
    
    log_error "$name no está disponible después de $timeout segundos"
    return 1
}

# =============================================================================
# FUNCIÓN PRINCIPAL DE ESPERA
# =============================================================================
wait_for_service() {
    local service_name=$1
    local service_info=${SERVICES[$service_name]}
    local timeout=${SERVICE_TIMEOUTS[$service_name]:-60}
    local service_type=${SERVICE_TYPES[$service_name]:-unknown}
    
    # Verificar si el contenedor existe
    if ! container_exists "$service_name"; then
        log_warning "Contenedor $service_name no existe"
        SERVICE_STATUS[$service_name]="error"
        return 1
    fi
    
    # Verificar si el contenedor está ejecutándose
    if ! container_running "$service_name"; then
        log_warning "Contenedor $service_name no está ejecutándose"
        SERVICE_STATUS[$service_name]="error"
        return 1
    fi
    
    SERVICE_STATUS[$service_name]="starting"
    
    case "$service_type" in
        "database")
            if [[ "$service_name" == "bd1_postgresql" ]]; then
                wait_for_postgres "$service_name" "$timeout"
            elif [[ "$service_name" == "bd2_mysql" ]]; then
                wait_for_mysql "$service_name" "$timeout"
            fi
            ;;
        "message_broker")
            wait_for_rabbitmq "$service_name" "$timeout"
            ;;
        "cache")
            wait_for_redis "$service_name" "$timeout"
            ;;
        "application")
            if [[ "$service_name" == "servicio-banco-lp1" ]]; then
                wait_for_http_service "$service_name" "8080" "/actuator/health" "$timeout" "Servicio Banco"
            elif [[ "$service_name" == "servicio-reniec-lp2" ]]; then
                wait_for_http_service "$service_name" "8000" "/health" "$timeout" "Servicio RENIEC"
            fi
            ;;
        "monitoring")
            if [[ "$service_name" == "prometheus" ]]; then
                wait_for_http_service "$service_name" "9090" "/-/healthy" "$timeout" "Prometheus"
            elif [[ "$service_name" == "grafana" ]]; then
                wait_for_http_service "$service_name" "3000" "/api/health" "$timeout" "Grafana"
            fi
            ;;
    esac
    
    if [[ $? -eq 0 ]]; then
        SERVICE_STATUS[$service_name]="ready"
        return 0
    else
        SERVICE_STATUS[$service_name]="error"
        return 1
    fi
}

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
declare -A SERVICE_STATUS
TOTAL_TIME=0

main() {
    local start_time=$(date +%s)
    
    print_header
    
    log_step "Verificando Docker"
    if ! check_docker; then
        log_error "Docker no está disponible"
        exit 1
    fi
    
    log_step "Esperando servicios"
    
    # Mostrar servicios a verificar
    echo -e "${COLOR_CYAN}Servicios a verificar:${COLOR_RESET}"
    for service in "${!SERVICES[@]}"; do
        echo -e "  ${COLOR_YELLOW}•${COLOR_RESET} ${COLOR_CYAN}$service${COLOR_RESET} (${SERVICE_TYPES[$service]})"
    done
    echo ""
    
    local failed_services=()
    
    # Esperar cada servicio
    for service in "${!SERVICES[@]}"; do
        if ! wait_for_service "$service"; then
            failed_services+=("$service")
        fi
        echo ""  # Nueva línea después de cada servicio
    done
    
    local end_time=$(date +%s)
    TOTAL_TIME=$((end_time - start_time))
    
    print_footer
    
    # Verificar servicios fallidos
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        log_error "Los siguientes servicios fallaron:"
        for service in "${failed_services[@]}"; do
            echo -e "  ${COLOR_RED}•${COLOR_RESET} ${COLOR_CYAN}$service${COLOR_RESET}"
        done
        
        echo ""
        echo -e "${COLOR_YELLOW}💡 Sugerencias:${COLOR_RESET}"
        echo -e "  • Verifique que todos los contenedores estén ejecutándose: ${COLOR_BOLD}docker ps${COLOR_RESET}"
        echo -e "  • Revise los logs de los contenedores: ${COLOR_BOLD}docker logs <container_name>${COLOR_RESET}"
        echo -e "  • Verifique los recursos del sistema: ${COLOR_BOLD}docker system df${COLOR_RESET}"
        
        exit 1
    fi
    
    log_success "🎉 Todos los servicios están listos y funcionando correctamente"
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