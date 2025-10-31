# Routers FastAPI - Servicio RENIEC

## Descripción

Esta documentación describe los routers REST implementados para el servicio RENIEC utilizando FastAPI. Los routers proporcionan endpoints para validación de DNI, consulta de ciudadanos y administración del sistema.

## Estructura de Routers

### 📁 `app/routers/`

- `reniec_router.py` - Endpoints públicos para validación y consulta RENIEC
- `admin_router.py` - Endpoints de administración del sistema

---

## 🔧 reniec_router.py

### Endpoints Públicos

#### `GET /api/reniec/health`
**Health Check del servicio**

```http
GET /api/reniec/health
```

**Respuesta:**
```json
{
  "status": "OK",
  "timestamp": "2025-10-30T09:14:40",
  "version": "1.0.0",
  "servicios": {
    "base_datos": "CONECTADO",
    "servidor": "OPERATIVO",
    "autenticacion": "ACTIVO"
  }
}
```

#### `GET /api/reniec/validar/{dni}`
**Validar un DNI específico**

```http
GET /api/reniec/validar/12345678
```

**Parámetros:**
- `dni` (string): DNI de 8 dígitos a validar

**Respuesta:**
```json
{
  "dni": "12345678",
  "es_valido": true,
  "mensaje": "DNI válido",
  "timestamp": "2025-10-30T09:14:40",
  "ciudadano": {
    "dni": "12345678",
    "nombres": "Juan Carlos",
    "apellido_paterno": "García",
    "apellido_materno": "López",
    "telefono": "987654321",
    "direccion": "Av. Principal 123",
    "fecha_nacimiento": "1990-05-15",
    "estado": "ACTIVO"
  }
}
```

#### `POST /api/reniec/consultar`
**Consultar información completa de un ciudadano**

```http
POST /api/reniec/consultar
Content-Type: application/json

{
  "dni": "12345678"
}
```

**Respuesta:**
```json
{
  "dni": "12345678",
  "nombres": "Juan Carlos",
  "apellido_paterno": "García",
  "apellido_materno": "López",
  "telefono": "987654321",
  "direccion": "Av. Principal 123",
  "fecha_nacimiento": "1990-05-15",
  "estado": "ACTIVO"
}
```

#### `GET /api/reniec/ciudadanos`
**Listar ciudadanos registrados**

```http
GET /api/reniec/ciudadanos?limit=100&offset=0
```

**Parámetros de consulta:**
- `limit` (int, opcional): Número máximo de resultados (default: 100, max: 1000)
- `offset` (int, opcional): Número de registros a omitir (default: 0)

**Respuesta:**
```json
[
  {
    "dni": "12345678",
    "nombres": "Juan Carlos",
    "apellido_paterno": "García",
    "apellido_materno": "López",
    "telefono": "987654321",
    "direccion": "Av. Principal 123",
    "fecha_nacimiento": "1990-05-15",
    "estado": "ACTIVO"
  }
]
```

---

## 🔧 admin_router.py

### Endpoints de Administración

#### `GET /api/admin/sessions`
**Listar sesiones activas en el sistema**

```http
GET /api/admin/sessions?estado=ACTIVA&limit=50
```

**Parámetros de consulta:**
- `estado` (string, opcional): Filtrar por estado (ACTIVA, INACTIVA, EXPIRADA)
- `limit` (int, opcional): Número máximo de resultados (default: 50, max: 200)

**Respuesta:**
```json
[
  {
    "id_sesion": "sess_001",
    "usuario": "admin",
    "ip_cliente": "192.168.1.100",
    "inicio_sesion": "2025-10-30T07:14:40",
    "ultima_actividad": "2025-10-30T09:09:40",
    "estado": "ACTIVA",
    "requests_totales": 150
  }
]
```

#### `GET /api/admin/estadisticas`
**Obtener estadísticas detalladas del sistema**

```http
GET /api/admin/estadisticas
```

**Respuesta:**
```json
{
  "timestamp": "2025-10-30T09:14:40",
  "total_requests": 15420,
  "requests_exitosos": 14789,
  "requests_fallidos": 631,
  "ciudadanos_registrados": 234567,
  "sesiones_activas": 3,
  "validaciones_ultima_hora": 234,
  "promedio_requests_por_segundo": 4.28,
  "top_ips": [
    {
      "ip": "192.168.1.100",
      "requests": 1250,
      "porcentaje": 8.11
    }
  ]
}
```

#### `POST /api/admin/validar-masivo`
**Validación masiva de múltiples DNIs**

```http
POST /api/admin/validar-masivo
Content-Type: application/json

{
  "lista_dnis": ["12345678", "87654321", "11223344"],
  "incluir_detalle": false
}
```

**Parámetros:**
- `lista_dnis` (array): Lista de DNIs a validar (max: 1000)
- `incluir_detalle` (boolean): Incluir detalles de cada ciudadano

**Respuesta:**
```json
{
  "total_consultados": 3,
  "validos": 2,
  "invalidos": 1,
  "tiempo_total": 0.345,
  "promedio_tiempo_respuesta": 0.115,
  "resultados": [
    {
      "dni": "12345678",
      "es_valido": true,
      "mensaje": "DNI válido",
      "tiempo_respuesta": 0.100
    },
    {
      "dni": "87654321",
      "es_valido": true,
      "mensaje": "DNI válido",
      "tiempo_respuesta": 0.120
    },
    {
      "dni": "11223344",
      "es_valido": false,
      "mensaje": "DNI no encontrado",
      "tiempo_respuesta": 0.125
    }
  ]
}
```

---

## 🚦 Rate Limiting

### Límites Configurados

| Tipo de Endpoint | Límite | Ventana |
|------------------|---------|---------|
| Endpoints Públicos | 100 requests | 1 minuto |
| Endpoints Admin | 50 requests | 1 minuto |

### Respuesta Rate Limit Excedido

```json
{
  "error": "Demasiadas solicitudes",
  "detalle": "Demasiadas solicitudes. Intente más tarde.",
  "timestamp": "2025-10-30T09:14:40"
}
```

**Código de estado:** `429 Too Many Requests`

---

## ✅ Validación con Pydantic

### Modelos Implementados

#### Endpoints Públicos (`reniec_router.py`)
- `CiudadanoResponse`: Respuesta de ciudadano
- `ConsultarRequest`: Solicitud de consulta
- `ValidacionResponse`: Respuesta de validación
- `CiudadanoRequest`: Solicitud de ciudadano
- `HealthResponse`: Respuesta de health check

#### Endpoints Admin (`admin_router.py`)
- `SesionResponse`: Respuesta de sesión
- `EstadisticasResponse`: Respuesta de estadísticas
- `ValidacionMasivaRequest`: Solicitud de validación masiva
- `ResultadoValidacionIndividual`: Resultado individual de validación
- `ValidacionMasivaResponse`: Respuesta de validación masiva

### Validaciones Automáticas

- **DNI**: Debe tener exactamente 8 dígitos numéricos
- **Límites**: Validación de parámetros de consulta y paginación
- **Tipos**: Validación de tipos de datos automática
- **Campos requeridos**: Validación de campos obligatorios

---

## 📊 Logging

### Configuración de Logs

```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Información Registrada

- **Requests**: Método, URL, IP del cliente, tiempo de procesamiento
- **Validaciones**: DNI, resultado, tiempo de respuesta
- **Errores**: Detalles de errores con stack trace
- **Rate Limiting**: IPs que exceden límites
- **Administración**: Operaciones administrativas y estadísticas

### Ejemplo de Log

```
2025-10-30 09:14:40 - INFO - Validando DNI: 12345678
2025-10-30 09:14:40 - INFO - DNI 12345678 válido
2025-10-30 09:14:45 - WARNING - Rate limit excedido para IP: 192.168.1.100
```

---

## 🛡️ Manejo de Errores

### Códigos de Estado HTTP

| Código | Descripción | Ejemplo |
|--------|-------------|---------|
| 200 | Éxito | Validación exitosa |
| 400 | Bad Request | DNI con formato inválido |
| 401 | No autorizado | Acceso a endpoints admin sin auth |
| 403 | Prohibido | Permisos insuficientes |
| 404 | No encontrado | Ciudadano no existe |
| 429 | Too Many Requests | Rate limit excedido |
| 500 | Error interno | Error del servidor |

### Estructura de Error

```json
{
  "error": {
    "codigo": 400,
    "mensaje": "DNI debe tener 8 dígitos numéricos",
    "timestamp": "2025-10-30T09:14:40",
    "path": "/api/reniec/validar/1234567"
  }
}
```

---

## 📚 Documentación Swagger

### Accesos

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI Spec**: `/openapi.json`

### Características

- ✅ Documentación automática de endpoints
- ✅ Ejemplos de request/response
- ✅ Esquemas Pydantic integrados
- ✅ Validación interactiva
- ✅ Autenticación (configurable)

---

## 🚀 Instalación y Uso

### Integración en main.py

```python
from app.routers import reniec_router, admin_router

# Incluir routers en la aplicación
app.include_router(reniec_router.router, prefix="/api/reniec", tags=["RENIEC-Public"])
app.include_router(admin_router.router, prefix="/api/admin", tags=["Admin"])
```

### Dependencias Requeridas

```python
fastapi>=0.68.0
pydantic>=1.8.0
uvicorn>=0.15.0
```

### Ejecución

```bash
# Desarrollo
uvicorn main:app --reload

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🔄 Próximos Pasos

### Mejoras Recomendadas

1. **Autenticación JWT** para endpoints de administración
2. **Integración real** con la API de RENIEC
3. **Base de datos** persistente para ciudadanos
4. **Cache** con Redis para mejorar performance
5. **Monitoreo** con métricas detalladas
6. **Tests unitarios** y de integración

### Configuración de Producción

```python
# .env
RENIEC_API_URL=https://api.reniec.gob.pe
RENIEC_API_KEY=your-api-key
DATABASE_URL=postgresql://user:pass@localhost/reniec_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
```

---

**📝 Nota**: Esta documentación cubre los routers implementados. Para integración completa con la aplicación existente, revisar `main.py` y ajustar configuraciones según necesidades específicas del proyecto.
