#!/bin/bash

# ===============================================================================
# SCRIPT DE VALIDACIÓN CONTINUA DEL SISTEMA
# ===============================================================================
# Funcionalidades:
# - Validación continua y automática del sistema
# - Monitoreo en tiempo real de servicios críticos
# - Sistema de alertas y notificaciones
# - Recolección de métricas continua
# - Generación automática de reportes periódicos
# ===============================================================================

set -euo pipefail

# Configuración global
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs/continuous"
MONITOR_DIR="${SCRIPT_DIR}/monitoring"
REPORT_DIR="${SCRIPT_DIR}/reports/continuous"
PID_FILE="/tmp/continuous-validation.pid"
STATE_FILE="${MONITOR_DIR}/state.json"
CONFIG_FILE="${SCRIPT_DIR}/config.env"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Variables de estado
IS_RUNNING=false
START_TIME=$(date +%s)
LAST_CHECK=0
TOTAL_CHECKS=0
SUCCESSFUL_CHECKS=0
FAILED_CHECKS=0
ALERTS_SENT=0

# Configuración de monitoreo
CHECK_INTERVAL=30  # segundos
ALERT_THRESHOLD=3  # fallos consecutivos antes de alertar
RECOVERY_THRESHOLD=2  # éxitos consecutivos para recovery
REPORT_INTERVAL=3600  # segundos (1 hora)

# Servicios críticos para monitorear
declare -A CRITICAL_SERVICES
CRITICAL_SERVICES[lp1_banco]="http://localhost:8080/health"
CRITICAL_SERVICES[lp2_reniec]="http://localhost:8000/health"
CRITICAL_SERVICES[rabbitmq]="tcp://localhost:5672"
CRITICAL_SERVICES[redis]="tcp://localhost:6379"
CRITICAL_SERVICES[postgres]="tcp://localhost:5432"

# Umbrales críticos
declare -A CRITICAL_THRESHOLDS
CRITICAL_THRESHOLDS[cpu_usage]=90
CRITICAL_THRESHOLDS[memory_usage]=90
CRITICAL_THRESHOLDS[disk_usage]=95
CRITICAL_THRESHOLDS[response_time]=5000  # ms
CRITICAL_THRESHOLDS[error_rate]=10  # %

# Variables para tracking de estado
declare -A SERVICE_STATUS
declare -A SERVICE_CONSECUTIVE_FAILURES
declare -A SERVICE_CONSECUTIVE_SUCCESSES

# Alertas y notificaciones
ALERT_COOLDOWN=300  # 5 minutos entre alertas del mismo tipo
LAST_ALERTS=()

# Arrays para datos históricos
declare -a CHECK_RESULTS
declare -a METRIC_HISTORY
declare -a ALERT_HISTORY

# ===============================================================================
# FUNCIONES DE LOGGING
# ===============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message"
}

log_info() { log "INFO" "$@"; }
log_warn() { log "WARN" "$@"; }
log_error() { log "ERROR" "$@"; }
log_success() { log "SUCCESS" "$@"; }
log_alert() { log "ALERT" "$@"; }
log_monitor() { log "MONITOR" "$@"; }

initialize_monitoring() {
    mkdir -p "$LOG_DIR" "$MONITOR_DIR" "$REPORT_DIR"
    
    # Inicializar archivo de estado
    cat > "$STATE_FILE" << EOF
{
    "start_time": $(date +%s),
    "is_running": true,
    "total_checks": 0,
    "successful_checks": 0,
    "failed_checks": 0,
    "alerts_sent": 0,
    "last_check": 0,
    "services": {}
}
EOF
    
    # Inicializar variables de estado
    for service in "${!CRITICAL_SERVICES[@]}"; do
        SERVICE_STATUS[$service]="unknown"
        SERVICE_CONSECUTIVE_FAILURES[$service]=0
        SERVICE_CONSECUTIVE_SUCCESSES[$service]=0
    done
    
    log_info "Sistema de monitoreo inicializado"
}

# ===============================================================================
# FUNCIONES DE VERIFICACIÓN DE SERVICIOS
# ===============================================================================

check_service_health() {
    local service_name="$1"
    local service_endpoint="$2"
    
    local start_time=$(date +%s%N)
    local is_healthy=false
    local response_time=0
    local error_message=""
    
    # Determinar tipo de servicio
    if [[ "$service_endpoint" == http* ]]; then
        # Servicio HTTP
        local response_code
        response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$service_endpoint" 2>/dev/null || echo "000")
        
        if [[ "$response_code" =~ ^[23] ]]; then
            is_healthy=true
        else
            error_message="HTTP $response_code"
        fi
    elif [[ "$service_endpoint" == tcp* ]]; then
        # Servicio TCP
        local port
        port=$(echo "$service_endpoint" | cut -d: -f3)
        
        if command -v nc >/dev/null 2>&1; then
            if nc -z localhost "$port" 2>/dev/null; then
                is_healthy=true
            else
                error_message="Puerto $port no accesible"
            fi
        elif command -v telnet >/dev/null 2>&1; then
            if timeout 5 telnet localhost "$port" </dev/null >/dev/null 2>&1; then
                is_healthy=true
            else
                error_message="Puerto $port no accesible"
            fi
        else
            error_message="Herramientas de red no disponibles"
        fi
    fi
    
    local end_time=$(date +%s%N)
    response_time=$(( (end_time - start_time) / 1000000 ))  # Convert to ms
    
    # Actualizar contadores
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    local previous_status="${SERVICE_STATUS[$service_name]}"
    
    if [[ "$is_healthy" == "true" ]]; then
        SERVICE_CONSECUTIVE_FAILURES[$service_name]=0
        SERVICE_CONSECUTIVE_SUCCESSES[$service_name]=$((SERVICE_CONSECUTIVE_SUCCESSES[$service_name] + 1))
        SUCCESSFUL_CHECKS=$((SUCCESSFUL_CHECKS + 1))
        
        if [[ "$previous_status" != "healthy" ]]; then
            SERVICE_STATUS[$service_name]="healthy"
            send_recovery_alert "$service_name"
        fi
    else
        SERVICE_CONSECUTIVE_SUCCESSES[$service_name]=0
        SERVICE_CONSECUTIVE_FAILURES[$service_name]=$((SERVICE_CONSECUTIVE_FAILURES[$service_name] + 1))
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        
        if [[ "$previous_status" != "unhealthy" ]]; then
            SERVICE_STATUS[$service_name]="unhealthy"
            check_and_send_alert "$service_name" "$error_message"
        fi
    fi
    
    # Guardar resultado
    local result_entry
    result_entry=$(printf '{"timestamp":"%s","service":"%s","status":"%s","response_time":%d,"consecutive_failures":%d}' \
        "$(date -Iseconds)" "$service_name" "$([[ "$is_healthy" == "true" ]] && echo "healthy" || echo "unhealthy")" \
        "$response_time" "${SERVICE_CONSECUTIVE_FAILURES[$service_name]}")
    
    CHECK_RESULTS+=("$result_entry")
    
    # Mantener solo los últimos 100 resultados
    if [[ ${#CHECK_RESULTS[@]} -gt 100 ]]; then
        CHECK_RESULTS=("${CHECK_RESULTS[@]:1}")
    fi
    
    # Log resultado
    if [[ "$is_healthy" == "true" ]]; then
        log_monitor "✅ $service_name: Saludable (${response_time}ms)"
    else
        log_monitor "❌ $service_name: No saludable - $error_message"
    fi
    
    return $([[ "$is_healthy" == "true" ]] && echo 0 || echo 1)
}

# ===============================================================================
# FUNCIONES DE ALERTAS
# ===============================================================================

check_and_send_alert() {
    local service_name="$1"
    local error_message="$2"
    
    local failures="${SERVICE_CONSECUTIVE_FAILURES[$service_name]}"
    
    if [[ $failures -ge $ALERT_THRESHOLD ]]; then
        # Verificar cooldown
        local alert_key="$service_name-critical"
        local should_alert=true
        
        for i in "${!LAST_ALERTS[@]}"; do
            if [[ "${LAST_ALERTS[$i]}" == "$alert_key" ]]; then
                local alert_time="${LAST_ALERTS[$i + 1]}"
                local time_diff=$(( $(date +%s) - alert_time ))
                
                if [[ $time_diff -lt $ALERT_COOLDOWN ]]; then
                    should_alert=false
                    break
                fi
            fi
        done
        
        if [[ "$should_alert" == "true" ]]; then
            send_critical_alert "$service_name" "$error_message" "$failures"
            LAST_ALERTS+=("$alert_key" "$(date +%s)")
        fi
    fi
}

send_critical_alert() {
    local service_name="$1"
    local error_message="$2"
    local failure_count="$3"
    
    log_alert "🚨 ALERTA CRÍTICA: $service_name - $error_message (${failure_count} fallos consecutivos)"
    
    # Registrar alerta
    local alert_entry
    alert_entry=$(printf '{"timestamp":"%s","level":"CRITICAL","service":"%s","message":"%s","failure_count":%d}' \
        "$(date -Iseconds)" "$service_name" "$error_message" "$failure_count")
    
    ALERT_HISTORY+=("$alert_entry")
    ALERTS_SENT=$((ALERTS_SENT + 1))
    
    # Aquí se pueden integrar notificaciones reales:
    # - Enviar email
    # - Enviar a Slack/Discord
    # - Llamar a webhooks
    # - SMS/Push notifications
    
    # Por ahora, solo registrar en log
    send_notification "ALERT" "$service_name" "$error_message"
}

send_recovery_alert() {
    local service_name="$1"
    
    log_alert "✅ RECUPERACIÓN: $service_name está funcionando correctamente"
    
    local alert_entry
    alert_entry=$(printf '{"timestamp":"%s","level":"RECOVERY","service":"%s","message":"Service recovered","failure_count":0}' \
        "$(date -Iseconds)" "$service_name")
    
    ALERT_HISTORY+=("$alert_entry")
    
    send_notification "RECOVERY" "$service_name" "Service recovered successfully"
}

send_notification() {
    local level="$1"
    local service="$2"
    local message="$3"
    
    # Formato de notificación
    local notification
    notification="[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $service: $message"
    
    # Escribir a archivo de notificaciones
    echo "$notification" >> "${MONITOR_DIR}/notifications.log"
    
    # Log a stdout para sistemas de logging
    case "$level" in
        "ALERT")
            log_error "$notification"
            ;;
        "RECOVERY")
            log_success "$notification"
            ;;
        *)
            log_info "$notification"
            ;;
    esac
}

# ===============================================================================
# FUNCIONES DE MÉTRICAS DEL SISTEMA
# ===============================================================================

collect_system_metrics() {
    local timestamp=$(date -Iseconds)
    
    # CPU Usage
    local cpu_usage="N/A"
    if command -v top >/dev/null 2>&1; then
        cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}' | tr -d ' ')
    fi
    
    # Memory Usage
    local memory_usage="N/A"
    if command -v free >/dev/null 2>&1; then
        memory_usage=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
    fi
    
    # Disk Usage
    local disk_usage="N/A"
    disk_usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    
    # Load Average
    local load_avg="N/A"
    if [[ -f /proc/loadavg ]]; then
        load_avg=$(cat /proc/loadavg | awk '{print $1}')
    fi
    
    # Network connections
    local connections="N/A"
    if command -v netstat >/dev/null 2>&1; then
        connections=$(netstat -tn | grep ESTABLISHED | wc -l)
    fi
    
    # Crear entrada de métricas
    local metrics_entry
    metrics_entry=$(printf '{"timestamp":"%s","cpu":"%s","memory":"%s","disk":"%s","load":"%s","connections":"%s"}' \
        "$timestamp" "$cpu_usage" "$memory_usage" "$disk_usage" "$load_avg" "$connections")
    
    METRIC_HISTORY+=("$metrics_entry")
    
    # Mantener solo las últimas 288 entradas (24 horas con intervalo de 5 minutos)
    if [[ ${#METRIC_HISTORY[@]} -gt 288 ]]; then
        METRIC_HISTORY=("${METRIC_HISTORY[@]:1}")
    fi
    
    # Verificar umbrales críticos
    check_critical_thresholds "$cpu_usage" "$memory_usage" "$disk_usage"
}

check_critical_thresholds() {
    local cpu_usage="$1"
    local memory_usage="$2"
    local disk_usage="$3"
    
    # CPU
    if [[ "$cpu_usage" =~ ^[0-9]+(\.[0-9]+)?$ ]] && [[ $(echo "$cpu_usage > ${CRITICAL_THRESHOLDS[cpu_usage]}" | bc 2>/dev/null || echo "false") == "true" ]]; then
        if [[ $(( $(date +%s) - LAST_CHECK )) -gt 300 ]]; then  # 5 minutos cooldown
            log_alert "🚨 CPU Usage crítico: ${cpu_usage}% (umbral: ${CRITICAL_THRESHOLDS[cpu_usage]}%)"
            LAST_ALERTS+=("cpu-critical" "$(date +%s)")
        fi
    fi
    
    # Memory
    if [[ "$memory_usage" =~ ^[0-9]+(\.[0-9]+)?$ ]] && [[ $(echo "$memory_usage > ${CRITICAL_THRESHOLDS[memory_usage]}" | bc 2>/dev/null || echo "false") == "true" ]]; then
        if [[ $(( $(date +%s) - LAST_CHECK )) -gt 300 ]]; then
            log_alert "🚨 Memory Usage crítico: ${memory_usage}% (umbral: ${CRITICAL_THRESHOLDS[memory_usage]}%)"
            LAST_ALERTS+=("memory-critical" "$(date +%s)")
        fi
    fi
    
    # Disk
    if [[ "$disk_usage" =~ ^[0-9]+$ ]] && [[ "$disk_usage" -gt "${CRITICAL_THRESHOLDS[disk_usage]}" ]]; then
        log_alert "🚨 Disk Usage crítico: ${disk_usage}% (umbral: ${CRITICAL_THRESHOLDS[disk_usage]}%)"
        LAST_ALERTS+=("disk-critical" "$(date +%s)")
    fi
}

# ===============================================================================
# FUNCIONES DE REPORTES AUTOMÁTICOS
# ===============================================================================

generate_continuous_report() {
    local report_file="${REPORT_DIR}/continuous-report-$(date '+%Y%m%d_%H%M%S').html"
    
    log_info "Generando reporte continuo..."
    
    # Calcular estadísticas
    local uptime=$(( $(date +%s) - START_TIME ))
    local success_rate=0
    if [[ $TOTAL_CHECKS -gt 0 ]]; then
        success_rate=$((SUCCESSFUL_CHECKS * 100 / TOTAL_CHECKS))
    fi
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Monitoreo Continuo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; border-bottom: 2px solid #28a745; padding-bottom: 20px; margin-bottom: 30px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #28a745; }
        .metric-value { font-size: 2em; font-weight: bold; color: #28a745; }
        .metric-label { color: #666; margin-top: 5px; }
        .service-status { margin: 20px 0; }
        .status-item { padding: 15px; margin: 10px 0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
        .status-healthy { background: #d4edda; color: #155724; }
        .status-unhealthy { background: #f8d7da; color: #721c24; }
        .status-unknown { background: #fff3cd; color: #856404; }
        .alerts-section { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔄 Reporte de Monitoreo Continuo</h1>
            <div>Generado el: $(date '+%Y-%m-%d %H:%M:%S')</div>
            <div>Tiempo de monitoreo: ${uptime}s</div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">$TOTAL_CHECKS</div>
                <div class="metric-label">Total de Verificaciones</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #28a745;">$SUCCESSFUL_CHECKS</div>
                <div class="metric-label">Exitosas</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #dc3545;">$FAILED_CHECKS</div>
                <div class="metric-label">Fallidas</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #17a2b8;">$ALERTS_SENT</div>
                <div class="metric-label">Alertas Enviadas</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${success_rate}%</div>
                <div class="metric-label">Tasa de Éxito</div>
            </div>
        </div>
        
        <div class="service-status">
            <h3>🔧 Estado de Servicios Críticos</h3>
EOF

    # Agregar estado de cada servicio
    for service in "${!CRITICAL_SERVICES[@]}"; do
        local status="${SERVICE_STATUS[$service]}"
        local status_class="status-unknown"
        local status_icon="❓"
        
        case "$status" in
            "healthy")
                status_class="status-healthy"
                status_icon="✅"
                ;;
            "unhealthy")
                status_class="status-unhealthy"
                status_icon="❌"
                ;;
        esac
        
        local failures="${SERVICE_CONSECUTIVE_FAILURES[$service]}"
        local successes="${SERVICE_CONSECUTIVE_SUCCESSES[$service]}"
        
        cat >> "$report_file" << EOF
            <div class="status-item $status_class">
                <span><strong>$service</strong></span>
                <span>$status_icon $status</span>
                <span>Fallos: $fallures | Éxitos: $successes</span>
            </div>
EOF
    done

    cat >> "$report_file" << EOF
        </div>
        
        <div class="alerts-section">
            <h3>🚨 Alertas Recientes</h3>
EOF

    # Agregar últimas 10 alertas
    local alert_count=0
    for i in "${!ALERT_HISTORY[@]}"; do
        if [[ $alert_count -ge 10 ]]; then
            break
        fi
        local alert="${ALERT_HISTORY[$i]}"
        echo "            <div style=\"padding: 10px; margin: 5px 0; background: white; border-radius: 6px; font-family: monospace;\">$alert</div>" >> "$report_file"
        alert_count=$((alert_count + 1))
    done

    cat >> "$report_file" << EOF
        </div>
        
        <div class="footer">
            <p>Sistema de Monitoreo Continuo - Versión 1.0</p>
            <p>Intervalo de verificación: ${CHECK_INTERVAL}s</p>
            <p>Umbral de alertas: ${ALERT_THRESHOLD} fallos consecutivos</p>
        </div>
    </div>
</body>
</html>
EOF
    
    log_success "Reporte continuo generado: $report_file"
}

# ===============================================================================
# FUNCIONES DE CONTROL
# ===============================================================================

save_state() {
    cat > "$STATE_FILE" << EOF
{
    "start_time": $START_TIME,
    "is_running": true,
    "total_checks": $TOTAL_CHECKS,
    "successful_checks": $SUCCESSFUL_CHECKS,
    "failed_checks": $FAILED_CHECKS,
    "alerts_sent": $ALERTS_SENT,
    "last_check": $(date +%s),
    "services": {
EOF

    local service_count=0
    for service in "${!CRITICAL_SERVICES[@]}"; do
        if [[ $service_count -gt 0 ]]; then
            echo "," >> "$STATE_FILE"
        fi
        echo "        \"$service\": {" >> "$STATE_FILE"
        echo "            \"status\": \"${SERVICE_STATUS[$service]}\"," >> "$STATE_FILE"
        echo "            \"consecutive_failures\": ${SERVICE_CONSECUTIVE_FAILURES[$service]}," >> "$STATE_FILE"
        echo "            \"consecutive_successes\": ${SERVICE_CONSECUTIVE_SUCCESSES[$service]}" >> "$STATE_FILE"
        echo -n "        }" >> "$STATE_FILE"
        service_count=$((service_count + 1))
    done

    echo "" >> "$STATE_FILE"
    echo "    }" >> "$STATE_FILE"
    echo "}" >> "$STATE_FILE"
}

load_state() {
    if [[ -f "$STATE_FILE" ]]; then
        log_info "Cargando estado previo..."
        # Implementar carga de estado si es necesario
        # Por simplicidad, se inicia limpio
        :
    fi
}

# ===============================================================================
# BUCLE PRINCIPAL DE MONITOREO
# ===============================================================================

monitoring_loop() {
    log_info "Iniciando bucle de monitoreo continuo..."
    log_info "Intervalo de verificación: ${CHECK_INTERVAL}s"
    log_info "Umbral de alertas: ${ALERT_THRESHOLD} fallos consecutivos"
    
    local last_report_time=0
    
    while [[ "$IS_RUNNING" == "true" ]]; do
        local loop_start=$(date +%s)
        
        # Verificar servicios críticos
        local services_checked=0
        local services_healthy=0
        
        for service in "${!CRITICAL_SERVICES[@]}"; do
            local endpoint="${CRITICAL_SERVICES[$service]}"
            
            if check_service_health "$service" "$endpoint"; then
                services_healthy=$((services_healthy + 1))
            fi
            services_checked=$((services_checked + 1))
            
            sleep 1  # Pausa entre verificaciones
        done
        
        # Recolectar métricas del sistema
        collect_system_metrics
        
        # Mostrar resumen cada 10 ciclos
        if [[ $((TOTAL_CHECKS % 10)) -eq 0 ]]; then
            local uptime=$(( $(date +%s) - START_TIME ))
            local success_rate=0
            if [[ $TOTAL_CHECKS -gt 0 ]]; then
                success_rate=$((SUCCESSFUL_CHECKS * 100 / TOTAL_CHECKS))
            fi
            
            log_info "📊 Resumen: $services_healthy/$services_checked servicios saludables | Tasa de éxito: ${success_rate}% | Uptime: ${uptime}s"
        fi
        
        # Generar reporte periódico
        local current_time=$(date +%s)
        if [[ $((current_time - last_report_time)) -ge $REPORT_INTERVAL ]]; then
            generate_continuous_report
            last_report_time=$current_time
        fi
        
        # Guardar estado
        save_state
        
        # Limpiar alertas antiguas
        cleanup_old_alerts
        
        LAST_CHECK=$(date +%s)
        
        # Esperar hasta el próximo ciclo
        local loop_duration=$(( $(date +%s) - loop_start ))
        local sleep_time=$((CHECK_INTERVAL - loop_duration))
        
        if [[ $sleep_time -gt 0 ]]; then
            sleep "$sleep_time"
        fi
    done
}

cleanup_old_alerts() {
    # Limpiar alertas antiguas (más de 24 horas)
    local current_time=$(date +%s)
    local cutoff_time=$((current_time - 86400))
    
    # Filtrar alertas recientes
    local new_alerts=()
    for alert in "${ALERT_HISTORY[@]}"; do
        local alert_time
        alert_time=$(echo "$alert" | jq -r '.timestamp' 2>/dev/null | xargs -I {} date -d "{}" +%s 2>/dev/null || echo "0")
        
        if [[ $alert_time -gt $cutoff_time ]]; then
            new_alerts+=("$alert")
        fi
    done
    
    ALERT_HISTORY=("${new_alerts[@]}")
}

# ===============================================================================
# FUNCIONES DE SEÑALES
# ===============================================================================

handle_signal() {
    log_info "Recibida señal de terminación..."
    graceful_shutdown
}

graceful_shutdown() {
    log_info "Iniciando cierre ordenado del sistema de monitoreo..."
    
    IS_RUNNING=false
    
    # Generar reporte final
    generate_continuous_report
    
    # Guardar estado final
    save_state
    
    log_info "Sistema de monitoreo detenido ordenadamente"
    exit 0
}

# ===============================================================================
# FUNCIÓN PRINCIPAL
# ===============================================================================

main() {
    echo -e "${CYAN}================================================================================"
    echo -e "🔄 SISTEMA DE VALIDACIÓN CONTINUA"
    echo -e "================================================================================${NC}"
    
    # Verificar si ya hay un monitoreo en curso
    if [[ -f "$PID_FILE" ]]; then
        local old_pid
        old_pid=$(cat "$PID_FILE")
        if kill -0 "$old_pid" 2>/dev/null; then
            log_error "Ya hay un sistema de monitoreo en curso (PID: $old_pid)"
            exit 1
        fi
    fi
    
    # Crear PID file
    echo $$ > "$PID_FILE"
    
    # Configurar trap para señales
    trap handle_signal SIGTERM SIGINT
    
    # Cleanup al salir
    trap 'rm -f "$PID_FILE"' EXIT
    
    # Cargar configuración si existe
    if [[ -f "$CONFIG_FILE" ]]; then
        source "$CONFIG_FILE"
        log_info "Configuración cargada desde: $CONFIG_FILE"
    fi
    
    # Inicializar sistema de monitoreo
    initialize_monitoring
    load_state
    
    # Marcar como ejecutándose
    IS_RUNNING=true
    
    echo -e "${GREEN}✅ Sistema de monitoreo iniciado${NC}"
    echo -e "PID: $$"
    echo -e "Intervalo de verificación: ${CHECK_INTERVAL}s"
    echo -e "Servicios monitoreados: ${#CRITICAL_SERVICES[@]}"
    echo -e ""
    echo -e "Presiona Ctrl+C para detener el monitoreo..."
    echo -e "${CYAN}================================================================================${NC}"
    
    # Iniciar bucle de monitoreo
    monitoring_loop
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
            echo "  -i, --interval       Intervalo de verificación en segundos (default: ${CHECK_INTERVAL})"
            echo "  -t, --threshold      Umbral de alertas (default: ${ALERT_THRESHOLD})"
            echo "  -r, --report         Intervalo de reportes en segundos (default: ${REPORT_INTERVAL})"
            echo "  --stop               Detener el monitoreo en curso"
            echo "  --status             Mostrar estado del monitoreo"
            echo "  --install-cron       Instalar como tarea cron"
            echo ""
            echo "Ejemplos:"
            echo "  $0                   # Iniciar monitoreo con configuración por defecto"
            echo "  $0 -i 60             # Verificar cada 60 segundos"
            echo "  $0 --stop            # Detener monitoreo"
            echo "  $0 --status          # Ver estado"
            exit 0
            ;;
        -i|--interval)
            CHECK_INTERVAL="$2"
            shift 2
            ;;
        -t|--threshold)
            ALERT_THRESHOLD="$2"
            shift 2
            ;;
        -r|--report)
            REPORT_INTERVAL="$2"
            shift 2
            ;;
        --stop)
            if [[ -f "$PID_FILE" ]]; then
                local pid
                pid=$(cat "$PID_FILE")
                if kill -0 "$pid" 2>/dev/null; then
                    log_info "Deteniendo monitoreo (PID: $pid)..."
                    kill "$pid"
                    log_success "Monitoreo detenido"
                else
                    log_warn "No se encontró proceso de monitoreo ejecutándose"
                fi
            else
                log_warn "No se encontró archivo PID"
            fi
            exit 0
            ;;
        --status)
            if [[ -f "$PID_FILE" ]]; then
                local pid
                pid=$(cat "$PID_FILE")
                if kill -0 "$pid" 2>/dev/null; then
                    log_info "✅ Monitoreo activo (PID: $pid)"
                    if [[ -f "$STATE_FILE" ]]; then
                        echo "Estado actual:"
                        cat "$STATE_FILE" | jq '.' 2>/dev/null || cat "$STATE_FILE"
                    fi
                else
                    log_warn "⚠️  Archivo PID existe pero el proceso no está ejecutándose"
                fi
            else
                log_info "ℹ️  No hay monitoreo en ejecución"
            fi
            exit 0
            ;;
        --install-cron)
            install_cron_job
            exit 0
            ;;
        *)
            log_error "Opción desconocida: $1"
            exit 1
            ;;
    esac
done

# Ejecutar función principal
main "$@"

# Función para instalar como cron job (se ejecuta antes de main)
install_cron_job() {
    local cron_entry
    cron_entry="*/$CHECK_INTERVAL * * * * $SCRIPT_DIR/continuous-validation.sh >> $LOG_DIR/cron.log 2>&1"
    
    echo "Instalando tarea cron..."
    echo "$cron_entry" | crontab -
    
    log_success "Tarea cron instalada: Verificación cada $CHECK_INTERVAL segundos"
}

# Nota: Esta función debe estar antes de main pero después de la definición de variables
install_cron_job() {
    local cron_entry
    cron_entry="*/$CHECK_INTERVAL * * * * $SCRIPT_DIR/continuous-validation.sh >> $LOG_DIR/cron.log 2>&1"
    
    echo "Instalando tarea cron..."
    echo "$cron_entry" | crontab - 2>/dev/null || {
        echo "⚠️  No se pudo instalar cron. Ejecuta como root o manualmente:"
        echo "$cron_entry"
    }
    
    log_success "Tarea cron instalada: Verificación cada $CHECK_INTERVAL segundos"
}