# Configuración RabbitMQ para Aplicaciones Cliente

## 📋 Resumen

Este documento describe la configuración completa de RabbitMQ para las aplicaciones cliente del sistema bancario LP3, incluyendo tanto la aplicación móvil (React Native) como la aplicación desktop (Electron).

## 🏗️ Arquitectura

### Configuración de RabbitMQ

La configuración incluye las siguientes colas específicas para clientes:

- **cliente.requests** - Solicitudes de operaciones bancarias
- **cliente.transactions** - Consultas de transacciones
- **cliente.loans** - Operaciones de préstamos
- **cliente.notifications** - Notificaciones en tiempo real

### Aplicaciones Cliente

#### 1. Aplicación Móvil (React Native)
- **Cliente**: WebSocket + HTTP API Gateway
- **Librería**: Custom client con WebSocket polyfill
- **Archivo**: `src/services/rabbitmq/react-native-client.js`

#### 2. Aplicación Desktop (Electron)
- **Cliente**: Socket.io + Electron IPC
- **Librería**: socket.io-client
- **Archivo**: `src/services/rabbitmq/socketio-client.js`

## 🔧 Configuración

### Configuración de RabbitMQ

#### Usuarios y Permisos

```json
{
  "name": "cliente_user",
  "password": "cliente_secure_2024",
  "tags": ["cliente"],
  "limits": {
    "max_channels": 30,
    "max_connections": 15
  }
}
```

#### Exchanges

- `cliente.requests` - Exchange para solicitudes de clientes
- `cliente.responses` - Exchange para respuestas del servidor
- `cliente.notifications` - Exchange para notificaciones

#### Colas

- `cliente.requests.requests` - Cola para solicitudes generales
- `cliente.requests.transactions` - Cola para consultas de transacciones
- `cliente.requests.loans` - Cola para operaciones de préstamos
- `cliente.notifications.push` - Cola para notificaciones push

#### Políticas

- **cliente-ha-policy**: Alta disponibilidad para todas las colas de cliente
- **cliente-requests-policy**: TTL y dead letter para requests

### Configuración de Aplicación Móvil

#### Dependencias

```json
{
  "dependencies": {
    "axios": "^1.4.0",
    "uuid": "^9.0.0",
    "socket.io-client": "^4.7.2",
    "react-native-websocket": "^5.0.0"
  }
}
```

#### Variables de Entorno

```env
RABBITMQ_API_URL=http://localhost:8080/api
RABBITMQ_WS_URL=ws://localhost:8080/ws
RABBITMQ_URL=amqp://localhost:5672
```

#### Configuración del Cliente

```javascript
import { initializeRabbitMQ, useRabbitMQInterceptor } from '../services/rabbitmq';

// Inicialización completa
const instance = await initializeRabbitMQ();
const { interceptor, services } = instance;

// Hook para React Native
const { interceptor, isInitialized, error } = useRabbitMQInterceptor();
```

### Configuración de Aplicación Desktop

#### Dependencias

```json
{
  "dependencies": {
    "socket.io-client": "^4.7.2",
    "uuid": "^9.0.0",
    "winston": "^3.11.0",
    "react": "^18.2.0",
    "electron-store": "^8.1.0"
  }
}
```

#### Configuración Electron (Main Process)

```javascript
import { setupElectronMain } from '../services/rabbitmq';

// En main.js
import { setupElectronMain } from './services/rabbitmq';

const mainWindow = new BrowserWindow(ELECTRON_CONFIG.window);
setupElectronMain(mainWindow);
```

#### Configuración Electron (Renderer Process)

```javascript
import { setupElectronRenderer, useDesktopRabbitMQ } from '../services/rabbitmq';

// Cliente para renderer
const client = setupElectronRenderer();

// Hook para React en Electron
const { services, isInitialized } = useDesktopRabbitMQ();
```

## 📡 API y Servicios

### Servicios de Cuenta y Saldo

#### Obtener Saldo
```javascript
const result = await services.getBalance({
  accountId: 'ACC_123',
  clientId: 'CLIENT_456',
  includeHistory: true
});
```

#### Obtener Transacciones
```javascript
const result = await services.getTransactions({
  accountId: 'ACC_123',
  startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
  endDate: new Date(),
  limit: 20,
  sortBy: 'timestamp',
  sortOrder: 'desc'
});
```

### Servicios de Préstamos

#### Obtener Préstamos
```javascript
const result = await services.getLoans({
  clientId: 'CLIENT_456',
  includePayments: true,
  includeDocuments: true
});
```

#### Solicitar Préstamo
```javascript
const result = await services.requestLoan({
  amount: 25000,
  term: 24,
  purpose: 'Renovación de negocio',
  type: 'comercial',
  interestRate: 0.18,
  clientId: 'CLIENT_456'
});
```

### Servicios de Perfil

#### Actualizar Perfil
```javascript
const result = await services.updateProfile({
  clientId: 'CLIENT_456',
  firstName: 'Juan',
  lastName: 'Pérez',
  email: 'juan.perez@email.com',
  phone: '+51 999 888 777',
  occupation: 'Ingeniero',
  monthlyIncome: 5000
});
```

#### Obtener Perfil
```javascript
const result = await services.getProfile('CLIENT_456', {
  includePreferences: true,
  includeStatistics: true
});
```

## 🔔 Notificaciones en Tiempo Real

### Suscripción a Notificaciones

```javascript
await services.subscribeToNotifications((notification) => {
  // Manejar notificación
  console.log('Notificación:', notification);
  
  // Mostrar en la UI
  showNotification(notification.title, notification.message);
});
```

### Tipos de Notificaciones

- **transaction_update**: Actualizaciones de transacciones
- **loan_update**: Cambios en el estado de préstamos
- **balance_update**: Cambios en el saldo de cuenta
- **system_alert**: Alertas del sistema

## 🔄 Manejo de Conexiones y Reconexión

### Reconexión Automática

Ambos clientes implementan reconexión automática con backoff exponencial:

```javascript
// Configuración de reconexión
const RECONNECT_CONFIG = {
  maxAttempts: 10,
  initialDelay: 1000,
  maxDelay: 30000,
  multiplier: 2
};
```

### Heartbeat

- **Intervalo**: 30 segundos
- **Timeout**: 60 segundos
- **Ping/Pong**: Activado para detectar conexiones muertas

## 🆔 Correlation IDs

### Generación

```javascript
generateCorrelationId() {
  return `${clientId}_${Date.now()}_${uuidv4()}`;
}
```

### Uso

Los correlation IDs se incluyen en:
- Headers de mensajes AMQP
- Propiedades de mensajes WebSocket
- Respuestas del servidor
- Logs de debugging

## ⏱️ Timeouts

### Por Tipo de Operación

```javascript
const TIMEOUTS = {
  default: 30000,      // 30 segundos
  balance: 10000,      // 10 segundos
  transactions: 20000, // 20 segundos
  loans: 45000,        // 45 segundos
  profile: 15000,      // 15 segundos
  auth: 5000           // 5 segundos
};
```

## 🔁 Retry Logic

### Configuración

```javascript
const RETRY_CONFIG = {
  maxAttempts: 3,
  initialDelay: 1000,
  maxDelay: 10000,
  multiplier: 2,
  backoffType: 'exponential'
};
```

### Comportamiento

1. **Intento inicial**: Envío inmediato
2. **Reintentos**: Backoff exponencial
3. **Límite**: Máximo 3 intentos
4. **Fallback**: HTTP/REST API como respaldo

## 🔐 Seguridad

### Autenticación

- **Tokens JWT**: Para autenticación con API Gateway
- **Credenciales RabbitMQ**: `cliente_user` / `cliente_secure_2024`
- **Headers de seguridad**: Incluyen clientId, userId, platform

### Headers de Correlación

```javascript
const headers = {
  clientId: 'mobile_client_123',
  userId: 'user_456',
  platform: 'react-native',
  timestamp: Date.now(),
  correlationId: 'corr_789'
};
```

## 📊 Monitoreo y Estadísticas

### Métricas Disponibles

- **Estado de conexión**: Conectado/Desconectado
- **Requests pendientes**: Contador de requests en vuelo
- **Intentos de reconexión**: Número de reconexiones realizadas
- **Estadísticas de rendimiento**: Uptime, memoria, etc.

### Obtener Estado

```javascript
// Móvil
const status = services.getConnectionStatus();

// Desktop
const stats = services.getClientStatistics();
console.log(stats);
```

## 🧪 Testing y Ejemplos

### Aplicación Móvil

```javascript
// Ver archivo: mobile-app/src/services/rabbitmq/examples/usage-example.js
import RabbitMQExample from '../examples/usage-example';

// Usar en componente
<RabbitMQExample />
```

### Aplicación Desktop

```javascript
// Ver archivo: desktop-app/src/services/rabbitmq/examples/usage-example.js
import DesktopRabbitMQExample from '../examples/usage-example';

// Usar en componente
<DesktopRabbitMQExample />
```

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Aplicación móvil
cd mobile-app
npm install

# Aplicación desktop
cd desktop-app
npm install
```

### 2. Configuración de Entorno

```bash
# Crear archivo .env en cada aplicación
RABBITMQ_API_URL=http://localhost:8080/api
RABBITMQ_WS_URL=ws://localhost:8080/ws
```

### 3. Inicialización

```javascript
// En tu aplicación
import { initializeRabbitMQ } from '../services/rabbitmq';

const init = async () => {
  try {
    const instance = await initializeRabbitMQ();
    console.log('RabbitMQ inicializado:', instance);
  } catch (error) {
    console.error('Error inicializando RabbitMQ:', error);
  }
};
```

### 4. Uso Básico

```javascript
// Obtener saldo
const balance = await services.getBalance({ accountId: 'ACC_123' });
console.log('Saldo:', balance.data);

// Suscribirse a notificaciones
await services.subscribeToNotifications((notification) => {
  console.log('Nueva notificación:', notification);
});
```

## 🔧 Solución de Problemas

### Problemas Comunes

1. **Conexión fallida**
   - Verificar URL del API Gateway
   - Comprobar credenciales de RabbitMQ
   - Revisar firewall/proxy

2. **Timeout en requests**
   - Aumentar timeout para operaciones complejas
   - Verificar conectividad de red
   - Revisar logs del servidor

3. **Reconexión excesiva**
   - Verificar estabilidad de la red
   - Ajustar configuración de heartbeat
   - Revisar logs de errores

### Logs de Debug

```javascript
// Habilitar logs detallados
const RABBITMQ_CONFIG = {
  logging: {
    level: 'debug',
    enableConsole: true
  }
};
```

## 📝 Notas Importantes

1. **Compatibilidad**: El cliente móvil usa WebSocket polyfill para React Native
2. **Persistencia**: Tokens y configuraciones se almacenan localmente
3. **Escalabilidad**: Implementa connection pooling y request batching
4. **Seguridad**: Todos los mensajes incluyen correlation IDs y headers de seguridad
5. **Performance**: Optimizado para operaciones móviles y desktop con diferentes prioridades

## 🎯 Próximos Pasos

1. Implementar API Gateway para comunicación HTTP/WebSocket
2. Configurar certificado SSL/TLS para producción
3. Implementar cache local para datos frecuentes
4. Agregar soporte para modo offline
5. Optimizar reconexión y manejo de errores

---

**Fecha**: 2025-10-30  
**Versión**: 1.0  
**Estado**: ✅ Completado