import amqp from 'amqplib';
import { v4 as uuidv4 } from 'uuid';
import { RABBITMQ_CONFIG, OPERATION_PRIORITIES, DEAD_LETTER_CONFIG } from './config';

class RabbitMQClient {
  constructor() {
    this.connection = null;
    this.channel = null;
    this.isConnected = false;
    this.pendingRequests = new Map();
    this.eventListeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.clientId = `mobile_${uuidv4()}`;
    this.heartbeatInterval = null;
  }

  // Generar correlation ID único
  generateCorrelationId() {
    return `${this.clientId}_${Date.now()}_${uuidv4()}`;
  }

  // Conectar a RabbitMQ
  async connect() {
    try {
      console.log('🔗 Conectando a RabbitMQ...');
      
      const connectionOptions = {
        ...RABBITMQ_CONFIG.connection.options,
        username: RABBITMQ_CONFIG.connection.credentials.username,
        password: RABBITMQ_CONFIG.connection.credentials.password
      };

      this.connection = await amqp.connect(RABBITMQ_CONFIG.connection.url, connectionOptions);
      
      // Configurar manejo de cierre de conexión
      this.connection.on('close', () => {
        console.log('❌ Conexión cerrada');
        this.isConnected = false;
        this.scheduleReconnect();
      });

      this.connection.on('error', (error) => {
        console.error('❌ Error de conexión:', error);
        this.isConnected = false;
        this.scheduleReconnect();
      });

      // Crear canal
      this.channel = await this.connection.createChannel();
      
      // Configurar prefetch para control de calidad de servicio
      await this.channel.prefetch(10);
      
      this.isConnected = true;
      this.reconnectAttempts = 0;
      
      console.log('✅ Conexión establecida con RabbitMQ');
      
      // Iniciar consumo de mensajes de respuesta
      await this.setupResponseConsumer();
      
      return true;
    } catch (error) {
      console.error('❌ Error conectando a RabbitMQ:', error);
      this.scheduleReconnect();
      throw error;
    }
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

  // Configurar consumidor de respuestas
  async setupResponseConsumer() {
    try {
      // Declarar cola temporal para respuestas
      const queueName = `${RABBITMQ_CONFIG.queues.requests}.${this.clientId}.responses`;
      
      await this.channel.assertQueue(queueName, {
        durable: false,
        autoDelete: true,
        exclusive: true
      });

      // Consumir respuestas
      await this.channel.consume(queueName, (message) => {
        if (message) {
          this.handleResponseMessage(message, queueName);
        }
      }, { noAck: true });

      this.responseQueue = queueName;
      console.log('📥 Consumidor de respuestas configurado');
    } catch (error) {
      console.error('❌ Error configurando consumidor de respuestas:', error);
      throw error;
    }
  }

  // Manejar mensaje de respuesta
  handleResponseMessage(message, queueName) {
    try {
      const correlationId = message.properties.correlationId;
      const responseType = message.properties.headers?.responseType;
      
      if (correlationId && this.pendingRequests.has(correlationId)) {
        const requestInfo = this.pendingRequests.get(correlationId);
        
        // Parse del mensaje
        const content = JSON.parse(message.content.toString());
        
        // Resolver promesa
        if (message.properties.headers?.error) {
          requestInfo.reject(new Error(content.error || 'Error en el servidor'));
        } else {
          requestInfo.resolve({
            data: content,
            correlationId,
            responseType,
            timestamp: Date.now()
          });
        }
        
        // Limpiar de pending requests
        this.pendingRequests.delete(correlationId);
      }
    } catch (error) {
      console.error('❌ Error procesando respuesta:', error);
    }
  }

  // Enviar solicitud con retry automático
  async request(type, payload, options = {}) {
    if (!this.isConnected) {
      throw new Error('No hay conexión activa con RabbitMQ');
    }

    const correlationId = options.correlationId || this.generateCorrelationId();
    const timeout = options.timeout || RABBITMQ_CONFIG.timeouts.default;
    const priority = options.priority || OPERATION_PRIORITIES[type] || 5;
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
      this.sendMessage(type, payload, correlationId, priority);
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
          correlationId // Usar mismo correlation ID
        });
      }
      
      throw error;
    }
  }

  // Enviar mensaje específico
  sendMessage(type, payload, correlationId, priority = 5) {
    try {
      const routingKey = this.getRoutingKey(type);
      const exchange = RABBITMQ_CONFIG.exchanges.requests;
      
      const headers = {
        ...RABBITMQ_CONFIG.correlation,
        clientId: this.clientId,
        userId: this.getCurrentUserId(),
        requestType: type,
        timestamp: Date.now()
      };

      const messageOptions = {
        contentType: 'application/json',
        correlationId,
        replyTo: this.responseQueue,
        priority,
        headers,
        expiration: RABBITMQ_CONFIG.timeouts[type] || RABBITMQ_CONFIG.timeouts.default
      };

      const message = JSON.stringify({
        payload,
        headers,
        correlationId,
        timestamp: Date.now()
      });

      this.channel.publish(exchange, routingKey, Buffer.from(message), messageOptions);
      
      console.log(`📤 Mensaje enviado: ${type} (ID: ${correlationId})`);
    } catch (error) {
      console.error('❌ Error enviando mensaje:', error);
      throw error;
    }
  }

  // Obtener routing key según el tipo de solicitud
  getRoutingKey(type) {
    const routingKeys = RABBITMQ_CONFIG.routingKeys;
    
    switch (type) {
      case 'balance':
        return routingKeys.GET_BALANCE;
      case 'transactions':
        return routingKeys.GET_TRANSACTIONS;
      case 'loans':
        return routingKeys.GET_LOANS;
      case 'request_loan':
        return routingKeys.REQUEST_LOAN;
      case 'profile':
        return routingKeys.UPDATE_PROFILE;
      default:
        return `${routingKeys.GET_BALANCE}.${type}`;
    }
  }

  // Obtener ID del usuario actual
  getCurrentUserId() {
    // Implementar según la lógica de autenticación de la app
    return 'current_user_id';
  }

  // Suscribirse a notificaciones
  async subscribeNotifications(callback) {
    if (!this.isConnected) {
      throw new Error('No hay conexión activa con RabbitMQ');
    }

    try {
      const queueName = `${RABBITMQ_CONFIG.queues.notifications}.${this.clientId}`;
      
      await this.channel.assertQueue(queueName, {
        durable: false,
        autoDelete: true,
        exclusive: false
      });

      await this.channel.consume(queueName, (message) => {
        if (message) {
          try {
            const content = JSON.parse(message.content.toString());
            callback(content);
            this.channel.ack(message);
          } catch (error) {
            console.error('❌ Error procesando notificación:', error);
            this.channel.nack(message, false, false);
          }
        }
      });

      this.eventListeners.set('notifications', callback);
      console.log('🔔 Suscripción a notificaciones configurada');
    } catch (error) {
      console.error('❌ Error configurando suscripción:', error);
      throw error;
    }
  }

  // Cancelar suscripción
  unsubscribeNotifications() {
    const callback = this.eventListeners.get('notifications');
    if (callback) {
      this.eventListeners.delete('notifications');
      console.log('🔕 Suscripción cancelada');
    }
  }

  // Verificar estado de conexión
  getStatus() {
    return {
      connected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      pendingRequests: this.pendingRequests.size,
      clientId: this.clientId
    };
  }

  // Desconectar
  async disconnect() {
    try {
      this.unsubscribeNotifications();
      
      if (this.heartbeatInterval) {
        clearInterval(this.heartbeatInterval);
      }

      if (this.channel) {
        await this.channel.close();
      }
      
      if (this.connection) {
        await this.connection.close();
      }

      this.isConnected = false;
      console.log('🔌 Desconectado de RabbitMQ');
    } catch (error) {
      console.error('❌ Error desconectando:', error);
    }
  }
}

export default RabbitMQClient;