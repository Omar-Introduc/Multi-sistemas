-- =====================================================
-- ESQUEMA DE BASE DE DATOS PARA SISTEMA RENIEC LP2
-- Registro Nacional de Identificación y Estado Civil
-- =====================================================

-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS reniec_lp2;
USE reniec_lp2;

-- =====================================================
-- TABLA: ciudadanos
-- Almacena la información de los ciudadanos peruanos
-- =====================================================
CREATE TABLE ciudadanos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dni VARCHAR(8) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    lugar_nacimiento VARCHAR(200),
    genero ENUM('M', 'F') NOT NULL,
    estado_civil ENUM('SOLTERO', 'CASADO', 'VIUDO', 'DIVORCIADO', 'CONVIVIENTE') DEFAULT 'SOLTERO',
    direccion VARCHAR(300),
    distrito VARCHAR(100),
    provincia VARCHAR(100),
    departamento VARCHAR(100),
    telefono VARCHAR(15),
    email VARCHAR(150),
    es_verificado BOOLEAN DEFAULT FALSE,
    fecha_verificacion TIMESTAMP NULL,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_dni (dni),
    INDEX idx_nombre (nombre, apellido_paterno, apellido_materno),
    INDEX idx_estado_verificacion (es_verificado, activo)
);

-- =====================================================
-- TABLA: validadores
-- Usuarios autorizados para validar documentos
-- =====================================================
CREATE TABLE validadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(200) NOT NULL,
    cargo VARCHAR(100),
    oficina VARCHAR(100),
    nivel_acceso ENUM('BASICO', 'INTERMEDIO', 'AVANZADO', 'ADMINISTRADOR') DEFAULT 'BASICO',
    ultimo_acceso TIMESTAMP NULL,
    intentos_fallidos INT DEFAULT 0,
    bloqueado BOOLEAN DEFAULT FALSE,
    fecha_bloqueo TIMESTAMP NULL,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_usuario (usuario),
    INDEX idx_nivel_acceso (nivel_acceso),
    INDEX idx_activo (activo, bloqueado)
);

-- =====================================================
-- TABLA: reniec_sessions
-- Gestión de sesiones de usuarios validadores
-- =====================================================
CREATE TABLE reniec_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    validador_id INT NOT NULL,
    token_sesion VARCHAR(255) NOT NULL UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultimo_uso TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL,
    activa BOOLEAN DEFAULT TRUE,
    operaciones_realizadas INT DEFAULT 0,
    datos_consultados JSON,
    FOREIGN KEY (validador_id) REFERENCES validadores(id) ON DELETE CASCADE,
    INDEX idx_validador (validador_id),
    INDEX idx_token (token_sesion),
    INDEX idx_activa (activa),
    INDEX idx_fecha_expiracion (fecha_expiracion)
);

-- =====================================================
-- TABLA: auditoria
-- Registro detallado de todas las operaciones
-- =====================================================
CREATE TABLE auditoria (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tabla_afectada VARCHAR(50) NOT NULL,
    registro_id INT NOT NULL,
    accion ENUM('INSERT', 'UPDATE', 'DELETE', 'SELECT') NOT NULL,
    validador_id INT NULL,
    session_id INT NULL,
    datos_anteriores JSON,
    datos_nuevos JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    FOREIGN KEY (validador_id) REFERENCES validadores(id) ON DELETE SET NULL,
    FOREIGN KEY (session_id) REFERENCES reniec_sessions(id) ON DELETE SET NULL,
    INDEX idx_tabla_registro (tabla_afectada, registro_id),
    INDEX idx_validador (validador_id),
    INDEX idx_fecha (timestamp_operacion),
    INDEX idx_accion (accion)
);

-- =====================================================
-- PROCEDIMIENTOS ALMACENADOS
-- =====================================================

DELIMITER //

-- Procedure para crear un nuevo ciudadano
CREATE PROCEDURE crear_ciudadano(
    IN p_dni VARCHAR(8),
    IN p_nombre VARCHAR(100),
    IN p_apellido_paterno VARCHAR(100),
    IN p_apellido_materno VARCHAR(100),
    IN p_fecha_nacimiento DATE,
    IN p_lugar_nacimiento VARCHAR(200),
    IN p_genero ENUM('M', 'F'),
    IN p_estado_civil ENUM('SOLTERO', 'CASADO', 'VIUDO', 'DIVORCIADO', 'CONVIVIENTE'),
    IN p_direccion VARCHAR(300),
    IN p_distrito VARCHAR(100),
    IN p_provincia VARCHAR(100),
    IN p_departamento VARCHAR(100),
    IN p_telefono VARCHAR(15),
    IN p_email VARCHAR(150),
    OUT resultado_mensaje VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET resultado_mensaje = 'Error al crear ciudadano';
    END;
    
    START TRANSACTION;
    
    INSERT INTO ciudadanos (
        dni, nombre, apellido_paterno, apellido_materno, fecha_nacimiento,
        lugar_nacimiento, genero, estado_civil, direccion, distrito, provincia,
        departamento, telefono, email
    ) VALUES (
        p_dni, p_nombre, p_apellido_paterno, p_apellido_materno,
        p_fecha_nacimiento, p_lugar_nacimiento, p_genero, p_estado_civil,
        p_direccion, p_distrito, p_provincia, p_departamento, p_telefono, p_email
    );
    
    COMMIT;
    SET resultado_mensaje = 'Ciudadano creado exitosamente';
END //

-- Procedure para iniciar sesión de validador
CREATE PROCEDURE iniciar_sesion_validador(
    IN p_usuario VARCHAR(50),
    IN p_password VARCHAR(255),
    IN p_ip_address VARCHAR(45),
    IN p_user_agent TEXT,
    OUT p_token VARCHAR(255),
    OUT resultado_mensaje VARCHAR(255)
)
BEGIN
    DECLARE v_validador_id INT;
    DECLARE v_password_hash VARCHAR(255);
    DECLARE v_bloqueado BOOLEAN;
    DECLARE v_activo BOOLEAN;
    
    SELECT id, password_hash, bloqueado, activo 
    INTO v_validador_id, v_password_hash, v_bloqueado, v_activo
    FROM validadores 
    WHERE usuario = p_usuario;
    
    IF v_validador_id IS NULL THEN
        SET resultado_mensaje = 'Usuario no encontrado';
        SET p_token = NULL;
    ELSEIF v_bloqueado = TRUE THEN
        SET resultado_mensaje = 'Usuario bloqueado';
        SET p_token = NULL;
    ELSEIF v_activo = FALSE THEN
        SET resultado_mensaje = 'Usuario inactivo';
        SET p_token = NULL;
    ELSEIF v_password_hash != p_password THEN
        UPDATE validadores 
        SET intentos_fallidos = intentos_fallidos + 1,
            bloqueado = CASE WHEN intentos_fallidos >= 4 THEN TRUE ELSE FALSE END,
            fecha_bloqueo = CASE WHEN intentos_fallidos >= 4 THEN CURRENT_TIMESTAMP ELSE fecha_bloqueo END
        WHERE id = v_validador_id;
        
        SET resultado_mensaje = 'Contraseña incorrecta';
        SET p_token = NULL;
    ELSE
        -- Resetear intentos fallidos y actualizar último acceso
        UPDATE validadores 
        SET intentos_fallidos = 0,
            ultimo_acceso = CURRENT_TIMESTAMP
        WHERE id = v_validador_id;
        
        -- Crear token de sesión
        SET p_token = CONCAT('RENIEC_', v_validador_id, '_', UNIX_TIMESTAMP());
        
        INSERT INTO reniec_sessions (
            validador_id, token_sesion, ip_address, user_agent, 
            fecha_expiracion
        ) VALUES (
            v_validador_id, p_token, p_ip_address, p_user_agent,
            DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 8 HOUR)
        );
        
        SET resultado_mensaje = 'Sesión iniciada exitosamente';
    END IF;
END //

DELIMITER ;

-- =====================================================
-- TRIGGERS DE AUDITORÍA
-- =====================================================

DELIMITER //

-- Trigger para auditoría en tabla ciudadanos
CREATE TRIGGER audit_ciudadanos_insert
AFTER INSERT ON ciudadanos
FOR EACH ROW
BEGIN
    INSERT INTO auditoria (tabla_afectada, registro_id, accion, datos_nuevos, timestamp_operacion)
    VALUES ('ciudadanos', NEW.id, 'INSERT', JSON_OBJECT(
        'dni', NEW.dni, 
        'nombre_completo', CONCAT(NEW.nombre, ' ', NEW.apellido_paterno, ' ', NEW.apellido_materno)
    ), CURRENT_TIMESTAMP);
END //

CREATE TRIGGER audit_ciudadanos_update
AFTER UPDATE ON ciudadanos
FOR EACH ROW
BEGIN
    INSERT INTO auditoria (tabla_afectada, registro_id, accion, datos_anteriores, datos_nuevos, timestamp_operacion)
    VALUES ('ciudadanos', NEW.id, 'UPDATE', 
        JSON_OBJECT('dni', OLD.dni, 'estado', OLD.es_verificado, 'activo', OLD.activo),
        JSON_OBJECT('dni', NEW.dni, 'estado', NEW.es_verificado, 'activo', NEW.activo),
        CURRENT_TIMESTAMP);
END //

CREATE TRIGGER audit_ciudadanos_delete
AFTER DELETE ON ciudadanos
FOR EACH ROW
BEGIN
    INSERT INTO auditoria (tabla_afectada, registro_id, accion, datos_anteriores, timestamp_operacion)
    VALUES ('ciudadanos', OLD.id, 'DELETE', 
        JSON_OBJECT('dni', OLD.dni, 'nombre_completo', 
        CONCAT(OLD.nombre, ' ', OLD.apellido_paterno, ' ', OLD.apellido_materno)), 
        CURRENT_TIMESTAMP);
END //

DELIMITER ;

-- =====================================================
-- VISTAS ÚTILES
-- =====================================================

-- Vista para consultas frecuentes de ciudadanos
CREATE VIEW vista_ciudadanos_completa AS
SELECT 
    c.id,
    c.dni,
    c.nombre,
    c.apellido_paterno,
    c.apellido_materno,
    c.fecha_nacimiento,
    c.lugar_nacimiento,
    c.genero,
    c.estado_civil,
    c.direccion,
    c.distrito,
    c.provincia,
    c.departamento,
    c.telefono,
    c.email,
    c.es_verificado,
    c.activo,
    CONCAT(c.nombre, ' ', c.apellido_paterno, ' ', c.apellido_materno) AS nombre_completo,
    CASE 
        WHEN c.genero = 'M' THEN 'Masculino'
        WHEN c.genero = 'F' THEN 'Femenino'
    END AS genero_descripcion
FROM ciudadanos c
WHERE c.activo = TRUE;

-- Vista para sesiones activas
CREATE VIEW vista_sesiones_activas AS
SELECT 
    s.id,
    s.validador_id,
    v.nombre_completo,
    v.usuario,
    v.oficina,
    s.token_sesion,
    s.fecha_inicio,
    s.fecha_ultimo_uso,
    s.operaciones_realizadas,
    TIMESTAMPDIFF(MINUTE, s.fecha_inicio, CURRENT_TIMESTAMP) AS minutos_activa
FROM reniec_sessions s
JOIN validadores v ON s.validador_id = v.id
WHERE s.activa = TRUE AND s.fecha_expiracion > CURRENT_TIMESTAMP;

-- =====================================================
-- FIN DEL ESQUEMA
-- =====================================================
