#!/bin/bash

# ===============================================================================
# SCRIPT MAESTRO DE VALIDACIÓN COMPLETA DEL SISTEMA
# ===============================================================================
# Funcionalidades:
# - Ejecuta todos los scripts de validación del sistema
# - Orchestration completa de tests
# - Reportes consolidados
# - Control de errores y recovery
# - Ejecución paralela o secuencial
# ===============================================================================

set -euo pipefail

# Configuración global
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
MASTER_LOG_DIR="${SCRIPT_DIR}/logs/master-validation"
REPORT_DIR="${SCRIPT_DIR}/reports/master"
MASTER_LOG_FILE="${MASTER_LOG_DIR}/master-validation_${TIMESTAMP}.log"
MASTER_REPORT_FILE="${REPORT_DIR}/master-report_${TIMESTAMP}.html"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Scripts de validación disponibles
declare -A VALIDATION_SCRIPTS
VALIDATION_SCRIPTS[system_validation]="validate-system.sh"
VALIDATION_SCRIPTS[communication_flows]="test-communication-flows.sh"
VALIDATION_SCRIPTS[failure_scenarios]="test-failure-scenarios.sh"
VALIDATION_SCRIPTS[performance_benchmark]="performance-benchmark.sh"
VALIDATION_SCRIPTS[system_report]="generate-system-report.sh"

# Variables de estado
TOTAL_SCRIPTS=0
COMPLETED_SCRIPTS=0
FAILED_SCRIPTS=0
SKIPPED_SCRIPTS=0
START_TIME=$(date +%s)
PARALLEL_MODE=false
INTERACTIVE_MODE=true

# Configuración de ejecución
TIMEOUT_DEFAULT=300  # 5 minutos por script
RETRY_FAILED=false
CLEANUP_ON_EXIT=true

# Arrays para tracking
declare -a SCRIPT_RESULTS
declare -a SCRIPT_TIMES
declare -a SCRIPT_OUTPUTS

# ===============================================================================
# FUNCIONES DE LOGGING
# ===============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$MASTER_LOG_FILE"
}

log_info() { log "INFO" "$@"; }
log_warn() { log "WARN" "$@"; }
log_error() { log "ERROR" "$@"; }
log_success() { log "SUCCESS" "$@"; }
log_exec() { log "EXEC" "$@"; }

initialize_logging() {
    mkdir -p "$MASTER_LOG_DIR" "$REPORT_DIR"
    
    cat > "$MASTER_LOG_FILE" << EOF
================================================================================
VALIDACIÓN MAESTRA DEL SISTEMA - INICIADA
Timestamp: $(date '+%Y-%m-%d %H:%M:%S')
Script: $0
Modo paralelo: $PARALLEL_MODE
Modo interactivo: $INTERACTIVE_MODE
================================================================================

EOF
    log_info "Sistema de logging maestro inicializado: $MASTER_LOG_FILE"
}

# ===============================================================================
# EJECUCIÓN DE SCRIPTS
# ===============================================================================

execute_script() {
    local script_name="$1"
    local script_path="$2"
    local timeout="${3:-$TIMEOUT_DEFAULT}"
    
    log_exec "Ejecutando script: $script_name"
    log_info "Ruta: $script_path"
    log_info "Timeout: ${timeout}s"
    
    local start_time=$(date +%s)
    local output_file="${MASTER_LOG_DIR}/${script_name}_${TIMESTAMP}.log"
    local exit_code=0
    
    # Ejecutar script con timeout
    if [[ "$INTERACTIVE_MODE" == "true" ]]; then
        echo -e "\n${CYAN}========================================${NC}"
        echo -e "${CYAN}Ejecutando: $script_name${NC}"
        echo -e "${CYAN}========================================${NC}\n"
    fi
    
    if timeout "$timeout" bash "$script_path" > "$output_file" 2>&1; then
        exit_code=0
        log_success "✅ $script_name completado exitosamente"
    else
        exit_code=$?
        if [[ $exit_code -eq 124 ]]; then
            log_error "❌ $script_name excedió el timeout de ${timeout}s"
        else
            log_error "❌ $script_name falló con código de salida: $exit_code"
        fi
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Guardar resultado
    SCRIPT_RESULTS+=("{\"script\":\"$script_name\",\"status\":\"$([[ $exit_code -eq 0 ]] && echo "SUCCESS" || echo "FAILED")\",\"exit_code\":$exit_code,\"duration\":$duration}")
    SCRIPT_TIMES+=("$duration")
    SCRIPT_OUTPUTS+=("$output_file")
    
    if [[ "$INTERACTIVE_MODE" == "true" ]]; then
        if [[ $exit_code -eq 0 ]]; then
            echo -e "${GREEN}✅ Completado en ${duration}s${NC}\n"
        else
            echo -e "${RED}❌ Falló en ${duration}s${NC}\n"
        fi
    fi
    
    return $exit_code
}

execute_scripts_sequential() {
    log_info "Ejecutando scripts en modo secuencial..."
    
    for script_name in "${!VALIDATION_SCRIPTS[@]}"; do
        local script_path="${SCRIPT_DIR}/${VALIDATION_SCRIPTS[$script_name]}"
        
        if [[ ! -f "$script_path" ]]; then
            log_warn "Script no encontrado: $script_path"
            SKIPPED_SCRIPTS=$((SKIPPED_SCRIPTS + 1))
            continue
        fi
        
        TOTAL_SCRIPTS=$((TOTAL_SCRIPTS + 1))
        
        if execute_script "$script_name" "$script_path"; then
            COMPLETED_SCRIPTS=$((COMPLETED_SCRIPTS + 1))
        else
            FAILED_SCRIPTS=$((FAILED_SCRIPTS + 1))
            
            if [[ "$RETRY_FAILED" == "true" ]]; then
                log_info "Reintentando $script_name..."
                sleep 5
                if execute_script "$script_name" "$script_path"; then
                    log_info "$script_name exitoso en el reintento"
                    COMPLETED_SCRIPTS=$((COMPLETED_SCRIPTS + 1))
                    FAILED_SCRIPTS=$((FAILED_SCRIPTS - 1))
                else
                    log_error "$script_name falló nuevamente"
                fi
            fi
        fi
        
        # Pausa entre scripts
        sleep 2
    done
}

execute_scripts_parallel() {
    log_info "Ejecutando scripts en modo paralelo..."
    
    local pids=()
    local script_count=0
    
    for script_name in "${!VALIDATION_SCRIPTS[@]}"; do
        local script_path="${SCRIPT_DIR}/${VALIDATION_SCRIPTS[$script_name]}"
        
        if [[ ! -f "$script_path" ]]; then
            log_warn "Script no encontrado: $script_path"
            SKIPPED_SCRIPTS=$((SKIPPED_SCRIPTS + 1))
            continue
        fi
        
        TOTAL_SCRIPTS=$((TOTAL_SCRIPTS + 1))
        
        # Ejecutar en background
        {
            local start_time=$(date +%s)
            local output_file="${MASTER_LOG_DIR}/${script_name}_${TIMESTAMP}.log"
            
            if timeout "$TIMEOUT_DEFAULT" bash "$script_path" > "$output_file" 2>&1; then
                local exit_code=0
                local status="SUCCESS"
            else
                local exit_code=$?
                local status="FAILED"
                if [[ $exit_code -eq 124 ]]; then
                    status="TIMEOUT"
                fi
            fi
            
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            
            # Guardar resultado en archivo temporal
            echo "{\"script\":\"$script_name\",\"status\":\"$status\",\"exit_code\":$exit_code,\"duration\":$duration}" > "/tmp/result_${script_name}.txt"
        } &
        
        pids+=("$!")
        script_count=$((script_count + 1))
        
        # Pausa inicial entre lanzamientos
        sleep 1
    done
    
    # Esperar a que todos los procesos terminen
    for pid in "${pids[@]}"; do
        wait "$pid"
    done
    
    # Recopilar resultados
    for script_name in "${!VALIDATION_SCRIPTS[@]}"; do
        local result_file="/tmp/result_${script_name}.txt"
        if [[ -f "$result_file" ]]; then
            local result
            result=$(cat "$result_file")
            SCRIPT_RESULTS+=("$result")
            
            local status
            status=$(echo "$result" | jq -r '.status' 2>/dev/null || echo "UNKNOWN")
            local duration
            duration=$(echo "$result" | jq -r '.duration' 2>/dev/null || echo "0")
            
            SCRIPT_TIMES+=("$duration")
            
            case "$status" in
                "SUCCESS")
                    COMPLETED_SCRIPTS=$((COMPLETED_SCRIPTS + 1))
                    log_success "✅ $script_name completado en ${duration}s"
                    ;;
                "FAILED"|"TIMEOUT")
                    FAILED_SCRIPTS=$((FAILED_SCRIPTS + 1))
                    log_error "❌ $script_name falló en ${duration}s"
                    ;;
                *)
                    SKIPPED_SCRIPTS=$((SKIPPED_SCRIPTS + 1))
                    log_warn "⏭️  $script_name omitido"
                    ;;
            esac
            
            rm -f "$result_file"
        fi
    done
}

# ===============================================================================
# GENERACIÓN DE REPORTE MAESTRO
# ===============================================================================

generate_master_report() {
    log_info "Generando reporte maestro..."
    
    local end_time=$(date +%s)
    local total_duration=$((end_time - START_TIME))
    
    # Calcular promedios
    local avg_duration=0
    if [[ ${#SCRIPT_TIMES[@]} -gt 0 ]]; then
        local total_time=0
        for time in "${SCRIPT_TIMES[@]}"; do
            total_time=$((total_time + time))
        done
        avg_duration=$((total_time / ${#SCRIPT_TIMES[@]}))
    fi
    
    # Determinar estado general
    local overall_status="success"
    local status_color="green"
    
    if [[ $FAILED_SCRIPTS -gt 0 ]]; then
        overall_status="failed"
        status_color="red"
    elif [[ $SKIPPED_SCRIPTS -gt 0 ]]; then
        overall_status="partial"
        status_color="orange"
    fi
    
    cat > "$MASTER_REPORT_FILE" << EOF
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Maestro de Validación del Sistema</title>
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
        .status-success { background: #28a745; }
        .status-failed { background: #dc3545; }
        .status-partial { background: #ffc107; color: #333; }
        
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
        
        .scripts-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin: 30px 0;
        }
        .script-card { 
            background: #f8f9fa; 
            padding: 25px; 
            border-radius: 12px; 
            border-left: 5px solid #17a2b8;
        }
        .script-card h3 { 
            margin-top: 0; 
            color: #333; 
            text-transform: capitalize;
        }
        .script-status { 
            padding: 10px; 
            margin: 8px 0; 
            border-radius: 8px; 
            font-weight: 500;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .status-success { 
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            color: #155724; 
        }
        .status-failed { 
            background: linear-gradient(135deg, #f8d7da, #f5c6cb);
            color: #721c24; 
        }
        .status-partial { 
            background: linear-gradient(135deg, #fff3cd, #ffeaa7);
            color: #856404; 
        }
        .status-skipped { 
            background: linear-gradient(135deg, #e2e3e5, #d6d8db);
            color: #383d41; 
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin: 20px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }
        
        .summary-section {
            background: linear-gradient(135deg, #e3f2fd, #bbdefb);
            padding: 25px;
            border-radius: 12px;
            margin: 30px 0;
            border-left: 5px solid #2196f3;
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
        
        @media (max-width: 768px) {
            .scripts-grid {
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
            <h1>🏆 Reporte Maestro de Validación del Sistema</h1>
            <div class="timestamp">Generado el: $(date '+%Y-%m-%d %H:%M:%S')</div>
            <div class="status-badge status-$([ "$overall_status" = "success" ] && echo "success" || [ "$overall_status" = "partial" ] && echo "partial" || echo "failed")">
                Estado: $(echo "$overall_status" | tr '[:lower:]' '[:upper:]')
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: $((COMPLETED_SCRIPTS * 100 / TOTAL_SCRIPTS))%"></div>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">$TOTAL_SCRIPTS</div>
                <div class="metric-label">Total de Scripts</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #28a745;">$COMPLETED_SCRIPTS</div>
                <div class="metric-label">Exitosos</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #dc3545;">$FAILED_SCRIPTS</div>
                <div class="metric-label">Fallidos</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #6c757d;">$SKIPPED_SCRIPTS</div>
                <div class="metric-label">Omitidos</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${total_duration}s</div>
                <div class="metric-label">Duración Total</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${avg_duration}s</div>
                <div class="metric-label">Duración Promedio</div>
            </div>
        </div>
        
        <div class="scripts-grid">
EOF

    # Agregar tarjetas de scripts
    for script_name in "${!VALIDATION_SCRIPTS[@]}"; do
        local script_path="${SCRIPT_DIR}/${VALIDATION_SCRIPTS[$script_name]}"
        local status="skipped"
        local duration="N/A"
        local status_class="status-skipped"
        
        # Buscar resultado para este script
        for result in "${SCRIPT_RESULTS[@]}"; do
            local script_result_name
            script_result_name=$(echo "$result" | jq -r '.script' 2>/dev/null || echo "")
            if [[ "$script_result_name" == "$script_name" ]]; then
                status=$(echo "$result" | jq -r '.status' 2>/dev/null || echo "UNKNOWN")
                duration=$(echo "$result" | jq -r '.duration' 2>/dev/null || echo "0")
                
                case "$status" in
                    "SUCCESS")
                        status_class="status-success"
                        ;;
                    "FAILED"|"TIMEOUT")
                        status_class="status-failed"
                        ;;
                    *)
                        status_class="status-partial"
                        ;;
                esac
                break
            fi
        done
        
        # Determinar icono y texto de estado
        local status_icon
        local status_text
        case "$status" in
            "SUCCESS")
                status_icon="✅"
                status_text="Exitoso"
                ;;
            "FAILED"|"TIMEOUT")
                status_icon="❌"
                status_text="Fallido"
                ;;
            *)
                status_icon="⏭️"
                status_text="Omitido"
                ;;
        esac
        
        # Capitalizar nombre del script
        local display_name
        display_name=$(echo "$script_name" | tr '_' ' ' | sed 's/\b\w/\U&/g')
        
        cat >> "$MASTER_REPORT_FILE" << EOF
            <div class="script-card">
                <h3>$display_name</h3>
                <div class="script-status $status_class">
                    <span>$status_icon $status_text</span>
                    <span>${duration}s</span>
                </div>
                <div style="font-size: 0.9em; color: #666; margin-top: 10px;">
                    Script: ${VALIDATION_SCRIPTS[$script_name]}
                </div>
            </div>
EOF
    done

    cat >> "$MASTER_REPORT_FILE" << EOF
        </div>
        
        <div class="summary-section">
            <h3>📋 Resumen Ejecutivo</h3>
            <p><strong>Estado General:</strong> $overall_status</p>
            <p><strong>Duración Total:</strong> ${total_duration} segundos</p>
            <p><strong>Tasa de Éxito:</strong> $(( TOTAL_SCRIPTS > 0 ? (COMPLETED_SCRIPTS * 100 / TOTAL_SCRIPTS) : 0 ))%</p>
            <p><strong>Modo de Ejecución:</strong> $PARALLEL_MODE && echo "Paralelo" || echo "Secuencial"</p>
            
            <h4>💡 Recomendaciones:</h4>
            <ul>
                $([ $FAILED_SCRIPTS -eq 0 ] && echo '<li>✅ Todos los scripts ejecutados exitosamente</li>' || echo '<li>⚠️ Revisar scripts fallidos y resolver problemas identificados</li>')
                <li>📊 Revisar logs detallados en: $MASTER_LOG_DIR</li>
                <li>📈 Monitorear métricas de rendimiento regularmente</li>
                <li>🔄 Programar ejecuciones automáticas para validación continua</li>
            </ul>
        </div>
        
        <div class="footer">
            <h4>📋 Información de Ejecución</h4>
            <p><strong>Scripts disponibles:</strong> ${#VALIDATION_SCRIPTS[@]}</p>
            <p><strong>Logs maestros:</strong> $MASTER_LOG_FILE</p>
            <p><strong>Reportes individuales:</strong> $SCRIPT_DIR/reports/</p>
            <p><em>Este reporte se generó automáticamente como parte de la validación maestra del sistema.</em></p>
        </div>
    </div>
</body>
</html>
EOF
    
    log_success "Reporte maestro generado: $MASTER_REPORT_FILE"
}

# ===============================================================================
# FUNCIÓN PRINCIPAL
# ===============================================================================

main() {
    echo -e "${MAGENTA}================================================================================"
    echo -e "🏆 VALIDACIÓN MAESTRA DEL SISTEMA"
    echo -e "================================================================================${NC}"
    
    # Inicializar logging
    initialize_logging
    
    log_info "Iniciando validación maestra del sistema..."
    log_info "Scripts disponibles: ${#VALIDATION_SCRIPTS[@]}"
    log_info "Modo paralelo: $PARALLEL_MODE"
    
    # Mostrar información de scripts
    echo -e "\n${BLUE}📋 SCRIPTS DE VALIDACIÓN DISPONIBLES:${NC}"
    for script_name in "${!VALIDATION_SCRIPTS[@]}"; do
        local script_path="${SCRIPT_DIR}/${VALIDATION_SCRIPTS[$script_name]}"
        local status="❌ No encontrado"
        
        if [[ -f "$script_path" ]]; then
            status="✅ Disponible"
        fi
        
        echo -e "  ${CYAN}$script_name${NC}: ${VALIDATION_SCRIPTS[$script_name]} ($status)"
    done
    
    # Ejecutar scripts
    echo -e "\n${YELLOW}🚀 INICIANDO EJECUCIÓN...${NC}\n"
    
    if [[ "$PARALLEL_MODE" == "true" ]]; then
        execute_scripts_parallel
    else
        execute_scripts_sequential
    fi
    
    # Generar reporte final
    generate_master_report
    
    # Mostrar resumen
    echo -e "\n${BLUE}📊 RESUMEN FINAL${NC}"
    echo -e "Total de scripts: $TOTAL_SCRIPTS"
    echo -e "Exitosos: ${GREEN}$COMPLETED_SCRIPTS${NC}"
    echo -e "Fallidos: ${RED}$FAILED_SCRIPTS${NC}"
    echo -e "Omitidos: ${YELLOW}$SKIPPED_SCRIPTS${NC}"
    echo -e "Tiempo total: $(( $(date +%s) - START_TIME ))s"
    echo -e "Log maestro: $MASTER_LOG_FILE"
    echo -e "Reporte maestro: $MASTER_REPORT_FILE"
    
    # Determinar resultado final
    if [[ $FAILED_SCRIPTS -eq 0 ]]; then
        echo -e "\n${GREEN}✅ VALIDACIÓN MAESTRA: COMPLETADA EXITOSAMENTE${NC}"
        exit 0
    else
        echo -e "\n${RED}❌ VALIDACIÓN MAESTRA: ALGUNOS SCRIPTS FALLARON${NC}"
        echo -e "${YELLOW}Revisar logs para detalles${NC}"
        exit 1
    fi
    
    log_info "Validación maestra completada"
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
            echo "  -p, --parallel       Ejecutar scripts en paralelo"
            echo "  -s, --sequential     Ejecutar scripts secuencialmente (default)"
            echo "  -r, --retry          Reintentar scripts fallidos"
            echo "  -q, --quiet          Modo silencioso"
            echo "  -t, --timeout        Timeout por script en segundos (default: ${TIMEOUT_DEFAULT})"
            echo ""
            echo "Ejemplos:"
            echo "  $0                   # Ejecución secuencial"
            echo "  $0 -p                # Ejecución paralela"
            echo "  $0 -p -r             # Paralela con reintentos"
            echo "  $0 -t 600            # Timeout de 10 minutos"
            exit 0
            ;;
        -p|--parallel)
            PARALLEL_MODE=true
            shift
            ;;
        -s|--sequential)
            PARALLEL_MODE=false
            shift
            ;;
        -r|--retry)
            RETRY_FAILED=true
            shift
            ;;
        -q|--quiet)
            INTERACTIVE_MODE=false
            shift
            ;;
        -t|--timeout)
            TIMEOUT_DEFAULT="$2"
            shift 2
            ;;
        *)
            log_error "Opción desconocida: $1"
            exit 1
            ;;
    esac
done

# Verificar scripts disponibles
for script_name in "${!VALIDATION_SCRIPTS[@]}"; do
    local script_path="${SCRIPT_DIR}/${VALIDATION_SCRIPTS[$script_name]}"
    if [[ ! -f "$script_path" ]]; then
        log_warn "Script no encontrado: $script_path"
    fi
done

# Ejecutar función principal
main "$@"