#!/bin/bash

# ===============================================================================
# SCRIPT DE GENERACIÓN DE REPORTES DEL SISTEMA
# ===============================================================================
# Funcionalidades:
# - Consolidación de logs y métricas del sistema
# - Generación de reportes ejecutivos detallados
# - Análisis de tendencias y patrones
# - Alertas y recomendaciones automatizadas
# - Exportación en múltiples formatos (HTML, JSON, CSV)
# ===============================================================================

set -euo pipefail

# Configuración global
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
REPORT_DIR="${SCRIPT_DIR}/reports"
TMP_DIR="/tmp/system-report-$$"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
DATE_RANGE="${1:-24h}"  # Default: últimas 24 horas
LOG_FILE="${LOG_DIR}/system-report_${TIMESTAMP}.log"
REPORT_FILE="${REPORT_DIR}/system-report_${TIMESTAMP}.html"
REPORT_JSON="${REPORT_DIR}/system-report_${TIMESTAMP}.json"
REPORT_CSV="${REPORT_DIR}/system-report_${TIMESTAMP}.csv"
PID_FILE="/tmp/system-report.pid"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Configuración del reporte
REPORT_TITLE="Reporte Ejecutivo del Sistema"
REPORT_VERSION="1.0"
TIMEZONE="America/Lima"
RETENTION_DAYS=30

# Variables de estado
REPORT_GENERATED=false
TOTAL_SECTIONS=0
SECTIONS_COMPLETED=0
ERRORS_COUNT=0
WARNINGS_COUNT=0

# Estructura del reporte
declare -A REPORT_SECTIONS
REPORT_SECTIONS[summary]="Resumen Ejecutivo"
REPORT_SECTIONS[health]="Salud del Sistema"
REPORT_SECTIONS[performance]="Análisis de Rendimiento"
REPORT_SECTIONS[logs]="Análisis de Logs"
REPORT_SECTIONS[errors]="Errores y Alertas"
REPORT_SECTIONS[recommendations]="Recomendaciones"
REPORT_SECTIONS[trends]="Tendencias y Patrones"

# Métricas del sistema
declare -A SYSTEM_METRICS
SYSTEM_METRICS[uptime]=""
SYSTEM_METRICS[cpu_usage]=""
SYSTEM_METRICS[memory_usage]=""
SYSTEM_METRICS[disk_usage]=""
SYSTEM_METRICS[network_io]=""
SYSTEM_METRICS[active_connections]=""
SYSTEM_METRICS[service_count]=""
SYSTEM_METRICS[error_rate]=""

# Datos de servicios
declare -A SERVICE_DATA
SERVICE_DATA[lp1_banco_status]=""
SERVICE_DATA[lp2_reniec_status]=""
SERVICE_DATA[rabbitmq_status]=""
SERVICE_DATA[redis_status]=""
SERVICE_DATA[postgres_status]=""
SERVICE_DATA[mysql_status]=""

# Arrays para datos detallados
declare -a ERROR_LOG_ENTRIES
declare -a WARNING_LOG_ENTRIES
declare -a PERFORMANCE_DATA
declare -a TREND_DATA

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
log_report() { log "REPORT" "$@"; }

initialize_logging() {
    mkdir -p "$LOG_DIR" "$REPORT_DIR"
    
    cat > "$LOG_FILE" << EOF
================================================================================
GENERACIÓN DE REPORTE DEL SISTEMA - INICIADO
Timestamp: $(date '+%Y-%m-%d %H:%M:%S')
Script: $0
Rango de fechas: $DATE_RANGE
================================================================================

EOF
    log_info "Sistema de logging inicializado: $LOG_FILE"
}

# ===============================================================================
# UTILIDADES DE RECOLECCIÓN DE DATOS
# ===============================================================================

collect_system_metrics() {
    log_report "Recolectando métricas del sistema..."
    
    TOTAL_SECTIONS=$((TOTAL_SECTIONS + 1))
    
    # Uptime
    if [[ -f /proc/uptime ]]; then
        local uptime_seconds
        uptime_seconds=$(awk '{print $1}' /proc/uptime)
        SYSTEM_METRICS[uptime]="$uptime_seconds"
    fi
    
    # CPU Usage
    if command -v top >/dev/null 2>&1; then
        local cpu_usage
        cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}' | tr -d ' ')
        SYSTEM_METRICS[cpu_usage]="$cpu_usage"
    fi
    
    # Memory Usage
    if command -v free >/dev/null 2>&1; then
        local mem_usage
        mem_usage=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
        SYSTEM_METRICS[memory_usage]="$mem_usage"
    fi
    
    # Disk Usage
    local disk_usage
    disk_usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    SYSTEM_METRICS[disk_usage]="$disk_usage"
    
    # Network I/O
    if [[ -f /proc/net/dev ]]; then
        # Sumar RX y TX bytes (simplificado)
        local rx_bytes tx_bytes
        rx_bytes=$(awk 'NR>2 {rx += $2} END {print rx}' /proc/net/dev)
        tx_bytes=$(awk 'NR>2 {tx += $10} END {print tx}' /proc/net/dev)
        SYSTEM_METRICS[network_io]="RX:${rx_bytes},TX:${tx_bytes}"
    fi
    
    # Service count
    local service_count=0
    for port in 8080 8000 5672 6379 5432 3306; do
        if command -v netstat >/dev/null 2>&1 && netstat -ln | grep -q ":$port "; then
            service_count=$((service_count + 1))
        elif command -v ss >/dev/null 2>&1 && ss -ln | grep -q ":$port "; then
            service_count=$((service_count + 1))
        fi
    done
    SYSTEM_METRICS[service_count]="$service_count"
    
    log_success "Métricas del sistema recolectadas"
    SECTIONS_COMPLETED=$((SECTIONS_COMPLETED + 1))
}

collect_service_status() {
    log_report "Recolectando estado de servicios..."
    
    TOTAL_SECTIONS=$((TOTAL_SECTIONS + 1))
    
    # LP1 Banco
    if curl -s --max-time 5 "http://localhost:8080/health" >/dev/null 2>&1; then
        SERVICE_DATA[lp1_banco_status]="online"
    else
        SERVICE_DATA[lp1_banco_status]="offline"
    fi
    
    # LP2 RENIEC
    if curl -s --max-time 5 "http://localhost:8000/health" >/dev/null 2>&1; then
        SERVICE_DATA[lp2_reniec_status]="online"
    else
        SERVICE_DATA[lp2_reniec_status]="offline"
    fi
    
    # RabbitMQ
    if command -v rabbitmqadmin >/dev/null 2>&1; then
        if rabbitmqadmin list overview >/dev/null 2>&1; then
            SERVICE_DATA[rabbitmq_status]="online"
        else
            SERVICE_DATA[rabbitmq_status]="offline"
        fi
    else
        # Verificar puerto
        if command -v netstat >/dev/null 2>&1 && netstat -ln | grep -q ":5672 "; then
            SERVICE_DATA[rabbitmq_status]="online"
        else
            SERVICE_DATA[rabbitmq_status]="offline"
        fi
    fi
    
    # Redis
    if command -v redis-cli >/dev/null 2>&1 && redis-cli ping >/dev/null 2>&1; then
        SERVICE_DATA[redis_status]="online"
    else
        SERVICE_DATA[redis_status]="offline"
    fi
    
    # PostgreSQL
    if command -v pg_isready >/dev/null 2>&1 && pg_isready >/dev/null 2>&1; then
        SERVICE_DATA[postgres_status]="online"
    else
        SERVICE_DATA[postgres_status]="offline"
    fi
    
    # MySQL
    if command -v mysqladmin >/dev/null 2>&1 && mysqladmin ping >/dev/null 2>&1; then
        SERVICE_DATA[mysql_status]="online"
    else
        SERVICE_DATA[mysql_status]="offline"
    fi
    
    log_success "Estado de servicios recolectado"
    SECTIONS_COMPLETED=$((SECTIONS_COMPLETED + 1))
}

# ===============================================================================
# ANÁLISIS DE LOGS
# ===============================================================================

analyze_logs() {
    log_report "Analizando logs del sistema..."
    
    TOTAL_SECTIONS=$((TOTAL_SECTIONS + 1))
    
    # Limpiar array de errores y warnings
    ERROR_LOG_ENTRIES=()
    WARNING_LOG_ENTRIES=()
    
    # Buscar logs en diferentes ubicaciones
    local log_locations=(
        "$LOG_DIR"
        "/var/log"
        "/tmp"
    )
    
    for location in "${log_locations[@]}"; do
        if [[ -d "$location" ]]; then
            # Buscar errores en logs recientes
            while IFS= read -r line; do
                if [[ -n "$line" ]]; then
                    ERROR_LOG_ENTRIES+=("$line")
                fi
            done < <(find "$location" -name "*.log" -mtime -1 -exec grep -l -i "error\|exception\|failed" {} \; 2>/dev/null | head -10)
            
            # Buscar warnings
            while IFS= read -r line; do
                if [[ -n "$line" ]]; then
                    WARNING_LOG_ENTRIES+=("$line")
                fi
            done < <(find "$location" -name "*.log" -mtime -1 -exec grep -l -i "warning\|warn" {} \; 2>/dev/null | head -10)
        fi
    done
    
    # Contar errores y warnings únicos
    ERRORS_COUNT=$(printf '%s\n' "${ERROR_LOG_ENTRIES[@]}" | sort -u | wc -l)
    WARNINGS_COUNT=$(printf '%s\n' "${WARNING_LOG_ENTRIES[@]}" | sort -u | wc -l)
    
    log_success "Análisis de logs completado - Errores: $ERRORS_COUNT, Warnings: $WARNINGS_COUNT"
    SECTIONS_COMPLETED=$((SECTIONS_COMPLETED + 1))
}

# ===============================================================================
# ANÁLISIS DE RENDIMIENTO
# ===============================================================================

analyze_performance() {
    log_report "Analizando rendimiento del sistema..."
    
    TOTAL_SECTIONS=$((TOTAL_SECTIONS + 1))
    
    # Limpiar datos de rendimiento
    PERFORMANCE_DATA=()
    
    # Recolectar datos de rendimiento recientes
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # CPU y memoria
    local cpu_data="$timestamp,CPU,$(echo "${SYSTEM_METRICS[cpu_usage]}" | tr -d '%')"
    local mem_data="$timestamp,MEM,$(echo "${SYSTEM_METRICS[memory_usage]}" | tr -d '%')"
    local disk_data="$timestamp,DISK,${SYSTEM_METRICS[disk_usage]}"
    
    PERFORMANCE_DATA+=("$cpu_data")
    PERFORMANCE_DATA+=("$mem_data")
    PERFORMANCE_DATA+=("$disk_data")
    
    # Buscar archivos de benchmark recientes
    local benchmark_files
    benchmark_files=$(find "$REPORT_DIR" -name "*benchmark*.html" -mtime -7 2>/dev/null | head -3)
    
    if [[ -n "$benchmark_files" ]]; then
        while IFS= read -r file; do
            local basename
            basename=$(basename "$file" .html)
            log_info "Incorporando datos de benchmark: $basename"
        done <<< "$benchmark_files"
    fi
    
    log_success "Análisis de rendimiento completado"
    SECTIONS_COMPLETED=$((SECTIONS_COMPLETED + 1))
}

# ===============================================================================
# ANÁLISIS DE TENDENCIAS
# ===============================================================================

analyze_trends() {
    log_report "Analizando tendencias y patrones..."
    
    TOTAL_SECTIONS=$((TOTAL_SECTIONS + 1))
    
    # Limpiar datos de tendencias
    TREND_DATA=()
    
    # Analizar tendencias de errores (últimos 7 días)
    local error_trend=0
    for i in {1..7}; do
        local date_str
        date_str=$(date -d "$i days ago" '+%Y-%m-%d' 2>/dev/null || date -v-${i}d '+%Y-%m-%d')
        
        local daily_errors
        daily_errors=$(find "$LOG_DIR" -name "*.log" -mtime -$i -exec grep -c -i "error\|exception" {} \; 2>/dev/null | awk '{sum += $1} END {print sum}')
        
        if [[ -n "$daily_errors" && "$daily_errors" -gt 0 ]]; then
            TREND_DATA+=("$date_str,errors,$daily_errors")
        fi
    done
    
    # Analizar tendencias de uso de recursos
    if [[ -f /proc/loadavg ]]; then
        local load_avg
        load_avg=$(cat /proc/loadavg | awk '{print $1}')
        TREND_DATA+=("$(date '+%Y-%m-%d'),load,$load_avg")
    fi
    
    # Analizar disponibilidad de servicios
    local available_services=0
    local total_services=0
    for service in "${!SERVICE_DATA[@]}"; do
        total_services=$((total_services + 1))
        if [[ "${SERVICE_DATA[$service]}" == "online" ]]; then
            available_services=$((available_services + 1))
        fi
    done
    
    local availability_percentage=0
    if [[ $total_services -gt 0 ]]; then
        availability_percentage=$((available_services * 100 / total_services))
    fi
    
    TREND_DATA+=("$(date '+%Y-%m-%d'),availability,$availability_percentage")
    
    log_success "Análisis de tendencias completado"
    SECTIONS_COMPLETED=$((SECTIONS_COMPLETED + 1))
}

# ===============================================================================
# GENERACIÓN DE RECOMENDACIONES
# ===============================================================================

generate_recommendations() {
    log_report "Generando recomendaciones..."
    
    TOTAL_SECTIONS=$((TOTAL_SECTIONS + 1))
    
    local recommendations=()
    
    # Recomendaciones basadas en métricas del sistema
    local cpu_usage
    cpu_usage=$(echo "${SYSTEM_METRICS[cpu_usage]}" | tr -d '%' 2>/dev/null || echo "0")
    
    if [[ "$cpu_usage" =~ ^[0-9]+$ ]] && [[ "$cpu_usage" -gt 80 ]]; then
        recommendations+=("🔴 ALTA: El uso de CPU está al ${cpu_usage}%. Se recomienda optimizar procesos o escalar recursos.")
    elif [[ "$cpu_usage" =~ ^[0-9]+$ ]] && [[ "$cpu_usage" -gt 60 ]]; then
        recommendations+=("🟡 MEDIA: El uso de CPU está al ${cpu_usage}%. Monitorear de cerca para optimizar si es necesario.")
    fi
    
    local mem_usage
    mem_usage=$(echo "${SYSTEM_METRICS[memory_usage]}" | tr -d '%' 2>/dev/null || echo "0")
    
    if [[ "$mem_usage" =~ ^[0-9]+$ ]] && [[ "$mem_usage" -gt 85 ]]; then
        recommendations+=("🔴 ALTA: El uso de memoria está al ${mem_usage}%. Considerar aumentar memoria RAM o optimizar uso.")
    elif [[ "$mem_usage" =~ ^[0-9]+$ ]] && [[ "$mem_usage" -gt 70 ]]; then
        recommendations+=("🟡 MEDIA: El uso de memoria está al ${mem_usage}%. Revisar consumo y optimizar si es necesario.")
    fi
    
    if [[ "${SYSTEM_METRICS[disk_usage]}" =~ ^[0-9]+$ ]] && [[ "${SYSTEM_METRICS[disk_usage]}" -gt 90 ]]; then
        recommendations+=("🔴 CRÍTICA: El espacio en disco está al ${SYSTEM_METRICS[disk_usage]}%. Liberar espacio inmediatamente.")
    elif [[ "${SYSTEM_METRICS[disk_usage]}" =~ ^[0-9]+$ ]] && [[ "${SYSTEM_METRICS[disk_usage]}" -gt 80 ]]; then
        recommendations+=("🟡 MEDIA: El espacio en disco está al ${SYSTEM_METRICS[disk_usage]}%. Planificar limpieza o expansión.")
    fi
    
    # Recomendaciones basadas en servicios offline
    for service in "${!SERVICE_DATA[@]}"; do
        if [[ "${SERVICE_DATA[$service]}" == "offline" ]]; then
            local service_name
            service_name=$(echo "$service" | tr '_' ' ' | sed 's/\b\w/\U&/g')
            recommendations+=("🔴 CRÍTICA: El servicio $service_name está offline. Verificar y reiniciar el servicio.")
        fi
    done
    
    # Recomendaciones basadas en logs de errores
    if [[ $ERRORS_COUNT -gt 50 ]]; then
        recommendations+=("🔴 ALTA: Se detectaron $ERRORS_COUNT errores en los logs. Revisar y resolver errores críticos.")
    elif [[ $ERRORS_COUNT -gt 10 ]]; then
        recommendations+=("🟡 MEDIA: Se detectaron $ERRORS_COUNT errores en los logs. Monitorear y resolver si aumentan.")
    fi
    
    # Recomendaciones generales
    recommendations+=("💡 SUGERENCIA: Implementar monitoreo continuo para detectar problemas proactivamente.")
    recommendations+=("💡 SUGERENCIA: Configurar alertas automáticas para métricas críticas.")
    recommendations+=("💡 SUGERENCIA: Realizar respaldos regulares de datos críticos.")
    
    # Guardar recomendaciones para el reporte
    printf '%s\n' "${recommendations[@]}" > "$TMP_DIR/recommendations.txt"
    
    log_success "Recomendaciones generadas (${#recommendations[@]} items)"
    SECTIONS_COMPLETED=$((SECTIONS_COMPLETED + 1))
}

# ===============================================================================
# GENERACIÓN DE REPORTE HTML
# ===============================================================================

generate_html_report() {
    log_report "Generando reporte HTML ejecutivo..."
    
    # Crear directorio temporal
    mkdir -p "$TMP_DIR"
    
    # Calcular uptime formateado
    local uptime_formatted
    if [[ -n "${SYSTEM_METRICS[uptime]}" ]]; then
        local uptime_seconds
        uptime_seconds=$(echo "${SYSTEM_METRICS[uptime]}" | cut -d. -f1)
        local days=$((uptime_seconds / 86400))
        local hours=$(( (uptime_seconds % 86400) / 3600 ))
        local minutes=$(( (uptime_seconds % 3600) / 60 ))
        uptime_formatted="${days}d ${hours}h ${minutes}m"
    else
        uptime_formatted="N/A"
    fi
    
    # Determinar estado general del sistema
    local system_status="saludable"
    local status_color="green"
    
    if [[ $ERRORS_COUNT -gt 10 ]] || [[ "${SYSTEM_METRICS[disk_usage]}" =~ ^[0-9]+$ && "${SYSTEM_METRICS[disk_usage]}" -gt 90 ]]; then
        system_status="crítico"
        status_color="red"
    elif [[ $WARNINGS_COUNT -gt 5 ]] || [[ "${SYSTEM_METRICS[disk_usage]}" =~ ^[0-9]+$ && "${SYSTEM_METRICS[disk_usage]}" -gt 80 ]]; then
        system_status="advertencia"
        status_color="orange"
    fi
    
    cat > "$REPORT_FILE" << EOF
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$REPORT_TITLE - $(date '+%Y-%m-%d')</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .header { 
            text-align: center; 
            color: #333; 
            border-bottom: 3px solid #667eea; 
            padding-bottom: 20px; 
            margin-bottom: 30px; 
        }
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 25px;
            color: white;
            font-weight: bold;
            margin: 10px 0;
        }
        .status-healthy { background: #28a745; }
        .status-warning { background: #ffc107; color: #333; }
        .status-critical { background: #dc3545; }
        
        .metrics-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .metric-card { 
            background: #f8f9fa; 
            padding: 25px; 
            border-radius: 12px; 
            text-align: center; 
            border-left: 5px solid #667eea;
            transition: transform 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .metric-value { 
            font-size: 2.5em; 
            font-weight: bold; 
            color: #667eea; 
        }
        .metric-label { 
            color: #666; 
            margin-top: 8px; 
            font-size: 0.9em;
        }
        
        .content-grid { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 30px; 
            margin: 30px 0;
        }
        .content-section { 
            background: #f8f9fa; 
            padding: 25px; 
            border-radius: 12px; 
            border-left: 5px solid #17a2b8;
        }
        .content-section h3 { 
            margin-top: 0; 
            color: #333; 
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 10px;
        }
        
        .service-item { 
            padding: 12px; 
            margin: 8px 0; 
            border-radius: 8px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            font-weight: 500;
        }
        .service-online { 
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            color: #155724; 
            border: 1px solid #c3e6cb;
        }
        .service-offline { 
            background: linear-gradient(135deg, #f8d7da, #f5c6cb);
            color: #721c24; 
            border: 1px solid #f5c6cb;
        }
        
        .recommendations {
            background: linear-gradient(135deg, #e3f2fd, #bbdefb);
            padding: 25px;
            border-radius: 12px;
            margin: 30px 0;
            border-left: 5px solid #2196f3;
        }
        .recommendation-item {
            padding: 15px;
            margin: 10px 0;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #2196f3;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .footer { 
            text-align: center; 
            margin-top: 40px; 
            padding-top: 30px; 
            border-top: 2px solid #dee2e6; 
            color: #666; 
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background: #e9ecef;
            border-radius: 3px;
            overflow: hidden;
            margin: 20px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }
        
        @media (max-width: 768px) {
            .content-grid {
                grid-template-columns: 1fr;
            }
            .metrics-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <script>
        function animateProgress() {
            const progressBars = document.querySelectorAll('.progress-fill');
            progressBars.forEach(bar => {
                const width = bar.style.width;
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.width = width;
                }, 500);
            });
        }
        
        window.onload = function() {
            animateProgress();
        };
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏢 $REPORT_TITLE</h1>
            <div class="timestamp">Generado el: $(date '+%Y-%m-%d %H:%M:%S')</div>
            <div class="status-badge status-$([ "$system_status" = "saludable" ] && echo "healthy" || echo "$status_color")">
                Estado: $(echo "$system_status" | tr '[:lower:]' '[:upper:]')
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: $((SECTIONS_COMPLETED * 100 / TOTAL_SECTIONS))%"></div>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">$uptime_formatted</div>
                <div class="metric-label">Tiempo de Actividad</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${SYSTEM_METRICS[cpu_usage]:-N/A}</div>
                <div class="metric-label">Uso de CPU</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${SYSTEM_METRICS[memory_usage]:-N/A}</div>
                <div class="metric-label">Uso de Memoria</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${SYSTEM_METRICS[disk_usage]:-N/A}</div>
                <div class="metric-label">Uso de Disco</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${SYSTEM_METRICS[service_count]:-0}/6</div>
                <div class="metric-label">Servicios Activos</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">$ERRORS_COUNT</div>
                <div class="metric-label">Errores Detectados</div>
            </div>
        </div>
        
        <div class="content-grid">
            <div class="content-section">
                <h3>🔧 Estado de Servicios</h3>
EOF

    # Agregar estado de cada servicio
    for service in "${!SERVICE_DATA[@]}"; do
        local service_display
        service_display=$(echo "$service" | tr '_' ' ' | sed 's/\b\w/\U&/g')
        local status_class
        local status_icon
        if [[ "${SERVICE_DATA[$service]}" == "online" ]]; then
            status_class="service-online"
            status_icon="✅"
        else
            status_class="service-offline"
            status_icon="❌"
        fi
        
        cat >> "$REPORT_FILE" << EOF
                <div class="service-item $status_class">
                    <span>$service_display</span>
                    <span>$status_icon ${SERVICE_DATA[$service]}</span>
                </div>
EOF
    done

    cat >> "$REPORT_FILE" << EOF
            </div>
            
            <div class="content-section">
                <h3>📊 Análisis de Logs</h3>
                <div style="padding: 15px; margin: 10px 0; background: white; border-radius: 8px;">
                    <strong>🔴 Errores:</strong> $ERRORS_COUNT entradas
                </div>
                <div style="padding: 15px; margin: 10px 0; background: white; border-radius: 8px;">
                    <strong>🟡 Warnings:</strong> $WARNINGS_COUNT entradas
                </div>
                <div style="padding: 15px; margin: 10px 0; background: white; border-radius: 8px;">
                    <strong>📈 Tendencia:</strong> $([ $ERRORS_COUNT -lt 5 ] && echo "Estable" || echo "Requiere atención")
                </div>
            </div>
        </div>
        
        <div class="content-section" style="margin: 30px 0;">
            <h3>📈 Tendencias del Sistema</h3>
EOF

    # Agregar datos de tendencias
    for trend in "${TREND_DATA[@]}"; do
        IFS=',' read -r date metric value <<< "$trend"
        echo "                <div style=\"padding: 10px; margin: 5px 0; background: white; border-radius: 6px; display: flex; justify-content: space-between;\">"
        echo "                    <span><strong>$metric</strong> ($date)</span>"
        echo "                    <span>$value</span>"
        echo "                </div>"
    done

    cat >> "$REPORT_FILE" << EOF
        </div>
        
        <div class="recommendations">
            <h3>💡 Recomendaciones Ejecutivas</h3>
EOF

    # Agregar recomendaciones
    if [[ -f "$TMP_DIR/recommendations.txt" ]]; then
        while IFS= read -r recommendation; do
            echo "            <div class=\"recommendation-item\">$recommendation</div>"
        done < "$TMP_DIR/recommendations.txt"
    else
        echo "            <div class=\"recommendation-item\">No hay recomendaciones específicas disponibles.</div>"
    fi

    cat >> "$REPORT_FILE" << EOF
        </div>
        
        <div class="footer">
            <h4>📋 Información del Reporte</h4>
            <p><strong>Versión:</strong> $REPORT_VERSION | <strong>Rango de fechas:</strong> $DATE_RANGE | <strong>Zona horaria:</strong> $TIMEZONE</p>
            <p><strong>Secciones completadas:</strong> $SECTIONS_COMPLETED/$TOTAL_SECTIONS | <strong>Estado general:</strong> <span class="status-badge status-$([ "$system_status" = "saludable" ] && echo "healthy" || echo "$status_color")">$system_status</span></p>
            <p><em>Este reporte se genera automáticamente. Para más detalles, consulte los logs del sistema.</em></p>
        </div>
    </div>
</body>
</html>
EOF
    
    log_success "Reporte HTML generado: $REPORT_FILE"
}

# ===============================================================================
# GENERACIÓN DE REPORTE JSON
# ===============================================================================

generate_json_report() {
    log_report "Generando reporte JSON..."
    
    # Crear estructura JSON
    cat > "$REPORT_JSON" << EOF
{
    "report_info": {
        "title": "$REPORT_TITLE",
        "version": "$REPORT_VERSION",
        "generated_at": "$(date -Iseconds)",
        "date_range": "$DATE_RANGE",
        "timezone": "$TIMEZONE"
    },
    "system_status": {
        "overall_status": "$([ "$system_status" = "saludable" ] && echo "healthy" || echo "$system_status")",
        "uptime": "${SYSTEM_METRICS[uptime]:-N/A}",
        "total_sections": $TOTAL_SECTIONS,
        "completed_sections": $SECTIONS_COMPLETED
    },
    "metrics": {
        "cpu_usage": "${SYSTEM_METRICS[cpu_usage]:-N/A}",
        "memory_usage": "${SYSTEM_METRICS[memory_usage]:-N/A}",
        "disk_usage": "${SYSTEM_METRICS[disk_usage]:-N/A}",
        "network_io": "${SYSTEM_METRICS[network_io]:-N/A}",
        "service_count": ${SYSTEM_METRICS[service_count]:-0}
    },
    "services": {
EOF

    # Agregar estado de servicios
    local service_count=0
    for service in "${!SERVICE_DATA[@]}"; do
        if [[ $service_count -gt 0 ]]; then
            echo "," >> "$REPORT_JSON"
        fi
        echo "        \"$service\": \"${SERVICE_DATA[$service]}\"" >> "$REPORT_JSON"
        service_count=$((service_count + 1))
    done

    cat >> "$REPORT_JSON" << EOF
    },
    "analysis": {
        "errors_count": $ERRORS_COUNT,
        "warnings_count": $WARNINGS_COUNT,
        "error_rate": "$([ ${SYSTEM_METRICS[total_requests]:-0} -gt 0 ] && echo "$((ERRORS_COUNT * 100 / SYSTEM_METRICS[total_requests]))" || echo "0")%"
    },
    "recommendations": [
EOF

    # Agregar recomendaciones
    if [[ -f "$TMP_DIR/recommendations.txt" ]]; then
        local rec_count=0
        while IFS= read -r recommendation; do
            if [[ $rec_count -gt 0 ]]; then
                echo "," >> "$REPORT_JSON"
            fi
            echo "        \"$recommendation\"" >> "$REPORT_JSON"
            rec_count=$((rec_count + 1))
        done < "$TMP_DIR/recommendations.txt"
    fi

    cat >> "$REPORT_JSON" << EOF
    ],
    "trends": [
EOF

    # Agregar datos de tendencias
    local trend_count=0
    for trend in "${TREND_DATA[@]}"; do
        IFS=',' read -r date metric value <<< "$trend"
        if [[ $trend_count -gt 0 ]]; then
            echo "," >> "$REPORT_JSON"
        fi
        echo "        {\"date\": \"$date\", \"metric\": \"$metric\", \"value\": \"$value\"}" >> "$REPORT_JSON"
        trend_count=$((trend_count + 1))
    done

    cat >> "$REPORT_JSON" << EOF
    ]
}
EOF
    
    log_success "Reporte JSON generado: $REPORT_JSON"
}

# ===============================================================================
# GENERACIÓN DE REPORTE CSV
# ===============================================================================

generate_csv_report() {
    log_report "Generando reporte CSV..."
    
    cat > "$REPORT_CSV" << EOF
Timestamp,Metric,Value,Status
$(date -Iseconds),Uptime,${SYSTEM_METRICS[uptime]:-N/A},OK
$(date -Iseconds),CPU_Usage,${SYSTEM_METRICS[cpu_usage]:-N/A},OK
$(date -Iseconds),Memory_Usage,${SYSTEM_METRICS[memory_usage]:-N/A},OK
$(date -Iseconds),Disk_Usage,${SYSTEM_METRICS[disk_usage]:-N/A},OK
$(date -Iseconds),Service_Count,${SYSTEM_METRICS[service_count]:-0},OK
$(date -Iseconds),Error_Count,$ERRORS_COUNT,$( [ $ERRORS_COUNT -lt 5 ] && echo "OK" || echo "WARNING" )
$(date -Iseconds),Warning_Count,$WARNINGS_COUNT,$( [ $WARNINGS_COUNT -lt 5 ] && echo "OK" || echo "WARNING" )
EOF

    # Agregar estado de servicios
    for service in "${!SERVICE_DATA[@]}"; do
        echo "$(date -Iseconds),$(echo "$service" | tr '[:lower:]' '[:upper:]')_Status,${SERVICE_DATA[$service]},$( [ "${SERVICE_DATA[$service]}" = "online" ] && echo "OK" || echo "ERROR" )" >> "$REPORT_CSV"
    done
    
    log_success "Reporte CSV generado: $REPORT_CSV"
}

# ===============================================================================
# LIMPIEZA DE ARCHIVOS ANTIGUOS
# ===============================================================================

cleanup_old_reports() {
    log_info "Limpiando reportes antiguos (más de $RETENTION_DAYS días)..."
    
    find "$REPORT_DIR" -name "system-report_*.html" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    find "$REPORT_DIR" -name "system-report_*.json" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    find "$REPORT_DIR" -name "system-report_*.csv" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    
    find "$LOG_DIR" -name "*benchmark*" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    find "$LOG_DIR" -name "*validation*" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    find "$LOG_DIR" -name "*communication*" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    find "$LOG_DIR" -name "*failure*" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    
    log_info "Limpieza completada"
}

# ===============================================================================
# FUNCIÓN PRINCIPAL
# ===============================================================================

main() {
    echo -e "${BLUE}================================================================================"
    echo -e "📊 GENERACIÓN DE REPORTE DEL SISTEMA"
    echo -e "================================================================================${NC}"
    
    # Verificar si ya hay un reporte en curso
    if [[ -f "$PID_FILE" ]]; then
        local old_pid
        old_pid=$(cat "$PID_FILE")
        if kill -0 "$old_pid" 2>/dev/null; then
            log_error "Ya hay un reporte en curso (PID: $old_pid)"
            exit 1
        fi
    fi
    
    # Crear PID file
    echo $$ > "$PID_FILE"
    
    # Cleanup al salir
    trap 'rm -f "$PID_FILE" && rm -rf "$TMP_DIR"' EXIT
    
    # Inicializar logging
    initialize_logging
    
    log_info "Iniciando generación de reporte del sistema..."
    log_info "Rango de fechas: $DATE_RANGE"
    
    # Recolectar datos
    collect_system_metrics
    collect_service_status
    analyze_logs
    analyze_performance
    analyze_trends
    generate_recommendations
    
    # Generar reportes
    generate_html_report
    generate_json_report
    generate_csv_report
    
    # Limpiar archivos antiguos
    cleanup_old_reports
    
    REPORT_GENERATED=true
    
    # Mostrar resumen
    echo -e "\n${BLUE}📊 RESUMEN DEL REPORTE${NC}"
    echo -e "Estado general del sistema: $system_status"
    echo -e "Secciones completadas: $SECTIONS_COMPLETED/$TOTAL_SECTIONS"
    echo -e "Errores detectados: $ERRORS_COUNT"
    echo -e "Warnings detectados: $WARNINGS_COUNT"
    echo -e "Servicios activos: ${SYSTEM_METRICS[service_count]:-0}/6"
    echo -e "Reporte HTML: $REPORT_FILE"
    echo -e "Reporte JSON: $REPORT_JSON"
    echo -e "Reporte CSV: $REPORT_CSV"
    
    if [[ "$system_status" == "crítico" ]]; then
        echo -e "\n${RED}⚠️  ADVERTENCIA: El sistema requiere atención inmediata${NC}"
    elif [[ "$system_status" == "advertencia" ]]; then
        echo -e "\n${YELLOW}⚠️  NOTA: El sistema requiere monitoreo${NC}"
    else
        echo -e "\n${GREEN}✅ El sistema está funcionando correctamente${NC}"
    fi
    
    log_success "Generación de reporte completada"
}

# ===============================================================================
# EJECUCIÓN
# ===============================================================================

# Manejo de argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "Uso: $0 [opciones] [rango_tiempo]"
            echo "Opciones:"
            echo "  -h, --help              Mostrar esta ayuda"
            echo "  -d, --days DAYS         Días de retención de archivos (default: $RETENTION_DAYS)"
            echo ""
            echo "Argumentos:"
            echo "  rango_tiempo            Rango de tiempo (ej: 1h, 24h, 7d, default: 24h)"
            echo ""
            echo "Ejemplos:"
            echo "  $0                      # Generar reporte de las últimas 24h"
            echo "  $0 7d                   # Generar reporte de los últimos 7 días"
            echo "  $0 -d 60                # Retener archivos por 60 días"
            exit 0
            ;;
        -d|--days)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        *)
            DATE_RANGE="$1"
            shift
            ;;
    esac
done

# Ejecutar función principal
main "$@"