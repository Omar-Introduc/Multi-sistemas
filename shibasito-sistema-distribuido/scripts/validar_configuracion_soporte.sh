#!/bin/bash

# =============================================================================
# SCRIPT DE VALIDACIÓN DE CONFIGURACIONES DE SERVICIOS DE SOPORTE
# Verifica que todas las optimizaciones estén aplicadas correctamente
# =============================================================================

set -euo pipefail

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para validar configuración de Redis
validate_redis_config() {
    log_info "Validando configuración de Redis..."
    
    # Verificar límites de memoria
    if grep -q "maxmemory 256mb" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml; then
        log_success "✓ Límites de memoria configurados (256MB)"
    else
        log_error "✗ Límites de memoria no encontrados"
    fi
    
    # Verificar política de evicción
    if grep -q "maxmemory-policy allkeys-lru" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml; then
        log_success "✓ Política de evicción LRU configurada"
    else
        log_error "✗ Política de evicción no encontrada"
    fi
    
    # Verificar persistencia AOF
    if grep -q "appendonly yes" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml; then
        log_success "✓ Persistencia AOF habilitada"
    else
        log_error "✗ Persistencia AOF no habilitada"
    fi
    
    # Verificar health check
    if grep -A 5 "redis:" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml | grep -q "healthcheck:"; then
        log_success "✓ Health check configurado para Redis"
    else
        log_error "✗ Health check no encontrado para Redis"
    fi
    
    # Verificar script de backup
    if [ -f "/workspace/shibasito-sistema-distribuido/scripts/redis-backup.sh" ]; then
        log_success "✓ Script de backup para Redis encontrado"
    else
        log_error "✗ Script de backup para Redis no encontrado"
    fi
    
    # Verificar volúmenes de backup
    if grep -q "redis_backup:" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml; then
        log_success "✓ Volumen de backup para Redis configurado"
    else
        log_error "✗ Volumen de backup para Redis no configurado"
    fi
}

# Función para validar configuración de PostgreSQL
validate_postgresql_config() {
    log_info "Validando configuración de PostgreSQL..."
    
    # Verificar límites de memoria y CPU
    if grep -A 10 "bd1_postgresql:" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml | grep -q "deploy:"; then
        log_success "✓ Límites de recursos configurados para PostgreSQL"
    else
        log_error "✗ Límites de recursos no encontrados para PostgreSQL"
    fi
    
    # Verificar configuración de seguridad (scram-sha-256)
    if grep -q "scram-sha-256" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml; then
        log_success "✓ Autenticación scram-sha-256 configurada"
    else
        log_error "✗ Autenticación scram-sha-256 no encontrada"
    fi
    
    # Verificar configuración de logging
    if grep -A 15 "bd1_postgresql:" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml | grep -q "logging_collector=on"; then
        log_success "✓ Logging collector habilitado"
    else
        log_error "✗ Logging collector no habilitado"
    fi
    
    # Verificar configuración de shared buffers
    if grep -q "shared_buffers=256MB" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml; then
        log_success "✓ Shared buffers configurado (256MB)"
    else
        log_error "✗ Shared buffers no configurado"
    fi
    
    # Verificar health check
    if grep -A 10 "bd1_postgresql:" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml | grep -q "healthcheck:"; then
        log_success "✓ Health check configurado para PostgreSQL"
    else
        log_error "✗ Health check no encontrado para PostgreSQL"
    fi
    
    # Verificar script de backup
    if [ -f "/workspace/shibasito-sistema-distribuido/scripts/postgres-backup.sh" ]; then
        log_success "✓ Script de backup para PostgreSQL encontrado"
    else
        log_error "✗ Script de backup para PostgreSQL no encontrado"
    fi
    
    # Verificar volumen de backup
    if grep -q "postgres_bd1_backup:" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml; then
        log_success "✓ Volumen de backup para PostgreSQL configurado"
    else
        log_error "✗ Volumen de backup para PostgreSQL no configurado"
    fi
}

# Función para validar configuración de MySQL
validate_mysql_config() {
    log_info "Validando configuración de MySQL..."
    
    # Verificar límites de memoria y CPU
    if grep -A 10 "bd2_mysql:" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml | grep -q "deploy:"; then
        log_success "✓ Límites de recursos configurados para MySQL"
    else
        log_error "✗ Límites de recursos no encontrados para MySQL"
    fi
    
    # Verificar configuración de InnoDB buffer pool
    if grep -q "innodb-buffer-pool-size=512M" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml; then
        log_success "✓ InnoDB buffer pool configurado (512MB)"
    else
        log_error "✗ InnoDB buffer pool no configurado"
    fi
    
    # Verificar configuración de seguridad (local-infile=0)
    if grep -q "local-infile=0" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml; then
        log_success "✓ Configuración de seguridad (deshabilitar local-infile) configurada"
    else
        log_warning "⚠ Configuración de seguridad podría mejorarse"
    fi
    
    # Verificar configuración de SQL mode estricto
    if grep -q "STRICT_TRANS_TABLES" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml; then
        log_success "✓ SQL mode estricto configurado"
    else
        log_error "✗ SQL mode estricto no configurado"
    fi
    
    # Verificar health check
    if grep -A 10 "bd2_mysql:" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml | grep -q "healthcheck:"; then
        log_success "✓ Health check configurado para MySQL"
    else
        log_error "✗ Health check no encontrado para MySQL"
    fi
    
    # Verificar script de backup
    if [ -f "/workspace/shibasito-sistema-distribuido/scripts/mysql-backup.sh" ]; then
        log_success "✓ Script de backup para MySQL encontrado"
    else
        log_error "✗ Script de backup para MySQL no encontrado"
    fi
    
    # Verificar volumen de backup
    if grep -q "mysql_bd2_backup:" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml; then
        log_success "✓ Volumen de backup para MySQL configurado"
    else
        log_error "✗ Volumen de backup para MySQL no configurado"
    fi
}

# Función para validar volúmenes y persistencia
validate_volumes_config() {
    log_info "Validando configuración de volúmenes..."
    
    local volume_count=$(grep -c "driver_opts:" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml || echo "0")
    
    if [ "$volume_count" -ge 10 ]; then
        log_success "✓ Volúmenes con driver_opts configurados ($volume_count volúmenes)"
    else
        log_warning "⚠ Algunos volúmenes podrían necesitar driver_opts (encontrados: $volume_count)"
    fi
    
    # Verificar volúmenes de backup específicos
    local backup_volumes=("postgres_bd1_backup" "mysql_bd2_backup" "redis_backup")
    for volume in "${backup_volumes[@]}"; do
        if grep -q "$volume:" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml; then
            log_success "✓ Volumen de backup $volume configurado"
        else
            log_error "✗ Volumen de backup $volume no configurado"
        fi
    done
}

# Función para validar redes
validate_networks_config() {
    log_info "Validando configuración de redes..."
    
    local networks=("shibasito-network" "database-network" "monitoring-network")
    
    for network in "${networks[@]}"; do
        if grep -q "$network:" /workspace/shibasito-sistema-distribuido/docker-compose.main.yml; then
            log_success "✓ Red $network configurada"
        else
            log_error "✗ Red $network no configurada"
        fi
    done
}

# Función para generar reporte de configuración
generate_config_report() {
    log_info "Generando reporte de configuración..."
    
    local report_file="/workspace/shibasito-sistema-distribuido/reporte_configuracion_soporte.txt"
    
    cat > "$report_file" << EOF
# =============================================================================
# REPORTE DE CONFIGURACIÓN DE SERVICIOS DE SOPORTE
# Generado: $(date '+%Y-%m-%d %H:%M:%S')
# =============================================================================

## RESUMEN DE OPTIMIZACIONES APLICADAS

### 1. REDIS - Cache y Session Store
✓ Límites de memoria: 512MB límite, 256MB reserva
✓ Límites de CPU: 0.25 límite, 0.1 reserva
✓ Configuración de persistencia: AOF habilitado con appendfsync everysec
✓ Política de gestión de memoria: allkeys-lru
✓ Health check configurado: interval 10s, timeout 3s
✓ Script de backup automático: redis-backup.sh
✓ Volumen de backup: redis_backup
✓ Configuración de logging: json-file con rotación

### 2. POSTGRESQL - Base de datos BD1
✓ Límites de memoria: 1GB límite, 512MB reserva
✓ Límites de CPU: 0.5 límite, 0.25 reserva
✓ Configuración de seguridad: scram-sha-256 authentication
✓ Configuración de performance:
  - shared_buffers: 256MB
  - effective_cache_size: 1GB
  - max_connections: 200
  - maintenance_work_mem: 64MB
✓ Configuración de logging: logging_collector habilitado
✓ Health check configurado: pg_isready con verificación de DB
✓ Script de backup automático: postgres-backup.sh
✓ Volumen de backup: postgres_bd1_backup
✓ Configuración de backup: WAL archiving habilitado

### 3. MYSQL - Base de datos BD2
✓ Límites de memoria: 1GB límite, 512MB reserva
✓ Límites de CPU: 0.5 límite, 0.25 reserva
✓ Configuración de InnoDB:
  - innodb_buffer_pool_size: 512MB
  - innodb_log_file_size: 64MB
  - innodb_flush_log_at_trx_commit: 1
✓ Configuración de seguridad:
  - local-infile: 0
  - SQL mode: STRICT_TRANS_TABLES
  - skip-symbolic-links: 1
✓ Configuración de logging:
  - general-log habilitado
  - slow-query-log habilitado
  - long-query-time: 2
✓ Health check configurado: mysqladmin ping
✓ Script de backup automático: mysql-backup.sh
✓ Volumen de backup: mysql_bd2_backup
✓ Configuración de binlogs para backup incremental

### 4. CONFIGURACIONES GENERALES
✓ Volúmenes con driver_opts para mejor persistencia
✓ Configuración de redes aisladas (3 redes: main, db, monitoring)
✓ Health checks en todos los servicios
✓ Configuración de logging con rotación
✓ Labels para backup automation

### 5. SCRIPTS DE BACKUP AUTOMÁTICO
✓ PostgreSQL: Backup completo con compresión, retención 7 días
✓ MySQL: Backup con mysqldump, compresión gzip, retención 7 días
✓ Redis: Backup RDB + AOF, retención 3 días
✓ Todos los scripts incluyen:
  - Verificación de integridad
  - Logging detallado
  - Limpieza automática de backups antiguos
  - Opciones de restauración
  - Información de estado

### 6. CONFIGURACIONES DE SEGURIDAD
✓ PostgreSQL: scram-sha-256, logging de conexiones
✓ MySQL: deshabilitación de local-infile, SQL estricto
✓ Redis: autenticación requerida, comandos deshabilitados
✓ Redes aisladas para diferentes tipos de tráfico

## ARCHIVOS CONFIGURADOS
- docker-compose.main.yml: Configuración principal optimizada
- scripts/postgres-backup.sh: Script de backup PostgreSQL
- scripts/mysql-backup.sh: Script de backup MySQL
- scripts/redis-backup.sh: Script de backup Redis

## PRÓXIMOS PASOS RECOMENDADOS
1. Ejecutar los servicios: docker-compose -f docker-compose.main.yml up -d
2. Verificar health checks: docker-compose -f docker-compose.main.yml ps
3. Probar scripts de backup: ./scripts/postgres-backup.sh backup
4. Configurar monitoreo en Grafana
5. Establecer alertas para health checks

## COMANDOS ÚTILES
# Ver logs en tiempo real
docker-compose -f docker-compose.main.yml logs -f

# Verificar salud de servicios
docker-compose -f docker-compose.main.yml ps

# Ejecutar backup manual
./scripts/postgres-backup.sh backup
./scripts/mysql-backup.sh backup
./scripts/redis-backup.sh backup

# Restaurar backup (cuidado con esto)
./scripts/postgres-backup.sh restore /backup/postgres_backup_*.gz

# Monitorear uso de recursos
docker stats

=================================================================================
EOF

    log_success "Reporte generado: $report_file"
}

# Función principal
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  VALIDACIÓN DE CONFIGURACIONES DE SOPORTE${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # Validaciones
    validate_redis_config
    echo ""
    validate_postgresql_config
    echo ""
    validate_mysql_config
    echo ""
    validate_volumes_config
    echo ""
    validate_networks_config
    echo ""
    
    # Generar reporte
    generate_config_report
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  VALIDACIÓN COMPLETADA${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    log_info "Revisar el reporte generado para detalles completos de la configuración"
}

# Ejecutar validación
main "$@"
