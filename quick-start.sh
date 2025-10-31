#!/bin/bash

###############################################################################
# Script: quick-start.sh
# Descripción: Guía de inicio rápido para el sistema de validación continua
# Autor: Sistema de Validación Continua
# Fecha: 2025-10-30
###############################################################################

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para mostrar banner
show_banner() {
    clear
    echo -e "${BLUE}"
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🚀 SISTEMA DE VALIDACIÓN CONTINUA                          ║
║                                                               ║
║   Guía de Inicio Rápido                                      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Función para mostrar menú
show_menu() {
    echo ""
    echo -e "${GREEN}Selecciona una opción:${NC}"
    echo ""
    echo "1. 📋 Verificar prerrequisitos"
    echo "2. 🔧 Configurar entorno"
    echo "3. 🧪 Ejecutar validación de prueba"
    echo "4. 📊 Generar reporte de ejemplo"
    echo "5. 🚀 Iniciar entorno de validación"
    echo "6. 📖 Ver documentación completa"
    echo "7. ❌ Salir"
    echo ""
}

# Función para verificar prerrequisitos
check_prerequisites() {
    echo -e "${BLUE}=== Verificando Prerrequisitos ===${NC}"
    echo ""
    
    local missing_tools=()
    local required_tools=("docker" "docker-compose" "curl" "git")
    
    for tool in "${required_tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            echo -e "${GREEN}✓${NC} $tool está instalado"
        else
            echo -e "${RED}✗${NC} $tool NO está instalado"
            missing_tools+=("$tool")
        fi
    done
    
    # Verificar Docker Compose V2
    if docker compose version &> /dev/null; then
        echo -e "${GREEN}✓${NC} Docker Compose V2 está disponible"
    else
        echo -e "${YELLOW}⚠${NC} Docker Compose V2 no detectado (V1 funciona)"
    fi
    
    # Verificar archivos del sistema
    echo ""
    echo "Verificando archivos del sistema..."
    
    local required_files=(
        ".github/workflows/validation-pipeline.yml"
        ".gitlab-ci.yml"
        "scripts/deploy-and-validate.sh"
        "scripts/health-monitor.sh"
        "scripts/generate-validation-report.py"
        "config/validation-config.yml"
        "docker-compose.validation.yml"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            echo -e "${GREEN}✓${NC} $file"
        else
            echo -e "${RED}✗${NC} $file (FALTANTE)"
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        echo ""
        echo -e "${RED}Herramientas faltantes:${NC}"
        for tool in "${missing_tools[@]}"; do
            echo "  - $tool"
        done
        echo ""
        echo -e "${YELLOW}Instalar herramientas faltantes para continuar.${NC}"
        return 1
    else
        echo ""
        echo -e "${GREEN}✅ Todos los prerrequisitos están disponibles!${NC}"
        return 0
    fi
}

# Función para configurar entorno
setup_environment() {
    echo -e "${BLUE}=== Configuración del Entorno ===${NC}"
    echo ""
    
    # Crear directorios necesarios
    echo "Creando directorios..."
    mkdir -p logs test-results security-reports coverage playwright-report
    
    # Hacer ejecutables los scripts
    echo "Configurando permisos de scripts..."
    chmod +x scripts/deploy-and-validate.sh 2>/dev/null || echo -e "${YELLOW}⚠${NC} No se pudieron cambiar permisos (requiere sudo)"
    chmod +x scripts/health-monitor.sh 2>/dev/null || echo -e "${YELLOW}⚠${NC} No se pudieron cambiar permisos (requiere sudo)"
    chmod +x scripts/generate-validation-report.py 2>/dev/null || echo -e "${YELLOW}⚠${NC} No se pudieron cambiar permisos (requiere sudo)"
    
    # Crear archivo de ejemplo de configuración
    if [[ ! -f ".env" ]]; then
        echo ""
        echo -e "${YELLOW}¿Deseas crear un archivo .env con configuraciones de ejemplo? (y/n)${NC}"
        read -r create_env
        
        if [[ "$create_env" =~ ^[Yy]$ ]]; then
            cat > .env << 'EOF'
# Configuración del Entorno de Validación

# Base de Datos
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app_validation
DB_HOST=localhost
DB_PORT=5432
DB_NAME=app_validation
DB_USER=postgres
DB_PASSWORD=postgres

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=guest
RABBITMQ_PASSWORD=guest

# Alertas (Opcional)
SLACK_WEBHOOK_URL=
EMAIL_SMTP_HOST=
EMAIL_USERNAME=
EMAIL_PASSWORD=

# Configuración
ENVIRONMENT=development
LOG_LEVEL=INFO
EOF
            echo -e "${GREEN}✓${NC} Archivo .env creado. Edita las variables según tu configuración."
        fi
    fi
    
    # Configurar endpoints personalizados
    echo ""
    echo -e "${YELLOW}¿Deseas crear archivo de endpoints personalizados? (y/n)${NC}"
    read -r create_endpoints
    
    if [[ "$create_endpoints" =~ ^[Yy]$ ]]; then
        cat > endpoints.txt << 'EOF'
# Endpoints para validación personalizada
# Un endpoint por línea
# Ejemplo:
# http://localhost:8080/api/v1/health
# http://localhost:8080/api/v1/status
# http://localhost:8080/api/v1/metrics
EOF
        echo -e "${GREEN}✓${NC} Archivo endpoints.txt creado. Edita con tus endpoints."
    fi
    
    echo ""
    echo -e "${GREEN}✅ Configuración del entorno completada!${NC}"
}

# Función para ejecutar validación de prueba
run_test_validation() {
    echo -e "${BLUE}=== Validación de Prueba ===${NC}"
    echo ""
    
    echo -e "${YELLOW}Selecciona el tipo de validación:${NC}"
    echo "1. Solo validación (sin despliegue)"
    echo "2. Validación completa con despliegue"
    echo "3. Monitoreo continuo (5 minutos)"
    echo ""
    read -p "Opción [1-3]: " validation_option
    
    case $validation_option in
        1)
            echo ""
            echo "Ejecutando validación de prueba..."
            if [[ -f "scripts/deploy-and-validate.sh" ]]; then
                bash scripts/deploy-and-validate.sh \
                    --environment development \
                    --validate-only \
                    --validation-type pre-deployment \
                    --timeout 300
            else
                echo -e "${RED}Script deploy-and-validate.sh no encontrado${NC}"
            fi
            ;;
        2)
            echo ""
            echo "Ejecutando validación completa..."
            if [[ -f "scripts/deploy-and-validate.sh" ]]; then
                bash scripts/deploy-and-validate.sh \
                    --environment development \
                    --validation-type post-deployment \
                    --timeout 600
            else
                echo -e "${RED}Script deploy-and-validate.sh no encontrado${NC}"
            fi
            ;;
        3)
            echo ""
            echo "Iniciando monitoreo continuo por 5 minutos..."
            if [[ -f "scripts/health-monitor.sh" ]]; then
                bash scripts/health-monitor.sh \
                    --environment development \
                    --interval 30 \
                    --duration 300 \
                    --alert-threshold 3
            else
                echo -e "${RED}Script health-monitor.sh no encontrado${NC}"
            fi
            ;;
        *)
            echo -e "${RED}Opción inválida${NC}"
            ;;
    esac
}

# Función para generar reporte de ejemplo
generate_sample_report() {
    echo -e "${BLUE}=== Generando Reporte de Ejemplo ===${NC}"
    echo ""
    
    if [[ -f "scripts/generate-validation-report.py" ]]; then
        echo "Generando reportes de ejemplo..."
        
        # Generar reporte HTML
        python3 scripts/generate-validation-report.py \
            --pipeline-id test-123 \
            --commit abc123def \
            --branch main \
            --environment development \
            --format html \
            --output sample-report || echo -e "${YELLOW}⚠${NC} Error generando reporte (requiere Python y dependencias)"
        
        # Generar todos los formatos
        python3 scripts/generate-validation-report.py \
            --pipeline-id test-456 \
            --commit def456abc \
            --branch develop \
            --environment staging \
            --format all \
            --output complete-report || echo -e "${YELLOW}⚠${NC} Error generando reporte completo"
        
        echo ""
        echo -e "${GREEN}✅ Reportes generados!${NC}"
        echo "Archivos creados:"
        ls -la *report* 2>/dev/null || echo "  (No se encontraron archivos de reporte)"
    else
        echo -e "${RED}Script generate-validation-report.py no encontrado${NC}"
    fi
}

# Función para iniciar entorno de validación
start_validation_environment() {
    echo -e "${BLUE}=== Iniciando Entorno de Validación ===${NC}"
    echo ""
    
    if [[ -f "docker-compose.validation.yml" ]]; then
        echo -e "${YELLOW}¿Qué acción deseas realizar?${NC}"
        echo "1. Iniciar servicios (modo daemon)"
        echo "2. Iniciar servicios (modo interactivo)"
        echo "3. Ver estado de servicios"
        echo "4. Ver logs de un servicio"
        echo "5. Detener servicios"
        echo ""
        read -p "Opción [1-5]: " action
        
        case $action in
            1)
                echo ""
                echo "Iniciando servicios en modo daemon..."
                docker-compose -f docker-compose.validation.yml up -d
                echo ""
                echo "⏳ Esperando que los servicios estén listos..."
                sleep 30
                docker-compose -f docker-compose.validation.yml ps
                ;;
            2)
                echo ""
                echo "Iniciando servicios en modo interactivo..."
                echo "Presiona Ctrl+C para detener"
                docker-compose -f docker-compose.validation.yml up
                ;;
            3)
                echo ""
                docker-compose -f docker-compose.validation.yml ps
                ;;
            4)
                echo ""
                echo "Servicios disponibles:"
                docker-compose -f docker-compose.validation.yml ps --services
                echo ""
                read -p "Nombre del servicio: " service_name
                docker-compose -f docker-compose.validation.yml logs -f "$service_name"
                ;;
            5)
                echo ""
                docker-compose -f docker-compose.validation.yml down
                ;;
            *)
                echo -e "${RED}Opción inválida${NC}"
                ;;
        esac
    else
        echo -e "${RED}docker-compose.validation.yml no encontrado${NC}"
    fi
}

# Función para mostrar documentación
show_documentation() {
    echo -e "${BLUE}=== Documentación ===${NC}"
    echo ""
    
    if [[ -f "README_VALIDACION_CONTINUA.md" ]]; then
        echo -e "${YELLOW}¿Qué sección deseas ver?${NC}"
        echo "1. Información general"
        echo "2. Configuración"
        echo "3. Ejemplos de uso"
        echo "4. Troubleshooting"
        echo "5. Abrir README completo"
        echo ""
        read -p "Opción [1-5]: " doc_option
        
        case $doc_option in
            1)
                head -100 README_VALIDACION_CONTINUA.md
                ;;
            2)
                grep -A 50 "## 📊 Configuración Detallada" README_VALIDACION_CONTINUA.md | head -60
                ;;
            3)
                grep -A 30 "## 🚀 Inicio Rápido" README_VALIDACION_CONTINUA.md | head -40
                ;;
            4)
                grep -A 50 "## 🛠️ Troubleshooting" README_VALIDACION_CONTINUA.md | head -60
                ;;
            5)
                if command -v less &> /dev/null; then
                    less README_VALIDACION_CONTINUA.md
                elif command -v cat &> /dev/null; then
                    cat README_VALIDACION_CONTINUA.md
                fi
                ;;
            *)
                echo -e "${RED}Opción inválida${NC}"
                ;;
        esac
    else
        echo -e "${RED}README_VALIDACION_CONTINUA.md no encontrado${NC}"
    fi
}

# Función para mostrar resumen final
show_summary() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                               ║${NC}"
    echo -e "${GREEN}║   ✅ SISTEMA DE VALIDACIÓN CONTINUA LISTO                      ║${NC}"
    echo -e "${GREEN}║                                                               ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Archivos principales:${NC}"
    echo "  • .github/workflows/validation-pipeline.yml"
    echo "  • .gitlab-ci.yml"
    echo "  • scripts/deploy-and-validate.sh"
    echo "  • scripts/health-monitor.sh"
    echo "  • scripts/generate-validation-report.py"
    echo "  • config/validation-config.yml"
    echo "  • docker-compose.validation.yml"
    echo ""
    echo -e "${BLUE}Próximos pasos:${NC}"
    echo "  1. Configurar secrets en tu plataforma CI/CD"
    echo "  2. Personalizar validation-config.yml para tu entorno"
    echo "  3. Ejecutar primera validación"
    echo "  4. Revisar documentación completa"
    echo ""
    echo -e "${YELLOW}Comandos útiles:${NC}"
    echo "  • Validación manual: ./scripts/deploy-and-validate.sh --environment staging"
    echo "  • Monitoreo continuo: ./scripts/health-monitor.sh --environment production"
    echo "  • Iniciar entorno: docker-compose -f docker-compose.validation.yml up -d"
    echo ""
}

# Función principal
main() {
    show_banner
    
    while true; do
        show_menu
        read -p "Selecciona una opción [1-7]: " choice
        echo ""
        
        case $choice in
            1)
                check_prerequisites
                ;;
            2)
                setup_environment
                ;;
            3)
                run_test_validation
                ;;
            4)
                generate_sample_report
                ;;
            5)
                start_validation_environment
                ;;
            6)
                show_documentation
                ;;
            7)
                show_summary
                echo ""
                exit 0
                ;;
            *)
                echo -e "${RED}Opción inválida. Por favor selecciona 1-7.${NC}"
                ;;
        esac
        
        echo ""
        read -p "Presiona Enter para continuar..."
        show_banner
    done
}

# Ejecutar función principal
main "$@"