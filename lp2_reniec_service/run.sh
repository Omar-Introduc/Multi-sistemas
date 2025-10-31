#!/bin/sh

# Script de inicio para el servicio LP2 RENIEC
echo "Iniciando servicio LP2 RENIEC..."

# Verificar que el archivo principal existe
if [ ! -f "main.py" ]; then
    echo "Error: Archivo main.py no encontrado"
    exit 1
fi

# Configurar variables de entorno
export PYTHONPATH="${PYTHONPATH}:/app"
export HOST=${HOST:-"0.0.0.0"}
export PORT=${PORT:-"8000"}

# Mostrar información de inicio
echo "Servicio: LP2 RENIEC"
echo "Host: $HOST"
echo "Puerto: $PORT"
echo "Directorio de trabajo: $(pwd)"

# Iniciar servidor FastAPI con Uvicorn
echo "Iniciando servidor FastAPI..."
exec uvicorn main:app \
    --host "$HOST" \
    --port "$PORT" \
    --workers 1 \
    --log-level info \
    --access-log