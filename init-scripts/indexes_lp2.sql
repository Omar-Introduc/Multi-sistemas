-- =====================================================
-- ÍNDICES PARA OPTIMIZACIÓN DE CONSULTAS RENIEC LP2
-- Registro Nacional de Identificación y Estado Civil
-- =====================================================

USE reniec_lp2;

-- =====================================================
-- ÍNDICES PARA TABLA CIUDADANOS
-- =====================================================

-- Índice compuesto para búsquedas por nombre completo
CREATE INDEX idx_ciudadanos_nombre_completo ON ciudadanos (apellido_paterno, apellido_materno, nombre);

-- Índice para búsquedas por DNI con estado de verificación
CREATE INDEX idx_ciudadanos_dni_verificado ON ciudadanos (dni, es_verificado, activo);

-- Índice para filtros por ubicación geográfica
CREATE INDEX idx_ciudadanos_ubicacion ON ciudadanos (departamento, provincia, distrito, activo);

-- Índice para consultas de ciudadanos por rango de edad
CREATE INDEX idx_ciudadanos_fecha_nacimiento ON ciudadanos (fecha_nacimiento, activo);

-- Índice para búsqueda por estado civil y género
CREATE INDEX idx_ciudadanos_estado_genero ON ciudadanos (estado_civil, genero, activo);

-- Índice de texto completo para búsquedas avanzadas
CREATE INDEX idx_ciudadanos_busqueda_text ON ciudadanos (nombre, apellido_paterno, apellido_materno, lugar_nacimiento);

-- Índice para consultas de verificación masiva
CREATE INDEX idx_ciudadanos_verificacion_activos ON ciudadanos (es_verificado, fecha_verificacion, activo);

-- =====================================================
-- ÍNDICES PARA TABLA VALIDADORES
-- =====================================================

-- Índice para autenticación rápida
CREATE INDEX idx_validadores_usuario_activo ON validadores (usuario, activo, bloqueado);

-- Índice para búsqueda por oficina y nivel de acceso
CREATE INDEX idx_validadores_oficina_nivel ON validadores (oficina, nivel_acceso, activo);

-- Índice para estadísticas de acceso
CREATE INDEX idx_validadores_ultimo_acceso ON validadores (ultimo_acceso DESC, activo);

-- Índice para auditoría de intentos fallidos
CREATE INDEX idx_validadores_intentos_fallidos ON validadores (intentos_fallidos, bloqueado, fecha_bloqueo);

-- =====================================================
-- ÍNDICES PARA TABLA RENIEC_SESSIONS
-- =====================================================

-- Índice principal para búsqueda de sesiones activas
CREATE INDEX idx_sesiones_activas ON reniec_sessions (validador_id, activa, fecha_expiracion);

-- Índice para limpieza de sesiones expiradas
CREATE INDEX idx_sesiones_expiracion ON reniec_sessions (fecha_expiracion, activa);

-- Índice para análisis de patrones de uso
CREATE INDEX idx_sesiones_patrones_uso ON reniec_sessions (validador_id, fecha_inicio, operaciones_realizadas);

-- Índice para geolocalización de sesiones
CREATE INDEX idx_sesiones_ip_time ON reniec_sessions (ip_address, fecha_inicio);

-- Índice para estadísticas por agente de usuario
CREATE INDEX idx_sesiones_user_agent ON reniec_sessions (user_agent(100), fecha_inicio);

-- =====================================================
-- ÍNDICES PARA TABLA AUDITORIA
-- =====================================================

-- Índice principal para consultas de auditoría por fecha
CREATE INDEX idx_auditoria_fecha_accion ON auditoria (timestamp_operacion DESC, accion);

-- Índice para búsquedas por tabla y registro
CREATE INDEX idx_auditoria_tabla_registro ON auditoria (tabla_afectada, registro_id, timestamp_operacion DESC);

-- Índice para auditoría por validador
CREATE INDEX idx_auditoria_validador ON auditoria (validador_id, timestamp_operacion DESC);

-- Índice para búsquedas por IP y timestamp
CREATE INDEX idx_auditoria_ip_time ON auditoria (ip_address, timestamp_operacion DESC);

-- Índice para reportes de auditoría
CREATE INDEX idx_auditoria_completa ON auditoria (timestamp_operacion DESC, tabla_afectada, accion);

-- =====================================================
-- ÍNDICES PARA VISTAS OPTIMIZADAS
-- =====================================================

-- Índices para vista_ciudadanos_completa
CREATE INDEX idx_vista_ciudadanos_dni ON vista_ciudadanos_completa (dni);
CREATE INDEX idx_vista_ciudadanos_ubicacion ON vista_ciudadanos_completa (departamento, provincia, distrito);
CREATE INDEX idx_vista_ciudadanos_fecha_verificacion ON vista_ciudadanos_completa (es_verificado, fecha_verificacion);

-- Índices para vista_sesiones_activas
CREATE INDEX idx_vista_sesiones_validador ON vista_sesiones_activas (validador_id, minutos_activa);
CREATE INDEX idx_vista_sesiones_operaciones ON vista_sesiones_activas (operaciones_realizadas, fecha_ultimo_uso);

-- =====================================================
-- ÍNDICES ESPECIALIZADOS PARA CONSULTAS FRECUENTES
-- =====================================================

-- Consulta frecuente 1: Buscar ciudadano por DNI
-- Ya tiene idx_ciudadanos_dni_verificado

-- Consulta frecuente 2: Buscar ciudadanos por ubicación
CREATE INDEX idx_ciudadanos_filtro_geografico ON ciudadanos (departamento, provincia, distrito, activo, es_verificado);

-- Consulta frecuente 3: Listar ciudadanos por fecha de nacimiento
CREATE INDEX idx_ciudadanos_rango_edad ON ciudadanos (fecha_nacimiento, genero, activo);

-- Consulta frecuente 4: Validar sesiones activas
CREATE INDEX idx_sesiones_validacion ON reniec_sessions (token_sesion, activa, fecha_expiracion, fecha_ultimo_uso);

-- Consulta frecuente 5: Auditoría por rango de fechas
CREATE INDEX idx_auditoria_rango_fechas ON auditoria (timestamp_operacion, validador_id, accion);

-- =====================================================
-- ÍNDICES PARA ESTADÍSTICAS Y REPORTES
-- =====================================================

-- Estadísticas por departamento
CREATE INDEX idx_ciudadanos_stats_departamento ON ciudadanos (departamento, activo, es_verificado);

-- Estadísticas por oficina de validadores
CREATE INDEX idx_validadores_stats_oficina ON validadores (oficina, nivel_acceso, activo);

-- Estadísticas de uso del sistema
CREATE INDEX idx_sesiones_stats_uso ON reniec_sessions (fecha_inicio, validador_id, operaciones_realizadas);

-- Estadísticas de auditoría
CREATE INDEX idx_auditoria_stats_operaciones ON auditoria (accion, timestamp_operacion DESC, tabla_afectada);

-- =====================================================
-- ÍNDICES PARA OPTIMIZACIÓN DE JOINS
-- =====================================================

-- Join entre ciudadanos y sesiones a través de auditoría
CREATE INDEX idx_auditoria_join_ciudadanos ON auditoria (tabla_afectada, registro_id, timestamp_operacion DESC);

-- Join entre validadores y sesiones
CREATE INDEX idx_sesiones_join_validadores ON reniec_sessions (validador_id, activa, fecha_expiracion);

-- Join entre sesiones y auditoría
CREATE INDEX idx_auditoria_join_sesiones ON auditoria (session_id, timestamp_operacion DESC);

-- =====================================================
-- ÍNDICES PARA FUNCIONALIDADES AVANZADAS
-- =====================================================

-- Búsqueda fonética (para nombres similares)
CREATE INDEX idx_ciudadanos_busqueda_fonetica ON ciudadanos (apellido_paterno(10), apellido_materno(10), nombre(10));

-- Índice para deduplicación de ciudadanos
CREATE INDEX idx_ciudadanos_deduplicacion ON ciudadanos (nombre, apellido_paterno, apellido_materno, fecha_nacimiento);

-- Índice para análisis de tendencias
CREATE INDEX idx_ciudadanos_tendencias ON ciudadanos (fecha_creacion, activo, es_verificado);

-- =====================================================
-- PROCEDIMIENTOS PARA ANÁLISIS DE ÍNDICES
-- =====================================================

DELIMITER //

-- Procedimiento para analizar uso de índices
CREATE PROCEDURE analizar_uso_indices()
BEGIN
    -- Mostrar estadísticas de uso de índices
    SELECT 
        TABLE_NAME,
        INDEX_NAME,
        CARDINALITY,
        SUB_PART,
        NULL,
        INDEX_TYPE,
        COMMENT
    FROM information_schema.STATISTICS 
    WHERE TABLE_SCHEMA = 'reniec_lp2'
    ORDER BY TABLE_NAME, INDEX_NAME;
END //

-- Procedimiento para verificar consultas lentas
CREATE PROCEDURE verificar_consultas_lentas()
BEGIN
    -- Consultas que podrían beneficiarse de índices adicionales
    SELECT 
        'ciudadanos' AS tabla,
        COUNT(*) AS registros,
        'dni' AS campo_frecuente,
        'SIMPLE' AS tipo_consulta,
        'Alto' AS prioridad
    FROM ciudadanos
    WHERE dni IS NOT NULL
    
    UNION ALL
    
    SELECT 
        'reniec_sessions' AS tabla,
        COUNT(*) AS registros,
        'validador_id' AS campo_frecuente,
        'JOIN' AS tipo_consulta,
        'Alto' AS prioridad
    FROM reniec_sessions
    WHERE activa = TRUE;
END //

DELIMITER ;

-- =====================================================
-- MANTENIMIENTO DE ÍNDICES
-- =====================================================

-- Comando para optimizar tablas y índices
-- OPTIMIZE TABLE ciudadanos, validadores, reniec_sessions, auditoria;

-- Comando para analizar tablas
-- ANALYZE TABLE ciudadanos, validadores, reniec_sessions, auditoria;

-- =====================================================
-- CONSULTA DE VERIFICACIÓN DE ÍNDICES
-- =====================================================

-- Mostrar todos los índices creados
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    NON_UNIQUE,
    SEQ_IN_INDEX,
    COLUMN_NAME,
    CARDINALITY,
    SUB_PART,
    NULLABLE,
    INDEX_TYPE
FROM information_schema.STATISTICS 
WHERE TABLE_SCHEMA = 'reniec_lp2'
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;

-- Verificar índices por tabla
SELECT 'CIUDADANOS' AS tabla, COUNT(*) AS total_indices 
FROM information_schema.STATISTICS 
WHERE TABLE_SCHEMA = 'reniec_lp2' AND TABLE_NAME = 'ciudadanos'

UNION ALL

SELECT 'VALIDADORES' AS tabla, COUNT(*) AS total_indices 
FROM information_schema.STATISTICS 
WHERE TABLE_SCHEMA = 'reniec_lp2' AND TABLE_NAME = 'validadores'

UNION ALL

SELECT 'RENIEC_SESSIONS' AS tabla, COUNT(*) AS total_indices 
FROM information_schema.STATISTICS 
WHERE TABLE_SCHEMA = 'reniec_lp2' AND TABLE_NAME = 'reniec_sessions'

UNION ALL

SELECT 'AUDITORIA' AS tabla, COUNT(*) AS total_indices 
FROM information_schema.STATISTICS 
WHERE TABLE_SCHEMA = 'reniec_lp2' AND TABLE_NAME = 'auditoria';

-- =====================================================
-- RECOMENDACIONES DE MANTENIMIENTO
-- =====================================================

/*
RECOMENDACIONES DE MANTENIMIENTO:

1. OPTIMIZACIÓN REGULAR:
   - Ejecutar OPTIMIZE TABLE mensualmente
   - Actualizar estadísticas con ANALYZE TABLE semanalmente

2. MONITOREO:
   - Verificar uso de índices trimestralmente
   - Eliminar índices no utilizados

3. OPTIMIZACIÓN DE CONSULTAS:
   - Usar EXPLAIN para analizar consultas lentas
   - Ajustar índices según patrones de uso reales

4. CAPACIDAD:
   - Monitorear crecimiento de índices
   - Considerar particionado para tablas grandes

5. RENDIMIENTO:
   - Balancear número de índices vs velocidad de escritura
   - Priorizar índices para consultas más frecuentes

COMANDOS ÚTILES:
- SHOW INDEX FROM tabla;
- EXPLAIN SELECT * FROM tabla WHERE condicion;
- SHOW TABLE STATUS LIKE 'tabla';
*/

-- =====================================================
-- FIN DE ÍNDICES
-- =====================================================
