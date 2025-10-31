# Suite de Pruebas - Servicio RENIEC (LP2)

Este directorio contiene la suite completa de pruebas para el servicio RENIEC.

## 📋 Estructura de Pruebas

### Archivos de Prueba

- **`test_models.py`** - Pruebas para modelos SQLAlchemy y Pydantic
- **`test_services.py`** - Pruebas unitarias para servicios de negocio  
- **`test_api.py`** - Pruebas de endpoints FastAPI
- **`conftest.py`** - Configuración y fixtures para pytest
- **`test_main.py`** - Pruebas existentes (compatibilidad)

### Configuración

- **`pytest.ini`** - Configuración global de pytest

## 🚀 Ejecución de Pruebas

### Ejecutar todas las pruebas
```bash
cd lp2_reniec_service
pytest
```

### Ejecutar por categoría

#### Tests Unitarios
```bash
pytest -m unit
```

#### Tests de Integración  
```bash
pytest -m integration
```

#### Tests de Modelos
```bash
pytest test_models.py -v
```

#### Tests de Servicios
```bash
pytest test_services.py -v
```

#### Tests de API
```bash
pytest test_api.py -v
```

### Ejecutar con cobertura
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Ejecutar tests específicos
```bash
# Test específico por nombre
pytest test_services.py::TestCiudadanoService::test_crear_ciudadano_success

# Test específico por marcador
pytest -m "test_crear_ciudadano"

# Tests sin cobertura (más rápido)
pytest --no-cov
```

## 📊 Cobertura de Pruebas

### Modelos SQLAlchemy (`test_models.py`)

#### BaseModel
- ✅ Creación de modelos base
- ✅ Campos heredados (id, fechas)
- ✅ Configuración de tabla abstracta

#### CiudadanoModel (Pydantic)
- ✅ Validaciones de DNI (numérico, 8 dígitos)
- ✅ Validaciones de teléfono (numérico)
- ✅ Validaciones de fecha de nacimiento (pasado)
- ✅ Configuración de serialización JSON

#### Ciudadano (SQLAlchemy)
- ✅ Creación y persistencia
- ✅ Restricciones únicas (DNI, email)
- ✅ Método `__repr__`
- ✅ Método `to_dict()`
- ✅ Campos automáticos (fechas)

#### Modelos RENIEC
- ✅ TipoDocumento
- ✅ Documento
- ✅ Solicitud
- ✅ EventoSolicitud
- ✅ SesionUsuario
- ✅ Relaciones entre modelos

### Servicios (`test_services.py`)

#### CiudadanoService
- ✅ Crear ciudadano
- ✅ Obtener por ID
- ✅ Buscar por documento
- ✅ Listar con paginación
- ✅ Actualizar datos
- ✅ Eliminar (desactivar)
- ✅ Búsqueda avanzada
- ✅ Verificar existencia
- ✅ Obtener documentos
- ✅ Obtener solicitudes
- ✅ Estadísticas

#### ReniecService
- ✅ Consultar DNI
- ✅ Verificar DNI
- ✅ Manejo de errores
- ✅ Formatos de respuesta

#### DocumentoService
- ✅ Crear documento
- ✅ Buscar documento
- ✅ Listar documentos
- ✅ Actualizar estado

### API Endpoints (`test_api.py`)

#### Health Check
- ✅ `/api/v1/health/` - Health check básico
- ✅ `/api/v1/health/detailed` - Health check detallado

#### RENIEC Endpoints
- ✅ `/api/v1/reniec/consulta-dni/{dni}` 
  - Formato de DNI inválido
  - DNI no encontrado
  - Consulta exitosa (ciudadano nuevo/existente)
  - Manejo de errores internos
- ✅ `/api/v1/reniec/verificar-dni`
  - Sin DNI proporcionado
  - Verificación exitosa
  - DNI inválido
  - Manejo de errores

#### Document Endpoints  
- ✅ `/api/v1/reniec/documento/{numero}`
  - Documento no encontrado
  - Consulta de DNI con datos RENIEC
  - Consulta de documento no-DNI

#### Statistics
- ✅ `/api/v1/reniec/estadisticas`
  - Obtención exitosa
  - Manejo de errores

#### Citizen Endpoints
- ✅ `/api/v1/citizens/`
  - Listado vacío
  - Listado con paginación
  - Parámetros inválidos
- ✅ POST `/api/v1/citizens/`
  - Creación exitosa
  - Datos inválidos

#### Document Management
- ✅ `/api/v1/documents/`
  - Listado vacío
  - Listado con paginación
- ✅ POST `/api/v1/documents/`
  - Creación exitosa
  - Datos inválidos

#### Integration Tests
- ✅ Flujo completo de consulta DNI
- ✅ Manejo de errores de API
- ✅ Estructura de respuestas
- ✅ Autenticación (endpoints públicos)

## 🛠️ Configuración

### Variables de Entorno de Prueba
```bash
ENVIRONMENT=test
DEBUG=true
DATABASE_URL=sqlite:///:memory:
TESTING=true
```

### Fixtures Disponibles

#### Base de Datos
- `test_database_url` - URL de BD en memoria
- `test_engine` - Engine SQLAlchemy
- `db_session` - Session de BD
- `clean_db` - BD limpia antes/después
- `populated_db` - BD con datos de prueba

#### Cliente HTTP
- `test_client` - Cliente FastAPI
- `test_client_with_auth` - Cliente con auth

#### Mocks
- `mock_reniec_api` - Mock API RENIEC
- `mock_ciudadano_service` - Mock servicio ciudadanos
- `mock_documento_service` - Mock servicio documentos

#### Datos de Prueba
- `sample_ciudadano_data` - Datos de ciudadano
- `sample_documento_data` - Datos de documento
- `sample_reniec_response` - Respuesta RENIEC

#### Objetos Mock
- `mock_ciudadano` - Objeto ciudadano
- `mock_documento` - Objeto documento
- `mock_solicitud` - Objeto solicitud

### Marcadores

- `@pytest.mark.unit` - Tests unitarios
- `@pytest.mark.integration` - Tests de integración  
- `@pytest.mark.slow` - Tests lentos
- `@pytest.mark.external_api` - Tests con APIs externas
- `@pytest.mark.database` - Tests que requieren BD

## 📈 Reportes

### Reportes Generados
- **HTML**: `reports/report.html` - Reporte visual
- **JUnit**: `reports/junit.xml` - Para CI/CD
- **Cobertura**: `htmlcov/index.html` - Cobertura detallada

### Métricas de Cobertura
- **Objetivo**: > 80% cobertura de código
- **Medición**: Líneas cubiertas / total
- **Exclusiones**: 
  - Archivos de prueba
  - `__pycache__`
  - Migraciones
  - Archivos de configuración

## 🚨 Manejo de Errores

### Errores de Base de Datos
- Rollback automático en caso de error
- Limpieza de conexiones
- Tests aislados con BD en memoria

### Errores de API Externa
- Mocks para RENIEC y servicios externos
- Simulación de respuestas y errores
- Timeouts configurables

### Errores de Validación
- Datos inválidos en requests
- Validaciones de formato
- Campos requeridos faltantes

## 🔧 Troubleshooting

### Problemas Comunes

#### Error de Importación
```bash
# Asegurar que el directorio padre esté en PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Tests Fallan por BD
```bash
# Usar BD en memoria explícitamente
pytest --db-url="sqlite:///:memory:"
```

#### Cobertura Baja
```bash
# Ver líneas no cubiertas
pytest --cov=app --cov-report=term-missing
```

#### Tests Lentos
```bash
# Ejecutar solo unit tests
pytest -m unit --durations=10
```

### Logs de Debug
```bash
# Habilitar logs detallados
pytest --log-cli-level=DEBUG --log-cli-format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
```

## 📝 Notas de Desarrollo

### Agregar Nuevos Tests

1. **Modelos**: Agregar en `test_models.py`
2. **Servicios**: Agregar en `test_services.py`  
3. **API**: Agregar en `test_api.py`
4. **Fixtures**: Agregar en `conftest.py`

### Convenciones

- **Nombres**: `test_[función]_[escenario]`
- **Documentación**: Docstrings descriptivos
- **Asserts**: Mensajes claros en aserciones
- **Cleanup**: Limpieza automática con fixtures

### Mejores Prácticas

1. **Aislar tests** - No dependencias entre tests
2. **Mock externo** - No llamar servicios reales
3. **Datos frescos** - Usar fixtures para datos
4. **Asserts específicos** - Verificar valores exactos
5. **Cleanup automático** - Usar fixtures para cleanup

## 🤝 Contribución

Al agregar nuevas funcionalidades:

1. Crear tests unitarios correspondientes
2. Actualizar tests de integración si aplica
3. Verificar cobertura > 80%
4. Documentar nuevos fixtures/marcadores
5. Ejecutar suite completa antes de commit

---

**Nota**: Esta suite de pruebas cubre la funcionalidad completa del servicio RENIEC según los requerimientos de LP2. Ejecutar regularmente para asegurar calidad del código.
