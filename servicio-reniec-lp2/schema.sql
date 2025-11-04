-- Tabla Personas
CREATE TABLE personas (
    dni VARCHAR(8) PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    sexo ENUM('M', 'F') NOT NULL,
    estado_civil ENUM('soltero', 'casado', 'divorciado', 'viudo') NOT NULL,
    lugar_nacimiento VARCHAR(100) NOT NULL,
    direccion_actual VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Índices para optimización
CREATE INDEX idx_personas_nombres ON personas(nombres);
CREATE INDEX idx_personas_apellidos ON personas(apellido_paterno, apellido_materno);
