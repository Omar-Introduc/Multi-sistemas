# Dockerfile para Aplicación Cliente Móvil - React Native/Expo
# Basado en Node.js 18

FROM node:18-bullseye

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para desarrollo móvil
RUN apt-get update && apt-get install -y \
    # Herramientas básicas
    git \
    curl \
    wget \
    unzip \
    # Java 11 (requerido para Android SDK)
    openjdk-11-jdk \
    # Librerías para desarrollo móvil
    libc6-dev \
    libstdc++6 \
    # Herramientas de construcción
    build-essential \
    # Dependencias adicionales
    file \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Configurar variables de entorno para Java
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/tools:$ANDROID_HOME/tools/bin:$ANDROID_HOME/platform-tools

# Crear directorio para Android SDK
RUN mkdir -p $ANDROID_HOME

# Descargar y configurar Android SDK Command Line Tools
RUN wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O commandlinetools.zip && \
    unzip commandlinetools.zip -d $ANDROID_HOME/ && \
    rm commandlinetools.zip && \
    mkdir -p $ANDROID_HOME/cmdline-tools/latest && \
    mv $ANDROID_HOME/cmdline-tools/* $ANDROID_HOME/cmdline-tools/latest/ 2>/dev/null || true

# Configurar Android SDK y descargar componentes necesarios
RUN yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --licenses && \
    $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager \
    "platform-tools" \
    "platforms;android-33" \
    "build-tools;33.0.2" \
    "system-images;android-33;google_apis;x86_64"

# Configurar React Native Environment variables
ENV REACT_NATIVE_PACKAGER_HOSTNAME=0.0.0.0

# Instalar Expo CLI globalmente
RUN npm install -g @expo/cli react-native-cli

# Instalar herramientas de desarrollo útiles
RUN npm install -g \
    yarn \
    @react-native-community/cli \
    @react-native-community/cli-platform-android

# Crear usuario no-root para desarrollo seguro
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 reactjs

# Cambiar ownership del directorio de trabajo
RUN chown -R reactjs:nodejs /app

# Cambiar a usuario no-root
USER reactjs

# Instalar dependencias de node modules si existe package.json
COPY package*.json ./
RUN npm install --silent

# Copiar código fuente de la aplicación
COPY . .

# Exponer puerto para Metro Bundler (Expo/React Native)
EXPOSE 8081

# Exponer puerto para desarrollo web de Expo
EXPOSE 19000
EXPOSE 19001

# Variables de entorno por defecto
ENV NODE_ENV=development
ENV EXPO_USE_STATIC=1

# Comandos por defecto
# El contenedor puede usarse para:
# 1. Ejecutar la aplicación: npm start
# 2. Construir para desarrollo: npx react-native start
# 3. Construir para producción: eas build --platform all

CMD ["npm", "start"]