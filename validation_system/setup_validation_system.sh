#!/bin/bash

# Script de Instalación del Sistema de Validación Integral
# Usage: ./setup_validation_system.sh

set -e

echo "=========================================="
echo "🏗️  SISTEMA DE VALIDACIÓN INTEGRAL"
echo "=========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging con colores
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si estamos en el directorio correcto
if [ ! -f "run_complete_validation.py" ]; then
    log_error "Ejecute este script desde el directorio validation_system/"
    exit 1
fi

log_info "Iniciando instalación del sistema de validación..."

# Crear directorios necesarios
log_info "Creando estructura de directorios..."
mkdir -p reports logs temp
log_success "Directorios creados"

# Verificar Python
log_info "Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    log_success "Python encontrado: $PYTHON_VERSION"
else
    log_error "Python 3 no está instalado"
    exit 1
fi

# Instalar dependencias Python
log_info "Instalando dependencias Python..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    log_success "Dependencias Python instaladas"
else
    log_warning "requirements.txt no encontrado, instalando dependencias básicas..."
    pip3 install aiohttp requests psutil pyyaml
fi

# Verificar Node.js (opcional)
log_info "Verificando Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    log_success "Node.js encontrado: $NODE_VERSION"
else
    log_warning "Node.js no está instalado (opcional para validación JavaScript)"
fi

# Verificar npm (opcional)
log_info "Verificando npm..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    log_success "npm encontrado: v$NPM_VERSION"
else
    log_warning "npm no está instalado (opcional para validación JavaScript)"
fi

# Verificar Java (opcional)
log_info "Verificando Java..."
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n1)
    log_success "Java encontrado: $JAVA_VERSION"
else
    log_warning "Java no está instalado (opcional para validación Java)"
fi

# Verificar Docker (opcional)
log_info "Verificando Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    log_success "Docker encontrado: $DOCKER_VERSION"
else
    log_warning "Docker no está instalado (opcional para validación Docker)"
fi

# Hacer ejecutables los scripts Python
log_info "Configurando permisos..."
chmod +x *.py
log_success "Permisos configurados"

# Verificar configuración
log_info "Verificando configuración..."
if [ -f "validation_config.json" ]; then
    log_success "Configuración encontrada"
else
    log_warning "Configuración no encontrada, se creará una por defecto"
fi

# Probar importación de módulos
log_info "Probando módulos de validación..."
python3 -c "
import sys
sys.path.append('.')
try:
    import integration_test_suite
    import validate_technologies
    import validate_architecture
    import scalability_tests
    import fault_tolerance_tests
    import run_complete_validation
    import generate_final_report
    print('✅ Todos los módulos importados correctamente')
except ImportError as e:
    print(f'❌ Error importando módulos: {e}')
    sys.exit(1)
" || {
    log_error "Error en la importación de módulos"
    exit 1
}

log_success "Módulos verificados correctamente"

# Crear script de prueba rápida
cat > test_validation_system.py << 'EOF'
#!/usr/bin/env python3
"""
Script de prueba rápida del sistema de validación
"""
import sys
import asyncio

async def quick_test():
    """Prueba rápida de conectividad"""
    try:
        from run_complete_validation import ValidationOrchestrator
        
        print("🧪 Ejecutando prueba rápida...")
        
        orchestrator = ValidationOrchestrator()
        
        # Solo verificar disponibilidad de servicios
        availability = orchestrator._check_services_availability()
        
        print("\n📊 Resultados de conectividad:")
        for service, available in availability.items():
            status = "✅" if available else "❌"
            print(f"  {status} {service}: {'Disponible' if available else 'No disponible'}")
        
        total_available = sum(availability.values())
        total_services = len(availability)
        health_pct = (total_available / total_services * 100) if total_services > 0 else 0
        
        print(f"\n🏥 Salud del sistema: {total_available}/{total_services} ({health_pct:.1f}%)")
        
        if health_pct >= 100:
            print("✅ Sistema completamente operativo")
        elif health_pct >= 67:
            print("⚠️  Sistema parcialmente operativo")
        else:
            print("❌ Sistema con problemas")
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")

if __name__ == "__main__":
    asyncio.run(quick_test())
EOF

chmod +x test_validation_system.py

echo ""
echo "=========================================="
echo "✅ INSTALACIÓN COMPLETADA"
echo "=========================================="
echo ""
echo "🎯 Para empezar:"
echo ""
echo "1. Verificar conectividad:"
echo "   python3 test_validation_system.py"
echo ""
echo "2. Ejecutar validación completa:"
echo "   python3 run_complete_validation.py"
echo ""
echo "3. Generar reportes:"
echo "   python3 generate_final_report.py --console"
echo ""
echo "4. Ejecutar módulos individuales:"
echo "   python3 integration_test_suite.py"
echo "   python3 validate_technologies.py"
echo "   python3 validate_architecture.py"
echo "   python3 scalability_tests.py"
echo "   python3 fault_tolerance_tests.py"
echo ""
echo "📁 Directorios creados:"
echo "   - reports/   (reportes generados)"
echo "   - logs/      (logs del sistema)"
echo "   - temp/      (archivos temporales)"
echo ""
echo "📖 Ver README.md para más información"
echo ""
