#!/bin/bash

# =============================================================================
# SCRIPT DE INICIALIZACIÓN DE REDIS
# Sistema Distribuido Shibasito - Setup completo de Redis
# =============================================================================

set -e  # Salir en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración por defecto
REDIS_VERSION="7.2"
REDIS_PORT=6379
REDIS_PASSWORD="redispass123_secure_2024"
REDIS_DATA_DIR="/data"
REDIS_LOG_DIR="/var/log/redis"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# =============================================================================
# FUNCIONES DE VERIFICACIÓN
# =============================================================================

check_redis_installed() {
    if command -v redis-server &> /dev/null; then
        local current_version=$(redis-server --version | grep -oE 'redis-server [0-9]+\.[0-9]+' | grep -oE '[0-9]+\.[0-9]+')
        log "Redis ya está instalado - Versión: $current_version"
        return 0
    else
        log "Redis no está instalado"
        return 1
    fi
}

check_port_available() {
    if netstat -ln | grep ":$REDIS_PORT " > /dev/null 2>&1; then
        warn "El puerto $REDIS_PORT ya está en uso"
        return 1
    else
        log "Puerto $REDIS_PORT está disponible"
        return 0
    fi
}

check_system_requirements() {
    info "Verificando requerimientos del sistema..."
    
    # Verificar memoria disponible
    local memory_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    local memory_mb=$((memory_kb / 1024))
    
    if [ $memory_mb -lt 1024 ]; then
        error "Se requiere al menos 1GB de RAM disponible"
    fi
    
    # Verificar espacio en disco
    local disk_space=$(df -h $REDIS_DATA_DIR | awk 'NR==2 {print $4}' | sed 's/G//')
    
    if [ "${disk_space%.*}" -lt 2 ]; then
        error "Se requiere al menos 2GB de espacio libre en disco"
    fi
    
    log "Sistema cumple requerimientos - Memoria: ${memory_mb}MB, Disco disponible: ${disk_space}"
}

# =============================================================================
# FUNCIONES DE INSTALACIÓN
# =============================================================================

install_redis() {
    info "Iniciando instalación de Redis $REDIS_VERSION..."
    
    # Detectar distribución
    if [ -f /etc/debian_version ]; then
        install_redis_debian
    elif [ -f /etc/redhat-release ]; then
        install_redis_rhel
    else
        error "Distribución no soportada. Instala Redis manualmente."
    fi
}

install_redis_debian() {
    info "Instalando Redis en sistema Debian/Ubuntu..."
    
    # Actualizar paquetes
    apt-get update -y
    
    # Instalar Redis
    apt-get install -y redis-server
    
    # Habilitar servicio
    systemctl enable redis-server
    
    log "Redis instalado correctamente en Debian/Ubuntu"
}

install_redis_rhel() {
    info "Instalando Redis en sistema RHEL/CentOS..."
    
    # Instalar EPEL si no está disponible
    yum install -y epel-release
    
    # Instalar Redis
    yum install -y redis
    
    # Habilitar servicio
    systemctl enable redis
    
    log "Redis instalado correctamente en RHEL/CentOS"
}

# =============================================================================
# FUNCIONES DE CONFIGURACIÓN
# =============================================================================

setup_directories() {
    info "Creando directorios necesarios..."
    
    # Crear directorio de datos
    mkdir -p $REDIS_DATA_DIR
    chown redis:redis $REDIS_DATA_DIR
    
    # Crear directorio de logs
    mkdir -p $REDIS_LOG_DIR
    chown redis:redis $REDIS_LOG_DIR
    
    # Crear directorio para backups
    mkdir -p $REDIS_DATA_DIR/backups
    chown redis:redis $REDIS_DATA_DIR/backups
    
    log "Directorios creados correctamente"
}

configure_redis() {
    info "Configurando Redis..."
    
    # Configurar como servicio systemd
    cat > /etc/systemd/system/redis.service << EOF
[Unit]
Description=Redis In-Memory Data Store
After=network.target

[Service]
User=redis
Group=redis
ExecStart=/usr/bin/redis-server $SCRIPT_DIR/redis.conf
ExecStop=/usr/bin/redis-cli shutdown
Restart=always
RestartSec=5
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

    # Recargar systemd
    systemctl daemon-reload
    
    log "Servicio systemd configurado"
}

setup_cluster_config() {
    info "Configurando Redis Cluster..."
    
    # Crear configuración especial para cluster si no existe
    if [ ! -f "$SCRIPT_DIR/redis-cluster.conf" ]; then
        warn "Archivo redis-cluster.conf no encontrado, usando configuración por defecto"
    else
        info "Usando configuración de cluster existente"
    fi
    
    log "Configuración de cluster lista"
}

# =============================================================================
# FUNCIONES DE SEGURIDAD
# =============================================================================

setup_firewall() {
    info "Configurando firewall..."
    
    # Configurar iptables para permitir Redis
    iptables -A INPUT -p tcp --dport $REDIS_PORT -j ACCEPT
    
    # Para cluster
    iptables -A INPUT -p tcp --dport 16379 -j ACCEPT
    
    log "Firewall configurado para puertos Redis"
}

setup_selinux_context() {
    if command -v getenforce &> /dev/null && [ "$(getenforce)" != "Disabled" ]; then
        info "Configurando contexto SELinux para Redis..."
        setsebool -P redis_can_rsync 1
        setsebool -P redis_can_network_connect 1
    fi
}

# =============================================================================
# FUNCIONES DE BACKUP
# =============================================================================

setup_backup_system() {
    info "Configurando sistema de backup automático..."
    
    # Crear script de backup
    cat > $SCRIPT_DIR/backup-redis.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/data/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="redis_backup_$DATE.rdb"

# Crear backup de la base de datos actual
cp /data/dump.rdb "$BACKUP_DIR/$BACKUP_FILE" 2>/dev/null || {
    echo "Error: No se pudo crear backup"
    exit 1
}

# Comprimir backup
gzip "$BACKUP_DIR/$BACKUP_FILE"

# Mantener solo los últimos 30 backups
find $BACKUP_DIR -name "redis_backup_*.rdb.gz" -mtime +30 -delete

echo "Backup completado: $BACKUP_FILE.gz"
EOF

    chmod +x $SCRIPT_DIR/backup-redis.sh
    
    # Configurar cron para backup diario a las 2 AM
    (crontab -l 2>/dev/null; echo "0 2 * * * $SCRIPT_DIR/backup-redis.sh >> /var/log/redis/backup.log 2>&1") | crontab -
    
    log "Sistema de backup configurado - Ejecutándose diariamente a las 2:00 AM"
}

# =============================================================================
# FUNCIONES DE MONITOREO
# =============================================================================

setup_monitoring() {
    info "Configurando sistema de monitoreo..."
    
    # Crear script de health check
    cat > $SCRIPT_DIR/health-check.sh << 'EOF'
#!/bin/bash

REDIS_CLI="/usr/bin/redis-cli"
REDIS_PASS="redispass123_secure_2024"

# Test básico de conectividad
$REDIS_CLI -a $REDIS_PASS ping > /dev/null
if [ $? -eq 0 ]; then
    echo "OK: Redis está respondiendo"
    exit 0
else
    echo "ERROR: Redis no está respondiendo"
    exit 1
fi
EOF

    chmod +x $SCRIPT_DIR/health-check.sh
    
    # Configurar cron para health check cada 5 minutos
    (crontab -l 2>/dev/null; echo "*/5 * * * * $SCRIPT_DIR/health-check.sh >> /var/log/redis/health.log 2>&1") | crontab -
    
    log "Sistema de monitoreo configurado - Health check cada 5 minutos"
}

# =============================================================================
# FUNCIONES DE CLUSTER
# =============================================================================

setup_cluster_scripts() {
    info "Creando scripts para gestión de cluster..."
    
    # Script para crear cluster
    cat > $SCRIPT_DIR/create-cluster.sh << 'EOF'
#!/bin/bash

# Script para crear un cluster de Redis
# Usar: ./create-cluster.sh <num_nodes>

if [ "$#" -ne 1 ]; then
    echo "Uso: $0 <numero_de_nodos>"
    echo "Ejemplo: $0 3"
    exit 1
fi

NODES=$1

echo "Creando cluster de $NODES nodos..."

# Aquí se implementarían los comandos para crear cluster
# redis-cli --cluster create node1:6379 node2:6379 node3:6379

echo "Cluster creado (implementar lógica específica según infraestructura)"
EOF

    chmod +x $SCRIPT_DIR/create-cluster.sh
    
    log "Scripts de cluster creados"
}

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

main() {
    log "=== INICIANDO SETUP DE REDIS ==="
    log "Directorio de scripts: $SCRIPT_DIR"
    log "Versión objetivo: $REDIS_VERSION"
    log "Puerto: $REDIS_PORT"
    
    # Verificaciones previas
    check_system_requirements
    
    if ! check_redis_installed; then
        install_redis
    fi
    
    if ! check_port_available; then
        warn "El puerto está en uso, verificando si Redis ya está ejecutándose..."
    fi
    
    # Configuración
    setup_directories
    configure_redis
    setup_cluster_config
    
    # Seguridad
    setup_firewall
    setup_selinux_context
    
    # Backup y monitoreo
    setup_backup_system
    setup_monitoring
    setup_cluster_scripts
    
    log "=== SETUP COMPLETADO ==="
    log "Redis ha sido configurado correctamente"
    log ""
    log "Para iniciar Redis:"
    log "  systemctl start redis"
    log ""
    log "Para verificar estado:"
    log "  systemctl status redis"
    log "  redis-cli -a $REDIS_PASSWORD ping"
    log ""
    log "Archivos de configuración:"
    log "  Configuración principal: $SCRIPT_DIR/redis.conf"
    log "  Configuración cluster: $SCRIPT_DIR/redis-cluster.conf"
    log ""
    log "Scripts de gestión:"
    log "  Backup: $SCRIPT_DIR/backup-redis.sh"
    log "  Health check: $SCRIPT_DIR/health-check.sh"
    log "  Crear cluster: $SCRIPT_DIR/create-cluster.sh"
    log ""
    log "Logs de Redis: /var/log/redis/"
    log "Backups en: /data/backups/"
}

# =============================================================================
# EJECUCIÓN
# =============================================================================

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    error "Este script debe ejecutarse como root"
fi

# Ejecutar función principal
main "$@"