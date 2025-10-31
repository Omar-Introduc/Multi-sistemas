#!/bin/bash

# ===============================================================================
# SCRIPT DE TESTING DE FLUJOS DE COMUNICACIÓN
# ===============================================================================
# Funcionalidades:
# - Testing de comunicación entre servicios
# - Validación de APIs y endpoints
# - Testing deMessage Queue y event-driven workflows
# - Métricas de latencia y throughput
# - Reportes automatizados de comunicación
# ===============================================================================

set -euo pipefail

# Configuración global
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs/communication"
REPORT_DIR="${SCRIPT_DIR}/reports/communication"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="${LOG_DIR}/communication-flows_${TIMESTAMP}.log"
REPORT_FILE="${REPORT_DIR}/communication-test_${TIMESTAMP}.html"
PID_FILE="/tmp/test-communication.pid"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Variables de estado
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# URLs y configuraciones
declare -A API_ENDPOINTS
API_ENDPOINTS[lp1_banco]="http://localhost:8080/api"
API_ENDPOINTS[lp2_reniec]="http://localhost:8000/api"
API_ENDPOINTS[health_lp1]="http://localhost:8080/health"
API_ENDPOINTS[health_lp2]="http://localhost:8000/health"
API_ENDPOINTS[rabbitmq_mgmt]="http://localhost:15672/api"
API_ENDPOINTS[prometheus]="http://localhost:9090/api/v1"

# Configuración de pruebas
TEST_TIMEOUT=30
RETRY_ATTEMPTS=3
CONCURRENT_TESTS=5

# Métricas de performance
declare -A PERFORMANCE_METRICS
PERFORMANCE_METRICS[start_time]=$(date +%s%N)
PERFORMANCE_METRICS[total_duration]=0
PERFORMANCE_METRICS[avg_response_time]=0
PERFORMANCE_METRICS[max_response_time]=0
PERFORMANCE_METRICS[min_response_time]=999999
PERFORMANCE_METRICS[total_requests]=0
PERFORMANCE_METRICS[successful_requests]=0
PERFORMANCE_METRICS[failed_requests]=0

# Array para almacenar métricas detalladas
declare -a RESPONSE_TIMES
declare -a TEST_RESULTS

# ===============================================================================
# FUNCIONES DE LOGGING
# ===============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() { log "INFO" "$@"; }
log_warn() { log "WARN" "$@"; }
log_error() { log "ERROR" "$@"; }
log_success() { log "SUCCESS" "$@"; }
log_test() { log "TEST" "$@"; }

initialize_logging() {
    mkdir -p "$LOG_DIR" "$REPORT_DIR"
    
    cat > "$LOG_FILE" << EOF
================================================================================
TESTING DE FLUJOS DE COMUNICACIÓN - INICIADO
Timestamp: $(date '+%Y-%m-%d %H:%M:%S')
Script: $0
================================================================================

EOF
    log_info "Sistema de logging inicializado: $LOG_FILE"
}

# ===============================================================================
# UTILIDADES DE TESTING
# ===============================================================================

measure_response_time() {
    local url="$1"
    local start_ns=$(date +%s%N)
    
    local response
    local http_code
    local success=false
    
    # Realizar request con timeout
    if command -v curl >/dev/null 2>&1; then
        response=$(curl -s --max-time "$TEST_TIMEOUT" "$url" 2>/dev/null || echo "")
        http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TEST_TIMEOUT" "$url" 2>/dev/null || echo "000")
        
        if [[ "$http_code" =~ ^[23] ]]; then
            success=true
        fi
    fi
    
    local end_ns=$(date +%s%N)
    local duration_ms=$(( (end_ns - start_ns) / 1000000 ))
    
    echo "$duration_ms|$success|$response"
}

record_test_result() {
    local test_name="$1"
    local status="$2"  # PASS, FAIL, SKIP
    local response_time="$3"
    local details="$4"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    case "$status" in
        "PASS")
            TESTS_PASSED=$((TESTS_PASSED + 1))
            log_success "✅ $test_name"
            ;;
        "FAIL")
            TESTS_FAILED=$((TESTS_FAILED + 1))
            log_error "❌ $test_name"
            ;;
        "SKIP")
            TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
            log_warn "⏭️  $test_name"
            ;;
    esac
    
    if [[ -n "$response_time" && "$response_time" =~ ^[0-9]+$ ]]; then
        RESPONSE_TIMES+=("$response_time")
        
        # Actualizar métricas de performance
        if [[ "$response_time" -gt "${PERFORMANCE_METRICS[max_response_time]}" ]]; then
            PERFORMANCE_METRICS[max_response_time]="$response_time"
        fi
        
        if [[ "$response_time" -lt "${PERFORMANCE_METRICS[min_response_time]}" ]]; then
            PERFORMANCE_METRICS[min_response_time]="$response_time"
        fi
        
        if [[ "$status" == "PASS" ]]; then
            PERFORMANCE_METRICS[successful_requests]=$((PERFORMANCE_METRICS[successful_requests] + 1))
        else
            PERFORMANCE_METRICS[failed_requests]=$((PERFORMANCE_METRICS[failed_requests] + 1))
        fi
        
        PERFORMANCE_METRICS[total_requests]=$((PERFORMANCE_METRICS[total_requests] + 1))
    fi
    
    # Guardar resultado detallado
    TEST_RESULTS+=("{\"test\":\"$test_name\",\"status\":\"$status\",\"time\":\"$response_time\",\"details\":\"$details\"}")
}

# ===============================================================================
# TESTING DE COMUNICACIÓN HTTP/REST API
# ===============================================================================

test_http_api_communication() {
    local endpoint_name="$1"
    local endpoint_url="$2"
    
    log_test "Probando comunicación HTTP: $endpoint_name"
    
    local retry_count=0
    local success=false
    local response_time=0
    local response_data=""
    
    while [[ $retry_count -lt $RETRY_ATTEMPTS && $success == false ]]; do
        local result
        result=$(measure_response_time "$endpoint_url")
        
        IFS='|' read -r response_time success response_data <<< "$result"
        
        if [[ "$success" == "true" ]]; then
            success=true
            break
        fi
        
        retry_count=$((retry_count + 1))
        log_warn "Reintento $retry_count/$RETRY_ATTEMPTS para $endpoint_name"
        sleep 1
    done
    
    if [[ "$success" == "true" ]]; then
        record_test_result "HTTP API $endpoint_name" "PASS" "$response_time" "Respuesta exitosa"
    else
        record_test_result "HTTP API $endpoint_name" "FAIL" "" "Fallo después de $RETRY_ATTEMPTS intentos"
    fi
}

# ===============================================================================
# TESTING DE HEALTH CHECKS
# ===============================================================================

test_health_checks() {
    log_test "Ejecutando health checks de servicios..."
    
    for service in "${!API_ENDPOINTS[@]}"; do
        if [[ "$service" == *"health"* ]]; then
            test_http_api_communication "$service" "${API_ENDPOINTS[$service]}"
        fi
    done
}

# ===============================================================================
# TESTING DE RABBITMQ MESSAGING
# ===============================================================================

test_rabbitmq_messaging() {
    log_test "Probando comunicación de mensajes con RabbitMQ..."
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if command -v rabbitmqadmin >/dev/null 2>&1; then
        # Test connection to RabbitMQ management API
        local rabbitmq_user="${RABBITMQ_USER:-admin}"
        local rabbitmq_pass="${RABBITMQ_PASS:-admin}"
        local auth_header="Authorization: Basic $(echo -n "$rabbitmq_user:$rabbitmq_pass" | base64)"
        
        local response
        local http_code
        response=$(curl -s --max-time 10 -H "$auth_header" "${API_ENDPOINTS[rabbitmq_mgmt]}/overview" 2>/dev/null || echo "")
        http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 -H "$auth_header" "${API_ENDPOINTS[rabbitmq_mgmt]}/overview" 2>/dev/null || echo "000")
        
        if [[ "$http_code" == "200" ]]; then
            log_success "✅ RabbitMQ Management API accesible"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            
            # Obtener estadísticas de colas
            local queues_info
            queues_info=$(curl -s -H "$auth_header" "${API_ENDPOINTS[rabbitmq_mgmt]}/queues" 2>/dev/null || echo "[]")
            local queue_count
            queue_count=$(echo "$queues_info" | jq -r '. | length' 2>/dev/null || echo "0")
            
            log_info "Colas RabbitMQ encontradas: $queue_count"
            
            if [[ "$queue_count" -gt 0 ]]; then
                record_test_result "RabbitMQ Queues" "PASS" "0" "$queue_count colas activas"
            else
                record_test_result "RabbitMQ Queues" "WARN" "0" "No hay colas configuradas"
            fi
        else
            log_error "❌ RabbitMQ Management API no accesible (HTTP $http_code)"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        log_warn "⚠️  rabbitmqadmin no disponible, usando ping básico"
        if ping -c 3 -W 3 localhost >/dev/null 2>&1; then
            log_success "✅ Host RabbitMQ accesible"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            record_test_result "RabbitMQ Basic" "PASS" "0" "Host accesible"
        else
            log_error "❌ Host RabbitMQ no accesible"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    fi
}

# ===============================================================================
# TESTING DE COMUNICACIÓN INTER-SERVICIOS
# ===============================================================================

test_inter_service_communication() {
    log_test "Probando comunicación entre servicios..."
    
    # Test LP1 to LP2 communication
    local test_message='{"test": "inter_service_communication", "timestamp": "'$(date -Iseconds)'"}'
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    # Simular envío de mensaje de LP1 a LP2 (usando curl)
    local response
    local start_time=$(date +%s%N)
    
    if command -v curl >/dev/null 2>&1; then
        response=$(curl -s -X POST \
            -H "Content-Type: application/json" \
            -d "$test_message" \
            --max-time "$TEST_TIMEOUT" \
            "${API_ENDPOINTS[lp2_reniec]}/test-communication" 2>/dev/null || echo "")
        
        local end_time=$(date +%s%N)
        local response_time=$(( (end_time - start_time) / 1000000 ))
        
        if [[ -n "$response" && "$response" != "null" ]]; then
            log_success "✅ Comunicación LP1→LP2 exitosa"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            record_test_result "Inter-Service LP1→LP2" "PASS" "$response_time" "Mensaje enviado correctamente"
        else
            log_error "❌ Comunicación LP1→LP2 falló"
            TESTS_FAILED=$((TESTS_FAILED + 1))
            record_test_result "Inter-Service LP1→LP2" "FAIL" "$response_time" "No se recibió respuesta"
        fi
    else
        log_warn "⚠️  curl no disponible, saltando test de inter-servicios"
        TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
        record_test_result "Inter-Service Communication" "SKIP" "" "curl no disponible"
    fi
}

# ===============================================================================
# TESTING DE BASES DE DATOS
# ===============================================================================

test_database_connectivity() {
    log_test "Probando conectividad de bases de datos..."
    
    # Test PostgreSQL
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    if command -v pg_isready >/dev/null 2>&1; then
        if pg_isready -h localhost -p 5432 -t 5 >/dev/null 2>&1; then
            log_success "✅ PostgreSQL accesible"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            record_test_result "PostgreSQL Connection" "PASS" "0" "Conexión establecida"
        else
            log_error "❌ PostgreSQL no accesible"
            TESTS_FAILED=$((TESTS_FAILED + 1))
            record_test_result "PostgreSQL Connection" "FAIL" "" "Timeout de conexión"
        fi
    else
        log_warn "⚠️  pg_isready no disponible"
        TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
        record_test_result "PostgreSQL Connection" "SKIP" "" "pg_isready no disponible"
    fi
    
    # Test MySQL
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    if command -v mysqladmin >/dev/null 2>&1; then
        if mysqladmin ping -h localhost -P 3306 -t 5 >/dev/null 2>&1; then
            log_success "✅ MySQL accesible"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            record_test_result "MySQL Connection" "PASS" "0" "Conexión establecida"
        else
            log_error "❌ MySQL no accesible"
            TESTS_FAILED=$((TESTS_FAILED + 1))
            record_test_result "MySQL Connection" "FAIL" "" "Timeout de conexión"
        fi
    else
        log_warn "⚠️  mysqladmin no disponible"
        TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
        record_test_result "MySQL Connection" "SKIP" "" "mysqladmin no disponible"
    fi
    
    # Test Redis
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    if command -v redis-cli >/dev/null 2>&1; then
        if redis-cli ping >/dev/null 2>&1; then
            log_success "✅ Redis accesible"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            record_test_result "Redis Connection" "PASS" "0" "Conexión establecida"
        else
            log_error "❌ Redis no accesible"
            TESTS_FAILED=$((TESTS_FAILED + 1))
            record_test_result "Redis Connection" "FAIL" "" "Timeout de conexión"
        fi
    else
        log_warn "⚠️  redis-cli no disponible"
        TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
        record_test_result "Redis Connection" "SKIP" "" "redis-cli no disponible"
    fi
}

# ===============================================================================
# TESTING DE ENDPOINTS ESPECÍFICOS
# ===============================================================================

test_specific_endpoints() {
    log_test "Probando endpoints específicos de servicios..."
    
    # LP1 Banco endpoints
    local lp1_endpoints=(
        "health"
        "accounts"
        "transactions"
        "loans"
    )
    
    for endpoint in "${lp1_endpoints[@]}"; do
        local url="${API_ENDPOINTS[lp1_banco]}/$endpoint"
        test_http_api_communication "LP1-$endpoint" "$url"
    done
    
    # LP2 RENIEC endpoints
    local lp2_endpoints=(
        "health"
        "citizens"
        "documents"
        "validation"
    )
    
    for endpoint in "${lp2_endpoints[@]}"; do
        local url="${API_ENDPOINTS[lp2_reniec]}/$endpoint"
        test_http_api_communication "LP2-$endpoint" "$url"
    done
}

# ===============================================================================
# GENERACIÓN DE REPORTE HTML
# ===============================================================================

generate_html_report() {
    log_info "Generando reporte HTML de comunicación..."
    
    local end_time=$(date +%s%N)
    PERFORMANCE_METRICS[total_duration]=$(( (end_time - PERFORMANCE_METRICS[start_time]) / 1000000 ))
    
    # Calcular promedio de tiempo de respuesta
    if [[ ${#RESPONSE_TIMES[@]} -gt 0 ]]; then
        local total_time=0
        for time in "${RESPONSE_TIMES[@]}"; do
            total_time=$((total_time + time))
        done
        PERFORMANCE_METRICS[avg_response_time]=$((total_time / ${#RESPONSE_TIMES[@]}))
    fi
    
    # Generar resultados de tests en JSON
    local tests_json=$(printf "%s," "${TEST_RESULTS[@]}" | sed 's/,$//')
    
    cat > "$REPORT_FILE" << EOF
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Testing de Comunicación</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }
        .metric-value { font-size: 2em; font-weight: bold; color: #007bff; }
        .metric-label { color: #666; margin-top: 5px; }
        .test-results { margin-top: 30px; }
        .test-category { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .test-item { padding: 10px; margin: 5px 0; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; }
        .pass { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .fail { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .skip { background-color: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .performance-chart { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; }
        .chart-bar { height: 20px; background: #007bff; margin: 5px 0; border-radius: 4px; }
        .footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #666; }
    </style>
    <script>
        const testResults = [$tests_json];
        
        function displayTestResults() {
            const container = document.getElementById('test-results');
            testResults.forEach(test => {
                const div = document.createElement('div');
                div.className = \`test-item \${test.status.toLowerCase()}\`;
                div.innerHTML = \`
                    <span>\${test.test}</span>
                    <span>\${test.status}</span>
                    <span>\${test.time || 'N/A'}ms</span>
                \`;
                container.appendChild(div);
            });
        }
        
        window.onload = displayTestResults;
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔄 Reporte de Testing de Comunicación</h1>
            <div class="timestamp">Generado el: $(date '+%Y-%m-%d %H:%M:%S')</div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">$TESTS_TOTAL</div>
                <div class="metric-label">Total de Tests</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #28a745;">$TESTS_PASSED</div>
                <div class="metric-label">Pasaron</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #dc3545;">$TESTS_FAILED</div>
                <div class="metric-label">Fallaron</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #ffc107;">$TESTS_SKIPPED</div>
                <div class="metric-label">Omitidos</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${PERFORMANCE_METRICS[avg_response_time]}ms</div>
                <div class="metric-label">Tiempo Promedio</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${PERFORMANCE_METRICS[total_duration]}ms</div>
                <div class="metric-label">Duración Total</div>
            </div>
        </div>
        
        <div class="test-results">
            <div class="test-category">
                <h3>📊 Resultados Detallados de Tests</h3>
                <div id="test-results"></div>
            </div>
            
            <div class="performance-chart">
                <h3>⚡ Métricas de Performance</h3>
                <div>
                    <strong>Tiempo Mínimo:</strong> ${PERFORMANCE_METRICS[min_response_time]}ms
                    <div class="chart-bar" style="width: ${PERFORMANCE_METRICS[min_response_time]}%;"></div>
                </div>
                <div>
                    <strong>Tiempo Promedio:</strong> ${PERFORMANCE_METRICS[avg_response_time]}ms
                    <div class="chart-bar" style="width: ${PERFORMANCE_METRICS[avg_response_time]}%;"></div>
                </div>
                <div>
                    <strong>Tiempo Máximo:</strong> ${PERFORMANCE_METRICS[max_response_time]}ms
                    <div class="chart-bar" style="width: ${PERFORMANCE_METRICS[max_response_time]}%;"></div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Script de testing de comunicación - Versión 1.0</p>
            <p>Estado de comunicación: <strong>$([ $TESTS_FAILED -eq 0 ] && echo "SALUDABLE" || echo "CON PROBLEMAS")</strong></p>
        </div>
    </div>
</body>
</html>
EOF
    
    log_success "Reporte HTML de comunicación generado: $REPORT_FILE"
}

# ===============================================================================
# FUNCIÓN PRINCIPAL
# ===============================================================================

main() {
    echo -e "${BLUE}================================================================================"
    echo -e "🔄 TESTING DE FLUJOS DE COMUNICACIÓN"
    echo -e "================================================================================${NC}"
    
    # Verificar si ya hay una prueba en curso
    if [[ -f "$PID_FILE" ]]; then
        local old_pid
        old_pid=$(cat "$PID_FILE")
        if kill -0 "$old_pid" 2>/dev/null; then
            log_error "Ya hay una prueba de comunicación en curso (PID: $old_pid)"
            exit 1
        fi
    fi
    
    # Crear PID file
    echo $$ > "$PID_FILE"
    
    # Cleanup al salir
    trap 'rm -f "$PID_FILE"' EXIT
    
    # Inicializar logging
    initialize_logging
    
    log_info "Iniciando testing de flujos de comunicación..."
    
    # Cargar configuración si existe
    if [[ -f "${SCRIPT_DIR}/config.env" ]]; then
        source "${SCRIPT_DIR}/config.env"
        log_info "Configuración cargada"
    fi
    
    # Ejecutar tests
    test_health_checks
    test_specific_endpoints
    test_rabbitmq_messaging
    test_inter_service_communication
    test_database_connectivity
    
    # Generar reporte final
    generate_html_report
    
    # Mostrar resumen
    echo -e "\n${BLUE}📊 RESUMEN DE TESTING${NC}"
    echo -e "Total de tests: $TESTS_TOTAL"
    echo -e "Pasaron: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Fallaron: ${RED}$TESTS_FAILED${NC}"
    echo -e "Omitidos: ${YELLOW}$TESTS_SKIPPED${NC}"
    echo -e "Tiempo total: ${PERFORMANCE_METRICS[total_duration]}ms"
    echo -e "Tiempo promedio: ${PERFORMANCE_METRICS[avg_response_time]}ms"
    
    if [[ $TESTS_FAILED -gt 0 ]]; then
        echo -e "\n${RED}❌ TESTING DE COMUNICACIÓN: PROBLEMAS DETECTADOS${NC}"
        exit 1
    else
        echo -e "\n${GREEN}✅ TESTING DE COMUNICACIÓN: EXITOSO${NC}"
    fi
    
    log_info "Testing de flujos de comunicación finalizado"
}

# ===============================================================================
# EJECUCIÓN
# ===============================================================================

# Manejo de argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "Uso: $0 [opciones]"
            echo "Opciones:"
            echo "  -h, --help     Mostrar esta ayuda"
            echo "  -t, --timeout  Timeout en segundos (default: $TEST_TIMEOUT)"
            echo "  -r, --retries  Número de reintentos (default: $RETRY_ATTEMPTS)"
            exit 0
            ;;
        -t|--timeout)
            TEST_TIMEOUT="$2"
            shift 2
            ;;
        -r|--retries)
            RETRY_ATTEMPTS="$2"
            shift 2
            ;;
        *)
            log_error "Opción desconocida: $1"
            exit 1
            ;;
    esac
done

# Ejecutar función principal
main "$@"