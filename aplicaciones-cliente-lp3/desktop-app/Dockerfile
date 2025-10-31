# Dockerfile para aplicación Desktop con Node.js 18 y Electron
# Multi-stage build para optimizar tamaño de imagen

# ===== FASE DE DESARROLLO =====
FROM node:18-bullseye-slim as development

# Instalar dependencias del sistema necesarias para Electron
RUN apt-get update && apt-get install -y \
    curl \
    git \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para desarrollo
RUN useradd -m -s /bin/bash appuser && \
    usermod -aG sudo appuser

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias primero para aprovechar cache
COPY package*.json ./

# Instalar dependencias de Node.js incluyendo devDependencies
RUN npm ci --include=dev

# Copiar código fuente
COPY . .

# Cambiar ownership de archivos al usuario no-root
RUN chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Exponer puerto para desarrollo
EXPOSE 3000

# Comando por defecto para desarrollo
CMD ["npm", "run", "dev"]

# ===== FASE DE BUILD DE PRODUCCIÓN =====
FROM node:18-bullseye-slim as build

# Instalar dependencias del sistema para build
RUN apt-get update && apt-get install -y \
    curl \
    git \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    xvfb \
    python3 \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar solo dependencias de producción para el build
RUN npm ci --only=production

# Copiar código fuente
COPY . .

# Build de la aplicación
RUN npm run build

# ===== FASE DE DISTRIBUCIÓN =====
FROM node:18-bullseye-slim as production

# Instalar dependencias mínimas para runtime
RUN apt-get update && apt-get install -y \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para producción
RUN useradd -m -s /bin/bash appuser

# Configurar directorio de trabajo
WORKDIR /app

# Copiar node_modules y package.json desde build stage
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package*.json ./

# Copiar archivos de build desde build stage
COPY --from=build /app/dist ./dist
COPY --from=build /app/package-lock.json ./

# Instalar electron-builder para crear distribución
RUN npm install -g electron-builder

# Configurar electron-builder
ENV ELECTRON_CACHE=/tmp/electron
RUN mkdir -p /tmp/electron

# Configurar variables de entorno para producción
ENV NODE_ENV=production
ENV ELECTRON_IS_DEV=false

# Crear directorio para builds de distribución
RUN mkdir -p /app/builds

# Cambiar ownership
RUN chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Comando por defecto para producción
CMD ["npm", "start"]

# ===== COMANDOS DE BUILD PARA DISTRIBUCIÓN =====

# Para construir ejecutables de distribución (Windows, macOS, Linux)
# docker build --target production --build-arg DISABLE_ELECTRON_ENV=1 -t desktop-app .
# docker run --rm -v $(pwd)/builds:/app/builds desktop-app npm run dist

# Para crear builds para diferentes plataformas:
# npm run dist:linux    # Linux AppImage, deb, rpm
# npm run dist:win      # Windows installer
# npm run dist:mac      # macOS app

# ===== CONFIGURACIÓN DE DOCKER COMPOSE =====

# En docker-compose.yml usar:
# build:
#   context: .
#   target: development  # Para desarrollo
#   # target: production # Para producción
#   dockerfile: Dockerfile

# Ports:
#   - "3000:3000"
#   - "8080:8080" # Para electron

# Volumes:
#   - ./src:/app/src        # Para desarrollo
#   - ./public:/app/public  # Para desarrollo
#   - ./builds:/app/builds  # Para distribución

# Environment:
#   - NODE_ENV=development  # O production
#   - CHOKIDAR_USEPOLLING=true # Para hot reload