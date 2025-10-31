# EJEMPLO RÁPIDO DE USO

## Verificación Rápida del Sistema

```bash
# 1. Validar la instalación
./scripts/validate.sh

# 2. Ejecutar health check general
./scripts/health-check.sh

# 3. Generar reporte completo
./scripts/generate-health-report.sh
```

## Instalación Completa en Producción

```bash
# 1. Instalar sistema completo (requiere sudo)
sudo ./scripts/install.sh

# 2. Configurar cron para ejecución automática
sudo ./scripts/setup-cron.sh

# 3. Verificar que cron esté activo
sudo crontab -l | grep health-checks

# 4. Ver logs en tiempo real
tail -f /var/log/health-checks/health-check-cron.log
```

## Configuración de Credenciales

```bash
# 1. Crear archivo de configuración
cp scripts/config.env.example scripts/config.env

# 2. Editar credenciales
nano scripts/config.env

# 3. Configurar variables importantes:
# - RABBITMQ_USER y RABBITMQ_PASSWORD
# - REDIS_PASSWORD
# - DB_POSTGRES_USER y DB_POSTGRES_PASSWORD
# - DB_MYSQL_USER y DB_MYSQL_PASSWORD
# - ALERT_EMAIL
```

## Docker - Ejecución Rápida

```bash
# 1. Construir imagen
docker build -f scripts/Dockerfile -t health-checks .

# 2. Ejecutar contenedor con configuración
docker run -d \
  --name health-checks-monitor \
  -v $(pwd)/scripts/config.env:/app/config.env:ro \
  -v $(pwd)/scripts/logs:/app/logs \
  -v $(pwd)/scripts/reports:/app/reports \
  health-checks

# 3. Ver logs del contenedor
docker logs -f health-checks-monitor

# 4. Ejecutar health check manual en contenedor
docker exec health-checks-monitor /app/health-check.sh
```

## Verificación de Servicios Específicos

```bash
# Solo bases de datos
./scripts/check-db-connections.sh

# Solo RabbitMQ
./scripts/check-rabbitmq.sh

# Solo Redis
./scripts/check-redis.sh

# Reporte completo con alertas
./scripts/generate-health-report.sh
```

## Monitoreo de Logs

```bash
# Ver logs generales
cat scripts/logs/health-check-$(date +%Y%m%d).log

# Ver alertas
tail -f scripts/logs/alerts.log

# Ver reportes generados
ls -lah scripts/reports/

# Abrir reporte HTML
# (usar navegador web)
firefox scripts/reports/health-report-*.html
```

## Solución de Problemas Comunes

### Error: "command not found"
```bash
# Instalar dependencias faltantes
sudo apt-get install postgresql-client mysql-client redis-tools rabbitmq-tools
```

### Error: "Permission denied"
```bash
# Ejecutar con sudo
sudo ./scripts/health-check.sh

# O cambiar propietario
sudo chown -R $USER:$USER scripts/
```

### Error: "Connection refused"
```bash
# Verificar que los servicios estén corriendo
sudo systemctl status postgresql redis rabbitmq-server

# Iniciar servicios si están parados
sudo systemctl start postgresql redis rabbitmq-server
```

### Timeout en verificaciones
```bash
# Aumentar timeout editando la variable en el script
# En health-check.sh, cambiar:
TIMEOUT=60  # Era 30
```

## Personalización de Umbrales

```bash
# Editar config.env.example y copiar a config.env
# Modificar umbrales:
export CPU_THRESHOLD_WARNING="70"
export MEMORY_THRESHOLD_WARNING="80"
export DISK_THRESHOLD_WARNING="85"
export DB_CONNECTION_THRESHOLD="80"
```

## Integración con Alertas Externas

### Slack
```bash
# En config.env:
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
export ENABLE_SLACK_ALERTS="true"
```

### Email
```bash
# En config.env:
export ALERT_EMAIL="admin@tudominio.com"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_USER="alerts@tudominio.com"
```

## Limpieza y Mantenimiento

```bash
# Limpiar logs antiguos (>30 días)
find scripts/logs/ -name "*.log" -mtime +30 -delete

# Limpiar reportes antiguos (>90 días)
find scripts/reports/ -name "*.html" -mtime +90 -delete
find scripts/reports/ -name "*.json" -mtime +90 -delete

# Backup de configuraciones
tar -czf health-checks-backup-$(date +%Y%m%d).tar.gz scripts/
```

## Verificación Final

```bash
# 1. Ejecutar validación
./scripts/validate.sh

# 2. Probar cada script individualmente
for script in health-check.sh check-db-connections.sh check-rabbitmq.sh check-redis.sh; do
  echo "Probando: $script"
  ./scripts/$script
  echo "---"
done

# 3. Generar reporte final
./scripts/generate-health-report.sh

# 4. Verificar archivos generados
ls -lah scripts/logs/ scripts/reports/
```

## Estado Final Esperado

```
✓ Todos los scripts ejecutables
✓ Logs generados en scripts/logs/
✓ Reportes HTML y JSON en scripts/reports/
✓ Configuración de cron activa (si se instaló)
✓ Sistema de alertas funcionando
```

## Documentación Completa

Para más información, consulta:
- README.md - Documentación completa
- RESUMEN.md - Resumen ejecutivo
- config.env.example - Todas las opciones de configuración
