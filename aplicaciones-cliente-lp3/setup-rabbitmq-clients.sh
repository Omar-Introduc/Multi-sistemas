#!/bin/bash

# Script de inicialización para configuración RabbitMQ de aplicaciones cliente
# Fecha: 2025-10-30
# Autor: LP3 Team

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
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

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Función para verificar Node.js
check_node() {
    if ! command_exists node; then
        log_error "Node.js no está instalado. Por favor instala Node.js 16+ primero."
        exit 1
    fi

    NODE_VERSION=$(node -v | sed 's/v//')
    REQUIRED_VERSION="16.0.0"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$NODE_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        log_error "Node.js versión $NODE_VERSION encontrada. Se requiere versión $REQUIRED_VERSION o superior."
        exit 1
    fi

    log_success "Node.js $NODE_VERSION detectado"
}

# Función para verificar npm
check_npm() {
    if ! command_exists npm; then
        log_error "npm no está instalado. Por favor instala npm primero."
        exit 1
    fi

    NPM_VERSION=$(npm -v)
    log_success "npm $NPM_VERSION detectado"
}

# Función para configurar aplicación móvil
setup_mobile_app() {
    log_info "Configurando aplicación móvil (React Native)..."
    
    cd mobile-app
    
    # Instalar dependencias
    log_info "Instalando dependencias para aplicación móvil..."
    npm install
    
    # Verificar que las dependencias de RabbitMQ estén instaladas
    if ! grep -q "uuid" package.json; then
        log_info "Instalando uuid..."
        npm install uuid
    fi
    
    if ! grep -q "socket.io-client" package.json; then
        log_info "Instalando socket.io-client..."
        npm install socket.io-client
    fi
    
    # Crear archivo de configuración de entorno si no existe
    if [ ! -f .env ]; then
        log_info "Creando archivo .env para aplicación móvil..."
        cat > .env << EOL
# Configuración RabbitMQ - Aplicación Móvil
RABBITMQ_API_URL=http://localhost:8080/api
RABBITMQ_WS_URL=ws://localhost:8080/ws
RABBITMQ_URL=amqp://localhost:5672

# Configuración de desarrollo
NODE_ENV=development
DEBUG=true
EOL
        log_success "Archivo .env creado para aplicación móvil"
    else
        log_warning "Archivo .env ya existe para aplicación móvil"
    fi
    
    # Verificar estructura de directorios
    if [ ! -d "src/services/rabbitmq" ]; then
        log_error "Directorio src/services/rabbitmq no encontrado en aplicación móvil"
        return 1
    fi
    
    log_success "Aplicación móvil configurada correctamente"
    cd ..
}

# Función para configurar aplicación desktop
setup_desktop_app() {
    log_info "Configurando aplicación desktop (Electron)..."
    
    cd desktop-app
    
    # Instalar dependencias
    log_info "Instalando dependencias para aplicación desktop..."
    npm install
    
    # Verificar que las dependencias de RabbitMQ estén instaladas
    if ! grep -q "uuid" package.json; then
        log_info "Instalando uuid..."
        npm install uuid
    fi
    
    if ! grep -q "socket.io-client" package.json; then
        log_info "Instalando socket.io-client..."
        npm install socket.io-client
    fi
    
    if ! grep -q "winston" package.json; then
        log_info "Instalando winston para logging..."
        npm install winston
    fi
    
    # Crear archivo de configuración de entorno si no existe
    if [ ! -f .env ]; then
        log_info "Creando archivo .env para aplicación desktop..."
        cat > .env << EOL
# Configuración RabbitMQ - Aplicación Desktop
RABBITMQ_API_URL=http://localhost:8080/api
RABBITMQ_SOCKETIO_URL=http://localhost:8080
RABBITMQ_URL=amqp://localhost:5672

# Configuración de desarrollo
NODE_ENV=development
DEBUG=true
ELECTRON_ENABLE_LOGGING=true
EOL
        log_success "Archivo .env creado para aplicación desktop"
    else
        log_warning "Archivo .env ya existe para aplicación desktop"
    fi
    
    # Verificar estructura de directorios
    if [ ! -d "src/services/rabbitmq" ]; then
        log_error "Directorio src/services/rabbitmq no encontrado en aplicación desktop"
        return 1
    fi
    
    # Verificar archivo principal de Electron
    if [ ! -f "src/main/main.js" ]; then
        log_warning "Archivo src/main/main.js no encontrado. Creando archivo básico..."
        mkdir -p src/main
        cat > src/main/main.js << EOL
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

// Configuración de la ventana principal
const createWindow = () => {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false
    }
  });

  mainWindow.loadFile('src/renderer/index.html');
};

// Evento ready de la app
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Cerrar cuando todas las ventanas estén cerradas
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Configurar IPC handlers
ipcMain.handle('rabbitmq:status', async () => {
  return { connected: false, message: 'Configuración básica - implementar RabbitMQ client' };
});
EOL
        log_success "Archivo main.js básico creado"
    fi
    
    log_success "Aplicación desktop configurada correctamente"
    cd ..
}

# Función para copiar configuraciones de RabbitMQ
copy_rabbitmq_config() {
    log_info "Copiando configuraciones de RabbitMQ..."
    
    # Verificar si existe configuración base de RabbitMQ
    if [ -f "../shibasito-sistema-distribuido/rabbitmq-config/definitions.json" ]; then
        log_info "Copiando configuraciones de RabbitMQ desde shibasito-sistema-distribuido..."
        cp ../shibasito-sistema-distribuido/rabbitmq-config/definitions.json ./
        log_success "Configuraciones de RabbitMQ copiadas"
    else
        log_warning "Configuraciones de RabbitMQ no encontradas en shibasito-sistema-distribuido"
    fi
}

# Función para verificar configuraciones
verify_configurations() {
    log_info "Verificando configuraciones..."
    
    # Verificar aplicación móvil
    if [ -d "mobile-app/src/services/rabbitmq" ]; then
        log_success "Configuración móvil: ✓"
        
        # Verificar archivos clave
        if [ -f "mobile-app/src/services/rabbitmq/index.js" ]; then
            log_success "  - Archivo principal móvil: ✓"
        else
            log_error "  - Archivo principal móvil: ✗"
        fi
        
        if [ -f "mobile-app/src/services/rabbitmq/react-native-client.js" ]; then
            log_success "  - Cliente React Native: ✓"
        else
            log_error "  - Cliente React Native: ✗"
        fi
        
        if [ -f "mobile-app/src/services/rabbitmq/axios-interceptor.js" ]; then
            log_success "  - Interceptor Axios: ✓"
        else
            log_error "  - Interceptor Axios: ✗"
        fi
    else
        log_error "Configuración móvil: ✗"
    fi
    
    # Verificar aplicación desktop
    if [ -d "desktop-app/src/services/rabbitmq" ]; then
        log_success "Configuración desktop: ✓"
        
        # Verificar archivos clave
        if [ -f "desktop-app/src/services/rabbitmq/index.js" ]; then
            log_success "  - Archivo principal desktop: ✓"
        else
            log_error "  - Archivo principal desktop: ✗"
        fi
        
        if [ -f "desktop-app/src/services/rabbitmq/socketio-client.js" ]; then
            log_success "  - Cliente Socket.io: ✓"
        else
            log_error "  - Cliente Socket.io: ✗"
        fi
    else
        log_error "Configuración desktop: ✗"
    fi
}

# Función para crear scripts de prueba
create_test_scripts() {
    log_info "Creando scripts de prueba..."
    
    # Script de prueba para móvil
    cat > test-mobile.js << EOL
const { initializeRabbitMQ } = require('./mobile-app/src/services/rabbitmq/index');

async function testMobile() {
  try {
    console.log('🧪 Probando cliente móvil RabbitMQ...');
    const instance = await initializeRabbitMQ();
    console.log('✅ Cliente móvil inicializado');
    console.log('Status:', instance.client.getStatus());
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

testMobile();
EOL
    
    # Script de prueba para desktop
    cat > test-desktop.js << EOL
const { initializeDesktopRabbitMQ } = require('./desktop-app/src/services/rabbitmq/index');

async function testDesktop() {
  try {
    console.log('🧪 Probando cliente desktop RabbitMQ...');
    const instance = await initializeDesktopRabbitMQ();
    console.log('✅ Cliente desktop inicializado');
    console.log('Status:', instance.client.getStatus());
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

testDesktop();
EOL
    
    chmod +x test-mobile.js test-desktop.js
    log_success "Scripts de prueba creados"
}

# Función para mostrar instrucciones finales
show_final_instructions() {
    echo ""
    echo "🎉 Configuración completada!"
    echo ""
    echo "📱 Aplicación Móvil:"
    echo "  cd mobile-app"
    echo "  npm start"
    echo ""
    echo "🖥️  Aplicación Desktop:"
    echo "  cd desktop-app"
    echo "  npm run dev"
    echo ""
    echo "🧪 Ejecutar pruebas:"
    echo "  node test-mobile.js"
    echo "  node test-desktop.js"
    echo ""
    echo "📚 Documentación completa:"
    echo "  Ver archivo: RABBITMQ_CLIENTS_CONFIG.md"
    echo ""
    echo "⚠️  Requisitos:"
    echo "  - RabbitMQ debe estar ejecutándose"
    echo "  - API Gateway debe estar configurado"
    echo "  - URLs en archivos .env deben ser correctas"
    echo ""
}

# Función principal
main() {
    echo "🚀 Inicializando configuración RabbitMQ para aplicaciones cliente"
    echo "=================================================================="
    
    # Verificar prerrequisitos
    check_node
    check_npm
    
    # Verificar que estamos en el directorio correcto
    if [ ! -d "mobile-app" ] || [ ! -d "desktop-app" ]; then
        log_error "Este script debe ejecutarse desde el directorio aplicaciones-cliente-lp3"
        exit 1
    fi
    
    # Configurar aplicaciones
    setup_mobile_app
    setup_desktop_app
    
    # Copiar configuraciones
    copy_rabbitmq_config
    
    # Verificar configuraciones
    verify_configurations
    
    # Crear scripts de prueba
    create_test_scripts
    
    # Mostrar instrucciones finales
    show_final_instructions
    
    log_success "🎊 ¡Configuración completada exitosamente!"
}

# Ejecutar función principal
main "$@"