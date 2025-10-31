# Documentación de APIs - Sistema Shibasito

## 📋 Índice

1. [Información General](#información-general)
2. [Servicio LP1 - Banco](#servicio-lp1---banco)
3. [Servicio LP2 - RENIEC](#servicio-lp2---reniec)
4. [Autenticación y Seguridad](#autenticación-y-seguridad)
5. [Códigos de Error](#códigos-de-error)
6. [Ejemplos de Uso](#ejemplos-de-uso)
7. [Rate Limiting](#rate-limiting)

---

## Información General

### Base URLs

| Servicio | URL Base | Puerto | Documentación |
|----------|----------|--------|---------------|
| **LP1 - Banco** | `http://localhost:8080` | 8080 | `/api/v1/banco/docs` |
| **LP2 - RENIEC** | `http://localhost:8000` | 8000 | `/api/v1/reniec/docs` |

### Formatos Soportados

- **Content-Type**: `application/json`
- **Accept**: `application/json`
- **Encoding**: UTF-8

### Headers Requeridos

```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer {jwt_token}
X-Request-ID: {uuid}
X-Client-Version: {version}
```

---

## Servicio LP1 - Banco

### Base URL
```
http://localhost:8080/api/v1/banco
```

### Endpoints Principales

#### 1. Health Check

##### GET `/health`
Verificación básica de salud del servicio.

**Response:**
```json
{
  "status": "UP",
  "timestamp": "2025-10-30T11:09:55Z",
  "version": "1.0.0",
  "uptime": "2d 15h 30m"
}
```

##### GET `/health/detailed`
Health check detallado con información de dependencias.

**Response:**
```json
{
  "status": "UP",
  "components": {
    "database": {
      "status": "UP",
      "details": {
        "database": "PostgreSQL",
        "version": "14.0",
        "activeConnections": 5,
        "maxConnections": 100
      }
    },
    "rabbitmq": {
      "status": "UP",
      "details": {
        "broker": "RabbitMQ",
        "version": "3.11.0",
        "queueDepth": 0
      }
    },
    "redis": {
      "status": "UP",
      "details": {
        "version": "7.0.0",
        "usedMemory": "45MB",
        "connectedClients": 2
      }
    }
  }
}
```

#### 2. Gestión de Clientes

##### POST `/clientes`
Crear un nuevo cliente bancario.

**Request Body:**
```json
{
  "nombres": "JUAN CARLOS",
  "apellidos": "PEREZ GARCIA",
  "dni": "12345678",
  "email": "juan.perez@email.com",
  "telefono": "+51 999 888 777",
  "direccion": {
    "calle": "Av. Principal 123",
    "distrito": "LIMA",
    "provincia": "LIMA",
    "departamento": "LIMA"
  },
  "fechaNacimiento": "1985-05-15",
  "estadoCivil": "CASADO"
}
```

**Response 201:**
```json
{
  "data": {
    "id": 1,
    "numeroCliente": "CLI-2025-001",
    "nombres": "JUAN CARLOS",
    "apellidos": "PEREZ GARCIA",
    "dni": "12345678",
    "email": "juan.perez@email.com",
    "estado": "ACTIVO",
    "fechaCreacion": "2025-10-30T11:09:55Z"
  },
  "message": "Cliente creado exitosamente"
}
```

##### GET `/clientes/{id}`
Obtener información de un cliente específico.

**Response 200:**
```json
{
  "data": {
    "id": 1,
    "numeroCliente": "CLI-2025-001",
    "nombres": "JUAN CARLOS",
    "apellidos": "PEREZ GARCIA",
    "dni": "12345678",
    "email": "juan.perez@email.com",
    "telefono": "+51 999 888 777",
    "cuentas": [
      {
        "numero": "123-456-7890123456-12",
        "tipo": "AHORRO",
        "saldo": 15000.50,
        "estado": "ACTIVA"
      }
    ],
    "fechaCreacion": "2025-10-30T11:09:55Z"
  }
}
```

##### PUT `/clientes/{id}`
Actualizar información de un cliente.

**Request Body:**
```json
{
  "email": "nuevo.email@email.com",
  "telefono": "+51 999 777 666"
}
```

##### GET `/clientes/dni/{dni}`
Buscar cliente por DNI.

#### 3. Gestión de Cuentas

##### POST `/cuentas`
Crear una nueva cuenta bancaria.

**Request Body:**
```json
{
  "clienteId": 1,
  "tipo": "AHORRO",
  "moneda": "PEN",
  "sucursal": "LIMA-CENTRO"
}
```

**Response 201:**
```json
{
  "data": {
    "numero": "123-456-7890123456-12",
    "tipo": "AHORRO",
    "saldo": 0.00,
    "moneda": "PEN",
    "estado": "ACTIVA",
    "fechaApertura": "2025-10-30T11:09:55Z"
  },
  "message": "Cuenta creada exitosamente"
}
```

##### GET `/cuentas/{numero}`
Obtener información de una cuenta específica.

##### GET `/cuentas/cliente/{clienteId}`
Listar cuentas de un cliente.

##### PUT `/cuentas/{numero}/bloquear`
Bloquear una cuenta bancaria.

#### 4. Transacciones

##### POST `/transacciones/deposito`
Realizar un depósito en cuenta.

**Request Body:**
```json
{
  "cuentaNumero": "123-456-7890123456-12",
  "monto": 1000.00,
  "descripcion": "Depósito en efectivo",
  "canal": "CAJERO"
}
```

**Response 200:**
```json
{
  "data": {
    "id": 1001,
    "numeroTransaccion": "TXN-2025-001001",
    "cuentaOrigen": "123-456-7890123456-12",
    "tipo": "DEPOSITO",
    "monto": 1000.00,
    "saldoAnterior": 5000.00,
    "saldoPosterior": 6000.00,
    "estado": "COMPLETADA",
    "fecha": "2025-10-30T11:09:55Z"
  },
  "message": "Depósito realizado exitosamente"
}
```

##### POST `/transacciones/retiro`
Realizar un retiro de cuenta.

**Request Body:**
```json
{
  "cuentaNumero": "123-456-7890123456-12",
  "monto": 500.00,
  "descripcion": "Retiro en cajero",
  "canal": "CAJERO",
  "cajeroId": "CAJ-001"
}
```

##### POST `/transacciones/transferencia`
Transferencia entre cuentas.

**Request Body:**
```json
{
  "cuentaOrigen": "123-456-7890123456-12",
  "cuentaDestino": "987-654-3210987654-32",
  "monto": 2000.00,
  "descripcion": "Transferencia a cuenta de ahorros",
  "referencia": "REF-001"
}
```

##### GET `/transacciones/cuenta/{numero}`
Obtener historial de transacciones de una cuenta.

##### GET `/transacciones/{id}`
Obtener detalles de una transacción específica.

#### 5. Validación de Identidad

##### POST `/validacion/identidad`
Solicitar validación de identidad a través del servicio RENIEC.

**Request Body:**
```json
{
  "dni": "12345678",
  "nombres": "JUAN CARLOS",
  "apellidoPaterno": "PEREZ",
  "apellidoMaterno": "GARCIA",
  "idSolicitud": "SOL-2025-001",
  "idBanco": "BANCO_001",
  "contexto": {
    "tipoOperacion": "APERTURA_CUENTA",
    "sucursal": "LIMA-CENTRO"
  }
}
```

**Response 202:**
```json
{
  "data": {
    "idSolicitud": "SOL-2025-001",
    "estado": "EN_PROCESO",
    "mensaje": "Solicitud de validación enviada",
    "tiempoEstimado": 30,
    "timestamp": "2025-10-30T11:09:55Z"
  },
  "message": "Validación de identidad en proceso"
}
```

##### GET `/validacion/solicitud/{idSolicitud}`
Consultar estado de una solicitud de validación.

**Response 200:**
```json
{
  "data": {
    "idSolicitud": "SOL-2025-001",
    "estado": "COMPLETADA",
    "resultado": {
      "valida": true,
      "scoreConfianza": 95,
      "datosCiudadano": {
        "numeroDocumento": "12345678",
        "nombres": "JUAN CARLOS",
        "apellidoPaterno": "PEREZ",
        "apellidoMaterno": "GARCIA",
        "fechaNacimiento": "1985-05-15"
      }
    },
    "timestampInicio": "2025-10-30T11:09:55Z",
    "timestampFin": "2025-10-30T11:10:15Z",
    "duracion": 20
  },
  "message": "Validación completada exitosamente"
}
```

#### 6. Préstamos

##### POST `/prestamos`
Solicitar un préstamo.

**Request Body:**
```json
{
  "clienteId": 1,
  "monto": 50000.00,
  "plazoMeses": 36,
  "tipo": "PERSONAL",
  "proposito": "Compra de vehículo",
  "ingresosMensuales": 8000.00,
  "gastosMensuales": 4000.00
}
```

##### GET `/prestamos/{id}`
Obtener información de un préstamo.

##### GET `/prestamos/cliente/{clienteId}`
Listar préstamos de un cliente.

##### PUT `/prestamos/{id}/aprobar`
Aprobar un préstamo.

##### POST `/prestamos/{id}/pago`
Realizar pago de cuota.

---

## Servicio LP2 - RENIEC

### Base URL
```
http://localhost:8000/api/v1/reniec
```

### Endpoints Principales

#### 1. Health Check

##### GET `/health`
Verificación básica de salud del servicio.

**Response:**
```json
{
  "status": "UP",
  "timestamp": "2025-10-30T11:09:55Z",
  "version": "1.0.0",
  "service": "LP2-RENIEC"
}
```

##### GET `/health/detailed`
Health check detallado con información de dependencias.

**Response:**
```json
{
  "status": "UP",
  "components": {
    "database": {
      "status": "UP",
      "details": {
        "database": "MySQL",
        "version": "8.0.30",
        "activeConnections": 3,
        "poolStatus": "HEALTHY"
      }
    },
    "rabbitmq": {
      "status": "UP",
      "details": {
        "broker": "RabbitMQ",
        "version": "3.11.0",
        "exchanges": 3,
        "queues": 5
      }
    },
    "redis": {
      "status": "UP",
      "details": {
        "version": "7.0.0",
        "usedMemory": "25MB",
        "hitRate": "98.5%"
      }
    }
  },
  "metrics": {
    "requestsProcessed": 1247,
    "averageResponseTime": 145,
    "errorRate": 0.02
  }
}
```

##### GET `/health/ready`
Readiness check para Kubernetes.

##### GET `/health/live`
Liveness check para Kubernetes.

#### 2. Consulta por DNI

##### GET `/consulta-dni/{dni}`
Consultar información ciudadana por DNI.

**Path Parameters:**
- `dni` (string): Número de DNI (8 dígitos)

**Response 200:**
```json
{
  "data": {
    "numeroDocumento": "12345678",
    "nombres": "JUAN CARLOS",
    "apellidoPaterno": "PEREZ",
    "apellidoMaterno": "GARCIA",
    "fechaNacimiento": "1985-05-15",
    "estadoCivil": "CASADO",
    "direccion": {
      "calle": "AV. PRINCIPAL 123",
      "distrito": "LIMA",
      "provincia": "LIMA",
      "departamento": "LIMA"
    },
    "activo": true,
    "fechaConsulta": "2025-10-30T11:09:55Z"
  },
  "message": "Datos obtenidos exitosamente"
}
```

**Response 400:**
```json
{
  "error": {
    "code": "INVALID_DNI",
    "message": "DNI debe tener exactamente 8 dígitos",
    "timestamp": "2025-10-30T11:09:55Z",
    "requestId": "req-123e4567-e89b-12d3-a456-426614174000"
  }
}
```

**Response 404:**
```json
{
  "error": {
    "code": "CITIZEN_NOT_FOUND",
    "message": "No se encontraron datos para el DNI especificado",
    "timestamp": "2025-10-30T11:09:55Z",
    "requestId": "req-123e4567-e89b-12d3-a456-426614174000"
  }
}
```

#### 3. Verificación de DNI

##### POST `/verificar-dni`
Verificar autenticidad de un DNI.

**Request Body:**
```json
{
  "numeroDni": "12345678",
  "nombres": "JUAN CARLOS",
  "apellidoPaterno": "PEREZ",
  "apellidoMaterno": "GARCIA",
  "fechaNacimiento": "1985-05-15"
}
```

**Response 200:**
```json
{
  "data": {
    "dni": "12345678",
    "valida": true,
    "scoreConfianza": 98,
    "diferencias": [],
    "fechaVerificacion": "2025-10-30T11:09:55Z",
    "metodoVerificacion": "DATABASE_LOOKUP"
  },
  "message": "DNI verificado exitosamente"
}
```

#### 4. Consulta de Documentos

##### GET `/documento/{numero}`
Consultar documento por número.

**Path Parameters:**
- `numero` (string): Número de documento

**Response 200:**
```json
{
  "data": {
    "id": 1,
    "numeroDocumento": "12345678",
    "tipo": "DNI",
    "estado": "VIGENTE",
    "fechaEmision": "2020-01-15",
    "fechaVencimiento": null,
    "ciudadanoId": "12345678",
    "metadata": {
      "lugarEmision": "LIMA",
      "oficina": "RENIEC-LIMA-001"
    }
  },
  "message": "Documento encontrado"
}
```

##### GET `/estadisticas`
Obtener estadísticas del servicio.

**Response 200:**
```json
{
  "data": {
    "totalConsultas": 15420,
    "consultasExitosas": 15187,
    "consultasFallidas": 233,
    "tiempoPromedioRespuesta": 145,
    "consultasUltimas24h": 1247,
    "dnisMasConsultados": [
      {"dni": "12345678", "consultas": 15},
      {"dni": "87654321", "consultas": 12}
    ]
  },
  "timestamp": "2025-10-30T11:09:55Z"
}
```

#### 5. Mensajería Asíncrona

##### POST `/mensajes/solicitud-validacion`
Procesar solicitud de validación de identidad.

**Request Body:**
```json
{
  "idSolicitud": "SOL-2025-001",
  "dni": "12345678",
  "nombres": "JUAN CARLOS",
  "apellidoPaterno": "PEREZ",
  "apellidoMaterno": "GARCIA",
  "idBanco": "BANCO_001",
  "contexto": {
    "tipoOperacion": "APERTURA_CUENTA",
    "timestamp": "2025-10-30T11:09:55Z"
  }
}
```

**Response 202:**
```json
{
  "data": {
    "idSolicitud": "SOL-2025-001",
    "estado": "RECEIVED",
    "mensaje": "Solicitud recibida y procesada",
    "tiempoEstimado": 30,
    "timestamp": "2025-10-30T11:09:55Z"
  },
  "message": "Solicitud de validación enviada al queue"
}
```

#### 6. Gestión de Ciudadanos

##### GET `/ciudadanos`
Listar ciudadanos (con paginación).

**Query Parameters:**
- `page` (int, default: 1): Número de página
- `size` (int, default: 20): Tamaño de página
- `search` (string, optional): Término de búsqueda

**Response 200:**
```json
{
  "data": {
    "ciudadanos": [
      {
        "numeroDocumento": "12345678",
        "nombres": "JUAN CARLOS",
        "apellidoPaterno": "PEREZ",
        "apellidoMaterno": "GARCIA",
        "fechaNacimiento": "1985-05-15",
        "activo": true,
        "fechaCreacion": "2025-10-30T11:09:55Z"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 50,
      "totalItems": 1000,
      "pageSize": 20
    }
  },
  "message": "Lista obtenida exitosamente"
}
```

##### POST `/ciudadanos`
Crear un nuevo registro de ciudadano.

**Request Body:**
```json
{
  "numeroDocumento": "12345678",
  "nombres": "JUAN CARLOS",
  "apellidoPaterno": "PEREZ",
  "apellidoMaterno": "GARCIA",
  "fechaNacimiento": "1985-05-15",
  "estadoCivil": "CASADO",
  "direccion": {
    "calle": "Av. Principal 123",
    "distrito": "LIMA",
    "provincia": "LIMA",
    "departamento": "LIMA"
  }
}
```

**Response 201:**
```json
{
  "data": {
    "numeroDocumento": "12345678",
    "nombres": "JUAN CARLOS",
    "apellidoPaterno": "PEREZ",
    "apellidoMaterno": "GARCIA",
    "fechaNacimiento": "1985-05-15",
    "estadoCivil": "CASADO",
    "activo": true,
    "fechaCreacion": "2025-10-30T11:09:55Z"
  },
  "message": "Ciudadano creado exitosamente"
}
```

##### GET `/ciudadanos/{id}`
Obtener ciudadano por ID.

##### GET `/ciudadanos/documento/{dni}`
Buscar ciudadano por DNI.

##### PUT `/ciudadanos/{id}`
Actualizar información de ciudadano.

##### DELETE `/ciudadanos/{id}`
Eliminar ciudadano (soft delete).

##### POST `/ciudadanos/buscar`
Búsqueda avanzada de ciudadanos.

**Request Body:**
```json
{
  "filtros": {
    "nombres": "JUAN",
    "apellidoPaterno": "PEREZ",
    "distrito": "LIMA",
    "fechaNacimientoDesde": "1980-01-01",
    "fechaNacimientoHasta": "1990-12-31",
    "activo": true
  },
  "orden": {
    "campo": "fechaCreacion",
    "direccion": "DESC"
  }
}
```

##### GET `/ciudadanos/{id}/documentos`
Obtener documentos de un ciudadano.

##### GET `/ciudadanos/{id}/solicitudes`
Obtener solicitudes de validación de un ciudadano.

#### 7. Gestión de Documentos

##### GET `/documents`
Listar documentos (con paginación).

##### POST `/documents`
Crear nuevo documento.

**Request Body:**
```json
{
  "numeroDocumento": "12345678",
  "tipo": "DNI",
  "estado": "VIGENTE",
  "fechaEmision": "2020-01-15",
  "metadata": {
    "lugarEmision": "LIMA",
    "oficina": "RENIEC-LIMA-001"
  }
}
```

##### GET `/documents/{id}`
Obtener documento por ID.

##### PUT `/documents/{id}`
Actualizar documento.

##### DELETE `/documents/{id}`
Eliminar documento.

##### POST `/documents/subir-archivo/{id}`
Subir archivo asociado al documento.

**Request:** Multipart form data
- `file`: Archivo a subir

---

## Autenticación y Seguridad

### JWT Token

Todos los endpoints (excepto health checks) requieren autenticación JWT.

#### Obtener Token

##### POST `/auth/login`
Iniciar sesión y obtener JWT token.

**Request Body:**
```json
{
  "username": "usuario",
  "password": "password",
  "clientId": "desktop-app"
}
```

**Response 200:**
```json
{
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 3600,
    "tokenType": "Bearer",
    "user": {
      "id": 1,
      "username": "usuario",
      "roles": ["USER"],
      "permissions": ["READ", "WRITE"]
    }
  },
  "message": "Autenticación exitosa"
}
```

#### Refresh Token

##### POST `/auth/refresh`
Renovar token de acceso.

**Request Body:**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response 200:**
```json
{
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 3600,
    "tokenType": "Bearer"
  },
  "message": "Token renovado exitosamente"
}
```

### Estructura JWT

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "1",
    "username": "usuario",
    "roles": ["USER"],
    "permissions": ["READ", "WRITE"],
    "iat": 1630000000,
    "exp": 1630003600,
    "iss": "shibasito-auth",
    "aud": "shibasito-api"
  }
}
```

### Headers de Autorización

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Códigos de Error

### Códigos de Estado HTTP

| Código | Significado | Descripción |
|--------|-------------|-------------|
| `200` | OK | Solicitud exitosa |
| `201` | Created | Recurso creado exitosamente |
| `202` | Accepted | Solicitud aceptada para procesamiento |
| `400` | Bad Request | Solicitud malformada |
| `401` | Unauthorized | No autenticado |
| `403` | Forbidden | Sin permisos |
| `404` | Not Found | Recurso no encontrado |
| `409` | Conflict | Conflicto de datos |
| `422` | Unprocessable Entity | Datos inválidos |
| `429` | Too Many Requests | Rate limit excedido |
| `500` | Internal Server Error | Error interno del servidor |
| `502` | Bad Gateway | Error de gateway |
| `503` | Service Unavailable | Servicio no disponible |

### Códigos de Error Específicos

#### Errores de Validación (LP1)

| Código | Descripción |
|--------|-------------|
| `INVALID_DNI` | DNI inválido o no encontrado |
| `INSUFFICIENT_FUNDS` | Fondos insuficientes |
| `ACCOUNT_BLOCKED` | Cuenta bloqueada |
| `INVALID_AMOUNT` | Monto inválido |
| `DUPLICATE_TRANSACTION` | Transacción duplicada |

#### Errores de Validación (LP2)

| Código | Descripción |
|--------|-------------|
| `CITIZEN_NOT_FOUND` | Ciudadano no encontrado |
| `INVALID_DOCUMENT_TYPE` | Tipo de documento inválido |
| `DATABASE_ERROR` | Error de base de datos |
| `VALIDATION_TIMEOUT` | Timeout en validación |
| `RABBITMQ_ERROR` | Error en mensaje queue |

### Formato de Error

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "DNI proporcionado no es válido",
    "details": {
      "field": "dni",
      "value": "12345",
      "reason": "DNI debe tener exactamente 8 dígitos"
    },
    "timestamp": "2025-10-30T11:09:55Z",
    "requestId": "req-123e4567-e89b-12d3-a456-426614174000",
    "traceId": "trace-123e4567-e89b-12d3-a456-426614174000"
  }
}
```

---

## Ejemplos de Uso

### Cliente Curl - Validación de Identidad

```bash
# 1. Obtener token de autenticación
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario",
    "password": "password",
    "clientId": "desktop-app"
  }'

# 2. Solicitar validación de identidad
curl -X POST http://localhost:8080/api/v1/banco/validacion/identidad \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: req-123e4567-e89b-12d3-a456-426614174000" \
  -d '{
    "dni": "12345678",
    "nombres": "JUAN CARLOS",
    "apellidoPaterno": "PEREZ",
    "apellidoMaterno": "GARCIA",
    "idSolicitud": "SOL-2025-001",
    "idBanco": "BANCO_001"
  }'

# 3. Consultar estado de la validación
curl -X GET http://localhost:8080/api/v1/banco/validacion/solicitud/SOL-2025-001 \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### Cliente Python - Consulta DNI

```python
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000/api/v1/reniec"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def consultar_dni(dni):
    """Consultar información por DNI"""
    url = f"{BASE_URL}/consulta-dni/{dni}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Datos encontrados para DNI {dni}:")
        print(f"   Nombres: {data['data']['nombres']}")
        print(f"   Apellidos: {data['data']['apellidoPaterno']} {data['data']['apellidoMaterno']}")
        print(f"   Fecha Nacimiento: {data['data']['fechaNacimiento']}")
        
        return data['data']
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error HTTP: {e}")
        print(f"   Response: {response.json()}")
        return None
    except Exception as e:
        print(f"❌ Error general: {e}")
        return None

# Ejemplo de uso
if __name__ == "__main__":
    dni = "12345678"
    result = consultar_dni(dni)
```

### Cliente JavaScript - Transacción Bancaria

```javascript
const axios = require('axios');

class BancoAPI {
    constructor(baseURL, accessToken) {
        this.client = axios.create({
            baseURL: baseURL,
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
                'X-Request-ID': this.generateUUID()
            }
        });
    }

    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    async realizarDeposito(cuentaNumero, monto, descripcion) {
        try {
            const response = await this.client.post('/api/v1/banco/transacciones/deposito', {
                cuentaNumero,
                monto,
                descripcion,
                canal: 'API'
            });

            console.log('✅ Depósito realizado exitosamente:');
            console.log(`   Transacción: ${response.data.data.numeroTransaccion}`);
            console.log(`   Monto: S/ ${response.data.data.monto}`);
            console.log(`   Saldo posterior: S/ ${response.data.data.saldoPosterior}`);

            return response.data.data;
        } catch (error) {
            console.error('❌ Error en depósito:', error.response.data);
            throw error;
        }
    }

    async consultarSaldo(cuentaNumero) {
        try {
            const response = await this.client.get(`/api/v1/banco/cuentas/${cuentaNumero}`);
            return response.data.data.saldo;
        } catch (error) {
            console.error('❌ Error consultando saldo:', error.response.data);
            throw error;
        }
    }
}

// Ejemplo de uso
async function ejemplo() {
    const api = new BancoAPI('http://localhost:8080', 'ACCESS_TOKEN_HERE');
    
    try {
        const saldo = await api.consultarSaldo('123-456-7890123456-12');
        console.log(`💰 Saldo actual: S/ ${saldo}`);
        
        const resultado = await api.realizarDeposito('123-456-7890123456-12', 1000, 'Depósito vía API');
        console.log('💳 Nueva transacción:', resultado.numeroTransaccion);
    } catch (error) {
        console.error('❌ Error:', error.message);
    }
}

ejemplo();
```

---

## Rate Limiting

### Límites por Endpoint

| Endpoint | Límite | Ventana | Headers |
|----------|--------|---------|---------|
| `/auth/login` | 5 req | 1 min | X-RateLimit-* |
| `/consulta-dni/{dni}` | 100 req | 1 hour | X-RateLimit-* |
| `/clientes` | 50 req | 1 hour | X-RateLimit-* |
| `/transacciones` | 200 req | 1 hour | X-RateLimit-* |
| Health checks | 1000 req | 1 hour | X-RateLimit-* |

### Headers de Rate Limiting

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1630000600
X-RateLimit-Window: 3600
```

### Respuesta de Rate Limit Excedido

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again later.",
    "details": {
      "limit": 100,
      "window": 3600,
      "retryAfter": 1800
    },
    "timestamp": "2025-10-30T11:09:55Z",
    "requestId": "req-123e4567-e89b-12d3-a456-426614174000"
  }
}
```

---

## 📊 Métricas y Monitoreo

### Prometheus Metrics

El sistema expone las siguientes métricas:

```
# Application metrics
http_requests_total{method="GET",endpoint="/health",status="200"} 1247
http_request_duration_seconds{method="POST",endpoint="/validacion",quantile="0.95"} 0.234
application_errors_total{error_type="VALIDATION_ERROR"} 15

# Business metrics
validations_processed_total 1247
validations_successful_total 1198
validations_failed_total 49
database_connections_active 5
rabbitmq_messages_sent_total 892
```

### Dashboards Disponibles

- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **RabbitMQ Management**: http://localhost:15672

---

**Documento generado**: 30 de Octubre de 2025  
**Versión**: 1.0  
**Última actualización**: 30 de Octubre de 2025
