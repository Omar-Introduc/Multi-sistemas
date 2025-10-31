#!/bin/bash

###############################################################################
# Script de ejecución para LP2 RENIEC Service
# 
# Funcionalidades:
# - Configuración de variables de entorno
# - Verificación de conectividad MySQL
# - Verificación de conectividad RabbitMQ
# - Verificación de Redis
# - Health check de servicios
# - Ejecución de uvicorn con --reload
###############################################################################

set -e  # Salir si hay error en algún comando

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging con timestamp
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Banner de inicio
echo -e "${BLUE}"
echo "================================================================"
echo "🚀 LP2 RENIEC Service - Script de Ejecución"
echo "================================================================"
echo -e "${NC}"

# Configuración por defecto
DEFAULT_HOST="${HOST:-0.0.0.0}"
DEFAULT_PORT="${PORT:-8000}"
DEFAULT_DEBUG="${DEBUG:-True}"

# Variables de entorno del servicio
export APP_NAME="${APP_NAME:-LP2 RENIEC Service}"
export DEBUG="${DEBUG:-$DEFAULT_DEBUG}"
export HOST="${HOST:-$DEFAULT_HOST}"
export PORT="${PORT:-$DEFAULT_PORT}"

# Configuración de base de datos MySQL
export DATABASE_HOST="${DATABASE_HOST:-localhost}"
export DATABASE_PORT="${DATABASE_PORT:-3306}"
export DATABASE_USER="${DATABASE_USER:-reniec_user}"
export DATABASE_PASSWORD="${DATABASE_PASSWORD:-password_seguro}"
export DATABASE_NAME="${DATABASE_NAME:-reniec_db}"
export DATABASE_URL="${DATABASE_URL:-mysql+mysqlconnector://$DATABASE_USER:$DATABASE_PASSWORD@$DATABASE_HOST:$DATABASE_PORT/$DATABASE_NAME}"

# Configuración de RabbitMQ
export RABBITMQ_HOST="${RABBITMQ_HOST:-localhost}"
export RABBITMQ_PORT="${RABBITMQ_PORT:-5672}"
export RABBITMQ_USER="${RABBITMQ_USER:-guest}"
export RABBITMQ_PASSWORD="${RABBITMQ_PASSWORD:-guest}"
export RABBITMQ_URL="${RABBITMQ_URL:-amqp://$RABBITMQ_USER:$RABBITMQ_PASSWORD@$RABBITMQ_HOST:$RABBITMQ_PORT/}"

# Configuración de Redis
export REDIS_HOST="${REDIS_HOST:-localhost}"
export REDIS_PORT="${REDIS_PORT:-6379}"
export REDIS_DB="${REDIS_DB:-0}"
export REDIS_PASSWORD="${REDIS_PASSWORD:-}"
export REDIS_URL="${REDIS_URL:-redis://$REDIS_HOST:$REDIS_PORT/$REDIS_DB}"

# Configuración de seguridad
export SECRET_KEY="${SECRET_KEY:-tu-clave-secreta-muy-segura-aqui}"
export ALGORITHM="${ALGORITHM:-HS256}"
export ACCESS_TOKEN_EXPIRE_MINUTES="${ACCESS_TOKEN_EXPIRE_MINUTES:-30}"

# Configuración de RENIEC API externa
export RENIEC_API_URL="${RENIEC_API_URL:-https://api.reniec.gob.pe}"
export RENIEC_API_KEY="${RENIEC_API_KEY:-}"
export RENIEC_TIMEOUT="${RENIEC_TIMEOUT:-30}"

# Configuración de logging
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export LOG_RETENTION_DAYS="${LOG_RETENTION_DAYS:-30}"

# Hosts permitidos
export ALLOWED_HOSTS="${ALLOWED_HOSTS:-\"http://localhost:3000\",\"http://localhost:8080\",\"http://localhost:8000\"}"

# Configuración CORS
export CORS_ALLOW_ORIGINS="${CORS_ALLOW_ORIGINS:-*}"

# Configuración de heartbeat y validación
export VALIDATION_ENABLED="${VALIDATION_ENABLED:-true}"
export VALIDATION_CACHE_TTL="${VALIDATION_CACHE_TTL:-300}"
export HEARTBEAT_ENABLED="${HEARTBEAT_ENABLED:-true}"
export HEARTBEAT_INTERVAL="${HEARTBEAT_INTERVAL:-30}"

log "Configuración de variables de entorno completada"
log "DEBUG: $DEBUG"
log "HOST: $HOST"
log "PORT: $PORT"
log "DATABASE_URL: $DATABASE_URL"
log "RABBITMQ_URL: $RABBITMQ_URL"
log "REDIS_URL: $REDIS_URL"

# Función para verificar si un puerto está en uso
check_port() {
    local port=$1
    local service=$2
    
    if nc -z localhost $port 2>/dev/null; then
        log_success "$service está ejecutándose en puerto $port"
        return 0
    else
        log_warning "$service no está disponible en puerto $port"
        return 1
    fi
}

# Función para verificar conectividad MySQL
check_mysql() {
    log "🔍 Verificando conectividad MySQL..."
    
    local max_attempts=10
    local attempt=1
    local db_host=${DATABASE_HOST}
    local db_port=${DATABASE_PORT}
    
    while [ $attempt -le $max_attempts ]; do
        log "Intento $attempt/$max_attempts - Conectando a MySQL en $db_host:$db_port"
        
        if command -v mysql >/dev/null 2>&1; then
            if mysqladmin ping -h"$db_host" -P"$db_port" -u"$DATABASE_USER" -p"$DATABASE_PASSWORD" --silent; then
                log_success "✅ MySQL está respondiendo correctamente"
                return 0
            fi
        elif command -v nc >/dev/null 2>&1; then
            if check_port $db_port "MySQL"; then
                log_success "✅ MySQL puerto disponible"
                return 0
            fi
        else
            log_warning "Herramientas de diagnóstico no disponibles, verificando puerto manualmente"
            if check_port $db_port "MySQL"; then
                log_success "✅ MySQL puerto disponible"
                return 0
            fi
        fi
        
        if [ $attempt -lt $max_attempts ]; then
            log_warning "MySQL no disponible, esperando 5 segundos..."
            sleep 5
        fi
        
        attempt=$((attempt + 1))
    done
    
    log_error "❌ No se pudo conectar a MySQL después de $max_attempts intentos"
    log_error "Verifica que MySQL esté ejecutándose en $db_host:$db_port"
    return 1
}

# Función para verificar conectividad RabbitMQ
check_rabbitmq() {
    log "🔍 Verificando conectividad RabbitMQ..."
    
    local max_attempts=10
    local attempt=1
    local rabbit_host=${RABBITMQ_HOST}
    local rabbit_port=${RABBITMQ_PORT}
    
    while [ $attempt -le $max_attempts ]; do
        log "Intento $attempt/$max_attempts - Conectando a RabbitMQ en $rabbit_host:$rabbit_port"
        
        if command -v nc >/dev/null 2>&1; then
            if check_port $rabbit_port "RabbitMQ"; then
                log_success "✅ RabbitMQ está respondiendo en el puerto $rabbit_port"
                return 0
            fi
        elif python3 -c "
import socket
import sys
try:
    sock = socket.create_connection(('$rabbit_host', $rabbit_port), timeout=5)
    sock.close()
    sys.exit(0)
except:
    sys.exit(1)
" 2>/dev/null; then
            log_success "✅ RabbitMQ está respondiendo"
            return 0
        fi
        
        if [ $attempt -lt $max_attempts ]; then
            log_warning "RabbitMQ no disponible, esperando 5 segundos..."
            sleep 5
        fi
        
        attempt=$((attempt + 1))
    done
    
    log_error "❌ No se pudo conectar a RabbitMQ después de $max_attempts intentos"
    log_error "Verifica que RabbitMQ esté ejecutándose en $rabbit_host:$rabbit_port"
    return 1
}

# Función para verificar conectividad Redis
check_redis() {
    log "🔍 Verificando conectividad Redis..."
    
    local max_attempts=5
    local attempt=1
    local redis_host=${REDIS_HOST}
    local redis_port=${REDIS_PORT}
    
    while [ $attempt -le $max_attempts ]; do
        log "Intento $attempt/$max_attempts - Conectando a Redis en $redis_host:$redis_port"
        
        if command -v redis-cli >/dev/null 2>&1; then
            if redis-cli -h "$redis_host" -p "$redis_port" ping >/dev/null 2>&1; then
                log_success "✅ Redis está respondiendo correctamente"
                return 0
            fi
        elif command -v nc >/dev/null 2>&1; then
            if check_port $redis_port "Redis"; then
                log_success "✅ Redis puerto disponible"
                return 0
            fi
        else
            log_warning "Verificando conectividad con Python..."
            if python3 -c "
import socket
import sys
try:
    sock = socket.create_connection(('$redis_host', $redis_port), timeout=5)
    sock.close()
    sys.exit(0)
except:
    sys.exit(1)
" 2>/dev/null; then
                log_success "✅ Redis está respondiendo"
                return 0
            fi
        fi
        
        if [ $attempt -lt $max_attempts ]; then
            log_warning "Redis no disponible, esperando 3 segundos..."
            sleep 3
        fi
        
        attempt=$((attempt + 1))
    done
    
    log_warning "⚠️ No se pudo conectar a Redis completamente"
    log_warning "La aplicación puede funcionar sin Redis, pero algunas funcionalidades estarán limitadas"
    return 0  # No es crítico, continuar
}

# Función para crear directorios necesarios
setup_directories() {
    log "📁 Configurando directorios necesarios..."
    
    mkdir -p logs
    mkdir -p uploads
    mkdir -p temp
    
    log_success "✅ Directorios configurados"
}

# Función para health check completo
perform_health_check() {
    log "🏥 Realizando health check de servicios..."
    
    local mysql_ok=0
    local rabbit_ok=0
    local redis_ok=0
    
    # Verificar MySQL
    if check_mysql; then
        mysql_ok=1
    fi
    
    # Verificar RabbitMQ
    if check_rabbitmq; then
        rabbit_ok=1
    fi
    
    # Verificar Redis (no crítico)
    check_redis
    redis_ok=1
    
    # Resumen del health check
    echo
    log "📊 Resumen del Health Check:"
    echo "  MySQL:  $([ $mysql_ok -eq 1 ] && echo -e "${GREEN}✅ OK${NC}" || echo -e "${RED}❌ FAIL${NC}")"
    echo "  RabbitMQ: $([ $rabbit_ok -eq 1 ] && echo -e "${GREEN}✅ OK${NC}" || echo -e "${RED}❌ FAIL${NC}")"
    echo "  Redis: $([ $redis_ok -eq 1 ] && echo -e "${GREEN}✅ OK${NC}" || echo -e "${YELLOW}⚠️ WARNING${NC}")"
    echo
    
    # Verificar si los servicios críticos están disponibles
    if [ $mysql_ok -eq 0 ] || [ $rabbit_ok -eq 0 ]; then
        log_error "❌ Servicios críticos no disponibles. La aplicación puede no funcionar correctamente."
        log_warning "¿Deseas continuar de todos modos? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            log_error "Saliendo debido a servicios no disponibles"
            exit 1
        fi
    fi
    
    log_success "✅ Health check completado"
}

# Función para verificar dependencias
check_dependencies() {
    log "🔍 Verificando dependencias del sistema..."
    
    # Verificar Python
    if ! command -v python3 >/dev/null 2>&1; then
        log_error "❌ Python3 no está instalado"
        exit 1
    fi
    
    log_success "✅ Python3 encontrado: $(python3 --version)"
    
    # Verificar pip
    if ! command -v pip3 >/dev/null 2>&1; then
        log_error "❌ pip3 no está instalado"
        exit 1
    fi
    
    log_success "✅ pip3 encontrado"
    
    # Verificar si las dependencias de Python están instaladas
    log "🔍 Verificando dependencias de Python..."
    if ! python3 -c "import fastapi, uvicorn, sqlalchemy, pika, redis" >/dev/null 2>&1; then
        log_warning "⚠️ Algunas dependencias de Python no están instaladas"
        log "Instalando dependencias..."
        pip3 install -r requirements.txt
    fi
    
    log_success "✅ Dependencias verificadas"
}

# Función principal de inicialización
initialize_app() {
    log "🚀 Inicializando LP2 RENIEC Service..."
    
    setup_directories
    check_dependencies
    perform_health_check
    
    log_success "✅ Aplicación lista para ejecutar"
    echo
}

# Función para mostrar información del servicio
show_service_info() {
    echo -e "${BLUE}"
    echo "📋 Información del Servicio:"
    echo "  🏠 Host: $HOST"
    echo "  🔌 Puerto: $PORT"
    echo "  🗄️  Database: $DATABASE_NAME"
    echo "  🐰 RabbitMQ: $RABBITMQ_HOST:$RABBITMQ_PORT"
    echo "  💾 Redis: $REDIS_HOST:$REDIS_PORT"
    echo "  📖 Documentación: http://$HOST:$PORT/docs"
    echo "  ❤️  Health Check: http://$HOST:$PORT/api/v1/health"
    echo -e "${NC}"
}

# Manejo de señales para cierre limpio
cleanup() {
    log "🔄 Recibida señal de cierre, finalizando aplicación..."
    if [ ! -z "$UVICORN_PID" ]; then
        kill $UVICORN_PID 2>/dev/null || true
        wait $UVICORN_PID 2>/dev/null || true
    fi
    log_success "✅ Aplicación cerrada correctamente"
    exit 0
}

# Configurar trap para señales
trap cleanup SIGINT SIGTERM EXIT

# Función para ejecutar uvicorn
run_uvicorn() {
    log "🔥 Iniciando servidor uvicorn..."
    
    show_service_info
    
    # Configurar variables adicionales para uvicorn
    export PYTHONPATH="${PYTHONPATH:-.}:${PWD}"
    
    # Opciones de uvicorn
    UVICORN_OPTS=(
        "main:app"
        "--host" "$HOST"
        "--port" "$PORT"
        "--log-level" "info"
        "--log-config" "none"
    )
    
    # Agregar --reload solo en modo debug
    if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "true" ]; then
        UVICORN_OPTS+=("--reload")
        log "🔄 Modo DEBUG habilitado - recarga automática activada"
    fi
    
    # Agregar workers solo si no está en modo reload
    if [ "$DEBUG" != "True" ] && [ "$DEBUG" != "true" ]; then
        UVICORN_OPTS+=("--workers" "4")
        log "👥 Ejecutando con 4 workers en modo producción"
    fi
    
    # Mostrar comando de ejecución
    log "Comando de ejecución: uvicorn ${UVICORN_OPTS[*]}"
    echo
    
    # Ejecutar uvicorn en segundo plano para poder manejar señales
    uvicorn "${UVICORN_OPTS[@]}" &
    UVICORN_PID=$!
    
    log "🚀 Servidor iniciado con PID: $UVICORN_PID"
    log "🌐 Accede al servicio en: http://$HOST:$PORT"
    log "📖 Documentación Swagger: http://$HOST:$PORT/docs"
    log "🔍 Para detener el servidor presiona Ctrl+C"
    echo
    
    # Monitorear el proceso
    wait $UVICORN_PID
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -ne 0 ]; then
        log_error "❌ El servidor terminó con código de error: $EXIT_CODE"
    else
        log_success "✅ Servidor terminado normalmente"
    fi
}

# Función principal
main() {
    # Verificar si se debe ejecutar health check únicamente
    if [ "$1" = "health" ]; then
        initialize_app
        exit 0
    fi
    
    # Verificar si se deben verificar servicios únicamente
    if [ "$1" = "check" ]; then
        check_mysql
        check_rabbitmq
        check_redis
        exit 0
    fi
    
    # Inicialización completa
    initialize_app
    
    # Ejecutar el servidor
    run_uvicorn
}

# Mostrar ayuda
show_help() {
    echo -e "${BLUE}LP2 RENIEC Service - Script de Ejecución${NC}"
    echo
    echo "Uso:"
    echo "  $0 [comando]"
    echo
    echo "Comandos disponibles:"
    echo "  (sin comando)  - Ejecutar el servidor con todas las verificaciones"
    echo "  health         - Solo realizar health check de servicios"
    echo "  check          - Verificar conectividad de servicios únicamente"
    echo "  help           - Mostrar esta ayuda"
    echo
    echo "Variables de entorno importantes:"
    echo "  HOST                    - Host del servidor (default: 0.0.0.0)"
    echo "  PORT                    - Puerto del servidor (default: 8000)"
    echo "  DEBUG                   - Modo debug (default: True)"
    echo "  DATABASE_URL            - URL de conexión a MySQL"
    echo "  RABBITMQ_URL            - URL de conexión a RabbitMQ"
    echo "  REDIS_URL               - URL de conexión a Redis"
    echo "  SECRET_KEY              - Clave secreta para JWT"
    echo
    echo "Ejemplos:"
    echo "  $0                      # Ejecutar servidor normalmente"
    echo "  DEBUG=False $0          # Ejecutar en modo producción"
    echo "  PORT=9000 $0            # Ejecutar en puerto personalizado"
    echo "  $0 health               # Solo verificar servicios"
    echo
}

# Procesar argumentos de línea de comandos
case "${1:-}" in
    "help"|"-h"|"--help")
        show_help
        exit 0
        ;;
    "health"|"check"|"")
        main "$1"
        ;;
    *)
        log_error "❌ Comando desconocido: $1"
        show_help
        exit 1
        ;;
esac
