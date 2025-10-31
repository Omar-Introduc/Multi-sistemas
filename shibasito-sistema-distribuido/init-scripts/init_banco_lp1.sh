#!/bin/bash

###############################################################################
# SCRIPT DE INICIALIZACIÓN DEL SISTEMA BANCARIO LP1
###############################################################################
# Este script ejecuta todos los scripts SQL necesarios para inicializar
# completamente la base de datos del sistema bancario LP1
#
# Versión: 1.0
# Fecha: 2025-10-30
# Autor: Sistema Bancario LP1
###############################################################################

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con formato
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar dependencias
check_dependencies() {
    print_header "VERIFICANDO DEPENDENCIAS"
    
    if ! command -v mysql &> /dev/null; then
        print_error "MySQL no está instalado o no está en el PATH"
        exit 1
    fi
    print_success "MySQL encontrado"
    
    if ! command -v mysqladmin &> /dev/null; then
        print_error "mysqladmin no está disponible"
        exit 1
    fi
    print_success "mysqladmin encontrado"
}

# Solicitar credenciales de base de datos
get_database_credentials() {
    print_header "CONFIGURACIÓN DE BASE DE DATOS"
    
    read -p "Ingrese el usuario de MySQL [root]: " DB_USER
    DB_USER=${DB_USER:-root}
    
    read -s -p "Ingrese la contraseña de MySQL: " DB_PASSWORD
    echo ""
    
    read -p "Ingrese el nombre de la base de datos [banco_lp1]: " DB_NAME
    DB_NAME=${DB_NAME:-banco_lp1}
    
    # Verificar conexión
    print_info "Verificando conexión a MySQL..."
    if mysql -u"$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1;" &> /dev/null; then
        print_success "Conexión exitosa"
    else
        print_error "No se pudo conectar a MySQL. Verifique credenciales."
        exit 1
    fi
}

# Verificar si la base de datos existe
check_database() {
    print_info "Verificando si la base de datos '$DB_NAME' existe..."
    
    DB_EXISTS=$(mysql -u"$DB_USER" -p"$DB_PASSWORD" -e "SHOW DATABASES LIKE '$DB_NAME';" 2>/dev/null | grep "$DB_NAME")
    
    if [ -n "$DB_EXISTS" ]; then
        print_warning "La base de datos '$DB_NAME' ya existe"
        read -p "¿Desea eliminarla y recrearla? (s/N): " REPLY
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            print_info "Eliminando base de datos existente..."
            mysql -u"$DB_USER" -p"$DB_PASSWORD" -e "DROP DATABASE IF EXISTS $DB_NAME;"
            print_success "Base de datos eliminada"
        else
            print_error "Operación cancelada por el usuario"
            exit 1
        fi
    fi
}

# Ejecutar script SQL
execute_sql_script() {
    local script_path=$1
    local script_name=$2
    
    print_info "Ejecutando $script_name..."
    
    if [ ! -f "$script_path" ]; then
        print_error "El archivo $script_path no existe"
        return 1
    fi
    
    if mysql -u"$DB_USER" -p"$DB_PASSWORD" < "$script_path" 2>/dev/null; then
        print_success "$script_name ejecutado exitosamente"
        return 0
    else
        print_error "Error al ejecutar $script_name"
        print_info "Revise los logs de MySQL para más detalles"
        return 1
    fi
}

# Mostrar resumen de inicialización
show_summary() {
    print_header "RESUMEN DE INICIALIZACIÓN"
    
    # Contar registros
    CLIENTES=$(mysql -u"$DB_USER" -p"$DB_PASSWORD" -D"$DB_NAME" -e "SELECT COUNT(*) FROM clientes;" -s -N)
    CUENTAS=$(mysql -u"$DB_USER" -p"$DB_PASSWORD" -D"$DB_NAME" -e "SELECT COUNT(*) FROM cuentas;" -s -N)
    TRANSACCIONES=$(mysql -u"$DB_USER" -p"$DB_PASSWORD" -D"$DB_NAME" -e "SELECT COUNT(*) FROM transacciones;" -s -N)
    PRESTAMOS=$(mysql -u"$DB_USER" -p"$DB_PASSWORD" -D"$DB_NAME" -e "SELECT COUNT(*) FROM prestamos;" -s -N)
    
    echo -e "${GREEN}Base de datos: ${NC}$DB_NAME"
    echo -e "${GREEN}Clientes: ${NC}$CLIENTES"
    echo -e "${GREEN}Cuentas: ${NC}$CUENTAS"
    echo -e "${GREEN}Transacciones: ${NC}$TRANSACCIONES"
    echo -e "${GREEN}Préstamos: ${NC}$PRESTAMOS"
    echo ""
    print_success "Inicialización completada exitosamente"
}

# Función principal
main() {
    clear
    
    print_header "INICIALIZADOR DEL SISTEMA BANCARIO LP1"
    print_info "Este script inicializará la base de datos completa"
    echo ""
    
    # Verificar dependencias
    check_dependencies
    
    echo ""
    
    # Obtener credenciales
    get_database_credentials
    
    echo ""
    
    # Verificar base de datos
    check_database
    
    echo ""
    
    # Confirmar inicialización
    print_header "CONFIRMACIÓN"
    print_info "Se procederà a:"
    print_info "1. Crear la base de datos $DB_NAME"
    print_info "2. Ejecutar schema_lp1_banco.sql"
    print_info "3. Ejecutar seed_data_lp1.sql"
    print_info "4. Ejecutar indexes_lp1.sql"
    print_info "5. Ejecutar verification_lp1.sql"
    echo ""
    read -p "¿Desea continuar? (s/N): " REPLY
    
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        print_error "Operación cancelada"
        exit 0
    fi
    
    echo ""
    print_header "INICIANDO INICIALIZACIÓN"
    
    # Obtener directorio donde está el script
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    
    # Lista de scripts a ejecutar en orden
    declare -a SCRIPTS=(
        "$SCRIPT_DIR/schema_lp1_banco.sql:Creación de esquema"
        "$SCRIPT_DIR/seed_data_lp1.sql:Inserción de datos de prueba"
        "$SCRIPT_DIR/indexes_lp1.sql:Creación de índices"
        "$SCRIPT_DIR/verification_lp1.sql:Verificación del sistema"
    )
    
    # Ejecutar cada script
    FAILED=0
    for script_info in "${SCRIPTS[@]}"; do
        IFS=':' read -r script_path script_name <<< "$script_info"
        execute_sql_script "$script_path" "$script_name"
        if [ $? -ne 0 ]; then
            FAILED=1
            break
        fi
        echo ""
    done
    
    # Mostrar resultado
    if [ $FAILED -eq 0 ]; then
        echo ""
        show_summary
        echo ""
        print_header "ACCESO A LA BASE DE DATOS"
        print_info "Para conectarse a la base de datos:"
        echo -e "${YELLOW}mysql -u$DB_USER -p$DB_NAME${NC}"
        echo ""
        print_info "Para ejecutar consultas de ejemplo:"
        echo -e "${YELLOW}mysql -u$DB_USER -p$DB_NAME -e 'SELECT * FROM vista_resumen_clientes;'${NC}"
        echo ""
        print_success "¡Sistema Bancario LP1 inicializado correctamente!"
    else
        print_error "La inicialización falló. Revise los errores anteriores."
        exit 1
    fi
}

# Capturar Ctrl+C
trap 'echo -e "\n${YELLOW}Operación cancelada por el usuario${NC}"; exit 1' INT

# Ejecutar función principal
main "$@"