#!/bin/bash

# =============================================================================
# Script de Instalación Automática del Stack de Monitoreo
# Sistema Bancario Distribuido - Shibasito
# =============================================================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    exit 1
}

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Función para verificar si un puerto está en uso
port_in_use() {
    local port=$1
    netstat -tuln 2>/dev/null | grep -q ":$port " || ss -tuln 2>/dev/null | grep -q ":$port "
}

# Función para crear directorios necesarios
create_directories() {
    log "Creando directorios necesarios..."
    
    local base_dir="$(dirname "$0")/../data"
    
    # Directorios para Prometheus
    mkdir -p "$base_dir/prometheus/{data,targets}"
    
    # Directorios para Grafana
    mkdir -p "$base_dir/grafana/{dashboards,datasources,plugins}"
    
    # Directorios para AlertManager
    mkdir -p "$base_dir/alertmanager"
    
    # Directorios para logs
    mkdir -p logs/{prometheus,grafana,alertmanager,node-exporter}
    
    # Directorios para backups
    mkdir -p backup/{prometheus,grafana,alertmanager}
    
    # Establecer permisos
    chmod -R 755 "$base_dir"
    chmod -R 755 logs
    chmod -R 755 backup
    
    log "Directorios creados exitosamente"
}

# Función para verificar dependencias
check_dependencies() {
    log "Verificando dependencias..."
    
    # Verificar Docker
    if ! command_exists docker; then
        error "Docker no está instalado. Por favor instala Docker primero."
    fi
    
    # Verificar Docker Compose
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        error "Docker Compose no está instalado. Por favor instala Docker Compose primero."
    fi
    
    # Verificar puertos disponibles
    local ports=(3000 8080 9090 9093 9100 9121 9187 9104 15692)
    local occupied_ports=()
    
    for port in "${ports[@]}"; do
        if port_in_use "$port"; then
            occupied_ports+=("$port")
        fi
    done
    
    if [ ${#occupied_ports[@]} -gt 0 ]; then
        warn "Los siguientes puertos están en uso: ${occupied_ports[*]}"
        warn "Esto puede causar conflictos. Considera liberar estos puertos."
        read -p "¿Continuar de todos modos? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "Instalación cancelada por el usuario"
        fi
    fi
    
    log "Dependencias verificadas"
}

# Función para crear archivo docker-compose para monitoreo
create_docker_compose() {
    log "Creando archivo docker-compose.yml para monitoreo..."
    
    local compose_file="$(dirname "$0")/../../docker-compose.monitoring.yml"
    
    cat > "$compose_file" << 'EOF'
version: '3.8'

services:
  # Prometheus - Recolección de métricas
  prometheus:
    image: prom/prometheus:v2.45.0
    container_name: shibasito-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./config/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./config/monitoring/alerting.yml:/etc/prometheus/alerting.yml
      - ./data/prometheus/data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
    networks:
      - monitoring
    labels:
      - "prometheus.io/scrape=true"
      - "prometheus.io/port=9090"

  # Grafana - Visualización
  grafana:
    image: grafana/grafana:10.0.0
    container_name: shibasito-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - ./data/grafana/dashboards:/var/lib/grafana/dashboards
      - ./data/grafana/datasources:/etc/grafana/provisioning/datasources
      - ./config/monitoring/grafana/dashboards.json:/var/lib/grafana/dashboards/sistema-bancario.json
      - ./config/monitoring/grafana/datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    networks:
      - monitoring
    depends_on:
      - prometheus

  # AlertManager - Gestión de alertas
  alertmanager:
    image: prom/alertmanager:v0.25.0
    container_name: shibasito-alertmanager
    restart: unless-stopped
    ports:
      - "9093:9093"
    volumes:
      - ./config/monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - ./data/alertmanager:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
      - '--web.external-url=http://localhost:9093'
    networks:
      - monitoring

  # Node Exporter - Métricas del sistema
  node-exporter:
    image: prom/node-exporter:v1.6.0
    container_name: shibasito-node-exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - monitoring
    labels:
      - "prometheus.io/scrape=true"
      - "prometheus.io/port=9100"

  # Redis Exporter
  redis-exporter:
    image: oliver006/redis_exporter:v1.51.0
    container_name: shibasito-redis-exporter
    restart: unless-stopped
    ports:
      - "9121:9121"
    environment:
      - REDIS_ADDR=redis:6379
    networks:
      - monitoring
    labels:
      - "prometheus.io/scrape=true"
      - "prometheus.io/port=9121"

  # MySQL Exporter
  mysql-exporter:
    image: prom/mysqld_exporter:v0.14.0
    container_name: shibasito-mysql-exporter
    restart: unless-stopped
    ports:
      - "9104:9104"
    environment:
      - DATA_SOURCE_NAME=root:password@tcp(mysql:3306)/
    networks:
      - monitoring
    labels:
      - "prometheus.io/scrape=true"
      - "prometheus.io/port=9104"

  # PostgreSQL Exporter
  postgres-exporter:
    image: prometheuscommunity/postgres_exporter:v0.13.2
    container_name: shibasito-postgres-exporter
    restart: unless-stopped
    ports:
      - "9187:9187"
    environment:
      - DATA_SOURCE_NAME=postgresql://postgres:password@postgres:5432/postgres?sslmode=disable
    networks:
      - monitoring
    labels:
      - "prometheus.io/scrape=true"
      - "prometheus.io/port=9187"

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:
EOF

    log "Archivo docker-compose.monitoring.yml creado"
}

# Función para crear configuración de AlertManager
create_alertmanager_config() {
    log "Creando configuración de AlertManager..."
    
    local config_file="$(dirname "$0")/../config/monitoring/alertmanager.yml"
    
    cat > "$config_file" << 'EOF'
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@shibasito-banco.com'
  smtp_auth_username: 'alerts@shibasito-banco.com'
  smtp_auth_password: 'password'

# Plantillas de notificación
templates:
  - '/etc/alertmanager/templates/*.tmpl'

# Configuración de enrutamiento
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
    # Alertas críticas van a Slack y Email inmediatamente
    - match:
        severity: critical
      receiver: 'critical-alerts'
      group_wait: 5s
      repeat_interval: 5m
    
    # Alertas de warning van a Slack
    - match:
        severity: warning
      receiver: 'warning-alerts'
      repeat_interval: 30m
    
    # Alertas de base de datos son críticas
    - match:
        service: mysql
      receiver: 'critical-alerts'
    - match:
        service: postgres
      receiver: 'critical-alerts'

# Configuración de receptores
receivers:
  # Receptor por defecto - webhook
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://localhost:5001/webhook'
        send_resolved: true
  
  # Alertas críticas
  - name: 'critical-alerts'
    email_configs:
      - to: 'admin@shibasito-banco.com'
        subject: '🚨 ALERTA CRÍTICA - {{ .GroupLabels.service }}'
        body: |
          Alerta: {{ .GroupLabels.alertname }}
          Servicio: {{ .GroupLabels.service }}
          Severidad: {{ .Labels.severity }}
          Descripción: {{ range .Alerts }}{{ .Annotations.description }}{{ end }}
          
          Estado: {{ if eq .Status "firing" }}ACTIVA{{ else }}RESUELTA{{ end }}
          Hora: {{ .CommonAnnotations.timestamp }}
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts-critical'
        title: '🚨 Alerta Crítica - {{ .GroupLabels.service }}'
        text: |
          *Alerta:* {{ .GroupLabels.alertname }}
          *Servicio:* {{ .GroupLabels.service }}
          *Descripción:* {{ range .Alerts }}{{ .Annotations.description }}{{ end }}
        send_resolved: true
  
  # Alertas de warning
  - name: 'warning-alerts'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts-warning'
        title: '⚠️ Alerta de Warning - {{ .GroupLabels.service }}'
        text: |
          *Alerta:* {{ .GroupLabels.alertname }}
          *Servicio:* {{ .GroupLabels.service }}
          *Descripción:* {{ range .Alerts }}{{ .Annotations.description }}{{ end }}
        send_resolved: true

# Reglas de inhibición
inhibit_rules:
  # Si un servicio está down, inhibir otras alertas del mismo servicio
  - source_match:
      alertname: 'ServicioBancoNoDisponible'
    target_match:
      service: 'lp1-banco'
    equal: ['instance']
  
  - source_match:
      alertname: 'ServicioRENEICNoDisponible'
    target_match:
      service: 'lp2-reniec'
    equal: ['instance']
EOF

    log "Configuración de AlertManager creada"
}

# Función para crear script de backup
create_backup_script() {
    log "Creando script de backup..."
    
    local backup_script="$(dirname "$0")/backup-monitoring.sh"
    
    cat > "$backup_script" << 'EOF'
#!/bin/bash

# Script de backup del stack de monitoreo
BACKUP_DIR="./backup/monitoring"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR/$DATE"

# Backup de configuraciones
cp -r ./config/monitoring/* "$BACKUP_DIR/$DATE/config/"

# Backup de datos de Prometheus
docker exec shibasito-prometheus tar czf - /prometheus > "$BACKUP_DIR/$DATE/prometheus_data.tar.gz"

# Backup de datos de Grafana
docker exec shibasito-grafana tar czf - /var/lib/grafana > "$BACKUP_DIR/$DATE/grafana_data.tar.gz"

# Backup de configuración de AlertManager
docker exec shibasito-alertmanager tar czf - /alertmanager > "$BACKUP_DIR/$DATE/alertmanager_data.tar.gz"

echo "Backup completado en $BACKUP_DIR/$DATE"
EOF

    chmod +x "$backup_script"
    log "Script de backup creado"
}

# Función para verificar la instalación
verify_installation() {
    log "Verificando instalación..."
    
    local errors=0
    
    # Verificar que todos los servicios estén corriendo
    local services=("shibasito-prometheus" "shibasito-grafana" "shibasito-alertmanager" "shibasito-node-exporter")
    
    for service in "${services[@]}"; do
        if docker ps | grep -q "$service"; then
            log "✓ $service está corriendo"
        else
            error "✗ $service no está corriendo"
            ((errors++))
        fi
    done
    
    # Verificar endpoints
    local endpoints=(
        "http://localhost:9090/api/v1/query?query=up"
        "http://localhost:3000/api/health"
        "http://localhost:9093/-/healthy"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -sf "$endpoint" >/dev/null; then
            log "✓ $endpoint responde correctamente"
        else
            warn "✗ $endpoint no responde"
            ((errors++))
        fi
    done
    
    if [ $errors -eq 0 ]; then
        log "✅ Instalación completada exitosamente"
    else
        error "❌ Instalación completada con $errors errores"
    fi
}

# Función principal
main() {
    log "======================================"
    log "Iniciando instalación del Stack de Monitoreo"
    log "Sistema Bancario Distribuido - Shibasito"
    log "======================================"
    
    # Cambiar al directorio del script
    cd "$(dirname "$0")/../.."
    
    # Ejecutar pasos de instalación
    check_dependencies
    create_directories
    create_docker_compose
    create_alertmanager_config
    create_backup_script
    
    log ""
    log "======================================"
    log "Para iniciar el stack de monitoreo, ejecuta:"
    log "  docker-compose -f docker-compose.monitoring.yml up -d"
    log ""
    log "Para verificar el estado:"
    log "  ./scripts/monitor-services.sh status"
    log ""
    log "Para acceder a las interfaces:"
    log "  - Grafana: http://localhost:3000 (admin/admin123)"
    log "  - Prometheus: http://localhost:9090"
    log "  - AlertManager: http://localhost:9093"
    log "======================================"
    
    # Preguntar si quiere iniciar ahora
    read -p "¿Deseas iniciar el stack de monitoreo ahora? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Iniciando stack de monitoreo..."
        docker-compose -f docker-compose.monitoring.yml up -d
        
        log "Esperando que los servicios estén listos..."
        sleep 30
        
        verify_installation
    else
        log "Instalación completada. Puedes iniciar el stack cuando quieras."
    fi
}

# Ejecutar función principal
main "$@"