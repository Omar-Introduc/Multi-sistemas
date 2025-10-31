// Cliente RabbitMQ optimizado para React Native
// Usa WebSocket para comunicación en tiempo real

import AsyncStorage from '@react-native-async-storage/async-storage';
import { v4 as uuidv4 } from 'uuid';

class ReactNativeRabbitMQClient {
  constructor() {
    this.baseUrl = process.env.RABBITMQ_API_URL || 'http://localhost:8080/api';
    this.websocketUrl = process.env.RABBITMQ_WS_URL || 'ws://localhost:8080/ws';
    this.ws = null;
    this.isConnected = false;
    this.pendingRequests = new Map();
    this.eventListeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.clientId = `mobile_${uuidv4()}`;
    this.authToken = null;
    this.heartbeatInterval = null;
  }

  // Generar correlation ID único
  generateCorrelationId() {
    return `${this.clientId}_${Date.now()}_${uuidv4()}`;
  }

  // Conectar usando WebSocket
  async connect() {
    try {
      console.log('🔗 Conectando a RabbitMQ (React Native)...');
      
      // Obtener token de autenticación
      await this.authenticate();
      
      // Conectar WebSocket
      await this.connectWebSocket();
      
      this.isConnected = true;
      this.reconnectAttempts = 0;
      
      console.log('✅ Conexión WebSocket establecida');
      
      // Iniciar heartbeat
      this.startHeartbeat();
      
      return true;
    } catch (error) {
      console.error('❌ Error conectando a RabbitMQ:', error);
      this.scheduleReconnect();
      throw error;
    }
  }

  // Autenticación con el servicio de bridge
  async authenticate() {
    try {
      const credentials = {
        username: 'cliente_user',
        password: 'cliente_secure_2024',
        clientId: this.clientId,
        platform: 'react-native'
      };

      const response = await fetch(`${this.baseUrl}/auth/login`, {
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
      
      // Almacenar token localmente
      await AsyncStorage.setItem('rabbitmq_token', this.authToken);
      await AsyncStorage.setItem('rabbitmq_client_id', this.clientId);
      
      console.log('✅ Autenticación exitosa');
    } catch (error) {
      console.error('❌ Error en autenticación:', error);
      
      // Intentar obtener token guardado
      const savedToken = await AsyncStorage.getItem('rabbitmq_token');
      if (savedToken) {
        this.authToken = savedToken;
        console.log('🔑 Usando token guardado');
      } else {
        throw error;
      }
    }
  }

  // Conectar WebSocket
  connectWebSocket() {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `${this.websocketUrl}?token=${this.authToken}&clientId=${this.clientId}`;
        
        // Para React Native, usar WebSocket polyfill
        const WebSocket = global.WebSocket || require('react-native-websocket');
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
          console.log('🔌 WebSocket abierto');
          this.isConnected = true;
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          this.handleWebSocketMessage(event.data);
        };
        
        this.ws.onerror = (error) => {
          console.error('❌ Error WebSocket:', error);
          this.isConnected = false;
          reject(error);
        };
        
        this.ws.onclose = (event) => {
          console.log('🔌 WebSocket cerrado:', event.code, event.reason);
          this.isConnected = false;
          this.handleDisconnection();
        };
        
        // Timeout de conexión
        setTimeout(() => {
          if (!this.isConnected) {
            reject(new Error('Connection timeout'));
          }
        }, 10000);
        
      } catch (error) {
        reject(error);
      }
    });
  }

  // Manejar mensajes WebSocket
  handleWebSocketMessage(data) {
    try {
      const message = JSON.parse(data);
      
      if (message.type === 'response' && message.correlationId) {
        this.handleResponseMessage(message);
      } else if (message.type === 'notification') {
        this.handleNotificationMessage(message);
      } else if (message.type === 'ping') {
        this.sendPong();
      }
    } catch (error) {
      console.error('❌ Error procesando mensaje WebSocket:', error);
    }
  }

  // Manejar mensaje de respuesta
  handleResponseMessage(message) {
    const correlationId = message.correlationId;
    
    if (correlationId && this.pendingRequests.has(correlationId)) {
      const requestInfo = this.pendingRequests.get(correlationId);
      
      if (message.success) {
        requestInfo.resolve({
          data: message.data,
          correlationId,
          responseType: message.responseType,
          timestamp: Date.now()
        });
      } else {
        requestInfo.reject(new Error(message.error || 'Error en el servidor'));
      }
      
      this.pendingRequests.delete(correlationId);
    }
  }

  // Manejar notificaciones
  handleNotificationMessage(message) {
    const callback = this.eventListeners.get('notifications');
    if (callback) {
      callback(message.data);
    }
  }

  // Enviar solicitud vía WebSocket
  async request(type, payload, options = {}) {
    if (!this.isConnected) {
      throw new Error('No hay conexión activa con RabbitMQ');
    }

    const correlationId = options.correlationId || this.generateCorrelationId();
    const timeout = options.timeout || 30000;
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
      this.sendWebSocketMessage(type, payload, correlationId, options.priority || 5);
    });

    try {
      return await requestPromise;
    } catch (error) {
      // Manejar retry
      if (retryCount < 3) {
        console.log(`🔄 Reintentando solicitud ${type} (intento ${retryCount + 1})`);
        
        const delay = Math.min(1000 * Math.pow(2, retryCount), 10000);
        
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

  // Enviar mensaje vía WebSocket
  sendWebSocketMessage(type, payload, correlationId, priority = 5) {
    try {
      const message = {
        type: 'request',
        correlationId,
        requestType: type,
        priority,
        payload: {
          ...payload,
          clientId: this.clientId,
          userId: this.getCurrentUserId(),
          timestamp: Date.now()
        }
      };

      this.ws.send(JSON.stringify(message));
      console.log(`📤 Mensaje WebSocket enviado: ${type} (ID: ${correlationId})`);
    } catch (error) {
      console.error('❌ Error enviando mensaje WebSocket:', error);
      throw error;
    }
  }

  // Iniciar heartbeat
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected && this.ws) {
        this.ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
      }
    }, 30000); // Cada 30 segundos
  }

  // Responder a ping
  sendPong() {
    if (this.ws && this.isConnected) {
      this.ws.send(JSON.stringify({ type: 'pong', timestamp: Date.now() }));
    }
  }

  // Manejar desconexión
  handleDisconnection() {
    this.isConnected = false;
    this.scheduleReconnect();
  }

  // Reconexión automática
  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ Máximo número de intentos de reconexión alcanzado');
      return;
    }

    this.reconnectAttempts++;
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

  // Suscribirse a notificaciones
  async subscribeNotifications(callback) {
    this.eventListeners.set('notifications', callback);
    console.log('🔔 Suscripción a notificaciones configurada');
  }

  // Cancelar suscripción
  unsubscribeNotifications() {
    this.eventListeners.delete('notifications');
    console.log('🔕 Suscripción cancelada');
  }

  // Obtener ID del usuario actual
  getCurrentUserId() {
    // Implementar según la lógica de autenticación de la app
    return 'current_user_id';
  }

  // Verificar estado de conexión
  getStatus() {
    return {
      connected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      pendingRequests: this.pendingRequests.size,
      clientId: this.clientId,
      hasAuthToken: !!this.authToken
    };
  }

  // Desconectar
  async disconnect() {
    try {
      this.unsubscribeNotifications();
      
      if (this.heartbeatInterval) {
        clearInterval(this.heartbeatInterval);
      }

      if (this.ws) {
        this.ws.close();
      }

      this.isConnected = false;
      console.log('🔌 Desconectado de RabbitMQ');
    } catch (error) {
      console.error('❌ Error desconectando:', error);
    }
  }
}

export default ReactNativeRabbitMQClient;