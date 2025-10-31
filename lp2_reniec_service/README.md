# LP2 RENIEC Service

Servicio FastAPI completo para la gestión de documentos de identidad del RENIEC (Registro Nacional de Identificación y Estado Civil del Perú).

## 🚀 Características

- **API RESTful** con FastAPI y Python 3.11
- **Base de datos MySQL** con SQLAlchemy ORM
- **RabbitMQ** para mensajería asíncrona
- **Redis** para caching y sesiones
- **Middleware CORS** configurado
- **Middleware de autenticación** y rate limiting
- **Logging avanzado** con Loguru
- **Validación de datos** con Pydantic
- **Testing** con Pytest
- **Arquitectura modular** y escalable

## 📁 Estructura del Proyecto

```
lp2_reniec_service/
├── main.py                    # Aplicación FastAPI principal
├── requirements.txt           # Dependencias Python
├── .env.example              # Variables de entorno de ejemplo
├── app/
│   ├── config/
│   │   ├── settings.py       # Configuración principal
│   │   └── database.py       # Configuración de BD
│   ├── models/
│   │   ├── reniec_models.py  # Modelos SQLAlchemy
│   │   └── schemas.py        # Esquemas Pydantic
│   ├── routers/
│   │   ├── health_check.py   # Endpoints de salud
│   │   ├── reniec_endpoints.py # Endpoints RENIEC
│   │   ├── document_management.py # Gestión de documentos
│   │   └── citizen_services.py # Servicios de ciudadanos
│   ├── services/
│   │   ├── reniec_service.py     # Servicio RENIEC
│   │   ├── ciudadano_service.py  # Gestión de ciudadanos
│   │   ├── documento_service.py  # Gestión de documentos
│   │   ├── rabbit_service.py     # Integración RabbitMQ
│   │   └── redis_service.py      # Integración Redis
│   ├── middleware/
│   │   ├── auth.py           # Middleware de autenticación
│   │   ├── logging.py        # Middleware de logging
│   │   └── rate_limiter.py   # Rate limiting
│   ├── listeners/
│   │   └── event_listener.py # Sistema de eventos
│   └── utils/
│       └── file_handler.py   # Manejo de archivos
└── tests/
    └── test_main.py          # Tests básicos
```

## 🛠️ Instalación

### Prerrequisitos

- Python 3.11+
- MySQL 8.0+
- RabbitMQ 3.8+
- Redis 6.0+

### Configuración

1. **Clonar repositorio**
```bash
cd lp2_reniec_service
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. **Configurar base de datos MySQL**
```sql
CREATE DATABASE reniec_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'reniec_user'@'localhost' IDENTIFIED BY 'password_seguro';
GRANT ALL PRIVILEGES ON reniec_db.* TO 'reniec_user'@'localhost';
FLUSH PRIVILEGES;
```

5. **Ejecutar la aplicación**
```bash
python main.py
```

La API estará disponible en: http://localhost:8000

## 📚 API Endpoints

### Health Check
- `GET /api/v1/health/` - Verificación básica de salud
- `GET /api/v1/health/detailed` - Health check detallado con dependencias
- `GET /api/v1/health/ready` - Readiness check para Kubernetes
- `GET /api/v1/health/live` - Liveness check para Kubernetes

### RENIEC Endpoints
- `GET /api/v1/reniec/consulta-dni/{dni}` - Consultar datos por DNI
- `POST /api/v1/reniec/verificar-dni` - Verificar autenticidad de DNI
- `GET /api/v1/reniec/documento/{numero}` - Consultar documento
- `GET /api/v1/reniec/estadisticas` - Estadísticas del servicio

### Gestión de Documentos
- `GET /api/v1/documents/` - Listar documentos (paginado)
- `POST /api/v1/documents/` - Crear nuevo documento
- `GET /api/v1/documents/{id}` - Obtener documento por ID
- `PUT /api/v1/documents/{id}` - Actualizar documento
- `DELETE /api/v1/documents/{id}` - Eliminar documento
- `POST /api/v1/documents/subir-archivo/{id}` - Subir archivo

### Servicios de Ciudadanos
- `GET /api/v1/citizens/` - Listar ciudadanos (paginado)
- `POST /api/v1/citizens/` - Crear nuevo ciudadano
- `GET /api/v1/citizens/{id}` - Obtener ciudadano por ID
- `GET /api/v1/citizens/documento/{dni}` - Buscar por DNI
- `PUT /api/v1/citizens/{id}` - Actualizar ciudadano
- `DELETE /api/v1/citizens/{id}` - Eliminar ciudadano
- `POST /api/v1/citizens/buscar` - Búsqueda avanzada
- `GET /api/v1/citizens/{id}/documentos` - Documentos del ciudadano
- `GET /api/v1/citizens/{id}/solicitudes` - Solicitudes del ciudadano

## 🏗️ Arquitectura

El proyecto sigue una arquitectura modular con separación clara de responsabilidades:

### Capas

1. **Routers** - Endpoints HTTP y validación de requests
2. **Services** - Lógica de negocio y integración con servicios externos
3. **Models** - Modelos de datos (SQLAlchemy + Pydantic)
4. **Middleware** - Cross-cutting concerns (auth, logging, rate limiting)
5. **Utils** - Utilidades compartidas

## Servicios

### 1. ReniecService

Servicio principal que maneja toda la lógica de negocio para validación de identidad.

#### Características:
- Validación de identidad contra base de datos RENIEC
- Consulta de datos ciudadanos
- Registro de sesiones de validación
- Validación simple de DNI
- Generación y envío de respuestas a bancos
- Cálculo de score de confianza
- Limpieza automática de sesiones expiradas

#### Métodos principales:
- `validarIdentidad(dni, nombres, apellido_paterno, apellido_materno, id_solicitud)`: Valida identidad completa
- `consultarCiudadano(numero_dni)`: Consulta datos de ciudadano
- `registrarSession(id_solicitud, numero_dni, estado)`: Registra sesión de validación
- `validarDni(numero_dni)`: Validación simple de DNI
- `generarRespuestaValidacion(respuesta, id_banco)`: Envía respuesta al banco

#### Ejemplo de uso:
```python
from services import ReniecService

# Crear servicio
reniec_service = ReniecService(database_service, rabbit_service, log_service)

# Validar identidad
resultado = reniec_service.validarIdentidad(
    numero_dni="12345678",
    nombres="JUAN CARLOS",
    apellido_paterno="PEREZ",
    apellido_materno="GARCIA",
    id_solicitud="SOL-2024-001"
)

print(f"Estado: {resultado.estado.value}")
print(f"Mensaje: {resultado.mensaje}")
```

### 2. DatabaseService

Servicio para manejo de base de datos MySQL con pool de conexiones.

#### Características:
- Pool de conexiones MySQL configurable
- Manejo automático de reconexión
- Soporte para transacciones
- Operaciones CRUD específicas para RENIEC
- Verificación de conexión
- Context manager para gestión de conexiones

#### Métodos principales:
- `inicializar()`: Inicializa el pool de conexiones
- `ejecutarQuery(query, parametros)`: Ejecuta INSERT/UPDATE/DELETE
- `ejecutarConsulta(query, parametros)`: Ejecuta SELECT múltiple
- `ejecutarConsultaUnica(query, parametros)`: Ejecuta SELECT único
- `ejecutarProcedimiento(nombre, parametros)`: Ejecuta procedimientos almacenados
- `obtenerCiudadano(numero_documento)`: Consulta ciudadano por DNI

#### Ejemplo de uso:
```python
from services import DatabaseService

# Crear servicio de base de datos
db_service = DatabaseService(
    log_service=log_service,
    host="localhost",
    database="reniec_db",
    username="usuario",
    password="contraseña"
)

# Inicializar
if db_service.inicializar():
    # Consultar ciudadano
    ciudadano = db_service.obtenerCiudadano("12345678")
    if ciudadano:
        print(f"Encontrado: {ciudadano['nombres']} {ciudadano['apellido_paterno']}")
```

### 3. RabbitMQService

Servicio para comunicación asíncrona con sistemas bancarios vía RabbitMQ.

#### Características:
- Conexión robusta con manejo de reconexión automática
- Configuración de exchanges y queues
- Envío de respuestas de validación
- Consumo de mensajes
- Manejo de errores de conectividad
- Logging detallado de operaciones

#### Métodos principales:
- `inicializar()`: Establece conexión con RabbitMQ
- `publicarMensaje(exchange, routing_key, mensaje)`: Publica mensaje
- `enviarRespuestaValidacion(id_banco, respuesta)`: Envía respuesta específica
- `consumirMensaje(queue, callback)`: Consume mensajes
- `verificarConexion()`: Verifica estado de conexión

#### Ejemplo de uso:
```python
from services import RabbitMQService

# Crear servicio de RabbitMQ
rabbit_service = RabbitMQService(
    log_service=log_service,
    host="localhost",
    username="guest",
    password="guest"
)

# Inicializar
if rabbit_service.inicializar():
    # Enviar respuesta al banco
    respuesta = {
        "id_solicitud": "SOL-2024-001",
        "estado": "exitoso",
        "datos_ciudadano": {...}
    }
    
    enviado = rabbit_service.enviarRespuestaValidacion("BANCO_001", respuesta)
```

### 4. LogService

Sistema completo de logging y auditoría.

#### Características:
- Logging en archivos con rotación automática
- Auditoría en base de datos
- Filtrado de datos sensibles
- Métricas del sistema
- Estadísticas y reportes
- Limpieza automática de logs antiguos

#### Métodos principales:
- `registrarEvento(tipo_evento, mensaje, datos)`: Registra evento de auditoría
- `registrarError(tipo_error, mensaje, contexto)`: Registra error
- `registrarMetrica(nombre, valor, unidad)`: Registra métrica
- `obtenerEventos(filtro)`: Consulta eventos de auditoría
- `obtenerErrores(filtro)`: Consulta errores registrados
- `obtenerEstadisticas(periodo)`: Obtiene estadísticas del sistema

#### Ejemplo de uso:
```python
from services import LogService

# Crear servicio de logging
log_service = LogService(
    database_service=db_service,
    log_level="INFO",
    log_dir="./logs"
)

# Registrar evento
evento_id = log_service.registrarEvento(
    tipo_evento="VALIDACION_INICIADA",
    mensaje="Inicio de validación de identidad",
    datos_adicionales={"dni": "12345678", "solicitud": "SOL-2024-001"}
)

# Registrar error
error_id = log_service.registrarError(
    tipo_error="ERROR_VALIDACION",
    mensaje="DNI no válido",
    contexto={"dni": "123", "motivo": "formato_invalido"}
)
```

## Configuración

### Configuración por Defecto

```python
DEFAULT_CONFIG = {
    "database": {
        "host": "localhost",
        "port": 3306,
        "database": "reniec_db",
        "username": "reniec_user",
        "password": "reniec_password",
        "pool_size": 10
    },
    "rabbitmq": {
        "host": "localhost",
        "port": 5672,
        "username": "guest",
        "password": "guest",
        "virtual_host": "/"
    },
    "logging": {
        "level": "INFO",
        "log_dir": "./logs",
        "max_log_size": 50 * 1024 * 1024,  # 50MB
        "backup_count": 10
    }
}
```

### Factory Function

Usar la función factory para crear todos los servicios:

```python
from services import crear_servicios

# Crear todos los servicios
reniec_service, db_service, rabbit_service, log_service = crear_servicios()

# Inicializar servicios
db_service.inicializar()
rabbit_service.inicializar()
log_service.database_service = db_service

# Usar los servicios
resultado = reniec_service.validarIdentidad(...)
```

## Base de Datos

### Esquema de Tablas

El sistema requiere las siguientes tablas en MySQL:

```sql
-- Tabla de ciudadanos
CREATE TABLE ciudadanos (
    numero_documento VARCHAR(8) PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    estado_civil VARCHAR(50),
    direccion TEXT,
    distrito VARCHAR(100),
    provincia VARCHAR(100),
    departamento VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    creado_en DATETIME,
    actualizado_en DATETIME,
    INDEX idx_nombres (nombres),
    INDEX idx_apellidos (apellido_paterno, apellido_materno)
);

-- Tabla de sesiones de validación
CREATE TABLE sesiones_validacion (
    id_solicitud VARCHAR(64) PRIMARY KEY,
    numero_dni VARCHAR(8) NOT NULL,
    fecha_validacion DATETIME NOT NULL,
    fecha_expiracion DATETIME NOT NULL,
    estado VARCHAR(20) NOT NULL,
    id_banco VARCHAR(50),
    intentos_validacion INT DEFAULT 0,
    creado_en DATETIME,
    INDEX idx_numero_dni (numero_dni),
    INDEX idx_estado (estado),
    INDEX idx_expiracion (fecha_expiracion)
);

-- Tabla de auditoría de eventos
CREATE TABLE auditoria_eventos (
    evento_id VARCHAR(64) PRIMARY KEY,
    tipo_evento VARCHAR(100) NOT NULL,
    timestamp DATETIME NOT NULL,
    usuario VARCHAR(100),
    ip_origen VARCHAR(45),
    datos_evento JSON,
    session_id VARCHAR(64),
    resultado VARCHAR(20),
    duracion_ms INT,
    hash_integridad VARCHAR(64),
    INDEX idx_tipo_evento (tipo_evento),
    INDEX idx_timestamp (timestamp),
    INDEX idx_usuario (usuario)
);

-- Tabla de auditoría de errores
CREATE TABLE auditoria_errores (
    error_id VARCHAR(64) PRIMARY KEY,
    tipo_error VARCHAR(100) NOT NULL,
    mensaje TEXT,
    stack_trace LONGTEXT,
    timestamp DATETIME NOT NULL,
    contexto JSON,
    severidad VARCHAR(20),
    resuelto BOOLEAN DEFAULT FALSE,
    INDEX idx_tipo_error (tipo_error),
    INDEX idx_timestamp (timestamp),
    INDEX idx_severidad (severidad)
);
```

## RabbitMQ

### Exchanges y Queues

El sistema configura automáticamente los siguientes exchanges y queues:

- **Exchanges:**
  - `validacion_exchange` (topic): Para mensajes de validación
  - `error_exchange` (fanout): Para mensajes de error
  - `audit_exchange` (topic): Para eventos de auditoría

- **Queues:**
  - `validacion_respuestas`: Respuestas de validación
  - `banco_respuestas`: Respuestas para bancos específicos
  - `errores_sistema`: Errores del sistema

### Routing Keys

- `validacion.respuesta.{banco_id}`: Respuestas a bancos específicos
- `banco.{banco_id}`: Mensajes para bancos
- `error.*`: Errores del sistema

## Logging

### Archivos de Log

El sistema genera automáticamente los siguientes archivos:

- `reniec_general.log`: Log general de la aplicación
- `reniec_errors.log`: Log específico de errores
- `reniec_audit.log`: Log de auditoría y eventos

### Características de Seguridad

- **Filtrado de datos sensibles**:自动amente filtra números de DNI, contraseñas, tokens
- **Hash de integridad**: Verificación de integridad para auditoría
- **Rotación de logs**: Manejo automático del tamaño de archivos
- **Logs encriptados**: Soporte para datos sensibles

## Ejemplos Completos

### Validación Completa

```python
#!/usr/bin/env python3

from services import crear_servicios
from datetime import datetime

def main():
    # Crear servicios
    reniec_service, db_service, rabbit_service, log_service = crear_servicios()
    
    # Inicializar servicios
    db_service.inicializar()
    rabbit_service.inicializar()
    log_service.database_service = db_service
    log_service.crear_tablas_auditoria()
    
    # Realizar validación
    resultado = reniec_service.validarIdentidad(
        numero_dni="12345678",
        nombres="JUAN CARLOS",
        apellido_paterno="PEREZ",
        apellido_materno="GARCIA",
        id_solicitud="SOL-2024-001"
    )
    
    # Procesar resultado
    if resultado.estado.value == "exitosa":
        print("Validación exitosa!")
        
        # Enviar respuesta al banco
        respuesta_banco = {
            "id_solicitud": resultado.id_validacion,
            "estado": "exitoso",
            "datos_ciudadano": {
                "numero_documento": resultado.datos_ciudadano.numero_documento,
                "nombres": resultado.datos_ciudadano.nombres,
                "apellido_paterno": resultado.datos_ciudadano.apellido_paterno,
                "apellido_materno": resultado.datos_ciudadano.apellido_materno
            },
            "score_confianza": resultado.score_confianza,
            "timestamp": datetime.now().isoformat()
        }
        
        rabbit_service.enviarRespuestaValidacion("BANCO_001", respuesta_banco)
    else:
        print(f"Validación fallida: {resultado.mensaje}")
    
    # Cerrar conexiones
    rabbit_service.cerrarConexion()
    db_service.cerrarPool()

if __name__ == "__main__":
    main()
```

## Monitoreo y Métricas

### Métricas Disponibles

- `validaciones_procesadas`: Número de validaciones procesadas
- `validaciones_exitosas`: Validaciones exitosas
- `validaciones_fallidas`: Validaciones fallidas
- `tiempo_consulta_promedio`: Tiempo promedio de consulta
- `conexiones_db_activas`: Conexiones activas a la base de datos
- `mensajes_rabbit_enviados`: Mensajes enviados por RabbitMQ

### Estadísticas

```python
# Obtener estadísticas del sistema
estadisticas = log_service.obtenerEstadisticas(periodo_horas=24)

print(f"Eventos totales: {estadisticas['eventos_total']}")
print(f"Errores totales: {estadisticas['errores_total']}")
print(f"Validaciones exitosas: {estadisticas['eventos_por_tipo'].get('VALIDACION_EXITOSA', 0)}")
```

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a MySQL**
   - Verificar que MySQL esté ejecutándose
   - Confirmar credenciales de acceso
   - Verificar firewall y puertos

2. **Error de conexión a RabbitMQ**
   - Verificar que RabbitMQ esté ejecutándose
   - Confirmar usuario y contraseña
   - Verificar virtual host

3. **Error de memoria**
   - Reducir tamaño del pool de conexiones
   - Ajustar configuraciones de logging
   - Limpiar logs antiguos

### Logs de Debug

```python
# Habilitar logging de debug
log_service = LogService(log_level="DEBUG")

# Verificar estado de conexiones
print("Estado base de datos:", db_service.verificarConexion())
print("Estado RabbitMQ:", rabbit_service.verificarConexion())
print("Estado pool:", db_service.obtenerEstadoPool())
```

## Requisitos

- Python 3.8+
- MySQL 5.7+
- RabbitMQ 3.8+
- Librerías Python:
  - mysql-connector-python
  - pika
  - typing-extensions

## Instalación

```bash
# Instalar dependencias
pip install mysql-connector-python pika

# Configurar base de datos
mysql -u root -p < database/setup.sql

# Ejecutar ejemplo
python app/services/ejemplo_uso.py
```

## Licencia

Sistema desarrollado para RENIEC - Registro Nacional de Identificación y Estado Civil del Perú.