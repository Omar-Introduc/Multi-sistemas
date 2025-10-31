# Sistema de Validación del Sistema

Este directorio contiene un conjunto completo de scripts de validación y monitoreo del sistema, diseñados para garantizar la calidad, rendimiento y disponibilidad de las aplicaciones del sistema distribuido.

## 📋 Scripts Disponibles

### 1. `validate-system.sh` - Validación Completa del Sistema
**Propósito:** Validación integral de todos los componentes del sistema

**Funcionalidades:**
- ✅ Verificación de salud de todos los servicios
- ✅ Validación de conectividad de bases de datos
- ✅ Análisis de recursos del sistema (CPU, memoria, disco)
- ✅ Verificación de puertos y conectividad de red
- ✅ Validación del entorno Docker
- ✅ Generación de reportes HTML con métricas detalladas
- ✅ Sistema de alertas automáticas

**Uso:**
```bash
# Validación básica
./validate-system.sh

# Modo verbose
./validate-system.sh --verbose

# Con configuración personalizada
./validate-system.sh --timeout 60 --retries 3
```

### 2. `test-communication-flows.sh` - Testing de Flujos de Comunicación
**Propósito:** Validación de comunicación entre servicios y APIs

**Funcionalidades:**
- 🔄 Testing de APIs REST y endpoints HTTP
- 📡 Verificación de colas de mensajes RabbitMQ
- 🔗 Testing de comunicación inter-servicios
- 📊 Métricas de latencia y throughput
- 🔍 Health checks específicos
- 📈 Análisis de rendimiento de comunicación

**Uso:**
```bash
# Testing básico de comunicación
./test-communication-flows.sh

# Con timeout personalizado
./test-communication-flows.sh --timeout 60

# Testing intensivo
./test-communication-flows.sh --retries 5
```

### 3. `test-failure-scenarios.sh` - Testing de Escenarios de Fallo
**Propósito:** Simulación y testing de tolerancia a fallos del sistema

**Funcionalidades:**
- 💥 Simulación de indisponibilidad de servicios
- 🔌 Pérdida de conexión a bases de datos
- 🌐 Particiones de red
- ⚡ Alta carga del sistema
- 🛡️ Testing de recuperación automática
- 📊 Métricas de MTTD y MTTR (Mean Time To Detect/Recover)
- 🔧 Validación de circuit breakers

**Uso:**
```bash
# Testing de fallos básico
./test-failure-scenarios.sh

# Modo destructivo (cuidado: afecta disponibilidad)
./test-failure-scenarios.sh --destructive

# Modo simulación (sin cambios reales)
./test-failure-scenarios.sh --dry-run

# Con timeout de recuperación personalizado
./test-failure-scenarios.sh --timeout 300
```

### 4. `performance-benchmark.sh` - Benchmarks de Rendimiento
**Propósito:** Medición y análisis de rendimiento del sistema

**Funcionalidades:**
- ⚡ Benchmarks de respuesta individual
- 🚀 Testing de concurrencia
- 🔄 Benchmarks de carga sostenida
- 🗄️ Testing de rendimiento de bases de datos
- 💾 Stress testing del sistema
- 📊 Análisis de percentiles (P95, P99)
- 📈 Métricas de throughput y capacidad

**Uso:**
```bash
# Benchmark básico
./performance-benchmark.sh

# Con duración personalizada
./performance-benchmark.sh --duration 120

# Testing intensivo
./performance-benchmark.sh --concurrent 20 --requests 2000
```

### 5. `generate-system-report.sh` - Generación de Reportes del Sistema
**Propósito:** Consolidación y análisis de datos del sistema

**Funcionalidades:**
- 📊 Análisis consolidado de logs y métricas
- 📈 Identificación de tendencias y patrones
- 🎯 Generación de recomendaciones automáticas
- 📄 Reportes ejecutivos en múltiples formatos (HTML, JSON, CSV)
- 🔍 Análisis de errores y warnings
- 💡 Sistema de recomendaciones inteligente
- 🧹 Limpieza automática de archivos antiguos

**Uso:**
```bash
# Reporte de las últimas 24 horas
./generate-system-report.sh

# Reporte de los últimos 7 días
./generate-system-report.sh 7d

# Con retención personalizada
./generate-system-report.sh --days 60
```

### 6. `continuous-validation.sh` - Validación Continua
**Propósito:** Monitoreo continuo y automático del sistema

**Funcionalidades:**
- 🔄 Monitoreo en tiempo real de servicios críticos
- 🚨 Sistema de alertas inteligentes
- 📊 Recolección continua de métricas
- 📱 Notificaciones automáticas
- 📈 Reportes periódicos automáticos
- 🔧 Gestión de estados y recovery
- ⏰ Configuración de intervalos personalizables

**Uso:**
```bash
# Iniciar monitoreo continuo
./continuous-validation.sh

# Con intervalo personalizado
./continuous-validation.sh --interval 60

# Ver estado del monitoreo
./continuous-validation.sh --status

# Detener monitoreo
./continuous-validation.sh --stop

# Instalar como cron job
./continuous-validation.sh --install-cron
```

### 7. `master-validation.sh` - Validación Maestra
**Propósito:** Orquestación y ejecución de todos los scripts de validación

**Funcionalidades:**
- 🎯 Ejecución coordinada de todos los scripts
- ⚡ Modo paralelo y secuencial
- 🔄 Reintentos automáticos de scripts fallidos
- 📊 Reportes consolidados maestros
- 🎛️ Control de timeouts y configuración global
- 📋 Resumen ejecutivo completo

**Uso:**
```bash
# Ejecución secuencial básica
./master-validation.sh

# Ejecución paralela
./master-validation.sh --parallel

# Con reintentos automáticos
./master-validation.sh --parallel --retry

# Con timeout personalizado
./master-validation.sh --timeout 600

# Modo silencioso
./master-validation.sh --quiet
```

## 🏗️ Estructura de Directorios

```
scripts/
├── validate-system.sh          # Validación completa del sistema
├── test-communication-flows.sh # Testing de comunicación
├── test-failure-scenarios.sh   # Testing de tolerancia a fallos
├── performance-benchmark.sh    # Benchmarks de rendimiento
├── generate-system-report.sh   # Generación de reportes
├── continuous-validation.sh    # Validación continua
├── master-validation.sh        # Orquestador maestro
├── config.env                  # Configuración global
├── logs/                       # Logs del sistema
│   ├── validation/            # Logs de validación
│   ├── communication/         # Logs de comunicación
│   ├── failure-scenarios/     # Logs de fallos
│   ├── performance/           # Logs de benchmarks
│   ├── continuous/            # Logs de monitoreo continuo
│   └── master-validation/     # Logs maestros
├── reports/                    # Reportes generados
│   ├── system/                # Reportes de validación
│   ├── communication/         # Reportes de comunicación
│   ├── failure-scenarios/     # Reportes de fallos
│   ├── performance/           # Reportes de benchmarks
│   ├── continuous/            # Reportes de monitoreo
│   └── master/                # Reportes maestros
├── monitoring/                 # Archivos de monitoreo
└── state.json                  # Estado del sistema
```

## ⚙️ Configuración

### Archivo de Configuración Global
Crea un archivo `config.env` en el directorio `scripts/` con las siguientes variables:

```bash
# Configuración de servicios
LP1_BANCO_URL="http://localhost:8080"
LP2_RENIEC_URL="http://localhost:8000"
RABBITMQ_URL="http://localhost:15672"
REDIS_URL="redis://localhost:6379"
POSTGRES_URL="postgresql://postgres:password@localhost:5432"
MYSQL_URL="mysql://root:password@localhost:3306"

# Configuración de timeouts
DEFAULT_TIMEOUT=30
BENCHMARK_DURATION=60
RECOVERY_TIMEOUT=300

# Configuración de umbrales
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
DISK_THRESHOLD=90

# Configuración de alertas
ALERT_EMAIL="admin@empresa.com"
SLACK_WEBHOOK="https://hooks.slack.com/..."
```

### Variables de Entorno Adicionales
```bash
# Para scripts que requieren autenticación
export RABBITMQ_USER="admin"
export RABBITMQ_PASS="admin"
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="password"
export MYSQL_USER="root"
export MYSQL_PASSWORD="password"

# Para herramientas específicas
export PATH="/usr/local/bin:$PATH"
```

## 🚀 Guía de Uso

### Ejecución Básica
```bash
# 1. Hacer los scripts ejecutables
chmod +x *.sh

# 2. Ejecutar validación completa
./master-validation.sh

# 3. Ver reportes generados
ls reports/
```

### Ejecución Individual de Scripts
```bash
# Validación básica del sistema
./validate-system.sh

# Testing de comunicación
./test-communication-flows.sh

# Benchmark de rendimiento
./performance-benchmark.sh

# Generar reporte
./generate-system-report.sh
```

### Configuración de Monitoreo Continuo
```bash
# Iniciar monitoreo en background
nohup ./continuous-validation.sh > monitoring.log 2>&1 &

# Verificar estado
./continuous-validation.sh --status

# Instalar cron job para validación diaria
echo "0 2 * * * /ruta/a/scripts/master-validation.sh" | crontab -
```

## 📊 Interpretación de Resultados

### Códigos de Salida
- **0**: Éxito - Todas las validaciones pasaron
- **1**: Fallo general - Algunos tests fallaron
- **2**: Error crítico - Sistema en estado crítico
- **124**: Timeout - Script excedió el tiempo límite

### Estados de Servicios
- 🟢 **ONLINE**: Servicio funcionando correctamente
- 🔴 **OFFLINE**: Servicio no disponible
- 🟡 **DEGRADED**: Servicio funcionando con limitaciones
- ⚫ **UNKNOWN**: Estado no determinado

### Niveles de Alerta
- 🔵 **INFO**: Información general
- 🟡 **WARNING**: Situación que requiere atención
- 🔴 **CRITICAL**: Problema crítico que requiere acción inmediata

## 🔧 Troubleshooting

### Problemas Comunes

#### Error: "Permission denied"
```bash
chmod +x *.sh
```

#### Error: "curl: command not found"
```bash
# Ubuntu/Debian
sudo apt-get install curl

# CentOS/RHEL
sudo yum install curl
```

#### Error: "jq: command not found"
```bash
# Ubuntu/Debian
sudo apt-get install jq

# CentOS/RHEL
sudo yum install jq
```

#### Scripts no encuentran servicios
1. Verificar que los servicios estén corriendo
2. Revisar configuración en `config.env`
3. Verificar conectividad de red

### Logs de Debug
```bash
# Ver logs en tiempo real
tail -f logs/validation/validate-system_*.log

# Verificar estado del monitoreo
./continuous-validation.sh --status

# Revisar errores en scripts específicos
grep -i "error" logs/*/*.log
```

## 📈 Métricas y KPIs

### Métricas de Validación
- **Tasa de Éxito**: % de tests que pasaron
- **Tiempo de Ejecución**: Duración total de validación
- **Cobertura**: % de componentes validados
- **Errores**: Número de errores detectados

### Métricas de Rendimiento
- **Latencia**: Tiempo de respuesta promedio
- **Throughput**: Requests por segundo
- **Percentiles**: P50, P95, P99 de latencia
- **Disponibilidad**: % de tiempo que el servicio está disponible

### Métricas de Recuperación
- **MTTD**: Mean Time To Detect (tiempo medio de detección)
- **MTTR**: Mean Time To Recover (tiempo medio de recuperación)
- **Disponibilidad**: 99.9% = ~43 minutos de downtime/mes
- **Recovery Rate**: % de recuperaciones exitosas

## 🔒 Seguridad

### Permisos
- Los scripts requieren permisos de ejecución
- Algunos tests pueden requerir permisos de root (iptables, docker)
- Verificar que los logs tengan permisos de escritura

### Datos Sensibles
- No incluir passwords en scripts
- Usar variables de entorno para datos sensibles
- Configurar .gitignore para archivos de configuración

### Logs
- Los logs pueden contener información sensible
- Configurar rotación automática de logs
- Establecer políticas de retención apropiadas

## 🚀 Mejores Prácticas

### Scheduling Regular
```bash
# Validación diaria completa
0 2 * * * /ruta/a/scripts/master-validation.sh

# Validación de comunicación cada hora
0 * * * * /ruta/a/scripts/test-communication-flows.sh

# Benchmarks semanales
0 3 * * 0 /ruta/a/scripts/performance-benchmark.sh
```

### Alertas y Notificaciones
1. Configurar webhooks para Slack/Discord
2. Integrar con sistemas de monitoreo (Prometheus, Grafana)
3. Configurar alertas por email para eventos críticos
4. Usar herramientas de incident management (PagerDuty, OpsGenie)

### Mantenimiento
1. Revisar y limpiar logs regularmente
2. Actualizar scripts con nuevas funcionalidades
3. Monitorear el rendimiento de los scripts mismos
4. Documentar nuevos casos de uso y configuraciones

## 📚 Documentación Adicional

- **API Documentation**: `docs/api-documentation.md`
- **Architecture Diagram**: `docs/architecture_diagram.mmd`
- **Testing Documentation**: `docs/testing-documentation.md`
- **Deployment Guide**: `docs/deployment-guide.md`

## 🤝 Contribución

Para contribuir al sistema de validación:

1. Seguir las convenciones de nomenclatura existentes
2. Incluir logging detallado en nuevos scripts
3. Generar reportes HTML con el mismo formato
4. Documentar nuevas funcionalidades
5. Incluir tests unitarios para funciones críticas

## 📞 Soporte

Para soporte técnico o reportar problemas:
- Revisar logs en `logs/`
- Consultar troubleshooting section
- Verificar configuración de servicios
- Contactar al equipo de DevOps

---

**Versión**: 1.0  
**Última actualización**: $(date '+%Y-%m-%d')  
**Mantenido por**: Equipo de DevOps