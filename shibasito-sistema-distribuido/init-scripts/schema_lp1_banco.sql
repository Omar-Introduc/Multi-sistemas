-- ===================================================================
-- SISTEMA BANCARIO LP1 - ESQUEMA DE BASE DE DATOS
-- ===================================================================
-- Este archivo contiene la definición de las tablas principales del 
-- sistema bancario, incluyendo relaciones y restricciones básicas.
-- Versión: 1.0
-- Fecha: 2025-10-30
-- ===================================================================

-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS banco_lp1 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE banco_lp1;

-- ===================================================================
-- TABLA: clientes
-- ===================================================================
-- Almacena la información personal y de contacto de los clientes del banco
-- Incluye datos personales, información de contacto y estado del cliente
-- ===================================================================

DROP TABLE IF EXISTS clientes;
CREATE TABLE clientes (
    -- Clave primaria
    cliente_id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Información personal
    numero_documento VARCHAR(20) NOT NULL UNIQUE,
    tipo_documento ENUM('DNI', 'RUC', 'PASS', 'CEX') NOT NULL DEFAULT 'DNI',
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    
    -- Información de contacto
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    
    -- Información del banco
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('activo', 'inactivo', 'suspendido', 'bloqueado') DEFAULT 'activo',
    limite_credito DECIMAL(12,2) DEFAULT 0.00,
    
    -- Índices y metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices para optimizar consultas
    INDEX idx_numero_documento (numero_documento),
    INDEX idx_email (email),
    INDEX idx_estado (estado),
    INDEX idx_fecha_registro (fecha_registro),
    
    -- Validaciones de integridad
    CONSTRAINT chk_numero_documento CHECK (
        (tipo_documento = 'DNI' AND LENGTH(numero_documento) = 8) OR
        (tipo_documento = 'RUC' AND LENGTH(numero_documento) = 11) OR
        (tipo_documento IN ('PASS', 'CEX'))
    ),
    CONSTRAINT chk_email_format CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_limite_credito CHECK (limite_credito >= 0)
);

-- ===================================================================
-- TABLA: cuentas
-- ===================================================================
-- Maneja las cuentas bancarias de los clientes
-- Soporta diferentes tipos de cuenta (ahorro, corriente, plazo fijo)
-- ===================================================================

DROP TABLE IF EXISTS cuentas;
CREATE TABLE cuentas (
    -- Clave primaria
    cuenta_id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Identificación de cuenta
    numero_cuenta VARCHAR(20) NOT NULL UNIQUE,
    
    -- Relación con cliente (clave foránea)
    cliente_id INT NOT NULL,
    
    -- Tipo y estado de cuenta
    tipo_cuenta ENUM('ahorro', 'corriente', 'plazo_fijo') NOT NULL DEFAULT 'ahorro',
    estado ENUM('activa', 'inactiva', 'bloqueada', 'cerrada') DEFAULT 'activa',
    
    -- Información financiera
    saldo_actual DECIMAL(15,2) DEFAULT 0.00,
    saldo_disponible DECIMAL(15,2) DEFAULT 0.00,
    
    -- Configuración de cuenta
    tasa_interes DECIMAL(5,4) DEFAULT 0.0000, -- Tasa anual en formato decimal
    limite_sobregiro DECIMAL(12,2) DEFAULT 0.00,
    
    -- Fechas importantes
    fecha_apertura DATE NOT NULL,
    fecha_cierre DATE NULL,
    fecha_ultimo_movimiento TIMESTAMP NULL,
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices para optimizar consultas
    INDEX idx_numero_cuenta (numero_cuenta),
    INDEX idx_cliente_id (cliente_id),
    INDEX idx_tipo_cuenta (tipo_cuenta),
    INDEX idx_estado_cuenta (estado),
    INDEX idx_fecha_apertura (fecha_apertura),
    INDEX idx_fecha_ultimo_movimiento (fecha_ultimo_movimiento),
    INDEX idx_saldo_actual (saldo_actual),
    
    -- Índices compuestos para consultas frecuentes
    INDEX idx_cliente_tipo (cliente_id, tipo_cuenta),
    INDEX idx_estado_saldo (estado, saldo_disponible),
    
    -- Clave foránea
    CONSTRAINT fk_cuentas_cliente 
        FOREIGN KEY (cliente_id) 
        REFERENCES clientes(cliente_id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    
    -- Validaciones de integridad
    CONSTRAINT chk_saldo_actual CHECK (saldo_actual >= -limite_sobregiro),
    CONSTRAINT chk_saldo_disponible CHECK (saldo_disponible <= saldo_actual + limite_sobregiro),
    CONSTRAINT chk_tasa_interes CHECK (tasa_interes >= 0),
    CONSTRAINT chk_fecha_cierre CHECK (fecha_cierre IS NULL OR fecha_cierre >= fecha_apertura)
);

-- ===================================================================
-- TABLA: transacciones
-- ===================================================================
-- Registra todas las transacciones bancarias realizadas
-- Incluye depósitos, retiros, transferencias y otros movimientos
-- ===================================================================

DROP TABLE IF EXISTS transacciones;
CREATE TABLE transacciones (
    -- Clave primaria
    transaccion_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- Referencias a cuentas involucradas
    cuenta_origen INT NOT NULL,
    cuenta_destino INT NULL, -- NULL para transacciones que no son transferencias
    
    -- Información de la transacción
    tipo_transaccion ENUM('deposito', 'retiro', 'transferencia', 'intereses', 'comision') NOT NULL,
    monto DECIMAL(12,2) NOT NULL,
    moneda VARCHAR(3) DEFAULT 'PEN',
    
    -- Estado y resultado
    estado ENUM('pendiente', 'completada', 'revertida', 'fallida') DEFAULT 'completada',
    fecha_ejecucion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_procesamiento TIMESTAMP NULL,
    
    -- Información adicional
    descripcion TEXT,
    referencia VARCHAR(50), -- Número de operación, voucher, etc.
    
    -- Información de auditoría
    usuario_id VARCHAR(50), -- ID del usuario que realizó la transacción
    canal ENUM('sucursal', 'cajero', 'web', 'movil', 'api') DEFAULT 'sucursal',
    ip_origen VARCHAR(45), -- Para auditoría de seguridad
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices para optimizar consultas
    INDEX idx_cuenta_origen (cuenta_origen),
    INDEX idx_cuenta_destino (cuenta_destino),
    INDEX idx_tipo_transaccion (tipo_transaccion),
    INDEX idx_estado (estado),
    INDEX idx_fecha_ejecucion (fecha_ejecucion),
    INDEX idx_fecha_procesamiento (fecha_procesamiento),
    INDEX idx_moneda (moneda),
    INDEX idx_referencia (referencia),
    INDEX idx_usuario (usuario_id),
    INDEX idx_canal (canal),
    
    -- Índices compuestos para consultas frecuentes
    INDEX idx_cuenta_fecha (cuenta_origen, fecha_ejecucion),
    INDEX idx_transaccion_estado_fecha (tipo_transaccion, estado, fecha_ejecucion),
    INDEX idx_fecha_monto (fecha_ejecucion, monto),
    
    -- Claves foráneas
    CONSTRAINT fk_transacciones_cuenta_origen 
        FOREIGN KEY (cuenta_origen) 
        REFERENCES cuentas(cuenta_id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_transacciones_cuenta_destino 
        FOREIGN KEY (cuenta_destino) 
        REFERENCES cuentas(cuenta_id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    
    -- Validaciones de integridad
    CONSTRAINT chk_monto_positivo CHECK (monto > 0),
    CONSTRAINT chk_misma_moneda CHECK (
        (SELECT moneda FROM cuentas WHERE cuenta_id = cuenta_origen) = 
        IFNULL((SELECT moneda FROM cuentas WHERE cuenta_id = cuenta_destino), moneda)
    ),
    CONSTRAINT chk_no_autotransferencia CHECK (cuenta_origen != cuenta_destino)
);

-- ===================================================================
-- TABLA: prestamos
-- ===================================================================
-- Gestiona los préstamos otorgados a los clientes
-- Incluye información de tasas, plazos y estados de pago
-- ===================================================================

DROP TABLE IF EXISTS prestamos;
CREATE TABLE prestamos (
    -- Clave primaria
    prestamo_id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Identificación del préstamo
    numero_prestamo VARCHAR(20) NOT NULL UNIQUE,
    
    -- Relación con cliente
    cliente_id INT NOT NULL,
    
    -- Información del préstamo
    tipo_prestamo ENUM('personal', 'vivienda', 'vehicular', 'empresarial', 'estudiantil') NOT NULL,
    monto_solicitado DECIMAL(15,2) NOT NULL,
    monto_aprobado DECIMAL(15,2) NOT NULL,
    
    -- Tasas y condiciones
    tasa_interes_anual DECIMAL(6,4) NOT NULL, -- En formato decimal (ej: 0.15 para 15%)
    plazo_meses INT NOT NULL,
    fecha_prestamo DATE NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    
    -- Estado del préstamo
    estado ENUM('solicitado', 'aprobado', 'desembolsado', 'activo', 'pagado', 'vencido', 'castigado') DEFAULT 'solicitado',
    fecha_desembolso DATE NULL,
    
    -- Información de pagos
    cuota_mensual DECIMAL(12,2) NOT NULL,
    capital_pendiente DECIMAL(15,2) DEFAULT 0.00,
    intereses_pagados DECIMAL(12,2) DEFAULT 0.00,
    numero_cuotas_totales INT NOT NULL,
    numero_cuotas_pagadas INT DEFAULT 0,
    
    -- Garantías
    tipo_garantia ENUM('ninguna', 'hipotecaria', 'vehicular', 'prendaria', 'aval') DEFAULT 'ninguna',
    descripcion_garantia TEXT,
    valor_garantia DECIMAL(15,2) DEFAULT 0.00,
    
    -- Información adicional
    proposito TEXT,
    observaciones TEXT,
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices para optimizar consultas
    INDEX idx_numero_prestamo (numero_prestamo),
    INDEX idx_cliente_id (cliente_id),
    INDEX idx_tipo_prestamo (tipo_prestamo),
    INDEX idx_estado (estado),
    INDEX idx_fecha_prestamo (fecha_prestamo),
    INDEX idx_fecha_vencimiento (fecha_vencimiento),
    INDEX idx_fecha_desembolso (fecha_desembolso),
    INDEX idx_capital_pendiente (capital_pendiente),
    INDEX idx_numero_cuotas_pagadas (numero_cuotas_pagadas),
    INDEX idx_tipo_garantia (tipo_garantia),
    
    -- Índices compuestos para consultas frecuentes
    INDEX idx_cliente_estado (cliente_id, estado),
    INDEX idx_estado_vencimiento (estado, fecha_vencimiento),
    INDEX idx_tipo_estado_monto (tipo_prestamo, estado, monto_aprobado),
    
    -- Clave foránea
    CONSTRAINT fk_prestamos_cliente 
        FOREIGN KEY (cliente_id) 
        REFERENCES clientes(cliente_id) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    
    -- Validaciones de integridad
    CONSTRAINT chk_monto_aprobado CHECK (monto_aprobado <= monto_solicitado),
    CONSTRAINT chk_tasa_interes_positiva CHECK (tasa_interes_anual > 0),
    CONSTRAINT chk_plazo_valido CHECK (plazo_meses BETWEEN 1 AND 480), -- Máximo 40 años
    CONSTRAINT chk_fecha_vencimiento CHECK (fecha_vencimiento > fecha_prestamo),
    CONSTRAINT chk_capital_pendiente CHECK (capital_pendiente >= 0),
    CONSTRAINT chk_cuotas_pagadas CHECK (numero_cuotas_pagadas BETWEEN 0 AND numero_cuotas_totales),
    CONSTRAINT chk_cuota_mensual CHECK (cuota_mensual > 0),
    CONSTRAINT chk_valor_garantia CHECK (valor_garantia >= 0),
    CONSTRAINT chk_valor_garantia_proporcion CHECK (
        valor_garantia = 0 OR valor_garantia >= monto_aprobado * 0.5
    )
);

-- ===================================================================
-- CONFIGURACIONES ADICIONALES
-- ===================================================================

-- Configurar MySQL para mejor rendimiento en transacciones bancarias
SET GLOBAL innodb_flush_log_at_trx_commit = 2;
SET GLOBAL innodb_buffer_pool_size = 1024 * 1024 * 1024; -- 1GB
SET GLOBAL max_connections = 200;
SET GLOBAL sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO';

-- ===================================================================
-- VISTAS ÚTILES PARA REPORTES
-- ===================================================================

-- Vista para resumen de clientes con sus cuentas
CREATE OR REPLACE VIEW vista_resumen_clientes AS
SELECT 
    c.cliente_id,
    c.numero_documento,
    CONCAT(c.nombres, ' ', c.apellidos) AS nombre_completo,
    c.email,
    c.telefono,
    c.estado AS estado_cliente,
    COUNT(cu.cuenta_id) AS total_cuentas,
    SUM(cu.saldo_actual) AS saldo_total_cuentas,
    MAX(cu.fecha_ultimo_movimiento) AS ultimo_movimiento
FROM clientes c
LEFT JOIN cuentas cu ON c.cliente_id = cu.cliente_id AND cu.estado = 'activa'
GROUP BY c.cliente_id;

-- Vista para movimientos recientes por cuenta
CREATE OR REPLACE VIEW vista_movimientos_recientes AS
SELECT 
    t.transaccion_id,
    t.cuenta_origen,
    t.cuenta_destino,
    t.tipo_transaccion,
    t.monto,
    t.estado,
    t.fecha_ejecucion,
    t.descripcion,
    t.referencia,
    c.numero_cuenta AS numero_cuenta_origen,
    c2.numero_cuenta AS numero_cuenta_destino
FROM transacciones t
JOIN cuentas c ON t.cuenta_origen = c.cuenta_id
LEFT JOIN cuentas c2 ON t.cuenta_destino = c2.cuenta_id
ORDER BY t.fecha_ejecucion DESC;

-- Vista para resumen de préstamos activos
CREATE OR REPLACE VIEW vista_prestamos_activos AS
SELECT 
    p.prestamo_id,
    p.numero_prestamo,
    p.tipo_prestamo,
    CONCAT(c.nombres, ' ', c.apellidos) AS nombre_cliente,
    p.monto_aprobado,
    p.capital_pendiente,
    p.cuota_mensual,
    p.fecha_vencimiento,
    p.numero_cuotas_pagadas,
    p.numero_cuotas_totales,
    ROUND((p.capital_pendiente / p.monto_aprobado) * 100, 2) AS porcentaje_pendiente
FROM prestamos p
JOIN clientes c ON p.cliente_id = c.cliente_id
WHERE p.estado IN ('activo', 'desembolsado')
ORDER BY p.fecha_vencimiento;

-- ===================================================================
-- COMENTARIOS FINALES
-- ===================================================================
/*
ESQUEMA CREADO EXITOSAMENTE:

TABLAS CREADAS:
1. clientes - Información de clientes del banco
2. cuentas - Cuentas bancarias asociadas a clientes
3. transacciones - Registro de todos los movimientos bancarios
4. prestamos - Préstamos otorgados a clientes

ÍNDICES INCLUIDOS:
- Índices en campos de búsqueda frecuente
- Índices compuestos para consultas complejas
- Índices en claves foráneas para optimizar joins

VISTAS CREADAS:
- vista_resumen_clientes - Resumen de clientes y sus cuentas
- vista_movimientos_recientes - Últimas transacciones realizadas
- vista_prestamos_activos - Préstamos activos con información detallada

CONFIGURACIONES:
- Optimizaciones para rendimiento en transacciones bancarias
- Configuraciones de MySQL para mejor performance
- Validaciones de integridad de datos

SIGUIENTE PASO:
Ejecutar seed_data_lp1.sql para cargar datos de prueba
*/