#!/bin/bash

# Script de entrada para LP1 - Servicio Banco
# Configuración y ejecución del contenedor

set -e

echo "==================================="
echo "Iniciando Servicio Banco LP1"
echo "Fecha: $(date)"
echo "==================================="

# Verificar variables de entorno
echo "Variables de entorno:"
echo "JAVA_OPTS: ${JAVA_OPTS}"
echo "SPRING_PROFILES_ACTIVE: ${SPRING_PROFILES_ACTIVE}"
echo "PUERTO: ${PORT:-8080}"

# Verificar que existe el JAR
if [ ! -f "app.jar" ]; then
    echo "ERROR: No se encontró app.jar"
    exit 1
fi

# Mostrar información del sistema
echo "Información del sistema:"
echo "Memoria disponible:"
free -h
echo ""
echo "Espacio en disco:"
df -h /app

# Configurar variables de Spring Boot
export SERVER_PORT=${PORT:-8080}

echo ""
echo "==================================="
echo "Ejecutando aplicación..."
echo "==================================="

# Ejecutar la aplicación
exec java $JAVA_OPTS -jar app.jar
