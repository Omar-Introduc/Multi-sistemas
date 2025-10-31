# Configuración de Base de Datos para Testing
# ===========================================

-- Crear base de datos de testing
CREATE DATABASE testing_db;

-- Conectar a la base de datos de testing
\c testing_db;

-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Tabla de cuentas bancarias
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(20) UNIQUE NOT NULL,
    dni VARCHAR(8) NOT NULL,
    name VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'PEN',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de transacciones
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(36) UNIQUE DEFAULT uuid_generate_v4(),
    from_account VARCHAR(20) NOT NULL,
    to_account VARCHAR(20) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'PEN',
    transaction_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de ciudadanos (sincronizada con RENIEC)
CREATE TABLE IF NOT EXISTS citizens (
    id SERIAL PRIMARY KEY,
    dni VARCHAR(8) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    birth_date DATE,
    birth_place VARCHAR(100),
    gender VARCHAR(1),
    civil_status VARCHAR(20),
    nationality VARCHAR(50) DEFAULT 'Peruana',
    address TEXT,
    phone VARCHAR(15),
    email VARCHAR(100),
    verification_status VARCHAR(20) DEFAULT 'unverified',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de documentos
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(36) UNIQUE DEFAULT uuid_generate_v4(),
    citizen_dni VARCHAR(8) NOT NULL REFERENCES citizens(dni),
    document_type VARCHAR(50) NOT NULL,
    document_number VARCHAR(50),
    issue_date DATE,
    expiry_date DATE,
    issuing_authority VARCHAR(100),
    document_status VARCHAR(20) DEFAULT 'valid',
    file_path TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de logs de testing
CREATE TABLE IF NOT EXISTS test_logs (
    id SERIAL PRIMARY KEY,
    test_suite VARCHAR(50) NOT NULL,
    test_name VARCHAR(100) NOT NULL,
    execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    duration_ms INTEGER,
    error_message TEXT,
    metadata JSONB
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_accounts_dni ON accounts(dni);
CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts(status);
CREATE INDEX IF NOT EXISTS idx_transactions_from_account ON transactions(from_account);
CREATE INDEX IF NOT EXISTS idx_transactions_to_account ON transactions(to_account);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_citizens_dni ON citizens(dni);
CREATE INDEX IF NOT EXISTS idx_documents_citizen_dni ON documents(citizen_dni);
CREATE INDEX IF NOT EXISTS idx_test_logs_suite_execution ON test_logs(test_suite, execution_time);

-- Triggers para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar triggers a tablas principales
CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_citizens_updated_at BEFORE UPDATE ON citizens FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Datos de prueba para testing
INSERT INTO accounts (account_id, dni, name, lastname, balance, currency) VALUES
    ('12345678901', '12345678', 'Juan Carlos', 'Pérez García', 1500.50, 'PEN'),
    ('98765432109', '87654321', 'María Elena', 'González López', 2500.00, 'PEN'),
    ('55554444333', '11223344', 'Ana Sofía', 'Ramírez Vega', 750.25, 'PEN'),
    ('9999888777', '55667788', 'Carlos Roberto', 'Martínez Silva', 3200.75, 'PEN')
ON CONFLICT (account_id) DO NOTHING;

INSERT INTO citizens (dni, name, lastname, birth_date, gender, civil_status, verification_status) VALUES
    ('12345678', 'Juan Carlos', 'Pérez García', '1990-05-15', 'M', 'single', 'verified'),
    ('87654321', 'María Elena', 'González López', '1985-03-22', 'F', 'married', 'verified'),
    ('11223344', 'Ana Sofía', 'Ramírez Vega', '1992-11-10', 'F', 'single', 'pending'),
    ('55667788', 'Carlos Roberto', 'Martínez Silva', '1988-07-08', 'M', 'divorced', 'verified'),
    ('99887766', 'Lucia Fernanda', 'Torres Castillo', '1995-01-30', 'F', 'single', 'unverified')
ON CONFLICT (dni) DO NOTHING;

INSERT INTO transactions (from_account, to_account, amount, transaction_type, status, description) VALUES
    ('12345678901', '98765432109', 100.00, 'transfer', 'completed', 'Transferencia de prueba'),
    ('98765432109', '55554444333', 250.00, 'transfer', 'completed', 'Pago de servicios'),
    ('55554444333', '9999888777', 75.50, 'transfer', 'pending', 'Pago pendiente'),
    ('12345678901', '99887766', 50.00, 'transfer', 'failed', 'Fondos insuficientes')
ON CONFLICT (transaction_id) DO NOTHING;

-- Vistas útiles para testing
CREATE OR REPLACE VIEW test_account_summary AS
SELECT 
    a.account_id,
    a.dni,
    c.name || ' ' || c.lastname AS full_name,
    a.balance,
    a.currency,
    a.status,
    COUNT(t.id) AS transaction_count,
    COALESCE(SUM(CASE WHEN t.status = 'completed' THEN t.amount ELSE 0 END), 0) AS total_completed_amount
FROM accounts a
LEFT JOIN citizens c ON a.dni = c.dni
LEFT JOIN transactions t ON a.account_id = t.from_account OR a.account_id = t.to_account
GROUP BY a.account_id, a.dni, c.name, c.lastname, a.balance, a.currency, a.status;

-- Funciones auxiliares para testing
CREATE OR REPLACE FUNCTION reset_test_account_balance(account_id_param VARCHAR(20), new_balance DECIMAL)
RETURNS BOOLEAN AS $$
DECLARE
    account_exists BOOLEAN;
BEGIN
    SELECT EXISTS(SELECT 1 FROM accounts WHERE account_id = account_id_param) INTO account_exists;
    
    IF account_exists THEN
        UPDATE accounts 
        SET balance = new_balance, updated_at = CURRENT_TIMESTAMP
        WHERE account_id = account_id_param;
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Función para limpiar datos de testing
CREATE OR REPLACE FUNCTION clean_testing_data()
RETURNS INTEGER AS $$
DECLARE
    rows_affected INTEGER := 0;
BEGIN
    -- Eliminar transacciones de prueba (excepto las últimas 24 horas para mantener historial)
    DELETE FROM transactions 
    WHERE created_at < NOW() - INTERVAL '1 day' 
    AND transaction_type = 'transfer' 
    AND description LIKE '%prueba%' OR description LIKE '%test%';
    
    GET DIAGNOSTICS rows_affected = ROW_COUNT;
    
    -- Resetear balances de cuentas de prueba
    UPDATE accounts 
    SET balance = CASE 
        WHEN account_id = '12345678901' THEN 1500.50
        WHEN account_id = '98765432109' THEN 2500.00
        WHEN account_id = '55554444333' THEN 750.25
        WHEN account_id = '9999888777' THEN 3200.75
        ELSE balance
    END,
    updated_at = CURRENT_TIMESTAMP
    WHERE account_id IN ('12345678901', '98765432109', '55554444333', '9999888777');
    
    -- Actualizar contadores
    GET DIAGNOSTICS rows_affected = rows_affected + ROW_COUNT;
    
    RETURN rows_affected;
END;
$$ LANGUAGE plpgsql;

-- Configuración de seguridad para testing
-- (En producción, estas configuraciones serían diferentes)
GRANT ALL PRIVILEGES ON DATABASE testing_db TO testing_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO testing_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO testing_user;

-- Comentarios para documentación
COMMENT ON TABLE accounts IS 'Cuentas bancarias para testing del sistema';
COMMENT ON TABLE transactions IS 'Transacciones para validación de flujos';
COMMENT ON TABLE citizens IS 'Datos de ciudadanos sincronizados con RENIEC';
COMMENT ON TABLE documents IS 'Documentos oficiales para verificación';
COMMENT ON TABLE test_logs IS 'Log de ejecuciones de tests para análisis';

COMMENT ON COLUMN accounts.account_id IS 'ID único de cuenta bancaria';
COMMENT ON COLUMN accounts.dni IS 'DNI del titular de la cuenta';
COMMENT ON COLUMN transactions.from_account IS 'Cuenta de origen';
COMMENT ON COLUMN transactions.to_account IS 'Cuenta de destino';
COMMENT ON COLUMN transactions.status IS 'Estado: pending, completed, failed, cancelled';

-- Configuración final
-- Estos comandos se ejecutan al inicializar la base de datos
-- SELECT clean_testing_data(); -- Limpiar datos antiguos
-- SELECT 'Database initialized successfully' AS status;