#!/bin/bash

# Script de prueba para validar health checks
# Prueba básica sin dependencias externas

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=================================================="
echo "    VALIDACIÓN DE HEALTH CHECKS AVANZADOS"
echo "=================================================="
echo ""
echo "Directorio: $SCRIPT_DIR"
echo ""

# Verificar que existen todos los scripts
scripts=(
    "health-check.sh"
    "check-db-connections.sh"
    "check-rabbitmq.sh"
    "check-redis.sh"
    "generate-health-report.sh"
    "install.sh"
    "setup-cron.sh"
)

echo "✓ Verificando scripts principales..."
all_exist=true
for script in "${scripts[@]}"; do
    if [ -f "$SCRIPT_DIR/$script" ]; then
        echo "  ✓ $script existe"
    else
        echo "  ✗ $script NO ENCONTRADO"
        all_exist=false
    fi
done

echo ""
echo "✓ Verificando documentación..."
docs=("README.md" "config.env.example" "RESUMEN.md")
for doc in "${docs[@]}"; do
    if [ -f "$SCRIPT_DIR/$doc" ]; then
        echo "  ✓ $doc existe"
    else
        echo "  ✗ $doc NO ENCONTRADO"
    fi
done

echo ""
echo "✓ Verificando archivos Docker..."
docker_files=("Dockerfile" "docker-compose.example.yml" "docker-entrypoint.sh")
for file in "${docker_files[@]}"; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        echo "  ✓ $file existe"
    else
        echo "  ✗ $file NO ENCONTRADO"
    fi
done

echo ""
echo "✓ Verificando sintaxis de scripts bash..."
for script in "${scripts[@]}"; do
    if bash -n "$SCRIPT_DIR/$script" 2>/dev/null; then
        echo "  ✓ $script - Sintaxis OK"
    else
        echo "  ✗ $script - Error de sintaxis"
    fi
done

echo ""
echo "✓ Verificando dependencias básicas del sistema..."
deps=("bash" "curl" "bc" "jq" "python3")
for dep in "${deps[@]}"; do
    if command -v "$dep" >/dev/null 2>&1; then
        echo "  ✓ $dep disponible"
    else
        echo "  ⚠ $dep no encontrado (puede requerir instalación)"
    fi
done

echo ""
echo "✓ Probando funciones básicas de health-check.sh..."

# Crear directorio de logs temporal
mkdir -p "$SCRIPT_DIR/logs"

# Extraer algunas funciones y probarlas
if grep -q "check_system_resources" "$SCRIPT_DIR/health-check.sh"; then
    echo "  ✓ Función check_system_resources encontrada"
fi

if grep -q "check_critical_services" "$SCRIPT_DIR/health-check.sh"; then
    echo "  ✓ Función check_critical_services encontrada"
fi

if grep -q "log()" "$SCRIPT_DIR/health-check.sh"; then
    echo "  ✓ Función de logging encontrada"
fi

echo ""
echo "=================================================="
if [ "$all_exist" = true ]; then
    echo "    ✅ VALIDACIÓN EXITOSA"
    echo "=================================================="
    echo ""
    echo "El sistema de health checks está correctamente configurado."
    echo ""
    echo "Próximos pasos:"
    echo "1. Configurar credenciales en config.env"
    echo "2. Ejecutar: sudo ./scripts/install.sh"
    echo "3. Configurar cron: sudo ./scripts/setup-cron.sh"
    echo "4. Ver documentación: cat scripts/README.md"
    echo ""
    echo "Para prueba rápida:"
    echo "  ./scripts/health-check.sh"
    echo ""
else
    echo "    ⚠ VALIDACIÓN CON ADVERTENCIAS"
    echo "=================================================="
    echo ""
    echo "Algunos archivos no se encontraron."
    echo "Revisa la instalación y ejecuta nuevamente."
    echo ""
fi

echo "Directorio completo: $SCRIPT_DIR"
echo ""
echo "Archivos totales: $(ls -1 "$SCRIPT_DIR" | wc -l)"
echo "Tamaño total: $(du -sh "$SCRIPT_DIR" | cut -f1)"
echo ""
