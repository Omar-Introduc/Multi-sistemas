# Listeners RabbitMQ - lp2_reniec_service

Este módulo contiene los listeners RabbitMQ para la comunicación entre el banco y el servicio RENIEC.

## Listeners Disponibles

### 1. BancoValidationListener
Escucha solicitudes de validación desde el banco y procesa validaciones de identidad contra RENIEC.

**Funcionalidades:**
- Escucha en la cola `banco.validation.queue`
- Procesa validaciones de documentos de identidad
- Envía respuestas con datos de RENIEC
- Manejo de reintentos y acknowledgment de mensajes
- Configuración QoS para manejo eficiente de carga

### 2. ReniecConfigListener
Recibe configuraciones dinámicas del sistema y las aplica en tiempo real.

**Funcionalidades:**
- Escucha en la cola `reniec.config.queue`
- Actualiza configuraciones del sistema
- Persiste configuraciones en archivos YAML
- Aplica cambios de configuración en tiempo real
- Thread-safe para actualizaciones concurrentes

### 3. HeartbeatListener
Maneja heartbeats del banco y monitoreo de conectividad.

**Funcionalidades:**
- Escucha en la cola `bank.heartbeat.queue`
- Responde a health checks del banco
- Envía heartbeats proactivos del servicio
- Monitoreo de estado del sistema (CPU, memoria, disco)
- Múltiples threads para monitoreo continuo

## Configuración de QoS

Todos los listeners implementan `@pika.channel.set_qos(prefetch_count=1)` para:
- Manejo eficiente de mensajes
- Balanceo de carga entre consumers
- Prevención de sobrecarga del sistema

## Manejo de Acknowledgments

- **Acknowledgment automático**: Solo después del procesamiento exitoso
- **Reject con requeue**: En errores recuperables
- **Reject sin requeue**: En errores críticos o max reintentos

## Sistema de Reintentos

- **Máximo 3 reintentos** por defecto
- **Delay de 5 segundos** entre reintentos
- **Dead Letter Exchange** para mensajes fallidos
- **Logging detallado** de cada intento

## Logging Detallado

Todos los listeners incluyen logging detallado con:
- **Niveles configurables** (DEBUG, INFO, WARNING, ERROR)
- **Correlation IDs** para trazabilidad
- **Timestamps** en todos los eventos
- **Estadísticas** de procesamiento
- **Métricas de salud** del sistema

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

### BancoValidationListener

```python
from app.listeners import BancoValidationListener

listener = BancoValidationListener(
    rabbitmq_host='localhost',
    queue_name='banco.validation.queue'
)

listener.start_consuming()
```

### ReniecConfigListener

```python
from app.listeners import ReniecConfigListener

listener = ReniecConfigListener(
    rabbitmq_host='localhost',
    queue_name='reniec.config.queue'
)

# Obtener configuración actual
config = listener.get_current_config()

# Solicitar actualización
success = listener.request_config_update(new_config_data)
```

### HeartbeatListener

```python
from app.listeners import HeartbeatListener

listener = HeartbeatListener(
    rabbitmq_host='localhost',
    queue_name='bank.heartbeat.queue'
)

# Obtener estado del servicio
status = listener.get_service_status()

listener.start_consuming()
```

## Estructura de Exchanges y Queues

### BancoValidationListener
- **Exchange**: `banco.validations` (topic)
- **Queue**: `banco.validation.queue`
- **Routing Keys**:
  - `banco.validation.request` (entrada)
  - `banco.validation.response` (salida)

### ReniecConfigListener
- **Exchange**: `reniec.config` (topic)
- **Queue**: `reniec.config.queue`
- **Routing Keys**:
  - `reniec.config.update` (entrada)
  - `reniec.config.response` (salida)

### HeartbeatListener
- **Exchange**: `bank.heartbeat` (topic)
- **Queue**: `bank.heartbeat.queue`
- **Routing Keys**:
  - `bank.heartbeat.request` (entrada)
  - `service.status.response` (salida)
  - `service.heartbeat.notification` (notificaciones)

## Características de Escalabilidad

- **Prefetch Count**: Configurable para balancear carga
- **Dead Letter Exchange**: Para manejo de mensajes fallidos
- **Message TTL**: Tiempo de vida para evitar colas congestionadas
- **Conexiones persistentes**: Heartbeat de 600s para mantener conexión
- **Threading**: Múltiples threads para monitoreo y procesamiento

## Monitoreo

Cada listener expone estadísticas:
- Mensajes recibidos/procesados/fallidos
- Tasa de éxito
- Tiempo de actividad
- Estado de conectividad
- Métricas del sistema (CPU, memoria, disco)