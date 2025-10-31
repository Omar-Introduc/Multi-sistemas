import io from 'socket.io-client';
import { v4 as uuidv4 } from 'uuid';
import { RABBITMQ_CONFIG, OPERATION_PRIORITIES } from './config';

class SocketIORabbitMQClient {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.pendingRequests = new Map();
    this.eventListeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.clientId = `desktop_${uuidv4()}`;
    this.authToken = null;
    this.userId = null;
    this.heartbeatInterval = null;
    this.connectionState = 'disconnected'; // disconnected, connecting, connected, reconnecting
  }

  // Generar correlation ID único
  generateCorrelationId() {
    return `${this.clientId}_${Date.now()}_${uuidv4()}`;
  }

  // Conectar usando Socket.io
  async connect() {
    try {
      console.log('🔗 Conectando a RabbitMQ (Socket.io)...');
      this.connectionState = 'connecting';

      // Configurar autenticación
      await this.authenticate();
      
      // Configurar opciones de conexión
      const socketOptions = {
        ...RABBITMQ_CONFIG.socketio.options,
        auth: {
          token: this.authToken,
          clientId: this.clientId,
          platform: 'electron'
        }
      };

      // Conectar socket
      this.socket = io(RABBITMQ_CONFIG.socketio.url, socketOptions);

      // Configurar eventos de conexión
      this.setupConnectionEvents();
      
      // Configurar eventos de RabbitMQ
      this.setupRabbitMQEvents();

      // Esperar a que la conexión esté lista
      await this.waitForConnection();
      
      this.isConnected = true;
      this.connectionState = 'connected';
      this.reconnectAttempts = 0;
      
      console.log('✅ Conexión Socket.io establecida');
      
      // Iniciar heartbeat
      this.startHeartbeat();
      
      return true;
    } catch (error) {
      console.error('❌ Error conectando a RabbitMQ:', error);
      this.connectionState = 'disconnected';
      this.scheduleReconnect();
      throw error;
    }
  }

  // Autenticación con el servidor
  async authenticate() {
    try {
      const credentials = {
        username: 'cliente_user',
        password: 'cliente_secure_2024',
        clientId: this.clientId,
        platform: 'electron',
        version: RABBITMQ_CONFIG.correlation.version
      };

      // Usar fetch para autenticación HTTP
      const response = await fetch(`${RABBITMQ_CONFIG.api.baseUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
      });

      if (!response.ok) {
        throw new Error(`Authentication failed: ${response.statusText}`);
      }

      const data = await response.json();
      this.authToken = data.token;
      this.userId = data.userId;
      
      console.log('✅ Autenticación exitosa');
    } catch (error) {
      console.error('❌ Error en autenticación:', error);
      throw error;
    }
  }

  // Configurar eventos de conexión
  setupConnectionEvents() {
    this.socket.on('connect', () => {
      console.log('🔌 Socket.io conectado');
      this.isConnected = true;
      this.connectionState = 'connected';
      this.reconnectAttempts = 0;
    });

    this.socket.on('disconnect', (reason) => {
      console.log('🔌 Socket.io desconectado:', reason);
      this.isConnected = false;
      this.connectionState = 'disconnected';
      this.handleDisconnection();
    });

    this.socket.on('connect_error', (error) => {
      console.error('❌ Error de conexión Socket.io:', error);
      this.connectionState = 'error';
      this.scheduleReconnect();
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log('🔄 Reconectado después de', attemptNumber, 'intentos');
      this.connectionState = 'connected';
      this.isConnected = true;
    });

    this.socket.on('reconnect_error', (error) => {
      console.error('❌ Error en reconexión:', error);
    });

    this.socket.on('reconnect_failed', () => {
      console.error('❌ Falló la reconexión');
      this.connectionState = 'failed';
    });
  }

  // Configurar eventos de RabbitMQ
  setupRabbitMQEvents() {
    // Eventos de respuesta
    Object.values(RABBITMQ_CONFIG.events).forEach(eventName => {
      if (eventName.startsWith('server:response_')) {
        this.socket.on(eventName, (data) => {
          this.handleResponseMessage(eventName, data);
        });
      }
    });

    // Eventos de notificación
    this.socket.on(RABBITMQ_CONFIG.events.NOTIFICATION, (data) => {
      this.handleNotificationMessage(data);
    });

    this.socket.on(RABBITMQ_CONFIG.events.TRANSACTION_UPDATE, (data) => {
      this.handleTransactionUpdate(data);
    });

    this.socket.on(RABBITMQ_CONFIG.events.LOAN_UPDATE, (data) => {
      this.handleLoanUpdate(data);
    });

    this.socket.on(RABBITMQ_CONFIG.events.BALANCE_UPDATE, (data) => {
      this.handleBalanceUpdate(data);
    });

    // Eventos de autenticación
    this.socket.on(RABBITMQ_CONFIG.events.AUTH_SUCCESS, (data) => {
      console.log('✅ Autenticación Socket.io exitosa');
    });

    this.socket.on(RABBITMQ_CONFIG.events.AUTH_ERROR, (error) => {
      console.error('❌ Error de autenticación Socket.io:', error);
    });
  }

  // Manejar mensaje de respuesta
  handleResponseMessage(eventName, data) {
    const correlationId = data.correlationId;
    
    if (correlationId && this.pendingRequests.has(correlationId)) {
      const requestInfo = this.pendingRequests.get(correlationId);
      
      if (data.success) {
        requestInfo.resolve({
          data: data.payload,
          correlationId,
          responseType: eventName,
          timestamp: Date.now()
        });
      } else {
        requestInfo.reject(new Error(data.error || 'Error en el servidor'));
      }
      
      this.pendingRequests.delete(correlationId);
    }
  }

  // Manejar notificaciones
  handleNotificationMessage(data) {
    const callback = this.eventListeners.get('notifications');
    if (callback) {
      callback(data);
    }

    // Emitir evento global para la aplicación
    if (global?.app?.emit) {
      global.app.emit('notification', data);
    }
  }

  // Manejar actualizaciones de transacciones
  handleTransactionUpdate(data) {
    const callback = this.eventListeners.get('transactionUpdate');
    if (callback) {
      callback(data);
    }
  }

  // Manejar actualizaciones de préstamos
  handleLoanUpdate(data) {
    const callback = this.eventListeners.get('loanUpdate');
    if (callback) {
      callback(data);
    }
  }

  // Manejar actualizaciones de saldo
  handleBalanceUpdate(data) {
    const callback = this.eventListeners.get('balanceUpdate');
    if (callback) {
      callback(data);
    }
  }

  // Esperar a que la conexión esté lista
  waitForConnection() {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Connection timeout'));
      }, RABBITMQ_CONFIG.api.timeout);

      if (this.socket?.connected) {
        clearTimeout(timeout);
        resolve();
      } else {
        this.socket.once('connect', () => {
          clearTimeout(timeout);
          resolve();
        });
      }
    });
  }

  // Enviar solicitud vía Socket.io
  async request(type, payload, options = {}) {
    if (!this.isConnected) {
      throw new Error('No hay conexión activa con RabbitMQ');
    }

    const correlationId = options.correlationId || this.generateCorrelationId();
    const timeout = options.timeout || RABBITMQ_CONFIG.timeouts.default;
    const retryCount = options.retryCount || 0;
    
    const requestPromise = new Promise((resolve, reject) => {
      // Configurar timeout
      const timeoutId = setTimeout(() => {
        if (this.pendingRequests.has(correlationId)) {
          this.pendingRequests.delete(correlationId);
          reject(new Error(`Timeout: ${timeout}ms`));
        }
      }, timeout);

      // Almacenar request info
      this.pendingRequests.set(correlationId, {
        resolve: (data) => {
          clearTimeout(timeoutId);
          resolve(data);
        },
        reject: (error) => {
          clearTimeout(timeoutId);
          reject(error);
        },
        type,
        retryCount
      });

      // Enviar mensaje
      this.sendSocketMessage(type, payload, correlationId, options.priority || 5);
    });

    try {
      return await requestPromise;
    } catch (error) {
      // Manejar retry
      if (retryCount < RABBITMQ_CONFIG.retry.maxAttempts) {
        console.log(`🔄 Reintentando solicitud ${type} (intento ${retryCount + 1})`);
        
        const delay = Math.min(
          RABBITMQ_CONFIG.retry.initialDelay * 
          Math.pow(RABBITMQ_CONFIG.retry.multiplier, retryCount),
          RABBITMQ_CONFIG.retry.maxDelay
        );
        
        await new Promise(resolve => setTimeout(resolve, delay));
        
        return this.request(type, payload, {
          ...options,
          retryCount: retryCount + 1,
          correlationId
        });
      }
      
      throw error;
    }
  }

  // Enviar mensaje vía Socket.io
  sendSocketMessage(type, payload, correlationId, priority = 5) {
    try {
      const eventName = this.getEventNameForType(type);
      
      const message = {
        correlationId,
        requestType: type,
        priority,
        payload: {
          ...payload,
          clientId: this.clientId,
          userId: this.userId || this.getCurrentUserId(),
          timestamp: Date.now()
        }
      };

      this.socket.emit(eventName, message);
      console.log(`📤 Mensaje Socket.io enviado: ${type} (ID: ${correlationId})`);
    } catch (error) {
      console.error('❌ Error enviando mensaje Socket.io:', error);
      throw error;
    }
  }

  // Obtener nombre del evento según el tipo
  getEventNameForType(type) {
    const events = RABBITMQ_CONFIG.events;
    
    switch (type) {
      case 'balance':
        return events.REQUEST_BALANCE;
      case 'transactions':
        return events.REQUEST_TRANSACTIONS;
      case 'loans':
        return events.REQUEST_LOANS;
      case 'request_loan':
        return events.REQUEST_LOAN;
      case 'profile':
        return events.UPDATE_PROFILE;
      default:
        return events.REQUEST_BALANCE;
    }
  }

  // Iniciar heartbeat
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected && this.socket) {
        this.socket.emit('ping', { timestamp: Date.now() });
      }
    }, 30000); // Cada 30 segundos
  }

  // Manejar desconexión
  handleDisconnection() {
    this.isConnected = false;
    this.connectionState = 'disconnected';
    this.scheduleReconnect();
  }

  // Reconexión automática
  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ Máximo número de intentos de reconexión alcanzado');
      return;
    }

    this.reconnectAttempts++;
    this.connectionState = 'reconnecting';
    
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), 30000);
    
    console.log(`🔄 Intentando reconectar en ${delay}ms (intento ${this.reconnectAttempts})`);
    
    setTimeout(async () => {
      try {
        await this.connect();
      } catch (error) {
        console.error('❌ Error en reconexión:', error);
      }
    }, delay);
  }

  // Suscribirse a eventos
  subscribe(eventType, callback) {
    this.eventListeners.set(eventType, callback);
    console.log(`🔔 Suscripción configurada para: ${eventType}`);
  }

  // Cancelar suscripción
  unsubscribe(eventType) {
    this.eventListeners.delete(eventType);
    console.log(`🔕 Suscripción cancelada para: ${eventType}`);
  }

  // Obtener ID del usuario actual
  getCurrentUserId() {
    // Implementar según la lógica de autenticación de la app
    return this.userId || 'current_user_id';
  }

  // Verificar estado de conexión
  getStatus() {
    return {
      connected: this.isConnected,
      connectionState: this.connectionState,
      reconnectAttempts: this.reconnectAttempts,
      pendingRequests: this.pendingRequests.size,
      clientId: this.clientId,
      userId: this.userId,
      hasAuthToken: !!this.authToken
    };
  }

  // Obtener estadísticas
  getStatistics() {
    return {
      connection: this.getStatus(),
      events: {
        listeners: this.eventListeners.size,
        pendingRequests: this.pendingRequests.size
      },
      performance: {
        uptime: process.uptime(),
        memoryUsage: process.memoryUsage()
      }
    };
  }

  // Desconectar
  async disconnect() {
    try {
      this.unsubscribe('notifications');
      this.unsubscribe('transactionUpdate');
      this.unsubscribe('loanUpdate');
      this.unsubscribe('balanceUpdate');
      
      if (this.heartbeatInterval) {
        clearInterval(this.heartbeatInterval);
      }

      if (this.socket) {
        this.socket.disconnect();
      }

      this.isConnected = false;
      this.connectionState = 'disconnected';
      console.log('🔌 Desconectado de RabbitMQ');
    } catch (error) {
      console.error('❌ Error desconectando:', error);
    }
  }
}

export default SocketIORabbitMQClient;