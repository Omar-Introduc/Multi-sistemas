#!/bin/bash

# =============================================================================
# Script de Monitoreo de Servicios
# Sistema Bancario Distribuido - Shibasito
# =============================================================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuración
SCRIPT_DIR="$(dirname "$0")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.monitoring.yml"
MONITORING_COMPOSE_FILE="$PROJECT_DIR/docker-compose.main.yml"

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR:${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] INFO:${NC} $1"
}

# Función para verificar si un servicio está corriendo
is_service_running() {
    local container_name=$1
    if docker ps --filter "name=$container_name" --format "table {{.Names}}" | grep -q "$container_name"; then
        return 0
    else
        return 1
    fi
}

# Función para obtener información del contenedor
get_container_info() {
    local container_name=$1
    if is_service_running "$container_name"; then
        local status=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null)
        local uptime=$(docker inspect --format='{{.State.StartedAt}}' "$container_name" 2>/dev/null | cut -d'.' -f1)
        local health=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "none")
        echo "$status|$uptime|$health"
    else
        echo "stopped|none|none"
    fi
}

# Función para verificar endpoint HTTP
check_endpoint() {
    local url=$1
    local service_name=$2
    local timeout=5
    
    if curl -sf --max-time "$timeout" "$url" >/dev/null 2>&1; then
        echo "✓ UP"
        return 0
    else
        echo "✗ DOWN"
        return 1
    fi
}

# Función para verificar métricas de Prometheus
check_prometheus_metrics() {
    local query=$1
    local threshold=$2
    local service=$3
    
    local result=$(curl -s "http://localhost:9090/api/v1/query?query=$query" 2>/dev/null | \
                   jq -r '.data.result[0].value[1]' 2>/dev/null || echo "0")
    
    if [ "$service" = "cpu" ] || [ "$service" = "memory" ] || [ "$service" = "disk" ]; then
        # Para métricas de porcentaje
        local value=$(echo "$result" | cut -d'.' -f1)
        if [ "$value" -lt "$threshold" ]; then
            echo "${GREEN}✓ Normal${NC} ($value%)"
        else
            echo "${YELLOW}⚠ Warning${NC} ($value%)"
        fi
    else
        echo "$result"
    fi
}

# Función para mostrar el estado general
show_status() {
    echo -e "${CYAN}================================================================${NC}"
    echo -e "${CYAN}    ESTADO DEL STACK DE MONITOREO - $(date +'%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${CYAN}================================================================${NC}"
    echo ""
    
    # Servicios de monitoreo
    echo -e "${YELLOW}📊 SERVICIOS DE MONITOREO:${NC}"
    echo "----------------------------------------"
    
    local monitoring_services=(
        "shibasito-prometheus:Prometheus:http://localhost:9090/-/healthy"
        "shibasito-grafana:Grafana:http://localhost:3000/api/health"
        "shibasito-alertmanager:AlertManager:http://localhost:9093/-/healthy"
        "shibasito-node-exporter:NodeExporter:http://localhost:9100/metrics"
    )
    
    local monitoring_down=0
    
    for service_info in "${monitoring_services[@]}"; do
        IFS=':' read -r container name endpoint <<< "$service_info"
        
        if is_service_running "$container"; then
            local info=$(get_container_info "$container")
            IFS='|' read -r status uptime health <<< "$info"
            
            local health_icon="✓"
            local health_color=$GREEN
            if [ "$health" = "unhealthy" ]; then
                health_icon="✗"
                health_color=$RED
                ((monitoring_down++))
            elif [ "$health" = "none" ]; then
                health_icon="-"
                health_color=$YELLOW
            fi
            
            local status_icon="✓"
            if [ "$status" != "running" ]; then
                status_icon="✗"
                health_color=$RED
                ((monitoring_down++))
            fi
            
            echo -e "  ${GREEN}${status_icon}${NC} $name"
            echo -e "    Container: $container"
            echo -e "    Status: $status | Health: $health_icon | Uptime: $uptime"
            
            if [ -n "$endpoint" ]; then
                local endpoint_status=$(check_endpoint "$endpoint" "$name")
                echo -e "    Endpoint: $endpoint_status"
            fi
        else
            echo -e "  ${RED}✗${NC} $name"
            echo -e "    Container: $container"
            echo -e "    Status: STOPPED"
            ((monitoring_down++))
        fi
        echo ""
    done
    
    # Servicios del negocio
    echo -e "${YELLOW}🏦 SERVICIOS DEL NEGOCIO:${NC}"
    echo "----------------------------------------"
    
    local business_services=(
        "lp1-servicio-banco:LPServicioBanco:http://localhost:8080/actuator/health"
        "lp2-reniec-service:LPServicioRENIEC:http://localhost:8000/health"
        "lp3-desktop-app:LP3DesktopApp:http://localhost:3000/health"
        "rabbitmq:RabbitMQ:http://localhost:15672"
        "redis:Redis:http://localhost:9121/metrics"
    )
    
    local business_down=0
    
    for service_info in "${business_services[@]}"; do
        IFS=':' read -r container name endpoint <<< "$service_info"
        
        if is_service_running "$container"; then
            local info=$(get_container_info "$container")
            IFS='|' read -r status uptime health <<< "$info"
            
            local status_icon="✓"
            if [ "$status" != "running" ]; then
                status_icon="✗"
                status_icon=$RED
                ((business_down++))
            fi
            
            echo -e "  ${GREEN}${status_icon}${NC} $name"
            echo -e "    Container: $container"
            echo -e "    Status: $status | Uptime: $uptime"
            
            if [ -n "$endpoint" ]; then
                local endpoint_status=$(check_endpoint "$endpoint" "$name")
                echo -e "    Endpoint: $endpoint_status"
            fi
        else
            echo -e "  ${YELLOW}-${NC} $name"
            echo -e "    Container: $container"
            echo -e "    Status: NOT MONITORING CONTAINER"
        fi
        echo ""
    done
    
    # Métricas del sistema
    echo -e "${YELLOW}📈 MÉTRICAS DEL SISTEMA:${NC}"
    echo "----------------------------------------"
    
    if curl -sf "http://localhost:9090/api/v1/query?query=up" >/dev/null 2>&1; then
        local cpu_usage=$(check_prometheus_metrics "100 - (avg by(instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)" 80 "cpu")
        local memory_usage=$(check_prometheus_metrics "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100" 85 "memory")
        local disk_usage=$(check_prometheus_metrics "100 - ((node_filesystem_avail_bytes{fstype!=\"tmpfs\"} / node_filesystem_size_bytes{fstype!=\"tmpfs\"}) * 100)" 90 "disk")
        
        echo "  CPU Usage: $cpu_usage"
        echo "  Memory Usage: $memory_usage"
        echo "  Disk Usage: $disk_usage"
        
        # Verificar servicios activos en Prometheus
        local active_targets=$(curl -s "http://localhost:9090/api/v1/targets" | jq -r '.data.activeTargets | length' 2>/dev/null || echo "0")
        echo "  Prometheus Active Targets: $active_targets"
    else
        echo -e "  ${RED}✗${NC} Prometheus no disponible para métricas"
    fi
    
    echo ""
    
    # Resumen
    echo -e "${CYAN}================================================================${NC}"
    echo -e "${CYAN}    RESUMEN${NC}"
    echo -e "${CYAN}================================================================${NC}"
    
    local total_services=4
    local monitoring_up=$((total_services - monitoring_down))
    
    echo "Servicios de Monitoreo: $monitoring_up/$total_services UP"
    echo "Servicios del Negocio: Variables"
    echo ""
    
    if [ $monitoring_down -eq 0 ]; then
        echo -e "${GREEN}✅ Todos los servicios de monitoreo están funcionando correctamente${NC}"
    else
        echo -e "${RED}❌ $monitoring_down servicios de monitoreo tienen problemas${NC}"
        warn "Ejecuta './scripts/monitor-services.sh restart' para reiniciar"
    fi
    
    echo -e "${CYAN}================================================================${NC}"
}

# Función para mostrar logs
show_logs() {
    local service=$1
    local lines=${2:-100}
    
    if [ -z "$service" ]; then
        error "Debes especificar un servicio. Usos: logs [servicio] [líneas]"
        echo "Servicios disponibles: prometheus, grafana, alertmanager, node-exporter"
        exit 1
    fi
    
    case "$service" in
        "prometheus")
            docker logs -f --tail="$lines" shibasito-prometheus
            ;;
        "grafana")
            docker logs -f --tail="$lines" shibasito-grafana
            ;;
        "alertmanager")
            docker logs -f --tail="$lines" shibasito-alertmanager
            ;;
        "node-exporter")
            docker logs -f --tail="$lines" shibasito-node-exporter
            ;;
        "redis-exporter")
            docker logs -f --tail="$lines" shibasito-redis-exporter
            ;;
        "mysql-exporter")
            docker logs -f --tail="$lines" shibasito-mysql-exporter
            ;;
        "postgres-exporter")
            docker logs -f --tail="$lines" shibasito-postgres-exporter
            ;;
        *)
            error "Servicio '$service' no reconocido"
            echo "Servicios disponibles: prometheus, grafana, alertmanager, node-exporter, redis-exporter, mysql-exporter, postgres-exporter"
            exit 1
            ;;
    esac
}

# Función para reiniciar servicios
restart_services() {
    log "Reiniciando servicios de monitoreo..."
    
    if [ -f "$COMPOSE_FILE" ]; then
        cd "$(dirname "$COMPOSE_FILE")"
        docker-compose -f "$(basename "$COMPOSE_FILE")" restart
    else
        error "Archivo docker-compose.monitoring.yml no encontrado"
        exit 1
    fi
    
    log "Esperando que los servicios estén listos..."
    sleep 15
    
    show_status
}

# Función para parar servicios
stop_services() {
    log "Deteniendo servicios de monitoreo..."
    
    if [ -f "$COMPOSE_FILE" ]; then
        cd "$(dirname "$COMPOSE_FILE")"
        docker-compose -f "$(basename "$COMPOSE_FILE")" down
    else
        error "Archivo docker-compose.monitoring.yml no encontrado"
        exit 1
    fi
}

# Función para iniciar servicios
start_services() {
    log "Iniciando servicios de monitoreo..."
    
    if [ -f "$COMPOSE_FILE" ]; then
        cd "$(dirname "$COMPOSE_FILE")"
        docker-compose -f "$(basename "$COMPOSE_FILE")" up -d
    else
        error "Archivo docker-compose.monitoring.yml no encontrado"
        exit 1
    fi
    
    log "Esperando que los servicios estén listos..."
    sleep 15
    
    show_status
}

# Función para mostrar métricas específicas
show_metrics() {
    local metric_type=$1
    
    case "$metric_type" in
        "performance")
            echo -e "${CYAN}📊 MÉTRICAS DE RENDIMIENTO${NC}"
            echo "================================"
            
            if curl -sf "http://localhost:9090/api/v1/query?query=up" >/dev/null 2>&1; then
                # Tiempo de respuesta promedio
                local response_time=$(curl -s "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket[5m]))" | \
                                    jq -r '.data.result[0].value[1]' 2>/dev/null || echo "N/A")
                echo "Tiempo de respuesta P95: ${response_time}s"
                
                # Requests por segundo
                local requests_per_sec=$(curl -s "http://localhost:9090/api/v1/query?query=rate(http_requests_total[5m])" | \
                                       jq -r '(.data.result | map(.value[1] | tonumber) | add // 0)' 2>/dev/null || echo "0")
                echo "Requests por segundo: ${requests_per_sec}"
                
                # Errores por minuto
                local errors_per_min=$(curl -s "http://localhost:9090/api/v1/query?query=rate(http_requests_total{status=~\"5..\"}[5m])*60" | \
                                     jq -r '(.data.result | map(.value[1] | tonumber) | add // 0)' 2>/dev/null || echo "0")
                echo "Errores por minuto: ${errors_per_min}"
            else
                echo -e "${RED}Prometheus no disponible${NC}"
            fi
            ;;
            
        "resources")
            echo -e "${CYAN}📊 RECURSOS DEL SISTEMA${NC}"
            echo "============================="
            
            if curl -sf "http://localhost:9090/api/v1/query?query=up" >/dev/null 2>&1; then
                # CPU
                local cpu_usage=$(curl -s "http://localhost:9090/api/v1/query?query=100-(avg by(instance)(rate(node_cpu_seconds_total{mode=\"idle\"}[5m]))*100)" | \
                                 jq -r '.data.result[0].value[1]' 2>/dev/null | cut -d'.' -f1 || echo "N/A")
                echo "CPU: ${cpu_usage}%"
                
                # Memoria
                local memory_usage=$(curl -s "http://localhost:9090/api/v1/query?query=(1-(node_memory_MemAvailable_bytes/node_memory_MemTotal_bytes))*100" | \
                                    jq -r '.data.result[0].value[1]' 2>/dev/null | cut -d'.' -f1 || echo "N/A")
                echo "Memoria: ${memory_usage}%"
                
                # Disco
                local disk_usage=$(curl -s "http://localhost:9090/api/v1/query?query=100-((node_filesystem_avail_bytes{fstype!=\"tmpfs\"}/node_filesystem_size_bytes{fstype!=\"tmpfs\"})*100)" | \
                                  jq -r '.data.result[0].value[1]' 2>/dev/null | cut -d'.' -f1 || echo "N/A")
                echo "Disco: ${disk_usage}%"
            else
                echo -e "${RED}Prometheus no disponible${NC}"
            fi
            ;;
            
        "business")
            echo -e "${CYAN}📊 MÉTRICAS DE NEGOCIO${NC}"
            echo "========================="
            
            if curl -sf "http://localhost:9090/api/v1/query?query=up" >/dev/null 2>&1; then
                # Transacciones bancarias
                local transactions=$(curl -s "http://localhost:9090/api/v1/query?query=rate(banco_transacciones_total[5m])" | \
                                   jq -r '.data.result[0].value[1]' 2>/dev/null || echo "N/A")
                echo "Transacciones bancarias/seg: ${transactions}"
                
                # Consultas RENIEC
                local consultas=$(curl -s "http://localhost:9090/api/v1/query?query=rate(reniec_consultas_total[5m])" | \
                                jq -r '.data.result[0].value[1]' 2>/dev/null || echo "N/A")
                echo "Consultas RENIEC/seg: ${consultas}"
            else
                echo -e "${RED}Prometheus no disponible${NC}"
            fi
            ;;
            
        *)
            error "Tipo de métrica no reconocido: $metric_type"
            echo "Tipos disponibles: performance, resources, business"
            exit 1
            ;;
    esac
}

# Función para mostrar ayuda
show_help() {
    cat << 'EOF'
==============================================
    Script de Monitoreo de Servicios
    Sistema Bancario Distribuido - Shibasito
==============================================

USO:
    ./scripts/monitor-services.sh [COMANDO] [OPCIONES]

COMANDOS:
    status          Mostrar estado general del stack de monitoreo
    logs [servicio] [líneas]  Mostrar logs de un servicio específico
    restart         Reiniciar servicios de monitoreo
    start           Iniciar servicios de monitoreo
    stop            Detener servicios de monitoreo
    metrics [tipo]  Mostrar métricas específicas (performance|resources|business)
    help            Mostrar esta ayuda

EJEMPLOS:
    # Ver estado general
    ./scripts/monitor-services.sh status

    # Ver logs de Prometheus
    ./scripts/monitor-services.sh logs prometheus 50

    # Ver métricas de rendimiento
    ./scripts/monitor-services.sh metrics performance

    # Reiniciar todos los servicios
    ./scripts/monitor-services.sh restart

SERVICIOS DISPONIBLES PARA LOGS:
    prometheus, grafana, alertmanager, node-exporter
    redis-exporter, mysql-exporter, postgres-exporter

TIPOS DE MÉTRICAS:
    performance: tiempo de respuesta, requests, errores
    resources: CPU, memoria, disco
    business: transacciones, consultas, etc.

EOF
}

# Función principal
main() {
    local command=${1:-status}
    
    case "$command" in
        "status")
            show_status
            ;;
        "logs")
            show_logs "$2" "$3"
            ;;
        "restart")
            restart_services
            ;;
        "start")
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "metrics")
            show_metrics "$2"
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            error "Comando no reconocido: $command"
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"