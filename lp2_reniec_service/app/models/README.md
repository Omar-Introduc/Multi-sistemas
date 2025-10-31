# Modelos de Datos - Servicio RENIEC

Este directorio contiene los modelos de datos SQLAlchemy para el servicio RENIEC, incluyendo validaciones Pydantic y relaciones entre entidades.

## Estructura de Modelos

### 1. Ciudadano

Representa a un ciudadano del sistema con toda su información personal.

**Campos:**
- `id` (Integer, Primary Key): ID único autoincremental
- `dni` (String(8), Unique): Documento Nacional de Identidad
- `nombres` (String(100)): Nombres del ciudadano
- `apellidos` (String(100)): Apellidos del ciudadano
- `fecha_nacimiento` (Date): Fecha de nacimiento
- `estado_civil` (String(50)): Estado civil
- `direccion` (String(255)): Dirección completa
- `telefono` (String(15)): Número de teléfono
- `email` (String(255), Unique): Correo electrónico
- `estado` (Boolean): Estado del registro (activo/inactivo)
- `fecha_registro` (DateTime): Fecha de registro
- `fecha_actualizacion` (DateTime): Fecha de última actualización

**Índices:**
- `idx_ciudadano_dni`: Índice único en DNI
- `idx_ciudadano_email`: Índice en email
- `idx_ciudadano_estado`: Índice en estado

**Validaciones Pydantic:**
- DNI debe ser numérico de 8 dígitos
- Teléfono debe ser numérico
- Fecha de nacimiento debe ser en el pasado
- Email debe ser un formato válido

**Relaciones:**
- `sesiones`: Relación uno-a-muchos con `ReniecSession`

### 2. ReniecSession

Representa una sesión de acceso al sistema RENIEC.

**Campos:**
- `id` (Integer, Primary Key): ID único autoincremental
- `session_id` (String(255), Unique): ID único de la sesión
- `dni` (String(8)): DNI del ciudadano
- `timestamp` (DateTime): Timestamp de la sesión
- `estado` (Boolean): Estado de la sesión
- `ip_address` (String(45)): Dirección IP (IPv4 o IPv6)
- `user_agent` (Text): User agent del navegador
- `ciudadano_id` (Integer, Foreign Key): ID del ciudadano

**Índices:**
- `idx_reniec_session_id`: Índice único en session_id
- `idx_reniec_session_dni`: Índice en DNI
- `idx_reniec_session_timestamp`: Índice en timestamp
- `idx_reniec_session_estado`: Índice en estado
- `idx_reniec_session_ip`: Índice en IP

**Validaciones Pydantic:**
- DNI debe ser numérico de 8 dígitos
- session_id debe contener solo caracteres alfanuméricos, guiones y guiones bajos
- IP debe ser una dirección IP válida

**Relaciones:**
- `ciudadano`: Relación muchos-a-uno con `Ciudadano`

### 3. Validador

Representa un validador del sistema con su versión y estado.

**Campos:**
- `id` (Integer, Primary Key): ID único autoincremental
- `nombre` (String(100)): Nombre del validador
- `version` (String(50)): Versión del validador
- `estado` (Boolean): Estado del validador
- `fecha_activacion` (DateTime): Fecha de activación

**Índices:**
- `idx_validador_nombre`: Índice en nombre
- `idx_validador_version`: Índice en versión
- `idx_validador_estado`: índice en estado
- `idx_validador_nombre_version`: Índice único compuesto en nombre y versión

**Validaciones Pydantic:**
- Nombre debe contener solo caracteres válidos (letras, números, espacios, guiones, puntos)
- Versión debe seguir formato semántico (ej: 1.0.0, v1.0.0, 1.2.3-alpha)
- Estado debe ser 'activo', 'inactivo' o 'mantenimiento'

**Métodos:**
- `activate()`: Activa el validador
- `deactivate()`: Desactiva el validador
- `is_active()`: Verifica si está activo

## Uso

### Importar modelos

```python
from app.models import Ciudadano, ReniecSession, Validador, Base
```

### Crear instancia de Ciudadano

```python
from datetime import date

ciudadano = Ciudadano(
    dni="12345678",
    nombres="Juan Carlos",
    apellidos="Pérez González",
    fecha_nacimiento=date(1990, 5, 15),
    estado_civil="soltero",
    direccion="Av. Principal 123, Lima, Perú",
    telefono="987654321",
    email="juan.perez@email.com",
    estado=True
)
```

### Crear instancia de ReniecSession

```python
from datetime import datetime

sesion = ReniecSession(
    session_id="sess_abc123def456",
    dni="12345678",
    timestamp=datetime.now(),
    estado=True,
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0...",
    ciudadano_id=1
)
```

### Crear instancia de Validador

```python
validador = Validador(
    nombre="ValidadorDNIv2",
    version="2.1.0",
    estado=True
)
validador.activate()
```

## Configuración de Base de Datos

Los modelos están configurados para MySQL con las siguientes opciones:
- Engine: InnoDB
- Charset: utf8mb4
- Soporte para comentarios en campos

## Validaciones

Cada modelo incluye:
1. **Modelo SQLAlchemy**: Para mapeo a base de datos
2. **Modelo Pydantic**: Para validaciones de entrada
3. **Validadores**: Con reglas específicas por campo
4. **Métodos auxiliares**: Para operaciones comunes

## Ejemplo de Uso Completo

Ver el archivo `ejemplo_uso.py` para ver ejemplos completos de uso de todos los modelos, incluyendo validaciones y relaciones.

## Notas Importantes

1. **Relaciones**: Las relaciones entre modelos se configuran automáticamente
2. **Índices**: Se crean índices para optimizar consultas frecuentes
3. **Validaciones**: Las validaciones se ejecutan antes de guardar en BD
4. **Fechas**: Se manejan automáticamente fecha_registro y fecha_actualizacion
5. **Escalabilidad**: Los modelos están diseñados para escalar en producción
