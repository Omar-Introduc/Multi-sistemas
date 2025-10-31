-- =============================================================================
-- INIT SCRIPT - MYSQL (BD2)
-- Script de inicialización para la base de datos del servicio RENIEC
-- =============================================================================

-- Crear base de datos adicional para auditoría
CREATE DATABASE IF NOT EXISTS reniec_audit;

-- Usar la base de datos principal
USE reniec_db;

-- Crear usuario adicional para lectura
CREATE USER IF NOT EXISTS 'reniec_readonly'@'%' IDENTIFIED BY 'readonly_pass123';
CREATE USER IF NOT EXISTS 'reniec_admin'@'%' IDENTIFIED BY 'admin_pass123';

-- Conceder permisos
GRANT SELECT ON reniec_db.* TO 'reniec_readonly'@'%';
GRANT ALL PRIVILEGES ON reniec_db.* TO 'reniec_admin'@'%';
GRANT ALL PRIVILEGES ON reniec_audit.* TO 'reniec_admin'@'%';

-- Crear tablas básicas (ejemplo)
CREATE TABLE IF NOT EXISTS personas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dni VARCHAR(8) UNIQUE NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    sexo CHAR(1) CHECK (sexo IN ('M', 'F')),
    estado_civil VARCHAR(20),
    direccion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_dni (dni),
    INDEX idx_nombres (nombres),
    INDEX idx_apellidos (apellido_paterno, apellido_materno)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS consultas_dni (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dni_consultado VARCHAR(8) NOT NULL,
    usuario VARCHAR(100),
    ip_address VARCHAR(45),
    resultado ENUM('ENCONTRADO', 'NO_ENCONTRADO', 'ERROR') NOT NULL,
    tiempo_respuesta_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_dni_consultado (dni_consultado),
    INDEX idx_fecha (created_at),
    INDEX idx_resultado (resultado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Usar base de datos de auditoría
USE reniec_audit;

CREATE TABLE IF NOT EXISTS audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tabla_afectada VARCHAR(100) NOT NULL,
    operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    registro_id INT,
    datos_anteriores JSON,
    datos_nuevos JSON,
    usuario VARCHAR(100),
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tabla (tabla_afectada),
    INDEX idx_operacion (operacion),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Configurar timezone
SET GLOBAL time_zone = '+00:00';

FLUSH PRIVILEGES;