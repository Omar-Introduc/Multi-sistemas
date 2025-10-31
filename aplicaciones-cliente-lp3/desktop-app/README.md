# Banco Desktop - Aplicación Electron

Una aplicación de gestión bancaria completa desarrollada con Electron para el curso LP3.

## Características

- 🔐 **Sistema de autenticación** con roles de usuario
- 🏦 **Gestión de cuentas bancarias** (ahorros, corriente, plazo fijo)
- 💰 **Transacciones en tiempo real** (depósitos, retiros, transferencias)
- 🏠 **Gestión de préstamos** con calculadora integrada
- 📱 **Generador de códigos QR** para pagos y transferencias
- 🗄️ **Base de datos SQLite** integrada
- 🐰 **Integración con RabbitMQ** para notificaciones
- 📊 **Dashboard con estadísticas** financieras
- 🎨 **Interfaz moderna** y responsive

## Estructura del Proyecto

```
aplicaciones-cliente-lp3/desktop-app/
├── package.json                 # Configuración del proyecto y dependencias
├── src/
│   ├── main/
│   │   ├── main.js             # Proceso principal de Electron
│   │   ├── preload.js          # Script de precarga para APIs seguras
│   │   └── config/
│   │       ├── database.js     # Configuración de base de datos SQLite
│   │       ├── rabbitmq.js     # Configuración de RabbitMQ
│   │       └── utils.js        # Utilidades y funciones auxiliares
│   └── renderer/
│       ├── index.html          # Página principal
│       ├── css/
│       │   ├── main.css        # Estilos principales
│       │   └── components.css  # Componentes de UI
│       ├── js/
│       │   ├── app.js          # Aplicación principal
│       │   ├── auth.js         # Manejo de autenticación
│       │   ├── router.js       # Sistema de rutas
│       │   └── utils.js        # Utilidades del frontend
│       ├── pages/              # Páginas de la aplicación
│       │   ├── Login.html      # Página de inicio de sesión
│       │   ├── Dashboard.html  # Panel principal
│       │   ├── Cuentas.html    # Gestión de cuentas
│       │   ├── Transacciones.html # Gestión de transacciones
│       │   ├── Prestamos.html  # Gestión de préstamos
│       │   └── QRGenerator.html # Generador de códigos QR
│       └── components/         # Componentes reutilizables
│           ├── Navigation      # Componentes de navegación
│           ├── Forms           # Formularios
│           ├── Tables          # Tablas
│           └── Modals          # Modales
```

## Requisitos

- Node.js 16 o superior
- npm o yarn
- Electron 28.x

## Instalación

1. **Instalar dependencias:**
   ```bash
   cd aplicaciones-cliente-lp3/desktop-app
   npm install
   ```

2. **Configurar variables de entorno** (opcional):
   ```bash
   # Crear archivo .env (opcional)
   RABBITMQ_HOST=localhost
   RABBITMQ_PORT=5672
   RABBITMQ_USER=guest
   RABBITMQ_PASSWORD=guest
   ```

## Ejecutar la Aplicación

### Modo Desarrollo
```bash
npm run dev
```

### Modo Producción
```bash
npm start
```

## Scripts Disponibles

- `npm start` - Ejecutar en modo producción
- `npm run dev` - Ejecutar en modo desarrollo con DevTools
- `npm run build` - Construir para distribución
- `npm run build:win` - Construir para Windows
- `npm run build:mac` - Construir para macOS
- `npm run build:linux` - Construir para Linux
- `npm run pack` - Empaquetar sin instalador
- `npm run dist` - Crear distribución completa

## Usuarios de Prueba

La aplicación incluye usuarios de prueba predefinidos:

| Usuario | Contraseña | Rol | Nombre |
|---------|------------|-----|--------|
| admin | admin123 | admin | Administrador |
| usuario | 123456 | user | Usuario Demo |
| banco | banco2023 | admin | Sistema Bancario |

## Funcionalidades

### 🔐 Autenticación
- Inicio de sesión seguro
- Gestión de sesiones
- Control de acceso por roles
- Logout automático por inactividad

### 🏦 Cuentas Bancarias
- Crear cuentas (ahorros, corriente, plazo fijo)
- Ver detalles de cuenta
- Bloquear/activar cuentas
- Búsqueda y filtrado
- Estadísticas de balance

### 💰 Transacciones
- Realizar transacciones (depósitos, retiros)
- Transferencias entre cuentas
- Historial completo de transacciones
- Filtros por fecha, tipo y estado
- Exportar transacciones
- Generación de recibos

### 🏠 Préstamos
- Solicitar diferentes tipos de préstamos
- Calculadora de préstamos integrada
- Tabla de amortización
- Historial de préstamos
- Estados (activo, pendiente, completado)

### 📱 Generador QR
- Códigos QR para pagos
- Códigos QR para transferencias
- Códigos QR con información de cuenta
- Códigos QR personalizados
- Historial de códigos generados
- Descarga e impresión de códigos

### 📊 Dashboard
- Estadísticas financieras en tiempo real
- Acciones rápidas
- Transacciones recientes
- Resumen de cuentas
- Gráficos de análisis financiero

## Arquitectura Técnica

### Frontend
- **HTML5** - Estructura semántica
- **CSS3** - Estilos modernos con variables CSS
- **JavaScript ES6+** - Lógica de frontend
- **Font Awesome** - Iconografía

### Backend (Electron Main Process)
- **Node.js** - Runtime de JavaScript
- **SQLite3** - Base de datos embebida
- **Electron-Store** - Almacenamiento de configuración
- **Axios** - Cliente HTTP
- **QRCode** - Generación de códigos QR
- **Node-PTY** - Pseudo-terminal
- **AMQPLib** - Cliente RabbitMQ

### Seguridad
- **Context Isolation** habilitado
- **Node Integration** deshabilitado
- **Preload Scripts** para APIs seguras
- **CSP** (Content Security Policy)
- Sanitización de entrada de usuario

## Base de Datos

La aplicación utiliza SQLite con las siguientes tablas:

### users
- id, username, email, full_name, dni, phone, created_at, updated_at

### accounts
- id, user_id, account_number, account_type, balance, status, created_at

### transactions
- id, account_id, transaction_type, amount, description, reference_number, status, created_at

### loans
- id, user_id, loan_type, amount, interest_rate, term_months, monthly_payment, status, created_at

### qr_codes
- id, account_id, qr_data, created_at

## Integración con RabbitMQ

La aplicación puede conectarse a RabbitMQ para:
- Notificaciones en tiempo real
- Eventos de transacciones
- Sincronización entre instancias
- Logs y monitoreo

## Distribución

### Windows
```bash
npm run build:win
```
Genera: `dist/Banco Desktop Setup 1.0.0.exe`

### macOS
```bash
npm run build:mac
```
Genera: `dist/Banco Desktop-1.0.0.dmg`

### Linux
```bash
npm run build:linux
```
Genera: `dist/Banco Desktop-1.0.0.AppImage`

## Configuración Avanzada

### Personalización de Tema
Modifica las variables CSS en `src/renderer/css/main.css`:
```css
:root {
  --primary-color: #2563eb;      /* Color principal */
  --success-color: #059669;      /* Color de éxito */
  --warning-color: #d97706;      /* Color de advertencia */
  --error-color: #dc2626;        /* Color de error */
}
```

### Configuración de Base de Datos
Modifica la configuración en `src/main/config/database.js`:
```javascript
this.dbPath = path.join(app.getPath('userData'), 'banco.db');
```

### Configuración de RabbitMQ
Modifica la configuración en `src/main/config/rabbitmq.js`:
```javascript
const defaultConfig = {
  hostname: process.env.RABBITMQ_HOST || 'localhost',
  port: process.env.RABBITMQ_PORT || 5672,
  username: process.env.RABBITMQ_USER || 'guest',
  password: process.env.RABBITMQ_PASSWORD || 'guest',
};
```

## Desarrollo

### Agregar Nuevas Páginas
1. Crear archivo HTML en `src/renderer/pages/`
2. Registrar ruta en `src/renderer/js/router.js`
3. Agregar enlace de navegación en `src/renderer/index.html`

### Agregar Nuevos Componentes
1. Crear archivo JavaScript en `src/renderer/components/`
2. Importar y usar en las páginas correspondientes

### API Personalizadas
1. Agregar handler en `src/main/main.js`
2. Exponer API en `src/main/preload.js`
3. Usar en el frontend con `window.electronAPI`

## Solución de Problemas

### Error: "Cannot find module"
```bash
npm install
```

### Error: "Database is locked"
Cerrar todas las instancias de la aplicación y reiniciar.

### Error: "RabbitMQ connection failed"
Verificar que RabbitMQ esté ejecutándose y la configuración sea correcta.

### Performance Issues
- Limpiar historial de QR codes
- Optimizar consultas de base de datos
- Reducir frecuencia de actualizaciones automáticas

## Licencia

MIT License - Ver archivo LICENSE para más detalles.

## Soporte

Para soporte técnico o reportar bugs, contactar al equipo de desarrollo LP3.
