-- Tabla Cuentas
CREATE TABLE cuentas (
    id_cuenta VARCHAR(10) PRIMARY KEY,
    id_cliente VARCHAR(10) NOT NULL,
    saldo DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    fecha_apertura DATE NOT NULL,
    tipo_cuenta VARCHAR(10) CHECK (tipo_cuenta IN ('ahorros', 'corriente')) DEFAULT 'ahorros',
    estado VARCHAR(10) CHECK (estado IN ('activa', 'inactiva', 'bloqueada')) DEFAULT 'activa',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla Préstamos
CREATE TABLE prestamos (
    id_prestamo VARCHAR(10) PRIMARY KEY,
    id_cliente VARCHAR(10) NOT NULL,
    monto DECIMAL(15,2) NOT NULL,
    monto_pendiente DECIMAL(15,2) NOT NULL,
    tasa_interes DECIMAL(5,2) NOT NULL,
    estado VARCHAR(20) CHECK (estado IN ('activo', 'pagado', 'vencido', 'cancelado', 'pendiente_validacion', 'rechazado')),
    fecha_solicitud DATE NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla Transacciones
CREATE TABLE transacciones (
    id_transaccion VARCHAR(10) PRIMARY KEY,
    id_cuenta VARCHAR(10) NOT NULL,
    tipo VARCHAR(15) CHECK (tipo IN ('deposito', 'retiro', 'pago', 'transferencia')) NOT NULL,
    monto DECIMAL(15,2) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    descripcion VARCHAR(255),
    id_destino VARCHAR(10), -- Para transferencias
    estado VARCHAR(10) CHECK (estado IN ('pendiente', 'completada', 'fallida')) DEFAULT 'pendiente'
);
