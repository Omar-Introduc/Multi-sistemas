# Configuración Completa de RabbitMQ

Este directorio contiene las configuraciones completas para el servidor RabbitMQ del sistema distribuido.

## Archivos de Configuración

### 1. `definitions.json`
**Propósito**: Define objetos de RabbitMQ (exchanges, queues, bindings, usuarios, vhosts, políticas)

**Contenido**:
- **Usuarios**: 
  - `admin`: Usuario administrador con permisos completos
  - `banco_user`: Usuario para servicio bancario
  - `reniec_user`: Usuario para servicio RENIEC
  - `monitor_user`: Usuario para monitoreo

- **Vhosts**:
  - `/`: Host virtual principal
  - `/banco`: Host especializado para servicios bancarios
  - `/reniec`: Host especializado para servicios RENIEC
  - `/monitoring`: Host para métricas y monitoreo

- **Exchanges**:
  - `banco.events`: Exchange para eventos del banco (topic)
  - `banco.audit`: Exchange para auditoría (fanout)
  - `reniec.queries`: Exchange para consultas RENIEC (topic)
  - Dead letter exchanges (DLX) para manejo de mensajes fallidos

- **Queues**:
  - `banco.transaction.queue`: Cola para transacciones bancarias
  - `banco.audit.queue`: Cola para auditoría
  - `reniec.lookup.queue`: Cola para búsquedas de DNI
  - Queues DLX para mensajes expirados

- **Bindings**:
  - Configuración de routing keys para topic exchanges
  - Bindings de DLX para dead letter routing

- **Políticas**:
  - HA (High Availability) para replicación de queues
  - Políticas de retención y expiración de mensajes

### 2. `rabbitmq.conf`
**Propósito**: Configuración principal de RabbitMQ

**Secciones principales**:
- **Configuraciones básicas**: usuarios, vhosts, permisos
- **Red y puertos**: AMQP, management, distribución
- **Memoria y disco**: límites y umbrales
- **Timeouts y performance**: heartbeats, timeouts de conexión
- **Seguridad**: autenticación, autorización
- **Clustering**: configuración para escalabilidad futura
- **Logging**: niveles y formatos de log
- **Monitoreo**: métricas y health checks
- **SSL**: configuración TLS (deshabilitado por defecto)

### 3. `advanced.config`
**Propósito**: Configuraciones avanzadas de Erlang y RabbitMQ

**Secciones principales**:
- **Memoria**: configuraciones detalladas de memoria y GC
- **Red**: opciones avanzadas de TCP, SSL, límites
- **Colas**: tipos, límites, configuraciones de lazy queues
- **Clustering**: peer discovery, nodos, cluster state
- **Logging**: SASL, rotación de logs, formatos
- **Monitoreo**: health checks, métricas, event exchange
- **Seguridad**: autenticación, heartbeat, frame size
- **Performance**: consumer settings, publisher confirms
- **Rate limiting**: flow control, consumer rate limiting
- **Erlang VM**: configuraciones de la máquina virtual

### 4. `rabbitmq-env.conf`
**Propósito**: Variables de entorno para RabbitMQ

**Variables principales**:
- **Servidor**: puertos, hostname, directorios
- **Memoria**: límites de memoria y disco
- **Clustering**: configuración de nodes
- **Red**: interfaces, timeouts
- **Seguridad**: usuarios, passwords, loopback
- **Logging**: niveles, rotación, formatos
- **Plugins**: configuraciones de plugins habilitados
- **Monitoreo**: health checks, métricas
- **SSL**: certificados y configuraciones TLS

## Uso de las Configuraciones

### En Docker Compose
```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    container_name: rabbitmq
    ports:
      - "5672:5672"    # AMQP
      - "15672:15672"  # Management UI
    volumes:
      - ./rabbitmq-config/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf:ro
      - ./rabbitmq-config/advanced.config:/etc/rabbitmq/advanced.config:ro
      - ./rabbitmq-config/rabbitmq-env.conf:/etc/rabbitmq/rabbitmq-env.conf:ro
      - ./rabbitmq-config/definitions.json:/etc/rabbitmq/definitions.json:ro
      - rabbitmq_data:/var/lib/rabbitmq
    environment:
      - RABBITMQ_CONFIG_FILE=/etc/rabbitmq/rabbitmq
    restart: unless-stopped
```

### Carga de Definiciones
Las definiciones se cargan automáticamente desde `definitions.json` mediante:
```bash
rabbitmqctl load_definitions /etc/rabbitmq/definitions.json
```

### Configuración de Variables de Entorno
```bash
source rabbitmq-env.conf
rabbitmq-server
```

## Servicios y Conexiones

### Servicio Banco
- **Vhost**: `/banco`
- **Usuario**: `banco_user`
- **Exchanges principales**: `banco.events`, `banco.audit`
- **Queues principales**: `banco.transaction.queue`, `banco.audit.queue`

### Servicio RENIEC
- **Vhost**: `/reniec`
- **Usuario**: `reniec_user`
- **Exchanges principales**: `reniec.queries`, `reniec.cache`
- **Queues principales**: `reniec.lookup.queue`, `reniec.validation.queue`

### Panel de Administración
- **URL**: http://localhost:15672
- **Usuario**: admin
- **Password**: admin123_secure_2024

## Características de Seguridad

1. **Usuario Guest Deshabilitado**: Solo usuarios autenticados pueden conectarse
2. **Usuarios Especializados**: Cada servicio tiene su propio usuario y permisos
3. **Vhosts Aislados**: Separación completa de servicios
4. **Políticas de Acceso**: Restricciones granulares por usuario y vhost
5. **Dead Letter Exchanges**: Manejo seguro de mensajes fallidos

## Características de Alta Disponibilidad

1. **Políticas HA**: Replicación automática de queues en todos los nodos
2. **Durabilidad**: Colas y exchanges configurados como durables
3. **Sincronización Automática**: Para nuevos nodos del cluster
4. **Dead Letter Routing**: Manejo robusto de mensajes expirados

## Monitoreo y Métricas

1. **Plugin de Management**: UI web para monitoreo
2. **Políticas de Retención**: Métricas de 1 día y 30 días
3. **Health Checks**: Monitoreo automático de salud
4. **Logs Estructurados**: Logging detallado de eventos

## Configuración de Producción

Para uso en producción, considerar:

1. **SSL/TLS**: Habilitar certificados SSL en `rabbitmq.conf`
2. **Clustering**: Configurar múltiples nodos para alta disponibilidad
3. **Políticas de Reinicio**: Configurar políticas de restart automático
4. **Backup**: Implementar estrategia de backup de configuraciones
5. **Monitoring**: Integrar con sistemas de monitoreo externos (Grafana, Prometheus)
6. **Auditoría**: Habilitar logging detallado para auditoría

## Comandos Útiles

```bash
# Verificar estado del cluster
rabbitmqctl cluster_status

# Ver queues
rabbitmqctl list_queues

# Ver exchanges
rabbitmqctl list_exchanges

# Ver bindings
rabbitmqctl list_bindings

# Ver conexiones
rabbitmqctl list_connections

# Ver usuarios
rabbitmqctl list_users

# Ver vhosts
rabbitmqctl list_vhosts

# Cargar definiciones
rabbitmqctl load_definitions /etc/rabbitmq/definitions.json

# Aplicar política HA
rabbitmqctl set_policy ha-all "^ha\." '{"ha-mode":"all","ha-sync-mode":"automatic"}'
```

## Troubleshooting

### Problemas de Memoria
- Ajustar `vm_memory_high_watermark` en `rabbitmq.conf`
- Verificar políticas de TTL en queues

### Problemas de Conexión
- Verificar puertos en `rabbitmq-env.conf`
- Validar credenciales en `definitions.json`
- Revisar logs en `/var/log/rabbitmq/`

### Problemas de Clustering
- Verificar `advanced.config` para configuración de nodes
- Validar cookies Erlang en `rabbitmq-env.conf`
- Comprobar resolución DNS entre nodos

---

**Versión**: 1.0  
**Fecha**: Octubre 2024  
**Entorno**: Sistema Distribuido - Servicios Banco y RENIEC