# Sistema Completo de Stress Testing

## 📋 Descripción General

Este sistema proporciona una suite completa de pruebas de estrés y validación para sistemas distribuidos con bases de datos MySQL. Incluye pruebas específicas para:

- **LP1 - Sistema Bancario**: Tests de estrés para operaciones bancarias
- **LP2 - Sistema RENIEC**: Tests de estrés para validación de identidad
- **Validación de Integridad**: Verificación cruzada entre bases de datos
- **Tests de Persistencia**: Validación de recuperación y backups
- **Generación de Reportes**: HTML y JSON automáticos
- **Automatización**: Ejecución programada y coordinación de tests

## 🏗️ Estructura del Sistema

```
testing_system/
├── stress_test_lp1.py              # Tests de estrés para LP1 Banco
├── stress_test_lp2.py              # Tests de estrés para LP2 RENIEC
├── validate_data_integrity.py      # Validación de integridad BD1 vs BD2
├── generate_test_reports.py        # Generador de reportes HTML/JSON
├── automation_test_suite.py        # Suite de automatización
├── persistence_tests.py            # Tests de persistencia y recuperación
├── README.md                       # Esta documentación
├── example_usage.py                # Ejemplo de uso
├── test_reports/                   # Reportes generados
├── automation_config.json         # Configuración (generable)
└── logs/                          # Archivos de log
```

## 🚀 Características Principales

### 1. Stress Testing LP1 (Sistema Bancario)
- ✅ 1500+ registros de prueba automatizados
- ✅ 50 hilos concurrentes para carga máxima
- ✅ Generación de clientes, cuentas, transacciones y préstamos
- ✅ Métricas detalladas de performance
- ✅ Validación de integridad de datos bancarios
- ✅ Timeouts configurables (30s por defecto)

### 2. Stress Testing LP2 (Sistema RENIEC)
- ✅ 1500+ ciudadanos de prueba
- ✅ Simulación de validadores y sesiones
- ✅ Validación específica de DNIs
- ✅ Tests de auditoría y trazabilidad
- ✅ Análisis de cumplimiento normativo
- ✅ Pruebas de verificación de identidad

### 3. Validación de Integridad
- ✅ Comparación cruzada entre BD1 y BD2
- ✅ Verificación de consistencia de datos
- ✅ Análisis de integridad referencial
- ✅ Detección de anomalías y duplicados
- ✅ Validación de transacciones ACID
- ✅ Evaluación de cumplimiento normativo

### 4. Tests de Persistencia
- ✅ Pruebas de recuperación ante fallos
- ✅ Validación de backups y restauraciones
- ✅ Tests de concurrencia y transacciones
- ✅ Análisis de performance de persistencia
- ✅ Verificación de constraints y triggers
- ✅ Simulación de escenarios de error

### 5. Generación de Reportes
- ✅ Reportes HTML interactivos con gráficos
- ✅ Reportes JSON estructurados para integración
- ✅ Dashboard ejecutivo con métricas clave
- ✅ Análisis estadístico avanzado
- ✅ Comparaciones históricas
- ✅ Exportación automática

### 6. Automatización Completa
- ✅ Ejecución secuencial y paralela
- ✅ Configuración centralizada JSON
- ✅ Programación de tests automáticos
- ✅ Manejo de dependencias entre tests
- ✅ Orquestación de reportes
- ✅ Monitoreo de resultados

## 📊 Métricas y Validaciones

### Métricas de Performance
- **Tiempo de respuesta promedio/mínimo/máximo**
- **Operaciones por segundo**
- **Tasa de éxito/fallo**
- **Uso de CPU y memoria**
- **Throughput de transacciones**

### Métricas de Calidad de Datos
- **Integridad referencial**
- **Validación de formatos (DNI, email, teléfono)**
- **Consistencia de datos**
- **Duplicados detectados**
- **Constraints y validaciones**

### Métricas de Concurrencia
- **Hilos completados exitosamente**
- **Colisiones y deadlocks**
- **Distribución de carga**
- **Escalabilidad del sistema**

## 🔧 Instalación y Configuración

### Prerrequisitos
```bash
# Python 3.8+
# MySQL 5.7+ / MariaDB 10.3+
# Bibliotecas Python:
pip install mysql-connector-python pandas schedule
```

### Configuración de Bases de Datos

#### LP1 - Sistema Bancario
```sql
CREATE DATABASE banco_lp1 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- Usar scripts de /workspace/shibasito-sistema-distribuido/init-scripts/
```

#### LP2 - Sistema RENIEC
```sql
CREATE DATABASE reniec_lp2 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- Usar scripts de /workspace/shibasito-sistema-distribuido/init-scripts/
```

### Configuración del Sistema

Crear archivo `automation_config.json`:

```json
{
    "databases": {
        "lp1": {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "password",
            "database": "banco_lp1",
            "charset": "utf8mb4"
        },
        "lp2": {
            "host": "localhost", 
            "port": 3306,
            "user": "root",
            "password": "password",
            "database": "reniec_lp2",
            "charset": "utf8mb4"
        }
    },
    "test_settings": {
        "target_records": 1500,
        "concurrent_threads": 50,
        "timeout_seconds": 30,
        "parallel_execution": true
    },
    "thresholds": {
        "success_rate_minimum": 95.0,
        "response_time_maximum": 2.0,
        "error_rate_maximum": 5.0
    }
}
```

## 🎯 Uso del Sistema

### Uso Básico - Ejecución Individual

#### Stress Test LP1 (Banco)
```bash
python stress_test_lp1.py
```

#### Stress Test LP2 (RENIEC)
```bash
python stress_test_lp2.py
```

#### Validación de Integridad
```bash
python validate_data_integrity.py
```

#### Tests de Persistencia
```bash
python persistence_tests.py
```

### Uso Avanzado - Suite Completa

#### Ejecutar Suite Completa
```bash
python automation_test_suite.py --mode full --config automation_config.json
```

#### Ejecutar Solo Tests de Stress
```bash
python automation_test_suite.py --mode stress --parallel
```

#### Ejecutar Tests Programados
```bash
python automation_test_suite.py --mode scheduled --config automation_config.json
```

#### Crear Configuración de Ejemplo
```bash
python automation_test_suite.py --create-config
```

### Ejemplo de Uso Programático

```python
from automation_test_suite import AutomationTestSuite, TestConfiguration

# Crear configuración
config = TestConfiguration('automation_config.json')

# Crear suite
suite = AutomationTestSuite(config)

# Ejecutar suite completa
results = suite.run_comprehensive_test_suite()

# Verificar resultados
if results['overall_success']:
    print("✅ Tests ejecutados exitosamente")
else:
    print("❌ Algunos tests fallaron")

# Ver reportes generados
report_files = results['final_report']['report_files']
for file_type, file_path in report_files.items():
    print(f"{file_type}: {file_path}")
```

## 📈 Interpretación de Resultados

### Códigos de Estado
- **PASSED**: Test ejecutado exitosamente, todos los criterios cumplidos
- **WARNING**: Test ejecutado con warnings, pero dentro de tolerancias
- **FAILED**: Test falló, requiere atención inmediata

### Métricas de Éxito
- **Tasa de Éxito**: >95% para considerar exitoso
- **Tiempo de Respuesta**: <2.0s promedio para considerar bueno
- **Tasa de Errores**: <5% para considerar aceptable

### Reportes Generados

#### Reporte HTML
- Dashboard interactivo con gráficos
- Navegación por secciones
- Visualización de métricas en tiempo real
- Exportación a PDF

#### Reporte JSON
- Datos estructurados para integración
- Métricas detalladas y metadata
- Historial de ejecuciones
- Análisis de tendencias

## 🔍 Validaciones Específicas

### LP1 - Sistema Bancario
- ✅ Emails válidos (formato RFC)
- ✅ Teléfonos peruanos (+51)
- ✅ Saldos no negativos
- ✅ Transacciones con cuentas válidas
- ✅ Préstamos con clientes asociados
- ✅ Fechas de vencimiento consistentes

### LP2 - Sistema RENIEC
- ✅ DNIs únicos y formato válido (8 dígitos)
- ✅ Fechas de nacimiento válidas
- ✅ Validadores con sesiones activas
- ✅ Auditoría completa de operaciones
- ✅ Trazabilidad de modificaciones
- ✅ Cumplimiento de niveles de acceso

### Integridad Cruzada
- ✅ Consistencia entre bases de datos
- ✅ Patrones de nombres similares
- ✅ Relación usuarios activos vs sesiones
- ✅ Verificación de integridad referencial

## 🚨 Alertas y Recomendaciones

### Alertas Críticas
- Tasa de éxito < 80%
- Tiempo de respuesta > 5s
- Pérdida de datos durante tests
- Fallas en recovery/backup

### Alertas de Atención
- Tasa de éxito 80-95%
- Tiempo de respuesta 2-5s
- Warnings en validaciones
- Uso de recursos elevado

### Recomendaciones Automáticas
- Optimización de índices
- Ajuste de timeouts
- Mejora de configuración de BD
- Procedimientos de backup

## 📅 Programación de Tests

### Configuración de Cron
```bash
# Tests diarios a las 2:00 AM
0 2 * * * cd /path/to/testing_system && python automation_test_suite.py --mode scheduled

# Tests de estrés cada 6 horas
0 */6 * * * cd /path/to/testing_system && python automation_test_suite.py --mode stress

# Validación de integridad semanal (domingos 3:00 AM)
0 3 * * 0 cd /path/to/testing_system && python automation_test_suite.py --mode integrity
```

### Configuración Programada
```json
{
    "scheduling": {
        "enable_scheduling": true,
        "daily_tests_time": "02:00",
        "weekly_tests_day": "sunday",
        "stress_tests_schedule": "0 */6 * * *",
        "integrity_tests_schedule": "0 3 * * 0"
    }
}
```

## 🔧 Solución de Problemas

### Errores Comunes

#### Error de Conexión a BD
```
❌ Error conectando a base de datos: Access denied
```
**Solución**: Verificar credenciales en configuración y que el usuario tenga permisos.

#### Timeout en Tests
```
⚠️ Hilo 7: Timeout excedido
```
**Solución**: Aumentar `timeout_seconds` en configuración o optimizar consultas.

#### Errores de Duplicados
```
Duplicate entry '12345678' for key 'dni'
```
**Solución**: Limpiar datos de prueba anteriores o usar datos únicos.

#### Memoria Insuficiente
```
MemoryError: Unable to allocate array
```
**Solución**: Reducir `concurrent_threads` o `target_records`.

### Logs de Debug

#### Habilitar Logging Detallado
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Archivos de Log
- `stress_test_lp1.log`: Logs específicos LP1
- `stress_test_lp2.log`: Logs específicos LP2  
- `data_integrity_validation.log`: Logs de validación
- `persistence_tests.log`: Logs de persistencia
- `automation_suite.log`: Logs de automatización

## 📊 Métricas de Performance Esperadas

### LP1 - Sistema Bancario
- **Throughput**: 100-200 ops/segundo
- **Latencia**: <500ms promedio
- **Éxito**: >95% operaciones exitosas
- **Concurrencia**: 50 hilos sin degradación

### LP2 - Sistema RENIEC
- **Throughput**: 80-150 consultas/segundo
- **Latencia**: <800ms promedio
- **Éxito**: >98% validaciones exitosas
- **Integridad**: 100% DNIs válidos

### Sistema Completo
- **Disponibilidad**: >99.5%
- **Recuperación**: <30 segundos
- **Backup**: <5 minutos
- **Restauración**: <10 minutos

## 🔒 Seguridad y Compliance

### Validaciones de Seguridad
- ✅ Sanitización de inputs
- ✅ Prevención de SQL injection
- ✅ Validación de formatos
- ✅ Logs de auditoría

### Compliance Normativo
- ✅ Trazabilidad de operaciones
- ✅ Integridad de datos
- ✅ Backup y recuperación
- ✅ Monitoreo continuo

## 📞 Soporte

Para soporte técnico o consultas:
1. Revisar logs en directorio `logs/`
2. Consultar archivos de reporte generados
3. Verificar configuración de base de datos
4. Contactar al equipo de desarrollo

## 📝 Changelog

### v1.0.0 (2025-10-30)
- ✅ Implementación completa de stress testing LP1/LP2
- ✅ Validación de integridad entre bases de datos
- ✅ Tests de persistencia y recuperación
- ✅ Generación automática de reportes HTML/JSON
- ✅ Suite de automatización completa
- ✅ Documentación detallada

---

**Sistema de Testing Automatizado v1.0.0**  
*Desarrollado para validación exhaustiva de sistemas distribuidos*
