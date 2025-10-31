// Configuración para el cliente RabbitMQ - Aplicación Desktop (Electron + Socket.io)
export const RABBITMQ_CONFIG = {
  // Configuración de Socket.io
  socketio: {
    url: process.env.RABBITMQ_SOCKETIO_URL || 'http://localhost:8080',
    options: {
      transports: ['websocket', 'polling'],
      timeout: 20000,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 10,
      maxReconnectionAttempts: 10,
      pingTimeout: 60000,
      pingInterval: 25000
    }
  },

  // Configuración de API REST
  api: {
    baseUrl: process.env.RABBITMQ_API_URL || 'http://localhost:8080/api',
    timeout: 30000,
    retries: 3
  },

  // Configuración de RabbitMQ (para debugging directo)
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

  // Configuración de eventos Socket.io
  events: {
    // Eventos de solicitud
    REQUEST_BALANCE: 'client:request_balance',
    REQUEST_TRANSACTIONS: 'client:request_transactions',
    REQUEST_LOANS: 'client:request_loans',
    REQUEST_LOAN: 'client:request_loan',
    UPDATE_PROFILE: 'client:update_profile',

    // Eventos de respuesta
    RESPONSE_BALANCE: 'server:response_balance',
    RESPONSE_TRANSACTIONS: 'server:response_transactions',
    RESPONSE_LOANS: 'server:response_loans',
    RESPONSE_LOAN: 'server:response_loan',
    RESPONSE_PROFILE: 'server:response_profile',

    // Eventos de notificación
    NOTIFICATION: 'server:notification',
    TRANSACTION_UPDATE: 'server:transaction_update',
    LOAN_UPDATE: 'server:loan_update',
    BALANCE_UPDATE: 'server:balance_update',

    // Eventos de sistema
    CONNECT: 'connect',
    DISCONNECT: 'disconnect',
    RECONNECT: 'reconnect',
    ERROR: 'error',
    AUTH_SUCCESS: 'auth_success',
    AUTH_ERROR: 'auth_error'
  },

  // Configuración de exchanges (vía Socket.io)
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

  // Configuración de timeouts
  timeouts: {
    default: 30000, // 30 segundos
    balance: 10000, // 10 segundos
    transactions: 20000, // 20 segundos
    loans: 45000, // 45 segundos
    profile: 15000, // 15 segundos
    auth: 5000 // 5 segundos para autenticación
  },

  // Configuración de retry
  retry: {
    maxAttempts: 3,
    initialDelay: 1000, // 1 segundo
    maxDelay: 10000, // 10 segundos
    multiplier: 2,
    backoffType: 'exponential'
  },

  // Configuración de headers de correlación
  correlation: {
    includeTimestamp: true,
    includeClientId: true,
    includeUserId: true,
    includePlatform: true,
    includeVersion: true,
    platform: 'electron',
    version: '1.0.0'
  },

  // Configuración de event handling
  eventHandling: {
    enableBatching: true,
    batchSize: 10,
    batchTimeout: 5000,
    enableDebouncing: true,
    debounceDelay: 300,
    enableThrottling: true,
    throttleRate: 100 // requests per minute
  },

  // Configuración de storage local (Electron Store)
  storage: {
    tokenKey: 'rabbitmq_token',
    clientIdKey: 'rabbitmq_client_id',
    sessionKey: 'rabbitmq_session',
    preferencesKey: 'rabbitmq_preferences',
    cacheKey: 'rabbitmq_cache'
  },

  // Configuración de logging
  logging: {
    level: process.env.NODE_ENV === 'development' ? 'debug' : 'info',
    enableConsole: true,
    enableFile: process.env.NODE_ENV === 'development',
    filePath: './logs/rabbitmq-client.log',
    maxFileSize: '10MB',
    maxFiles: 5
  }
};

// Configuración de prioridades por tipo de operación
export const OPERATION_PRIORITIES = {
  balance: 10,
  transactions: 8,
  loans: 5,
  profile: 7,
  notifications: 1,
  auth: 9,
  system: 3
};

// Configuración de exchange de dead letters
export const DEAD_LETTER_CONFIG = {
  exchange: 'banco.dlx',
  routingKeyPrefix: 'cliente.'
};

// Configuración específica para Electron
export const ELECTRON_CONFIG = {
  // Configuración de ventana principal
  window: {
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    show: false,
    center: true,
    title: 'Banco Desktop - Cliente'
  },

  // Configuración de menú
  menu: {
    enabled: true,
    template: [
      {
        label: 'Archivo',
        submenu: [
          { role: 'quit', label: 'Salir' }
        ]
      },
      {
        label: 'Ver',
        submenu: [
          { role: 'reload', label: 'Recargar' },
          { role: 'forceReload', label: 'Forzar Recarga' },
          { role: 'toggleDevTools', label: 'Herramientas de Desarrollador' },
          { type: 'separator' },
          { role: 'resetZoom', label: 'Zoom Real' },
          { role: 'zoomIn', label: 'Acercar' },
          { role: 'zoomOut', label: 'Alejar' },
          { type: 'separator' },
          { role: 'togglefullscreen', label: 'Pantalla Completa' }
        ]
      },
      {
        label: 'Ventana',
        submenu: [
          { role: 'minimize', label: 'Minimizar' },
          { role: 'close', label: 'Cerrar' }
        ]
      }
    ]
  },

  // Configuración de seguridad
  security: {
    contentSecurityPolicy: {
      enabled: true,
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", "data:", "https:"],
        connectSrc: ["'self'", "ws:", "wss:"],
        fontSrc: ["'self'"],
        objectSrc: ["'none'"],
        mediaSrc: ["'self'"],
        frameSrc: ["'none'"]
      }
    }
  }
};

// Configuración de tema y UI
export const UI_CONFIG = {
  theme: {
    primary: '#1e40af',
    secondary: '#64748b',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    background: '#f8fafc',
    surface: '#ffffff',
    text: '#1e293b'
  },

  // Configuración de notificaciones desktop
  notifications: {
    enabled: true,
    showInApp: true,
    showNative: true,
    duration: 5000,
    position: 'top-right'
  },

  // Configuración de layout
  layout: {
    sidebar: {
      width: 250,
      collapsedWidth: 60,
      enabled: true
    },
    header: {
      height: 60,
      enabled: true
    },
    content: {
      padding: 20,
      maxWidth: 1200
    }
  }
};