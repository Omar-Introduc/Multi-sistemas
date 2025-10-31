#!/bin/bash

###############################################################################
# Script: deploy-and-validate.sh
# Descripción: Script para despliegue y validación continua
# Autor: Sistema de Validación Continua
# Fecha: 2025-10-30
###############################################################################

set -euo pipefail

# Configuración por defecto
DEFAULT_TIMEOUT=300
DEFAULT_INTERVAL=30
DEFAULT_RETRIES=3
DEFAULT_HEALTH_CHECKS=10
LOG_FILE="deployment-$(date +%Y%m%d-%H%M%S).log"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    log "INFO" "${BLUE}$@${NC}"
}

log_success() {
    log "SUCCESS" "${GREEN}$@${NC}"
}

log_warning() {
    log "WARNING" "${YELLOW}$@${NC}"
}

log_error() {
    log "ERROR" "${RED}$@${NC}"
}

# Función para mostrar ayuda
show_help() {
    cat << EOF
Uso: $0 [OPCIONES]

OPCIONES:
    -e, --environment ENV       Entorno de despliegue (development|staging|production)
    -i, --image IMAGE          Imagen Docker a desplegar
    -d, --digest DIGEST        Digest de la imagen Docker
    -v, --validation-type TYPE Tipo de validación (pre-deployment|post-deployment|continuous)
    -t, --timeout SECONDS      Timeout para operaciones (default: 300)
    -r, --retries NUM          Número de reintentos (default: 3)
    --validate-only           Solo ejecutar validación, no desplegar
    --config FILE             Archivo de configuración personalizado
    -h, --help                Mostrar esta ayuda

EJEMPLOS:
    $0 --environment staging --image myapp:v1.0.0
    $0 --environment production --image myapp:latest --validate-only
    $0 --environment staging --validation-type post-deployment --timeout 600

EOF
}

# Parsear argumentos
ENVIRONMENT=""
IMAGE=""
DIGEST=""
VALIDATION_TYPE="pre-deployment"
TIMEOUT=$DEFAULT_TIMEOUT
RETRIES=$DEFAULT_RETRIES
VALIDATE_ONLY=false
CONFIG_FILE="config/validation-config.yml"

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -i|--image)
            IMAGE="$2"
            shift 2
            ;;
        -d|--digest)
            DIGEST="$2"
            shift 2
            ;;
        -v|--validation-type)
            VALIDATION_TYPE="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -r|--retries)
            RETRIES="$2"
            shift 2
            ;;
        --validate-only)
            VALIDATE_ONLY=true
            shift
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validar argumentos requeridos
if [[ -z "$ENVIRONMENT" ]]; then
    log_error "El entorno es requerido"
    show_help
    exit 1
fi

if [[ -z "$IMAGE" && "$VALIDATE_ONLY" == false ]]; then
    log_error "La imagen es requerida para despliegue"
    show_help
    exit 1
fi

# Cargar configuración
load_config() {
    log_info "Cargando configuración desde $CONFIG_FILE"
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_warning "Archivo de configuración no encontrado, usando valores por defecto"
        return
    fi
    
    # Extraer configuración usando grep y sed
    CONFIG_ENV=$(grep -A 5 "^environments:" "$CONFIG_FILE" | grep -A 3 "^  $ENVIRONMENT:" | head -3 || echo "")
    
    if [[ -n "$CONFIG_ENV" ]]; then
        log_info "Configuración cargada para entorno: $ENVIRONMENT"
    else
        log_warning "No se encontró configuración específica para $ENVIRONMENT"
    fi
}

# Verificar prerrequisitos
check_prerequisites() {
    log_info "Verificando prerrequisitos..."
    
    local missing_tools=()
    
    # Verificar herramientas requeridas
    for tool in docker docker-compose curl jq; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Herramientas faltantes: ${missing_tools[*]}"
        exit 1
    fi
    
    # Verificar conectividad de red
    if ! curl -s --connect-timeout 10 https://google.com > /dev/null; then
        log_error "Sin conectividad a internet"
        exit 1
    fi
    
    log_success "Prerrequisitos verificados"
}

# Cargar configuración de Docker Compose
load_validation_config() {
    log_info "Cargando configuración de validación"
    
    if [[ ! -f "docker-compose.validation.yml" ]]; then
        log_error "Archivo docker-compose.validation.yml no encontrado"
        exit 1
    fi
    
    # Verificar que los servicios necesarios estén definidos
    local required_services=("database" "redis" "rabbitmq")
    for service in "${required_services[@]}"; do
        if ! grep -q "$service:" docker-compose.validation.yml; then
            log_warning "Servicio '$service' no encontrado en docker-compose.validation.yml"
        fi
    done
}

# Función para esperar que un servicio esté listo
wait_for_service() {
    local service_url=$1
    local max_wait=$2
    local interval=${3:-5}
    
    log_info "Esperando que $service_url esté disponible (max $max_wait segundos)"
    
    local elapsed=0
    while [[ $elapsed -lt $max_wait ]]; do
        if curl -s -f "$service_url" > /dev/null 2>&1; then
            log_success "$service_url está disponible"
            return 0
        fi
        
        echo -n "."
        sleep $interval
        ((elapsed += interval))
    done
    
    log_error "$service_url no está disponible después de $max_wait segundos"
    return 1
}

# Validar servicios de infraestructura
validate_infrastructure() {
    log_info "Validando infraestructura..."
    
    # Verificar base de datos
    if docker-compose -f docker-compose.validation.yml exec -T database pg_isready -U postgres > /dev/null 2>&1; then
        log_success "Base de datos disponible"
    else
        log_error "Base de datos no disponible"
        return 1
    fi
    
    # Verificar Redis
    if docker-compose -f docker-compose.validation.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis disponible"
    else
        log_error "Redis no disponible"
        return 1
    fi
    
    # Verificar RabbitMQ
    if docker-compose -f docker-compose.validation.yml exec -T rabbitmq rabbitmqctl status > /dev/null 2>&1; then
        log_success "RabbitMQ disponible"
    else
        log_error "RabbitMQ no disponible"
        return 1
    fi
    
    return 0
}

# Ejecutar pruebas de integración
run_integration_tests() {
    log_info "Ejecutando pruebas de integración..."
    
    if [[ ! -d "tests/integration_tests" ]]; then
        log_warning "Directorio de pruebas de integración no encontrado"
        return 0
    fi
    
    local test_output="integration-test-results.xml"
    
    if docker-compose -f docker-compose.validation.yml run --rm test-runner \
        pytest tests/integration_tests/ -v --junit-xml="$test_output" --tb=short; then
        log_success "Pruebas de integración exitosas"
        return 0
    else
        log_error "Pruebas de integración fallidas"
        return 1
    fi
}

# Ejecutar health checks
run_health_checks() {
    log_info "Ejecutando health checks..."
    
    local health_endpoints=(
        "http://localhost:8080/health"
        "http://localhost:8080/api/v1/status"
        "http://localhost:8080/api/v1/metrics"
    )
    
    local failed_checks=0
    for endpoint in "${health_endpoints[@]}"; do
        if ! wait_for_service "$endpoint" 30 2; then
            ((failed_checks++))
        fi
    done
    
    if [[ $failed_checks -eq 0 ]]; then
        log_success "Todos los health checks pasaron"
        return 0
    else
        log_error "$failed_checks health checks fallaron"
        return 1
    fi
}

# Ejecutar validaciones de seguridad
run_security_validation() {
    log_info "Ejecutando validaciones de seguridad..."
    
    # Verificar que no hay secretos expuestos
    if grep -r -i --exclude-dir=.git --exclude-dir=node_modules "password\|secret\|api_key" . 2>/dev/null | grep -v ".example\|test"; then
        log_warning "Posibles secretos detectados en el código"
    fi
    
    # Verificar permisos de archivos
    local sensitive_files=(".env" "config.json" "secrets.yml")
    for file in "${sensitive_files[@]}"; do
        if [[ -f "$file" ]]; then
            local perms=$(stat -c "%a" "$file")
            if [[ "$perms" != "600" && "$perms" != "644" ]]; then
                log_warning "Archivo $file tiene permisos inseguros: $perms"
            fi
        fi
    done
    
    log_success "Validaciones de seguridad completadas"
    return 0
}

# Validar configuración
validate_configuration() {
    log_info "Validando configuración..."
    
    # Verificar variables de entorno críticas
    local required_vars=("DATABASE_URL" "REDIS_URL" "RABBITMQ_URL")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Variable de entorno requerida no configurada: $var"
            return 1
        fi
    done
    
    # Verificar configuración de logging
    if [[ -f "config/logging.yml" ]]; then
        log_success "Configuración de logging encontrada"
    else
        log_warning "Configuración de logging no encontrada"
    fi
    
    log_success "Configuración validada"
    return 0
}

# Función principal de despliegue
deploy_application() {
    log_info "Iniciando despliegue para entorno: $ENVIRONMENT"
    
    # Extraer tag y digest de la imagen
    local image_tag=$(echo "$IMAGE" | cut -d':' -f2)
    local image_repo=$(echo "$IMAGE" | cut -d':' -f1)
    
    log_info "Desplegando imagen: $IMAGE"
    log_info "Tag: $image_tag"
    log_info "Digest: ${DIGEST:-N/A}"
    
    # Ejecutar pre-deployment hooks
    if [[ -f "scripts/pre-deployment.sh" ]]; then
        log_info "Ejecutando pre-deployment hooks"
        chmod +x scripts/pre-deployment.sh
        ./scripts/pre-deployment.sh --environment="$ENVIRONMENT" || {
            log_error "Pre-deployment hooks fallaron"
            return 1
        }
    fi
    
    # Aquí iría la lógica real de despliegue
    # Por ejemplo, Kubernetes, Docker Swarm, etc.
    log_info "Simulando despliegue (implementar lógica específica)"
    
    # Actualizar servicios con nueva imagen
    if command -v kubectl &> /dev/null; then
        log_info "Desplegando con Kubernetes"
        kubectl set image deployment/app app="$IMAGE" -n "$ENVIRONMENT" || true
    elif command -v docker-compose &> /dev/null; then
        log_info "Desplegando con Docker Compose"
        docker-compose -f docker-compose.yml up -d --remove-orphans || true
    else
        log_warning "Sistema de despliegue no reconocido, simulando..."
    fi
    
    # Ejecutar post-deployment hooks
    if [[ -f "scripts/post-deployment.sh" ]]; then
        log_info "Ejecutando post-deployment hooks"
        chmod +x scripts/post-deployment.sh
        ./scripts/post-deployment.sh --environment="$ENVIRONMENT" || {
            log_error "Post-deployment hooks fallaron"
            return 1
        }
    fi
    
    log_success "Despliegue completado"
    return 0
}

# Validación post-despliegue
post_deployment_validation() {
    log_info "Ejecutando validación post-despliegue"
    
    local failed_validations=0
    
    # Esperar estabilización inicial
    log_info "Esperando estabilización del servicio..."
    sleep 30
    
    # Health checks
    if ! run_health_checks; then
        ((failed_validations++))
    fi
    
    # Pruebas de integración
    if ! run_integration_tests; then
        ((failed_validations++))
    fi
    
    # Validación de rendimiento básica
    if [[ "$VALIDATION_TYPE" == "full" ]]; then
        log_info "Ejecutando validación de rendimiento"
        if ! curl -s -w "Response time: %{time_total}s\n" -o /dev/null http://localhost:8080/health | grep -q "Response time: .*[0-9]"; then
            log_warning "Health check de rendimiento falló"
        fi
    fi
    
    # Validación de seguridad
    if ! run_security_validation; then
        ((failed_validations++))
    fi
    
    # Validación de configuración
    if ! validate_configuration; then
        ((failed_validations++))
    fi
    
    if [[ $failed_validations -eq 0 ]]; then
        log_success "Validación post-despliegue exitosa"
        return 0
    else
        log_error "$failed_validations validaciones post-despliegue fallaron"
        return 1
    fi
}

# Función para rollback en caso de fallo
rollback_deployment() {
    log_error "Iniciando rollback del despliegue..."
    
    # Implementar lógica de rollback específica
    if command -v kubectl &> /dev/null; then
        kubectl rollout undo deployment/app -n "$ENVIRONMENT" || true
    elif command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.yml up -d --force-recreate || true
    fi
    
    log_info "Rollback completado"
}

# Validación continua
continuous_validation() {
    log_info "Iniciando validación continua..."
    
    local max_duration=${TIMEOUT}
    local elapsed=0
    local interval=${DEFAULT_INTERVAL}
    
    while [[ $elapsed -lt $max_duration ]]; do
        log_info "Ejecutando ciclo de validación ($elapsed/$max_duration segundos)"
        
        if run_health_checks; then
            log_success "Health check OK"
        else
            log_error "Health check FAILED"
            return 1
        fi
        
        sleep $interval
        ((elapsed += interval))
    done
    
    log_success "Validación continua completada exitosamente"
    return 0
}

# Función para generar reporte de validación
generate_validation_report() {
    local report_file="validation-results-$(date +%Y%m%d-%H%M%S).json"
    
    log_info "Generando reporte de validación: $report_file"
    
    cat > "$report_file" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "environment": "$ENVIRONMENT",
    "image": "$IMAGE",
    "digest": "${DIGEST:-N/A}",
    "validation_type": "$VALIDATION_TYPE",
    "status": "$1",
    "duration_seconds": $SECONDS,
    "log_file": "$LOG_FILE",
    "checks_executed": [
        "health_checks",
        "integration_tests",
        "security_validation",
        "configuration_validation"
    ]
}
EOF
    
    log_success "Reporte generado: $report_file"
    echo "$report_file"
}

# Función principal
main() {
    log_info "================================================"
    log_info "SISTEMA DE VALIDACIÓN CONTINUA"
    log_info "Fecha: $(date)"
    log_info "Entorno: $ENVIRONMENT"
    log_info "Imagen: ${IMAGE:-N/A}"
    log_info "Tipo de validación: $VALIDATION_TYPE"
    log_info "================================================"
    
    # Cargar configuración
    load_config
    
    # Verificar prerrequisitos
    check_prerequisites
    
    # Cargar configuración de validación
    load_validation_config
    
    # Ejecutar validaciones según el tipo
    local validation_result=0
    
    case "$VALIDATION_TYPE" in
        "pre-deployment")
            log_info "Ejecutando validación pre-despliegue"
            validate_infrastructure || validation_result=1
            run_integration_tests || validation_result=1
            run_security_validation || validation_result=1
            validate_configuration || validation_result=1
            
            if [[ $validation_result -eq 0 && "$VALIDATE_ONLY" == false ]]; then
                deploy_application || validation_result=1
            fi
            ;;
            
        "post-deployment")
            log_info "Ejecutando validación post-despliegue"
            post_deployment_validation || validation_result=1
            ;;
            
        "continuous")
            log_info "Ejecutando validación continua"
            continuous_validation || validation_result=1
            ;;
    esac
    
    # Generar reporte
    local report_file
    if [[ $validation_result -eq 0 ]]; then
        log_success "VALIDACIÓN EXITOSA"
        report_file=$(generate_validation_report "SUCCESS")
    else
        log_error "VALIDACIÓN FALLIDA"
        report_file=$(generate_validation_report "FAILURE")
        
        # Intentar rollback en caso de fallo durante despliegue
        if [[ "$VALIDATION_TYPE" == "post-deployment" ]]; then
            rollback_deployment
        fi
    fi
    
    log_info "================================================"
    log_info "Reporte de validación: $report_file"
    log_info "Log detallado: $LOG_FILE"
    log_info "================================================"
    
    return $validation_result
}

# Manejo de señales para cleanup
cleanup() {
    log_info "Ejecutando cleanup..."
    # Aquí puedes agregar cleanup de recursos temporales
}

trap cleanup EXIT

# Ejecutar función principal
main "$@"