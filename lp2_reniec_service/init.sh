#!/bin/bash

# Script de inicialización rápida para LP2 RENIEC Service
set -e

echo "🚀 Inicializando LP2 RENIEC Service..."

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar dependencias
echo "📋 Verificando dependencias..."

if ! command_exists docker; then
    echo "❌ Docker no está instalado. Por favor instalar Docker."
    exit 1
fi

if ! command_exists docker-compose; then
    echo "❌ Docker Compose no está instalado. Por favor instalar Docker Compose."
    exit 1
fi

# Crear archivos de configuración
echo "📁 Creando archivos de configuración..."
cp .env.example .env 2>/dev/null || echo "⚠️  .env.example no encontrado, usando valores por defecto"

# Crear directorios necesarios
echo "📂 Creando directorios..."
mkdir -p logs uploads uploads/documentos uploads/imagenes uploads/temporales uploads/respaldos

# Establecer permisos
chmod 755 logs uploads uploads/* 2>/dev/null || true

# Construir y ejecutar servicios
echo "🐳 Construyendo y ejecutando servicios Docker..."
docker-compose down --remove-orphans 2>/dev/null || true
docker-compose up --build -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 30

# Verificar que los servicios estén funcionando
echo "🔍 Verificando servicios..."

# Verificar MySQL
if docker-compose exec mysql mysql -u reniec_user -ppassword_seguro -e "USE reniec_db; SELECT 1;" 2>/dev/null; then
    echo "✅ MySQL está funcionando"
else
    echo "⚠️  MySQL aún no está listo"
fi

# Verificar RabbitMQ
if curl -s http://localhost:15672 >/dev/null; then
    echo "✅ RabbitMQ está funcionando (http://localhost:15672)"
else
    echo "⚠️  RabbitMQ aún no está listo"
fi

# Verificar Redis
if docker-compose exec redis redis-cli ping 2>/dev/null | grep -q PONG; then
    echo "✅ Redis está funcionando"
else
    echo "⚠️  Redis aún no está listo"
fi

# Verificar la aplicación
echo "🌐 Verificando aplicación FastAPI..."
sleep 10
if curl -s http://localhost:8000/api/v1/health/ >/dev/null; then
    echo "✅ Aplicación FastAPI está funcionando (http://localhost:8000)"
    echo "📚 Documentación API: http://localhost:8000/docs"
else
    echo "⚠️  Aplicación aún no está lista"
fi

echo ""
echo "🎉 ¡LP2 RENIEC Service iniciado!"
echo ""
echo "📍 URLs importantes:"
echo "   • API: http://localhost:8000"
echo "   • Documentación: http://localhost:8000/docs"
echo "   • RabbitMQ Management: http://localhost:15672 (guest/guest)"
echo ""
echo "🔧 Comandos útiles:"
echo "   • Ver logs: docker-compose logs -f"
echo "   • Parar servicios: docker-compose down"
echo "   • Reiniciar: docker-compose restart"
echo ""
echo "📖 Revisa el README.md para más información."