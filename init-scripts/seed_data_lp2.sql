-- =====================================================
-- DATOS DE PRUEBA PARA SISTEMA RENIEC LP2
-- Registro Nacional de Identificación y Estado Civil
-- =====================================================

USE reniec_lp2;

-- =====================================================
-- DATOS DE VALIDADORES
-- =====================================================

-- Insertar validadores del sistema
INSERT INTO validadores (usuario, password_hash, nombre_completo, cargo, oficina, nivel_acceso, activo) VALUES
('admin_reniec', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPk4YJ6gX4NlW', 'María Elena Vásquez Rojas', 'Administradora Principal', 'Oficina Central Lima', 'ADMINISTRADOR', TRUE),
('validador_01', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPk4YJ6gX4NlW', 'Carlos Alberto Mendoza Silva', 'Validador Senior', 'Mesa de Partes - Lima', 'AVANZADO', TRUE),
('validador_02', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPk4YJ6gX4NlW', 'Ana Patricia González Torres', 'Validador', 'Oficina Lima Cercado', 'INTERMEDIO', TRUE),
('validador_03', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPk4YJ6gX4NlW', 'Miguel Ángel Rodríguez López', 'Validador Junior', 'Oficina Callao', 'BASICO', TRUE),
('validador_04', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPk4YJ6gX4NlW', 'Luis Fernando Herrera Flores', 'Supervisor Regional', 'Dirección Regional Arequipa', 'AVANZADO', TRUE),
('validador_05', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPk4YJ6gX4NlW', 'Carmen Rosa Jiménez Castillo', 'Validador Senior', 'Dirección Regional Cusco', 'AVANZADO', TRUE),
('validador_06', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPk4YJ6gX4NlW', 'Jorge Eduardo Vásquez Morales', 'Validador', 'Oficina Chiclayo', 'INTERMEDIO', TRUE),
('validador_07', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPk4YJ6gX4NlW', 'Patricia Elena Castro Ramírez', 'Validador', 'Oficina Huancayo', 'BASICO', TRUE),
('validador_08', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPk4YJ6gX4NlW', 'Roberto Carlos Mendoza Aliaga', 'Validador Senior', 'Oficina Trujillo', 'AVANZADO', TRUE),
('validador_09', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPk4YJ6gX4NlW', 'Sandra Milagros Quesada Cruz', 'Validador', 'Oficina Iquitos', 'INTERMEDIO', TRUE),
('validador_10', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPk4YJ6gX4NlW', 'Eduardo José Rivera Sánchez', 'Validador', 'Oficina Piura', 'BASICO', TRUE),
('validador_11', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPk4YJ6gX4NlW', 'Lucía Esperanza Torres Pérez', 'Validador', 'Oficina Tacna', 'BASICO', TRUE),
('validador_12', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPk4YJ6gX4NlW', 'Fernando Alberto Campos Díaz', 'Validador Senior', 'Oficina Pucallpa', 'AVANZADO', TRUE);

-- =====================================================
-- DATOS DE CIUDADANOS
-- =====================================================

-- Insertar ciudadanos de ejemplo de diferentes departamentos
INSERT INTO ciudadanos (dni, nombre, apellido_paterno, apellido_materno, fecha_nacimiento, lugar_nacimiento, genero, estado_civil, direccion, distrito, provincia, departamento, telefono, email, es_verificado, fecha_verificacion, activo) VALUES
-- Lima y Callao
('12345678', 'Juan Carlos', 'Martínez', 'González', '1985-03-15', 'Lima, Lima', 'M', 'CASADO', 'Av. 2 de Mayo 1234', 'San Isidro', 'Lima', 'Lima', '987654321', 'juan.martinez@email.com', TRUE, '2024-01-15 10:30:00', TRUE),
('23456789', 'María Elena', 'Rodríguez', 'López', '1990-07-22', 'Lima, Lima', 'F', 'SOLTERO', 'Jr. De la Unión 456', 'Cercado de Lima', 'Lima', 'Lima', '987654322', 'maria.rodriguez@email.com', TRUE, '2024-02-10 14:20:00', TRUE),
('34567890', 'Carlos Alberto', 'Vásquez', 'Mendoza', '1978-11-08', 'Callao, Callao', 'M', 'DIVORCIADO', 'Av. Argentina 789', 'Callao', 'Callao', 'Callao', '987654323', 'carlos.vasquez@email.com', TRUE, '2024-01-20 09:15:00', TRUE),
('45678901', 'Ana Patricia', 'González', 'Torres', '1995-05-30', 'Lima, Lima', 'F', 'CONVIVIENTE', 'Calle Los Olivos 321', 'La Molina', 'Lima', 'Lima', '987654324', 'ana.gonzalez@email.com', TRUE, '2024-03-05 16:45:00', TRUE),
('56789012', 'Miguel Ángel', 'Hernández', 'Silva', '1982-09-14', 'Lima, Lima', 'M', 'CASADO', 'Av. Universitaria 654', 'San Juan de Lurigancho', 'Lima', 'Lima', '987654325', 'miguel.hernandez@email.com', TRUE, '2024-02-28 11:30:00', TRUE),

-- Arequipa
('67890123', 'Carmen Rosa', 'Flores', 'Quispe', '1987-12-03', 'Arequipa, Arequipa', 'F', 'CASADO', 'Calle Mercaderes 147', 'Cercado', 'Arequipa', 'Arequipa', '987654326', 'carmen.floris@email.com', TRUE, '2024-01-10 13:20:00', TRUE),
('78901234', 'José Luis', 'Mamani', 'Condori', '1993-04-18', 'Arequipa, Arequipa', 'M', 'SOLTERO', 'Av. Independencia 852', 'Cercado', 'Arequipa', 'Arequipa', '987654327', 'jose.mamani@email.com', TRUE, '2024-03-12 08:50:00', TRUE),
('89012345', 'Lucía Esperanza', 'Cutipa', 'Machuca', '1991-08-25', 'Camaná, Arequipa', 'F', 'CASADO', 'Jr. Grau 369', 'Camaná', 'Camaná', 'Arequipa', '987654328', 'lucia.cutipa@email.com', TRUE, '2024-02-15 15:10:00', TRUE),

-- Cusco
('90123456', 'Pedro Antonio', 'Quispe', 'Mamani', '1984-01-07', 'Cusco, Cusco', 'M', 'VIUDO', 'Av. El Sol 123', 'Cercado', 'Cusco', 'Cusco', '987654329', 'pedro.quispe@email.com', TRUE, '2024-01-25 10:00:00', TRUE),
('01234567', 'Rosa María', 'Huamán', 'Sallo', '1989-06-12', 'Urubamba, Cusco', 'F', 'CONVIVIENTE', 'Calle Petra 456', 'Urubamba', 'Urubamba', 'Cusco', '987654330', 'rosa.huaman@email.com', TRUE, '2024-03-20 12:30:00', TRUE),

-- Piura
('13579246', 'Roberto Carlos', 'García', 'Pérez', '1986-10-30', 'Piura, Piura', 'M', 'SOLTERO', 'Av. Grau 789', 'Piura', 'Piura', 'Piura', '987654331', 'roberto.garcia@email.com', TRUE, '2024-02-05 14:45:00', TRUE),
('24681357', 'Sandra Milagros', 'Castillo', 'Torres', '1992-02-14', 'Sullana, Piura', 'F', 'CASADO', 'Calle San Miguel 321', 'Sullana', 'Sullana', 'Piura', '987654332', 'sandra.castillo@email.com', TRUE, '2024-01-30 09:20:00', TRUE),

-- Lambayeque
('35792468', 'Eduardo José', 'Castro', 'Rodríguez', '1983-07-20', 'Chiclayo, Lambayeque', 'M', 'CASADO', 'Av. Balta 654', 'Chiclayo', 'Chiclayo', 'Lambayeque', '987654333', 'eduardo.castro@email.com', TRUE, '2024-03-10 16:00:00', TRUE),
('46813579', 'Patricia Elena', 'Díaz', 'Sánchez', '1990-11-05', 'Lambayeque, Lambayeque', 'F', 'DIVORCIADO', 'Calle Tacna 987', 'Lambayeque', 'Lambayeque', 'Lambayeque', '987654334', 'patricia.diaz@email.com', TRUE, '2024-02-18 11:15:00', TRUE),

-- La Libertad
('57924680', 'Fernando Alberto', 'Morales', 'Vargas', '1988-12-28', 'Trujillo, La Libertad', 'M', 'SOLTERO', 'Av. España 147', 'Trujillo', 'Trujillo', 'La Libertad', '987654335', 'fernando.morales@email.com', TRUE, '2024-03-25 13:40:00', TRUE),
('68035791', 'Silvia Cristina', 'León', 'Jiménez', '1987-04-16', 'Trujillo, La Libertad', 'F', 'CONVIVIENTE', 'Calle Pizarro 258', 'Trujillo', 'Trujillo', 'La Libertad', '987654336', 'silvia.leon@email.com', TRUE, '2024-01-12 10:25:00', TRUE),

-- Junín
('79146802', 'Luis Enrique', 'Torres', 'Campos', '1985-09-03', 'Huancayo, Junín', 'M', 'CASADO', 'Av. Ferrocarril 369', 'Huancayo', 'Huancayo', 'Junín', '987654337', 'luis.torres@email.com', TRUE, '2024-02-22 15:30:00', TRUE),
('80257913', 'Gloria María', 'Espinoza', 'Rojas', '1994-05-17', 'Jauja, Junín', 'F', 'SOLTERO', 'Calle Plaza 480', 'Jauja', 'Jauja', 'Junín', '987654338', 'gloria.espinoza@email.com', TRUE, '2024-03-18 08:45:00', TRUE),

-- Ancash
('91368024', 'Alberto Rafael', 'Cordero', 'Salazar', '1989-08-11', 'Huaraz, Ancash', 'M', 'CASADO', 'Av. Confraternidad 591', 'Huaraz', 'Huaraz', 'Ancash', '987654339', 'alberto.cordero@email.com', TRUE, '2024-01-28 12:20:00', TRUE),
('02479135', 'Rosa Esperanza', 'Vargas', 'Ortega', '1991-03-25', 'Chimbote, Ancash', 'F', 'CASADO', 'Calle Los Andes 602', 'Santa', 'Santa', 'Ancash', '987654340', 'rosa.vargas@email.com', TRUE, '2024-02-14 14:50:00', TRUE),

-- Ica
('13580246', 'Javier Alexander', 'Mendoza', 'Bravo', '1986-06-08', 'Ica, Ica', 'M', 'SOLTERO', 'Av. Grau 713', 'Ica', 'Ica', 'Ica', '987654341', 'javier.mendoza@email.com', TRUE, '2024-03-08 09:35:00', TRUE),
('24691357', 'Mónica Lucia', 'Paredes', 'Herrera', '1993-10-22', 'Chincha, Ica', 'F', 'CONVIVIENTE', 'Calle San Martín 824', 'Chincha Alta', 'Chincha', 'Ica', '987654342', 'monica.paredes@email.com', TRUE, '2024-01-18 16:15:00', TRUE),

-- Tacna
('35702468', 'Oscar Daniel', 'Cruz', 'Quispe', '1984-11-14', 'Tacna, Tacna', 'M', 'CASADO', 'Av. Bolognesi 935', 'Tacna', 'Tacna', 'Tacna', '987654343', 'oscar.cruz@email.com', TRUE, '2024-02-26 11:55:00', TRUE),
('46813579', 'Yolanda Guadalupe', 'Mamani', 'Mamani', '1990-07-09', 'Tarata, Tacna', 'F', 'CASADO', 'Calle Lima 1046', 'Tarata', 'Tarata', 'Tacna', '987654344', 'yolanda.mamani@email.com', TRUE, '2024-03-22 13:05:00', TRUE),

-- Puno
('57924680', 'Víctor Hugo', 'Coaquira', 'Huanca', '1987-12-01', 'Puno, Puno', 'M', 'SOLTERO', 'Av. De la Cultura 1157', 'Puno', 'Puno', 'Puno', '987654345', 'victor.coaquira@email.com', TRUE, '2024-01-22 10:40:00', TRUE),
('68035791', 'Julia Rosmery', 'Mamani', 'Quispe', '1992-04-19', 'Juliaca, Puno', 'F', 'SOLTERO', 'Calle脊椎 Roosevelt 1268', 'Juliaca', 'San Román', 'Puno', '987654346', 'julia.mamani@email.com', TRUE, '2024-03-15 15:25:00', TRUE),

-- Madre de Dios
('79146802', 'Raúl Ernesto', 'Rengifo', 'Pinedo', '1988-08-27', 'Puerto Maldonado, Madre de Dios', 'M', 'CONVIVIENTE', 'Av.善良美洲 1379', 'Tahuamanu', 'Tahuamanu', 'Madre de Dios', '987654347', 'raul.rengifo@email.com', TRUE, '2024-02-08 12:10:00', TRUE),
('80257913', 'Celia Amparo', 'Ruiz', 'García', '1989-02-13', 'Tahuamanu, Madre de Dios', 'F', 'CONVIVIENTE', 'Jr. Los Claveles 1390', 'Tahuamanu', 'Tahuamanu', 'Madre de Dios', '987654348', 'celia.ruiz@email.com', TRUE, '2024-03-05 14:30:00', TRUE),

-- Casos especiales
('99999999', 'Ciudadano', 'Inactivo', 'Temporal', '1990-01-01', 'Lima, Lima', 'M', 'SOLTERO', 'Dirección Temporal', 'Lima', 'Lima', 'Lima', '987654349', 'inactivo@email.com', FALSE, NULL, FALSE),
('88888888', 'Juan Pérez', 'Pendiente', 'Verificación', '1985-05-15', 'Lima, Lima', 'M', 'SOLTERO', 'Dirección Pendiente', 'Lima', 'Lima', 'Lima', '987654350', 'pendiente@email.com', FALSE, NULL, TRUE),
('77777777', 'Usuario', 'Bloqueado', 'Sistema', '1980-12-31', 'Lima, Lima', 'M', 'DIVORCIADO', 'Dirección Bloqueada', 'Lima', 'Lima', 'Lima', '987654351', 'bloqueado@email.com', TRUE, '2024-01-01 00:00:00', FALSE);

-- =====================================================
-- DATOS DE SESIONES DE EJEMPLO
-- =====================================================

-- Sesiones activas recientes
INSERT INTO reniec_sessions (validador_id, token_sesion, ip_address, user_agent, fecha_inicio, fecha_ultimo_uso, fecha_expiracion, activa, operaciones_realizadas, datos_consultados) VALUES
(1, 'RENIEC_1_1738137200', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-01-30 08:30:00', '2025-01-30 09:15:00', '2025-01-30 16:30:00', TRUE, 25, '["consulta_dni", "verificacion_identidad", "actualizacion_datos"]'),
(2, 'RENIEC_2_1738138100', '192.168.1.101', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', '2025-01-30 08:45:00', '2025-01-30 09:20:00', '2025-01-30 16:45:00', TRUE, 18, '["busqueda_ciudadano", "validacion_documento"]'),
(3, 'RENIEC_3_1738138900', '192.168.1.102', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36', '2025-01-30 09:00:00', '2025-01-30 09:25:00', '2025-01-30 17:00:00', TRUE, 12, '["consulta_estado_civil", "generacion_reporte"]');

-- Sesiones expiradas
INSERT INTO reniec_sessions (validador_id, token_sesion, ip_address, user_agent, fecha_inicio, fecha_ultimo_uso, fecha_expiracion, activa, operaciones_realizadas, datos_consultados) VALUES
(4, 'RENIEC_4_1738051500', '192.168.1.103', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-01-29 08:00:00', '2025-01-29 15:30:00', '2025-01-29 16:00:00', FALSE, 35, '["consulta_masiva", "verificacion_lote"]'),
(5, 'RENIEC_5_1737965100', '192.168.1.104', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', '2025-01-28 10:15:00', '2025-01-28 17:45:00', '2025-01-28 18:15:00', FALSE, 42, '["actualizacion_datos", "auditoria_operaciones"]');

-- =====================================================
-- DATOS DE AUDITORÍA DE EJEMPLO
-- =====================================================

-- Auditorías recientes de operaciones importantes
INSERT INTO auditoria (tabla_afectada, registro_id, accion, validador_id, session_id, datos_nuevos, ip_address, timestamp_operacion, observaciones) VALUES
('ciudadanos', 1, 'INSERT', 1, 1, '{"dni": "12345678", "nombre_completo": "Juan Carlos Martínez González", "estado": "verificado"}', '192.168.1.100', '2025-01-30 08:30:00', 'Registro inicial de ciudadano'),
('ciudadanos', 2, 'UPDATE', 2, 2, '{"dni": "23456789", "estado": "verificado", "cambios": "verificacion_email"}', '192.168.1.101', '2025-01-30 09:15:00', 'Verificación de correo electrónico'),
('ciudadanos', 3, 'INSERT', 3, 3, '{"dni": "34567890", "nombre_completo": "Carlos Alberto Vásquez Mendoza", "estado": "verificado"}', '192.168.1.102', '2025-01-30 09:20:00', 'Nuevo registro de ciudadano'),
('validadores', 1, 'UPDATE', 1, 1, '{"usuario": "admin_reniec", "ultimo_acceso": "2025-01-30 09:15:00", "operaciones": 25}', '192.168.1.100', '2025-01-30 09:15:00', 'Actualización de sesión de administrador'),
('ciudadanos', 5, 'SELECT', 2, 2, '{"dni": "56789012", "operacion": "consulta_datos"}', '192.168.1.101', '2025-01-30 09:10:00', 'Consulta de datos de ciudadano');

-- =====================================================
-- PROCEDIMIENTOS DE VERIFICACIÓN
-- =====================================================

-- Verificar que los datos se insertaron correctamente
SELECT 'Validadores insertados' AS verificacion, COUNT(*) AS total FROM validadores;
SELECT 'Ciudadanos insertados' AS verificacion, COUNT(*) AS total FROM ciudadanos;
SELECT 'Sesiones insertadas' AS verificacion, COUNT(*) AS total FROM reniec_sessions;
SELECT 'Auditorías insertadas' AS verificacion, COUNT(*) AS total FROM auditoria;

-- Mostrar estadísticas por departamento
SELECT 
    departamento,
    COUNT(*) AS total_ciudadanos,
    SUM(CASE WHEN es_verificado = TRUE THEN 1 ELSE 0 END) AS ciudadanos_verificados,
    ROUND(SUM(CASE WHEN es_verificado = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS porcentaje_verificacion
FROM ciudadanos 
WHERE activo = TRUE
GROUP BY departamento
ORDER BY total_ciudadanos DESC;

-- Mostrar distribución de validadores por oficina
SELECT 
    oficina,
    COUNT(*) AS total_validadores,
    nivel_acceso,
    SUM(CASE WHEN activo = TRUE THEN 1 ELSE 0 END) AS validadores_activos
FROM validadores
GROUP BY oficina, nivel_acceso
ORDER BY total_validadores DESC;

-- =====================================================
-- FIN DE DATOS DE PRUEBA
-- =====================================================
