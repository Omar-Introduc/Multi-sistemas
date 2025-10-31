#!/bin/bash

# =============================================================================
# SCRIPT DE VERIFICACIÓN RÁPIDA
# Sistema Distribuido Shibasito
# =============================================================================

set -euo pipefail

# =============================================================================
# CONFIGURACIÓN DE COLORES Y LOGGING
# =============================================================================
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
print_header() {
    clear
    echo -e "${COLOR_BOLD}${COLOR_BLUE}"
    echo "================================================================================"
    echo "🔍 SISTEMA DISTRIBUIDO SHIBASITO - VERIFICACIÓN RÁPIDA"
    echo "================================================================================"
    echo -e "${COLOR_RESET}"
    echo -e "${COLOR_CYAN}Fecha: ${COLOR_BOLD}$(date '+%Y-%m-%d %H:%M:%S')${COLOR_RESET}"
    echo ""
}

check_service() {
    local service_name=$1
    local port=$2
    
    if docker ps --format '{{.Names}}' | grep -q "^${service_name}$"; then
        # Verificar si el puerto responde
        if docker exec "$service_name" curl -f -s "http://localhost:${port}/" >/dev/null 2>&1 || \
           docker exec "$service_name" nc -z localhost "$port" >/dev/null 2>&1; then
            echo -e "  ${COLOR_GREEN}✅${COLOR_RESET} ${COLOR_CYAN}$service_name${COLOR_RESET} - ${COLOR_GREEN}Funcionando${COLOR_RESET}"
            return 0
        else
            echo -e "  ${COLOR_YELLOW}⚠️${COLOR_RESET} ${COLOR_CYAN}$service_name${COLOR_RESET} - ${COLOR_YELLOW}Contenedor corriendo pero no responde${COLOR_RESET}"
            return 1
        fi
    else
        echo -e "  ${COLOR_RED}❌${COLOR_RESET} ${COLOR_CYAN}$service_name${COLOR_RESET} - ${COLOR_RED}No encontrado${COLOR_RESET}"
        return 1
    fi
}

print_summary() {
    echo ""
    echo -e "${COLOR_BOLD}${COLOR_BLUE}================================================================================"
    echo -e "📊 RESUMEN DEL SISTEMA"
    echo -e "================================================================================${COLOR_RESET}"
    
    # Estadísticas de Docker
    local running_containers=$(docker ps --format '{{.Names}}' | wc -l)
    local total_containers=$(docker ps -a --format '{{.Names}}' | wc -l)
    
    echo -e "${COLOR_CYAN}🐳 Docker:${COLOR_RESET}"
    echo -e "  ${COLOR_BOLD}Contenedores ejecutándose:${COLOR_RESET} $running_containers"
    echo -e "  ${COLOR_BOLD}Contenedores totales:${COLOR_RESET} $total_containers"
    
    # Estadísticas de uso de recursos
    local memory_usage=$(docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}" | tail -n +2 | awk '{sum+=$2} END {print sum}' | sed 's/GiB/ GB/')
    local cpu_usage=$(docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}" | tail -n +2 | awk -v count=$(docker ps -q | wc -l) 'NR<=count {sum+=$2} END {printf "%.1f", sum/count}')
    
    echo -e "${COLOR_CYAN}💾 Recursos:${COLOR_RESET}"
    echo -e "  ${COLOR_BOLD}Memoria estimada:${COLOR_RESET} $memory_usage"
    echo -e "  ${COLOR_BOLD}CPU promedio:${COLOR_RESET} $cpu_usage"
    
    # Puertos en uso
    echo -e "${COLOR_CYAN}🌐 Puertos en uso:${COLOR_RESET}"
    echo -e "  ${COLOR_BOLD}8080${COLOR_RESET} - Servicio Banco"
    echo -e "  ${COLOR_BOLD}8000${COLOR_RESET} - Servicio RENIEC"
    echo -e "  ${COLOR_BOLD}5432${COLOR_RESET} - PostgreSQL"
    echo -e "  ${COLOR_BOLD}3306${COLOR_RESET} - MySQL"
    echo -e "  ${COLOR_BOLD}5672${COLOR_RESET} - RabbitMQ"
    echo -e "  ${COLOR_BOLD}6379${COLOR_RESET} - Redis"
    echo -e "  ${COLOR_BOLD}9090${COLOR_RESET} - Prometheus"
    echo -e "  ${COLOR_BOLD}3000${COLOR_RESET} - Grafana"
    echo ""
}

main() {
    print_header
    
    echo -e "${COLOR_CYAN}🔍 Verificando servicios principales...${COLOR_RESET}\n"
    
    # Verificar servicios de aplicación
    echo -e "${COLOR_BOLD}Servicios de Aplicación:${COLOR_RESET}"
    check_service "servicio-banco-lp1" "8080"
    check_service "servicio-reniec-lp2" "8000"
    
    echo ""
    echo -e "${COLOR_BOLD}Bases de Datos:${COLOR_RESET}"
    check_service "bd1_postgresql" "5432"
    check_service "bd2_mysql" "3306"
    
    echo ""
    echo -e "${COLOR_BOLD}Servicios de Infraestructura:${COLOR_RESET}"
    check_service "rabbitmq" "5672"
    check_service "redis" "6379"
    
    echo ""
    echo -e "${COLOR_BOLD}Monitoreo:${COLOR_RESET}"
    check_service "prometheus" "9090"
    check_service "grafana" "3000"
    
    print_summary
}

# =============================================================================
# EJECUCIÓN
# =============================================================================
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi