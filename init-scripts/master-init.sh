#!/bin/bash

# =============================================================================
# SCRIPT MAESTRO DE INICIALIZACIÓN COMPLETA
# Sistema Distribuido Shibasito
# =============================================================================

set -euo pipefail

# =============================================================================
# CONFIGURACIÓN DE COLORES Y LOGGING
# =============================================================================
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="${SCRIPT_DIR}/../logs/master_init_$(date +%Y%m%d_%H%M%S).log"
readonly LOG_DIR="$(dirname "$LOG_FILE")"

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

print_header() {
    clear
    echo -e "${COLOR_BOLD}${COLOR_BLUE}"
    echo "================================================================================"
    echo "🚀 SISTEMA DISTRIBUIDO SHIBASITO - INICIALIZACIÓN MAESTRA"
    echo "================================================================================"
    echo -e "${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Script: ${COLOR_BOLD}${SCRIPT_NAME}${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Directorio: ${COLOR_BOLD}${SCRIPT_DIR}${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Log: ${COLOR_BOLD}${LOG_FILE}${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Fecha: ${COLOR_BOLD}$(date '+%Y-%m-%d %H:%M:%S')${COLOR_RESET}"
    echo ""
}

print_footer() {
    echo ""
    echo -e "${COLOR_BOLD}${COLOR_BLUE}================================================================================"
    echo -e "🎉 INICIALIZACIÓN COMPLETA FINALIZADA"
    echo -e "================================================================================${COLOR_RESET}"
    echo ""
    echo -e "${COLOR_CYAN}📋 Proceso completado:${COLOR_RESET}"
    echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} Variables de entorno configuradas"
    echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} Servicios iniciados"
    echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} Bases de datos inicializadas"
    echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} Servicios verificados"
    echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} Configuración validada"
    echo ""
    echo -e "${COLOR_CYAN}🌐 Acceso a servicios:${COLOR_RESET}"
    echo -e "  ${COLOR_BOLD}Servicio Banco LP1:${COLOR_RESET} http://localhost:8080"
    echo -e "  ${COLOR_BOLD}Servicio RENIEC LP2:${COLOR_RESET} http://localhost:8000"
    echo -e "  ${COLOR_BOLD}RabbitMQ Management:${COLOR_RESET} http://localhost:15672"
    echo -e "  ${COLOR_BOLD}Prometheus:${COLOR_RESET} http://localhost:9090"
    echo -e "  ${COLOR_BOLD}Grafana:${COLOR_RESET} http://localhost:3000"
    echo ""
    echo -e "${COLOR_CYAN}📄 Archivos generados:${COLOR_RESET}"
    echo -e "  ${COLOR_CYAN}• Log maestro: ${COLOR_BOLD}${LOG_FILE}${COLOR_RESET}"
    echo -e "  ${COLOR_CYAN}• Reporte de validación: ${COLOR_BOLD}${SCRIPT_DIR}/../logs/validation_report_*.html${COLOR_RESET}"
    echo ""
}

# =============================================================================
# FUNCIÓN DE EJECUCIÓN DE SCRIPTS
# =============================================================================
run_script() {
    local script_name=$1
    local script_description=$2
    local script_path="$SCRIPT_DIR/$script_name"
    
    log_step "Ejecutando: $script_description"
    
    if [[ ! -f "$script_path" ]]; then
        log_error "Script no encontrado: $script_path"
        return 1
    fi
    
    log_info "Ejecutando script: $script_path"
    
    if bash "$script_path" >> "$LOG_FILE" 2>&1; then
        log_success "$script_description completado exitosamente"
        return 0
    else
        log_error "$script_description falló"
        log_info "Revise el log para más detalles: $LOG_FILE"
        return 1
    fi
}

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
main() {
    local start_time=$(date +%s)
    local failed_steps=()
    
    print_header
    
    log_step "Iniciando proceso de inicialización completa"
    
    # Paso 1: Configurar variables de entorno
    log_info "PASO 1: Configuración de variables de entorno"
    if ! run_script "setup-environments.sh" "Configuración de variables de entorno"; then
        failed_steps+=("setup-environments")
    fi
    
    # Verificar si se debe continuar
    if [[ ${#failed_steps[@]} -gt 0 ]]; then
        log_error "Error en configuración de entorno. ¿Desea continuar? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            log_error "Inicialización cancelada por el usuario"
            exit 1
        fi
    fi
    
    # Paso 2: Esperar a que los servicios estén listos
    log_info "\nPASO 2: Verificación de servicios"
    if ! run_script "wait-for-services.sh" "Espera de servicios"; then
        failed_steps+=("wait-for-services")
    fi
    
    # Paso 3: Inicializar bases de datos
    log_info "\nPASO 3: Inicialización de bases de datos"
    if ! run_script "init-all-databases.sh" "Inicialización de bases de datos"; then
        failed_steps+=("init-all-databases")
    fi
    
    # Paso 4: Validar configuración completa
    log_info "\nPASO 4: Validación de configuración"
    if ! run_script "validate-setup.sh" "Validación de configuración"; then
        failed_steps+=("validate-setup")
    fi
    
    # Resumen final
    local end_time=$(date +%s)
    local total_time=$((end_time - start_time))
    
    print_footer
    
    if [[ ${#failed_steps[@]} -eq 0 ]]; then
        log_success "🎉 ¡INICIALIZACIÓN COMPLETADA EXITOSAMENTE!"
        log_info "⏱️ Tiempo total: ${total_time} segundos"
        log_info "🚀 Todos los servicios están listos para usar"
        exit 0
    else
        log_error "❌ INICIALIZACIÓN COMPLETADA CON ERRORES"
        log_error "Pasos fallidos: ${failed_steps[*]}"
        log_info "⏱️ Tiempo total: ${total_time} segundos"
        log_info "📄 Revise los logs para más detalles"
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