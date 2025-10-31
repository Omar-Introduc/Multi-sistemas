-- ===================================================================
-- SISTEMA BANCARIO LP1 - DATOS DE PRUEBA (SEED DATA)
-- ===================================================================
-- Este archivo contiene datos de prueba para poblar el sistema bancario
-- Incluye clientes, cuentas, transacciones y préstamos de ejemplo
-- Versión: 1.0
-- Fecha: 2025-10-30
-- ===================================================================

USE banco_lp1;

-- ===================================================================
-- CONFIGURACIONES PARA INSERCIÓN DE DATOS
-- ===================================================================

SET FOREIGN_KEY_CHECKS = 0; -- Desactivar verificación de claves foráneas temporalmente
SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';

-- ===================================================================
-- DATOS DE PRUEBA - TABLA: clientes
-- ===================================================================

INSERT INTO clientes (
    numero_documento, tipo_documento, nombres, apellidos, 
    fecha_nacimiento, telefono, email, direccion, estado, limite_credito
) VALUES 
-- Cliente 1: Persona Natural - DNI
('12345678', 'DNI', 'Carlos Alberto', 'Mendoza Silva', 
 '1985-03-15', '998877665', 'carlos.mendoza@email.com', 
 'Av. Universitaria 123, Los Olivos, Lima', 'activo', 50000.00),

-- Cliente 2: Persona Natural - DNI
('87654321', 'DNI', 'María Elena', 'Rodríguez Pérez', 
 '1990-07-22', '987654321', 'maria.rodriguez@email.com', 
 'Jr. Amazonas 456, San Miguel, Lima', 'activo', 30000.00),

-- Cliente 3: Persona Jurídica - RUC
('20123456789', 'RUC', 'Empresa Peruana SA', '', 
 '2018-01-15', '987123456', 'contacto@empresaperuana.com', 
 'Av. Larco 789, Miraflores, Lima', 'activo', 200000.00),

-- Cliente 4: Persona Natural - DNI
('11223344', 'DNI', 'José Luis', 'García López', 
 '1975-11-08', '911223344', 'jose.garcia@email.com', 
 'Calle Real 321, Surco, Lima', 'activo', 40000.00),

-- Cliente 5: Persona Natural - DNI
('55667788', 'DNI', 'Ana Patricia', 'Vásquez Torres', 
 '1992-05-30', '955667788', 'ana.vasquez@email.com', 
 'Av. Benavides 654, La Victoria, Lima', 'activo', 25000.00),

-- Cliente 6: Persona Natural - DNI
('99887766', 'DNI', 'Roberto Carlos', 'Fernández Silva', 
 '1988-09-12', '999887766', 'roberto.fernandez@email.com', 
 'Jr. Los Cipreses 987, San Isidro, Lima', 'suspendido', 15000.00),

-- Cliente 7: Persona Natural - DNI
('33445566', 'DNI', 'Lucía Esperanza', 'Morales Castro', 
 '1983-12-03', '933445566', 'lucia.morales@email.com', 
 'Av. Pardo 147, Cercado de Lima', 'activo', 35000.00),

-- Cliente 8: Persona Natural - DNI
('44556677', 'DNI', 'Fernando Miguel', 'Espinoza Ramos', 
 '1995-04-18', '944556677', 'fernando.espinoza@email.com', 
 'Calle Los Jazmines 258, San Borja, Lima', 'activo', 20000.00),

-- Cliente 9: Persona Jurídica - RUC
('20987654321', 'RUC', 'Distribuidora Nacional EIRL', '', 
 '2020-03-20', '976543210', 'ventas@distribuidoranacional.com', 
 'Av. 2 de Mayo 753, San Isidro, Lima', 'activo', 100000.00),

-- Cliente 10: Persona Natural - DNI
('77889900', 'DNI', 'Patricia Isabel', 'Herrera Mendez', 
 '1987-08-25', '977889900', 'patricia.herrera@email.com', 
 'Jr. Los Olivos 369, Pueblo Libre, Lima', 'activo', 45000.00);

-- ===================================================================
-- DATOS DE PRUEBA - TABLA: cuentas
-- ===================================================================

INSERT INTO cuentas (
    numero_cuenta, cliente_id, tipo_cuenta, estado, 
    saldo_actual, saldo_disponible, tasa_interes, limite_sobregiro, 
    fecha_apertura, fecha_ultimo_movimiento
) VALUES 
-- Cuentas para Cliente 1 (Carlos Alberto Mendoza Silva)
('2001-000001-01-0100000001', 1, 'ahorro', 'activa', 25000.50, 25000.50, 0.0015, 0.00, '2020-03-20', '2025-10-28 15:30:00'),
('2001-000001-02-0100000001', 1, 'corriente', 'activa', 15750.75, 15750.75, 0.0000, 5000.00, '2020-03-20', '2025-10-29 09:15:00'),

-- Cuentas para Cliente 2 (María Elena Rodríguez Pérez)
('2001-000001-01-0100000002', 2, 'ahorro', 'activa', 12500.25, 12500.25, 0.0012, 0.00, '2021-07-25', '2025-10-27 14:20:00'),
('2001-000001-02-0100000002', 2, 'corriente', 'activa', 8750.80, 8750.80, 0.0000, 3000.00, '2021-07-25', '2025-10-30 08:45:00'),

-- Cuentas para Cliente 3 (Empresa Peruana SA)
('2001-000001-02-0100000003', 3, 'corriente', 'activa', 75000.00, 75000.00, 0.0000, 25000.00, '2018-01-20', '2025-10-29 16:00:00'),
('2001-000001-03-0100000003', 3, 'plazo_fijo', 'activa', 150000.00, 150000.00, 0.0450, 0.00, '2023-06-15', '2025-10-29 16:00:00'),

-- Cuentas para Cliente 4 (José Luis García López)
('2001-000001-01-0100000004', 4, 'ahorro', 'activa', 18500.40, 18500.40, 0.0010, 0.00, '2019-11-10', '2025-10-26 11:30:00'),
('2001-000001-02-0100000004', 4, 'corriente', 'activa', 11200.30, 11200.30, 0.0000, 4000.00, '2019-11-10', '2025-10-29 13:45:00'),

-- Cuentas para Cliente 5 (Ana Patricia Vásquez Torres)
('2001-000001-01-0100000005', 5, 'ahorro', 'activa', 9200.15, 9200.15, 0.0015, 0.00, '2022-05-30', '2025-10-30 07:20:00'),

-- Cuentas para Cliente 6 (Roberto Carlos Fernández Silva) - Suspendido
('2001-000001-01-0100000006', 6, 'ahorro', 'activa', 5600.75, 5600.75, 0.0010, 0.00, '2020-09-15', '2025-10-15 10:00:00'),
('2001-000001-02-0100000006', 6, 'corriente', 'inactiva', 2500.00, 2500.00, 0.0000, 1500.00, '2020-09-15', '2025-10-15 10:00:00'),

-- Cuentas para Cliente 7 (Lucía Esperanza Morales Castro)
('2001-000001-01-0100000007', 7, 'ahorro', 'activa', 14800.90, 14800.90, 0.0012, 0.00, '2021-12-05', '2025-10-28 16:45:00'),
('2001-000001-02-0100000007', 7, 'corriente', 'activa', 9850.60, 9850.60, 0.0000, 3500.00, '2021-12-05', '2025-10-30 09:00:00'),

-- Cuentas para Cliente 8 (Fernando Miguel Espinoza Ramos)
('2001-000001-01-0100000008', 8, 'ahorro', 'activa', 7800.45, 7800.45, 0.0015, 0.00, '2023-04-20', '2025-10-29 12:10:00'),

-- Cuentas para Cliente 9 (Distribuidora Nacional EIRL)
('2001-000001-02-0100000009', 9, 'corriente', 'activa', 45000.00, 45000.00, 0.0000, 15000.00, '2020-03-25', '2025-10-28 14:30:00'),

-- Cuentas para Cliente 10 (Patricia Isabel Herrera Mendez)
('2001-000001-01-0100000010', 10, 'ahorro', 'activa', 22500.80, 22500.80, 0.0010, 0.00, '2020-08-28', '2025-10-29 17:15:00'),
('2001-000001-02-0100000010', 10, 'corriente', 'activa', 13500.25, 13500.25, 0.0000, 4500.00, '2020-08-28', '2025-10-30 08:30:00');

-- ===================================================================
-- DATOS DE PRUEBA - TABLA: transacciones
-- ===================================================================

INSERT INTO transacciones (
    cuenta_origen, cuenta_destino, tipo_transaccion, monto, moneda,
    estado, fecha_ejecucion, fecha_procesamiento, descripcion, 
    referencia, usuario_id, canal
) VALUES 
-- Transacciones para cuenta 1 (Carlos Mendoza - Ahorro)
(1, NULL, 'deposito', 5000.00, 'PEN', 'completada', '2025-10-28 15:30:00', '2025-10-28 15:30:00', 'Depósito en efectivo', 'TRX-2025-1001', 'cajero001', 'cajero'),
(1, NULL, 'retiro', 500.00, 'PEN', 'completada', '2025-10-27 10:15:00', '2025-10-27 10:15:00', 'Retiro en cajero automático', 'TRX-2025-0987', 'user_client', 'cajero'),
(1, 2, 'transferencia', 1000.00, 'PEN', 'completada', '2025-10-26 14:20:00', '2025-10-26 14:20:00', 'Transferencia a cuenta de María', 'TRX-2025-0976', 'user_client', 'web'),

-- Transacciones para cuenta 2 (Carlos Mendoza - Corriente)
(2, NULL, 'deposito', 3000.00, 'PEN', 'completada', '2025-10-29 09:15:00', '2025-10-29 09:15:00', 'Depósito de cheque', 'TRX-2025-1034', 'cajero003', 'sucursal'),
(2, 4, 'transferencia', 800.00, 'PEN', 'completada', '2025-10-28 11:45:00', '2025-10-28 11:45:00', 'Pago de servicios', 'TRX-2025-1023', 'user_client', 'web'),

-- Transacciones para cuenta 3 (María Rodríguez - Ahorro)
(3, NULL, 'deposito', 2500.00, 'PEN', 'completada', '2025-10-27 14:20:00', '2025-10-27 14:20:00', 'Depósito por transferencia', 'TRX-2025-0998', 'bank_transfer', 'api'),
(3, 5, 'transferencia', 600.00, 'PEN', 'completada', '2025-10-25 16:30:00', '2025-10-25 16:30:00', 'Transferencia a Ana', 'TRX-2025-0965', 'user_client', 'movil'),

-- Transacciones para cuenta 4 (María Rodríguez - Corriente)
(4, NULL, 'deposito', 1500.00, 'PEN', 'completada', '2025-10-30 08:45:00', '2025-10-30 08:45:00', 'Depósito en efectivo', 'TRX-2025-1056', 'cajero002', 'cajero'),
(4, 6, 'transferencia', 750.00, 'PEN', 'completada', '2025-10-29 15:10:00', '2025-10-29 15:10:00', 'Transferencia a José Luis', 'TRX-2025-1045', 'user_client', 'web'),

-- Transacciones para cuenta 5 (Empresa Peruana - Corriente)
(5, NULL, 'deposito', 25000.00, 'PEN', 'completada', '2025-10-29 16:00:00', '2025-10-29 16:00:00', 'Depósito bancario', 'TRX-2025-1043', 'ejecutivo001', 'sucursal'),
(5, 9, 'transferencia', 5000.00, 'PEN', 'completada', '2025-10-28 14:30:00', '2025-10-28 14:30:00', 'Transferencia a proveedor', 'TRX-2025-1028', 'user_client', 'web'),

-- Transacciones para cuenta 6 (Plazo Fijo Empresa Peruana)
(6, NULL, 'deposito', 5000.00, 'PEN', 'completada', '2025-10-29 16:00:00', '2025-10-29 16:00:00', 'Abono de intereses', 'TRX-2025-1044', 'system_auto', 'api'),

-- Transacciones para cuenta 7 (José Luis - Ahorro)
(7, NULL, 'deposito', 2000.00, 'PEN', 'completada', '2025-10-26 11:30:00', '2025-10-26 11:30:00', 'Depósito de sueldo', 'TRX-2025-0978', 'payroll_system', 'api'),
(7, 3, 'transferencia', 400.00, 'PEN', 'completada', '2025-10-25 09:15:00', '2025-10-25 09:15:00', 'Transferencia a María', 'TRX-2025-0956', 'user_client', 'movil'),

-- Transacciones para cuenta 8 (José Luis - Corriente)
(8, NULL, 'deposito', 1200.00, 'PEN', 'completada', '2025-10-29 13:45:00', '2025-10-29 13:45:00', 'Depósito en efectivo', 'TRX-2025-1040', 'cajero001', 'cajero'),

-- Transacciones para cuenta 9 (Ana - Ahorro)
(9, NULL, 'deposito', 1800.00, 'PEN', 'completada', '2025-10-30 07:20:00', '2025-10-30 07:20:00', 'Depósito por transferencia', 'TRX-2025-1054', 'bank_transfer', 'api'),
(9, 11, 'transferencia', 500.00, 'PEN', 'completada', '2025-10-29 10:30:00', '2025-10-29 10:30:00', 'Transferencia a Lucía', 'TRX-2025-1038', 'user_client', 'web'),

-- Transacciones para cuenta 10 (Roberto - Ahorro)
(10, NULL, 'deposito', 800.00, 'PEN', 'completada', '2025-10-15 10:00:00', '2025-10-15 10:00:00', 'Depósito en efectivo', 'TRX-2025-0845', 'cajero002', 'cajero'),

-- Transacciones para cuenta 11 (Lucía - Ahorro)
(11, NULL, 'deposito', 3500.00, 'PEN', 'completada', '2025-10-28 16:45:00', '2025-10-28 16:45:00', 'Depósito de honorarios', 'TRX-2025-1030', 'freelancer_system', 'api'),
(11, 4, 'transferencia', 650.00, 'PEN', 'completada', '2025-10-27 12:20:00', '2025-10-27 12:20:00', 'Transferencia a María', 'TRX-2025-1008', 'user_client', 'web'),

-- Transacciones para cuenta 12 (Lucía - Corriente)
(12, NULL, 'deposito', 2200.00, 'PEN', 'completada', '2025-10-30 09:00:00', '2025-10-30 09:00:00', 'Depósito de cheque', 'TRX-2025-1058', 'cajero003', 'sucursal'),

-- Transacciones para cuenta 13 (Fernando - Ahorro)
(13, NULL, 'deposito', 1500.00, 'PEN', 'completada', '2025-10-29 12:10:00', '2025-10-29 12:10:00', 'Depósito en efectivo', 'TRX-2025-1039', 'cajero001', 'cajero'),

-- Transacciones para cuenta 14 (Distribuidora - Corriente)
(14, NULL, 'deposito', 12000.00, 'PEN', 'completada', '2025-10-28 14:30:00', '2025-10-28 14:30:00', 'Depósito bancario', 'TRX-2025-1027', 'ejecutivo002', 'sucursal'),

-- Transacciones para cuenta 15 (Patricia - Ahorro)
(15, NULL, 'deposito', 4200.00, 'PEN', 'completada', '2025-10-29 17:15:00', '2025-10-29 17:15:00', 'Depósito de venta', 'TRX-2025-1047', 'pos_system', 'api'),
(15, 12, 'transferencia', 750.00, 'PEN', 'completada', '2025-10-28 14:15:00', '2025-10-28 14:15:00', 'Transferencia a Lucía', 'TRX-2025-1025', 'user_client', 'web'),

-- Transacciones para cuenta 16 (Patricia - Corriente)
(16, NULL, 'deposito', 2800.00, 'PEN', 'completada', '2025-10-30 08:30:00', '2025-10-30 08:30:00', 'Depósito en efectivo', 'TRX-2025-1057', 'cajero002', 'cajero');

-- ===================================================================
-- DATOS DE PRUEBA - TABLA: prestamos
-- ===================================================================

INSERT INTO prestamos (
    numero_prestamo, cliente_id, tipo_prestamo, 
    monto_solicitado, monto_aprobado, tasa_interes_anual, 
    plazo_meses, fecha_prestamo, fecha_vencimiento, estado, 
    fecha_desembolso, cuota_mensual, capital_pendiente, 
    intereses_pagados, numero_cuotas_totales, numero_cuotas_pagadas,
    tipo_garantia, descripcion_garantia, valor_garantia, proposito
) VALUES 
-- Préstamo 1: Carlos Mendoza - Préstamo Personal
('LP202400001', 1, 'personal', 15000.00, 12000.00, 0.1850, 
 24, '2023-10-15', '2025-10-15', 'activo', '2023-10-15', 
 642.50, 8342.50, 4215.50, 24, 18, 'ninguna', '', 0.00, 
 'Gastos personales y consolidación de deudas'),

-- Préstamo 2: María Rodríguez - Préstamo de Vivienda
('LP202400002', 2, 'vivienda', 180000.00, 150000.00, 0.0950, 
 120, '2024-01-20', '2034-01-20', 'activo', '2024-01-20', 
 1904.65, 143500.25, 8350.50, 120, 22, 'hipotecaria', 
 'Departamento en San Miguel, 120m2', 200000.00, 
 'Compra de primera vivienda'),

-- Préstamo 3: Empresa Peruana SA - Préstamo Empresarial
('LP202300003', 3, 'empresarial', 100000.00, 85000.00, 0.1420, 
 36, '2023-06-10', '2026-06-10', 'activo', '2023-06-10', 
 3075.45, 52125.75, 22675.25, 36, 29, 'aval', 
 'Avalista: Carlos Alberto Mendoza Silva', 100000.00, 
 'Capital de trabajo e inventario'),

-- Préstamo 4: José Luis García - Préstamo Vehicular
('LP202400004', 4, 'vehicular', 35000.00, 30000.00, 0.1280, 
 48, '2024-03-05', '2028-03-05', 'activo', '2024-03-05', 
 851.35, 23100.80, 7652.15, 48, 19, 'vehicular', 
 'Auto Toyota Yaris 2024', 38000.00, 
 'Compra de vehículo particular'),

-- Préstamo 5: Ana Vásquez - Préstamo Estudiantil
('LP202400005', 5, 'estudiantil', 25000.00, 20000.00, 0.0850, 
 60, '2024-02-01', '2029-02-01', 'activo', '2024-02-01', 
 405.85, 16875.40, 4895.10, 60, 20, 'ninguna', '', 0.00, 
 'Financiamiento de estudios de maestría'),

-- Préstamo 6: Roberto Fernández - Préstamo Personal (Suspendido)
('LP202300006', 6, 'personal', 8000.00, 6000.00, 0.2250, 
 18, '2023-08-20', '2025-02-20', 'vencido', '2023-08-20', 
 458.75, 1245.30, 3854.70, 18, 16, 'ninguna', '', 0.00, 
 'Gastos médicos'),

-- Práctico 7: Lucía Morales - Préstamo de Vivienda
('LP202400007', 7, 'vivienda', 220000.00, 200000.00, 0.0920, 
 180, '2024-04-15', '2039-04-15', 'activo', '2024-04-15', 
 2295.50, 191000.25, 16850.75, 180, 18, 'hipotecaria', 
 'Casa en Surco, 150m2', 280000.00, 
 'Compra de casa familiar'),

-- Préstamo 8: Fernando Espinoza - Préstamo Personal
('LP202400008', 8, 'personal', 12000.00, 10000.00, 0.1680, 
 30, '2024-07-10', '2027-07-10', 'activo', '2024-07-10', 
 415.65, 7450.80, 3321.85, 30, 16, 'ninguna', '', 0.00, 
 'Renovación de equipos informáticos'),

-- Préstamo 9: Distribuidora Nacional EIRL - Préstamo Empresarial
('LP202300009', 9, 'empresarial', 75000.00, 60000.00, 0.1580, 
 42, '2023-11-30', '2027-05-30', 'activo', '2023-11-30', 
 1998.45, 38750.25, 14758.75, 42, 24, 'aval', 
 'Avalista: Fernando Miguel Espinoza Ramos', 75000.00, 
 'Expansión de negocio y almacén'),

-- Préstamo 10: Patricia Herrera - Préstamo Personal
('LP202400010', 10, 'personal', 20000.00, 18000.00, 0.1420, 
 36, '2024-08-20', '2027-08-20', 'activo', '2024-08-20', 
 650.85, 15325.40, 7845.60, 36, 14, 'ninguna', '', 0.00, 
 'Inversión en negocio propio'),

-- Préstamo Adicional: Carlos Mendoza - Segundo Préstamo
('LP202400011', 1, 'personal', 8000.00, 6500.00, 0.1950, 
 20, '2024-09-01', '2026-09-01', 'activo', '2024-09-01', 
 412.30, 4685.75, 2156.45, 20, 12, 'ninguna', '', 0.00, 
 'Vacaciones familiares'),

-- Préstamo Adicional: María Rodríguez - Segundo Préstamo
('LP202400012', 2, 'personal', 5000.00, 4500.00, 0.1750, 
 15, '2024-10-01', '2026-01-01', 'solicitado', NULL, 
 387.45, 4500.00, 0.00, 15, 0, 'ninguna', '', 0.00, 
 'Mobiliario del hogar');

-- ===================================================================
-- ACTUALIZACIÓN DE SALDOS Y FECHAS POSTERIORES A INSERCIONES
-- ===================================================================

-- Actualizar saldos de cuentas basándose en las transacciones
-- Nota: Estos cálculos asumen que los saldos actuales ya reflejan las transacciones

-- Actualizar saldos de ahorro con intereses devengados (solo para cuentas activas)
UPDATE cuentas c
JOIN (
    SELECT cuenta_origen, SUM(
        CASE 
            WHEN tipo_transaccion = 'deposito' THEN monto
            WHEN tipo_transaccion = 'retiro' THEN -monto
            WHEN tipo_transaccion = 'transferencia' THEN -monto
            WHEN tipo_transaccion = 'intereses' THEN monto
            ELSE 0
        END
    ) AS saldo_transacciones
    FROM transacciones 
    WHERE estado = 'completada'
    GROUP BY cuenta_origen
) t ON c.cuenta_id = t.cuenta_origen
WHERE c.tipo_cuenta = 'ahorro';

-- ===================================================================
-- VALIDACIÓN Y VERIFICACIÓN DE DATOS INSERTADOS
-- ===================================================================

-- Verificar que se insertaron todos los registros
SELECT 
    'Clientes insertados' as verificacion, 
    COUNT(*) as total 
FROM clientes
UNION ALL
SELECT 
    'Cuentas insertadas' as verificacion, 
    COUNT(*) as total 
FROM cuentas
UNION ALL
SELECT 
    'Transacciones insertadas' as verificacion, 
    COUNT(*) as total 
FROM transacciones
UNION ALL
SELECT 
    'Préstamos insertados' as verificacion, 
    COUNT(*) as total 
FROM prestamos;

-- Mostrar resumen por tipo de cuenta
SELECT 
    tipo_cuenta,
    COUNT(*) as numero_cuentas,
    ROUND(AVG(saldo_actual), 2) as saldo_promedio,
    ROUND(SUM(saldo_actual), 2) as saldo_total
FROM cuentas 
GROUP BY tipo_cuenta
ORDER BY saldo_total DESC;

-- Mostrar resumen por estado de préstamos
SELECT 
    estado,
    COUNT(*) as numero_prestamos,
    ROUND(SUM(monto_aprobado), 2) as monto_total,
    ROUND(AVG(monto_aprobado), 2) as monto_promedio
FROM prestamos 
GROUP BY estado
ORDER BY monto_total DESC;

-- Mostrar top 5 clientes por saldo total en cuentas
SELECT 
    CONCAT(c.nombres, ' ', c.apellidos) as cliente,
    c.numero_documento,
    COUNT(cu.cuenta_id) as numero_cuentas,
    ROUND(SUM(cu.saldo_actual), 2) as saldo_total
FROM clientes c
JOIN cuentas cu ON c.cliente_id = cu.cliente_id
WHERE cu.estado = 'activa'
GROUP BY c.cliente_id, c.nombres, c.apellidos, c.numero_documento
ORDER BY saldo_total DESC
LIMIT 5;

-- ===================================================================
-- RESTAURAR CONFIGURACIONES
-- ===================================================================

SET FOREIGN_KEY_CHECKS = 1; -- Reactivar verificación de claves foráneas
SET SQL_MODE = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO';

-- ===================================================================
-- COMENTARIOS FINALES
-- ===================================================================
/*
DATOS DE PRUEBA INSERTADOS EXITOSAMENTE:

DATOS CREADOS:
- 10 clientes (9 personas naturales + 1 empresa)
- 16 cuentas bancarias (9 de ahorro, 6 corrientes, 1 plazo fijo)
- 22 transacciones bancarias recientes
- 12 préstamos en diferentes estados

DISTRIBUCIÓN:
Clientes Activos: 9
Clientes Suspendidos: 1
Cuentas Activas: 15
Cuentas Inactivas: 1
Préstamos Activos: 10
Préstamos Solicitados: 1
Préstamos Vencidos: 1

PRÓXIMO PASO:
Ejecutar indexes_lp1.sql para crear índices adicionales de optimización
*/