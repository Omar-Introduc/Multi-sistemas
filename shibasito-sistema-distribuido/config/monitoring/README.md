# Stack de Monitoreo - Sistema Bancario Distribuido

## Descripción General

Este stack de monitoreo proporciona una solución completa para monitorear el sistema bancario distribuido "Shibasito", incluyendo servicios LP1, LP2 y LP3, así como toda la infraestructura subyacente.

## Componentes del Stack

### 📊 Prometheus (Métricas)
- **Puerto**: 9090
- **Descripción**: Sistema de recolección y almacenamiento de métricas
- **Configuración**: `config/monitoring/prometheus.yml`
- **Funciones**:
  - Recolección de métricas de todos los servicios
  - Configuración de targets para LP1, LP2, LP3
  - Métricas de infraestructura (CPU, memoria, disco)
  - Métricas de bases de datos (MySQL, PostgreSQL)
  - Métricas de mensajería (RabbitMQ, Redis)

### 🎯 Grafana (Visualización)
- **Puerto**: 3000
- **Credenciales**: admin/admin123
- **Descripción**: Plataforma de visualización y dashboards
- **Configuración**: `config/monitoring/grafana/`
- **Dashboards disponibles**:
  - Dashboard Ejecutivo del Sistema Bancario
  - Métricas de rendimiento por servicio
  - Alertas y notificaciones

### 🚨 AlertManager (Alertas)
- **Puerto**: 9093
- **Descripción**: Gestión de alertas y notificaciones
- **Configuración**: `config/monitoring/alertmanager.yml`
- **Canales de notificación**:
  - Email (admin@shibasito-banco.com)
  - Slack (#alerts-critical, #alerts-warning)
  - Webhooks personalizados

### 📈 Exporters
- **Node Exporter** (puerto 9100): Métricas del sistema
- **Redis Exporter** (puerto 9121): Métricas de Redis
- **MySQL Exporter** (puerto 9104): Métricas de MySQL
- **PostgreSQL Exporter** (puerto 9187): Métricas de PostgreSQL

## Estructura de Archivos

```
config/monitoring/
├── prometheus.yml           # Configuración principal de Prometheus
├── alerting.yml            # Reglas de alertas
├── alertmanager.yml        # Configuración de AlertManager
├── grafana/
│   ├── dashboards.json     # Dashboard principal del sistema
│   └── datasources.yml     # Configuración de datasources
└── scripts/
    ├── setup-monitoring.sh # Instalación automática
    └── monitor-services.sh # Script de monitoreo
```

## Instalación Rápida

### 1. Ejecutar Instalación Automática

```bash
cd shibasito-sistema-distribuido
./config/monitoring/scripts/setup-monitoring.sh
```

### 2. Iniciar Stack Manualmente

```bash
# Iniciar servicios de monitoreo
docker-compose -f docker-compose.monitoring.yml up -d

# Verificar estado
./config/monitoring/scripts/monitor-services.sh status
```

### 3. Acceder a Interfaces

- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093

## Métricas Personalizadas

### LP1 - Servicio Banco
- `banco_transacciones_total`: Contador de transacciones procesadas
- `banco_cuentas_activas`: Número de cuentas activas
- `banco_saldo_promedio`: Saldo promedio de cuentas
- `banco_errores_validacion`: Errores de validación por operación

### LP2 - Servicio RENIEC
- `reniec_consultas_total`: Total de consultas realizadas
- `reniec_tiempo_consulta`: Tiempo promedio de consulta
- `reniec_documentos_validados`: Documentos validados exitosamente
- `reniec_errores_sistema`: Errores del sistema por consulta

### LP3 - Aplicaciones Cliente
- `lp3_sesiones_activas`: Sesiones activas de usuario
- `lp3_requests_exitosas`: Requests exitosas por aplicación
- `lp3_tiempo_responda_promedio`: Tiempo de respuesta promedio
- `lp3_usuarios_conectados`: Número de usuarios conectados

## Alertas Críticas Configuradas

### 🔴 Alertas Críticas (Respuesta Inmediata)
- Servicios principales caídos (LP1, LP2)
- Bases de datos inaccesibles (MySQL, PostgreSQL)
- RabbitMQ o Redis caídos
- Espacio en disco < 15%
- Operaciones sospechosas detectadas

### 🟡 Alertas de Warning (Monitoreo)
- Alto tiempo de respuesta (>2s LP1, >3s LP2)
- Alto uso de CPU (>80%) o memoria (>85%)
- Conexiones de base de datos > 80%
- Colas de mensajes con alto volumen (>1000)

### 🔵 Alertas Informativas
- Bajo volumen de transacciones
- Alto volumen de consultas RENIEC
- Violación de SLA (>99% uptime)

## Dashboards Disponibles

### Dashboard Ejecutivo
- Vista general del estado del sistema
- Métricas de rendimiento en tiempo real
- Alertas activas
- KPIs de negocio
- Estado de servicios críticos

### Dashboard Técnico Detallado
- Métricas por servicio
- Gráficos de tendencias
- Análisis de capacidad
- Logs y eventos

## Scripts de Gestión

### Script de Monitoreo

```bash
# Ver estado general
./config/monitoring/scripts/monitor-services.sh status

# Ver logs específicos
./config/monitoring/scripts/monitor-services.sh logs prometheus 100

# Reiniciar servicios
./config/monitoring/scripts/monitor-services.sh restart

# Ver métricas específicas
./config/monitoring/scripts/monitor-services.sh metrics performance
./config/monitoring/scripts/monitor-services.sh metrics resources
./config/monitoring/scripts/monitor-services.sh metrics business

# Detener servicios
./config/monitoring/scripts/monitor-services.sh stop

# Iniciar servicios
./config/monitoring/scripts/monitor-services.sh start
```

### Script de Backup

```bash
# Crear backup completo
./config/monitoring/scripts/backup-monitoring.sh

# Los backups se guardan en ./backup/monitoring/
```

## Configuración de Notificaciones

### Email
- Configurado en `alertmanager.yml`
- Destinatarios críticos: admin@shibasito-banco.com
- Plantillas personalizables

### Slack
- Requiere configurar webhook URL en `alertmanager.yml`
- Canales separados por severidad:
  - `#alerts-critical`: Alertas críticas
  - `#alerts-warning`: Alertas de warning

### Webhooks
- Endpoint configurado: `http://localhost:5001/webhook`
- Compatible con sistemas de ticketing
- Datos JSON con información completa de alertas

## Mantenimiento

### Backup Automático
```bash
# Configurar cron para backups diarios
# Editar crontab
crontab -e

# Agregar línea para backup diario a las 2 AM
0 2 * * * /path/to/backup-monitoring.sh >> /var/log/monitoring-backup.log 2>&1
```

### Limpieza de Datos
```bash
# Limpiar logs antiguos (ejecutar semanalmente)
find logs/ -name "*.log" -mtime +30 -delete

# Limpiar backups antiguos (mantener últimos 7 días)
find backup/ -name "*.tar.gz" -mtime +7 -delete
```

### Actualizaciones
```bash
# Actualizar imágenes de Docker
docker-compose -f docker-compose.monitoring.yml pull

# Reiniciar con nuevas imágenes
docker-compose -f docker-compose.monitoring.yml up -d
```

## Troubleshooting

### Problemas Comunes

1. **Servicios no inician**
   ```bash
   # Verificar logs
   ./config/monitoring/scripts/monitor-services.sh logs prometheus
   
   # Reiniciar stack
   docker-compose -f docker-compose.monitoring.yml down
   docker-compose -f docker-compose.monitoring.yml up -d
   ```

2. **Métricas no aparecen**
   - Verificar configuración de targets en Prometheus
   - Comprobar conectividad de red entre contenedores
   - Validar configuración de exporters

3. **Alertas no se envían**
   - Verificar configuración de AlertManager
   - Comprobar conectividad de red para email/Slack
   - Revisar logs de AlertManager

### Logs Importantes
```bash
# Prometheus
docker logs shibasito-prometheus

# Grafana
docker logs shibasito-grafana

# AlertManager
docker logs shibasito-alertmanager
```

### Endpoints de Salud
- Prometheus: http://localhost:9090/-/healthy
- Grafana: http://localhost:3000/api/health
- AlertManager: http://localhost:9093/-/healthy

## Métricas de Rendimiento Esperadas

### SLA Objetivos
- **Disponibilidad**: 99.9%
- **Tiempo de respuesta P95**: < 2 segundos
- **Tiempo de respuesta P99**: < 5 segundos
- **Uptime de bases de datos**: 99.95%

### Límites de Alerta
- CPU: Warning > 80%, Critical > 90%
- Memoria: Warning > 85%, Critical > 95%
- Disco: Warning > 80%, Critical > 90%
- Conexiones DB: Warning > 80%, Critical > 95%

## Contacto y Soporte

Para soporte técnico o consultas sobre el sistema de monitoreo:
- **Email**: soporte@shibasito-banco.com
- **Documentación**: Este README y archivos de configuración
- **Logs**: Directorio `logs/` y salida de scripts

---

**Nota**: Este stack está diseñado específicamente para el Sistema Bancario Distribuido Shibasito y puede requerir ajustes según las necesidades específicas del entorno de producción.