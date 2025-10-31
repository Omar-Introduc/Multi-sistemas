#!/bin/bash

# Script para generar reporte completo de health check
# Compila resultados de todos los componentes del sistema
# Autor: Sistema de Monitoreo
# Fecha: $(date +%Y-%m-%d)

set -e

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="${SCRIPT_DIR}/reports"
HTML_REPORT="${REPORT_DIR}/health-report-$(date +%Y%m%d_%H%M%S).html"
JSON_REPORT="${REPORT_DIR}/health-report-$(date +%Y%m%d_%H%M%S).json"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
TIMESTAMP_UNIX=$(date +%s)

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Crear directorio de reportes si no existe
mkdir -p "$REPORT_DIR"

# Variables globales para resultados
declare -A CHECK_RESULTS
declare -A CHECK_DETAILS
declare -A CHECK_TIMESTAMPS
declare -A CHECK_SEVERITY
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNINGS_COUNT=0
OVERALL_STATUS="UNKNOWN"

# Función para logging
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
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

# Registrar resultado de una verificación
register_check_result() {
    local check_name=$1
    local status=$2
    local details=$3
    local severity=${4:-"INFO"}
    
    CHECK_RESULTS["$check_name"]=$status
    CHECK_DETAILS["$check_name"]="$details"
    CHECK_TIMESTAMPS["$check_name"]=$(date '+%Y-%m-%d %H:%M:%S')
    CHECK_SEVERITY["$check_name"]=$severity
    
    ((TOTAL_CHECKS++))
    
    case $status in
        "PASS")
            ((PASSED_CHECKS++))
            ;;
        "FAIL")
            ((FAILED_CHECKS++))
            ;;
        "WARN")
            ((WARNINGS_COUNT++))
            ;;
    esac
}

# Ejecutar verificación con timeout y captura de errores
run_check_with_timeout() {
    local check_name=$1
    local script_path=$2
    local timeout=${3:-120}
    
    log "INFO" "Ejecutando $check_name..."
    
    local start_time=$(date +%s)
    local result
    local output
    local error
    
    # Ejecutar script y capturar salida
    if output=$(timeout $timeout "$script_path" 2>&1); then
        result="PASS"
        error=""
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            result="FAIL"
            error="Timeout después de ${timeout}s"
        elif [ $exit_code -eq 125 ]; then
            result="FAIL"
            error="Error de ejecución del script"
        elif [ $exit_code -eq 126 ]; then
            result="FAIL"
            error="Script no ejecutable"
        elif [ $exit_code -eq 127 ]; then
            result="FAIL"
            error="Comando no encontrado"
        else
            result="FAIL"
            error="Error en script (código: $exit_code)"
        fi
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Procesar salida para extraer información relevante
    local status_summary
    if [ "$result" = "PASS" ]; then
        status_summary="Completado exitosamente (${duration}s)"
    else
        status_summary="Falló: $error (${duration}s)"
    fi
    
    # Registrar resultado
    register_check_result "$check_name" "$result" "$status_summary" "$(get_severity_from_status "$result")"
    
    # Agregar detalles de salida si hay fallo
    if [ "$result" = "FAIL" ] && [ -n "$output" ]; then
        CHECK_DETAILS["$check_name"]="${CHECK_DETAILS[$check_name]} | Output: ${output:0:500}..."
    fi
    
    log "$([ "$result" = "PASS" ] && echo SUCCESS || echo ERROR)" "$check_name: $status_summary"
}

# Determinar severidad basada en status
get_severity_from_status() {
    case $1 in
        "PASS") echo "INFO" ;;
        "FAIL") echo "ERROR" ;;
        "WARN") echo "WARNING" ;;
        *) echo "INFO" ;;
    esac
}

# Verificar recursos del sistema
check_system_resources() {
    log "INFO" "Verificando recursos del sistema..."
    
    # CPU
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}' | sed 's/us,//')
    local cpu_status="PASS"
    local cpu_detail="Uso de CPU: ${cpu_usage}%"
    
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        cpu_status="WARN"
        cpu_detail="$cpu_detail (Alto uso)"
    fi
    
    register_check_result "CPU_USAGE" "$cpu_status" "$cpu_detail" "$(get_severity_from_status "$cpu_status")"
    
    # Memoria
    local mem_usage=$(free | grep Mem | awk '{printf("%.2f"), $3/$2 * 100.0}')
    local mem_status="PASS"
    local mem_detail="Uso de memoria: ${mem_usage}%"
    
    if (( $(echo "$mem_usage > 85" | bc -l) )); then
        mem_status="WARN"
        mem_detail="$mem_detail (Alto uso)"
    fi
    
    register_check_result "MEMORY_USAGE" "$mem_status" "$mem_detail" "$(get_severity_from_status "$mem_status")"
    
    # Disco
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    local disk_status="PASS"
    local disk_detail="Uso de disco: ${disk_usage}%"
    
    if [ "$disk_usage" -gt 90 ]; then
        disk_status="WARN"
        disk_detail="$disk_detail (Alto uso)"
    fi
    
    register_check_result "DISK_USAGE" "$disk_status" "$disk_detail" "$(get_severity_from_status "$disk_status")"
    
    # Carga del sistema
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    local cores=$(nproc)
    local load_status="PASS"
    local load_detail="Carga promedio: $load_avg (núcleos: $cores)"
    
    local load_threshold=$(echo "$cores * 0.8" | bc -l)
    if (( $(echo "$load_avg > $load_threshold" | bc -l) )); then
        load_status="WARN"
        load_detail="$load_detail (Alta carga)"
    fi
    
    register_check_result "SYSTEM_LOAD" "$load_status" "$load_detail" "$(get_severity_from_status "$load_status")"
}

# Verificar servicios del sistema
check_system_services() {
    log "INFO" "Verificando servicios del sistema..."
    
    local services=("nginx" "postgresql" "redis" "rabbitmq-server" "systemd-resolved" "ssh")
    local service_results=""
    
    for service in "${services[@]}"; do
        local service_status="FAIL"
        local service_detail=""
        
        if systemctl list-unit-files --type=service | grep -q "^$service"; then
            if systemctl is-active --quiet "$service"; then
                service_status="PASS"
                service_detail="Servicio activo y corriendo"
            else
                service_detail="Servicio instalado pero no activo"
            fi
        else
            service_status="WARN"
            service_detail="Servicio no instalado"
        fi
        
        register_check_result "SERVICE_$service" "$service_status" "$service_detail" "$(get_severity_from_status "$service_status")"
        service_results="$service_results$service: $service_status | "
    done
    
    register_check_result "SERVICES_OVERVIEW" "PASS" "Verificación de servicios completada" "INFO"
}

# Verificar conectividad de red
check_network_connectivity() {
    log "INFO" "Verificando conectividad de red..."
    
    # DNS
    if nslookup google.com >/dev/null 2>&1; then
        register_check_result "DNS_RESOLUTION" "PASS" "Resolución DNS funcionando correctamente" "INFO"
    else
        register_check_result "DNS_RESOLUTION" "FAIL" "Problema con resolución DNS" "ERROR"
    fi
    
    # Ping a gateway
    local gateway=$(ip route | grep default | awk '{print $3}' | head -1)
    if [ -n "$gateway" ] && ping -c 1 -W 3 "$gateway" >/dev/null 2>&1; then
        register_check_result "GATEWAY_CONNECTIVITY" "PASS" "Conectividad a gateway ($gateway) OK" "INFO"
    else
        register_check_result "GATEWAY_CONNECTIVITY" "FAIL" "No se puede alcanzar el gateway" "ERROR"
    fi
    
    # Ping a internet
    if ping -c 1 -W 5 8.8.8.8 >/dev/null 2>&1; then
        register_check_result "INTERNET_CONNECTIVITY" "PASS" "Conectividad a internet OK" "INFO"
    else
        register_check_result "INTERNET_CONNECTIVITY" "FAIL" "No hay conectividad a internet" "ERROR"
    fi
    
    # Verificar puertos abiertos críticos
    local critical_ports=("80" "443" "22" "5432" "6379" "5672")
    for port in "${critical_ports[@]}"; do
        if timeout 3 bash -c "echo >/dev/tcp/localhost/$port" 2>/dev/null; then
            register_check_result "PORT_$port" "PASS" "Puerto $port accesible" "INFO"
        else
            register_check_result "PORT_$port" "WARN" "Puerto $port no accesible" "WARNING"
        fi
    done
}

# Verificar logs del sistema
check_system_logs() {
    log "INFO" "Verificando logs del sistema..."
    
    # Verificar errores en journal
    local journal_errors=$(journalctl --since "10 minutes ago" --priority=err --no-pager | wc -l)
    if [ "$journal_errors" -eq 0 ]; then
        register_check_result "SYSTEM_LOGS" "PASS" "No hay errores en journal (últimos 10 min)" "INFO"
    else
        register_check_result "SYSTEM_LOGS" "WARN" "$journal_errors errores encontrados en journal (últimos 10 min)" "WARNING"
    fi
    
    # Verificar espacio en logs
    local log_usage=$(df -h /var/log | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$log_usage" -lt 90 ]; then
        register_check_result "LOG_DISK_USAGE" "PASS" "Espacio en /var/log: ${log_usage}%" "INFO"
    else
        register_check_result "LOG_DISK_USAGE" "WARN" "Alto uso de espacio en /var/log: ${log_usage}%" "WARNING"
    fi
}

# Verificar configuraciones críticas
check_critical_configs() {
    log "INFO" "Verificando configuraciones críticas..."
    
    local config_files=(
        "/etc/nginx/nginx.conf"
        "/etc/postgresql/postgresql.conf"
        "/etc/redis/redis.conf"
        "/etc/rabbitmq/rabbitmq.conf"
        "/etc/ssh/sshd_config"
        "/etc/systemd/resolved.conf"
    )
    
    for config in "${config_files[@]}"; do
        if [ -f "$config" ]; then
            if [ -r "$config" ]; then
                register_check_result "CONFIG_$(basename "$config")" "PASS" "Configuración legible y accesible" "INFO"
            else
                register_check_result "CONFIG_$(basename "$config")" "FAIL" "Configuración no legible" "ERROR"
            fi
        else
            register_check_result "CONFIG_$(basename "$config")" "WARN" "Archivo de configuración no encontrado" "WARNING"
        fi
    done
}

# Verificar permisos y ownership
check_file_permissions() {
    log "INFO" "Verificando permisos de archivos críticos..."
    
    local critical_files=(
        "/etc/passwd"
        "/etc/shadow"
        "/var/log"
        "/tmp"
        "/etc/nginx"
        "/etc/ssl"
    )
    
    for file in "${critical_files[@]}"; do
        if [ -e "$file" ]; then
            local perms=$(stat -c "%a" "$file" 2>/dev/null || echo "unknown")
            local owner=$(stat -c "%U" "$file" 2>/dev/null || echo "unknown")
            
            register_check_result "PERM_$(basename "$file")" "PASS" "Permisos: $perms, Owner: $owner" "INFO"
        fi
    done
}

# Generar reporte JSON
generate_json_report() {
    log "INFO" "Generando reporte JSON..."
    
    local json_content="{"
    json_content+="\"timestamp\": \"$TIMESTAMP\","
    json_content+="\"timestamp_unix\": $TIMESTAMP_UNIX,"
    json_content+="\"overall_status\": \"$OVERALL_STATUS\","
    json_content+="\"summary\": {"
    json_content+="\"total_checks\": $TOTAL_CHECKS,"
    json_content+="\"passed\": $PASSED_CHECKS,"
    json_content+="\"failed\": $FAILED_CHECKS,"
    json_content+="\"warnings\": $WARNINGS_COUNT"
    json_content+="},"
    json_content+="\"checks\": {"
    
    local first=true
    for check_name in "${!CHECK_RESULTS[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            json_content+=","
        fi
        
        json_content+="\"$check_name\": {"
        json_content+="\"status\": \"${CHECK_RESULTS[$check_name]}\","
        json_content+="\"details\": \"${CHECK_DETAILS[$check_name]}\","
        json_content+="\"timestamp\": \"${CHECK_TIMESTAMPS[$check_name]}\","
        json_content+="\"severity\": \"${CHECK_SEVERITY[$check_name]}\""
        json_content+="}"
    done
    
    json_content+="}"
    json_content+="}"
    
    echo "$json_content" > "$JSON_REPORT"
    log "SUCCESS" "Reporte JSON guardado: $JSON_REPORT"
}

# Generar reporte HTML
generate_html_report() {
    log "INFO" "Generando reporte HTML..."
    
    local html_content="<!DOCTYPE html>
<html lang=\"es\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Reporte de Health Check - $TIMESTAMP</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .status-badge { display: inline-block; padding: 5px 15px; border-radius: 20px; color: white; font-weight: bold; }
        .status-OK { background-color: #28a745; }
        .status-WARNING { background-color: #ffc107; color: black; }
        .status-ERROR { background-color: #dc3545; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .summary-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }
        .summary-card h3 { margin: 0; font-size: 2em; color: #333; }
        .summary-card p { margin: 5px 0 0 0; color: #666; }
        .checks-grid { display: grid; gap: 15px; }
        .check-item { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 15px; }
        .check-header { display: flex; justify-content: between; align-items: center; margin-bottom: 10px; }
        .check-name { font-weight: bold; color: #333; }
        .check-status { padding: 3px 10px; border-radius: 12px; color: white; font-size: 0.9em; }
        .check-details { color: #666; font-size: 0.9em; margin-top: 5px; }
        .timestamp { color: #888; font-size: 0.8em; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; text-align: center; }
    </style>
</head>
<body>
    <div class=\"container\">
        <div class=\"header\">
            <h1>Reporte de Health Check del Sistema</h1>
            <p><strong>Generado:</strong> $TIMESTAMP</p>
            <div>
                <span class=\"status-badge status-$OVERALL_STATUS\">Estado General: $OVERALL_STATUS</span>
            </div>
        </div>
        
        <div class=\"summary\">
            <div class=\"summary-card\">
                <h3>$TOTAL_CHECKS</h3>
                <p>Total de Verificaciones</p>
            </div>
            <div class=\"summary-card\" style=\"border-left-color: #28a745;\">
                <h3>$PASSED_CHECKS</h3>
                <p>Exitosas</p>
            </div>
            <div class=\"summary-card\" style=\"border-left-color: #dc3545;\">
                <h3>$FAILED_CHECKS</h3>
                <p>Fallidas</p>
            </div>
            <div class=\"summary-card\" style=\"border-left-color: #ffc107;\">
                <h3>$WARNINGS_COUNT</h3>
                <p>Advertencias</p>
            </div>
        </div>
        
        <div class=\"checks-grid\">"
    
    # Agregar cada verificación
    for check_name in $(printf '%s\n' "${!CHECK_RESULTS[@]}" | sort); do
        local status="${CHECK_RESULTS[$check_name]}"
        local details="${CHECK_DETAILS[$check_name]}"
        local timestamp="${CHECK_TIMESTAMPS[$check_name]}"
        local severity="${CHECK_SEVERITY[$check_name]}"
        
        html_content+="
            <div class=\"check-item\">
                <div class=\"check-header\">
                    <span class=\"check-name\">$check_name</span>
                    <span class=\"check-status status-$severity\">$status</span>
                </div>
                <div class=\"check-details\">$details</div>
                <div class=\"timestamp\">Verificado: $timestamp</div>
            </div>"
    done
    
    html_content+="
        </div>
        
        <div class=\"footer\">
            <p>Reporte generado automáticamente por el Sistema de Monitoreo</p>
            <p>Para más detalles, revisar logs en: ${SCRIPT_DIR}/logs/</p>
        </div>
    </div>
</body>
</html>"
    
    echo "$html_content" > "$HTML_REPORT"
    log "SUCCESS" "Reporte HTML guardado: $HTML_REPORT"
}

# Enviar alertas si es necesario
send_alerts_if_needed() {
    local alert_level=$1
    local message=$2
    
    # Aquí se pueden agregar integraciones con sistemas de alertas
    # Email, Slack, PagerDuty, etc.
    
    log "WARN" "ALERTA [$alert_level]: $message"
    
    # Enviar por email si está configurado
    if command -v mail >/dev/null 2>&1; then
        echo "$message" | mail -s "Health Check Alert: $alert_level" admin@sistema.local 2>/dev/null || true
    fi
    
    # Escribir a archivo de alertas
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$alert_level] $message" >> "${SCRIPT_DIR}/logs/alerts.log"
}

# Función principal
generate_health_report() {
    log "INFO" "=== INICIANDO GENERACIÓN DE REPORTE COMPLETO $(date) ==="
    
    # Ejecutar verificaciones del sistema
    check_system_resources
    check_system_services
    check_network_connectivity
    check_system_logs
    check_critical_configs
    check_file_permissions
    
    # Ejecutar scripts de verificación específicos
    if [ -f "${SCRIPT_DIR}/health-check.sh" ]; then
        run_check_with_timeout "HEALTH_CHECK_GENERAL" "${SCRIPT_DIR}/health-check.sh" 300
    fi
    
    if [ -f "${SCRIPT_DIR}/check-db-connections.sh" ]; then
        run_check_with_timeout "DATABASE_CONNECTIVITY" "${SCRIPT_DIR}/check-db-connections.sh" 180
    fi
    
    if [ -f "${SCRIPT_DIR}/check-rabbitmq.sh" ]; then
        run_check_with_timeout "RABBITMQ_STATUS" "${SCRIPT_DIR}/check-rabbitmq.sh" 180
    fi
    
    if [ -f "${SCRIPT_DIR}/check-redis.sh" ]; then
        run_check_with_timeout "REDIS_STATUS" "${SCRIPT_DIR}/check-redis.sh" 120
    fi
    
    # Determinar estado general
    if [ $FAILED_CHECKS -eq 0 ]; then
        if [ $WARNINGS_COUNT -eq 0 ]; then
            OVERALL_STATUS="OK"
        else
            OVERALL_STATUS="WARNING"
        fi
    else
        OVERALL_STATUS="ERROR"
    fi
    
    # Generar reportes
    generate_json_report
    generate_html_report
    
    # Enviar alertas si es necesario
    if [ "$OVERALL_STATUS" = "ERROR" ]; then
        send_alerts_if_needed "CRITICAL" "Health check falló: $FAILED_CHECKS verificaciones fallaron, $WARNINGS_COUNT advertencias"
    elif [ "$OVERALL_STATUS" = "WARNING" ]; then
        send_alerts_if_needed "WARNING" "Health check con advertencias: $WARNINGS_COUNT advertencias detectadas"
    fi
    
    # Mostrar resumen final
    log "INFO" "=== RESUMEN DEL REPORTE ==="
    log "INFO" "Estado General: $OVERALL_STATUS"
    log "INFO" "Total Verificaciones: $TOTAL_CHECKS"
    log "INFO" "Exitosas: $PASSED_CHECKS | Fallidas: $FAILED_CHECKS | Advertencias: $WARNINGS_COUNT"
    log "INFO" "Reporte HTML: $HTML_REPORT"
    log "INFO" "Reporte JSON: $JSON_REPORT"
    
    # Código de salida basado en estado
    case $OVERALL_STATUS in
        "OK") exit 0 ;;
        "WARNING") exit 1 ;;
        "ERROR") exit 2 ;;
        *) exit 3 ;;
    esac
}

# Manejo de señales
trap 'log "ERROR" "Generación de reporte interrumpida"; exit 130' INT TERM

# Verificar dependencias
command -v bc >/dev/null 2>&1 || { log "ERROR" "bc no encontrado"; exit 127; }
command -v systemd >/dev/null 2>&1 || { log "WARN" "systemd no disponible"; }

# Ejecutar generación de reporte si el script es llamado directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    generate_health_report
fi
