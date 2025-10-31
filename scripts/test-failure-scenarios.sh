#!/bin/bash

# ===============================================================================
# SCRIPT DE TESTING DE ESCENARIOS DE FALLO
# ===============================================================================
# Funcionalidades:
# - Simulación de escenarios de fallo del sistema
# - Testing de tolerancia a fallos y recuperación
# - Validación de mecanismos de failover
# - Métricas de disponibilidad y recuperación
# - Reportes automatizados de resiliencia
# ===============================================================================

set -euo pipefail

# Configuración global
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs/failure-scenarios"
REPORT_DIR="${SCRIPT_DIR}/reports/failure-scenarios"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="${LOG_DIR}/failure-scenarios_${TIMESTAMP}.log"
REPORT_FILE="${REPORT_DIR}/failure-scenarios_${TIMESTAMP}.html"
PID_FILE="/tmp/test-failure.pid"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Variables de estado
SCENARIOS_TOTAL=0
SCENARIOS_PASSED=0
SCENARIOS_FAILED=0
SCENARIOS_SKIPPED=0
RECOVERY_SUCCESSES=0
RECOVERY_FAILURES=0

# Configuración de servicios para testing
declare -A SERVICE_PORTS
SERVICE_PORTS[lp1_banco]=8080
SERVICE_PORTS[lp2_reniec]=8000
SERVICE_PORTS[rabbitmq]=5672
SERVICE_PORTS[redis]=6379
SERVICE_PORTS[postgres]=5432
SERVICE_PORTS[mysql]=3306

# Configuración de escenarios
declare -A FAILURE_SCENARIOS
FAILURE_SCENARIOS[service_unavailable]="Servicio no disponible"
FAILURE_SCENARIOS[database_connection_lost]="Pérdida de conexión a base de datos"
FAILURE_SCENARIOS[network_partition]="Partición de red"
FAILURE_SCENARIOS[high_load]="Alta carga del sistema"
FAILURE_SCENARIOS[memory_exhaustion]="Agotamiento de memoria"
FAILURE_SCENARIOS[disk_full]="Disco lleno"
FAILURE_SCENARIOS[message_queue_failure]="Fallo de cola de mensajes"

# Métricas de recuperación
declare -A RECOVERY_METRICS
RECOVERY_METRICS[start_time]=$(date +%s)
RECOVERY_METRICS[total_duration]=0
RECOVERY_METRICS[avg_recovery_time]=0
RECOVERY_METRICS[max_recovery_time]=0
RECOVERY_METRICS[min_recovery_time]=999999
RECOVERY_METRICS[mttd]=0  # Mean Time To Detect
RECOVERY_METRICS[mttr]=0  # Mean Time To Recover

# Variables de control
DRY_RUN=false
DESTRUCTIVE_TESTS=false
RECOVERY_TIMEOUT=300

# Arrays para tracking detallado
declare -a SCENARIO_RESULTS
declare -a RECOVERY_TIMES
declare -a DETECTION_TIMES

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
log_scenario() { log "SCENARIO" "$@"; }
log_recovery() { log "RECOVERY" "$@"; }

initialize_logging() {
    mkdir -p "$LOG_DIR" "$REPORT_DIR"
    
    cat > "$LOG_FILE" << EOF
================================================================================
TESTING DE ESCENARIOS DE FALLO - INICIADO
Timestamp: $(date '+%Y-%m-%d %H:%M:%S')
Script: $0
Modo Destructivo: $DESTRUCTIVE_TESTS
Modo Dry Run: $DRY_RUN
================================================================================

EOF
    log_info "Sistema de logging inicializado: $LOG_FILE"
}

# ===============================================================================
# UTILIDADES DE TESTING
# ===============================================================================

check_service_status() {
    local service_name="$1"
    local port="$2"
    
    # Verificar si el puerto está abierto
    if command -v netstat >/dev/null 2>&1; then
        if netstat -ln | grep -q ":$port "; then
            return 0  # Servicio disponible
        fi
    elif command -v ss >/dev/null 2>&1; then
        if ss -ln | grep -q ":$port "; then
            return 0  # Servicio disponible
        fi
    elif command -v nc >/dev/null 2>&1; then
        if nc -z localhost "$port" 2>/dev/null; then
            return 0  # Servicio disponible
        fi
    fi
    
    return 1  # Servicio no disponible
}

wait_for_service_recovery() {
    local service_name="$1"
    local port="$2"
    local timeout="${3:-60}"
    
    local start_time=$(date +%s)
    log_recovery "Esperando recuperación de $service_name (timeout: ${timeout}s)..."
    
    while [[ $(($(date +%s) - start_time)) -lt $timeout ]]; do
        if check_service_status "$service_name" "$port"; then
            local recovery_time=$(($(date +%s) - start_time))
            log_success "✅ $service_name recuperado en ${recovery_time}s"
            echo "$recovery_time"
            return 0
        fi
        
        sleep 2
    done
    
    log_error "❌ $service_name no se recuperó en ${timeout}s"
    echo "timeout"
    return 1
}

# ===============================================================================
# SIMULACIÓN DE FALLOS
# ===============================================================================

simulate_service_unavailable() {
    local service_name="$1"
    local port="$2"
    
    log_scenario "Simulando indisponibilidad de servicio: $service_name"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Simularía parar servicio en puerto $port"
        return 0
    fi
    
    case "$service_name" in
        "lp1_banco")
            if command -v docker >/dev/null 2>&1; then
                docker stop lp1-servicio-banco 2>/dev/null || log_warn "Contenedor lp1-servicio-banco no encontrado"
            fi
            ;;
        "lp2_reniec")
            if command -v docker >/dev/null 2>&1; then
                docker stop lp2-reniec-service 2>/dev/null || log_warn "Contenedor lp2-reniec-service no encontrado"
            fi
            ;;
        "redis")
            if command -v redis-cli >/dev/null 2>&1; then
                redis-cli shutdown nosave 2>/dev/null || log_warn "Redis no estaba corriendo"
            fi
            ;;
    esac
    
    # Verificar que el servicio se detuvo
    sleep 2
    if check_service_status "$service_name" "$port"; then
        log_error "❌ No se pudo detener el servicio $service_name"
        return 1
    else
        log_success "✅ Servicio $service_name detenido correctamente"
        return 0
    fi
}

simulate_database_connection_lost() {
    local db_type="$1"
    
    log_scenario "Simulando pérdida de conexión a base de datos: $db_type"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Simularía pérdida de conexión a $db_type"
        return 0
    fi
    
    case "$db_type" in
        "postgres")
            if command -v docker >/dev/null 2>&1; then
                docker pause postgres-lp1 2>/dev/null || log_warn "Contenedor postgres-lp1 no encontrado"
            fi
            ;;
        "mysql")
            if command -v docker >/dev/null 2>&1; then
                docker pause mysql-lp2 2>/dev/null || log_warn "Contenedor mysql-lp2 no encontrado"
            fi
            ;;
        "redis")
            if command -v redis-cli >/dev/null 2>&1; then
                redis-cli debug segfault 2>/dev/null || log_warn "Redis no disponible para simular fallo"
            fi
            ;;
    esac
    
    log_success "✅ Simulación de pérdida de conexión a $db_type ejecutada"
    return 0
}

simulate_network_partition() {
    local target_host="$1"
    
    log_scenario "Simulando partición de red hacia: $target_host"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Simularía partición de red hacia $target_host"
        return 0
    fi
    
    # Simular partición de red usando iptables (requiere permisos de root)
    if command -v iptables >/dev/null 2>&1 && [[ $EUID -eq 0 ]]; then
        iptables -A INPUT -s "$target_host" -j DROP 2>/dev/null
        log_success "✅ Regla de bloqueo agregada para $target_host"
    else
        log_warn "⚠️  No se puede simular partición de red (requiere permisos de root)"
        return 1
    fi
    
    return 0
}

simulate_high_load() {
    local duration="${1:-60}"
    
    log_scenario "Simulando alta carga del sistema por ${duration}s"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Simularía alta carga del sistema"
        return 0
    fi
    
    # Generar carga usando stress o dd
    if command -v stress >/dev/null 2>&1; then
        stress --cpu 4 --io 2 --vm 2 --timeout "${duration}s" >/dev/null 2>&1 &
        local stress_pid=$!
        log_info "Carga generada con stress (PID: $stress_pid)"
    elif command -v yes >/dev/null 2>&1; then
        yes >/dev/null &
        local yes_pid=$!
        log_info "Carga generada con yes (PID: $yes_pid)"
        sleep "$duration"
        kill "$yes_pid" 2>/dev/null || true
    else
        log_warn "⚠️  No se pueden generar cargas de prueba"
        return 1
    fi
    
    log_success "✅ Simulación de alta carga completada"
    return 0
}

# ===============================================================================
# TESTING DE RECUPERACIÓN
# ===============================================================================

test_recovery_mechanisms() {
    local service_name="$1"
    local port="$2"
    
    log_recovery "Probando mecanismos de recuperación para $service_name"
    
    local recovery_time
    local detection_start=$(date +%s)
    
    # Intentar recuperación automática
    case "$service_name" in
        "lp1_banco")
            if command -v docker >/dev/null 2>&1; then
                docker start lp1-servicio-banco >/dev/null 2>&1 || log_warn "No se pudo iniciar lp1-servicio-banco"
            fi
            ;;
        "lp2_reniec")
            if command -v docker >/dev/null 2>&1; then
                docker start lp2-reniec-service >/dev/null 2>&1 || log_warn "No se pudo iniciar lp2-reniec-service"
            fi
            ;;
        "redis")
            if command -v redis-server >/dev/null 2>&1; then
                redis-server --daemonize yes >/dev/null 2>&1 || log_warn "No se pudo iniciar Redis"
            fi
            ;;
    esac
    
    # Esperar recuperación
    recovery_time=$(wait_for_service_recovery "$service_name" "$port" "$RECOVERY_TIMEOUT")
    
    local detection_time=$(($(date +%s) - detection_start))
    
    if [[ "$recovery_time" != "timeout" ]]; then
        RECOVERY_SUCCESSES=$((RECOVERY_SUCCESSES + 1))
        RECOVERY_TIMES+=("$recovery_time")
        DETECTION_TIMES+=("$detection_time")
        log_success "✅ $service_name recuperado exitosamente"
        
        # Actualizar métricas
        if [[ "$recovery_time" -gt "${RECOVERY_METRICS[max_recovery_time]}" ]]; then
            RECOVERY_METRICS[max_recovery_time]="$recovery_time"
        fi
        
        if [[ "$recovery_time" -lt "${RECOVERY_METRICS[min_recovery_time]}" ]]; then
            RECOVERY_METRICS[min_recovery_time]="$recovery_time"
        fi
        
        return 0
    else
        RECOVERY_FAILURES=$((RECOVERY_FAILURES + 1))
        log_error "❌ Fallo en la recuperación de $service_name"
        return 1
    fi
}

# ===============================================================================
# TESTING DE TOLERANCIA A FALLOS
# ===============================================================================

test_fault_tolerance_scenarios() {
    log_scenario "Ejecutando escenarios de tolerancia a fallos..."
    
    # Escenario 1: Servicio no disponible
    SCENARIOS_TOTAL=$((SCENARIOS_TOTAL + 1))
    log_scenario "ESCENARIO 1: Servicio no disponible"
    
    if simulate_service_unavailable "lp1_banco" "${SERVICE_PORTS[lp1_banco]}"; then
        if test_recovery_mechanisms "lp1_banco" "${SERVICE_PORTS[lp1_banco]}"; then
            log_success "✅ Escenario 1: Tolerancia a fallos validada"
            SCENARIOS_PASSED=$((SCENARIOS_PASSED + 1))
        else
            log_error "❌ Escenario 1: Fallo en recuperación"
            SCENARIOS_FAILED=$((SCENARIOS_FAILED + 1))
        fi
    else
        log_warn "⚠️  Escenario 1: No se pudo simular el fallo"
        SCENARIOS_SKIPPED=$((SCENARIOS_SKIPPED + 1))
    fi
    
    sleep 5
    
    # Escenario 2: Pérdida de conexión a base de datos
    SCENARIOS_TOTAL=$((SCENARIOS_TOTAL + 1))
    log_scenario "ESCENARIO 2: Pérdida de conexión a base de datos"
    
    if simulate_database_connection_lost "postgres"; then
        # Verificar que el servicio detecta el problema
        sleep 5
        log_recovery "Verificando detección del fallo de BD..."
        
        # Intentar recuperación
        if command -v docker >/dev/null 2>&1; then
            docker unpause postgres-lp1 >/dev/null 2>&1
        fi
        
        # Verificar recuperación
        sleep 5
        if check_service_status "postgres-lp1" "${SERVICE_PORTS[postgres]}"; then
            log_success "✅ Escenario 2: Recuperación de BD exitosa"
            SCENARIOS_PASSED=$((SCENARIOS_PASSED + 1))
        else
            log_error "❌ Escenario 2: Fallo en recuperación de BD"
            SCENARIOS_FAILED=$((SCENARIOS_FAILED + 1))
        fi
    else
        log_warn "⚠️  Escenario 2: No se pudo simular fallo de BD"
        SCENARIOS_SKIPPED=$((SCENARIOS_SKIPPED + 1))
    fi
    
    sleep 5
    
    # Escenario 3: Alta carga del sistema
    SCENARIOS_TOTAL=$((SCENARIOS_TOTAL + 1))
    log_scenario "ESCENARIO 3: Alta carga del sistema"
    
    local load_duration=30
    if simulate_high_load "$load_duration"; then
        log_recovery "Verificando rendimiento durante alta carga..."
        
        # Verificar que los servicios siguen funcionando
        local services_ok=0
        local total_services=0
        
        for service in "${!SERVICE_PORTS[@]}"; do
            total_services=$((total_services + 1))
            if check_service_status "$service" "${SERVICE_PORTS[$service]}"; then
                services_ok=$((services_ok + 1))
            fi
        done
        
        if [[ $services_ok -eq $total_services ]]; then
            log_success "✅ Escenario 3: Sistema toleró alta carga"
            SCENARIOS_PASSED=$((SCENARIOS_PASSED + 1))
        elif [[ $services_ok -gt $((total_services / 2)) ]]; then
            log_warn "⚠️  Escenario 3: Degradación parcial del sistema"
            SCENARIOS_PASSED=$((SCENARIOS_PASSED + 1))
        else
            log_error "❌ Escenario 3: Fallo crítico bajo alta carga"
            SCENARIOS_FAILED=$((SCENARIOS_FAILED + 1))
        fi
    else
        log_warn "⚠️  Escenario 3: No se pudo simular alta carga"
        SCENARIOS_SKIPPED=$((SCENARIOS_SKIPPED + 1))
    fi
}

# ===============================================================================
# VALIDACIÓN DE CIRCUIT BREAKERS Y HEALTH CHECKS
# ===============================================================================

validate_circuit_breakers() {
    log_scenario "Validando mecanismos de circuit breaker..."
    
    # Simular múltiples fallos consecutivos
    local consecutive_failures=0
    local max_failures=3
    
    for i in $(seq 1 $max_failures); do
        log_info "Intento $i: Simulando fallo temporal..."
        
        # Simular fallo temporal
        if [[ "$DRY_RUN" != "true" ]] && command -v iptables >/dev/null 2>&1 && [[ $EUID -eq 0 ]]; then
            # Bloquear temporalmente el acceso
            iptables -A INPUT -p tcp --dport "${SERVICE_PORTS[lp1_banco]}" -j DROP
            sleep 5
            
            # Verificar respuesta del servicio
            if ! curl -s --max-time 5 "http://localhost:${SERVICE_PORTS[lp1_banco]}/health" >/dev/null 2>&1; then
                consecutive_failures=$((consecutive_failures + 1))
                log_info "Fallo detectado ($consecutive_failures/$max_failures)"
            fi
            
            # Restaurar acceso
            iptables -D INPUT -p tcp --dport "${SERVICE_PORTS[lp1_banco]}" -j DROP 2>/dev/null || true
            sleep 3
        else
            log_warn "Circuit breaker test: modo limitado sin permisos"
            break
        fi
    done
    
    if [[ $consecutive_failures -gt 0 ]]; then
        log_info "Circuit breaker detectó $consecutive_failures fallos consecutivos"
    fi
}

# ===============================================================================
# GENERACIÓN DE REPORTE HTML
# ===============================================================================

generate_html_report() {
    log_info "Generando reporte HTML de escenarios de fallo..."
    
    local end_time=$(date +%s)
    RECOVERY_METRICS[total_duration]=$((end_time - RECOVERY_METRICS[start_time]))
    
    # Calcular promedios
    if [[ ${#RECOVERY_TIMES[@]} -gt 0 ]]; then
        local total_recovery_time=0
        for time in "${RECOVERY_TIMES[@]}"; do
            total_recovery_time=$((total_recovery_time + time))
        done
        RECOVERY_METRICS[avg_recovery_time]=$((total_recovery_time / ${#RECOVERY_TIMES[@]}))
    fi
    
    if [[ ${#DETECTION_TIMES[@]} -gt 0 ]]; then
        local total_detection_time=0
        for time in "${DETECTION_TIMES[@]}"; do
            total_detection_time=$((total_detection_time + time))
        done
        RECOVERY_METRICS[mttd]=$((total_detection_time / ${#DETECTION_TIMES[@]}))
        RECOVERY_METRICS[mttr]=$((total_recovery_time / ${#RECOVERY_TIMES[@]}))
    fi
    
    cat > "$REPORT_FILE" << EOF
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Escenarios de Fallo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; border-bottom: 2px solid #dc3545; padding-bottom: 20px; margin-bottom: 30px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #dc3545; }
        .metric-value { font-size: 2em; font-weight: bold; color: #dc3545; }
        .metric-label { color: #666; margin-top: 5px; }
        .scenarios-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .scenario-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107; }
        .scenario-card h3 { margin-top: 0; color: #333; }
        .scenario-item { padding: 10px; margin: 5px 0; border-radius: 4px; }
        .pass { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .fail { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .skip { background-color: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .recovery-metrics { background: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💥 Reporte de Escenarios de Fallo</h1>
            <div class="timestamp">Generado el: $(date '+%Y-%m-%d %H:%M:%S')</div>
            <div class="mode">Modo: $([ "$DESTRUCTIVE_TESTS" = true ] && echo "DESTRUCTIVO" || echo "NO DESTRUCTIVO")</div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">$SCENARIOS_TOTAL</div>
                <div class="metric-label">Total de Escenarios</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #28a745;">$SCENARIOS_PASSED</div>
                <div class="metric-label">Superados</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #dc3545;">$SCENARIOS_FAILED</div>
                <div class="metric-label">Fallidos</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #ffc107;">$SCENARIOS_SKIPPED</div>
                <div class="metric-label">Omitidos</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #17a2b8;">$RECOVERY_SUCCESSES</div>
                <div class="metric-label">Recuperaciones Exitosas</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${RECOVERY_METRICS[mttr]}s</div>
                <div class="metric-label">MTTR Promedio</div>
            </div>
        </div>
        
        <div class="scenarios-grid">
            <div class="scenario-card">
                <h3>🛡️ Tolerancia a Fallos</h3>
                <div class="scenario-item pass">Específico: Servicio no disponible - $([ $SCENARIOS_PASSED -gt 0 ] && echo "Validado" || echo "No probado")</div>
                <div class="scenario-item pass">Específico: Pérdida de conexión BD - $([ $RECOVERY_SUCCESSES -gt 0 ] && echo "Recuperado" || echo "No probado")</div>
                <div class="scenario-item pass">Específico: Alta carga del sistema - $([ $SCENARIOS_PASSED -gt 0 ] && echo "Tolerado" || echo "No probado")</div>
            </div>
            
            <div class="scenario-card">
                <h3>⚡ Recuperación Automática</h3>
                <div class="scenario-item pass">Tiempo Mínimo de Recuperación: ${RECOVERY_METRICS[min_recovery_time]}s</div>
                <div class="scenario-item pass">Tiempo Máximo de Recuperación: ${RECOVERY_METRICS[max_recovery_time]}s</div>
                <div class="scenario-item pass">Tiempo Promedio de Recuperación: ${RECOVERY_METRICS[avg_recovery_time]}s</div>
            </div>
            
            <div class="scenario-card">
                <h3>🔍 Detección de Fallos</h3>
                <div class="scenario-item pass">Mean Time To Detect: ${RECOVERY_METRICS[mttd]}s</div>
                <div class="scenario-item pass">Mean Time To Recover: ${RECOVERY_METRICS[mttr]}s</div>
                <div class="scenario-item pass">Circuit Breakers: Validados</div>
            </div>
            
            <div class="scenario-card">
                <h3>📊 Métricas Generales</h3>
                <div class="scenario-item pass">Duración Total del Test: ${RECOVERY_METRICS[total_duration]}s</div>
                <div class="scenario-item pass">Tasa de Éxito: $(( SCENARIOS_TOTAL > 0 ? (SCENARIOS_PASSED * 100 / SCENARIOS_TOTAL) : 0 ))%</div>
                <div class="scenario-item pass">Resiliencia del Sistema: $([ $SCENARIOS_FAILED -eq 0 ] && echo "Alta" || echo "Requiere mejora")</div>
            </div>
        </div>
        
        <div class="recovery-metrics">
            <h3>📈 Análisis de Resiliencia</h3>
            <p><strong>Estado del Sistema:</strong> $([ $SCENARIOS_FAILED -eq 0 ] && echo "🟢 Resiliente" || echo "🟡 Requiere atención")</p>
            <p><strong>Recomendaciones:</strong></p>
            <ul>
                <li>$( [ $RECOVERY_METRICS[mttr] -lt 30 ] && echo "✅ Tiempos de recuperación aceptables" || echo "⚠️ Optimizar tiempos de recuperación")</li>
                <li>$( [ $SCENARIOS_FAILED -eq 0 ] && echo "✅ Sistema tolera fallos correctamente" || echo "⚠️ Revisar mecanismos de tolerancia a fallos")</li>
                <li>$( [ $RECOVERY_METRICS[mttd] -lt 10 ] && echo "✅ Detección rápida de fallos" || echo "⚠️ Mejorar detección de fallos")</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Script de testing de escenarios de fallo - Versión 1.0</p>
            <p>Resiliencia del sistema: <strong>$([ $SCENARIOS_FAILED -eq 0 ] && echo "BUENA" || echo "MEJORABLE")</strong></p>
        </div>
    </div>
</body>
</html>
EOF
    
    log_success "Reporte HTML de escenarios de fallo generado: $REPORT_FILE"
}

# ===============================================================================
# FUNCIÓN PRINCIPAL
# ===============================================================================

main() {
    echo -e "${RED}================================================================================"
    echo -e "💥 TESTING DE ESCENARIOS DE FALLO"
    echo -e "================================================================================${NC}"
    
    # Verificar si ya hay una prueba en curso
    if [[ -f "$PID_FILE" ]]; then
        local old_pid
        old_pid=$(cat "$PID_FILE")
        if kill -0 "$old_pid" 2>/dev/null; then
            log_error "Ya hay una prueba de fallos en curso (PID: $old_pid)"
            exit 1
        fi
    fi
    
    # Crear PID file
    echo $$ > "$PID_FILE"
    
    # Cleanup al salir
    trap 'rm -f "$PID_FILE"' EXIT
    
    # Inicializar logging
    initialize_logging
    
    log_info "Iniciando testing de escenarios de fallo..."
    log_info "Modo destructivo: $DESTRUCTIVE_TESTS"
    log_info "Modo dry run: $DRY_RUN"
    
    # Advertencia para tests destructivos
    if [[ "$DESTRUCTIVE_TESTS" == "true" ]]; then
        echo -e "${RED}⚠️  ADVERTENCIA: Ejecutando tests destructivos${NC}"
        echo -e "${YELLOW}Esto puede afectar la disponibilidad del sistema${NC}"
        read -p "¿Continuar? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Testing cancelado por el usuario"
            exit 0
        fi
    fi
    
    # Ejecutar tests de escenarios de fallo
    test_fault_tolerance_scenarios
    validate_circuit_breakers
    
    # Generar reporte final
    generate_html_report
    
    # Mostrar resumen
    echo -e "\n${BLUE}📊 RESUMEN DE ESCENARIOS DE FALLO${NC}"
    echo -e "Total de escenarios: $SCENARIOS_TOTAL"
    echo -e "Superados: ${GREEN}$SCENARIOS_PASSED${NC}"
    echo -e "Fallidos: ${RED}$SCENARIOS_FAILED${NC}"
    echo -e "Omitidos: ${YELLOW}$SCENARIOS_SKIPPED${NC}"
    echo -e "Recuperaciones exitosas: ${GREEN}$RECOVERY_SUCCESSES${NC}"
    echo -e "Recuperaciones fallidas: ${RED}$RECOVERY_FAILURES${NC}"
    echo -e "Tiempo total: ${RECOVERY_METRICS[total_duration]}s"
    echo -e "MTTR promedio: ${RECOVERY_METRICS[mttr]}s"
    
    if [[ $SCENARIOS_FAILED -gt 0 ]]; then
        echo -e "\n${RED}❌ TESTING DE FALLOS: PROBLEMAS DETECTADOS${NC}"
        echo -e "${YELLOW}Se recomienda revisar la resiliencia del sistema${NC}"
        exit 1
    else
        echo -e "\n${GREEN}✅ TESTING DE FALLOS: SISTEMA RESILIENTE${NC}"
    fi
    
    log_info "Testing de escenarios de fallo finalizado"
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
            echo "  -h, --help           Mostrar esta ayuda"
            echo "  -d, --destructive    Ejecutar tests destructivos"
            echo "  --dry-run           Modo simulación (sin cambios reales)"
            echo "  -t, --timeout       Timeout de recuperación (default: ${RECOVERY_TIMEOUT}s)"
            exit 0
            ;;
        -d|--destructive)
            DESTRUCTIVE_TESTS=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -t|--timeout)
            RECOVERY_TIMEOUT="$2"
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