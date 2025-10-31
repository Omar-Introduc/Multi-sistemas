// Configuración para el cliente RabbitMQ - Aplicación Móvil React Native
export const RABBITMQ_CONFIG = {
  // Configuración de conexión para React Native (vía API Gateway)
  api: {
    baseUrl: process.env.RABBITMQ_API_URL || 'http://localhost:8080/api',
    websocketUrl: process.env.RABBITMQ_WS_URL || 'ws://localhost:8080/ws',
    auth: {
      loginEndpoint: '/auth/login',
      refreshEndpoint: '/auth/refresh',
      tokenKey: 'rabbitmq_token'
    }
  },

  // Configuración de conexión directa AMQP (solo para desarrollo)
  connection: {
    url: process.env.RABBITMQ_URL || 'amqp://localhost:5672',
    credentials: {
      username: 'cliente_user',
      password: 'cliente_secure_2024'
    },
    options: {
      heartbeat: 60,
      reconnectTimeInSeconds: 3,
      connectionTimeout: 10000,
      maxRetriesPerRequest: 3,
      noDelay: true,
      keepAlive: true
    }
  },

  // Virtual host
  vhost: '/banco',

  // Configuración de endpoints de la API Gateway
  endpoints: {
    balance: '/balance',
    transactions: '/transactions',
    loans: '/loans',
    profile: '/profile',
    notifications: '/notifications'
  },

  // Configuración de exchanges (a través de API Gateway)
  exchanges: {
    requests: 'cliente.requests',
    responses: 'cliente.responses',
    notifications: 'cliente.notifications'
  },

  // Configuración de queues específicas para clientes
  queues: {
    requests: 'cliente.requests.requests',
    transactions: 'cliente.requests.transactions',
    loans: 'cliente.requests.loans',
    notifications: 'cliente.notifications.push'
  },

  // Routing keys
  routingKeys: {
    // Requests
    GET_BALANCE: 'cliente.requests.balance',
    GET_TRANSACTIONS: 'cliente.requests.transactions',
    GET_LOANS: 'cliente.requests.loans',
    REQUEST_LOAN: 'cliente.requests.loans.request',
    UPDATE_PROFILE: 'cliente.requests.profile.update',
    
    // Responses
    RESPONSE_PREFIX: 'cliente.responses.',
    
    // Notifications
    NOTIFICATION_PREFIX: 'cliente.notifications.'
  },

  // Configuración de timeouts (en milisegundos)
  timeouts: {
    default: 30000, // 30 segundos
    balance: 10000, // 10 segundos
    transactions: 20000, // 20 segundos
    loans: 45000, // 45 segundos
    profile: 15000, // 15 segundos
    websocket: 5000 // 5 segundos para WebSocket
  },

  // Configuración de retry
  retry: {
    maxAttempts: 3,
    initialDelay: 1000, // 1 segundo
    maxDelay: 10000, // 10 segundos
    multiplier: 2,
    backoffType: 'exponential' // 'exponential', 'linear', 'fixed'
  },

  // Configuración de headers de correlación
  correlation: {
    includeTimestamp: true,
    includeClientId: true,
    includeUserId: true,
    includePlatform: true,
    platform: 'react-native'
  },

  // Configuración de WebSocket
  websocket: {
    heartbeatInterval: 30000, // 30 segundos
    reconnectDelay: 5000, // 5 segundos
    maxReconnectAttempts: 10,
    enablePingPong: true
  },

  // Configuración de almacenamiento local
  storage: {
    tokenKey: 'rabbitmq_token',
    clientIdKey: 'rabbitmq_client_id',
    lastSyncKey: 'rabbitmq_last_sync'
  }
};

// Configuración de prioridades por tipo de operación
export const OPERATION_PRIORITIES = {
  balance: 10,
  transactions: 8,
  loans: 5,
  profile: 7,
  notifications: 1,
  auth: 9
};

// Configuración de exchange de dead letters
export const DEAD_LETTER_CONFIG = {
  exchange: 'banco.dlx',
  routingKeyPrefix: 'cliente.'
};

// Configuración específica para React Native
export const REACT_NATIVE_CONFIG = {
  // Habilitar modo offline
  offlineMode: {
    enabled: true,
    queueRequests: true,
    maxOfflineRequests: 100,
    syncInterval: 60000 // 1 minuto
  },

  // Configuración de notificaciones push
  pushNotifications: {
    enabled: true,
    topics: ['cliente.notifications', 'cliente.alerts'],
    includeData: true
  },

  // Configuración de background sync
  backgroundSync: {
    enabled: true,
    interval: 300000, // 5 minutos
    maxRetries: 3
  }
};