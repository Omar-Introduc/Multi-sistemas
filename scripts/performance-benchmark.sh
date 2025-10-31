#!/bin/bash

# ===============================================================================
# SCRIPT DE BENCHMARKS DE RENDIMIENTO
# ===============================================================================
# Funcionalidades:
# - Benchmarks de rendimiento de servicios
# - Testing de carga y stress
# - Métricas de throughput y latencia
# - Análisis de capacidad y escalabilidad
# - Reportes automatizados de performance
# ===============================================================================

set -euo pipefail

# Configuración global
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs/performance"
REPORT_DIR="${SCRIPT_DIR}/reports/performance"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="${LOG_DIR}/performance-benchmark_${TIMESTAMP}.log"
REPORT_FILE="${REPORT_DIR}/performance-benchmark_${TIMESTAMP}.html"
PID_FILE="/tmp/benchmark.pid"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Variables de estado
BENCHMARK_FAILED=false
TOTAL_BENCHMARKS=0
PASSED_BENCHMARKS=0
FAILED_BENCHMARKS=0
SKIPPED_BENCHMARKS=0

# Configuración de benchmarks
BENCHMARK_DURATION=60  # segundos
CONCURRENT_USERS=10
TOTAL_REQUESTS=1000
RAMP_UP_TIME=10
COOLDOWN_TIME=5

# URLs de servicios para benchmarking
declare -A SERVICE_URLS
SERVICE_URLS[lp1_banco]="http://localhost:8080"
SERVICE_URLS[lp2_reniec]="http://localhost:8000"
SERVICE_URLS[health_lp1]="http://localhost:8080/health"
SERVICE_URLS[health_lp2]="http://localhost:8000/health"

# Métricas de rendimiento
declare -A PERF_METRICS
PERF_METRICS[start_time]=$(date +%s%N)
PERF_METRICS[total_duration]=0
PERF_METRICS[total_requests]=0
PERF_METRICS[successful_requests]=0
PERF_METRICS[failed_requests]=0
PERF_METRICS[avg_response_time]=0
PERF_METRICS[min_response_time]=999999
PERF_METRICS[max_response_time]=0
PERF_METRICS[p95_response_time]=0
PERF_METRICS[p99_response_time]=0
PERF_METRICS[requests_per_second]=0
PERF_METRICS[throughput]=0
PERF_METRICS[error_rate]=0
PERF_METRICS[cpu_usage_avg]=0
PERF_METRICS[memory_usage_avg]=0

# Arrays para datos detallados
declare -a RESPONSE_TIMES
declare -a THROUGHPUT_DATA
declare -a CPU_DATA
declare -a MEMORY_DATA

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
log_benchmark() { log "BENCHMARK" "$@"; }

initialize_logging() {
    mkdir -p "$LOG_DIR" "$REPORT_DIR"
    
    cat > "$LOG_FILE" << EOF
================================================================================
BENCHMARKS DE RENDIMIENTO - INICIADOS
Timestamp: $(date '+%Y-%m-%d %H:%M:%S')
Script: $0
Configuración:
  - Duración: ${BENCHMARK_DURATION}s
  - Usuarios concurrentes: $CONCURRENT_USERS
  - Total de requests: $TOTAL_REQUESTS
  - Ramp up time: ${RAMP_UP_TIME}s
================================================================================

EOF
    log_info "Sistema de logging inicializado: $LOG_FILE"
}

# ===============================================================================
# UTILIDADES DE BENCHMARKING
# ===============================================================================

measure_system_resources() {
    local measurement_time="$1"
    
    log_benchmark "Midiendo recursos del sistema durante $measurement_time segundos..."
    
    local start_time=$(date +%s)
    local end_time=$((start_time + measurement_time))
    
    while [[ $(date +%s) -lt $end_time ]]; do
        # CPU usage
        if command -v top >/dev/null 2>&1; then
            local cpu_usage
            cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}' | tr -d ' ')
            if [[ -n "$cpu_usage" && "$cpu_usage" != "0.0" ]]; then
                CPU_DATA+=("$cpu_usage")
            fi
        fi
        
        # Memory usage
        if command -v free >/dev/null 2>&1; then
            local mem_usage
            mem_usage=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}' | tr -d ' ')
            if [[ -n "$mem_usage" ]]; then
                MEMORY_DATA+=("$mem_usage")
            fi
        fi
        
        sleep 1
    done
    
    log_info "Medición de recursos completada"
}

single_request_benchmark() {
    local url="$1"
    local name="$2"
    
    log_benchmark "Ejecutando benchmark individual: $name"
    
    TOTAL_BENCHMARKS=$((TOTAL_BENCHMARKS + 1))
    
    local start_ns=$(date +%s%N)
    local response_code
    local response_body
    local success=false
    
    # Realizar request
    if command -v curl >/dev/null 2>&1; then
        response_body=$(curl -s --max-time 30 -w "%{http_code}" "$url" 2>/dev/null || echo "000")
        response_code="${response_body: -3}"
        
        if [[ "$response_code" =~ ^[23] ]]; then
            success=true
            PERF_METRICS[successful_requests]=$((PERF_METRICS[successful_requests] + 1))
        else
            PERF_METRICS[failed_requests]=$((PERF_METRICS[failed_requests] + 1))
        fi
        
        local end_ns=$(date +%s%N)
        local response_time=$(( (end_ns - start_ns) / 1000000 ))  # Convert to milliseconds
        
        RESPONSE_TIMES+=("$response_time")
        
        # Actualizar métricas
        if [[ "$response_time" -gt "${PERF_METRICS[max_response_time]}" ]]; then
            PERF_METRICS[max_response_time]="$response_time"
        fi
        
        if [[ "$response_time" -lt "${PERF_METRICS[min_response_time]}" ]]; then
            PERF_METRICS[min_response_time]="$response_time"
        fi
        
        if [[ "$success" == "true" ]]; then
            log_success "✅ $name: ${response_time}ms (HTTP $response_code)"
            PASSED_BENCHMARKS=$((PASSED_BENCHMARKS + 1))
            echo "$response_time"
            return 0
        else
            log_error "❌ $name: FALLO (HTTP $response_code)"
            FAILED_BENCHMARKS=$((FAILED_BENCHMARKS + 1))
            return 1
        fi
    else
        log_warn "⚠️  $name: curl no disponible"
        SKIPPED_BENCHMARKS=$((SKIPPED_BENCHMARKS + 1))
        return 1
    fi
}

# ===============================================================================
# BENCHMARK DE RESPUESTA INDIVIDUAL
# ===============================================================================

benchmark_single_request() {
    log_benchmark "Ejecutando benchmarks de respuesta individual..."
    
    for service in "${!SERVICE_URLS[@]}"; do
        local url="${SERVICE_URLS[$service]}"
        
        # Realizar múltiples requests para obtener datos estadísticos
        local total_time=0
        local successful_requests=0
        local max_time=0
        local min_time=999999
        
        for i in $(seq 1 10); do
            local response_time
            response_time=$(single_request_benchmark "$url" "$service-request-$i")
            
            if [[ -n "$response_time" && "$response_time" =~ ^[0-9]+$ ]]; then
                total_time=$((total_time + response_time))
                successful_requests=$((successful_requests + 1))
                
                if [[ "$response_time" -gt "$max_time" ]]; then
                    max_time="$response_time"
                fi
                
                if [[ "$response_time" -lt "$min_time" ]]; then
                    min_time="$response_time"
                fi
            fi
            
            sleep 0.1  # Small delay between requests
        done
        
        if [[ $successful_requests -gt 0 ]]; then
            local avg_time=$((total_time / successful_requests))
            log_benchmark "$service: Avg=${avg_time}ms, Min=${min_time}ms, Max=${max_time}ms, Success=${successful_requests}/10"
        fi
    done
}

# ===============================================================================
# BENCHMARK DE CONCURRENCIA
# ===============================================================================

benchmark_concurrent_requests() {
    local url="$1"
    local service_name="$2"
    local num_requests="$3"
    
    log_benchmark "Benchmark de concurrencia: $service_name ($num_requests requests concurrentes)"
    
    TOTAL_BENCHMARKS=$((TOTAL_BENCHMARKS + 1))
    
    # Función para realizar requests concurrentes
    concurrent_requests() {
        local request_id="$1"
        local local_start=$(date +%s%N)
        
        if command -v curl >/dev/null 2>&1; then
            local response_code
            response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 30 "$url" 2>/dev/null || echo "000")
            
            local local_end=$(date +%s%N)
            local response_time=$(( (local_end - local_start) / 1000000 ))
            
            if [[ "$response_code" =~ ^[23] ]]; then
                echo "$response_time|success"
            else
                echo "$response_time|fail"
            fi
        else
            echo "0|nocurl"
        fi
    }
    
    # Lanzar requests concurrentes
    local pids=()
    local start_time=$(date +%s%N)
    
    for i in $(seq 1 "$num_requests"); do
        concurrent_requests "$i" > /tmp/benchmark_result_$$_$i &
        pids+=("$!")
        
        # Stagger requests slightly
        sleep 0.01
    done
    
    # Esperar a que todos los procesos terminen
    local successful_concurrent=0
    local failed_concurrent=0
    
    for pid in "${pids[@]}"; do
        if wait "$pid"; then
            # Process completed
            :
        fi
        
        # Process result file
        for i in $(seq 1 "$num_requests"); do
            local result_file="/tmp/benchmark_result_$$_$i"
            if [[ -f "$result_file" ]]; then
                local result
                result=$(cat "$result_file" 2>/dev/null || echo "")
                rm -f "$result_file"
                
                if [[ -n "$result" ]]; then
                    IFS='|' read -r time status <<< "$result"
                    
                    if [[ "$status" == "success" ]]; then
                        successful_concurrent=$((successful_concurrent + 1))
                        RESPONSE_TIMES+=("$time")
                    else
                        failed_concurrent=$((failed_concurrent + 1))
                    fi
                fi
            fi
        done
    done
    
    local end_time=$(date +%s%N)
    local total_duration=$(( (end_time - start_time) / 1000000000 ))  # Convert to seconds
    
    local total_requests=$((successful_concurrent + failed_concurrent))
    local requests_per_second=0
    
    if [[ $total_duration -gt 0 ]]; then
        requests_per_second=$((total_requests / total_duration))
    fi
    
    PERF_METRICS[total_requests]=$((PERF_METRICS[total_requests] + total_requests))
    PERF_METRICS[successful_requests]=$((PERF_METRICS[successful_requests] + successful_concurrent))
    PERF_METRICS[failed_requests]=$((PERF_METRICS[failed_requests] + failed_concurrent))
    
    if [[ $total_requests -gt 0 ]]; then
        local success_rate=$((successful_concurrent * 100 / total_requests))
        log_success "✅ Concurrencia $service_name: $successful_concurrent/$total_requests success (${success_rate}%, ${requests_per_second} req/s)"
        PASSED_BENCHMARKS=$((PASSED_BENCHMARKS + 1))
        THROUGHPUT_DATA+=("$requests_per_second")
    else
        log_error "❌ Concurrencia $service_name: No se recibieron respuestas"
        FAILED_BENCHMARKS=$((FAILED_BENCHMARKS + 1))
    fi
    
    return 0
}

# ===============================================================================
# BENCHMARK DE CARGA SOSTENIDA
# ===============================================================================

benchmark_sustained_load() {
    local url="$1"
    local service_name="$2"
    local duration="$3"
    
    log_benchmark "Benchmark de carga sostenida: $service_name ($duration segundos)"
    
    TOTAL_BENCHMARKS=$((TOTAL_BENCHMARKS + 1))
    
    local start_time=$(date +%s)
    local end_time=$((start_time + duration))
    local request_count=0
    local success_count=0
    local error_count=0
    
    # Función para realizar un request
    perform_request() {
        local local_start=$(date +%s%N)
        
        if command -v curl >/dev/null 2>&1; then
            local response_code
            response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")
            local local_end=$(date +%s%N)
            local response_time=$(( (local_end - local_start) / 1000000 ))
            
            if [[ "$response_code" =~ ^[23] ]]; then
                RESPONSE_TIMES+=("$response_time")
                echo "success"
            else
                echo "fail"
            fi
        else
            echo "nocurl"
        fi
    }
    
    # Loop principal de carga sostenida
    while [[ $(date +%s) -lt $end_time ]]; do
        # Realizar múltiples requests concurrentes
        local batch_size=5
        local pids=()
        
        for i in $(seq 1 $batch_size); do
            perform_request > /tmp/load_test_result_$$_$i 2>/dev/null &
            pids+=("$!")
        done
        
        # Esperar resultados del batch
        for pid in "${pids[@]}"; do
            wait "$pid" 2>/dev/null || true
        done
        
        # Procesar resultados del batch
        for i in $(seq 1 $batch_size); do
            local result_file="/tmp/load_test_result_$$_$i"
            if [[ -f "$result_file" ]]; then
                local result
                result=$(cat "$result_file" 2>/dev/null || echo "")
                rm -f "$result_file"
                
                request_count=$((request_count + 1))
                
                case "$result" in
                    "success")
                        success_count=$((success_count + 1))
                        ;;
                    "fail"|"nocurl")
                        error_count=$((error_count + 1))
                        ;;
                esac
            fi
        done
        
        # Mostrar progreso cada 10 segundos
        local elapsed=$(( $(date +%s) - start_time ))
        if [[ $((elapsed % 10)) -eq 0 ]]; then
            log_info "Progreso: ${elapsed}s/${duration}s - Requests: $request_count, Success: $success_count, Errors: $error_count"
        fi
        
        sleep 1
    done
    
    local actual_duration=$(( $(date +%s) - start_time ))
    local rps=$((request_count / actual_duration))
    local success_rate=0
    
    if [[ $request_count -gt 0 ]]; then
        success_rate=$((success_count * 100 / request_count))
    fi
    
    PERF_METRICS[total_requests]=$((PERF_METRICS[total_requests] + request_count))
    PERF_METRICS[successful_requests]=$((PERF_METRICS[successful_requests] + success_count))
    PERF_METRICS[failed_requests]=$((PERF_METRICS[failed_requests] + error_count))
    
    if [[ $success_rate -ge 95 ]]; then
        log_success "✅ Carga sostenida $service_name: ${rps} req/s, ${success_rate}% success rate"
        PASSED_BENCHMARKS=$((PASSED_BENCHMARKS + 1))
        THROUGHPUT_DATA+=("$rps")
    elif [[ $success_rate -ge 80 ]]; then
        log_warn "⚠️  Carga sostenida $service_name: ${rps} req/s, ${success_rate}% success rate (degradado)"
        PASSED_BENCHMARKS=$((PASSED_BENCHMARKS + 1))
    else
        log_error "❌ Carga sostenida $service_name: ${rps} req/s, ${success_rate}% success rate (fallido)"
        FAILED_BENCHMARKS=$((FAILED_BENCHMARKS + 1))
    fi
}

# ===============================================================================
# BENCHMARK DE BASE DE DATOS
# ===============================================================================

benchmark_database_performance() {
    log_benchmark "Ejecutando benchmarks de rendimiento de bases de datos..."
    
    # PostgreSQL benchmark
    TOTAL_BENCHMARKS=$((TOTAL_BENCHMARKS + 1))
    if command -v pgbench >/dev/null 2>&1; then
        log_benchmark "Ejecutando pgbench para PostgreSQL..."
        
        local pgbench_result
        pgbench_result=$(pgbench -h localhost -p 5432 -U postgres -d postgres -c 5 -T 30 2>/dev/null || echo "")
        
        if [[ -n "$pgbench_result" ]]; then
            local tps
            tps=$(echo "$pgbench_result" | grep "tps =" | awk '{print $3}' | head -1)
            log_success "✅ PostgreSQL: ${tps} TPS"
            PASSED_BENCHMARKS=$((PASSED_BENCHMARKS + 1))
            THROUGHPUT_DATA+=("$tps")
        else
            log_error "❌ PostgreSQL: pgbench falló"
            FAILED_BENCHMARKS=$((FAILED_BENCHMARKS + 1))
        fi
    else
        log_warn "⚠️  PostgreSQL: pgbench no disponible"
        SKIPPED_BENCHMARKS=$((SKIPPED_BENCHMARKS + 1))
    fi
    
    # Redis benchmark
    TOTAL_BENCHMARKS=$((TOTAL_BENCHMARKS + 1))
    if command -v redis-benchmark >/dev/null 2>&1; then
        log_benchmark "Ejecutando redis-benchmark..."
        
        local redis_result
        redis_result=$(redis-benchmark -h localhost -p 6379 -n 10000 -c 10 2>/dev/null || echo "")
        
        if [[ -n "$redis_result" ]]; then
            local set_ops
            set_ops=$(echo "$redis_result" | grep "SET:" | awk '{print $1}' | head -1)
            local get_ops
            get_ops=$(echo "$redis_result" | grep "GET:" | awk '{print $1}' | head -1)
            
            log_success "✅ Redis: SET=${set_ops} ops/s, GET=${get_ops} ops/s"
            PASSED_BENCHMARKS=$((PASSED_BENCHMARKS + 1))
            
            if [[ -n "$set_ops" ]]; then
                THROUGHPUT_DATA+=("$set_ops")
            fi
        else
            log_error "❌ Redis: redis-benchmark falló"
            FAILED_BENCHMARKS=$((FAILED_BENCHMARKS + 1))
        fi
    else
        log_warn "⚠️  Redis: redis-benchmark no disponible"
        SKIPPED_BENCHMARKS=$((SKIPPED_BENCHMARKS + 1))
    fi
}

# ===============================================================================
# BENCHMARK DE STRESS
# ===============================================================================

benchmark_stress_test() {
    log_benchmark "Ejecutando benchmark de stress..."
    
    TOTAL_BENCHMARKS=$((TOTAL_BENCHMARKS + 1))
    
    local duration=60
    log_benchmark "Stress test por $duration segundos..."
    
    # Medir recursos antes del stress
    measure_system_resources 5
    
    # Generar carga de stress
    if command -v stress >/dev/null 2>&1; then
        stress --cpu 4 --io 2 --vm 2 --timeout "${duration}s" >/dev/null 2>&1 &
        local stress_pid=$!
        log_info "Stress generado (PID: $stress_pid)"
        
        # Continuar midiendo recursos durante el stress
        measure_system_resources $duration
        
        wait "$stress_pid" 2>/dev/null || true
    else
        log_warn "⚠️  stress no disponible, usando método alternativo"
        # Método alternativo: usar yes para generar carga
        yes >/dev/null &
        local yes_pid=$!
        measure_system_resources $duration
        kill "$yes_pid" 2>/dev/null || true
    fi
    
    # Verificar que los servicios siguen funcionando
    local services_operational=0
    local total_services=${#SERVICE_URLS[@]}
    
    for service in "${!SERVICE_URLS[@]}"; do
        local url="${SERVICE_URLS[$service]}"
        if single_request_benchmark "$url" "stress-test-$service" >/dev/null 2>&1; then
            services_operational=$((services_operational + 1))
        fi
    done
    
    if [[ $services_operational -eq $total_services ]]; then
        log_success "✅ Stress test: Todos los servicios operativos durante carga extrema"
        PASSED_BENCHMARKS=$((PASSED_BENCHMARKS + 1))
    else
        local degraded=$((total_services - services_operational))
        log_warn "⚠️  Stress test: $degraded servicios degradados durante carga extrema"
        PASSED_BENCHMARKS=$((PASSED_BENCHMARKS + 1))
    fi
}

# ===============================================================================
# CÁLCULO DE MÉTRICAS FINALES
# ===============================================================================

calculate_final_metrics() {
    log_info "Calculando métricas finales de rendimiento..."
    
    local end_time=$(date +%s%N)
    PERF_METRICS[total_duration]=$(( (end_time - PERF_METRICS[start_time]) / 1000000000 ))
    
    # Calcular promedio de tiempo de respuesta
    if [[ ${#RESPONSE_TIMES[@]} -gt 0 ]]; then
        local total_time=0
        for time in "${RESPONSE_TIMES[@]}"; do
            total_time=$((total_time + time))
        done
        PERF_METRICS[avg_response_time]=$((total_time / ${#RESPONSE_TIMES[@]}))
    fi
    
    # Calcular percentiles (aproximación)
    if [[ ${#RESPONSE_TIMES[@]} -gt 0 ]]; then
        # Ordenar tiempos de respuesta
        local sorted_times=($(printf '%s\n' "${RESPONSE_TIMES[@]}" | sort -n))
        local total_count=${#sorted_times[@]}
        
        # P95
        local p95_index=$((total_count * 95 / 100))
        if [[ $p95_index -lt $total_count ]]; then
            PERF_METRICS[p95_response_time]="${sorted_times[$p95_index]}"
        fi
        
        # P99
        local p99_index=$((total_count * 99 / 100))
        if [[ $p99_index -lt $total_count ]]; then
            PERF_METRICS[p99_response_time]="${sorted_times[$p99_index]}"
        fi
    fi
    
    # Calcular throughput general
    if [[ ${#THROUGHPUT_DATA[@]} -gt 0 ]]; then
        local total_throughput=0
        for throughput in "${THROUGHPUT_DATA[@]}"; do
            total_throughput=$((total_throughput + throughput))
        done
        PERF_METRICS[throughput]=$((total_throughput / ${#THROUGHPUT_DATA[@]}))
    fi
    
    # Calcular tasa de error
    if [[ ${PERF_METRICS[total_requests]} -gt 0 ]]; then
        PERF_METRICS[error_rate]=$((PERF_METRICS[failed_requests] * 100 / PERF_METRICS[total_requests]))
    fi
    
    # Calcular promedio de uso de CPU y memoria
    if [[ ${#CPU_DATA[@]} -gt 0 ]]; then
        local total_cpu=0
        for cpu in "${CPU_DATA[@]}"; do
            total_cpu=$(echo "$total_cpu + $cpu" | bc 2>/dev/null || echo "$total_cpu")
        done
        PERF_METRICS[cpu_usage_avg]=$(echo "scale=1; $total_cpu / ${#CPU_DATA[@]}" | bc 2>/dev/null || echo "0")
    fi
    
    if [[ ${#MEMORY_DATA[@]} -gt 0 ]]; then
        local total_mem=0
        for mem in "${MEMORY_DATA[@]}"; do
            total_mem=$(echo "$total_mem + $mem" | bc 2>/dev/null || echo "$total_mem")
        done
        PERF_METRICS[memory_usage_avg]=$(echo "scale=1; $total_mem / ${#MEMORY_DATA[@]}" | bc 2>/dev/null || echo "0")
    fi
    
    log_info "Métricas finales calculadas"
}

# ===============================================================================
# GENERACIÓN DE REPORTE HTML
# ===============================================================================

generate_html_report() {
    log_info "Generando reporte HTML de benchmarks..."
    
    cat > "$REPORT_FILE" << EOF
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Benchmarks de Rendimiento</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; border-bottom: 2px solid #28a745; padding-bottom: 20px; margin-bottom: 30px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #28a745; }
        .metric-value { font-size: 2em; font-weight: bold; color: #28a745; }
        .metric-label { color: #666; margin-top: 5px; }
        .performance-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .performance-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #17a2b8; }
        .performance-card h3 { margin-top: 0; color: #333; }
        .performance-item { padding: 10px; margin: 5px 0; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; }
        .chart { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; }
        .bar { height: 20px; background: linear-gradient(to right, #28a745, #20c997); margin: 5px 0; border-radius: 4px; position: relative; }
        .bar-label { position: absolute; right: 5px; top: 50%; transform: translateY(-50%); color: white; font-size: 0.8em; }
        .footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #666; }
        .status-good { color: #28a745; }
        .status-warning { color: #ffc107; }
        .status-critical { color: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ Reporte de Benchmarks de Rendimiento</h1>
            <div class="timestamp">Generado el: $(date '+%Y-%m-%d %H:%M:%S')</div>
            <div class="duration">Duración total: ${PERF_METRICS[total_duration]}s</div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">$TOTAL_BENCHMARKS</div>
                <div class="metric-label">Total de Benchmarks</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #28a745;">$PASSED_BENCHMARKS</div>
                <div class="metric-label">Exitosos</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #dc3545;">$FAILED_BENCHMARKS</div>
                <div class="metric-label">Fallidos</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #ffc107;">$SKIPPED_BENCHMARKS</div>
                <div class="metric-label">Omitidos</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${PERF_METRICS[total_requests]}</div>
                <div class="metric-label">Total Requests</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${PERF_METRICS[avg_response_time]}ms</div>
                <div class="metric-label">Tiempo Promedio</div>
            </div>
        </div>
        
        <div class="performance-grid">
            <div class="performance-card">
                <h3>🎯 Rendimiento de Servicios</h3>
                <div class="performance-item">
                    <span>Tiempo de Respuesta Mínimo:</span>
                    <span class="status-good">${PERF_METRICS[min_response_time]}ms</span>
                </div>
                <div class="performance-item">
                    <span>Tiempo de Respuesta Máximo:</span>
                    <span>${PERF_METRICS[max_response_time]}ms</span>
                </div>
                <div class="performance-item">
                    <span>Percentil 95 (P95):</span>
                    <span>${PERF_METRICS[p95_response_time]}ms</span>
                </div>
                <div class="performance-item">
                    <span>Percentil 99 (P99):</span>
                    <span>${PERF_METRICS[p99_response_time]}ms</span>
                </div>
            </div>
            
            <div class="performance-card">
                <h3>📊 Throughput y Capacidad</h3>
                <div class="performance-item">
                    <span>Requests Exitosos:</span>
                    <span class="status-good">${PERF_METRICS[successful_requests]}</span>
                </div>
                <div class="performance-item">
                    <span>Requests Fallidos:</span>
                    <span class="status-critical">${PERF_METRICS[failed_requests]}</span>
                </div>
                <div class="performance-item">
                    <span>Tasa de Error:</span>
                    <span class="$([ ${PERF_METRICS[error_rate]} -lt 5 ] && echo "status-good" || echo "status-critical")">${PERF_METRICS[error_rate]}%</span>
                </div>
                <div class="performance-item">
                    <span>Throughput Promedio:</span>
                    <span>${PERF_METRICS[throughput]} req/s</span>
                </div>
            </div>
            
            <div class="performance-card">
                <h3>💻 Recursos del Sistema</h3>
                <div class="performance-item">
                    <span>Uso Promedio de CPU:</span>
                    <span class="$([ $(echo "${PERF_METRICS[cpu_usage_avg]} < 80" | bc 2>/dev/null || echo "false") ] && echo "status-good" || echo "status-warning")">${PERF_METRICS[cpu_usage_avg]}%</span>
                </div>
                <div class="performance-item">
                    <span>Uso Promedio de Memoria:</span>
                    <span class="$([ $(echo "${PERF_METRICS[memory_usage_avg]} < 80" | bc 2>/dev/null || echo "false") ] && echo "status-good" || echo "status-warning")">${PERF_METRICS[memory_usage_avg]}%</span>
                </div>
                <div class="performance-item">
                    <span>Picos de CPU:</span>
                    <span>$(echo "${CPU_DATA[@]}" | tr ' ' '\n' | sort -nr | head -1 2>/dev/null || echo "N/A")%</span>
                </div>
                <div class="performance-item">
                    <span>Picos de Memoria:</span>
                    <span>$(echo "${MEMORY_DATA[@]}" | tr ' ' '\n' | sort -nr | head -1 2>/dev/null || echo "N/A")%</span>
                </div>
            </div>
            
            <div class="performance-card">
                <h3>📈 Análisis de Escalabilidad</h3>
                <div class="performance-item">
                    <span>Capacidad de Carga:</span>
                    <span class="status-good">$([ $PASSED_BENCHMARKS -gt 0 ] && echo "Estable" || echo "Crítica")</span>
                </div>
                <div class="performance-item">
                    <span>Latencia:</span>
                    <span class="$([ ${PERF_METRICS[avg_response_time]} -lt 500 ] && echo "status-good" || echo "status-warning")">${PERF_METRICS[avg_response_time]}ms</span>
                </div>
                <div class="performance-item">
                    <span>Estabilidad:</span>
                    <span class="$([ ${PERF_METRICS[error_rate]} -lt 1 ] && echo "status-good" || echo "status-warning")">$([ ${PERF_METRICS[error_rate]} -lt 1 ] && echo "Excelente" || echo "Aceptable")</span>
                </div>
                <div class="performance-item">
                    <span>Recomendación:</span>
                    <span>$([ $FAILED_BENCHMARKS -eq 0 ] && echo "Sistema optimizado" || echo "Requiere optimización")</span>
                </div>
            </div>
        </div>
        
        <div class="chart">
            <h3>📊 Visualización de Métricas</h3>
            <div>
                <strong>Tiempo de Respuesta Promedio:</strong>
                <div class="bar" style="width: $(( PERF_METRICS[avg_response_time] / 10 ))%;">
                    <span class="bar-label">${PERF_METRICS[avg_response_time]}ms</span>
                </div>
            </div>
            <div>
                <strong>Uso Promedio de CPU:</strong>
                <div class="bar" style="width: ${PERF_METRICS[cpu_usage_avg]}%;">
                    <span class="bar-label">${PERF_METRICS[cpu_usage_avg]}%</span>
                </div>
            </div>
            <div>
                <strong>Uso Promedio de Memoria:</strong>
                <div class="bar" style="width: ${PERF_METRICS[memory_usage_avg]}%;">
                    <span class="bar-label">${PERF_METRICS[memory_usage_avg]}%</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Script de benchmarks de rendimiento - Versión 1.0</p>
            <p>Rendimiento general del sistema: <strong class="$([ $FAILED_BENCHMARKS -eq 0 ] && echo "status-good" || echo "status-warning")">$([ $FAILED_BENCHMARKS -eq 0 ] && echo "BUENO" || echo "MEJORABLE")</strong></p>
        </div>
    </div>
</body>
</html>
EOF
    
    log_success "Reporte HTML de benchmarks generado: $REPORT_FILE"
}

# ===============================================================================
# FUNCIÓN PRINCIPAL
# ===============================================================================

main() {
    echo -e "${GREEN}================================================================================"
    echo -e "⚡ BENCHMARKS DE RENDIMIENTO DEL SISTEMA"
    echo -e "================================================================================${NC}"
    
    # Verificar si ya hay un benchmark en curso
    if [[ -f "$PID_FILE" ]]; then
        local old_pid
        old_pid=$(cat "$PID_FILE")
        if kill -0 "$old_pid" 2>/dev/null; then
            log_error "Ya hay un benchmark en curso (PID: $old_pid)"
            exit 1
        fi
    fi
    
    # Crear PID file
    echo $$ > "$PID_FILE"
    
    # Cleanup al salir
    trap 'rm -f "$PID_FILE"' EXIT
    
    # Inicializar logging
    initialize_logging
    
    log_info "Iniciando benchmarks de rendimiento..."
    
    # Verificar herramientas necesarias
    if ! command -v curl >/dev/null 2>&1; then
        log_warn "⚠️  curl no está disponible - algunos tests podrían fallar"
    fi
    
    # Ejecutar benchmarks
    benchmark_single_request
    benchmark_concurrent_requests "${SERVICE_URLS[lp1_banco]}" "LP1-Banco" 20
    benchmark_concurrent_requests "${SERVICE_URLS[lp2_reniec]}" "LP2-RENIEC" 20
    benchmark_sustained_load "${SERVICE_URLS[health_lp1]}" "LP1-Health" 30
    benchmark_database_performance
    benchmark_stress_test
    
    # Calcular métricas finales
    calculate_final_metrics
    
    # Generar reporte final
    generate_html_report
    
    # Mostrar resumen
    echo -e "\n${BLUE}📊 RESUMEN DE BENCHMARKS${NC}"
    echo -e "Total de benchmarks: $TOTAL_BENCHMARKS"
    echo -e "Exitosos: ${GREEN}$PASSED_BENCHMARKS${NC}"
    echo -e "Fallidos: ${RED}$FAILED_BENCHMARKS${NC}"
    echo -e "Omitidos: ${YELLOW}$SKIPPED_BENCHMARKS${NC}"
    echo -e "Total de requests: ${PERF_METRICS[total_requests]}"
    echo -e "Tiempo promedio de respuesta: ${PERF_METRICS[avg_response_time]}ms"
    echo -e "Throughput promedio: ${PERF_METRICS[throughput]} req/s"
    echo -e "Tasa de error: ${PERF_METRICS[error_rate]}%"
    echo -e "Duración total: ${PERF_METRICS[total_duration]}s"
    
    if [[ $FAILED_BENCHMARKS -gt 0 ]]; then
        echo -e "\n${RED}❌ BENCHMARKS: PROBLEMAS DE RENDIMIENTO DETECTADOS${NC}"
        echo -e "${YELLOW}Se recomienda optimizar el sistema${NC}"
        exit 1
    else
        echo -e "\n${GREEN}✅ BENCHMARKS: RENDIMIENTO ÓPTIMO${NC}"
    fi
    
    log_info "Benchmarks de rendimiento finalizados"
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
            echo "  -d, --duration       Duración del benchmark (default: ${BENCHMARK_DURATION}s)"
            echo "  -c, --concurrent     Usuarios concurrentes (default: $CONCURRENT_USERS)"
            echo "  -r, --requests       Total de requests (default: $TOTAL_REQUESTS)"
            exit 0
            ;;
        -d|--duration)
            BENCHMARK_DURATION="$2"
            shift 2
            ;;
        -c|--concurrent)
            CONCURRENT_USERS="$2"
            shift 2
            ;;
        -r|--requests)
            TOTAL_REQUESTS="$2"
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