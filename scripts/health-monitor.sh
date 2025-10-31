#!/bin/bash

###############################################################################
# Script: health-monitor.sh
# Descripción: Sistema de monitoreo continuo de salud de aplicaciones
# Autor: Sistema de Validación Continua
# Fecha: 2025-10-30
###############################################################################

set -euo pipefail

# Configuración por defecto
DEFAULT_INTERVAL=60
DEFAULT_DURATION=3600
DEFAULT_ALERT_THRESHOLD=3
DEFAULT_METRICS_RETENTION=24
LOG_FILE="health-monitor-$(date +%Y%m%d-%H%M%S).log"
METRICS_FILE="health-metrics-$(date +%Y%m%d-%H%M%S).json"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Estados de salud
HEALTHY="healthy"
WARNING="warning"
CRITICAL="critical"
UNKNOWN="unknown"

# Función para logging
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    log "INFO" "${BLUE}$@${NC}"
}

log_success() {
    log "SUCCESS" "${GREEN}$@${NC}"
}

log_warning() {
    log "WARNING" "${YELLOW}$@${NC}"
}

log_error() {
    log "ERROR" "${RED}$@${NC}"
}

log_critical() {
    log "CRITICAL" "${RED}$@${NC}"
}

# Función para mostrar ayuda
show_help() {
    cat << EOF
Uso: $0 [OPCIONES]

OPCIONES:
    -e, --environment ENV       Entorno a monitorear
    -i, --interval SECONDS      Intervalo entre checks (default: 60)
    -d, --duration SECONDS      Duración total del monitoreo (default: 3600)
    -a, --alert-threshold NUM   Threshold de alertas consecutivas (default: 3)
    -r, --metrics-retention HRS Retención de métricas en horas (default: 24)
    --config FILE              Archivo de configuración personalizado
    --endpoints FILE           Archivo con endpoints a monitorear
    --slack-webhook URL        Webhook de Slack para alertas
    --email-to EMAIL           Email para alertas críticas
    -v, --verbose              Modo verboso
    -h, --help                 Mostrar esta ayuda

EJEMPLOS:
    $0 --environment production --interval 30
    $0 --environment staging --duration 7200 --alert-threshold 5
    $0 --environment production --slack-webhook \$SLACK_WEBHOOK_URL

EOF
}

# Variables globales
ENVIRONMENT=""
INTERVAL=$DEFAULT_INTERVAL
DURATION=$DEFAULT_DURATION
ALERT_THRESHOLD=$DEFAULT_ALERT_THRESHOLD
METRICS_RETENTION=$DEFAULT_METRICS_RETENTION
CONFIG_FILE="config/validation-config.yml"
ENDPOINTS_FILE=""
SLACK_WEBHOOK=""
EMAIL_TO=""
VERBOSE=false

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -i|--interval)
            INTERVAL="$2"
            shift 2
            ;;
        -d|--duration)
            DURATION="$2"
            shift 2
            ;;
        -a|--alert-threshold)
            ALERT_THRESHOLD="$2"
            shift 2
            ;;
        -r|--metrics-retention)
            METRICS_RETENTION="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --endpoints)
            ENDPOINTS_FILE="$2"
            shift 2
            ;;
        --slack-webhook)
            SLACK_WEBHOOK="$2"
            shift 2
            ;;
        --email-to)
            EMAIL_TO="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validar argumentos requeridos
if [[ -z "$ENVIRONMENT" ]]; then
    log_error "El entorno es requerido"
    show_help
    exit 1
fi

# Función para cargar configuración
load_config() {
    log_info "Cargando configuración de monitoreo"
    
    if [[ -f "$CONFIG_FILE" ]]; then
        # Extraer endpoints del archivo de configuración
        local health_endpoints=$(grep -A 10 "^  $ENVIRONMENT:" "$CONFIG_FILE" | grep "health_endpoints:" -A 5 | tail -5 || echo "")
        if [[ -n "$health_endpoints" ]]; then
            log_info "Configuración cargada para entorno: $ENVIRONMENT"
        fi
    fi
    
    # Cargar endpoints personalizados
    if [[ -n "$ENDPOINTS_FILE" && -f "$ENDPOINTS_FILE" ]]; then
        log_info "Cargando endpoints desde: $ENDPOINTS_FILE"
    fi
}

# Función para obtener endpoints de monitoreo
get_monitoring_endpoints() {
    local endpoints=()
    
    # Endpoint base de salud
    endpoints+=("http://localhost:8080/health")
    
    # API status
    endpoints+=("http://localhost:8080/api/v1/status")
    
    # Métricas
    endpoints+=("http://localhost:8080/api/v1/metrics")
    
    # Readiness probe
    endpoints+=("http://localhost:8080/ready")
    
    # Liveness probe
    endpoints+=("http://localhost:8080/live")
    
    # Endpoint personalizado si se proporciona archivo
    if [[ -n "$ENDPOINTS_FILE" && -f "$ENDPOINTS_FILE" ]]; then
        while IFS= read -r line; do
            # Skip comments and empty lines
            [[ "$line" =~ ^[[:space:]]*# ]] && continue
            [[ -z "${line// }" ]] && continue
            endpoints+=("$line")
        done < "$ENDPOINTS_FILE"
    fi
    
    echo "${endpoints[@]}"
}

# Función para medir latencia de endpoint
measure_latency() {
    local url=$1
    local start_time=$(date +%s%3N)
    
    if curl -s -f "$url" > /dev/null; then
        local end_time=$(date +%s%3N)
        local latency=$((end_time - start_time))
        echo "$latency"
    else
        echo "0"
    fi
}

# Función para verificar endpoint de salud
check_health_endpoint() {
    local url=$1
    local endpoint_name=$(basename "$url")
    
    if [[ "$VERBOSE" == true ]]; then
        log_info "Verificando endpoint: $url"
    fi
    
    # Verificar disponibilidad básica
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" "$url" --max-time 10 || echo "000")
    
    if [[ "$http_status" == "200" ]]; then
        # Medir latencia
        local latency=$(measure_latency "$url")
        
        # Verificar latencia contra thresholds
        local status=$HEALTHY
        if [[ $latency -gt 5000 ]]; then
            status=$CRITICAL
        elif [[ $latency -gt 2000 ]]; then
            status=$WARNING
        fi
        
        echo "$status|$latency|$http_status"
    else
        echo "$CRITICAL|0|$http_status"
    fi
}

# Función para verificar servicios de infraestructura
check_infrastructure_services() {
    log_info "Verificando servicios de infraestructura"
    
    local infrastructure_status=0
    
    # Base de datos
    if docker-compose -f docker-compose.validation.yml exec -T database pg_isready -U postgres > /dev/null 2>&1; then
        log_success "Base de datos: OK"
    else
        log_error "Base de datos: FAIL"
        ((infrastructure_status++))
    fi
    
    # Redis
    if docker-compose -f docker-compose.validation.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis: OK"
    else
        log_error "Redis: FAIL"
        ((infrastructure_status++))
    fi
    
    # RabbitMQ
    if docker-compose -f docker-compose.validation.yml exec -T rabbitmq rabbitmqctl status > /dev/null 2>&1; then
        log_success "RabbitMQ: OK"
    else
        log_error "RabbitMQ: FAIL"
        ((infrastructure_status++))
    fi
    
    return $infrastructure_status
}

# Función para verificar recursos del sistema
check_system_resources() {
    local status=0
    
    # Uso de CPU
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    local cpu_int=${cpu_usage%.*}
    if [[ $cpu_int -gt 90 ]]; then
        log_warning "CPU usage alto: ${cpu_int}%"
        status=1
    else
        log_info "CPU usage: ${cpu_int}%"
    fi
    
    # Uso de memoria
    local mem_info=$(free | grep Mem)
    local mem_total=$(echo $mem_info | awk '{print $2}')
    local mem_used=$(echo $mem_info | awk '{print $3}')
    local mem_percent=$((mem_used * 100 / mem_total))
    
    if [[ $mem_percent -gt 90 ]]; then
        log_warning "Memory usage alto: ${mem_percent}%"
        status=1
    else
        log_info "Memory usage: ${mem_percent}%"
    fi
    
    # Uso de disco
    local disk_usage=$(df -h . | awk 'NR==2{print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 90 ]]; then
        log_warning "Disk usage alto: ${disk_usage}%"
        status=1
    else
        log_info "Disk usage: ${disk_usage}%"
    fi
    
    return $status
}

# Función para registrar métrica
record_metric() {
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local metric_name=$1
    local metric_value=$2
    local metric_unit=${3:-"count"}
    
    # Agregar a archivo de métricas
    echo "{\"timestamp\": \"$timestamp\", \"metric\": \"$metric_name\", \"value\": $metric_value, \"unit\": \"$metric_unit\", \"environment\": \"$ENVIRONMENT\"}" >> "$METRICS_FILE.tmp"
}

# Función para enviar alerta
send_alert() {
    local severity=$1
    local message=$2
    
    log_error "ALERT [$severity]: $message"
    
    # Alerta por Slack
    if [[ -n "$SLACK_WEBHOOK" ]]; then
        local emoji=""
        case $severity in
            "CRITICAL") emoji="🚨" ;;
            "WARNING") emoji="⚠️" ;;
            "INFO") emoji="ℹ️" ;;
        esac
        
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$emoji [$severity] $ENVIRONMENT: $message\"}" \
            "$SLACK_WEBHOOK" 2>/dev/null || log_warning "No se pudo enviar alerta a Slack"
    fi
    
    # Alerta por email (solo para críticos)
    if [[ "$severity" == "CRITICAL" && -n "$EMAIL_TO" ]]; then
        echo "$message" | mail -s "ALERTA CRÍTICA - $ENVIRONMENT" "$EMAIL_TO" 2>/dev/null || \
            log_warning "No se pudo enviar email de alerta"
    fi
}

# Función para generar reporte de salud
generate_health_report() {
    local elapsed=$1
    local total_checks=$2
    local failed_checks=$3
    local average_latency=$4
    
    local report_file="health-report-$(date +%Y%m%d-%H%M%S).html"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Health Report - $ENVIRONMENT</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .success { color: green; }
        .warning { color: orange; }
        .critical { color: red; }
        .metric { margin: 10px 0; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Health Report - $ENVIRONMENT</h1>
        <p>Generated: $(date)</p>
        <p>Duration: ${elapsed} seconds</p>
    </div>
    
    <h2>Summary</h2>
    <div class="metric">
        <strong>Total Checks:</strong> $total_checks<br>
        <strong>Failed Checks:</strong> $failed_checks<br>
        <strong>Success Rate:</strong> $(( (total_checks - failed_checks) * 100 / total_checks ))%<br>
        <strong>Average Latency:</strong> ${average_latency}ms<br>
    </div>
    
    <h2>Health Status</h2>
    <table>
        <tr><th>Timestamp</th><th>Service</th><th>Status</th><th>Latency</th><th>HTTP Code</th></tr>
EOF
    
    # Agregar datos de métricas
    if [[ -f "$METRICS_FILE.tmp" ]]; then
        while IFS= read -r line; do
            echo "$line" | jq -r '|
                "<tr><td>" + .timestamp + "</td><td>" + 
                .metric + "</td><td>" + 
                (if .value == 0 then "CRITICAL" else "HEALTHY" end) + "</td><td>" + 
                (.value | tostring) + "ms</td><td>" + 
                (if .value == 0 then "000" else "200" end) + "</td></tr>"
            ' >> "$report_file" 2>/dev/null || true
        done < "$METRICS_FILE.tmp"
    fi
    
    cat >> "$report_file" << EOF
    </table>
</body>
</html>
EOF
    
    log_info "Reporte generado: $report_file"
    echo "$report_file"
}

# Función principal de monitoreo
monitor_health() {
    log_info "Iniciando monitoreo continuo"
    log_info "Entorno: $ENVIRONMENT"
    log_info "Interval: ${INTERVAL}s, Duration: ${DURATION}s"
    
    local endpoints=($(get_monitoring_endpoints))
    local start_time=$(date +%s)
    local end_time=$((start_time + DURATION))
    local current_time
    local check_count=0
    local failed_checks=0
    local total_latency=0
    local consecutive_failures=0
    
    # Limpiar archivo temporal de métricas
    > "$METRICS_FILE.tmp"
    
    while [[ $(date +%s) -lt $end_time ]]; do
        current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        log_info "=== Ciclo de monitoreo $((check_count + 1)) (${elapsed}s elapsed) ==="
        
        local cycle_failed=0
        
        # Verificar cada endpoint
        for endpoint in "${endpoints[@]}"; do
            local result=$(check_health_endpoint "$endpoint")
            local status=$(echo "$result" | cut -d'|' -f1)
            local latency=$(echo "$result" | cut -d'|' -f2)
            local http_code=$(echo "$result" | cut -d'|' -f3)
            
            local endpoint_name=$(basename "$endpoint")
            
            case $status in
                "$HEALTHY")
                    log_success "$endpoint_name: HEALTHY (${latency}ms)"
                    consecutive_failures=0
                    ((total_latency += latency))
                    ;;
                "$WARNING")
                    log_warning "$endpoint_name: WARNING (${latency}ms)"
                    ((cycle_failed++))
                    ((total_latency += latency))
                    ;;
                "$CRITICAL")
                    log_error "$endpoint_name: CRITICAL (HTTP: $http_code)"
                    ((cycle_failed++))
                    ((failed_checks++))
                    ((consecutive_failures++))
                    
                    if [[ $consecutive_failures -ge $ALERT_THRESHOLD ]]; then
                        send_alert "CRITICAL" "Endpoint $endpoint_name fallando consecutivamente ($consecutive_failures times)"
                    fi
                    ;;
            esac
            
            # Registrar métrica
            record_metric "health_check_latency" "$latency" "milliseconds"
            record_metric "health_check_status" "$(echo $status | tr '[:lower:]' '[:upper:]')" "status"
            
            ((check_count++))
        done
        
        # Verificar infraestructura
        local infra_failures=0
        if ! check_infrastructure_services; then
            ((infra_failures++))
            send_alert "CRITICAL" "Servicios de infraestructura fallando"
        fi
        
        # Verificar recursos del sistema
        if ! check_system_resources; then
            send_alert "WARNING" "Alto uso de recursos del sistema"
        fi
        
        # Determinar estado general del ciclo
        if [[ $cycle_failed -gt 0 ]]; then
            log_warning "Ciclo $((check_count + 1)): $cycle_failed endpoints con problemas"
        else
            log_success "Ciclo $((check_count + 1)): Todos los endpoints saludables"
        fi
        
        # Esperar al próximo ciclo
        if [[ $(date +%s) -lt $end_time ]]; then
            log_info "Esperando ${INTERVAL}s para el próximo ciclo..."
            sleep "$INTERVAL"
        fi
    done
    
    # Calcular estadísticas finales
    local total_time=$((end_time - start_time))
    local average_latency=0
    if [[ $check_count -gt 0 ]]; then
        average_latency=$((total_latency / check_count))
    fi
    
    # Generar reporte final
    local report_file=$(generate_health_report "$total_time" "$check_count" "$failed_checks" "$average_latency")
    
    # Limpiar archivo temporal
    if [[ -f "$METRICS_FILE.tmp" ]]; then
        mv "$METRICS_FILE.tmp" "$METRICS_FILE"
    fi
    
    log_info "============================================"
    log_info "MONITOREO COMPLETADO"
    log_info "Duración: ${total_time}s"
    log_info "Total checks: $check_count"
    log_info "Checks fallidos: $failed_checks"
    log_info "Tasa de éxito: $(( (check_count - failed_checks) * 100 / check_count ))%"
    log_info "Latencia promedio: ${average_latency}ms"
    log_info "Reporte: $report_file"
    log_info "Métricas: $METRICS_FILE"
    log_info "============================================"
    
    # Cleanup de métricas antiguas
    find . -name "health-metrics-*.json" -mtime +1 -delete 2>/dev/null || true
    
    # Retornar código de éxito si no hay fallos críticos
    if [[ $failed_checks -eq 0 ]]; then
        return 0
    else
        return 1
    fi
}

# Función para cleanup
cleanup() {
    log_info "Ejecutando cleanup de monitoreo..."
    
    # Limpiar archivo temporal si existe
    [[ -f "$METRICS_FILE.tmp" ]] && rm -f "$METRICS_FILE.tmp"
    
    # Aquí puedes agregar más cleanup de recursos temporales
}

# Manejo de señales
trap cleanup EXIT

# Verificar prerrequisitos
check_prerequisites() {
    log_info "Verificando prerrequisitos..."
    
    local missing_tools=()
    
    for tool in curl docker-compose jq; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Herramientas faltantes: ${missing_tools[*]}"
        exit 1
    fi
    
    log_success "Prerrequisitos verificados"
}

# Función principal
main() {
    log_info "============================================"
    log_info "SISTEMA DE MONITOREO CONTINUO"
    log_info "Fecha: $(date)"
    log_info "Entorno: $ENVIRONMENT"
    log_info "Intervalo: ${INTERVAL}s"
    log_info "Duración: ${DURATION}s"
    log_info "Threshold de alertas: $ALERT_THRESHOLD"
    log_info "============================================"
    
    # Verificar prerrequisitos
    check_prerequisites
    
    # Cargar configuración
    load_config
    
    # Ejecutar monitoreo
    if monitor_health; then
        log_success "MONITOREO COMPLETADO EXITOSAMENTE"
        exit 0
    else
        log_error "MONITOREO COMPLETADO CON FALLOS"
        exit 1
    fi
}

# Ejecutar función principal
main "$@"