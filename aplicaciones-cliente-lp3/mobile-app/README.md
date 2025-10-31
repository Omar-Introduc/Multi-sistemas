# Aplicación Móvil Banco LP3

Aplicación móvil completa desarrollada en React Native con Expo para servicios bancarios.

## 📱 Características

### Funcionalidades Principales
- **Autenticación segura** con login y gestión de sesión
- **Dashboard principal** con resumen de cuentas y acciones rápidas
- **Gestión de cuentas** visualizando saldo y detalles
- **Transacciones** con historial y filtros
- **Pagos QR** generar y escanear códigos QR para pagos
- **Préstamos** solicitar préstamos con simulación de cuotas
- **Historial completo** de todas las actividades

### Tecnologías Utilizadas
- **React Native** con Expo
- **React Navigation** para navegación Stack y Tab
- **Axios** para comunicación con API
- **React Native QR Code SVG** para generación de códigos QR
- **Expo Camera** para escaneo de códigos QR
- **AsyncStorage** para persistencia local
- **RabbitMQ** para comunicación asíncrona (simulada)

## 🏗️ Estructura del Proyecto

```
mobile-app/
├── App.js                          # Componente principal y navegación
├── package.json                    # Dependencias del proyecto
├── README.md                       # Este archivo
├── screens/                        # Pantallas de la aplicación
│   ├── LoginScreen.js             # Pantalla de inicio de sesión
│   ├── HomeScreen.js              # Dashboard principal
│   ├── AccountsScreen.js          # Lista de cuentas
│   ├── TransactionsScreen.js      # Historial de transacciones
│   ├── QRGeneratorScreen.js       # Generar códigos QR
│   ├── QRScannerScreen.js         # Escanear códigos QR
│   ├── LoanRequestScreen.js       # Solicitar préstamos
│   └── HistoryScreen.js           # Historial general
├── components/                     # Componentes reutilizables
│   ├── Button.js                  # Componente de botón
│   ├── Input.js                   # Componente de entrada
│   ├── Card.js                    # Componente de tarjeta
│   ├── QRCodeComponent.js         # Componente de código QR
│   └── Alert.js                   # Componente de alertas
├── utils/                         # Utilidades y servicios
│   ├── api.js                     # Servicios API y RabbitMQ
│   ├── auth.js                    # Manejo de autenticación
│   └── navigation.js              # Configuración de navegación
└── styles/                        # Estilos y temas
    ├── theme.js                   # Tema de la aplicación
    └── styles.js                  # Estilos globales
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Node.js 16 o superior
- npm o yarn
- Expo CLI (`npm install -g @expo/cli`)
- Expo Go app en tu dispositivo móvil (opcional)

### Instalación de Dependencias

```bash
cd mobile-app
npm install
```

### Ejecutar la Aplicación

```bash
# Iniciar el servidor de desarrollo
npm start

# O con Expo CLI
expo start
```

### Opciones de Ejecución
- **Expo Go** (recomendado): Escanea el código QR con la app Expo Go
- **Emulador Android**: Presiona `a` después de ejecutar `npm start`
- **Emulador iOS**: Presiona `i` (solo en macOS)
- **Navegador web**: Presiona `w`

## 🎯 Uso de la Aplicación

### Credenciales de Prueba

La aplicación incluye credenciales de prueba para desarrollo:

```
Usuario 1:
- Email: usuario@banco.com
- Contraseña: 123456

Usuario 2:
- Email: maria@banco.com
- Contraseña: 654321
```

### Flujo de Uso

1. **Inicio de Sesión**: Usa las credenciales de prueba para acceder
2. **Dashboard**: Revisa el saldo total y acciones rápidas
3. **Cuentas**: Visualiza todas tus cuentas bancarias
4. **Transacciones**: Revisa el historial con filtros
5. **Generar QR**: Crea códigos QR para recibir pagos
6. **Escanear QR**: Escanea códigos para realizar pagos
7. **Préstamos**: Solicita préstamos con simulación
8. **Historial**: Revisa toda tu actividad bancaria

## 🔧 Características Técnicas

### Navegación
- **Stack Navigator**: Para navegación entre pantallas
- **Bottom Tabs**: Para navegación principal
- **Autenticación**: Protección de rutas no autenticadas

### Estado y Persistencia
- **AsyncStorage**: Para guardar sesión y datos locales
- **Context API**: Para manejo de estado global
- **Local State**: Para estado de componentes

### API y Comunicación
- **Axios**: Cliente HTTP para llamadas a API
- **RabbitMQ**: Comunicación asíncrona simulada
- **Mock Data**: Datos simulados para desarrollo

### UI/UX
- **Tema personalizado**: Colores y estilos consistentes
- **Responsive**: Adaptable a diferentes tamaños de pantalla
- **Animaciones**: Transiciones suaves entre pantallas
- **Iconos**: Iconografía consistente con Ionicons

## 📋 Scripts Disponibles

```bash
npm start              # Iniciar servidor de desarrollo
npm run android        # Ejecutar en Android
npm run ios           # Ejecutar en iOS
npm run web           # Ejecutar en navegador
npm run eject         # Expulsar de Expo (no reversible)
```

## 🔐 Seguridad

### Autenticación
- Validación de credenciales
- Manejo seguro de tokens
- Limpieza de sesión al cerrar
- Protección contra acceso no autorizado

### Datos
- Comunicación HTTPS simulada
- Validación de datos de entrada
- Manejo seguro de información bancaria

## 🐛 Solución de Problemas

### Errores Comunes

**Error de dependencias:**
```bash
npm install --legacy-peer-deps
```

**Metro Bundler problemas:**
```bash
npx react-native start --reset-cache
```

**Expo problemas:**
```bash
expo start --clear
```

### Debugging
- Usa React Native Debugger
- Habilita Remote JS Debugging
- Revisa logs de Metro Bundler

## 📱 Construcción para Producción

### Con Expo EAS

```bash
# Instalar EAS CLI
npm install -g @expo/eas-cli

# Configurar proyecto
eas build:configure

# Construir para Android
eas build --platform android

# Construir para iOS
eas build --platform ios
```

### APK de Desarrollo

```bash
# Generar APK para testing
npx expo install --fix
expo build:android -t apk
```

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

## 📞 Soporte

Para soporte técnico o consultas:
- Email: soporte@banco-lp3.com
- Documentación: [docs.banco-lp3.com](http://docs.banco-lp3.com)
- Issues: GitHub Issues

---

**Desarrollado para LP3 - Laboratorio de Programación 3**