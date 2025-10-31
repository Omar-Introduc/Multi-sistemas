#!/bin/bash

# =============================================================================
# SCRIPT DE LIMPIEZA Y MANTENIMIENTO
# Sistema Distribuido Shibasito
# =============================================================================

set -euo pipefail

# =============================================================================
# CONFIGURACIÓN DE COLORES Y LOGGING
# =============================================================================
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="${SCRIPT_DIR}/../logs/cleanup_$(date +%Y%m%d_%H%M%S).log"

# Crear directorio de logs si no existe
mkdir -p "$(dirname "$LOG_FILE")"

# Colores para output
readonly COLOR_RESET='\033[0m'
readonly COLOR_RED='\033[0;31m'
readonly COLOR_GREEN='\033[0;32m'
readonly COLOR_YELLOW='\033[0;33m'
readonly COLOR_BLUE='\033[0;34m'
readonly COLOR_CYAN='\033[0;36m'
readonly COLOR_BOLD='\033[1m'

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================
log_info() {
    echo -e "${COLOR_CYAN}[INFO]${COLOR_RESET} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${COLOR_GREEN}[SUCCESS]${COLOR_RESET} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${COLOR_YELLOW}[WARNING]${COLOR_RESET} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${COLOR_RED}[ERROR]${COLOR_RESET} $1" | tee -a "$LOG_FILE"
}

print_header() {
    clear
    echo -e "${COLOR_BOLD}${COLOR_BLUE}"
    echo "================================================================================"
    echo "🧹 SISTEMA DISTRIBUIDO SHIBASITO - LIMPIEZA Y MANTENIMIENTO"
    echo "================================================================================"
    echo -e "${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Fecha: ${COLOR_BOLD}$(date '+%Y-%m-%d %H:%M:%S')${COLOR_RESET}"
    echo ""
}

get_disk_usage() {
    echo "$(du -sh "$1" 2>/dev/null | cut -f1)"
}

clean_logs() {
    echo -e "${COLOR_CYAN}🧹 Limpiando archivos de logs antiguos...${COLOR_RESET}"
    
    local log_dir="$SCRIPT_DIR/../logs"
    local max_age_days=7
    
    if [[ -d "$log_dir" ]]; then
        local log_count_before=$(find "$log_dir" -type f | wc -l)
        local size_before=$(get_disk_usage "$log_dir")
        
        log_info "Archivos antes: $log_count_before"
        log_info "Tamaño antes: $size_before"
        
        # Limpiar logs más antiguos que 7 días
        find "$log_dir" -name "*.log" -mtime +$max_age_days -delete 2>/dev/null || true
        find "$log_dir" -name "*.html" -mtime +$max_age_days -delete 2>/dev/null || true
        
        local log_count_after=$(find "$log_dir" -type f | wc -l)
        local size_after=$(get_disk_usage "$log_dir")
        
        log_success "Archivos después: $log_count_after"
        log_success "Tamaño después: $size_after"
    else
        log_warning "Directorio de logs no encontrado: $log_dir"
    fi
}

clean_docker() {
    echo -e "${COLOR_CYAN}🐳 Limpiando recursos de Docker...${COLOR_RESET}"
    
    # Limpiar contenedores detenidos
    local stopped_containers=$(docker ps -a --filter "status=exited" --format "{{.Names}}" | wc -l)
    if [[ $stopped_containers -gt 0 ]]; then
        log_info "Eliminando $stopped_containers contenedores detenidos..."
        docker container prune -f >> "$LOG_FILE" 2>&1
    fi
    
    # Limpiar imágenes no utilizadas
    local unused_images=$(docker images --filter "dangling=true" --format "{{.Repository}}:{{.Tag}}" | wc -l)
    if [[ $unused_images -gt 0 ]]; then
        log_info "Eliminando $unused_images imágenes no utilizadas..."
        docker image prune -f >> "$LOG_FILE" 2>&1
    fi
    
    # Limpiar redes no utilizadas
    local unused_networks=$(docker network ls --filter "name=shibasito" --format "{{.Name}}" | wc -l)
    log_info "Verificando redes de Shibasito: $unused_networks encontradas"
    
    # Limpiar volúmenes huérfanos
    log_info "Limpiando volúmenes huérfanos..."
    docker volume prune -f >> "$LOG_FILE" 2>&1
    
    # Limpiar cache de build
    log_info "Limpiando cache de build..."
    docker builder prune -f >> "$LOG_FILE" 2>&1
}

system_cleanup() {
    echo -e "${COLOR_CYAN}💾 Limpiando archivos temporales del sistema...${COLOR_RESET}"
    
    # Limpiar archivos temporales en /tmp (solo los relacionados con shibasito)
    local tmp_files=$(find /tmp -name "*shibasito*" -type f 2>/dev/null | wc -l)
    if [[ $tmp_files -gt 0 ]]; then
        log_info "Eliminando $tmp_files archivos temporales de shibasito..."
        find /tmp -name "*shibasito*" -type f -delete 2>/dev/null || true
    fi
    
    # Limpiar cache de bash
    if [[ -f ~/.bash_cache ]]; then
        rm -f ~/.bash_cache
    fi
}

show_system_stats() {
    echo -e "${COLOR_CYAN}📊 Estadísticas del sistema:${COLOR_RESET}"
    
    # Docker stats
    echo ""
    echo -e "${COLOR_BOLD}Docker:${COLOR_RESET}"
    echo -e "  ${COLOR_CYAN}Contenedores:${COLOR_RESET} $(docker ps -a --format '{{.Names}}' | wc -l) total, $(docker ps --format '{{.Names}}' | wc -l) ejecutándose"
    echo -e "  ${COLOR_CYAN}Imágenes:${COLOR_RESET} $(docker images --format '{{.Repository}}:{{.Tag}}' | wc -l)"
    echo -e "  ${COLOR_CYAN}Volúmenes:${COLOR_RESET} $(docker volume ls --format '{{.Name}}' | wc -l)"
    echo -e "  ${COLOR_CYAN}Redes:${COLOR_RESET} $(docker network ls --format '{{.Name}}' | wc -l)"
    
    # Uso de disco
    echo ""
    echo -e "${COLOR_BOLD}Uso de Disco:${COLOR_RESET}"
    echo -e "  ${COLOR_CYAN}Proyecto:${COLOR_RESET} $(get_disk_usage "$SCRIPT_DIR/..")"
    echo -e "  ${COLOR_CYAN}Logs:${COLOR_RESET} $(get_disk_usage "$SCRIPT_DIR/../logs")"
    echo -e "  ${COLOR_CYAN}Docker:${COLOR_RESET} $(docker system df --format '{{.Size}}' | head -1)"
    
    # Memoria
    echo ""
    echo -e "${COLOR_BOLD}Memoria del Sistema:${COLOR_RESET}"
    echo -e "  ${COLOR_CYAN}Total:${COLOR_RESET} $(free -h | awk '/^Mem:/ {print $2}')"
    echo -e "  ${COLOR_CYAN}Usada:${COLOR_RESET} $(free -h | awk '/^Mem:/ {print $3}')"
    echo -e "  ${COLOR_CYAN}Libre:${COLOR_RESET} $(free -h | awk '/^Mem:/ {print $4}')"
}

backup_important_data() {
    echo -e "${COLOR_CYAN}💾 Respaldo de datos importantes...${COLOR_RESET}"
    
    local backup_dir="$SCRIPT_DIR/../backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup de variables de entorno
    if [[ -f "$SCRIPT_DIR/../.env" ]]; then
        cp "$SCRIPT_DIR/../.env" "$backup_dir/env_backup.env"
        log_success "Respaldo de .env creado"
    fi
    
    # Backup de docker-compose files
    if [[ -f "$SCRIPT_DIR/../docker-compose.main.yml" ]]; then
        cp "$SCRIPT_DIR/../docker-compose.main.yml" "$backup_dir/"
        cp "$SCRIPT_DIR/../docker-compose.override.yml" "$backup_dir/" 2>/dev/null || true
        log_success "Respaldo de docker-compose creado"
    fi
    
    # Backup de logs recientes (últimos 3 días)
    if [[ -d "$SCRIPT_DIR/../logs" ]]; then
        find "$SCRIPT_DIR/../logs" -name "*.log" -mtime -3 -exec cp {} "$backup_dir/" \; 2>/dev/null || true
        log_success "Respaldo de logs recientes creado"
    fi
    
    log_success "Respaldo completado en: $backup_dir"
}

main() {
    print_header
    
    local action="${1:-full}"
    
    case "$action" in
        "logs")
            clean_logs
            ;;
        "docker")
            clean_docker
            ;;
        "system")
            system_cleanup
            ;;
        "backup")
            backup_important_data
            ;;
        "stats")
            show_system_stats
            ;;
        "full")
            log_info "Ejecutando limpieza completa..."
            clean_logs
            echo ""
            clean_docker
            echo ""
            system_cleanup
            echo ""
            show_system_stats
            ;;
        *)
            echo -e "${COLOR_YELLOW}Uso: $0 [logs|docker|system|backup|stats|full]${COLOR_RESET}"
            echo -e "${COLOR_CYAN}  logs   - Limpiar solo logs antiguos${COLOR_RESET}"
            echo -e "${COLOR_CYAN}  docker - Limpiar recursos de Docker${COLOR_RESET}"
            echo -e "${COLOR_CYAN}  system - Limpiar archivos temporales${COLOR_RESET}"
            echo -e "${COLOR_CYAN}  backup - Crear respaldo de datos${COLOR_RESET}"
            echo -e "${COLOR_CYAN}  stats  - Mostrar estadísticas${COLOR_RESET}"
            echo -e "${COLOR_CYAN}  full   - Limpieza completa (default)${COLOR_RESET}"
            exit 1
            ;;
    esac
    
    echo ""
    log_success "Limpieza completada"
    log_info "Log detallado: $LOG_FILE"
}

# =============================================================================
# EJECUCIÓN
# =============================================================================
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi