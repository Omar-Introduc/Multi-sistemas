#!/bin/bash
# =============================================================================
# INIT SCRIPT - POSTGRESQL (BD1) 
# Script de inicialización para la base de datos del servicio Banco
# =============================================================================

set -e

# Variables
PSQL="psql -v ON_ERROR_STOP=1 --username \"$POSTGRES_USER\" --dbname \"$POSTGRES_DB\""

# Esperar a que PostgreSQL esté listo
echo "Esperando a que PostgreSQL esté listo..."
sleep 5

# Crear extensiones necesarias
echo "Creando extensiones..."
$PSQL <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    CREATE EXTENSION IF NOT EXISTS "btree_gin";
    CREATE EXTENSION IF NOT EXISTS "btree_gist";

    -- Crear roles adicionales
    CREATE ROLE banco_readonly WITH LOGIN PASSWORD 'readonly_pass123';
    CREATE ROLE banco_admin WITH LOGIN PASSWORD 'admin_pass123';

    -- Permisos para el rol de lectura
    GRANT CONNECT ON DATABASE banco_db TO banco_readonly;
    GRANT USAGE ON SCHEMA public TO banco_readonly;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO banco_readonly;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO banco_readonly;

    -- Permisos para el rol de administración
    GRANT ALL PRIVILEGES ON DATABASE banco_db TO banco_admin;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO banco_admin;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO banco_admin;

EOSQL

echo "PostgreSQL inicializado correctamente"