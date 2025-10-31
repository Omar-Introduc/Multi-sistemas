#!/bin/bash

# Quick Start - Sistema de Validación Integral
# Uso: ./quick_start.sh

echo "🏗️  SISTEMA DE VALIDACIÓN INTEGRAL - QUICK START"
echo "================================================"
echo ""

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar Python
if ! command_exists python3; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Instalar dependencias básicas si no están instaladas
echo ""
echo "📦 Instalando dependencias..."
pip3 install aiohttp requests psutil pyyaml --quiet

# Ejecutar prueba rápida
echo ""
echo "🧪 Ejecutando prueba de conectividad..."
python3 -c "
import sys
sys.path.append('.')
from run_complete_validation import ValidationOrchestrator

try:
    orchestrator = ValidationOrchestrator()
    availability = orchestrator._check_services_availability()
    
    print('\\n📊 Conectividad:')
    for service, available in availability.items():
        status = '✅' if available else '❌'
        print(f'  {status} {service}')
    
    total = len(availability)
    available = sum(availability.values())
    health = (available / total * 100) if total > 0 else 0
    
    print(f'\\n🏥 Salud del sistema: {available}/{total} ({health:.1f}%)')
    
    if health >= 100:
        print('✅ Sistema operativo - Ejecutando validación completa')
    elif health >= 67:
        print('⚠️  Sistema parcial - Ejecutando validación disponible')
    else:
        print('❌ Sistema con problemas - Validación limitada')
        
except Exception as e:
    print(f'❌ Error: {e}')
"

echo ""
echo "🎯 OPCIONES DE EJECUCIÓN:"
echo ""
echo "1️⃣  Validación completa:"
echo "   python3 run_complete_validation.py"
echo ""
echo "2️⃣  Validación con reporte HTML:"
echo "   python3 run_complete_validation.py && python3 generate_final_report.py"
echo ""
echo "3️⃣  Solo pruebas de integración:"
echo "   python3 integration_test_suite.py"
echo ""
echo "4️⃣  Solo validación de tecnologías:"
echo "   python3 validate_technologies.py"
echo ""
echo "5️⃣  Solo escalabilidad:"
echo "   python3 scalability_tests.py"
echo ""
echo "6️⃣  Solo tolerancia a fallos:"
echo "   python3 fault_tolerance_tests.py"
echo ""
echo "📖 Documentación completa en README.md"
echo ""
