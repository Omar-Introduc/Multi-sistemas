#!/bin/bash

# Banco Desktop - Script de instalación y ejecución
# Autor: Equipo LP3

echo "============================================"
echo "    Banco Desktop - Instalador v1.0"
echo "============================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
show_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

show_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

show_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_header() {
    echo -e "${BLUE}$1${NC}"
}

# Verificar si Node.js está instalado
check_nodejs() {
    if ! command -v node &> /dev/null; then
        show_error "Node.js no está instalado. Por favor instala Node.js 16 o superior."
        echo "Visita: https://nodejs.org/"
        exit 1
    fi
    
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 16 ]; then
        show_error "Node.js versión $NODE_VERSION detectada. Se requiere versión 16 o superior."
        exit 1
    fi
    
    show_message "Node.js $(node -v) detectado correctamente."
}

# Verificar si npm está disponible
check_npm() {
    if ! command -v npm &> /dev/null; then
        show_error "npm no está disponible. Instala npm primero."
        exit 1
    fi
    show_message "npm $(npm -v) disponible."
}

# Instalar dependencias
install_dependencies() {
    show_header "Instalando dependencias..."
    
    if [ ! -f "package.json" ]; then
        show_error "No se encontró package.json en el directorio actual."
        exit 1
    fi
    
    show_message "Instalando paquetes de npm..."
    npm install
    
    if [ $? -eq 0 ]; then
        show_message "Dependencias instaladas correctamente."
    else
        show_error "Error al instalar las dependencias."
        exit 1
    fi
}

# Verificar estructura del proyecto
check_project_structure() {
    show_header "Verificando estructura del proyecto..."
    
    required_dirs=(
        "src/main"
        "src/renderer"
        "src/renderer/css"
        "src/renderer/js"
        "src/renderer/pages"
        "src/main/config"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            show_warning "Directorio faltante: $dir"
        fi
    done
    
    required_files=(
        "package.json"
        "src/main/main.js"
        "src/main/preload.js"
        "src/renderer/index.html"
        "src/renderer/css/main.css"
        "src/renderer/js/app.js"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            show_warning "Archivo faltante: $file"
        fi
    done
    
    show_message "Estructura del proyecto verificada."
}

# Mostrar información de usuarios de prueba
show_test_users() {
    show_header "Usuarios de Prueba Disponibles:"
    echo ""
    echo "👤 Administrador:"
    echo "   Usuario: admin"
    echo "   Contraseña: admin123"
    echo ""
    echo "👤 Usuario Demo:"
    echo "   Usuario: usuario"
    echo "   Contraseña: 123456"
    echo ""
    echo "👤 Sistema Bancario:"
    echo "   Usuario: banco"
    echo "   Contraseña: banco2023"
    echo ""
}

# Ejecutar en modo desarrollo
run_dev() {
    show_header "Iniciando Banco Desktop en modo desarrollo..."
    show_message "Las herramientas de desarrollo se abrirán automáticamente."
    echo ""
    show_test_users
    echo ""
    show_warning "Presiona Ctrl+C para cerrar la aplicación."
    echo ""
    npm run dev
}

# Ejecutar en modo producción
run_prod() {
    show_header "Iniciando Banco Desktop en modo producción..."
    show_message "La aplicación se ejecutará sin herramientas de desarrollo."
    echo ""
    show_test_users
    echo ""
    show_warning "Presiona Ctrl+C para cerrar la aplicación."
    echo ""
    npm start
}

# Construir para distribución
build_app() {
    show_header "Construyendo aplicación para distribución..."
    show_message "Esto puede tomar varios minutos..."
    echo ""
    
    read -p "¿Para qué plataforma quieres construir? (win/mac/linux/all): " platform
    
    case $platform in
        win|Win|WIN)
            show_message "Construyendo para Windows..."
            npm run build:win
            ;;
        mac|Mac|MAC)
            show_message "Construyendo para macOS..."
            npm run build:mac
            ;;
        linux|Linux|LINUX)
            show_message "Construyendo para Linux..."
            npm run build:linux
            ;;
        all|All|ALL)
            show_message "Construyendo para todas las plataformas..."
            npm run build
            ;;
        *)
            show_warning "Plataforma no reconocida. Construyendo para la plataforma actual..."
            npm run build
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        show_message "¡Construcción completada exitosamente!"
        show_message "Los archivos de distribución están en el directorio 'dist/'"
    else
        show_error "Error durante la construcción."
        exit 1
    fi
}

# Mostrar menú principal
show_menu() {
    clear
    show_header "    Banco Desktop - Aplicación Electron    "
    echo ""
    echo "Selecciona una opción:"
    echo ""
    echo "1. Instalar dependencias"
    echo "2. Ejecutar en modo desarrollo"
    echo "3. Ejecutar en modo producción"
    echo "4. Construir para distribución"
    echo "5. Verificar instalación"
    echo "6. Mostrar usuarios de prueba"
    echo "7. Salir"
    echo ""
}

# Función principal
main() {
    cd "$(dirname "$0")"
    
    while true; do
        show_menu
        read -p "Opción [1-7]: " choice
        
        case $choice in
            1)
                check_nodejs
                check_npm
                install_dependencies
                check_project_structure
                echo ""
                read -p "Presiona Enter para continuar..."
                ;;
            2)
                run_dev
                ;;
            3)
                run_prod
                ;;
            4)
                build_app
                echo ""
                read -p "Presiona Enter para continuar..."
                ;;
            5)
                check_nodejs
                check_npm
                check_project_structure
                echo ""
                read -p "Presiona Enter para continuar..."
                ;;
            6)
                show_test_users
                echo ""
                read -p "Presiona Enter para continuar..."
                ;;
            7)
                show_message "¡Hasta luego!"
                exit 0
                ;;
            *)
                show_error "Opción inválida. Selecciona una opción del 1 al 7."
                echo ""
                read -p "Presiona Enter para continuar..."
                ;;
        esac
    done
}

# Verificar argumentos de línea de comandos
case "$1" in
    --dev|-d)
        check_nodejs
        check_npm
        install_dependencies
        run_dev
        ;;
    --prod|-p)
        check_nodejs
        check_npm
        install_dependencies
        run_prod
        ;;
    --build|-b)
        check_nodejs
        check_npm
        install_dependencies
        build_app
        ;;
    --install|-i)
        check_nodejs
        check_npm
        install_dependencies
        check_project_structure
        show_message "Instalación completada."
        ;;
    --help|-h)
        echo "Banco Desktop - Script de instalación y ejecución"
        echo ""
        echo "Uso: $0 [opción]"
        echo ""
        echo "Opciones:"
        echo "  --dev, -d     Ejecutar en modo desarrollo"
        echo "  --prod, -p    Ejecutar en modo producción"
        echo "  --build, -b   Construir para distribución"
        echo "  --install, -i Instalar dependencias solamente"
        echo "  --help, -h    Mostrar esta ayuda"
        echo ""
        echo "Sin argumentos: mostrar menú interactivo"
        ;;
    *)
        main
        ;;
esac
