# Scripts Avanzados de Inicialización - Sistema Shibasito

Este directorio contiene scripts avanzados de inicialización para el Sistema Distribuido Shibasito, con logging detallado, manejo de errores y output colorido.

## 📋 Scripts Disponibles

### 1. `master-init.sh` - Script Maestro
**Script principal que coordina todo el proceso de inicialización**

```bash
# Ejecutar inicialización completa
bash master-init.sh

# Hacer ejecutable si es necesario
chmod +x master-init.sh
```

**Características:**
- Ejecuta todos los scripts en el orden correcto
- Maneja errores y permite recuperación
- Proporciona resumen final con enlaces a servicios
- Logging completo del proceso

### 2. `setup-environments.sh` - Configuración de Variables de Entorno
**Configura todas las variables de entorno necesarias para el sistema**

```bash
# Configuración interactiva
bash setup-environments.sh interactive

# Configuración con valores por defecto
bash setup-environments.sh default

# Configuración de producción con contraseñas seguras
bash setup-environments.sh production
```

**Características:**
- Modo interactivo con prompts para el usuario
- Modo por defecto para desarrollo rápido
- Modo de producción con contraseñas generadas
- Validación de configuración
- Archivo `.env` generado automáticamente
- Template disponible en `.env.template`

**Variables configuradas:**
- PostgreSQL (BD1) - Servicio Banco
- MySQL (BD2) - Servicio RENIEC
- RabbitMQ
- Redis
- Servicios de aplicación (Banco LP1, RENIEC LP2)
- Monitoreo (Prometheus, Grafana)

### 3. `wait-for-services.sh` - Espera de Servicios
**Espera a que todos los servicios estén disponibles y funcionando**

```bash
# Esperar a que todos los servicios estén listos
bash wait-for-services.sh
```

**Características:**
- Verifica estado de contenedores Docker
- Comprueba conectividad de bases de datos
- Valida APIs de servicios
- Timeouts configurables por servicio
- Progress bar visual
- Verificación de health checks
- Detección de servicios faltantes

**Servicios monitoreados:**
- PostgreSQL (bd1_postgresql)
- MySQL (bd2_mysql)
- RabbitMQ
- Redis
- Servicio Banco LP1
- Servicio RENIEC LP2
- Prometheus
- Grafana

### 4. `init-all-databases.sh` - Inicialización de Bases de Datos
**Script maestro para inicializar todas las bases de datos**

```bash
# Inicializar todas las bases de datos
bash init-all-databases.sh
```

**Características:**
- Inicialización de PostgreSQL (BD1)
- Inicialización de MySQL (BD2)
- Aplicación de esquemas de base de datos
- Creación de índices
- Inserción de datos de prueba
- Verificación de integridad
- Manejo de errores con rollback

**Archivos SQL utilizados:**
- `schema_lp1_banco.sql` - Esquema PostgreSQL
- `schema_lp2_reniec.sql` - Esquema MySQL
- `indexes_lp1.sql` - Índices PostgreSQL
- `indexes_lp2.sql` - Índices MySQL
- `seed_data_lp1.sql` - Datos de prueba PostgreSQL
- `seed_data_lp2.sql` - Datos de prueba MySQL
- `verification_lp1.sql` - Scripts de verificación

### 5. `validate-setup.sh` - Validación Completa del Setup
**Valida que toda la configuración esté correcta y funcionando**

```bash
# Validar configuración completa
bash validate-setup.sh
```

**Características:**
- Tests de infraestructura (Docker, Docker Compose)
- Tests de contenedores (estado, health checks)
- Tests de red (configuración de redes)
- Tests de bases de datos (conectividad)
- Tests de aplicaciones (APIs)
- Tests de mensajería (RabbitMQ)
- Tests de caché (Redis)
- Tests de monitoreo (Prometheus, Grafana)
- Tests de archivos de configuración
- Reporte HTML generado automáticamente

**Categorías de pruebas:**
- Infrastructure
- Containers
- Network
- Database
- Application
- Messaging
- Cache
- Monitoring
- Configuration
- Reporting

## 🚀 Uso Recomendado

### Opción 1: Ejecución Completa Automática
```bash
cd init-scripts
bash master-init.sh
```

### Opción 2: Ejecución Paso a Paso
```bash
cd init-scripts

# 1. Configurar entorno
bash setup-environments.sh interactive

# 2. Verificar servicios (requiere que los contenedores estén ejecutándose)
bash wait-for-services.sh

# 3. Inicializar bases de datos
bash init-all-databases.sh

# 4. Validar todo
bash validate-setup.sh
```

## 📁 Estructura de Archivos

```
init-scripts/
├── master-init.sh              # Script maestro
├── setup-environments.sh       # Configuración de entorno
├── wait-for-services.sh        # Espera de servicios
├── init-all-databases.sh       # Inicialización de BD
├── validate-setup.sh           # Validación completa
├── README.md                   # Esta documentación
└── logs/                       # Directorio de logs
    ├── master_init_*.log
    ├── environment_setup_*.log
    ├── wait_for_services_*.log
    ├── database_init_*.log
    ├── validate_setup_*.log
    └── validation_report_*.html
```

## 📊 Logging y Reportes

### Logs Detallados
Cada script genera logs detallados en la carpeta `logs/` con:
- Timestamps precisos
- Niveles de log (INFO, SUCCESS, WARNING, ERROR)
- Colores en output en tiempo real
- Archivos de log individuales

### Reporte HTML
El script de validación genera un reporte HTML completo con:
- Resumen ejecutivo con estadísticas
- Detalles de cada prueba realizada
- Clasificación por categorías
- Diseño responsivo y profesional

## 🎨 Características del Output

### Colores Utilizados
- 🔵 **Cyan**: Información general
- 🟢 **Verde**: Éxito y confirmaciones
- 🟡 **Amarillo**: Advertencias
- 🔴 **Rojo**: Errores críticos
- 🟣 **Magenta**: Pasos del proceso
- 🔵 **Azul**: Headers y títulos

### Formato de Mensajes
```
[TIPO] TIMESTAMP - Mensaje descriptivo
```

Ejemplos:
- `[INFO] 2025-10-30 10:55:20 - Configurando PostgreSQL`
- `[SUCCESS] 2025-10-30 10:55:25 - PostgreSQL inicializado correctamente`
- `[ERROR] 2025-10-30 10:55:30 - Error al conectar con MySQL`

## ⚠️ Requisitos Previos

### Software Requerido
- Docker Engine 20.10+
- Docker Compose 2.0+
- Bash 4.0+
- Curl (para health checks)
- OpenSSL (para generación de contraseñas)

### Servicios Docker
Los siguientes contenedores deben estar definidos en docker-compose:
- `bd1_postgresql`
- `bd2_mysql`
- `rabbitmq`
- `redis`
- `servicio-banco-lp1`
- `servicio-reniec-lp2`
- `prometheus`
- `grafana`

## 🔧 Configuración Avanzada

### Personalización de Timeouts
Los timeouts se pueden ajustar modificando el array `SERVICE_TIMEOUTS` en `wait-for-services.sh`:

```bash
declare -A SERVICE_TIMEOUTS
SERVICE_TIMEOUTS=(
    ["bd1_postgresql"]=90    # 90 segundos
    ["bd2_mysql"]=90
    ["rabbitmq"]=120
    # ... más servicios
)
```

### Variables de Entorno Personalizadas
Para agregar nuevas variables, edite el array en `setup-environments.sh`:

```bash
# Agregar nueva variable
NEW_VAR=$(prompt_user_input "Nueva variable" "valor_por_defecto")
```

### Nuevos Tests de Validación
Para agregar tests, edite `validate-setup.sh`:

```bash
test_nuevo_servicio() {
    local test_name="Nuevo Servicio"
    local category="Custom"
    local start_time=$(start_timer)
    
    # Lógica del test
    
    local duration=$(end_timer "$start_time")
    record_test "$test_name" "PASS" "Detalles" "$duration" "$category"
    print_test_result "$test_name" "PASS" "Detalles" "$duration"
}
```

## 🐛 Solución de Problemas

### Error: "Docker no está ejecutándose"
```bash
# Verificar estado de Docker
sudo systemctl status docker

# Iniciar Docker si es necesario
sudo systemctl start docker
```

### Error: "Contenedor no encontrado"
```bash
# Verificar contenedores ejecutándose
docker ps -a

# Revisar logs del contenedor
docker logs <nombre_contenedor>
```

### Error: "No se puede conectar a base de datos"
```bash
# Verificar credenciales en .env
cat .env

# Probar conexión manualmente
docker exec bd1_postgresql pg_isready -U banco_user -d banco_db
```

### Logs corruptos o incompletos
```bash
# Limpiar logs antiguos
find logs/ -name "*.log" -mtime +7 -delete

# Verificar permisos
ls -la logs/
```

## 📞 Soporte

Para reportar problemas o solicitar nuevas funcionalidades:

1. **Revise los logs** en la carpeta `logs/`
2. **Verifique los contenedores** con `docker ps`
3. **Ejecute validación completa** con `validate-setup.sh`
4. **Guarde el reporte HTML** generado

## 🔄 Actualizaciones

Este sistema de scripts está diseñado para ser:
- **Modular**: Cada script es independiente pero coordinable
- **Extensible**: Fácil de agregar nuevos servicios y tests
- **Configurable**: Variables ajustables para diferentes entornos
- **Robusto**: Manejo completo de errores y recovery

---

**Versión**: 1.0  
**Fecha**: 2025-10-30  
**Autor**: Sistema Shibasito DevOps Team