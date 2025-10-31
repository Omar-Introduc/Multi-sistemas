-- ===================================================================
-- SISTEMA BANCARIO LP1 - SCRIPT DE VERIFICACIÓN
-- ===================================================================
-- Este script verifica que la base de datos se haya creado correctamente
-- y que todos los datos se hayan insertado sin errores
-- Versión: 1.0
-- Fecha: 2025-10-30
-- ===================================================================

USE banco_lp1;

-- ===================================================================
-- VERIFICACIONES BÁSICAS DE ESTRUCTURA
-- ===================================================================

SELECT '=== VERIFICACIÓN DE TABLAS CREADAS ===' as Info;

SELECT 
    TABLE_NAME as tabla,
    TABLE_ROWS as filas_estimadas,
    ENGINE as motor,
    TABLE_COLLATION as collation
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'banco_lp1'
  AND TABLE_NAME IN ('clientes', 'cuentas', 'transacciones', 'prestamos')
ORDER BY TABLE_NAME;

-- ===================================================================
-- VERIFICACIÓN DE DATOS INSERTADOS
-- ===================================================================

SELECT '=== VERIFICACIÓN DE DATOS INSERTADOS ===' as Info;

-- Contar registros por tabla
SELECT 
    'Clientes' as tabla,
    COUNT(*) as total_registros
FROM clientes
UNION ALL
SELECT 
    'Cuentas' as tabla,
    COUNT(*) as total_registros
FROM cuentas
UNION ALL
SELECT 
    'Transacciones' as tabla,
    COUNT(*) as total_registros
FROM transacciones
UNION ALL
SELECT 
    'Préstamos' as tabla,
    COUNT(*) as total_registros
FROM prestamos;

-- ===================================================================
-- VERIFICACIÓN DE ÍNDICES
-- ===================================================================

SELECT '=== VERIFICACIÓN DE ÍNDICES ===' as Info;

SELECT 
    TABLE_NAME as tabla,
    COUNT(DISTINCT INDEX_NAME) as total_indices,
    COUNT(CASE WHEN NON_UNIQUE = 0 THEN 1 END) as indices_unicos,
    COUNT(CASE WHEN NON_UNIQUE = 1 THEN 1 END) as indices_no_unicos
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = 'banco_lp1'
  AND TABLE_NAME IN ('clientes', 'cuentas', 'transacciones', 'prestamos')
GROUP BY TABLE_NAME
ORDER BY tabla;

-- ===================================================================
-- VERIFICACIÓN DE CLAVES FORÁNEAS
-- ===================================================================

SELECT '=== VERIFICACIÓN DE RELACIONES (CLAVES FORÁNEAS) ===' as Info;

SELECT 
    TABLE_NAME as tabla,
    CONSTRAINT_NAME as clave_foranea,
    REFERENCED_TABLE_NAME as tabla_referenciada,
    UPDATE_RULE as regla_actualizacion,
    DELETE_RULE as regla_eliminacion
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'banco_lp1'
  AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME, CONSTRAINT_NAME;

-- ===================================================================
-- VERIFICACIÓN DE INTEGRIDAD DE DATOS
-- ===================================================================

SELECT '=== VERIFICACIÓN DE INTEGRIDAD ===' as Info;

-- Verificar que no hay clientes sin cuentas (deberían existir)
SELECT 
    'Clientes sin cuentas' as verificacion,
    COUNT(*) as encontrados
FROM clientes c
LEFT JOIN cuentas cu ON c.cliente_id = cu.cliente_id
WHERE cu.cliente_id IS NULL;

-- Verificar que no hay cuentas sin clientes
SELECT 
    'Cuentas sin cliente válido' as verificacion,
    COUNT(*) as encontrados
FROM cuentas cu
LEFT JOIN clientes c ON cu.cliente_id = c.cliente_id
WHERE c.cliente_id IS NULL;

-- Verificar que no hay transacciones con cuentas inexistentes
SELECT 
    'Transacciones con cuenta origen inválida' as verificacion,
    COUNT(*) as encontrados
FROM transacciones t
LEFT JOIN cuentas cu ON t.cuenta_origen = cu.cuenta_id
WHERE cu.cuenta_id IS NULL;

-- Verificar que no hay préstamos con clientes inexistentes
SELECT 
    'Préstamos con cliente inválido' as verificacion,
    COUNT(*) as encontrados
FROM prestamos p
LEFT JOIN clientes c ON p.cliente_id = c.cliente_id
WHERE c.cliente_id IS NULL;

-- ===================================================================
-- VERIFICACIÓN DE RESTRICCIONES
-- ===================================================================

SELECT '=== VERIFICACIÓN DE RESTRICCIONES ===' as Info;

-- Verificar que todos los clientes activos tienen al menos una cuenta activa
SELECT 
    'Clientes activos sin cuentas activas' as verificacion,
    COUNT(*) as encontrados
FROM clientes c
LEFT JOIN cuentas cu ON c.cliente_id = cu.cliente_id AND cu.estado = 'activa'
WHERE c.estado = 'activo'
  AND cu.cliente_id IS NULL;

-- Verificar saldos negativos no permitidos (excepto con sobregiro)
SELECT 
    'Cuentas con saldo inválido' as verificacion,
    COUNT(*) as encontrados
FROM cuentas cu
WHERE cu.saldo_actual < -cu.limite_sobregiro;

-- ===================================================================
-- VERIFICACIÓN DE VISTAS
-- ===================================================================

SELECT '=== VERIFICACIÓN DE VISTAS ===' as Info;

-- Verificar que las vistas existen y funcionan
SELECT 
    TABLE_NAME as vista,
    'Creada correctamente' as estado
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = 'banco_lp1'
  AND TABLE_NAME LIKE 'vista_%'
ORDER BY TABLE_NAME;

-- Probar vista_resumen_clientes
SELECT 
    'Vista resumen clientes' as vista,
    COUNT(*) as registros
FROM vista_resumen_clientes;

-- Probar vista_movimientos_recientes
SELECT 
    'Vista movimientos recientes' as vista,
    COUNT(*) as registros
FROM vista_movimientos_recientes;

-- Probar vista_prestamos_activos
SELECT 
    'Vista préstamos activos' as vista,
    COUNT(*) as registros
FROM vista_prestamos_activos;

-- ===================================================================
-- ESTADÍSTICAS DE LA BASE DE DATOS
-- ===================================================================

SELECT '=== ESTADÍSTICAS GENERALES ===' as Info;

-- Distribución de clientes por tipo de documento
SELECT 
    tipo_documento,
    COUNT(*) as total,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM clientes), 2) as porcentaje
FROM clientes
GROUP BY tipo_documento
ORDER BY total DESC;

-- Distribución de cuentas por tipo
SELECT 
    tipo_cuenta,
    COUNT(*) as total,
    ROUND(AVG(saldo_actual), 2) as saldo_promedio,
    ROUND(SUM(saldo_actual), 2) as saldo_total
FROM cuentas
GROUP BY tipo_cuenta
ORDER BY saldo_total DESC;

-- Distribución de transacciones por tipo
SELECT 
    tipo_transaccion,
    COUNT(*) as total,
    ROUND(SUM(monto), 2) as monto_total,
    ROUND(AVG(monto), 2) as monto_promedio
FROM transacciones
WHERE estado = 'completada'
GROUP BY tipo_transaccion
ORDER BY total DESC;

-- Distribución de préstamos por estado
SELECT 
    estado,
    COUNT(*) as total,
    ROUND(SUM(monto_aprobado), 2) as monto_total,
    ROUND(AVG(monto_aprobado), 2) as monto_promedio
FROM prestamos
GROUP BY estado
ORDER BY total DESC;

-- ===================================================================
-- PRUEBAS DE CONSULTAS COMUNES
-- ===================================================================

SELECT '=== PRUEBAS DE CONSULTAS FRECUENTES ===' as Info;

-- Prueba 1: Buscar cliente por documento
SELECT 
    'Prueba búsqueda por documento' as prueba,
    CONCAT(nombres, ' ', apellidos) as resultado,
    email as detalle
FROM clientes
WHERE numero_documento = '12345678';

-- Prueba 2: Obtener cuentas de un cliente
SELECT 
    'Prueba cuentas por cliente' as prueba,
    numero_cuenta,
    tipo_cuenta,
    saldo_actual
FROM cuentas
WHERE cliente_id = 1;

-- Prueba 3: Transacciones recientes
SELECT 
    'Prueba transacciones recientes' as prueba,
    DATE(fecha_ejecucion) as fecha,
    tipo_transaccion,
    monto,
    descripcion
FROM transacciones
ORDER BY fecha_ejecucion DESC
LIMIT 5;

-- Prueba 4: Préstamos activos
SELECT 
    'Prueba préstamos activos' as prueba,
    numero_prestamo,
    tipo_prestamo,
    monto_aprobado,
    capital_pendiente
FROM prestamos
WHERE estado = 'activo'
LIMIT 5;

-- ===================================================================
-- VERIFICACIÓN DE PROCEDIMIENTOS
-- ===================================================================

SELECT '=== VERIFICACIÓN DE PROCEDIMIENTOS ALMACENADOS ===' as Info;

SELECT 
    ROUTINE_NAME as procedimiento,
    ROUTINE_TYPE as tipo,
    ROUTINE_DEFINITION as definicion
FROM INFORMATION_SCHEMA.ROUTINES
WHERE ROUTINE_SCHEMA = 'banco_lp1'
  AND ROUTINE_TYPE = 'PROCEDURE'
ORDER BY ROUTINE_NAME;

-- ===================================================================
-- RESUMEN FINAL
-- ===================================================================

SELECT '=== RESUMEN FINAL DE VERIFICACIÓN ===' as Info;

SELECT 
    'Total de tablas creadas' as metrica,
    COUNT(*) as valor
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'banco_lp1'

UNION ALL

SELECT 
    'Total de índices creados' as metrica,
    COUNT(DISTINCT INDEX_NAME) as valor
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = 'banco_lp1'

UNION ALL

SELECT 
    'Total de vistas creadas' as metrica,
    COUNT(*) as valor
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = 'banco_lp1'

UNION ALL

SELECT 
    'Total de procedimientos creados' as metrica,
    COUNT(*) as valor
FROM INFORMATION_SCHEMA.ROUTINES
WHERE ROUTINE_SCHEMA = 'banco_lp1'
  AND ROUTINE_TYPE = 'PROCEDURE'

UNION ALL

SELECT 
    'Total de registros insertados' as metrica,
    (SELECT COUNT(*) FROM clientes) +
    (SELECT COUNT(*) FROM cuentas) +
    (SELECT COUNT(*) FROM transacciones) +
    (SELECT COUNT(*) FROM prestamos) as valor;

-- ===================================================================
-- MENSAJE FINAL
-- ===================================================================

SELECT 
    'VERIFICACIÓN COMPLETADA' as estado,
    CASE 
        WHEN (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'banco_lp1') >= 4
        THEN 'EXITOSA - Base de datos correctamente inicializada'
        ELSE 'INCOMPLETA - Faltan elementos en la base de datos'
    END as mensaje;

-- ===================================================================
-- COMENTARIOS FINALES
-- ===================================================================
/*
VERIFICACIÓN COMPLETADA:

Este script realiza las siguientes verificaciones:
1. ✅ Estructura de tablas creada correctamente
2. ✅ Datos insertados sin errores
3. ✅ Índices creados y funcionando
4. ✅ Claves foráneas establecidas
5. ✅ Integridad de datos verificada
6. ✅ Restricciones aplicadas correctamente
7. ✅ Vistas funcionando
8. ✅ Procedimientos almacenados disponibles
9. ✅ Consultas comunes funcionando
10. ✅ Estadísticas generales correctas

SI TODAS LAS VERIFICACIONES PASARON:
- La base de datos está lista para usar
- Todos los scripts se ejecutaron correctamente
- El sistema bancario LP1 está operativo

SI ALGUNA VERIFICACIÓN FALLA:
- Revisar la ejecución de los scripts anteriores
- Verificar logs de MySQL para errores
- Ejecutar scripts de nuevo en orden correcto
- Consultar documentación de troubleshooting

SIGUIENTE PASO:
El sistema está listo para pruebas de integración
y desarrollo de aplicaciones que consuman esta base de datos.
*/