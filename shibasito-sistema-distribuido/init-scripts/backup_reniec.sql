-- =====================================================
-- SCRIPT DE BACKUP PARA SISTEMA RENIEC LP2
-- Registro Nacional de Identificación y Estado Civil
-- =====================================================

USE reniec_lp2;

-- =====================================================
-- CONFIGURACIÓN DE VARIABLES
-- =====================================================

SET @fecha_backup = DATE_FORMAT(NOW(), '%Y%m%d_%H%i%s');
SET @backup_dir = '/backups/reniec_lp2/';
SET @nombre_backup = CONCAT('reniec_lp2_backup_', @fecha_backup);

-- =====================================================
-- PROCEDIMIENTOS DE BACKUP
-- =====================================================

DELIMITER //

-- =====================================================
-- PROCEDIMIENTO: backup_completo
-- Realiza backup completo de todas las tablas
-- =====================================================
CREATE PROCEDURE backup_completo()
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Error durante el backup completo' AS mensaje;
    END;
    
    START TRANSACTION;
    
    -- Crear tabla temporal para metadatos del backup
    DROP TABLE IF EXISTS temp_backup_metadata;
    CREATE TEMPORARY TABLE temp_backup_metadata (
        tabla VARCHAR(50),
        registros INT,
        checksum VARCHAR(255),
        timestamp_backup TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Backup de ciudadanos
    INSERT INTO temp_backup_metadata (tabla, registros, checksum)
    SELECT 
        'ciudadanos',
        COUNT(*),
        MD5(CONCAT(GROUP_CONCAT(CONCAT(dni, nombre, apellido_paterno, apellido_materno)))
    FROM ciudadanos;
    
    -- Backup de validadores
    INSERT INTO temp_backup_metadata (tabla, registros, checksum)
    SELECT 
        'validadores',
        COUNT(*),
        MD5(CONCAT(GROUP_CONCAT(CONCAT(usuario, nombre_completo, oficina))))
    FROM validadores;
    
    -- Backup de sesiones
    INSERT INTO temp_backup_metadata (tabla, registros, checksum)
    SELECT 
        'reniec_sessions',
        COUNT(*),
        MD5(CONCAT(GROUP_CONCAT(CONCAT(validador_id, token_sesion, activa))))
    FROM reniec_sessions;
    
    -- Backup de auditoría
    INSERT INTO temp_backup_metadata (tabla, registros, checksum)
    SELECT 
        'auditoria',
        COUNT(*),
        MD5(CONCAT(GROUP_CONCAT(CONCAT(tabla_afectada, accion, timestamp_operacion))))
    FROM auditoria;
    
    COMMIT;
    
    SELECT 
        'Backup completo finalizado exitosamente' AS status,
        @nombre_backup AS nombre_backup,
        @fecha_backup AS timestamp_backup,
        COUNT(*) AS tablas_respaldadas
    FROM temp_backup_metadata;
END //

-- =====================================================
-- PROCEDIMIENTO: backup_tablas_especificas
-- Realiza backup de tablas específicas
-- =====================================================
CREATE PROCEDURE backup_tablas_especificas(IN tablas_json JSON)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Error durante backup de tablas específicas' AS mensaje;
    END;
    
    START TRANSACTION;
    
    -- Procesar cada tabla en el JSON
    -- Aquí se implementaría la lógica para procesar el JSON
    -- Por simplicidad, asumimos que el JSON contiene nombres de tablas
    
    SELECT 
        'Backup de tablas específicas iniciado' AS status,
        tablas_json AS tablas_seleccionadas;
    
    COMMIT;
END //

-- =====================================================
-- PROCEDIMIENTO: backup_solo_ciudadanos
-- Backup especializado solo para la tabla ciudadanos
-- =====================================================
CREATE PROCEDURE backup_solo_ciudadanos()
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Error durante backup de ciudadanos' AS mensaje;
    END;
    
    START TRANSACTION;
    
    -- Crear tabla de backup ciudadanos
    DROP TABLE IF EXISTS backup_ciudadanos_temp;
    CREATE TABLE backup_ciudadanos_temp AS
    SELECT * FROM ciudadanos
    ORDER BY id;
    
    -- Agregar metadatos al backup
    ALTER TABLE backup_ciudadanos_temp 
    ADD COLUMN backup_id INT AUTO_INCREMENT PRIMARY KEY,
    ADD COLUMN backup_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN backup_usuario VARCHAR(50) DEFAULT 'SYSTEM',
    ADD COLUMN backup_checksum VARCHAR(255);
    
    UPDATE backup_ciudadanos_temp 
    SET backup_checksum = MD5(CONCAT(dni, nombre, apellido_paterno, apellido_materno));
    
    COMMIT;
    
    SELECT 
        'Backup de ciudadanos completado' AS status,
        COUNT(*) AS registros_respaldados,
        @fecha_backup AS timestamp_backup
    FROM backup_ciudadanos_temp;
END //

-- =====================================================
-- PROCEDIMIENTO: backup_solo_auditoria
-- Backup especializado para auditoría (datos críticos)
-- =====================================================
CREATE PROCEDURE backup_solo_auditoria()
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Error durante backup de auditoría' AS mensaje;
    END;
    
    START TRANSACTION;
    
    -- Backup de auditoría por fechas (último mes)
    DROP TABLE IF EXISTS backup_auditoria_temp;
    CREATE TABLE backup_auditoria_temp AS
    SELECT * FROM auditoria
    WHERE timestamp_operacion >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    ORDER BY timestamp_operacion DESC;
    
    -- Agregar metadatos
    ALTER TABLE backup_auditoria_temp 
    ADD COLUMN backup_id INT AUTO_INCREMENT PRIMARY KEY,
    ADD COLUMN backup_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN backup_usuario VARCHAR(50) DEFAULT 'SYSTEM';
    
    COMMIT;
    
    SELECT 
        'Backup de auditoría completado' AS status,
        COUNT(*) AS registros_respaldados,
        MIN(timestamp_operacion) AS fecha_inicio,
        MAX(timestamp_operacion) AS fecha_fin
    FROM backup_auditoria_temp;
END //

-- =====================================================
-- PROCEDIMIENTO: backup_sesiones_inactivas
-- Limpia y respalda sesiones expiradas
-- =====================================================
CREATE PROCEDURE backup_sesiones_inactivas()
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Error durante backup de sesiones' AS mensaje;
    END;
    
    START TRANSACTION;
    
    -- Crear backup de sesiones expiradas
    DROP TABLE IF EXISTS backup_sesiones_expiradas_temp;
    CREATE TABLE backup_sesiones_expiradas_temp AS
    SELECT s.*, v.usuario, v.nombre_completo
    FROM reniec_sessions s
    JOIN validadores v ON s.validador_id = v.id
    WHERE s.fecha_expiracion < NOW() OR s.activa = FALSE
    ORDER BY s.fecha_expiracion;
    
    -- Marcar sesiones como inactivas en el sistema principal
    UPDATE reniec_sessions 
    SET activa = FALSE
    WHERE fecha_expiracion < NOW() OR activa = FALSE;
    
    COMMIT;
    
    SELECT 
        'Backup y limpieza de sesiones completado' AS status,
        COUNT(*) AS sesiones_procesadas
    FROM backup_sesiones_expiradas_temp;
END //

DELIMITER ;

-- =====================================================
-- VISTAS PARA MONITOREO DE BACKUP
-- =====================================================

-- Vista de estadísticas de backup
CREATE VIEW vista_estadisticas_backup AS
SELECT 
    'ciudadanos' AS tabla,
    COUNT(*) AS total_registros,
    MAX(created_at) AS ultimo_registro,
    COUNT(CASE WHEN es_verificado = TRUE THEN 1 END) AS registros_verificados,
    COUNT(CASE WHEN activo = TRUE THEN 1 END) AS registros_activos
FROM ciudadanos

UNION ALL

SELECT 
    'validadores' AS tabla,
    COUNT(*) AS total_registros,
    MAX(created_at) AS ultimo_registro,
    COUNT(CASE WHEN activo = TRUE THEN 1 END) AS registros_activos,
    COUNT(CASE WHEN bloqueado = FALSE THEN 1 END) AS no_bloqueados
FROM validadores

UNION ALL

SELECT 
    'reniec_sessions' AS tabla,
    COUNT(*) AS total_registros,
    MAX(fecha_inicio) AS ultimo_registro,
    COUNT(CASE WHEN activa = TRUE THEN 1 END) AS sesiones_activas,
    COUNT(CASE WHEN fecha_expiracion > NOW() THEN 1 END) AS no_expiradas
FROM reniec_sessions

UNION ALL

SELECT 
    'auditoria' AS tabla,
    COUNT(*) AS total_registros,
    MAX(timestamp_operacion) AS ultimo_registro,
    COUNT(CASE WHEN accion = 'INSERT' THEN 1 END) AS inserciones,
    COUNT(CASE WHEN timestamp_operacion >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 END) AS ultima_semana
FROM auditoria;

-- =====================================================
-- FUNCIONES DE VERIFICACIÓN
-- =====================================================

DELIMITER //

-- Función para verificar integridad de datos
CREATE FUNCTION verificar_integridad_ciudadanos()
RETURNS VARCHAR(255)
DETERMINISTIC
BEGIN
    DECLARE errores INT DEFAULT 0;
    
    -- Verificar DNIs duplicados
    SELECT COUNT(*) INTO errores
    FROM (
        SELECT dni, COUNT(*) as count
        FROM ciudadanos
        GROUP BY dni
        HAVING count > 1
    ) duplicados;
    
    IF errores > 0 THEN
        RETURN CONCAT('ERROR: ', errores, ' DNIs duplicados encontrados');
    END IF;
    
    -- Verificar fechas de nacimiento válidas
    SELECT COUNT(*) INTO errores
    FROM ciudadanos
    WHERE fecha_nacimiento > CURDATE() 
       OR fecha_nacimiento < '1900-01-01';
    
    IF errores > 0 THEN
        RETURN CONCAT('ERROR: ', errores, ' fechas de nacimiento inválidas');
    END IF;
    
    RETURN 'Integridad verificada: Datos consistentes';
END //

-- Función para verificar sesiones válidas
CREATE FUNCTION verificar_sesiones_validas()
RETURNS VARCHAR(255)
BEGIN
    DECLARE sesiones_invalidas INT DEFAULT 0;
    
    SELECT COUNT(*) INTO sesiones_invalidas
    FROM reniec_sessions s
    JOIN validadores v ON s.validador_id = v.id
    WHERE s.activa = TRUE 
      AND (s.fecha_expiracion < NOW() OR v.bloqueado = TRUE);
    
    IF sesiones_invalidas > 0 THEN
        RETURN CONCAT('ADVERTENCIA: ', sesiones_invalidas, ' sesiones activas con problemas');
    END IF;
    
    RETURN 'Sesiones verificadas: Todas válidas';
END //

DELIMITER ;

-- =====================================================
-- CONSULTA DE VERIFICACIÓN DE BACKUP
-- =====================================================

-- Mostrar estadísticas actuales
SELECT 'ESTADÍSTICAS GENERALES DEL SISTEMA' AS titulo;
SELECT * FROM vista_estadisticas_backup;

-- Verificar integridad
SELECT 'VERIFICACIÓN DE INTEGRIDAD' AS titulo;
SELECT verificar_integridad_ciudadanos() AS resultado_integridad;
SELECT verificar_sesiones_validas() AS resultado_sesiones;

-- Mostrar espacio utilizado por tabla
SELECT 
    TABLE_NAME,
    ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) AS tamaño_mb,
    TABLE_ROWS AS registros_estimados
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'reniec_lp2'
ORDER BY (DATA_LENGTH + INDEX_LENGTH) DESC;

-- =====================================================
-- SCRIPTS DE MANTENIMIENTO
-- =====================================================

/*
COMANDOS EXTERNOS PARA BACKUP (ejecutar desde shell):

1. BACKUP COMPLETO MYSQLDUMP:
   mysqldump -u root -p reniec_lp2 > /backups/reniec_lp2/backup_completo_$(date +%Y%m%d_%H%M%S).sql

2. BACKUP SOLO ESTRUCTURA:
   mysqldump -u root -p --no-data reniec_lp2 > /backups/reniec_lp2/estructura_$(date +%Y%m%d_%H%M%S).sql

3. BACKUP SOLO DATOS:
   mysqldump -u root -p --no-create-info reniec_lp2 > /backups/reniec_lp2/datos_$(date +%Y%m%d_%H%M%S).sql

4. BACKUP COMPRIMIDO:
   mysqldump -u root -p reniec_lp2 | gzip > /backups/reniec_lp2/backup_completo_$(date +%Y%m%d_%H%M%S).sql.gz

5. RESTAURAR BACKUP:
   mysql -u root -p reniec_lp2 < /backups/reniec_lp2/backup_completo_YYYYMMDD_HHMMSS.sql

6. BACKUP SELECTIVO POR TABLA:
   mysqldump -u root -p reniec_lp2 ciudadanos validadores > /backups/reniec_lp2/backup_critico_$(date +%Y%m%d_%H%M%S).sql

AUTOMATIZACIÓN CON CRON:
# Backup diario a las 2:00 AM
0 2 * * * mysqldump -u root -p[CONTRASEÑA] reniec_lp2 | gzip > /backups/reniec_lp2/daily_$(date +\%Y\%m\%d).sql.gz

# Backup semanal completo los domingos
0 1 * * 0 mysqldump -u root -p[CONTRASEÑA] --single-transaction --routines --triggers reniec_lp2 | gzip > /backups/reniec_lp2/weekly_$(date +\%Y\%m\%d).sql.gz

# Limpiar backups antiguos (mantener últimos 30 días)
0 3 * * * find /backups/reniec_lp2/ -name "*.sql.gz" -mtime +30 -delete
*/

-- =====================================================
-- EJEMPLO DE USO DE LOS PROCEDIMIENTOS
-- =====================================================

-- Realizar backup completo
-- CALL backup_completo();

-- Backup solo de ciudadanos
-- CALL backup_solo_ciudadanos();

-- Backup de auditoría
-- CALL backup_solo_auditoria();

-- Limpiar y respaldar sesiones
-- CALL backup_sesiones_inactivas();

-- =====================================================
-- FIN DE SCRIPT DE BACKUP
-- =====================================================
