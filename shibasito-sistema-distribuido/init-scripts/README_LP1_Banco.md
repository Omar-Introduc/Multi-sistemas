# Scripts de Inicialización SQL - Sistema Bancario LP1

Este directorio contiene los scripts SQL necesarios para inicializar la base de datos del Sistema Bancario LP1 con su esquema completo, datos de prueba e índices de optimización.

## Archivos Incluidos

### 1. `schema_lp1_banco.sql` (15.2 KB)
Define la estructura completa de la base de datos bancaria incluyendo:
- **Tablas principales:**
  - `clientes`: Información de clientes del banco
  - `cuentas`: Cuentas bancarias (ahorro, corriente, plazo fijo)
  - `transacciones`: Registro de todos los movimientos bancarios
  - `prestamos`: Préstamos otorgados a clientes
- **Características:**
  - Validaciones de integridad de datos
  - Claves foráneas con restricciones ON DELETE/UPDATE
  - Índices básicos para optimización
  - Vistas útiles para reportes
  - Configuraciones de MySQL para rendimiento

### 2. `seed_data_lp1.sql` (19.6 KB)
Datos de prueba para poblar el sistema:
- **10 clientes** (9 personas naturales + 1 empresa)
- **16 cuentas bancarias** distribuidas en diferentes tipos
- **22 transacciones** recientes con diferentes tipos de movimientos
- **12 préstamos** en diversos estados (activos, solicitados, vencidos)
- **Verificaciones** automáticas de datos insertados

### 3. `indexes_lp1.sql` (19.4 KB)
Índices avanzados para optimizar el rendimiento:
- **60+ índices adicionales** para consultas frecuentes
- **Índices compuestos** para consultas complejas
- **Índices de texto completo** para búsquedas avanzadas
- **Procedimientos** de mantenimiento automático
- **Vistas de monitoreo** de performance
- **Configuraciones optimizadas** de MySQL

## Configuración del Sistema

### Prerrequisitos
- MySQL 5.7+ o MariaDB 10.3+
- Permisos de administrador de base de datos
- Al menos 2GB de espacio disponible en disco

### Orden de Ejecución

Ejecutar los scripts **en el siguiente orden**:

```bash
# 1. Crear esquema y estructura
mysql -u root -p < schema_lp1_banco.sql

# 2. Cargar datos de prueba
mysql -u root -p < seed_data_lp1.sql

# 3. Crear índices de optimización
mysql -u root -p < indexes_lp1.sql
```

## Estructura de Tablas

### Tabla: clientes
| Campo | Tipo | Descripción |
|-------|------|-------------|
| cliente_id | INT | Clave primaria (auto-incremental) |
| numero_documento | VARCHAR(20) | DNI, RUC, etc. (único) |
| tipo_documento | ENUM | Tipo de documento |
| nombres/apellidos | VARCHAR(100) | Nombre completo |
| email/telefono | VARCHAR | Información de contacto |
| direccion | TEXT | Dirección completa |
| estado | ENUM | Estado del cliente |
| limite_credito | DECIMAL | Límite de crédito asignado |

### Tabla: cuentas
| Campo | Tipo | Descripción |
|-------|------|-------------|
| cuenta_id | INT | Clave primaria |
| numero_cuenta | VARCHAR(20) | Número único de cuenta |
| cliente_id | INT | Referencia a cliente |
| tipo_cuenta | ENUM | ahorro/corriente/plazo_fijo |
| saldo_actual | DECIMAL | Saldo disponible |
| estado | ENUM | Estado de la cuenta |

### Tabla: transacciones
| Campo | Tipo | Descripción |
|-------|------|-------------|
| transaccion_id | BIGINT | Clave primaria |
| cuenta_origen/destino | INT | Cuentas involucradas |
| tipo_transaccion | ENUM | depósito/retiro/transferencia/intereses |
| monto | DECIMAL | Cantidad de la transacción |
| estado | ENUM | Estado de la transacción |
| fecha_ejecucion | TIMESTAMP | Fecha y hora |

### Tabla: prestamos
| Campo | Tipo | Descripción |
|-------|------|-------------|
| prestamo_id | INT | Clave primaria |
| numero_prestamo | VARCHAR(20) | Número único |
| cliente_id | INT | Referencia a cliente |
| tipo_prestamo | ENUM | personal/vivienda/vehicular/etc. |
| monto_aprobado | DECIMAL | Monto aprobado |
| capital_pendiente | DECIMAL | Saldo pendiente |
| estado | ENUM | Estado del préstamo |

## Vistas Disponibles

### vista_resumen_clientes
Muestra un resumen completo de cada cliente incluyendo:
- Información personal
- Total de cuentas
- Saldo total acumulado
- Último movimiento

```sql
SELECT * FROM vista_resumen_clientes;
```

### vista_movimientos_recientes
Últimas transacciones realizadas con información detallada:
- Tipo de transacción
- Monto y moneda
- Cuentas involucradas
- Referencia y descripción

```sql
SELECT * FROM vista_movimientos_recientes LIMIT 50;
```

### vista_prestamos_activos
Préstamos activos con información de seguimiento:
- Información del préstamo y cliente
- Capital pendiente
- Progreso de pagos
- Porcentaje de deuda pendiente

```sql
SELECT * FROM vista_prestamos_activos ORDER BY fecha_vencimiento;
```

## Procedimientos de Mantenimiento

### Analizar Rendimiento de Tabla
```sql
CALL Analyze_Table_Performance('cuentas');
```

### Optimizar Todas las Tablas
```sql
CALL Optimize_All_Tables();
```

### Mantenimiento Mensual Completo
```sql
CALL Mantenimiento_Indices_Mensual();
```

## Monitoreo y Performance

### Ver Uso de Índices
```sql
SELECT * FROM vista_uso_indices;
```

### Estadísticas de Tablas
```sql
SELECT * FROM vista_estadisticas_tablas;
```

### Consultas Lentas (requiere slow query log)
```sql
SELECT * FROM vista_consultas_lentas;
```

## Datos de Prueba Incluidos

### Clientes de Ejemplo
1. **Carlos Alberto Mendoza Silva** - DNI: 12345678
2. **María Elena Rodríguez Pérez** - DNI: 87654321
3. **Empresa Peruana SA** - RUC: 20123456789
4. **José Luis García López** - DNI: 11223344
5. **Ana Patricia Vásquez Torres** - DNI: 55667788
6. **Roberto Carlos Fernández Silva** - DNI: 99887766 (Suspendido)
7. **Lucía Esperanza Morales Castro** - DNI: 33445566
8. **Fernando Miguel Espinoza Ramos** - DNI: 44556677
9. **Distribuidora Nacional EIRL** - RUC: 20987654321
10. **Patricia Isabel Herrera Mendez** - DNI: 77889900

### Tipos de Cuentas
- **Ahorro**: Con intereses bajos (0.1% - 0.15% anual)
- **Corriente**: Sin intereses, con sobregiros disponibles
- **Plazo Fijo**: Con intereses altos (4.5% anual)

### Transacciones de Ejemplo
- Depósitos en efectivo y cheques
- Retiros en cajeros automáticos
- Transferencias entre cuentas
- Abonos de intereses
- Pagos de comisiones

### Préstamos de Ejemplo
- **Préstamos Personales**: Tasas altas (14% - 22%)
- **Préstamos de Vivienda**: Tasas bajas (8.5% - 9.5%)
- **Préstamos Empresariales**: Tasas medias (12% - 16%)
- **Préstamos Vehiculares**: Tasas medias (11% - 13%)
- **Préstamos Estudiantiles**: Tasas preferenciales (8.5%)

## Configuraciones de Optimización

### Variables de MySQL Configuradas
```sql
innodb_buffer_pool_size = 1GB
innodb_log_file_size = 256MB
innodb_flush_log_at_trx_commit = 2
innodb_file_per_table = 1
query_cache_size = 64MB
tmp_table_size = 64MB
max_heap_table_size = 64MB
```

### Beneficios Esperados
- **Consultas 60-80% más rápidas**
- **Mejor rendimiento en reportes**
- **Optimización automática de JOINs**
- **Búsquedas de texto eficiente**
- **Mantenimiento automatizado**

## Casos de Uso Típicos

### Consulta de Saldo de Cliente
```sql
SELECT 
    CONCAT(c.nombres, ' ', c.apellidos) as cliente,
    cu.numero_cuenta,
    cu.tipo_cuenta,
    cu.saldo_actual
FROM clientes c
JOIN cuentas cu ON c.cliente_id = cu.cliente_id
WHERE c.numero_documento = '12345678'
  AND cu.estado = 'activa';
```

### Historial de Transacciones
```sql
SELECT 
    t.fecha_ejecucion,
    t.tipo_transaccion,
    t.monto,
    t.descripcion,
    t.referencia
FROM transacciones t
JOIN cuentas cu ON t.cuenta_origen = cu.cuenta_id
WHERE cu.numero_cuenta = '2001-000001-01-0100000001'
ORDER BY t.fecha_ejecucion DESC
LIMIT 10;
```

### Préstamos Próximos a Vencer
```sql
SELECT 
    p.numero_prestamo,
    CONCAT(c.nombres, ' ', c.apellidos) as cliente,
    p.fecha_vencimiento,
    p.capital_pendiente,
    p.cuota_mensual
FROM prestamos p
JOIN clientes c ON p.cliente_id = c.cliente_id
WHERE p.estado IN ('activo', 'desembolsado')
  AND p.fecha_vencimiento BETWEEN CURDATE() 
    AND DATE_ADD(CURDATE(), INTERVAL 60 DAY)
ORDER BY p.fecha_vencimiento;
```

## Mantenimiento Recomendado

### Diario
- Revisar transacciones fallidas
- Verificar saldos de cuentas críticas
- Monitorear alertas de seguridad

### Semanal
- Analizar performance de consultas lentas
- Revisar crecimiento de logs
- Verificar respaldos automáticos

### Mensual
- Ejecutar `CALL Mantenimiento_Indices_Mensual();`
- Revisar estadísticas de uso de índices
- Optimizar tablas según necesidad
- Analizar patrones de uso de la base de datos

### Trimestral
- Revisar y ajustar configuraciones de MySQL
- Evaluar necesidad de índices adicionales
- Actualizar documentación de consultas frecuentes
- Realizar pruebas de carga y rendimiento

## Solución de Problemas

### Error: "Table doesn't exist"
- Verificar que `schema_lp1_banco.sql` se ejecutó correctamente
- Confirmar que la base de datos `banco_lp1` fue creada

### Error: "Foreign key constraint fails"
- Verificar orden de ejecución de los scripts
- Confirmar que las tablas padre existen antes que las hija

### Consultas Lentas
- Ejecutar `ANALYZE TABLE` en las tablas afectadas
- Revisar si faltan índices necesarios
- Verificar configuraciones de MySQL

### Espacio en Disco
- Revisar `vista_estadisticas_tablas` para tamaño de tablas
- Ejecutar `OPTIMIZE TABLE` en tablas fragmentadas
- Considerar archiving de transacciones antiguas

## Contribución y Extensiones

Para agregar nuevas funcionalidades:

1. **Nuevas Tablas**: Seguir la convención de nombres y agregar validaciones
2. **Nuevos Índices**: Considerar patrones de consulta antes de crear
3. **Nuevas Vistas**: Documentar el propósito y casos de uso
4. **Procedimientos**: Incluir manejo de errores y logging

## Soporte

Para soporte técnico o preguntas:
- Revisar la documentación inline en cada script SQL
- Consultar las vistas de monitoreo para diagnóstico
- Ejecutar los procedimientos de mantenimiento para optimizar
- Verificar logs de MySQL para errores específicos

---

**Versión:** 1.0  
**Fecha:** 2025-10-30  
**Compatibilidad:** MySQL 5.7+, MariaDB 10.3+  
**Licencia:** Uso interno del proyecto LP1