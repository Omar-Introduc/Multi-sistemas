# Script de Ejecución - Servicio Banco LP1

## Descripción

El script `run.sh` es un script de bash completo para ejecutar, gestionar y monitorear la aplicación del Servicio Banco LP1. Incluye verificación de variables de entorno, configuración automática de JVM, health checks y logging detallado.

## Características

- ✅ **Verificación de Variables**: Valida todas las variables de entorno requeridas
- ✅ **Configuración JVM**: Argumentos optimizados para servidor de banco
- ✅ **Health Check**: Verificación automática del estado de la aplicación
- ✅ **Logging**: Logs detallados con timestamps y colores
- ✅ **Gestión de Procesos**: Control completo del ciclo de vida de la aplicación
- ✅ **Modo DEBUG**: Soporte para debugging remoto
- ✅ **Variables Configurables**: Personalización completa via variables de entorno

## Comandos Disponibles

```bash
./run.sh start    # Inicia la aplicación
./run.sh stop     # Detiene la aplicación
./run.sh restart  # Reinicia la aplicación
./run.sh status   # Muestra el estado actual
./run.sh logs     # Muestra los logs en tiempo real
./run.sh health   # Ejecuta health check manual
./run.sh help     # Muestra la ayuda
```

## Variables de Entorno Requeridas

Antes de ejecutar la aplicación, debe configurar las siguientes variables:

```bash
# Base de datos PostgreSQL
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=banco_db
export DB_USER=banco_user
export DB_PASSWORD=mi_password

# Seguridad JWT
export JWT_SECRET=mi_jwt_secret_super_largo_y_seguro
```

## Variables Opcionales

```bash
# Configuración del servidor
export PORT=8080                                    # Puerto del servidor
export JAR_FILE=/path/to/lp1-servicio-banco.jar    # Ruta personalizada del JAR
export LOG_LEVEL=INFO                               # Nivel de logging

# Perfiles de Spring
export SPRING_PROFILES_ACTIVE=prod                  # dev, prod, test

# Configuración de debug (automática si SPRING_PROFILES_ACTIVE contiene 'dev')
export DEBUG_PORT=5005                              # Puerto para debug remoto
```

## Ejemplo de Uso

### 1. Configurar variables de entorno

```bash
# Opción 1: Cargar desde archivo .env
source .env

# Opción 2: Exportar manualmente
export DB_HOST=localhost
export DB_PORT=5432
# ... etc

# Opción 3: Exportar todas en una línea
export DB_HOST=localhost DB_PORT=5432 DB_NAME=banco_db DB_USER=banco_user DB_PASSWORD=password JWT_SECRET=secret
```

### 2. Iniciar la aplicación

```bash
./run.sh start
```

### 3. Verificar estado

```bash
./run.sh status
```

### 4. Ver logs

```bash
./run.sh logs
```

### 5. Health check manual

```bash
./run.sh health
```

## Configuración de JVM

El script configura automáticamente los siguientes argumentos JVM:

### Argumentos Base
- `-Xms512m`: Memoria inicial
- `-Xmx2048m`: Memoria máxima
- `-XX:+UseG1GC`: Garbage Collector G1
- `-XX:MaxGCPauseMillis=200`: Tiempo máximo de pausa GC
- `-XX:+UseStringDeduplication`: Deduplicación de strings
- `-Djava.awt.headless=true`: Modo headless
- `-Dfile.encoding=UTF-8`: Codificación UTF-8
- `-Duser.timezone=UTC`: Zona horaria UTC

### Argumentos de Logging
- `-Dlogging.level.root=${LOG_LEVEL:-INFO}`: Nivel de logging
- `-Dlogging.pattern.console`: Patrón de formato de logs

### Argumentos de Aplicación
- `-Dserver.port=${PORT}`: Puerto del servidor
- Configuración de datasource automática
- Configuración de aplicación (nombre, versión)

### Modo Debug
Si `SPRING_PROFILES_ACTIVE` contiene "dev", se agregan automáticamente:
- `-Xdebug`
- `-Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=5005`

## Health Check

El script incluye un sistema de health check que:

1. **Verifica el endpoint**: `http://localhost:${PORT}/actuator/health`
2. **Reintentos**: Hasta 30 intentos con espera progresiva
3. **Timeout**: Tiempo límite de 60 segundos
4. **Logging**: Información detallada del proceso

### Health Check Automático
Se ejecuta automáticamente después del inicio para confirmar que la aplicación está funcionando correctamente.

### Health Check Manual
```bash
./run.sh health
```

## Sistema de Logging

### Logs de Startup
- **Ubicación**: `logs/startup.log`
- **Rotación**: Manual (archivo único)
- **Formato**: Timestamp + nivel + mensaje

### Logging en Tiempo Real
```bash
tail -f logs/startup.log
./run.sh logs
```

### Niveles de Log Disponibles
- `TRACE`: Información muy detallada
- `DEBUG`: Información de debugging
- `INFO`: Información general (default)
- `WARN`: Advertencias
- `ERROR`: Errores

## Gestión de Procesos

### Archivo PID
- **Ubicación**: `lp1-servicio-banco.pid`
- **Uso**: Control de procesos y verificación de estado

### Comandos de Gestión
- **Inicio**: Verifica si ya está ejecutándose
- **Detención**: Envía SIGTERM, espera, luego SIGKILL si es necesario
- **Reinicio**: Combinación de stop + start con pausa

### Verificación de Estado
```bash
./run.sh status
```

Muestra:
- Estado del proceso (ejecutándose/no ejecutándose)
- PID del proceso
- Uso de CPU y memoria
- Estado del health check

## Estructura de Directorios

```
lp1-servicio-banco/
├── run.sh                    # Script principal
├── .env.example             # Ejemplo de variables de entorno
├── README-run.sh            # Este archivo
├── target/                  # Archivos JAR compilados
│   └── lp1-servicio-banco-*.jar
├── logs/                    # Logs de la aplicación
│   └── startup.log
└── lp1-servicio-banco.pid   # Archivo PID (generado)
```

## Resolución de Problemas

### Error: Variables de entorno faltantes
```bash
error: Variables de entorno requeridas faltantes:
  - DB_HOST
  - DB_PASSWORD
```
**Solución**: Configure todas las variables requeridas antes de ejecutar.

### Error: No se encontró archivo JAR
```bash
error: No se encontrado archivo JAR
```
**Solución**: 
1. Compile la aplicación: `mvn clean package`
2. O configure `JAR_FILE` con la ruta correcta

### Health check falla
```bash
warn: Health check: FAILED o no disponible
```
**Solución**:
1. Verifique que el puerto esté disponible
2. Revise los logs: `tail -f logs/startup.log`
3. Verifique la configuración de la base de datos

### La aplicación no inicia
```bash
error: La aplicación falló al iniciar
```
**Solución**:
1. Revise los logs: `tail -f logs/startup.log`
2. Verifique la configuración de la base de datos
3. Confirme que Java está instalado: `java -version`

## Variables de Entorno - Configuración Detallada

### Base de Datos
| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DB_HOST` | Host de PostgreSQL | `localhost`, `postgres-db` |
| `DB_PORT` | Puerto de PostgreSQL | `5432` |
| `DB_NAME` | Nombre de la base de datos | `banco_db` |
| `DB_USER` | Usuario de la base de datos | `banco_user` |
| `DB_PASSWORD` | Password del usuario | `password123` |

### Seguridad
| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `JWT_SECRET` | Secreto para tokens JWT | `mi_secret_muy_largo_y_aleatorio` |

### Servidor
| Variable | Descripción | Default | Ejemplo |
|----------|-------------|---------|---------|
| `PORT` | Puerto del servidor | `8080` | `8080`, `3000` |
| `LOG_LEVEL` | Nivel de logging | `INFO` | `DEBUG`, `WARN` |
| `SPRING_PROFILES_ACTIVE` | Perfiles de Spring | - | `dev`, `prod` |

## Personalización

### Argumentos JVM Personalizados
Para agregar argumentos JVM personalizados, modifique la función `setup_jvm_args()` en el script:

```bash
# Agregar después de la línea 158
JVM_ARGS+=(
    "-Dmi.propiedad.personalizada=valor"
    "-Xmx4096m"  # Aumentar memoria máxima
)
```

### Health Check Personalizado
Para cambiar el endpoint de health check, modifique la variable `url` en la función `health_check()`:

```bash
local url="http://localhost:${PORT}/mi/health/endpoint"
```

## Integración con Docker

### Dockerfile Example
```dockerfile
FROM openjdk:17-jre-slim

COPY target/lp1-servicio-banco-*.jar app.jar
COPY run.sh .
COPY .env.example .

# Hacer el script ejecutable
RUN chmod +x run.sh

# Exponer puerto
EXPOSE 8080

# Comando por defecto
CMD ["./run.sh", "start"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  banco-app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=banco_db
      - DB_USER=banco_user
      - DB_PASSWORD=password
      - JWT_SECRET=mi_secret
    depends_on:
      - postgres
    restart: unless-stopped
```

## Changelog

### Versión 1.0.0
- ✅ Script inicial con todas las funcionalidades básicas
- ✅ Verificación de variables de entorno
- ✅ Health check automático
- ✅ Gestión completa de procesos
- ✅ Logging detallado
- ✅ Soporte para modo debug
- ✅ Documentación completa

## Soporte

Para reportar problemas o solicitar funcionalidades:
1. Revise la sección "Resolución de Problemas"
2. Verifique los logs en `logs/startup.log`
3. Use `./run.sh status` para diagnosticar el estado

---

**Nota**: Este script está diseñado específicamente para el Servicio Banco LP1. Asegúrese de cumplir con todos los requisitos antes de ejecutar la aplicación.
