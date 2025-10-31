# Dockerfile para Aplicación Desktop con Electron

Este directorio contiene la configuración Docker para una aplicación desktop desarrollada con Node.js 18 y Electron.

## Características

- **Multi-stage build** para optimizar el tamaño de la imagen
- Configuración para **desarrollo** y **producción**
- Incluye todas las dependencias necesarias para compilación y distribución
- Usuario no-root para mayor seguridad
- Soporte para builds multiplataforma

## Estructura de Build

### 1. Development Stage
```dockerfile
FROM node:18-bullseye-slim as development
```
- Configurado para desarrollo local
- Incluye devDependencies
- Hot reload habilitado
- Volúmenes para desarrollo dinámico

### 2. Build Stage  
```dockerfile
FROM node:18-bullseye-slim as build
```
- Compila la aplicación
- Optimiza assets
- Prepara para distribución

### 3. Production Stage
```dockerfile
FROM node:18-bullseye-slim as production
```
- Imagen optimizada para producción
- Runtime mínimo requerido
- Lista para distribución

## Comandos de Uso

### Desarrollo

#### Con Docker Compose (Recomendado)
```bash
# Iniciar servicio de desarrollo
docker-compose up desktop-app-dev

# Modo detached
docker-compose up -d desktop-app-dev

# Rebuild completo
docker-compose up --build desktop-app-dev
```

#### Con Docker directamente
```bash
# Construir imagen de desarrollo
docker build --target development -t desktop-app:dev .

# Ejecutar contenedor
docker run -it --rm \
  -p 3000:3000 \
  -p 8080:8080 \
  -v $(pwd)/src:/app/src:ro \
  -v $(pwd)/public:/app/public:ro \
  desktop-app:dev
```

### Build de Producción

```bash
# Construir imagen de build
docker build --target build -t desktop-app:build .

# Ejecutar build
docker run --rm -v $(pwd)/dist:/app/dist desktop-app:build
```

### Crear Distribución

```bash
# Construir imagen de producción
docker build --target production -t desktop-app:prod .

# Crear builds para diferentes plataformas
docker run --rm -it -v $(pwd)/builds:/app/builds desktop-app:prod bash

# Dentro del contenedor:
npm run dist          # Todas las plataformas
npm run dist:linux    # Solo Linux
npm run dist:win      # Solo Windows
npm run dist:mac      # Solo macOS
```

### Scripts de Conveniencia

Crear script `build.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Building Desktop App..."

# Clean previous builds
rm -rf dist builds

# Build production image
echo "📦 Building production image..."
docker build --target production -t desktop-app:prod .

# Create distribution builds
echo "🔨 Creating distribution builds..."
docker run --rm \
  -v $(pwd)/builds:/app/builds \
  desktop-app:prod \
  npm run dist

echo "✅ Build complete! Check ./builds directory"
```

```bash
chmod +x build.sh
./build.sh
```

## Variables de Entorno

| Variable | Descripción | Valores |
|----------|-------------|---------|
| `NODE_ENV` | Entorno de ejecución | `development`, `production` |
| `ELECTRON_IS_DEV` | Modo desarrollo de Electron | `true`, `false` |
| `CHOKIDAR_USEPOLLING` | Hot reload en desarrollo | `true`, `false` |
| `DISABLE_ELECTRON_ENV` | Deshabilitar variables Electron | `1` |

## Puertos

| Puerto | Propósito |
|--------|-----------|
| 3000 | Puerto de desarrollo/web |
| 8080 | Puerto de Electron |

## Volúmenes

| Volumen | Propósito |
|---------|-----------|
| `./src` | Código fuente (desarrollo) |
| `./public` | Archivos públicos |
| `./builds` | Builds de distribución |
| `node_modules` | Dependencias de Node.js |

## Dependencias del Sistema Incluidas

- **Node.js 18** (Bullseye)
- **Herramientas de compilación**: make, g++, python3
- **Librerías de GUI**: GTK3, libgtk-3-0, libgbm1
- **Audio**: libasound2
- **Red**: libcups2, libdbus-1-3
- **Fuentes**: fonts-liberation
- **Utilidades**: xdg-utils, curl, wget

## Distribución Multiplataforma

### Plataformas Soportadas

| Plataforma | Formatos |
|------------|----------|
| **Linux** | AppImage, DEB, RPM, Snap |
| **Windows** | NSIS, ZIP, Portable |
| **macOS** | DMG, PKG, ZIP |

### Configuración Electron Builder

Agregar a `package.json`:

```json
{
  "build": {
    "appId": "com.empresa.desktop-app",
    "productName": "Desktop App",
    "directories": {
      "output": "builds"
    },
    "files": [
      "dist/**/*",
      "node_modules/**/*",
      "package.json"
    ],
    "linux": {
      "target": [
        {
          "target": "AppImage",
          "arch": ["x64"]
        },
        {
          "target": "deb",
          "arch": ["x64"]
        }
      ]
    },
    "win": {
      "target": [
        {
          "target": "nsis",
          "arch": ["x64"]
        }
      ]
    },
    "mac": {
      "target": [
        {
          "target": "dmg",
          "arch": ["x64"]
        }
      ]
    }
  }
}
```

## Optimizaciones

1. **Cache de dependencias**: Copia `package*.json` antes del código fuente
2. **Usuario no-root**: Seguridad mejorada
3. **Multi-stage**: Imágenes más pequeñas
4. **Volúmenes**: Desarrollo más rápido
5. **Hot reload**: Recarga automática en desarrollo

## Troubleshooting

### Error: `EACCES: permission denied`
```bash
# Cambiar ownership de archivos
sudo chown -R $USER:$USER .
```

### Error: `Cannot find module`
```bash
# Rebuild completo
docker-compose up --build desktop-app-dev
```

### Electron no carga recursos
```bash
# Verificar permisos de archivos
docker-compose exec desktop-app-dev ls -la /app
```

## Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f desktop-app-dev

# Acceder al contenedor
docker-compose exec desktop-app-dev bash

# Limpiar todo
docker-compose down -v --remove-orphans

# Verificar espacio usado
docker system df
docker system prune
```

## Estructura de Proyecto Recomendada

```
desktop-app/
├── Dockerfile
├── docker-compose.yml
├── package.json
├── .dockerignore
├── src/
│   ├── main/
│   │   ├── main.js
│   │   └── preload.js
│   ├── renderer/
│   │   ├── index.html
│   │   ├── index.js
│   │   └── styles/
│   └── assets/
├── public/
├── dist/
└── builds/
```

## Next Steps

1. Crear `package.json` con scripts de build
2. Configurar estructura de directorios
3. Implementar Electron main process
4. Crear scripts de build y distribución
5. Configurar CI/CD para automatización