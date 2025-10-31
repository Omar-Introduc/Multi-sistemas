#!/bin/bash

###############################################################################
# Script de ejecución para Servicio Banco LP1
# Ejecuta la aplicación Java con configuración completa
###############################################################################

set -e  # Salir en caso de error

# Colores para logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función de logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

###############################################################################
# CONFIGURACIÓN
###############################################################################

# Nombre de la aplicación
APP_NAME="lp1-servicio-banco"
APP_VERSION="1.0.0"

# Directorios
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${APP_DIR}/logs"
PID_FILE="${APP_DIR}/${APP_NAME}.pid"

# Archivo JAR (se puede sobrescribir con variable de entorno)
JAR_FILE="${JAR_FILE:-${APP_DIR}/target/lp1-servicio-banco-*.jar}"

# Puerto por defecto
PORT="${PORT:-8080}"

###############################################################################
# VERIFICACIÓN DE VARIABLES REQUERIDAS
###############################################################################

check_required_vars() {
    local missing_vars=()
    
    # Verificar variables críticas para el servicio banco
    if [[ -z "${DB_HOST}" ]]; then
        missing_vars+=("DB_HOST")
    fi
    
    if [[ -z "${DB_PORT}" ]]; then
        missing_vars+=("DB_PORT")
    fi
    
    if [[ -z "${DB_NAME}" ]]; then
        missing_vars+=("DB_NAME")
    fi
    
    if [[ -z "${DB_USER}" ]]; then
        missing_vars+=("DB_USER")
    fi
    
    if [[ -z "${DB_PASSWORD}" ]]; then
        missing_vars+=("DB_PASSWORD")
    fi
    
    if [[ -z "${JWT_SECRET}" ]]; then
        missing_vars+=("JWT_SECRET")
    fi
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        error "Variables de entorno requeridas faltantes:"
        for var in "${missing_vars[@]}"; do
            error "  - ${var}"
        done
        error "Por favor configure estas variables antes de ejecutar la aplicación"
        exit 1
    fi
    
    log "✓ Todas las variables requeridas están configuradas"
}

###############################################################################
# PREPARACIÓN DEL ENTORNO
###############################################################################

prepare_environment() {
    log "Preparando entorno de ejecución..."
    
    # Crear directorios necesarios
    mkdir -p "${LOG_DIR}"
    
    # Verificar que existe el archivo JAR
    if [[ ! -f "${JAR_FILE}" ]]; then
        # Buscar archivos JAR en el directorio target
        local found_jars=($(find "${APP_DIR}/target" -name "${APP_NAME}-*.jar" 2>/dev/null || true))
        
        if [[ ${#found_jars[@]} -eq 0 ]]; then
            error "No se encontró archivo JAR: ${JAR_FILE}"
            error "Asegúrese de que la aplicación está compilada"
            exit 1
        elif [[ ${#found_jars[@]} -eq 1 ]]; then
            JAR_FILE="${found_jars[0]}"
            info "Usando JAR encontrado: ${JAR_FILE}"
        else
            error "Múltiples archivos JAR encontrados:"
            for jar in "${found_jars[@]}"; do
                error "  - ${jar}"
            done
            error "Configure JAR_FILE para especificar cuál usar"
            exit 1
        fi
    fi
    
    log "✓ Archivo JAR encontrado: ${JAR_FILE}"
    
    # Verificar que Java está instalado
    if ! command -v java &> /dev/null; then
        error "Java no está instalado o no está en PATH"
        exit 1
    fi
    
    local java_version=$(java -version 2>&1 | head -n 1)
    log "✓ Java encontrado: ${java_version}"
}

###############################################################################
# CONFIGURACIÓN DE ARGUMENTOS JVM
###############################################################################

setup_jvm_args() {
    log "Configurando argumentos JVM..."
    
    # Argumentos JVM base
    JVM_ARGS=(
        "-Xms512m"                    # Memoria inicial
        "-Xmx2048m"                   # Memoria máxima
        "-XX:+UseG1GC"               # Garbage Collector G1
        "-XX:MaxGCPauseMillis=200"    # Tiempo máximo de pausa GC
        "-XX:+UseStringDeduplication" # Deduplicación de strings
        "-Djava.awt.headless=true"    # Modo headless
        "-Dfile.encoding=UTF-8"       # Codificación de archivos
        "-Duser.timezone=UTC"         # Zona horaria
    )
    
    # Argumentos adicionales si está habilitado el perfil de desarrollo
    if [[ "${SPRING_PROFILES_ACTIVE}" == *"dev"* ]]; then
        JVM_ARGS+=(
            "-Xdebug"
            "-Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=5005"
        )
        info "Modo DEBUG habilitado en puerto 5005"
    fi
    
    # Argumentos de logging
    JVM_ARGS+=(
        "-Dlogging.level.root=${LOG_LEVEL:-INFO}"
        "-Dlogging.pattern.console=%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
    )
    
    # Argumentos específicos del servicio banco
    JVM_ARGS+=(
        "-Dserver.port=${PORT}"
        "-Dspring.datasource.url=jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME}"
        "-Dspring.datasource.username=${DB_USER}"
        "-Dspring.datasource.password=${DB_PASSWORD}"
        "-Dapp.name=${APP_NAME}"
        "-Dapp.version=${APP_VERSION}"
    )
    
    log "✓ Argumentos JVM configurados (${#JVM_ARGS[@]} argumentos)"
}

###############################################################################
# FUNCIÓN DE HEALTH CHECK
###############################################################################

health_check() {
    local url="http://localhost:${PORT}/actuator/health"
    local max_attempts=30
    local attempt=1
    local wait_time=2
    
    log "Iniciando health check..."
    info "Verificando endpoint: ${url}"
    
    while [[ ${attempt} -le ${max_attempts} ]]; do
        if curl -sf "${url}" > /dev/null 2>&1; then
            log "✓ Health check passed - Aplicación está saludable"
            return 0
        fi
        
        info "Intento ${attempt}/${max_attempts} - Esperando ${wait_time}s..."
        sleep ${wait_time}
        
        # Incrementar tiempo de espera progresivamente
        if [[ ${attempt} -gt 10 ]]; then
            wait_time=3
        fi
        if [[ ${attempt} -gt 20 ]]; then
            wait_time=5
        fi
        
        ((attempt++))
    done
    
    error "Health check falló después de ${max_attempts} intentos"
    return 1
}

###############################################################################
# FUNCIÓN DE ARRANQUE
###############################################################################

start_application() {
    log "Iniciando ${APP_NAME} v${APP_VERSION}..."
    info "Directorio: ${APP_DIR}"
    info "Puerto: ${PORT}"
    info "Logs: ${LOG_DIR}"
    
    # Verificar si ya está ejecutándose
    if [[ -f "${PID_FILE}" ]]; then
        local pid=$(cat "${PID_FILE}")
        if ps -p "${pid}" > /dev/null 2>&1; then
            warn "La aplicación ya está ejecutándose (PID: ${pid})"
            return 0
        else
            warn "Archivo PID obsoleto encontrado, limpiando..."
            rm -f "${PID_FILE}"
        fi
    fi
    
    # Construir comando de ejecución
    local java_cmd="java ${JVM_ARGS[@]} -jar ${JAR_FILE}"
    
    log "Comando de ejecución:"
    info "${java_cmd}"
    
    # Iniciar aplicación en background
    log "Ejecutando aplicación..."
    nohup java ${JVM_ARGS[@]} -jar "${JAR_FILE}" > "${LOG_DIR}/startup.log" 2>&1 &
    
    # Guardar PID
    local app_pid=$!
    echo "${app_pid}" > "${PID_FILE}"
    
    log "✓ Aplicación iniciada con PID: ${app_pid}"
    
    # Esperar y verificar que la aplicación esté funcionando
    sleep 5
    
    if ps -p "${app_pid}" > /dev/null 2>&1; then
        log "✓ Proceso de aplicación está ejecutándose"
        
        # Ejecutar health check
        if health_check; then
            log "🎉 ${APP_NAME} está funcionando correctamente!"
            info "PID: ${app_pid}"
            info "Logs: ${LOG_DIR}/startup.log"
            info "PID file: ${PID_FILE}"
            return 0
        else
            warn "La aplicación se inició pero el health check falló"
            warn "Revise los logs en: ${LOG_DIR}/startup.log"
            return 1
        fi
    else
        error "La aplicación falló al iniciar"
        error "Revise los logs en: ${LOG_DIR}/startup.log"
        return 1
    fi
}

###############################################################################
# FUNCIÓN DE PARADA
###############################################################################

stop_application() {
    log "Deteniendo ${APP_NAME}..."
    
    if [[ ! -f "${PID_FILE}" ]]; then
        warn "No se encontró archivo PID - ¿La aplicación está ejecutándose?"
        return 0
    fi
    
    local pid=$(cat "${PID_FILE}")
    
    if ! ps -p "${pid}" > /dev/null 2>&1; then
        warn "El proceso ${pid} no está ejecutándose"
        rm -f "${PID_FILE}"
        return 0
    fi
    
    log "Enviando señal TERM al proceso ${pid}..."
    kill -TERM "${pid}"
    
    # Esperar a que termine el proceso
    local max_wait=30
    local count=0
    
    while ps -p "${pid}" > /dev/null 2>&1; do
        if [[ ${count} -ge ${max_wait} ]]; then
            warn "El proceso no terminó en ${max_wait}s, enviando KILL..."
            kill -KILL "${pid}"
            sleep 2
            break
        fi
        sleep 1
        ((count++))
    done
    
    if ! ps -p "${pid}" > /dev/null 2>&1; then
        log "✓ Aplicación detenida correctamente"
        rm -f "${PID_FILE}"
    else
        error "No se pudo detener la aplicación"
        return 1
    fi
}

###############################################################################
# FUNCIÓN DE STATUS
###############################################################################

show_status() {
    log "Estado de ${APP_NAME}:"
    
    if [[ -f "${PID_FILE}" ]]; then
        local pid=$(cat "${PID_FILE}")
        
        if ps -p "${pid}" > /dev/null 2>&1; then
            info "✓ Ejecutándose (PID: ${pid})"
            
            # Mostrar información adicional del proceso
            local cpu_usage=$(ps -p "${pid}" -o %cpu --no-headers | tr -d ' ')
            local mem_usage=$(ps -p "${pid}" -o %mem --no-headers | tr -d ' ')
            
            info "  CPU: ${cpu_usage}%"
            info "  Memoria: ${mem_usage}%"
            
            # Intentar health check si el puerto está disponible
            if curl -sf "http://localhost:${PORT}/actuator/health" > /dev/null 2>&1; then
                info "✓ Health check: OK"
            else
                warn "Health check: FAILED o no disponible"
            fi
        else
            error "✗ No está ejecutándose (PID file existe pero proceso no encontrado)"
            rm -f "${PID_FILE}"
        fi
    else
        error "✗ No está ejecutándose (sin archivo PID)"
    fi
}

###############################################################################
# FUNCIÓN DE LOGS
###############################################################################

show_logs() {
    if [[ -f "${LOG_DIR}/startup.log" ]]; then
        log "Mostrando logs de startup:"
        tail -f "${LOG_DIR}/startup.log"
    else
        warn "No se encontraron logs en: ${LOG_DIR}/startup.log"
    fi
}

###############################################################################
# FUNCIÓN DE AYUDA
###############################################################################

show_help() {
    echo "Uso: $0 {start|stop|restart|status|logs|health}"
    echo ""
    echo "Comandos:"
    echo "  start    - Inicia la aplicación"
    echo "  stop     - Detiene la aplicación"
    echo "  restart  - Reinicia la aplicación"
    echo "  status   - Muestra el estado de la aplicación"
    echo "  logs     - Muestra los logs de la aplicación"
    echo "  health   - Ejecuta health check manual"
    echo ""
    echo "Variables de entorno requeridas:"
    echo "  DB_HOST      - Host de la base de datos"
    echo "  DB_PORT      - Puerto de la base de datos"
    echo "  DB_NAME      - Nombre de la base de datos"
    echo "  DB_USER      - Usuario de la base de datos"
    echo "  DB_PASSWORD  - Password de la base de datos"
    echo "  JWT_SECRET   - Secreto para JWT"
    echo ""
    echo "Variables opcionales:"
    echo "  PORT                    - Puerto del servidor (default: 8080)"
    echo "  JAR_FILE               - Ruta del archivo JAR"
    echo "  LOG_LEVEL              - Nivel de logging (default: INFO)"
    echo "  SPRING_PROFILES_ACTIVE - Perfiles de Spring"
    echo ""
}

###############################################################################
# FUNCIÓN PRINCIPAL
###############################################################################

main() {
    # Verificar argumentos
    if [[ $# -eq 0 ]]; then
        show_help
        exit 1
    fi
    
    case "${1}" in
        start)
            check_required_vars
            prepare_environment
            setup_jvm_args
            start_application
            ;;
        stop)
            stop_application
            ;;
        restart)
            stop_application
            sleep 3
            check_required_vars
            prepare_environment
            setup_jvm_args
            start_application
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        health)
            health_check
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Comando desconocido: ${1}"
            show_help
            exit 1
            ;;
    esac
}

###############################################################################
# EJECUCIÓN
###############################################################################

# Verificar que el script se ejecuta desde el directorio correcto
if [[ ! -f "${APP_DIR}/run.sh" ]]; then
    error "Este script debe ejecutarse desde el directorio de la aplicación"
    exit 1
fi

# Ejecutar función principal
main "$@"
