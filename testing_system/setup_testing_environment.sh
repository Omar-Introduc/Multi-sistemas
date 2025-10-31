#!/bin/bash
# Script de Configuración Automática del Sistema de Testing
# ========================================================
#
# Este script configura automáticamente el entorno completo para el
# Sistema de Testing Final v2.0, incluyendo dependencias, servicios
# y configuraciones necesarias.
#
# Autor: Testing System v2.0
# Fecha: 2025-10-30

set -e  # Salir en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Variables globales
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
PYTHON_CMD="python3"
PIP_CMD="pip3"

# Funciones de utilidad
print_header() {
    echo -e "${PURPLE}"
    echo "=========================================="
    echo "🎯 Sistema de Testing Final v2.0"
    echo "🚀 Configuración Automática"
    echo "=========================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

check_python_version() {
    local python_version=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    local major=$(echo $python_version | cut -d'.' -f1)
    local minor=$(echo $python_version | cut -d'.' -f2)
    
    if [ "$major" -eq 3 ] && [ "$minor" -ge 8 ]; then
        print_success "Python version: $python_version (compatible)"
        return 0
    else
        print_error "Python version: $python_version (se requiere Python 3.8+)"
        return 1
    fi
}

install_python_dependencies() {
    print_step "Instalando dependencias Python..."
    
    # Actualizar pip
    $PYTHON_CMD -m pip install --upgrade pip
    
    # Instalar dependencias del archivo requirements
    if [ -f "requirements-test.txt" ]; then
        $PYTHON_CMD -m pip install -r requirements-test.txt
        print_success "Dependencias de requirements-test.txt instaladas"
    else
        print_warning "requirements-test.txt no encontrado"
    fi
    
    # Instalar herramientas de testing específicas
    $PYTHON_CMD -m pip install pytest pytest-asyncio pytest-html pytest-xdist \
        requests playwright locust bandit safety coverage memory-profiler \
        psutil matplotlib seaborn pandas jinja2 pyyaml python-dotenv \
        colorama tabulate click responses factory-boy faker httpx \
        selenium beautifulsoup4 lxml
    
    print_success "Dependencias Python instaladas"
}

install_playwright() {
    print_step "Configurando Playwright..."
    
    # Instalar playwright si no está instalado
    if ! $PYTHON_CMD -c "import playwright" 2>/dev/null; then
        $PYTHON_CMD -m pip install playwright
        print_success "Playwright instalado"
    else
        print_success "Playwright ya está instalado"
    fi
    
    # Instalar navegadores
    print_step "Instalando navegadores para Playwright..."
    playwright install chromium
    playwright install-deps chromium
    
    print_success "Playwright configurado"
}

install_docker() {
    print_step "Verificando Docker..."
    
    if ! check_command "docker"; then
        print_warning "Docker no está instalado"
        print_step "Instalando Docker..."
        
        # Detectar distribución de Linux
        if [ -f /etc/debian_version ]; then
            # Ubuntu/Debian
            sudo apt-get update
            sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io
        elif [ -f /etc/redhat-release ]; then
            # CentOS/RHEL/Fedora
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io
            sudo systemctl start docker
            sudo systemctl enable docker
        fi
        
        # Agregar usuario al grupo docker
        sudo usermod -aG docker $USER
        print_success "Docker instalado y configurado"
    else
        print_success "Docker ya está instalado: $(docker --version)"
    fi
    
    # Verificar docker-compose
    if ! check_command "docker-compose"; then
        print_step "Instalando Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        print_success "Docker Compose instalado"
    else
        print_success "Docker Compose ya está instalado: $(docker-compose --version)"
    fi
}

setup_virtual_environment() {
    print_step "Configurando entorno virtual Python..."
    
    if [ ! -d "$VENV_DIR" ]; then
        $PYTHON_CMD -m venv "$VENV_DIR"
        print_success "Entorno virtual creado en $VENV_DIR"
    else
        print_success "Entorno virtual ya existe en $VENV_DIR"
    fi
    
    # Activar entorno virtual
    source "$VENV_DIR/bin/activate"
    print_success "Entorno virtual activado"
}

create_directories() {
    print_step "Creando estructura de directorios..."
    
    directories=(
        "reports"
        "execution_logs"
        "unit_tests"
        "integration_tests"
        "e2e_tests"
        "performance_tests"
        "security_tests"
        "test_data"
        "screenshots"
        "videos"
        "coverage_reports"
        "performance_results"
        "security_reports"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Directorio creado: $dir"
        else
            print_success "Directorio ya existe: $dir"
        fi
    done
}

setup_permissions() {
    print_step "Configurando permisos..."
    
    # Hacer ejecutables los scripts Python
    chmod +x *.py
    
    # Configurar permisos de escritura en directorios
    chmod -R 755 reports execution_logs test_data
    
    print_success "Permisos configurados"
}

configure_services() {
    print_step "Configurando servicios para testing..."
    
    # Crear archivo de configuración para servicios
    cat > testing.env << EOF
# Configuración de servicios para testing
# ======================================

# Base de datos
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=testing_db
POSTGRES_USER=testing_user
POSTGRES_PASSWORD=testing_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6380
REDIS_PASSWORD=testing_redis_pass

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5674
RABBITMQ_USER=testing_rabbit
RABBITMQ_PASSWORD=testing_rabbit_pass

# Servicios de aplicación
LP1_BANCO_URL=http://localhost:8004
LP2_RENIEC_URL=http://localhost:8005
NGINX_URL=http://localhost:8080

# Configuración de testing
TESTING_MODE=true
LOG_LEVEL=INFO
PARALLEL_EXECUTIONS=true
MAX_WORKERS=4
TIMEOUT_SECONDS=300
RETRY_ATTEMPTS=2
COVERAGE_THRESHOLD=80

# Configuración de reportes
REPORTS_DIR=./reports
GENERATE_HTML=true
GENERATE_PDF=false
GENERATE_JSON=true
INCLUDE_SCREENSHOTS=true
INCLUDE_VIDEOS=true

# Notificaciones
NOTIFY_ON_SUCCESS=false
NOTIFY_ON_FAILURE=true
NOTIFY_ON_REGRESSION=true
EMAIL_RECIPIENTS=qa-team@empresa.com,dev-team@empresa.com

# CI/CD
CI_MODE=false
GITHUB_ACTIONS=false
GITLAB_CI=false
JENKINS=false

# Monitoreo
ENABLE_MONITORING=true
MONITORING_INTERVAL=5
METRICS_RETENTION_DAYS=7
EOF
    
    print_success "Archivo de configuración testing.env creado"
}

run_system_validation() {
    print_step "Ejecutando validación del sistema..."
    
    if [ -f "validate_system.py" ]; then
        $PYTHON_CMD validate_system.py --verbose
        print_success "Validación del sistema completada"
    else
        print_warning "validate_system.py no encontrado, saltando validación"
    fi
}

create_startup_scripts() {
    print_step "Creando scripts de inicio..."
    
    # Script de inicio rápido
    cat > quick_start.sh << 'EOF'
#!/bin/bash
# Quick Start Script para Sistema de Testing
echo "🚀 Iniciando testing rápido..."
python run_all_tests.py --validate-system
python run_all_tests.py
EOF
    
    # Script de testing completo
    cat > full_test.sh << 'EOF'
#!/bin/bash
# Full Test Suite Script
echo "🎯 Ejecutando suite completa de testing..."
docker-compose -f docker-compose.testing.yml up --build --abort-on-container-exit
EOF
    
    # Script de desarrollo
    cat > dev_setup.sh << 'EOF'
#!/bin/bash
# Development Setup Script
echo "👨‍💻 Configurando entorno de desarrollo..."
source venv/bin/activate
pip install -e .
make dev-install
EOF
    
    # Hacer ejecutables
    chmod +x quick_start.sh full_test.sh dev_setup.sh
    
    print_success "Scripts de inicio creados"
}

print_final_instructions() {
    echo -e "${CYAN}"
    echo "=========================================="
    echo "🎉 CONFIGURACIÓN COMPLETADA"
    echo "=========================================="
    echo -e "${NC}"
    
    echo -e "${GREEN}✅ Sistema de Testing Final v2.0 configurado exitosamente!${NC}"
    echo ""
    echo -e "${YELLOW}📋 Próximos pasos:${NC}"
    echo "  1. Ejecutar: python validate_system.py"
    echo "  2. Probar: python run_all_tests.py"
    echo "  3. Generar reportes: python generate_final_report.py"
    echo ""
    echo -e "${YELLOW}🚀 Comandos útiles:${NC}"
    echo "  make help          - Mostrar todos los comandos"
    echo "  make setup         - Configuración completa"
    echo "  make test-all      - Ejecutar todos los tests"
    echo "  make validate      - Validar sistema"
    echo "  make clean         - Limpiar archivos temporales"
    echo ""
    echo -e "${YELLOW}🐳 Docker:${NC}"
    echo "  make docker-build  - Construir imagen Docker"
    echo "  make docker-run    - Ejecutar testing en Docker"
    echo "  docker-compose -f docker-compose.testing.yml up --build"
    echo ""
    echo -e "${YELLOW}📊 Reportes:${NC}"
    echo "  Los reportes se guardan en ./reports/"
    echo "  Los logs se guardan en ./execution_logs/"
    echo ""
    echo -e "${GREEN}🎯 ¡Listo para comenzar!${NC}"
}

# Función principal
main() {
    print_header
    
    # Verificar requisitos del sistema
    print_step "Verificando requisitos del sistema..."
    
    if ! check_command "$PYTHON_CMD"; then
        print_error "Python 3 no está instalado"
        exit 1
    fi
    
    if ! check_python_version; then
        print_error "Versión de Python incompatible"
        exit 1
    fi
    
    if ! check_command "git"; then
        print_warning "Git no está instalado (opcional)"
    fi
    
    # Configurar entorno
    setup_virtual_environment
    install_python_dependencies
    install_playwright
    install_docker
    
    # Crear estructura
    create_directories
    setup_permissions
    configure_services
    create_startup_scripts
    
    # Validar sistema
    run_system_validation
    
    # Mostrar instrucciones finales
    print_final_instructions
    
    echo -e "${GREEN}🎉 ¡Configuración exitosa!${NC}"
}

# Verificar argumentos de línea de comandos
case "${1:-}" in
    --help|-h)
        echo "Uso: $0 [opciones]"
        echo ""
        echo "Opciones:"
        echo "  --help, -h     Mostrar esta ayuda"
        echo "  --quick        Instalación rápida"
        echo "  --docker-only  Solo configurar Docker"
        echo "  --no-venv      No crear entorno virtual"
        exit 0
        ;;
    --quick)
        print_step "Instalación rápida seleccionada..."
        install_python_dependencies
        create_directories
        setup_permissions
        create_startup_scripts
        print_success "Instalación rápida completada"
        exit 0
        ;;
    --docker-only)
        install_docker
        print_success "Solo Docker configurado"
        exit 0
        ;;
    --no-venv)
        print_step "Saltando creación de entorno virtual..."
        install_python_dependencies
        install_playwright
        create_directories
        setup_permissions
        configure_services
        create_startup_scripts
        run_system_validation
        print_final_instructions
        exit 0
        ;;
    *)
        # Ejecutar instalación completa
        main
        ;;
esac