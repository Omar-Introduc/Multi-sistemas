#!/bin/bash

# =============================================================================
# SCRIPT DE GESTIÓN - SISTEMA DISTRIBUIDO SHIBASITO
# Gestiona la construcción, despliegue y monitoreo del sistema distribuido
# =============================================================================

set -e

# Configuración de colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuración de timeouts (en segundos)
TIMEOUT_START=300
TIMEOUT_HEALTH_CHECK=180
TIMEOUT_BUILD=600
TIMEOUT_STOP=60

# Archivo de configuración de timeouts
CONFIG_FILE="${HOME}/.shibasito-config"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE_MAIN="docker-compose.main.yml"
COMPOSE_FILE_OVERRIDE="docker-compose.override.yml"

# Funciones de utilidad para colores
print_header() {
    echo -e "\n${CYAN}=================================${NC}"
    echo -e "${WHITE}$1${NC}"
    echo -e "${CYAN}=================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_step() {
    echo -e "${PURPLE}➤ $1${NC}"
}

# Función para cargar configuración personalizada
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        source "$CONFIG_FILE"
        print_info "Configuración personalizada cargada desde $CONFIG_FILE"
    fi
}

# Función para guardar configuración
save_config() {
    cat > "$CONFIG_FILE" << EOF
# Configuración personalizada de Shibasito
TIMEOUT_START=${TIMEOUT_START:-300}
TIMEOUT_HEALTH_CHECK=${TIMEOUT_HEALTH_CHECK:-180}
TIMEOUT_BUILD=${TIMEOUT_BUILD:-600}
TIMEOUT_STOP=${TIMEOUT_STOP:-60}
EOF
    print_success "Configuración guardada en $CONFIG_FILE"
}

# Función para mostrar ayuda
show_help() {
    cat << EOF
${WHITE}SISTEMA DISTRIBUIDO SHIBASITO - SCRIPT DE GESTIÓN${NC}

${CYAN}USO:${NC}
    $0 <COMANDO> [OPCIONES]

${CYAN}COMANDOS DISPONIBLES:${NC}
    ${GREEN}build${NC}          Construir todas las imágenes del sistema
    ${GREEN}start${NC}          Iniciar el sistema completo
    ${GREEN}stop${NC}           Detener todos los servicios
    ${GREEN}restart${NC}        Reiniciar el sistema
    ${GREEN}status${NC}         Mostrar estado de los servicios
    ${GREEN}logs${NC}           Mostrar logs del sistema
    ${GREEN}logs-follow${NC}    Seguir logs en tiempo real
    ${GREEN}clean${NC}          Limpiar contenedores e imágenes
    ${GREEN}clean-all${NC}      Limpieza completa (incluye volúmenes)
    ${GREEN}health-check${NC}   Verificar salud del sistema
    ${GREEN}config${NC}         Configurar timeouts y opciones
    ${GREEN}help${NC}           Mostrar esta ayuda

${CYAN}OPCIONES PARA LOGS:${NC}
    --service <nombre>  Mostrar logs de un servicio específico
    --lines <número>    Mostrar las últimas N líneas
    --since <tiempo>    Mostrar logs desde hace X tiempo (ej: 1h, 30m)

${CYAN}OPCIONES PARA HEALTH-CHECK:${NC}
    --detailed         Mostrar información detallada
    --json             Salida en formato JSON

${CYAN}EJEMPLOS:${NC}
    $0 build
    $0 start --detach
    $0 logs --service servicio-banco-lp1 --lines 100
    $0 health-check --detailed
    $0 logs-follow --service rabbitmq

${CYAN}TIEMPO DE ESPERA POR DEFECTO:${NC}
    - Start: ${TIMEOUT_START}s
    - Health Check: ${TIMEOUT_HEALTH_CHECK}s
    - Build: ${TIMEOUT_BUILD}s
    - Stop: ${TIMEOUT_STOP}s

EOF
}

# Verificar dependencias del sistema
check_dependencies() {
    print_step "Verificando dependencias del sistema..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado"
        echo -e "${YELLOW}Instale Docker desde: https://docs.docker.com/get-docker/${NC}"
        exit 1
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose no está instalado"
        echo -e "${YELLOW}Instale Docker Compose desde: https://docs.docker.com/compose/install/${NC}"
        exit 1
    fi
    
    # Verificar que Docker esté corriendo
    if ! docker info &> /dev/null; then
        print_error "Docker no está ejecutándose"
        echo -e "${YELLOW}Inicie Docker y vuelva a intentar${NC}"
        exit 1
    fi
    
    print_success "Todas las dependencias están disponibles"
}

# Verificar archivos necesarios
check_files() {
    print_step "Verificando archivos de configuración..."
    
    if [[ ! -f "$COMPOSE_FILE_MAIN" ]]; then
        print_error "Archivo $COMPOSE_FILE_MAIN no encontrado"
        exit 1
    fi
    
    if [[ ! -f "$COMPOSE_FILE_OVERRIDE" ]]; then
        print_warning "Archivo $COMPOSE_FILE_OVERRIDE no encontrado, usando solo configuración principal"
    fi
    
    print_success "Archivos de configuración verificados"
}

# Construir el sistema
build_system() {
    print_header "CONSTRUYENDO SISTEMA SHIBASITO"
    
    check_dependencies
    check_files
    
    print_step "Iniciando construcción de imágenes..."
    
    # Construir con Docker Compose
    if docker-compose -f "$COMPOSE_FILE_MAIN" -f "$COMPOSE_FILE_OVERRIDE" build --parallel; then
        print_success "Sistema construido correctamente"
    else
        print_error "Error durante la construcción"
        exit 1
    fi
}

# Iniciar el sistema
start_system() {
    local detach=false
    local build_flag=""
    
    # Procesar argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --detach)
                detach=true
                shift
                ;;
            --no-build)
                build_flag="--no-build"
                shift
                ;;
            *)
                print_warning "Opción desconocida: $1"
                shift
                ;;
        esac
    done
    
    print_header "INICIANDO SISTEMA SHIBASITO"
    
    check_dependencies
    check_files
    
    # Construir si no se especifica --no-build
    if [[ -z "$build_flag" ]]; then
        print_step "Construyendo sistema antes de iniciar..."
        build_system
    fi
    
    print_step "Iniciando servicios..."
    
    # Iniciar servicios
    if docker-compose -f "$COMPOSE_FILE_MAIN" -f "$COMPOSE_FILE_OVERRIDE" up -d $build_flag; then
        print_success "Servicios iniciados correctamente"
    else
        print_error "Error al iniciar servicios"
        exit 1
    fi
    
    # Esperar a que el sistema esté listo
    print_step "Esperando a que el sistema esté listo..."
    wait_for_system
    
    # Mostrar estado
    if [[ "$detach" == "false" ]]; then
        show_status
    fi
}

# Esperar a que el sistema esté listo
wait_for_system() {
    local elapsed=0
    local interval=10
    
    print_info "Verificando que todos los servicios estén saludables..."
    
    while [[ $elapsed -lt $TIMEOUT_START ]]; do
        local healthy_count=$(get_healthy_services_count)
        local total_count=$(get_total_services_count)
        
        if [[ $healthy_count -eq $total_count ]]; then
            print_success "Sistema completamente operativo ($healthy_count/$total_count servicios saludables)"
            return 0
        fi
        
        echo -ne "\r${BLUE}Progreso: $healthy_count/$total_count servicios saludables (${elapsed}s)${NC}"
        sleep $interval
        elapsed=$((elapsed + interval))
    done
    
    echo ""
    print_warning "Timeout alcanzado. Algunos servicios pueden no estar completamente listos"
    print_info "Ejecute 'health-check' para verificar el estado detallado"
}

# Detener el sistema
stop_system() {
    print_header "DETENIENDO SISTEMA SHIBASITO"
    
    print_step "Deteniendo servicios..."
    
    if docker-compose -f "$COMPOSE_FILE_MAIN" -f "$COMPOSE_FILE_OVERRIDE" down --timeout $TIMEOUT_STOP; then
        print_success "Sistema detenido correctamente"
    else
        print_error "Error al detener servicios"
        exit 1
    fi
}

# Reiniciar el sistema
restart_system() {
    print_header "REINICIANDO SISTEMA SHIBASITO"
    
    stop_system
    sleep 5
    start_system
}

# Mostrar estado de los servicios
show_status() {
    print_header "ESTADO DEL SISTEMA SHIBASITO"
    
    echo -e "${WHITE}Estado de Servicios:${NC}\n"
    
    # Obtener estado de contenedores
    local containers=$(docker-compose -f "$COMPOSE_FILE_MAIN" -f "$COMPOSE_FILE_OVERRIDE" ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}")
    
    if [[ -n "$containers" ]]; then
        echo "$containers" | while read line; do
            if [[ $line == *"Up"* ]]; then
                echo -e "${GREEN}$line${NC}"
            elif [[ $line == *"Exit"* ]] || [[ $line == *" restarting"* ]]; then
                echo -e "${RED}$line${NC}"
            elif [[ $line == *"Name"* ]]; then
                echo -e "${CYAN}$line${NC}"
            else
                echo "$line"
            fi
        done
    fi
    
    echo -e "\n${WHITE}Servicios Adicionales:${NC}"
    
    # Verificar servicios de monitoreo
    check_service_port "Prometheus" "9090"
    check_service_port "Grafana" "3000"
    check_service_port "RabbitMQ Management" "15672"
    check_service_port "Servicio Banco" "8080"
    check_service_port "Servicio RENIEC" "8000"
}

# Verificar puerto de servicio
check_service_port() {
    local service_name=$1
    local port=$2
    
    if nc -z localhost "$port" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $service_name (puerto $port): ${GREEN}Activo${NC}"
    else
        echo -e "${RED}✗${NC} $service_name (puerto $port): ${RED}Inactivo${NC}"
    fi
}

# Mostrar logs
show_logs() {
    local service=""
    local lines="50"
    local since=""
    local follow=false
    
    # Procesar argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --service)
                service="$2"
                shift 2
                ;;
            --lines)
                lines="$2"
                shift 2
                ;;
            --since)
                since="$2"
                shift 2
                ;;
            -f|--follow)
                follow=true
                shift
                ;;
            *)
                print_warning "Opción desconocida: $1"
                shift
                ;;
        esac
    done
    
    print_header "LOGS DEL SISTEMA SHIBASITO"
    
    local compose_args="-f $COMPOSE_FILE_MAIN -f $COMPOSE_FILE_OVERRIDE"
    local docker_args=""
    
    # Construir argumentos para docker-compose
    if [[ -n "$service" ]]; then
        docker_args="$docker_args $service"
    fi
    
    if [[ -n "$lines" ]]; then
        docker_args="$docker_args --lines=$lines"
    fi
    
    if [[ -n "$since" ]]; then
        docker_args="$docker_args --since=$since"
    fi
    
    if [[ "$follow" == "true" ]]; then
        docker_args="$docker_args -f"
    fi
    
    # Mostrar logs con colores
    if [[ -n "$service" ]]; then
        echo -e "${CYAN}Logs para servicio: $service${NC}\n"
    else
        echo -e "${CYAN}Logs de todos los servicios${NC}\n"
    fi
    
    # Ejecutar docker-compose logs con colors
    docker-compose $compose_args logs $docker_args 2>&1 | \
        sed "s/ERROR/${RED}&${NC}/g" | \
        sed "s/WARN/${YELLOW}&${NC}/g" | \
        sed "s/INFO/${BLUE}&${NC}/g" | \
        sed "s/DEBUG/${PURPLE}&${NC}/g" | \
        sed "s/TRACE/${CYAN}&${NC}/g"
}

# Limpiar el sistema
clean_system() {
    print_header "LIMPIANDO SISTEMA SHIBASITO"
    
    print_warning "Esto eliminará contenedores e imágenes del sistema"
    read -p "¿Continuar? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Operación cancelada"
        return 0
    fi
    
    print_step "Deteniendo servicios..."
    docker-compose -f "$COMPOSE_FILE_MAIN" -f "$COMPOSE_FILE_OVERRIDE" down --remove-orphans
    
    print_step "Eliminando contenedores..."
    docker container prune -f
    
    print_step "Eliminando imágenes huérfanas..."
    docker image prune -f
    
    print_success "Sistema limpiado correctamente"
}

# Limpieza completa (incluye volúmenes)
clean_all_system() {
    print_header "LIMPIEZA COMPLETA DEL SISTEMA"
    
    print_error "ADVERTENCIA: Esto eliminará TODOS los datos del sistema"
    print_warning "Incluye: contenedores, imágenes, volúmenes y redes"
    read -p "¿Está seguro? Escriba 'CONFIRMAR' para continuar: " confirmation
    
    if [[ "$confirmation" != "CONFIRMAR" ]]; then
        print_info "Operación cancelada"
        return 0
    fi
    
    print_step "Deteniendo servicios..."
    docker-compose -f "$COMPOSE_FILE_MAIN" -f "$COMPOSE_FILE_OVERRIDE" down --volumes --remove-orphans
    
    print_step "Eliminando volúmenes..."
    docker volume prune -f
    
    print_step "Eliminando redes..."
    docker network prune -f
    
    print_step "Eliminando contenedores..."
    docker container prune -f
    
    print_step "Eliminando imágenes..."
    docker image prune -f
    
    print_success "Limpieza completa realizada"
}

# Verificar salud del sistema
health_check() {
    local detailed=false
    local json_output=false
    
    # Procesar argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --detailed)
                detailed=true
                shift
                ;;
            --json)
                json_output=true
                shift
                ;;
            *)
                print_warning "Opción desconocida: $1"
                shift
                ;;
        esac
    done
    
    print_header "VERIFICACIÓN DE SALUD DEL SISTEMA"
    
    if [[ "$json_output" == "true" ]]; then
        check_health_json
    else
        check_health_text $detailed
    fi
}

# Verificar salud en formato texto
check_health_text() {
    local detailed=$1
    local elapsed=0
    local interval=5
    local services_healthy=0
    local total_services=0
    
    print_info "Realizando verificación de salud..."
    
    # Obtener todos los servicios
    local services=$(docker-compose -f "$COMPOSE_FILE_MAIN" -f "$COMPOSE_FILE_OVERRIDE" ps --services)
    total_services=$(echo "$services" | wc -l)
    
    echo -e "\n${WHITE}Estado de Servicios:${NC}"
    
    while IFS= read -r service; do
        local status=$(docker-compose -f "$COMPOSE_FILE_MAIN" -f "$COMPOSE_FILE_OVERRIDE" ps --format "table {{.Name}}\t{{.Status}}" | grep "$service" | awk '{print $2}')
        
        if [[ -n "$status" ]]; then
            if [[ $status == *"Up"* ]]; then
                echo -e "${GREEN}✓${NC} $service: ${GREEN}Operativo${NC}"
                ((services_healthy++))
            else
                echo -e "${RED}✗${NC} $service: ${RED}No operativo${NC}"
            fi
            
            if [[ "$detailed" == "true" ]]; then
                local health=$(docker inspect $(docker-compose -f "$COMPOSE_FILE_MAIN" -f "$COMPOSE_FILE_OVERRIDE" ps -q $service) --format='{{.State.Health.Status}}' 2>/dev/null || echo "Sin healthcheck")
                echo -e "  ${BLUE}Health:${NC} $health"
                
                # Verificar puertos
                local ports=$(docker port $(docker-compose -f "$COMPOSE_FILE_MAIN" -f "$COMPOSE_FILE_OVERRIDE" ps -q $service) 2>/dev/null | awk '{print $1}' | sort | uniq | tr '\n' ' ' || echo "Ninguno")
                echo -e "  ${BLUE}Puertos:${NC} $ports"
                echo
            fi
        else
            echo -e "${YELLOW}⚠${NC} $service: ${YELLOW}No encontrado${NC}"
        fi
    done <<< "$services"
    
    echo -e "\n${WHITE}Resumen:${NC}"
    echo -e "Servicios saludables: ${GREEN}$services_healthy${NC}/$total_services"
    
    # Verificar conectividad de servicios clave
    echo -e "\n${WHITE}Verificación de Conectividad:${NC}"
    check_connectivity
    
    if [[ $services_healthy -eq $total_services ]]; then
        print_success "Todos los servicios están operativos"
        return 0
    else
        print_warning "Algunos servicios no están completamente operativos"
        return 1
    fi
}

# Verificar conectividad de servicios
check_connectivity() {
    # Verificar bases de datos
    if docker exec postgresql-bd1-container pg_isready -U banco_user &>/dev/null; then
        echo -e "${GREEN}✓${NC} PostgreSQL BD1: ${GREEN}Conectable${NC}"
    else
        echo -e "${RED}✗${NC} PostgreSQL BD1: ${RED}No conectable${NC}"
    fi
    
    if docker exec mysql-bd2-container mysqladmin ping -h localhost &>/dev/null; then
        echo -e "${GREEN}✓${NC} MySQL BD2: ${GREEN}Conectable${NC}"
    else
        echo -e "${RED}✗${NC} MySQL BD2: ${RED}No conectable${NC}"
    fi
    
    # Verificar Redis
    if docker exec redis-container redis-cli ping | grep -q PONG; then
        echo -e "${GREEN}✓${NC} Redis: ${GREEN}Conectable${NC}"
    else
        echo -e "${RED}✗${NC} Redis: ${RED}No conectable${NC}"
    fi
    
    # Verificar RabbitMQ
    if docker exec rabbitmq-container rabbitmq-diagnostics ping &>/dev/null; then
        echo -e "${GREEN}✓${NC} RabbitMQ: ${GREEN}Conectable${NC}"
    else
        echo -e "${RED}✗${NC} RabbitMQ: ${RED}No conectable${NC}"
    fi
}

# Verificar salud en formato JSON
check_health_json() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local status="unknown"
    local services=()
    
    # Obtener estado de servicios
    local docker_services=$(docker-compose -f "$COMPOSE_FILE_MAIN" -f "$COMPOSE_FILE_OVERRIDE" ps --format json 2>/dev/null || echo "[]")
    
    # Crear JSON de respuesta
    cat << EOF
{
  "timestamp": "$timestamp",
  "system": "shibasito-distributed-system",
  "status": "$status",
  "services": $docker_services,
  "healthy_services": 0,
  "total_services": 0,
  "uptime": "$(uptime -p 2>/dev/null || echo 'unknown')",
  "docker_version": "$(docker --version 2>/dev/null || echo 'unknown')",
  "docker_compose_version": "$(docker-compose --version 2>/dev/null || echo 'unknown')"
}
EOF
}

# Obtener conteo de servicios saludables
get_healthy_services_count() {
    docker-compose -f "$COMPOSE_FILE_MAIN" -f "$COMPOSE_FILE_OVERRIDE" ps --format json 2>/dev/null | grep -c '"State":"running"' || echo "0"
}

# Obtener conteo total de servicios
get_total_services_count() {
    docker-compose -f "$COMPOSE_FILE_MAIN" -f "$COMPOSE_FILE_OVERRIDE" ps --services | wc -l
}

# Configurar timeouts y opciones
configure_system() {
    print_header "CONFIGURACIÓN DEL SISTEMA"
    
    echo -e "${WHITE}Configuración actual de timeouts:${NC}"
    echo -e "Timeout Start: ${GREEN}$TIMEOUT_START${NC} segundos"
    echo -e "Timeout Health Check: ${GREEN}$TIMEOUT_HEALTH_CHECK${NC} segundos"
    echo -e "Timeout Build: ${GREEN}$TIMEOUT_BUILD${NC} segundos"
    echo -e "Timeout Stop: ${GREEN}$TIMEOUT_STOP${NC} segundos"
    
    echo -e "\n${CYAN}¿Desea modificar la configuración? (y/N)${NC}"
    read -p "> " modify_config
    
    if [[ $modify_config =~ ^[Yy]$ ]]; then
        echo -e "\n${WHITE}Ingrese los nuevos valores:${NC}"
        
        read -p "Timeout Start [$TIMEOUT_START]: " new_timeout_start
        read -p "Timeout Health Check [$TIMEOUT_HEALTH_CHECK]: " new_timeout_health
        read -p "Timeout Build [$TIMEOUT_BUILD]: " new_timeout_build
        read -p "Timeout Stop [$TIMEOUT_STOP]: " new_timeout_stop
        
        # Usar valores por defecto si están vacíos
        TIMEOUT_START=${new_timeout_start:-$TIMEOUT_START}
        TIMEOUT_HEALTH_CHECK=${new_timeout_health:-$TIMEOUT_HEALTH_CHECK}
        TIMEOUT_BUILD=${new_timeout_build:-$TIMEOUT_BUILD}
        TIMEOUT_STOP=${new_timeout_stop:-$TIMEOUT_STOP}
        
        save_config
        print_success "Configuración actualizada"
    else
        print_info "Configuración sin cambios"
    fi
}

# Función principal
main() {
    # Cargar configuración
    load_config
    
    # Verificar si se proporciona un comando
    if [[ $# -eq 0 ]]; then
        show_help
        exit 0
    fi
    
    local command=$1
    shift
    
    case $command in
        build)
            build_system
            ;;
        start)
            start_system "$@"
            ;;
        stop)
            stop_system
            ;;
        restart)
            restart_system
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$@"
            ;;
        logs-follow)
            show_logs -f "$@"
            ;;
        clean)
            clean_system
            ;;
        clean-all)
            clean_all_system
            ;;
        health-check)
            health_check "$@"
            ;;
        config)
            configure_system
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Comando desconocido: $command"
            echo -e "\nUse '$0 help' para ver los comandos disponibles"
            exit 1
            ;;
    esac
}

# Verificar si el script se está ejecutando directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi