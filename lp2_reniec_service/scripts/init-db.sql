-- Script de inicialización de base de datos para LP2 RENIEC Service
-- Crear base de datos y usuario

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS reniec_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE reniec_db;

-- Crear tabla de ciudadanos
CREATE TABLE ciudadanos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    documento_identidad VARCHAR(8) UNIQUE NOT NULL,
    nombres VARCHAR(255) NOT NULL,
    apellidos VARCHAR(255) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    lugar_nacimiento VARCHAR(255) NOT NULL,
    genero VARCHAR(1) NOT NULL CHECK (genero IN ('M', 'F')),
    estado_civil VARCHAR(20) NULL,
    direccion VARCHAR(500) NULL,
    telefono VARCHAR(15) NULL,
    email VARCHAR(255) NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_documento_identidad (documento_identidad),
    INDEX idx_nombres (nombres),
    INDEX idx_apellidos (apellidos),
    INDEX idx_email (email)
) ENGINE=InnoDB;

-- Crear tabla de tipos de documento
CREATE TABLE tipos_documento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT NULL,
    requiere_renovacion BOOLEAN DEFAULT FALSE,
    vigencia_meses INT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_codigo (codigo)
) ENGINE=InnoDB;

-- Crear tabla de documentos
CREATE TABLE documentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_documento VARCHAR(20) UNIQUE NOT NULL,
    ciudadano_id INT NOT NULL,
    tipo_documento_id INT NOT NULL,
    fecha_emision DATE NOT NULL,
    fecha_vencimiento DATE NULL,
    estado VARCHAR(20) DEFAULT 'vigente' CHECK (estado IN ('vigente', 'vencido', 'perdido', 'robado', 'anulado')),
    archivo_documento VARCHAR(500) NULL,
    metadatos JSON NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (ciudadano_id) REFERENCES ciudadanos(id) ON DELETE CASCADE,
    FOREIGN KEY (tipo_documento_id) REFERENCES tipos_documento(id) ON DELETE RESTRICT,
    INDEX idx_numero_documento (numero_documento),
    INDEX idx_ciudadano (ciudadano_id),
    INDEX idx_tipo_documento (tipo_documento_id),
    INDEX idx_estado (estado)
) ENGINE=InnoDB;

-- Crear tabla de solicitudes
CREATE TABLE solicitudes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_solicitud VARCHAR(20) UNIQUE NOT NULL,
    ciudadano_id INT NOT NULL,
    documento_id INT NULL,
    tipo_solicitud VARCHAR(50) NOT NULL CHECK (tipo_solicitud IN ('primera_vez', 'renovacion', 'duplicado', 'actualizacion')),
    motivo VARCHAR(255) NULL,
    observaciones TEXT NULL,
    estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'en_proceso', 'aprobado', 'rechazado', 'entregado')),
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_procesamiento TIMESTAMP NULL,
    fecha_entrega TIMESTAMP NULL,
    
    FOREIGN KEY (ciudadano_id) REFERENCES ciudadanos(id) ON DELETE CASCADE,
    FOREIGN KEY (documento_id) REFERENCES documentos(id) ON DELETE SET NULL,
    INDEX idx_numero_solicitud (numero_solicitud),
    INDEX idx_ciudadano (ciudadano_id),
    INDEX idx_estado (estado),
    INDEX idx_tipo_solicitud (tipo_solicitud)
) ENGINE=InnoDB;

-- Crear tabla de eventos de solicitud
CREATE TABLE eventos_solicitud (
    id INT AUTO_INCREMENT PRIMARY KEY,
    solicitud_id INT NOT NULL,
    evento VARCHAR(100) NOT NULL,
    descripcion TEXT NULL,
    usuario VARCHAR(100) NULL,
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (solicitud_id) REFERENCES solicitudes(id) ON DELETE CASCADE,
    INDEX idx_solicitud (solicitud_id),
    INDEX idx_evento (evento)
) ENGINE=InnoDB;

-- Crear tabla de sesiones de usuario
CREATE TABLE sesiones_usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    token_sesion VARCHAR(255) UNIQUE NOT NULL,
    fecha_expiracion TIMESTAMP NOT NULL,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    
    INDEX idx_usuario (usuario_id),
    INDEX idx_token_sesion (token_sesion),
    INDEX idx_fecha_expiracion (fecha_expiracion)
) ENGINE=InnoDB;

-- Insertar tipos de documento básicos
INSERT INTO tipos_documento (codigo, nombre, descripcion, requiere_renovacion, vigencia_meses) VALUES
('DNI', 'Documento Nacional de Identidad', 'Documento principal de identidad', TRUE, NULL),
('CE', 'Carné de Extranjería', 'Carné para extranjeros', TRUE, 60),
('PASAPORTE', 'Pasaporte', 'Documento de viaje internacional', TRUE, 120),
('LICENCIA', 'Licencia de Conducir', 'Documento para conducir vehículos', TRUE, 36);

-- Crear usuario de aplicación
CREATE USER IF NOT EXISTS 'reniec_user'@'%' IDENTIFIED BY 'password_seguro';
GRANT ALL PRIVILEGES ON reniec_db.* TO 'reniec_user'@'%';
FLUSH PRIVILEGES;