-- Script de configuración de base de datos para el sistema de validación RENIEC
-- Versión: 1.0.0
-- Fecha: 2024-10-30

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS reniec_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE reniec_db;

-- ===========================================
-- TABLA: ciudadanos
-- ===========================================
-- Almacena los datos de los ciudadanos peruanos registrados en RENIEC

CREATE TABLE IF NOT EXISTS ciudadanos (
    numero_documento VARCHAR(8) PRIMARY KEY COMMENT 'Número de DNI (8 dígitos)',
    nombres VARCHAR(100) NOT NULL COMMENT 'Nombres del ciudadano',
    apellido_paterno VARCHAR(100) NOT NULL COMMENT 'Apellido paterno',
    apellido_materno VARCHAR(100) NOT NULL COMMENT 'Apellido materno',
    fecha_nacimiento DATE COMMENT 'Fecha de nacimiento',
    estado_civil VARCHAR(50) COMMENT 'Estado civil (soltero, casado, divorciado, viudo)',
    direccion TEXT COMMENT 'Dirección completa',
    distrito VARCHAR(100) COMMENT 'Distrito',
    provincia VARCHAR(100) COMMENT 'Provincia',
    departamento VARCHAR(100) COMMENT 'Departamento/Región',
    activo BOOLEAN DEFAULT TRUE COMMENT 'Indica si el registro está activo',
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creación del registro',
    actualizado_en DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Última actualización',
    
    INDEX idx_nombres (nombres),
    INDEX idx_apellidos (apellido_paterno, apellido_materno),
    INDEX idx_distrito (distrito),
    INDEX idx_provincia (provincia),
    INDEX idx_departamento (departamento),
    INDEX idx_activo (activo),
    
    CONSTRAINT chk_numero_documento CHECK (numero_documento REGEXP '^[0-9]{8}$')
) ENGINE=InnoDB COMMENT='Tabla de ciudadanos registrados en RENIEC';

-- ===========================================
-- TABLA: sesiones_validacion
-- ===========================================
-- Registra las sesiones de validación de identidad

CREATE TABLE IF NOT EXISTS sesiones_validacion (
    id_solicitud VARCHAR(64) PRIMARY KEY COMMENT 'ID único de la solicitud de validación',
    numero_dni VARCHAR(8) NOT NULL COMMENT 'Número de DNI validado',
    fecha_validacion DATETIME NOT NULL COMMENT 'Fecha y hora de la validación',
    fecha_expiracion DATETIME NOT NULL COMMENT 'Fecha y hora de expiración de la sesión',
    estado VARCHAR(20) NOT NULL COMMENT 'Estado: pendiente, validando, exitosa, fallida, expirada',
    id_banco VARCHAR(50) COMMENT 'Identificador del banco que solicitó la validación',
    intentos_validacion INT DEFAULT 0 COMMENT 'Número de intentos de validación',
    mensaje_error TEXT COMMENT 'Mensaje de error en caso de fallo',
    score_confianza DECIMAL(3,2) COMMENT 'Score de confianza de la validación (0.00-1.00)',
    datos_validacion JSON COMMENT 'Datos adicionales de la validación',
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creación',
    
    INDEX idx_numero_dni (numero_dni),
    INDEX idx_estado (estado),
    INDEX idx_fecha_validacion (fecha_validacion),
    INDEX idx_fecha_expiracion (fecha_expiracion),
    INDEX idx_banco (id_banco),
    INDEX idx_fecha_banco (fecha_validacion, id_banco),
    
    FOREIGN KEY (numero_dni) REFERENCES ciudadanos(numero_documento) ON DELETE RESTRICT ON UPDATE CASCADE,
    
    CONSTRAINT chk_estado CHECK (estado IN ('pendiente', 'validando', 'exitosa', 'fallida', 'expirada')),
    CONSTRAINT chk_score_confianza CHECK (score_confianza IS NULL OR (score_confianza >= 0 AND score_confianza <= 1))
) ENGINE=InnoDB COMMENT='Sesiones de validación de identidad';

-- ===========================================
-- TABLA: auditoria_eventos
-- ===========================================
-- Registra todos los eventos del sistema para auditoría

CREATE TABLE IF NOT EXISTS auditoria_eventos (
    evento_id VARCHAR(64) PRIMARY KEY COMMENT 'ID único del evento',
    tipo_evento VARCHAR(100) NOT NULL COMMENT 'Tipo de evento (VALIDACION_INICIADA, etc.)',
    timestamp DATETIME NOT NULL COMMENT 'Fecha y hora del evento',
    usuario VARCHAR(100) COMMENT 'Usuario que realizó la acción',
    ip_origen VARCHAR(45) COMMENT 'Dirección IP de origen',
    datos_evento JSON COMMENT 'Datos adicionales del evento en formato JSON',
    session_id VARCHAR(64) COMMENT 'ID de sesión asociado',
    resultado VARCHAR(20) COMMENT 'Resultado: exito, fallo, error',
    duracion_ms INT COMMENT 'Duración en milisegundos',
    hash_integridad VARCHAR(64) COMMENT 'Hash para verificar integridad',
    
    INDEX idx_tipo_evento (tipo_evento),
    INDEX idx_timestamp (timestamp),
    INDEX idx_usuario (usuario),
    INDEX idx_session (session_id),
    INDEX idx_resultado (resultado),
    INDEX idx_timestamp_tipo (timestamp, tipo_evento)
) ENGINE=InnoDB COMMENT='Auditoría de eventos del sistema';

-- ===========================================
-- TABLA: auditoria_errores
-- ===========================================
-- Registra todos los errores del sistema

CREATE TABLE IF NOT EXISTS auditoria_errores (
    error_id VARCHAR(64) PRIMARY KEY COMMENT 'ID único del error',
    tipo_error VARCHAR(100) NOT NULL COMMENT 'Tipo de error (ERROR_DB, etc.)',
    mensaje TEXT COMMENT 'Descripción del error',
    stack_trace LONGTEXT COMMENT 'Stack trace completo del error',
    timestamp DATETIME NOT NULL COMMENT 'Fecha y hora del error',
    contexto JSON COMMENT 'Contexto adicional del error en JSON',
    severidad VARCHAR(20) COMMENT 'Severidad: WARNING, ERROR, CRITICAL',
    resuelto BOOLEAN DEFAULT FALSE COMMENT 'Indica si el error fue resuelto',
    evento_id VARCHAR(64) COMMENT 'ID del evento relacionado (si aplica)',
    
    INDEX idx_tipo_error (tipo_error),
    INDEX idx_timestamp (timestamp),
    INDEX idx_severidad (severidad),
    INDEX idx_resuelto (resuelto),
    INDEX idx_timestamp_severidad (timestamp, severidad),
    
    CONSTRAINT chk_severidad CHECK (severidad IN ('WARNING', 'ERROR', 'CRITICAL'))
) ENGINE=InnoDB COMMENT='Auditoría de errores del sistema';

-- ===========================================
-- TABLA: auditoria_metricas
-- ===========================================
-- Registra métricas y estadísticas del sistema

CREATE TABLE IF NOT EXISTS auditoria_metricas (
    metrica_id VARCHAR(64) PRIMARY KEY COMMENT 'ID único de la métrica',
    timestamp DATETIME NOT NULL COMMENT 'Fecha y hora de la métrica',
    nombre_metrica VARCHAR(100) NOT NULL COMMENT 'Nombre de la métrica',
    valor DECIMAL(15,6) COMMENT 'Valor numérico de la métrica',
    unidad VARCHAR(20) COMMENT 'Unidad de medida (count, ms, bytes, etc.)',
    etiquetas JSON COMMENT 'Etiquetas adicionales en JSON',
    
    INDEX idx_nombre_metrica (nombre_metrica),
    INDEX idx_timestamp (timestamp),
    INDEX idx_timestamp_metrica (timestamp, nombre_metrica)
) ENGINE=InnoDB COMMENT='Métricas del sistema';

-- ===========================================
-- TABLA: configuracion_sistema
-- ===========================================
-- Configuraciones del sistema

CREATE TABLE IF NOT EXISTS configuracion_sistema (
    clave VARCHAR(100) PRIMARY KEY COMMENT 'Clave de configuración',
    valor TEXT NOT NULL COMMENT 'Valor de configuración',
    descripcion TEXT COMMENT 'Descripción de la configuración',
    tipo VARCHAR(20) DEFAULT 'string' COMMENT 'Tipo: string, integer, float, boolean, json',
    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    modificado_por VARCHAR(100) COMMENT 'Usuario que modificó',
    
    INDEX idx_tipo (tipo)
) ENGINE=InnoDB COMMENT='Configuraciones del sistema';

-- ===========================================
-- TABLA: bancos_registrados
-- ===========================================
-- Bancos autorizados para solicitar validaciones

CREATE TABLE IF NOT EXISTS bancos_registrados (
    id_banco VARCHAR(50) PRIMARY KEY COMMENT 'Identificador único del banco',
    nombre_banco VARCHAR(200) NOT NULL COMMENT 'Nombre completo del banco',
    activo BOOLEAN DEFAULT TRUE COMMENT 'Indica si el banco está activo',
    configuracion JSON COMMENT 'Configuración específica del banco',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso DATETIME COMMENT 'Último acceso al sistema',
    total_solicitudes INT DEFAULT 0 COMMENT 'Total de solicitudes realizadas',
    
    INDEX idx_nombre_banco (nombre_banco),
    INDEX idx_activo (activo),
    INDEX idx_ultimo_acceso (ultimo_acceso)
) ENGINE=InnoDB COMMENT='Bancos autorizados';

-- ===========================================
-- INSERTAR DATOS DE EJEMPLO
-- ===========================================

-- Insertar configuraciones por defecto
INSERT INTO configuracion_sistema (clave, valor, descripcion, tipo) VALUES
('tiempo_expiracion_session', '24', 'Tiempo de expiración de sesión en horas', 'integer'),
('max_intentos_validacion', '3', 'Número máximo de intentos de validación', 'integer'),
('score_minimo_validacion', '0.8', 'Score mínimo de confianza para validación exitosa', 'float'),
('enable_audit_db', 'true', 'Habilitar auditoría en base de datos', 'boolean'),
('max_log_size', '52428800', 'Tamaño máximo de archivo de log en bytes', 'integer');

-- Insertar bancos de ejemplo
INSERT INTO bancos_registrados (id_banco, nombre_banco, configuracion) VALUES
('BANCO_001', 'Banco de la Nación', '{"routing_key_pattern": "validacion.banco.{banco_id}", "prioridad": 5}'),
('BANCO_002', 'Banco de Crédito del Perú', '{"routing_key_pattern": "validacion.banco.{banco_id}", "prioridad": 5}'),
('BANCO_003', 'Interbank', '{"routing_key_pattern": "validacion.banco.{banco_id}", "prioridad": 4}');

-- Insertar ciudadanos de ejemplo
INSERT INTO ciudadanos (numero_documento, nombres, apellido_paterno, apellido_materno, fecha_nacimiento, estado_civil, direccion, distrito, provincia, departamento) VALUES
('12345678', 'JUAN CARLOS', 'PEREZ', 'GARCIA', '1985-03-15', 'casado', 'Av. Principal 123', 'LIMA', 'LIMA', 'LIMA'),
('23456789', 'MARIA ELENA', 'RODRIGUEZ', 'LOPEZ', '1990-07-22', 'soltero', 'Calle Secundaria 456', 'MIRAFLORES', 'LIMA', 'LIMA'),
('34567890', 'CARLOS ALBERTO', 'GOMEZ', 'VARGAS', '1978-11-10', 'casado', 'Jr. Los Olivos 789', 'SAN ISIDRO', 'LIMA', 'LIMA'),
('45678901', 'ANA LUCIA', 'MENDOZA', 'TORRES', '1992-01-05', 'soltero', 'Av. Universitaria 321', 'LA VICTORIA', 'LIMA', 'LIMA'),
('56789012', 'PEDRO ANTONIO', 'JIMENEZ', 'HERRERA', '1987-09-18', 'divorciado', 'Calle Los Pinos 654', 'SURCO', 'LIMA', 'LIMA');

-- ===========================================
-- PROCEDIMIENTOS ALMACENADOS
-- ===========================================

DELIMITER //

-- Procedimiento para validar identidad
CREATE PROCEDURE IF NOT EXISTS sp_validar_identidad(
    IN p_numero_dni VARCHAR(8),
    IN p_nombres VARCHAR(100),
    IN p_apellido_paterno VARCHAR(100),
    IN p_apellido_materno VARCHAR(100),
    IN p_id_solicitud VARCHAR(64),
    IN p_id_banco VARCHAR(50)
)
BEGIN
    DECLARE v_existe_ciudadano BOOLEAN DEFAULT FALSE;
    DECLARE v_score_confianza DECIMAL(3,2) DEFAULT 0.0;
    DECLARE v_estado VARCHAR(20) DEFAULT 'fallida';
    DECLARE v_mensaje TEXT DEFAULT 'Validación fallida';
    
    -- Verificar si existe el ciudadano
    SELECT EXISTS(
        SELECT 1 FROM ciudadanos 
        WHERE numero_documento = p_numero_dni AND activo = 1
    ) INTO v_existe_ciudadano;
    
    IF v_existe_ciudadano THEN
        -- Calcular score de confianza (simplificado)
        SET v_score_confianza = 0.85;
        
        IF v_score_confianza >= 0.8 THEN
            SET v_estado = 'exitosa';
            SET v_mensaje = 'Validación exitosa';
        ELSE
            SET v_estado = 'fallida';
            SET v_mensaje = CONCAT('Score insuficiente: ', v_score_confianza);
        END IF;
    ELSE
        SET v_mensaje = 'Ciudadano no encontrado';
    END IF;
    
    -- Registrar sesión
    INSERT INTO sesiones_validacion (
        id_solicitud, numero_dni, fecha_validacion, fecha_expiracion,
        estado, id_banco, score_confianza, mensaje_error
    ) VALUES (
        p_id_solicitud, p_numero_dni, NOW(), DATE_ADD(NOW(), INTERVAL 24 HOUR),
        v_estado, p_banco, v_score_confianza, 
        CASE WHEN v_estado = 'fallida' THEN v_mensaje ELSE NULL END
    );
    
    -- Retornar resultado
    SELECT 
        p_id_solicitud as id_solicitud,
        v_estado as estado,
        v_mensaje as mensaje,
        v_score_confianza as score_confianza,
        v_existe_ciudadano as existe_ciudadano;
        
END //

-- Procedimiento para obtener estadísticas
CREATE PROCEDURE IF NOT EXISTS sp_obtener_estadisticas(
    IN p_fecha_desde DATETIME,
    IN p_fecha_hasta DATETIME
)
BEGIN
    SELECT 
        'validaciones_totales' as metrica,
        COUNT(*) as valor,
        'count' as unidad
    FROM sesiones_validacion 
    WHERE fecha_validacion BETWEEN p_fecha_desde AND p_fecha_hasta
    
    UNION ALL
    
    SELECT 
        'validaciones_exitosas' as metrica,
        COUNT(*) as valor,
        'count' as unidad
    FROM sesiones_validacion 
    WHERE fecha_validacion BETWEEN p_fecha_desde AND p_fecha_hasta
    AND estado = 'exitosa'
    
    UNION ALL
    
    SELECT 
        'validaciones_fallidas' as metrica,
        COUNT(*) as valor,
        'count' as unidad
    FROM sesiones_validacion 
    WHERE fecha_validacion BETWEEN p_fecha_desde AND p_fecha_hasta
    AND estado = 'fallida'
    
    UNION ALL
    
    SELECT 
        'bancos_activos' as metrica,
        COUNT(DISTINCT id_banco) as valor,
        'count' as unidad
    FROM sesiones_validacion 
    WHERE fecha_validacion BETWEEN p_fecha_desde AND p_fecha_hasta
    AND id_banco IS NOT NULL;
    
END //

-- Procedimiento para limpiar sesiones expiradas
CREATE PROCEDURE IF NOT EXISTS sp_limpiar_sesiones_expiradas()
BEGIN
    DECLARE v_registros_actualizados INT DEFAULT 0;
    
    UPDATE sesiones_validacion 
    SET estado = 'expirada'
    WHERE fecha_expiracion < NOW() 
    AND estado = 'exitosa';
    
    SET v_registros_actualizados = ROW_COUNT();
    
    -- Log del procedimiento
    INSERT INTO auditoria_eventos (
        evento_id, tipo_evento, timestamp, datos_evento, resultado
    ) VALUES (
        UUID(), 'SESSIONES_LIMPIADAS', NOW(),
        JSON_OBJECT('registros_actualizados', v_registros_actualizados),
        'exito'
    );
    
    SELECT v_registros_actualizados as registros_limpiados;
    
END //

DELIMITER ;

-- ===========================================
-- VISTAS ÚTILES
-- ===========================================

-- Vista de resumen de validaciones por banco
CREATE OR REPLACE VIEW v_resumen_validaciones_banco AS
SELECT 
    id_banco,
    nombre_banco,
    COUNT(*) as total_solicitudes,
    SUM(CASE WHEN sv.estado = 'exitosa' THEN 1 ELSE 0 END) as validaciones_exitosas,
    SUM(CASE WHEN sv.estado = 'fallida' THEN 1 ELSE 0 END) as validaciones_fallidas,
    ROUND(
        (SUM(CASE WHEN sv.estado = 'exitosa' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2
    ) as porcentaje_exitosas,
    AVG(sv.score_confianza) as score_promedio
FROM sesiones_validacion sv
JOIN bancos_registrados br ON sv.id_banco = br.id_banco
WHERE sv.fecha_validacion >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY id_banco, nombre_banco
ORDER BY total_solicitudes DESC;

-- Vista de ciudadanos activos con estadísticas
CREATE OR REPLACE VIEW v_ciudadanos_estadisticas AS
SELECT 
    c.numero_documento,
    c.nombres,
    c.apellido_paterno,
    c.apellido_materno,
    c.distrito,
    c.provincia,
    c.departamento,
    COUNT(sv.id_solicitud) as total_validaciones,
    SUM(CASE WHEN sv.estado = 'exitosa' THEN 1 ELSE 0 END) as validaciones_exitosas,
    MAX(sv.fecha_validacion) as ultima_validacion,
    AVG(sv.score_confianza) as score_promedio
FROM ciudadanos c
LEFT JOIN sesiones_validacion sv ON c.numero_documento = sv.numero_dni
WHERE c.activo = 1
GROUP BY c.numero_documento, c.nombres, c.apellido_paterno, c.apellido_materno,
         c.distrito, c.provincia, c.departamento
ORDER BY total_validaciones DESC;

-- ===========================================
-- TRIGGERS
-- ===========================================

-- Trigger para actualizar estadísticas de banco al crear sesión
DELIMITER //

CREATE TRIGGER IF NOT EXISTS tr_actualizar_estadisticas_banco
AFTER INSERT ON sesiones_validacion
FOR EACH ROW
BEGIN
    IF NEW.id_banco IS NOT NULL THEN
        UPDATE bancos_registrados 
        SET 
            total_solicitudes = total_solicitudes + 1,
            ultimo_acceso = NEW.fecha_validacion
        WHERE id_banco = NEW.id_banco;
    END IF;
END //

DELIMITER ;

-- ===========================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- ===========================================

-- Índices compuestos para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_sesiones_fecha_estado ON sesiones_validacion (fecha_validacion, estado);
CREATE INDEX IF NOT EXISTS idx_eventos_fecha_tipo ON auditoria_eventos (timestamp, tipo_evento);
CREATE INDEX IF NOT EXISTS idx_errores_fecha_severidad ON auditoria_errores (timestamp, severidad);

-- ===========================================
-- CONFIGURACIÓN FINAL
-- ===========================================

-- Configurar AUTO_INCREMENT para mejor rendimiento
SET GLOBAL innodb_buffer_pool_size = 1073741824; -- 1GB
SET GLOBAL innodb_log_file_size = 268435456; -- 256MB

-- Verificar que las tablas se crearon correctamente
SHOW TABLES;

-- Mostrar información de las tablas creadas
DESCRIBE ciudadanos;
DESCRIBE sesiones_validacion;
DESCRIBE auditoria_eventos;
DESCRIBE auditoria_errores;
DESCRIBE auditoria_metricas;

-- Mensaje de confirmación
SELECT 'Script de configuración completado exitosamente' as mensaje;