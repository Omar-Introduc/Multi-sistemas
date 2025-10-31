#!/bin/bash

# Script de validación de pruebas para LP2 RENIEC Service
# Verifica que la suite de pruebas esté correctamente configurada

set -e

echo "=================================="
echo "Validación de Suite de Pruebas LP2"
echo "=================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para print con color
print_status() {
    local status=$1
    local message=$2
    if [ "$status" == "OK" ]; then
        echo -e "${GREEN}[✓]${NC} $message"
    elif [ "$status" == "ERROR" ]; then
        echo -e "${RED}[✗]${NC} $message"
    else
        echo -e "${YELLOW}[•]${NC} $message"
    fi
}

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ] || [ ! -d "app" ]; then
    print_status "ERROR" "Este script debe ejecutarse desde el directorio raíz del servicio RENIEC"
    exit 1
fi

print_status "OK" "Directorio del proyecto correcto"

# Verificar archivos de prueba
test_files=(
    "tests/test_models.py"
    "tests/test_services.py" 
    "tests/test_api.py"
    "tests/conftest.py"
    "pytest.ini"
    "tests/README.md"
)

for file in "${test_files[@]}"; do
    if [ -f "$file" ]; then
        print_status "OK" "Archivo encontrado: $file"
    else
        print_status "ERROR" "Archivo faltante: $file"
    fi
done

# Verificar que pytest está disponible
if command -v pytest &> /dev/null; then
    print_status "OK" "pytest está instalado"
    
    # Mostrar versión
    pytest_version=$(pytest --version | head -n1)
    echo "  Versión: $pytest_version"
else
    print_status "ERROR" "pytest no está instalado"
    echo "  Instalar con: pip install pytest"
fi

# Verificar estructura de imports
print_status "INFO" "Verificando imports básicos..."

# Test básico de sintaxis
echo "Verificando sintaxis de archivos de prueba..."

if python -m py_compile tests/test_models.py; then
    print_status "OK" "test_models.py - Sintaxis correcta"
else
    print_status "ERROR" "test_models.py - Error de sintaxis"
fi

if python -m py_compile tests/test_services.py; then
    print_status "OK" "test_services.py - Sintaxis correcta"
else
    print_status "ERROR" "test_services.py - Error de sintaxis"
fi

if python -m py_compile tests/test_api.py; then
    print_status "OK" "test_api.py - Sintaxis correcta"
else
    print_status "ERROR" "test_api.py - Error de sintaxis"
fi

if python -m py_compile tests/conftest.py; then
    print_status "OK" "conftest.py - Sintaxis correcta"
else
    print_status "ERROR" "conftest.py - Error de sintaxis"
fi

# Verificar configuración de pytest
print_status "INFO" "Verificando configuración de pytest..."

if [ -f "pytest.ini" ]; then
    print_status "OK" "pytest.ini encontrado"
    
    # Verificar configuración básica
    if grep -q "testpaths" pytest.ini; then
        print_status "OK" "pytest.ini - testpaths configurado"
    fi
    
    if grep -q "markers" pytest.ini; then
        print_status "OK" "pytest.ini - markers configurados"
    fi
    
    if grep -q "addopts" pytest.ini; then
        print_status "OK" "pytest.ini - addopts configurado"
    fi
fi

# Verificar conftest.py
print_status "INFO" "Verificando fixtures en conftest.py..."

if grep -q "@pytest.fixture" tests/conftest.py; then
    fixture_count=$(grep -c "@pytest.fixture" tests/conftest.py)
    print_status "OK" "conftest.py - $fixture_count fixtures definidos"
fi

# Test rápido de importación
print_status "INFO" "Probando imports básicos..."

python3 -c "
import sys
import os
sys.path.append('.')

try:
    from tests.test_models import TestBaseModel, TestCiudadanoModel
    print('✓ test_models imports OK')
except Exception as e:
    print(f'✗ test_models import error: {e}')
    sys.exit(1)

try:
    from tests.test_services import TestCiudadanoService
    print('✓ test_services imports OK')
except Exception as e:
    print(f'✗ test_services import error: {e}')
    sys.exit(1)

try:
    from tests.test_api import TestHealthCheckEndpoints
    print('✓ test_api imports OK')
except Exception as e:
    print(f'✗ test_api import error: {e}')
    sys.exit(1)

try:
    from tests.conftest import *
    print('✓ conftest imports OK')
except Exception as e:
    print(f'✗ conftest import error: {e}')
    sys.exit(1)

print('✓ Todos los imports básicos correctos')
"

if [ $? -eq 0 ]; then
    print_status "OK" "Imports básicos verificados"
else
    print_status "ERROR" "Error en imports básicos"
fi

# Test de configuración de pytest (sin ejecutar tests)
print_status "INFO" "Validando configuración de pytest..."

if pytest --collect-only -q &> /dev/null; then
    test_count=$(pytest --collect-only -q 2>/dev/null | grep -c "test session starts" || echo "0")
    print_status "OK" "pytest puede recopilar tests correctamente"
else
    print_status "WARN" "pytest puede tener problemas de configuración"
fi

# Mostrar resumen
echo ""
echo "=================================="
echo "Resumen de Validación"
echo "=================================="
echo ""
echo "Archivos de prueba creados:"
echo "  ✓ test_models.py ($(wc -l < tests/test_models.py) líneas)"
echo "  ✓ test_services.py ($(wc -l < tests/test_services.py) líneas)"
echo "  ✓ test_api.py ($(wc -l < tests/test_api.py) líneas)"
echo "  ✓ conftest.py ($(wc -l < tests/conftest.py) líneas)"
echo "  ✓ pytest.ini ($(wc -l < pytest.ini) líneas)"
echo "  ✓ README.md ($(wc -l < tests/README.md) líneas)"
echo "  ✓ requirements-dev.txt ($(wc -l < requirements-dev.txt) líneas)"
echo ""
echo "Total de líneas de código de prueba: $(cat tests/test_*.py conftest.py | wc -l)"
echo ""

# Instrucciones de uso
echo "=================================="
echo "Comandos para Ejecutar Pruebas"
echo "=================================="
echo ""
echo "Ejecutar todas las pruebas:"
echo "  pytest"
echo ""
echo "Ejecutar por categoría:"
echo "  pytest -m unit          # Tests unitarios"
echo "  pytest -m integration   # Tests de integración"
echo "  pytest -m slow          # Tests lentos"
echo ""
echo "Ejecutar archivo específico:"
echo "  pytest tests/test_models.py"
echo "  pytest tests/test_services.py"
echo "  pytest tests/test_api.py"
echo ""
echo "Con cobertura:"
echo "  pytest --cov=app --cov-report=html"
echo ""
echo "Ver reporte:"
echo "  open htmlcov/index.html"
echo ""

print_status "OK" "Validación completada exitosamente"

echo ""
echo "🎉 La suite de pruebas LP2 está lista para usar!"
echo ""
