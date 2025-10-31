# Sistema de Health Checks Avanzados

Conjunto completo de scripts para monitoreo y verificación del estado de servicios críticos del sistema.

## Scripts Incluidos

### 1. `health-check.sh`
**Propósito:** Verificación general del sistema
**Uso:**
```bash
./health-check.sh
```

**Verificaciones incluidas:**
- Recursos del sistema (CPU, memoria, disco)
- Servicios críticos (nginx, postgresql, redis, rabbitmq-server)
- Conectividad de red
- Archivos de log críticos
- Configuraciones de servicios
- Verificaciones específicas de componentes

### 2. `check-db-connections.sh`
**Propósito:** Verificación de conectividad a bases de datos
**Uso:**
```bash
./check-db-connections.sh
```

**Verificaciones incluidas:**
- PostgreSQL (primary y replica)
- MySQL (primary y replica)
- MongoDB
- Métricas de bases de datos (conexiones activas, tamaño, integridad)
- Logs de bases de datos
- Estado de backups

### 3. `check-rabbitmq.sh`
**Propósito:** Verificación de RabbitMQ y colas de mensajes
**Uso:**
```bash
./check-rabbitmq.sh
```

**Verificaciones incluidas:**
- Estado del servicio RabbitMQ
- Conectividad API HTTP
- Estado de colas y exchanges
- Conexiones y canales
- Métricas de performance
- Logs y configuraciones

### 4. `check-redis.sh`
**Propósito:** Verificación de conectividad y estado de Redis
**Uso:**
```bash
./check-redis.sh
```

**Verificaciones incluidas:**
- Estado del servicio Redis
- Uso de memoria y fragmentación
- Conexiones y clientes
- Estadísticas de comandos
- Persistencia (RDB/AOF)
- Replicación (si está configurada)
- Latencia

### 5. `generate-health-report.sh`
**Propósito:** Generar reporte completo combinando todas las verificaciones
**Uso:**
```bash
./generate-health-report.sh
```

**Características:**
- Combina resultados de todos los scripts de verificación
- Genera reportes en formato HTML y JSON
- Incluye resumen estadístico
- Envía alertas automáticas
- Sistema de severidad (INFO, WARNING, ERROR)

## Configuración

### Variables de Entorno

Puedes configurar las siguientes variables de entorno:

**Para RabbitMQ:**
- `RABBITMQ_USER`: Usuario de RabbitMQ (default: admin)
- `RABBITMQ_PASSWORD`: Contraseña de RabbitMQ
- `RABBITMQ_HOST`: Host de RabbitMQ (default: localhost)
- `RABBITMQ_PORT`: Puerto de RabbitMQ (default: 15672)

**Para Redis:**
- `REDIS_HOST`: Host de Redis (default: localhost)
- `REDIS_PORT`: Puerto de Redis (default: 6379)
- `REDIS_PASSWORD`: Contraseña de Redis

**Para Bases de Datos:**
Modifica las configuraciones en `check-db-connections.sh`:
```bash
declare -A DB_CONFIGS
DB_CONFIGS["postgresql_primary"]="host=localhost port=5432 dbname=app_db user=app_user"
DB_CONFIGS["mysql_primary"]="--host=localhost --port=3306 --user=app_user"
```

### Configuración de Base de Datos

Para `check-db-connections.sh`, actualiza las credenciales de base de datos:

```bash
# PostgreSQL
export PGPASSWORD=tu_password
# O modificar en el script:
PGPASSWORD=tu_password psql -h host -U user -d dbname

# MySQL
# Modificar en el script las credenciales en la configuración DB_CONFIGS
```

## Instalación

### 1. Hacer ejecutables los scripts
```bash
chmod +x scripts/*.sh
```

### 2. Instalar dependencias requeridas
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    postgresql-client \
    mysql-client \
    redis-tools \
    rabbitmq-tools \
    curl \
    bc \
    jq \
    python3

# Verificar versiones
psql --version
mysql --version
redis-cli --version
rabbitmqctl --version
```

### 3. Configurar variables de entorno
Crea un archivo `.env`:
```bash
# /path/to/scripts/.env
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=your_password
REDIS_PASSWORD=your_redis_password
```

## Uso

### Ejecución Manual
```bash
# Verificación completa
./scripts/health-check.sh

# Solo bases de datos
./scripts/check-db-connections.sh

# Solo RabbitMQ
./scripts/check-rabbitmq.sh

# Solo Redis
./scripts/check-redis.sh

# Reporte completo
./scripts/generate-health-report.sh
```

### Ejecución Programada con Cron

Agregar al crontab:
```bash
crontab -e
```

**Ejemplos de configuraciones:**

1. **Health check cada 5 minutos:**
```bash
*/5 * * * * /path/to/scripts/health-check.sh >> /var/log/health-check.log 2>&1
```

2. **Verificación de bases de datos cada 15 minutos:**
```bash
*/15 * * * * /path/to/scripts/check-db-connections.sh >> /var/log/db-check.log 2>&1
```

3. **Reporte completo cada hora:**
```bash
0 * * * * /path/to/scripts/generate-health-report.sh >> /var/log/health-report.log 2>&1
```

4. **Reporte diario completo:**
```bash
0 6 * * * /path/to/scripts/generate-health-report.sh >> /var/log/daily-health-report.log 2>&1
```

### Configuración para Docker

Si usas Docker, puedes ejecutar los checks dentro del contenedor:
```bash
# Dockerfile
COPY scripts/ /usr/local/bin/health-checks/
RUN chmod +x /usr/local/bin/health-checks/*.sh

# docker-compose.yml
services:
  app:
    healthcheck:
      test: ["/usr/local/bin/health-checks/health-check.sh"]
      interval: 5m
      timeout: 30s
      retries: 3
```

## Salidas y Logs

### Archivos de Log
Los logs se guardan en `scripts/logs/`:
- `health-check-YYYYMMDD.log`: Logs del health check general
- `db-check-YYYYMMDD.log`: Logs de verificación de bases de datos
- `rabbitmq-check-YYYYMMDD.log`: Logs de verificación de RabbitMQ
- `redis-check-YYYYMMDD.log`: Logs de verificación de Redis
- `alerts.log`: Registro de alertas enviadas

### Reportes
Los reportes se generan en `scripts/reports/`:
- `health-report-YYYYMMDD_HHMMSS.html`: Reporte visual en HTML
- `health-report-YYYYMMDD_HHMMSS.json`: Datos en formato JSON

### Códigos de Salida
- `0`: Éxito (todos los checks OK)
- `1`: Advertencias (algunos checks con warnings)
- `2`: Error crítico (algunos checks fallaron)
- `3`: Error desconocido

## Integración con Sistemas de Alertas

### Email
Los scripts envían alertas por email si `mail` está disponible:
```bash
sudo apt-get install mailutils
```

### Slack
Para integrar con Slack, modifica el script para usar webhooks:
```bash
# En generate-health-report.sh, función send_alerts_if_needed
send_alert_to_slack() {
    local message="$1"
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"$message\"}" \
        YOUR_SLACK_WEBHOOK_URL
}
```

### Prometheus + Grafana
Los reportes JSON son compatibles con Prometheus para visualización:
```bash
# Extraer métricas para Prometheus
jq '.checks | to_entries | .[] | select(.value.status=="FAIL") | {check: .key, status: .value.status}' \
    scripts/reports/health-report-*.json
```

## Personalización

### Agregar Nuevas Verificaciones

1. **Crea una nueva función en el script correspondiente:**
```bash
check_custom_service() {
    log "INFO" "Verificando servicio personalizado..."
    
    # Tu lógica de verificación aquí
    
    if condition; then
        register_check_result "CUSTOM_SERVICE" "PASS" "Servicio OK" "INFO"
        return 0
    else
        register_check_result "CUSTOM_SERVICE" "FAIL" "Servicio con problemas" "ERROR"
        return 1
    fi
}
```

2. **Agrega la función a la función principal**

### Modificar Umbrales

Para cambiar los umbrales de alerta, edita las variables en los scripts:
```bash
# Ejemplo: Cambiar umbral de CPU en health-check.sh
CPU_THRESHOLD_WARNING=70  # Era 80
CPU_THRESHOLD_CRITICAL=90 # Era no definido
```

## Solución de Problemas

### Errores Comunes

1. **"command not found"**
   - Verifica que todas las dependencias estén instaladas
   - Usa `which psql mysql redis-cli rabbitmqctl` para verificar

2. **"Permission denied"**
   - Asegúrate de que el usuario tenga permisos para ejecutar systemctl
   - Para bases de datos, verifica credenciales

3. **"Connection refused"**
   - Verifica que los servicios estén corriendo
   - Confirma que los puertos estén abiertos

4. **Timeouts**
   - Aumenta el timeout en la variable `TIMEOUT`
   - Verifica conectividad de red

### Debugging

Activar modo debug:
```bash
# Al inicio del script, agregar:
set -x  # Debug mode
```

Ver logs detallados:
```bash
tail -f scripts/logs/health-check-$(date +%Y%m%d).log
```

## Mantenimiento

### Limpieza de Logs
Limpiar logs antiguos (>30 días):
```bash
find scripts/logs/ -name "*.log" -mtime +30 -delete
find scripts/reports/ -name "*" -mtime +30 -delete
```

### Backup de Configuraciones
Respaldo de configuraciones de salud:
```bash
tar -czf health-checks-backup-$(date +%Y%m%d).tar.gz scripts/
```

## Soporte

Para problemas o mejoras:
1. Revisa los logs en `scripts/logs/`
2. Verifica la configuración de servicios
3. Consulta la documentación de servicios específicos

## Licencia

Sistema de monitoreo interno - Usar según políticas de la organización.
