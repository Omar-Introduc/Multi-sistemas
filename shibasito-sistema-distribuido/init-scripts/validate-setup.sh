#!/bin/bash

# =============================================================================
# SCRIPT DE VALIDACIÓN COMPLETA DEL SETUP
# Sistema Distribuido Shibasito
# =============================================================================

set -euo pipefail

# =============================================================================
# CONFIGURACIÓN DE COLORES Y LOGGING
# =============================================================================
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="${SCRIPT_DIR}/../logs/validate_setup_$(date +%Y%m%d_%H%M%S).log"
readonly LOG_DIR="$(dirname "$LOG_FILE")"
readonly REPORT_FILE="${SCRIPT_DIR}/../logs/validation_report_$(date +%Y%m%d_%H%M%S).html"

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

print_test_result() {
    local test_name=$1
    local result=$2
    local details=$3
    local duration=$4
    
    case "$result" in
        "PASS")
            echo -e "  ${COLOR_GREEN}✅ PASS${COLOR_RESET} ${COLOR_BOLD}$test_name${COLOR_RESET}"
            [[ -n "$details" ]] && echo -e "     ${COLOR_WHITE}$details${COLOR_RESET}"
            [[ -n "$duration" ]] && echo -e "     ${COLOR_CYAN}Tiempo: ${duration}s${COLOR_RESET}"
            ;;
        "FAIL")
            echo -e "  ${COLOR_RED}❌ FAIL${COLOR_RESET} ${COLOR_BOLD}$test_name${COLOR_RESET}"
            [[ -n "$details" ]] && echo -e "     ${COLOR_RED}$details${COLOR_RESET}"
            [[ -n "$duration" ]] && echo -e "     ${COLOR_CYAN}Tiempo: ${duration}s${COLOR_RESET}"
            ;;
        "WARNING")
            echo -e "  ${COLOR_YELLOW}⚠️  WARN${COLOR_RESET} ${COLOR_BOLD}$test_name${COLOR_RESET}"
            [[ -n "$details" ]] && echo -e "     ${COLOR_YELLOW}$details${COLOR_RESET}"
            [[ -n "$duration" ]] && echo -e "     ${COLOR_CYAN}Tiempo: ${duration}s${COLOR_RESET}"
            ;;
    esac
}

# =============================================================================
# ESTRUCTURA DE REPORTE
# =============================================================================
declare -A TEST_RESULTS
declare -A TEST_DETAILS
declare -A TEST_DURATIONS
declare -A TEST_CATEGORIES

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================
print_header() {
    clear
    echo -e "${COLOR_BOLD}${COLOR_BLUE}"
    echo "================================================================================"
    echo "🔍 SISTEMA DISTRIBUIDO SHIBASITO - VALIDACIÓN COMPLETA DEL SETUP"
    echo "================================================================================"
    echo -e "${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Script: ${COLOR_BOLD}${SCRIPT_NAME}${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Directorio: ${COLOR_BOLD}${SCRIPT_DIR}${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Log: ${COLOR_BOLD}${LOG_FILE}${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Reporte: ${COLOR_BOLD}${REPORT_FILE}${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Fecha: ${COLOR_BOLD}$(date '+%Y-%m-%d %H:%M:%S')${COLOR_RESET}"
    echo ""
}

print_footer() {
    echo ""
    echo -e "${COLOR_BOLD}${COLOR_BLUE}================================================================================"
    echo -e "📊 RESUMEN DE VALIDACIÓN"
    echo -e "================================================================================${COLOR_RESET}"
    echo ""
    
    # Contar resultados
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    local warning_tests=0
    
    for test in "${!TEST_RESULTS[@]}"; do
        total_tests=$((total_tests + 1))
        case "${TEST_RESULTS[$test]}" in
            "PASS") passed_tests=$((passed_tests + 1)) ;;
            "FAIL") failed_tests=$((failed_tests + 1)) ;;
            "WARNING") warning_tests=$((warning_tests + 1)) ;;
        esac
    done
    
    echo -e "${COLOR_CYAN}📈 Estadísticas generales:${COLOR_RESET}"
    echo -e "  ${COLOR_BOLD}Total de pruebas:${COLOR_RESET} $total_tests"
    echo -e "  ${COLOR_GREEN}Exitosas:${COLOR_RESET} $passed_tests"
    echo -e "  ${COLOR_RED}Fallidas:${COLOR_RESET} $failed_tests"
    echo -e "  ${COLOR_YELLOW}Advertencias:${COLOR_RESET} $warning_tests"
    echo ""
    
    if [[ $failed_tests -eq 0 ]]; then
        echo -e "${COLOR_GREEN}${COLOR_BOLD}🎉 ¡VALIDACIÓN EXITOSA!${COLOR_RESET}"
        echo -e "${COLOR_GREEN}Todos los componentes del sistema están funcionando correctamente.${COLOR_RESET}"
    else
        echo -e "${COLOR_RED}${COLOR_BOLD}❌ VALIDACIÓN FALLIDA${COLOR_RESET}"
        echo -e "${COLOR_RED}Se encontraron $failed_tests errores que requieren atención.${COLOR_RESET}"
    fi
    
    if [[ $warning_tests -gt 0 ]]; then
        echo -e "${COLOR_YELLOW}⚠️  Se encontraron $warning_tests advertencias.${COLOR_RESET}"
    fi
    
    echo ""
    echo -e "${COLOR_CYAN}📄 Archivos generados:${COLOR_RESET}"
    echo -e "  ${COLOR_CYAN}• Log detallado:${COLOR_RESET} ${COLOR_BOLD}${LOG_FILE}${COLOR_RESET}"
    echo -e "  ${COLOR_CYAN}• Reporte HTML:${COLOR_RESET} ${COLOR_BOLD}${REPORT_FILE}${COLOR_RESET}"
    echo ""
}

start_timer() {
    echo $(date +%s.%N)
}

end_timer() {
    local start_time=$1
    local end_time=$(date +%s.%N)
    echo "$(echo "$end_time - $start_time" | bc -l)"
}

record_test() {
    local test_name=$1
    local result=$2
    local details=$3
    local duration=$4
    local category=$5
    
    TEST_RESULTS[$test_name]=$result
    TEST_DETAILS[$test_name]="$details"
    TEST_DURATIONS[$test_name]="$duration"
    TEST_CATEGORIES[$test_name]="$category"
}

# =============================================================================
# TESTS DE INFRAESTRUCTURA
# =============================================================================
test_docker_installation() {
    local test_name="Docker Installation"
    local category="Infrastructure"
    local start_time=$(start_timer)
    
    log_info "Verificando instalación de Docker..."
    
    if command -v docker &> /dev/null; then
        local docker_version=$(docker --version)
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "PASS" "$docker_version" "$duration" "$category"
        print_test_result "$test_name" "PASS" "$docker_version" "$duration"
    else
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "FAIL" "Docker no está instalado" "$duration" "$category"
        print_test_result "$test_name" "FAIL" "Docker no está instalado" "$duration"
    fi
}

test_docker_daemon() {
    local test_name="Docker Daemon"
    local category="Infrastructure"
    local start_time=$(start_timer)
    
    log_info "Verificando Docker daemon..."
    
    if docker info >/dev/null 2>&1; then
        local docker_info=$(docker version --format '{{.Server.Version}}' 2>/dev/null || echo "unknown")
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "PASS" "Docker daemon versión $docker_info" "$duration" "$category"
        print_test_result "$test_name" "PASS" "Docker daemon versión $docker_info" "$duration"
    else
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "FAIL" "Docker daemon no está ejecutándose" "$duration" "$category"
        print_test_result "$test_name" "FAIL" "Docker daemon no está ejecutándose" "$duration"
    fi
}

test_docker_compose() {
    local test_name="Docker Compose"
    local category="Infrastructure"
    local start_time=$(start_timer)
    
    log_info "Verificando Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        local compose_version=$(docker-compose --version)
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "PASS" "$compose_version" "$duration" "$category"
        print_test_result "$test_name" "PASS" "$compose_version" "$duration"
    else
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "FAIL" "Docker Compose no está instalado" "$duration" "$category"
        print_test_result "$test_name" "FAIL" "Docker Compose no está instalado" "$duration"
    fi
}

# =============================================================================
# TESTS DE CONTENEDORES
# =============================================================================
test_container_status() {
    local test_name="Container Status"
    local category="Containers"
    local start_time=$(start_timer)
    
    log_info "Verificando estado de contenedores..."
    
    local expected_containers=(
        "bd1_postgresql"
        "bd2_mysql"
        "rabbitmq"
        "redis"
        "servicio-banco-lp1"
        "servicio-reniec-lp2"
        "prometheus"
        "grafana"
    )
    
    local running_containers=$(docker ps --format '{{.Names}}')
    local all_running=true
    
    for container in "${expected_containers[@]}"; do
        if ! echo "$running_containers" | grep -q "^${container}$"; then
            all_running=false
            log_warning "Contenedor no encontrado: $container"
        fi
    done
    
    local duration=$(end_timer "$start_time")
    
    if $all_running; then
        record_test "$test_name" "PASS" "Todos los contenedores están ejecutándose" "$duration" "$category"
        print_test_result "$test_name" "PASS" "Todos los contenedores están ejecutándose" "$duration"
    else
        record_test "$test_name" "FAIL" "Algunos contenedores no están ejecutándose" "$duration" "$category"
        print_test_result "$test_name" "FAIL" "Algunos contenedores no están ejecutándose" "$duration"
    fi
}

test_container_health() {
    local test_name="Container Health"
    local category="Containers"
    local start_time=$(start_timer)
    
    log_info "Verificando health checks de contenedores..."
    
    local containers=("bd1_postgresql" "bd2_mysql" "rabbitmq" "redis")
    local all_healthy=true
    
    for container in "${containers[@]}"; do
        if docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null | grep -q "healthy"; then
            log_success "$container está saludable"
        else
            all_healthy=false
            log_warning "$container no está saludable"
        fi
    done
    
    local duration=$(end_timer "$start_time")
    
    if $all_healthy; then
        record_test "$test_name" "PASS" "Todos los health checks son exitosos" "$duration" "$category"
        print_test_result "$test_name" "PASS" "Todos los health checks son exitosos" "$duration"
    else
        record_test "$test_name" "WARNING" "Algunos health checks fallaron" "$duration" "$category"
        print_test_result "$test_name" "WARNING" "Algunos health checks fallaron" "$duration"
    fi
}

# =============================================================================
# TESTS DE REDES
# =============================================================================
test_network_configuration() {
    local test_name="Network Configuration"
    local category="Network"
    local start_time=$(start_timer)
    
    log_info "Verificando configuración de redes..."
    
    local networks=("shibasito-network" "database-network" "monitoring-network")
    local all_networks_exist=true
    
    for network in "${networks[@]}"; do
        if ! docker network ls --format '{{.Name}}' | grep -q "^${network}$"; then
            all_networks_exist=false
            log_error "Red no encontrada: $network"
        fi
    done
    
    local duration=$(end_timer "$start_time")
    
    if $all_networks_exist; then
        record_test "$test_name" "PASS" "Todas las redes están configuradas" "$duration" "$category"
        print_test_result "$test_name" "PASS" "Todas las redes están configuradas" "$duration"
    else
        record_test "$test_name" "FAIL" "Faltan configuraciones de red" "$duration" "$category"
        print_test_result "$test_name" "FAIL" "Faltan configuraciones de red" "$duration"
    fi
}

# =============================================================================
# TESTS DE BASES DE DATOS
# =============================================================================
test_postgresql() {
    local test_name="PostgreSQL Connection"
    local category="Database"
    local start_time=$(start_timer)
    
    log_info "Probando conexión a PostgreSQL..."
    
    if docker exec bd1_postgresql pg_isready -U banco_user -d banco_db >/dev/null 2>&1; then
        local version=$(docker exec bd1_postgresql psql -U banco_user -d banco_db -t -c "SELECT version();" 2>/dev/null | head -1)
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "PASS" "PostgreSQL conectado correctamente" "$duration" "$category"
        print_test_result "$test_name" "PASS" "PostgreSQL conectado correctamente" "$duration"
    else
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "FAIL" "No se puede conectar a PostgreSQL" "$duration" "$category"
        print_test_result "$test_name" "FAIL" "No se puede conectar a PostgreSQL" "$duration"
    fi
}

test_mysql() {
    local test_name="MySQL Connection"
    local category="Database"
    local start_time=$(start_timer)
    
    log_info "Probando conexión a MySQL..."
    
    if docker exec bd2_mysql mysqladmin ping -h localhost -u reniec_user -preniec_pass123 >/dev/null 2>&1; then
        local version=$(docker exec bd2_mysql mysql -u reniec_user -preniec_pass123 -e "SELECT VERSION();" 2>/dev/null | grep -v "VERSION()")
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "PASS" "MySQL conectado correctamente" "$duration" "$category"
        print_test_result "$test_name" "PASS" "MySQL conectado correctamente" "$duration"
    else
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "FAIL" "No se puede conectar a MySQL" "$duration" "$category"
        print_test_result "$test_name" "FAIL" "No se puede conectar a MySQL" "$duration"
    fi
}

# =============================================================================
# TESTS DE SERVICIOS DE APLICACIÓN
# =============================================================================
test_banco_api() {
    local test_name="Banco API Health"
    local category="Application"
    local start_time=$(start_timer)
    
    log_info "Probando API del Servicio Banco..."
    
    if docker exec servicio-banco-lp1 curl -f -s http://localhost:8080/actuator/health >/dev/null 2>&1; then
        local health_response=$(docker exec servicio-banco-lp1 curl -s http://localhost:8080/actuator/health)
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "PASS" "API del Banco respondiendo correctamente" "$duration" "$category"
        print_test_result "$test_name" "PASS" "API del Banco respondiendo correctamente" "$duration"
    else
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "FAIL" "API del Banco no responde" "$duration" "$category"
        print_test_result "$test_name" "FAIL" "API del Banco no responde" "$duration"
    fi
}

test_reniec_api() {
    local test_name="RENIEC API Health"
    local category="Application"
    local start_time=$(start_timer)
    
    log_info "Probando API del Servicio RENIEC..."
    
    if docker exec servicio-reniec-lp2 curl -f -s http://localhost:8000/health >/dev/null 2>&1; then
        local health_response=$(docker exec servicio-reniec-lp2 curl -s http://localhost:8000/health)
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "PASS" "API de RENIEC respondiendo correctamente" "$duration" "$category"
        print_test_result "$test_name" "PASS" "API de RENIEC respondiendo correctamente" "$duration"
    else
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "FAIL" "API de RENIEC no responde" "$duration" "$category"
        print_test_result "$test_name" "FAIL" "API de RENIEC no responde" "$duration"
    fi
}

# =============================================================================
# TESTS DE MENSAJERÍA Y CACHÉ
# =============================================================================
test_rabbitmq() {
    local test_name="RabbitMQ Connection"
    local category="Messaging"
    local start_time=$(start_timer)
    
    log_info "Probando conexión a RabbitMQ..."
    
    if docker exec rabbitmq rabbitmq-diagnostics ping >/dev/null 2>&1; then
        local version=$(docker exec rabbitmq rabbitmq-diagnostics version 2>/dev/null | grep -i version || echo "unknown")
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "PASS" "RabbitMQ funcionando correctamente" "$duration" "$category"
        print_test_result "$test_name" "PASS" "RabbitMQ funcionando correctamente" "$duration"
    else
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "FAIL" "No se puede conectar a RabbitMQ" "$duration" "$category"
        print_test_result "$test_name" "FAIL" "No se puede conectar a RabbitMQ" "$duration"
    fi
}

test_redis() {
    local test_name="Redis Connection"
    local category="Cache"
    local start_time=$(start_timer)
    
    log_info "Probando conexión a Redis..."
    
    if docker exec redis redis-cli ping >/dev/null 2>&1; then
        local redis_info=$(docker exec redis redis-cli info server 2>/dev/null | grep "redis_version" || echo "unknown")
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "PASS" "Redis funcionando correctamente" "$duration" "$category"
        print_test_result "$test_name" "PASS" "Redis funcionando correctamente" "$duration"
    else
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "FAIL" "No se puede conectar a Redis" "$duration" "$category"
        print_test_result "$test_name" "FAIL" "No se puede conectar a Redis" "$duration"
    fi
}

# =============================================================================
# TESTS DE MONITOREO
# =============================================================================
test_prometheus() {
    local test_name="Prometheus Monitoring"
    local category="Monitoring"
    local start_time=$(start_timer)
    
    log_info "Probando Prometheus..."
    
    if docker exec prometheus wget --quiet --tries=1 --spider http://localhost:9090/-/healthy >/dev/null 2>&1; then
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "PASS" "Prometheus funcionando correctamente" "$duration" "$category"
        print_test_result "$test_name" "PASS" "Prometheus funcionando correctamente" "$duration"
    else
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "FAIL" "Prometheus no responde" "$duration" "$category"
        print_test_result "$test_name" "FAIL" "Prometheus no responde" "$duration"
    fi
}

test_grafana() {
    local test_name="Grafana Dashboard"
    local category="Monitoring"
    local start_time=$(start_timer)
    
    log_info "Probando Grafana..."
    
    if docker exec grafana curl -f -s http://localhost:3000/api/health >/dev/null 2>&1; then
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "PASS" "Grafana funcionando correctamente" "$duration" "$category"
        print_test_result "$test_name" "PASS" "Grafana funcionando correctamente" "$duration"
    else
        local duration=$(end_timer "$start_time")
        record_test "$test_name" "FAIL" "Grafana no responde" "$duration" "$category"
        print_test_result "$test_name" "FAIL" "Grafana no responde" "$duration"
    fi
}

# =============================================================================
# TESTS DE ARCHIVOS DE CONFIGURACIÓN
# =============================================================================
test_configuration_files() {
    local test_name="Configuration Files"
    local category="Configuration"
    local start_time=$(start_timer)
    
    log_info "Verificando archivos de configuración..."
    
    local required_files=(
        "docker-compose.main.yml"
        "docker-compose.override.yml"
        ".env"
        "init-scripts/schema_lp1_banco.sql"
        "init-scripts/schema_lp2_reniec.sql"
    )
    
    local missing_files=()
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$SCRIPT_DIR/../$file" ]]; then
            missing_files+=("$file")
        fi
    done
    
    local duration=$(end_timer "$start_time")
    
    if [[ ${#missing_files[@]} -eq 0 ]]; then
        record_test "$test_name" "PASS" "Todos los archivos de configuración están presentes" "$duration" "$category"
        print_test_result "$test_name" "PASS" "Todos los archivos de configuración están presentes" "$duration"
    else
        local missing_list=$(IFS=", "; echo "${missing_files[*]}")
        record_test "$test_name" "FAIL" "Archivos faltantes: $missing_list" "$duration" "$category"
        print_test_result "$test_name" "FAIL" "Archivos faltantes: $missing_list" "$duration"
    fi
}

# =============================================================================
# GENERADOR DE REPORTE HTML
# =============================================================================
generate_html_report() {
    local test_name="HTML Report Generation"
    local category="Reporting"
    local start_time=$(start_timer)
    
    log_info "Generando reporte HTML..."
    
    cat > "$REPORT_FILE" << 'EOF'
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Validación - Sistema Shibasito</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .title {
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }
        .subtitle {
            color: #7f8c8d;
            margin: 10px 0 0 0;
            font-size: 1.2em;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .summary-card {
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid;
        }
        .summary-card.pass {
            background-color: #d4edda;
            border-left-color: #28a745;
            color: #155724;
        }
        .summary-card.fail {
            background-color: #f8d7da;
            border-left-color: #dc3545;
            color: #721c24;
        }
        .summary-card.warning {
            background-color: #fff3cd;
            border-left-color: #ffc107;
            color: #856404;
        }
        .summary-card.total {
            background-color: #e7f3ff;
            border-left-color: #007bff;
            color: #004085;
        }
        .summary-number {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .summary-label {
            font-size: 1.1em;
            opacity: 0.8;
        }
        .test-section {
            margin-bottom: 40px;
        }
        .section-title {
            color: #2c3e50;
            font-size: 1.5em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e0e0e0;
        }
        .test-item {
            display: flex;
            align-items: center;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 4px solid;
        }
        .test-item.pass {
            background-color: #f8fff9;
            border-left-color: #28a745;
        }
        .test-item.fail {
            background-color: #fff8f8;
            border-left-color: #dc3545;
        }
        .test-item.warning {
            background-color: #fffef8;
            border-left-color: #ffc107;
        }
        .test-icon {
            font-size: 1.2em;
            margin-right: 15px;
            width: 20px;
            text-align: center;
        }
        .test-content {
            flex-grow: 1;
        }
        .test-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .test-details {
            font-size: 0.9em;
            opacity: 0.8;
        }
        .test-duration {
            font-size: 0.8em;
            opacity: 0.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🔍 Reporte de Validación</h1>
            <p class="subtitle">Sistema Distribuido Shibasito</p>
            <p>Generado el: $(date '+%Y-%m-%d %H:%M:%S')</p>
        </div>
        
        <div class="summary">
            <div class="summary-card total">
                <div class="summary-number">${TOTAL_TESTS}</div>
                <div class="summary-label">Total de Pruebas</div>
            </div>
            <div class="summary-card pass">
                <div class="summary-number">${PASSED_TESTS}</div>
                <div class="summary-label">Exitosas</div>
            </div>
            <div class="summary-card fail">
                <div class="summary-number">${FAILED_TESTS}</div>
                <div class="summary-label">Fallidas</div>
            </div>
            <div class="summary-card warning">
                <div class="summary-number">${WARNING_TESTS}</div>
                <div class="summary-label">Advertencias</div>
            </div>
        </div>
        
        <div class="test-sections">
EOF

    # Agrupar tests por categoría
    declare -A CATEGORIES
    
    for test in "${!TEST_RESULTS[@]}"; do
        local category="${TEST_CATEGORIES[$test]}"
        CATEGORIES[$category]=1
    done
    
    # Generar secciones por categoría
    for category in "${!CATEGORIES[@]}"; do
        echo "            <div class=\"test-section\">" >> "$REPORT_FILE"
        echo "                <h2 class=\"section-title\">$category</h2>" >> "$REPORT_FILE"
        
        for test in "${!TEST_RESULTS[@]}"; do
            if [[ "${TEST_CATEGORIES[$test]}" == "$category" ]]; then
                local result="${TEST_RESULTS[$test]}"
                local details="${TEST_DETAILS[$test]}"
                local duration="${TEST_DURATIONS[$test]}"
                
                case "$result" in
                    "PASS") local icon="✅" ;;
                    "FAIL") local icon="❌" ;;
                    "WARNING") local icon="⚠️" ;;
                esac
                
                echo "                <div class=\"test-item $result\">" >> "$REPORT_FILE"
                echo "                    <div class=\"test-icon\">$icon</div>" >> "$REPORT_FILE"
                echo "                    <div class=\"test-content\">" >> "$REPORT_FILE"
                echo "                        <div class=\"test-name\">$test</div>" >> "$REPORT_FILE"
                if [[ -n "$details" ]]; then
                    echo "                        <div class=\"test-details\">$details</div>" >> "$REPORT_FILE"
                fi
                if [[ -n "$duration" ]]; then
                    echo "                        <div class=\"test-duration\">Tiempo: ${duration}s</div>" >> "$REPORT_FILE"
                fi
                echo "                    </div>" >> "$REPORT_FILE"
                echo "                </div>" >> "$REPORT_FILE"
            fi
        done
        
        echo "            </div>" >> "$REPORT_FILE"
    done
    
    cat >> "$REPORT_FILE" << 'EOF'
        </div>
    </div>
</body>
</html>
EOF

    # Reemplazar variables en el HTML
    local total_tests=${#TEST_RESULTS[@]}
    local passed_tests=0
    local failed_tests=0
    local warning_tests=0
    
    for test in "${!TEST_RESULTS[@]}"; do
        case "${TEST_RESULTS[$test]}" in
            "PASS") passed_tests=$((passed_tests + 1)) ;;
            "FAIL") failed_tests=$((failed_tests + 1)) ;;
            "WARNING") warning_tests=$((warning_tests + 1)) ;;
        esac
    done
    
    sed -i "s/\${TOTAL_TESTS}/$total_tests/g" "$REPORT_FILE"
    sed -i "s/\${PASSED_TESTS}/$passed_tests/g" "$REPORT_FILE"
    sed -i "s/\${FAILED_TESTS}/$failed_tests/g" "$REPORT_FILE"
    sed -i "s/\${WARNING_TESTS}/$warning_tests/g" "$REPORT_FILE"
    
    local duration=$(end_timer "$start_time")
    record_test "$test_name" "PASS" "Reporte HTML generado exitosamente" "$duration" "$category"
    print_test_result "$test_name" "PASS" "Reporte HTML generado exitosamente" "$duration"
}

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
main() {
    local start_time=$(date +%s)
    
    print_header
    
    log_step "Iniciando validación completa del setup"
    
    # Tests de infraestructura
    log_step "Ejecutando tests de infraestructura"
    test_docker_installation
    test_docker_daemon
    test_docker_compose
    
    # Tests de contenedores
    log_step "Ejecutando tests de contenedores"
    test_container_status
    test_container_health
    
    # Tests de red
    log_step "Ejecutando tests de red"
    test_network_configuration
    
    # Tests de bases de datos
    log_step "Ejecutando tests de bases de datos"
    test_postgresql
    test_mysql
    
    # Tests de aplicaciones
    log_step "Ejecutando tests de servicios de aplicación"
    test_banco_api
    test_reniec_api
    
    # Tests de mensajería y caché
    log_step "Ejecutando tests de mensajería y caché"
    test_rabbitmq
    test_redis
    
    # Tests de monitoreo
    log_step "Ejecutando tests de monitoreo"
    test_prometheus
    test_grafana
    
    # Tests de configuración
    log_step "Ejecutando tests de configuración"
    test_configuration_files
    
    # Generar reporte
    log_step "Generando reporte final"
    generate_html_report
    
    # Calcular tiempo total
    local end_time=$(date +%s)
    local total_duration=$((end_time - start_time))
    
    print_footer
    
    # Resumen final
    local failed_count=0
    for result in "${TEST_RESULTS[@]}"; do
        [[ "$result" == "FAIL" ]] && failed_count=$((failed_count + 1))
    done
    
    if [[ $failed_count -eq 0 ]]; then
        log_success "✅ VALIDACIÓN COMPLETADA EXITOSAMENTE"
        log_info "🎯 Tiempo total: ${total_duration}s"
        exit 0
    else
        log_error "❌ VALIDACIÓN FALLIDA - $failed_count errores encontrados"
        log_info "⏱️ Tiempo total: ${total_duration}s"
        exit 1
    fi
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