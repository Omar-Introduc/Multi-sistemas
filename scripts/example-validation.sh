#!/bin/bash

# ===============================================================================
# SCRIPT DE EJEMPLO: VALIDACIÓN INTEGRAL DEL SISTEMA
# ===============================================================================
# Este script demuestra cómo implementar una validación integral usando
# los scripts de validación del sistema. Puede ser usado como template
# para implementar validación en pipelines CI/CD.
# ===============================================================================

set -euo pipefail

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="${SCRIPT_DIR}/logs/example-integration-${TIMESTAMP}.log"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Función de logging
log() {
    local level="$1"
    shift
    local message="$*"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() { log "INFO" "$@"; }
log_success() { log "SUCCESS" "$@"; }
log_error() { log "ERROR" "$@"; }

# ===============================================================================
# VALIDACIÓN BÁSICA DEL SISTEMA
# ===============================================================================

run_basic_validation() {
    log_info "🚀 Iniciando validación básica del sistema..."
    
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}🔍 VALIDACIÓN BÁSICA${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    
    # 1. Validación rápida del sistema
    if [[ -f "${SCRIPT_DIR}/validate-system.sh" ]]; then
        log_info "Ejecutando validación rápida del sistema..."
        if timeout 120 "${SCRIPT_DIR}/validate-system.sh" --quiet; then
            log_success "✅ Validación básica del sistema: EXITOSA"
        else
            log_error "❌ Validación básica del sistema: FALLÓ"
            return 1
        fi
    else
        log_error "Script validate-system.sh no encontrado"
        return 1
    fi
    
    # 2. Test de comunicación básico
    if [[ -f "${SCRIPT_DIR}/test-communication-flows.sh" ]]; then
        log_info "Ejecutando test de comunicación básico..."
        if timeout 60 "${SCRIPT_DIR}/test-communication-flows.sh" --timeout 15; then
            log_success "✅ Test de comunicación: EXITOSO"
        else
            log_error "❌ Test de comunicación: FALLÓ"
            return 1
        fi
    fi
    
    log_success "Validación básica completada"
}

# ===============================================================================
# VALIDACIÓN COMPLETA (PARA PIPELINES PRINCIPALES)
# ===============================================================================

run_full_validation() {
    log_info "🚀 Iniciando validación completa del sistema..."
    
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}🏆 VALIDACIÓN COMPLETA${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    
    # Verificar que existe el script maestro
    if [[ ! -f "${SCRIPT_DIR}/master-validation.sh" ]]; then
        log_error "Script master-validation.sh no encontrado"
        return 1
    fi
    
    # Ejecutar validación completa
    log_info "Ejecutando validación maestra completa..."
    if timeout 1800 "${SCRIPT_DIR}/master-validation.sh" --parallel --retry; then
        log_success "✅ Validación completa: EXITOSA"
    else
        log_error "❌ Validación completa: FALLÓ"
        return 1
    fi
    
    log_success "Validación completa finalizada"
}

# ===============================================================================
# VALIDACIÓN DE PERFORMANCE (PARA RELEASES)
# ===============================================================================

run_performance_validation() {
    log_info "🚀 Iniciando validación de performance..."
    
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}⚡ VALIDACIÓN DE PERFORMANCE${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    
    # Benchmarks de rendimiento
    if [[ -f "${SCRIPT_DIR}/performance-benchmark.sh" ]]; then
        log_info "Ejecutando benchmarks de rendimiento..."
        if timeout 900 "${SCRIPT_DIR}/performance-benchmark.sh" --duration 120 --concurrent 15; then
            log_success "✅ Benchmarks de rendimiento: COMPLETADOS"
        else
            log_error "❌ Benchmarks de rendimiento: FALLARON"
            return 1
        fi
    fi
    
    log_success "Validación de performance finalizada"
}

# ===============================================================================
# VALIDACIÓN DE RESILIENCIA (PARA TESTING AVANZADO)
# ===============================================================================

run_resilience_validation() {
    log_info "🚀 Iniciando validación de resiliencia..."
    
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}🛡️ VALIDACIÓN DE RESILIENCIA${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    
    # Testing de escenarios de fallo
    if [[ -f "${SCRIPT_DIR}/test-failure-scenarios.sh" ]]; then
        log_info "Ejecutando testing de escenarios de fallo..."
        if timeout 600 "${SCRIPT_DIR}/test-failure-scenarios.sh" --dry-run --timeout 120; then
            log_success "✅ Testing de escenarios de fallo: COMPLETADO"
        else
            log_error "❌ Testing de escenarios de fallo: FALLÓ"
            return 1
        fi
    fi
    
    log_success "Validación de resiliencia finalizada"
}

# ===============================================================================
# VALIDACIÓN PARA DESARROLLO RÁPIDO
# ===============================================================================

run_quick_validation() {
    log_info "🚀 Iniciando validación rápida para desarrollo..."
    
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}⚡ VALIDACIÓN RÁPIDA${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    
    # Solo validación básica sin tests destructivos
    if [[ -f "${SCRIPT_DIR}/validate-system.sh" ]]; then
        log_info "Ejecutando validación rápida..."
        if timeout 60 "${SCRIPT_DIR}/validate-system.sh" --quiet; then
            log_success "✅ Validación rápida: EXITOSA"
        else
            log_error "❌ Validación rápida: FALLÓ"
            return 1
        fi
    fi
    
    log_success "Validación rápida finalizada"
}

# ===============================================================================
# GENERACIÓN DE REPORTES CONSOLIDADOS
# ===============================================================================

generate_consolidated_report() {
    log_info "📊 Generando reportes consolidados..."
    
    if [[ -f "${SCRIPT_DIR}/generate-system-report.sh" ]]; then
        log_info "Generando reporte del sistema..."
        if timeout 120 "${SCRIPT_DIR}/generate-system-report.sh" 24h; then
            log_success "✅ Reporte del sistema generado"
        else
            log_error "❌ Error generando reporte del sistema"
            return 1
        fi
    fi
    
    log_success "Reportes consolidados generados"
}

# ===============================================================================
# FUNCIÓN PRINCIPAL
# ===============================================================================

main() {
    echo -e "${GREEN}================================================================================"
    echo -e "🚀 EJEMPLO DE VALIDACIÓN INTEGRAL DEL SISTEMA"
    echo -e "================================================================================${NC}"
    echo ""
    echo -e "${YELLOW}Tipos de validación disponibles:${NC}"
    echo "  1. Básica      - Validación rápida para desarrollo"
    echo "  2. Completa    - Validación integral para producción"
    echo "  3. Performance - Benchmarks de rendimiento"
    echo "  4. Resiliencia - Testing de tolerancia a fallos"
    echo "  5. Rápida      - Validación express para commits"
    echo ""
    
    # Determinar tipo de validación
    local validation_type="${1:-basica}"
    
    case "$validation_type" in
        "1"|"basica"|"básica")
            log_info "Ejecutando validación básica..."
            run_basic_validation
            ;;
        "2"|"completa"|"full")
            log_info "Ejecutando validación completa..."
            run_full_validation
            ;;
        "3"|"performance"|"perf")
            log_info "Ejecutando validación de performance..."
            run_performance_validation
            ;;
        "4"|"resiliencia"|"resilience")
            log_info "Ejecutando validación de resiliencia..."
            run_resilience_validation
            ;;
        "5"|"rapida"|"rápida"|"quick"|"express")
            log_info "Ejecutando validación rápida..."
            run_quick_validation
            ;;
        "help"|"-h"|"--help")
            echo "Uso: $0 [tipo_validacion]"
            echo ""
            echo "Tipos de validación:"
            echo "  basica      - Validación básica del sistema"
            echo "  completa    - Validación completa con todos los tests"
            echo "  performance - Benchmarks de rendimiento"
            echo "  resiliencia - Testing de tolerancia a fallos"
            echo "  rapida      - Validación express para desarrollo"
            echo ""
            echo "Ejemplos:"
            echo "  $0                  # Validación básica"
            echo "  $0 completa         # Validación completa"
            echo "  $0 performance      # Solo benchmarks"
            echo "  $0 rapida           # Validación rápida"
            exit 0
            ;;
        *)
            log_error "Tipo de validación no reconocido: $validation_type"
            echo "Usar '$0 help' para ver opciones disponibles"
            exit 1
            ;;
    esac
    
    # Generar reportes siempre
    generate_consolidated_report || true
    
    echo ""
    echo -e "${GREEN}================================================================================${NC}"
    echo -e "${GREEN}✅ VALIDACIÓN COMPLETADA${NC}"
    echo -e "${GREEN}================================================================================${NC}"
    echo ""
    echo -e "${BLUE}📊 Archivos generados:${NC}"
    echo "  📝 Log principal: $LOG_FILE"
    echo "  📋 Reportes: ${SCRIPT_DIR}/reports/"
    echo "  📁 Logs detallados: ${SCRIPT_DIR}/logs/"
    echo ""
    echo -e "${YELLOW}💡 Próximos pasos:${NC}"
    echo "  1. Revisar logs en: ${SCRIPT_DIR}/logs/"
    echo "  2. Abrir reportes HTML en: ${SCRIPT_DIR}/reports/"
    echo "  3. Configurar monitoreo continuo con: ${SCRIPT_DIR}/continuous-validation.sh"
    echo ""
}

# ===============================================================================
# EJEMPLO DE INTEGRACIÓN EN CI/CD
# ===============================================================================

# Este script puede ser integrado en pipelines CI/CD de la siguiente manera:

# GitLab CI/CD:
# validate_system:
#   stage: test
#   script:
#     - ./scripts/example-validation.sh completa
#   artifacts:
#     reports:
#       junit: reports/junit.xml
#     paths:
#       - reports/
#       - logs/
#     expire_in: 1 week

# Jenkins Pipeline:
# pipeline {
#     agent any
#     stages {
#         stage('Validate System') {
#             steps {
#                 sh './scripts/example-validation.sh completa'
#             }
#             post {
#                 always {
#                     archiveArtifacts artifacts: 'reports/**, logs/**', allowEmptyArchive: true
#                 }
#             }
#         }
#     }
# }

# GitHub Actions:
# - name: Validate System
#   run: ./scripts/example-validation.sh completa
# - name: Upload Reports
#   uses: actions/upload-artifact@v3
#   with:
#     name: validation-reports
#     path: |
#       reports/
#       logs/

# ===============================================================================
# EJECUCIÓN
# ===============================================================================

main "$@"