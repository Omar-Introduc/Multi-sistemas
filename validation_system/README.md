# Sistema de Validación Integral

Sistema completo de validación para el sistema distribuido bancario LP1-LP2-LP3.

## 📋 Descripción

Este sistema proporciona validación integral de:
- ✅ Comunicación entre servicios heterogéneos (Java, Python, JavaScript)
- ✅ Arquitectura distribuida y patrones de microservicios
- ✅ Escalabilidad y manejo de concurrencia
- ✅ Tolerancia a fallos y resiliencia
- ✅ Infraestructura de base de datos heterogénea (MySQL, PostgreSQL, Redis)
- ✅ Message queue (RabbitMQ)
- ✅ Containerización y Docker

## 🏗️ Arquitectura del Sistema de Validación

```
validation_system/
├── integration_test_suite.py      # Pruebas de integración LP1↔LP2↔LP3
├── validate_technologies.py       # Validación Java+Python+JS
├── validate_architecture.py       # Validación arquitectura distribuida
├── scalability_tests.py           # Pruebas de escalabilidad y concurrencia
├── fault_tolerance_tests.py       # Pruebas de tolerancia a fallos
├── run_complete_validation.py     # Ejecutor maestro
├── generate_final_report.py       # Generador de reportes
├── validation_config.json         # Configuración
├── reports/                       # Reportes generados
├── logs/                          # Logs del sistema
└── temp/                          # Archivos temporales
```

## 🚀 Uso

### Ejecución Completa

```bash
cd /workspace/validation_system
python3 run_complete_validation.py
```

### Ejecución de Módulos Individuales

```bash
# Solo pruebas de integración
python3 integration_test_suite.py

# Solo validación de tecnologías
python3 validate_technologies.py

# Solo validación de arquitectura
python3 validate_architecture.py

# Solo pruebas de escalabilidad
python3 scalability_tests.py

# Solo pruebas de tolerancia a fallos
python3 fault_tolerance_tests.py
```

### Generación de Reportes

```bash
# Generar todos los reportes
python3 generate_final_report.py --console

# Solo reporte HTML
python3 generate_final_report.py --output-html reporte.html

# Solo resumen JSON
python3 generate_final_report.py --output-json resumen.json
```

### Configuración Personalizada

```bash
# Usar configuración personalizada
python3 run_complete_validation.py --config mi_config.json

# Ejecutar solo módulos específicos
python3 run_complete_validation.py --modules integration scalability
```

## 📊 Módulos de Validación

### 1. Integration Test Suite (`integration_test_suite.py`)

**Propósito**: Validar comunicación y flujos entre servicios LP1, LP2 y LP3.

**Pruebas incluidas**:
- Health checks de servicios
- Flujo de validación de clientes (LP3→LP2→LP1)
- Integración con RabbitMQ
- Conectividad de bases de datos heterogéneas
- Peticiones concurrentes

**Tecnologías validadas**:
- ✅ HTTP/HTTPS entre servicios
- ✅ Message queues (RabbitMQ)
- ✅ Bases de datos múltiples (MySQL, PostgreSQL, Redis)

### 2. Technology Validation (`validate_technologies.py`)

**Propósito**: Verificar presencia y funcionalidad de tecnologías heterogéneas.

**Tecnologías validadas**:
- ✅ **Java**: JDK, compilación y ejecución
- ✅ **Python**: Runtime y librerías (requests, aiohttp, psycopg2, etc.)
- ✅ **Node.js/JavaScript**: Runtime, npm, ejecución
- ✅ **Docker**: Containerización y Docker Compose
- ✅ **RabbitMQ Clients**: pika (Python), amqplib (Node.js)
- ✅ **Database Clients**: PostgreSQL, MySQL, Redis
- ✅ **Testing Frameworks**: pytest, jest, JUnit

### 3. Architecture Validation (`validate_architecture.py`)

**Propósito**: Evaluar la arquitectura distribuida del sistema.

**Aspectos validados**:
- ✅ **Patrón de Microservicios**: Independencia y separación
- ✅ **Distribución de BD**: Heterogeneidad y especialización
- ✅ **Comunicación**: APIs, messaging, dependencias
- ✅ **Containerización**: Dockerfiles, Docker Compose
- ✅ **Escalabilidad**: Diseño horizontal, caching
- ✅ **Seguridad**: Aislamiento, encriptación, validación
- ✅ **Monitoreo**: Observabilidad, métricas

### 4. Scalability Tests (`scalability_tests.py`)

**Propósito**: Evaluar rendimiento bajo carga y concurrencia.

**Pruebas incluidas**:
- ✅ **Concurrencia Básica**: 1-50 usuarios concurrentes
- ✅ **Load Stress**: Incremento gradual hasta 200 usuarios
- ✅ **Uso de Memoria**: Detección de memory leaks
- ✅ **Escalabilidad de BD**: Rendimiento con operaciones concurrentes
- ✅ **Operaciones Concurrentes**: Entre múltiples servicios

**Métricas calculadas**:
- Requests por segundo (RPS)
- Tiempo de respuesta promedio
- Tasa de éxito bajo carga
- Throughput máximo

### 5. Fault Tolerance Tests (`fault_tolerance_tests.py`)

**Propósito**: Evaluar capacidad de recuperación y tolerancia a fallos.

**Escenarios probados**:
- ✅ **Indisponibilidad de Servicio**: Simulación de caída de LP2
- ✅ **Fallo de Base de Datos**: Degradación gradual de conectividad
- ✅ **Fallo de Message Queue**: RabbitMQ no disponible
- ✅ **Circuit Breaker Pattern**: Comportamiento bajo fallo repetitivo
- ✅ **Graceful Degradation**: Funcionamiento con recursos limitados

**Métricas de resiliencia**:
- Tiempo de recuperación
- Disponibilidad durante fallos
- Patrones de recuperación

## 📈 Reportes Generados

### Reporte HTML
- 📊 Dashboard interactivo con métricas visuales
- 📈 Gráficos de rendimiento y escalabilidad
- 📋 Tablas detalladas de resultados
- 🎯 Puntajes por módulo y general

### Resumen JSON
- 📄 Estructura de datos para integración
- 🔢 Métricas numéricas precisas
- 📊 Indicadores de salud del sistema

### Archivos de Log
- 🔍 Logs detallados de cada módulo
- 🐛 Trazas de errores y debugging
- ⚡ Métricas de rendimiento en tiempo real

## ⚙️ Configuración

Editar `validation_config.json`:

```json
{
  "services": {
    "lp1_banco": {
      "url": "http://localhost:8080",
      "port": 8080
    },
    "lp2_reniec": {
      "url": "http://localhost:8000", 
      "port": 8000
    },
    "lp3_cliente": {
      "url": "http://localhost:3000",
      "port": 3000
    }
  },
  "validation_modules": {
    "integration_tests": {
      "enabled": true,
      "timeout": 300
    },
    "scalability_tests": {
      "enabled": true,
      "timeout": 600
    }
  },
  "thresholds": {
    "min_success_rate": 90,
    "max_response_time": 2.0
  }
}
```

## 🎯 Criterios de Evaluación

### Puntaje General del Sistema (0-100%)
- **90-100%**: Excelente - Sistema robusto y confiable
- **70-89%**: Bueno - Sistema funcional con optimizaciones menores
- **50-69%**: Regular - Sistema funcional con mejoras requeridas
- **< 50%**: Deficiente - Sistema necesita revisión significativa

### Criterios Específicos

**Pruebas de Integración**:
- ✅ Tasa de éxito: ≥ 95%
- ✅ Comunicación entre servicios: 100%
- ✅ Conectividad de BD: 100%

**Validación de Tecnologías**:
- ✅ Java, Python, Node.js: Instalados y funcionales
- ✅ Docker: Disponible
- ✅ Clientes de BD: Presentes

**Escalabilidad**:
- ✅ Concurrencia: Maneja 50+ usuarios concurrentes
- ✅ RPS: > 10 requests/segundo
- ✅ Memoria: Sin leaks significativos

**Tolerancia a Fallos**:
- ✅ Recuperación: < 30 segundos
- ✅ Disponibilidad: ≥ 80% durante fallos
- ✅ Degradation: Graceful fallback

## 🐛 Troubleshooting

### Servicios No Disponibles
```bash
# Verificar estado de servicios
curl http://localhost:8080/api/health
curl http://localhost:8000/api/health  
curl http://localhost:3000/api/health
```

### Errores de Dependencias
```bash
# Instalar dependencias Python
pip3 install aiohttp psutil requests

# Instalar dependencias Node.js
npm install -g jest amqplib

# Verificar Java
javac -version
```

### Problemas de Docker
```bash
# Verificar Docker daemon
docker info

# Verificar Docker Compose
docker-compose --version
```

## 📁 Estructura de Archivos

```
validation_system/
├── reports/
│   ├── integration_test_results_YYYYMMDD_HHMMSS.json
│   ├── technology_validation_results_YYYYMMDD_HHMMSS.json
│   ├── architecture_validation_results_YYYYMMDD_HHMMSS.json
│   ├── scalability_test_results_YYYYMMDD_HHMMSS.json
│   ├── fault_tolerance_test_results_YYYYMMDD_HHMMSS.json
│   ├── consolidated_validation_report_YYYYMMDD_HHMMSS.json
│   ├── validation_report_YYYYMMDD_HHMMSS.html
│   └── validation_summary_YYYYMMDD_HHMMSS.json
├── logs/
│   ├── integration_tests.log
│   ├── technology_validation.log
│   ├── architecture_validation.log
│   ├── scalability_tests.log
│   ├── fault_tolerance_tests.log
│   └── validation_orchestrator_YYYYMMDD_HHMMSS.log
└── temp/
    └── (archivos temporales de prueba)
```

## 🔄 Integración Continua

### En GitLab CI/CD
```yaml
validation:
  stage: test
  script:
    - cd /workspace/validation_system
    - python3 run_complete_validation.py
    - python3 generate_final_report.py --console
  artifacts:
    reports:
      junit: reports/*.json
    paths:
      - reports/
    expire_in: 1 week
```

### En Docker
```dockerfile
FROM python:3.9-slim
COPY . /workspace/validation_system
WORKDIR /workspace/validation_system
RUN pip install -r requirements.txt
CMD ["python3", "run_complete_validation.py"]
```

## 🤝 Contribución

Para agregar nuevas pruebas:
1. Crear nuevo archivo `test_name.py`
2. Implementar clase con métodos de prueba
3. Agregar al `run_complete_validation.py`
4. Actualizar `generate_final_report.py`

## 📞 Soporte

Para problemas o preguntas:
- Revisar logs en `/workspace/validation_system/logs/`
- Verificar configuración en `validation_config.json`
- Ejecutar módulo individual para debugging

## 📜 Licencia

Este sistema de validación es parte del proyecto de Sistema Distribuido Bancario.
