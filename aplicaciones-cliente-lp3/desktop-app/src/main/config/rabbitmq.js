const amqp = require('amqplib');
const { ipcMain } = require('electron');

class RabbitMQManager {
  constructor() {
    this.connection = null;
    this.channel = null;
    this.connected = false;
    this.consumers = new Map();
    this.setupIPCHandlers();
  }

  async connect(config = {}) {
    try {
      const defaultConfig = {
        hostname: process.env.RABBITMQ_HOST || 'localhost',
        port: process.env.RABBITMQ_PORT || 5672,
        username: process.env.RABBITMQ_USER || 'guest',
        password: process.env.RABBITMQ_PASSWORD || 'guest',
        ...config
      };

      this.connection = await amqp.connect(defaultConfig);
      this.channel = await this.connection.createChannel();
      this.connected = true;

      console.log('Connected to RabbitMQ');

      // Manejar desconexiones
      this.connection.on('close', () => {
        console.log('RabbitMQ connection closed');
        this.connected = false;
      });

      this.connection.on('error', (err) => {
        console.error('RabbitMQ connection error:', err);
        this.connected = false;
      });

      return { success: true, message: 'Connected to RabbitMQ' };
    } catch (error) {
      console.error('Error connecting to RabbitMQ:', error);
      return { success: false, error: error.message };
    }
  }

  async publish(exchange, routingKey, message, options = {}) {
    if (!this.connected || !this.channel) {
      throw new Error('RabbitMQ not connected');
    }

    try {
      // Declarar exchange si no existe
      await this.channel.assertExchange(exchange, 'topic', { durable: true });

      // Publicar mensaje
      const msg = Buffer.from(JSON.stringify(message));
      const published = this.channel.publish(
        exchange,
        routingKey,
        msg,
        {
          contentType: 'application/json',
          persistent: true,
          ...options
        }
      );

      return { success: published, message: 'Message published' };
    } catch (error) {
      console.error('Error publishing message:', error);
      return { success: false, error: error.message };
    }
  }

  async subscribe(queue, callback, options = {}) {
    if (!this.connected || !this.channel) {
      throw new Error('RabbitMQ not connected');
    }

    try {
      // Declarar cola
      const q = await this.channel.assertQueue(queue, {
        durable: true,
        ...options
      });

      // Configurar consumidor
      const consumerTag = await this.channel.consume(
        queue,
        async (msg) => {
          if (msg) {
            try {
              const content = JSON.parse(msg.content.toString());
              const result = await callback(content);
              
              if (result !== false) {
                this.channel.ack(msg);
              } else {
                this.channel.nack(msg, false, true);
              }
            } catch (error) {
              console.error('Error processing message:', error);
              this.channel.nack(msg, false, false);
            }
          }
        },
        { noAck: false }
      );

      this.consumers.set(queue, consumerTag.consumerTag);
      return { success: true, consumerTag: consumerTag.consumerTag };
    } catch (error) {
      console.error('Error subscribing to queue:', error);
      return { success: false, error: error.message };
    }
  }

  async unsubscribe(queue) {
    try {
      const consumerTag = this.consumers.get(queue);
      if (consumerTag) {
        await this.channel.cancel(consumerTag);
        this.consumers.delete(queue);
        return { success: true, message: 'Unsubscribed from queue' };
      }
      return { success: false, error: 'Consumer not found' };
    } catch (error) {
      console.error('Error unsubscribing:', error);
      return { success: false, error: error.message };
    }
  }

  async close() {
    try {
      // Cancelar todos los consumidores
      for (const [queue, consumerTag] of this.consumers) {
        await this.channel.cancel(consumerTag);
      }

      if (this.channel) {
        await this.channel.close();
      }
      if (this.connection) {
        await this.connection.close();
      }

      this.connected = false;
      this.consumers.clear();
      console.log('RabbitMQ connection closed');
    } catch (error) {
      console.error('Error closing RabbitMQ connection:', error);
    }
  }

  setupIPCHandlers() {
    // Connect to RabbitMQ
    ipcMain.handle('rabbitmq:connect', async (event, config) => {
      return await this.connect(config);
    });

    // Publish message
    ipcMain.handle('rabbitmq:publish', async (event, exchange, routingKey, message) => {
      return await this.publish(exchange, routingKey, message);
    });

    // Subscribe to queue
    ipcMain.handle('rabbitmq:subscribe', async (event, queue, callback) => {
      // Store callback for later use
      event.sender.on('rabbitmq:message', (event, message) => {
        callback(message);
      });

      return await this.subscribe(queue, async (message) => {
        // Forward message to renderer
        event.sender.send('rabbitmq:message', message);
        return true; // Acknowledge message
      });
    });

    // Unsubscribe from queue
    ipcMain.handle('rabbitmq:unsubscribe', async (event, queue) => {
      return await this.unsubscribe(queue);
    });

    // Close connection
    ipcMain.handle('rabbitmq:close', async () => {
      await this.close();
      return { success: true };
    });
  }

  // Métodos de utilidad para patrones comunes
  async publishTransaction(transaction) {
    return await this.publish(
      'banco.exchange',
      'transaction.created',
      {
        type: 'transaction',
        data: transaction,
        timestamp: new Date().toISOString()
      }
    );
  }

  async publishAccountUpdate(account) {
    return await this.publish(
      'banco.exchange',
      'account.updated',
      {
        type: 'account_update',
        data: account,
        timestamp: new Date().toISOString()
      }
    );
  }

  async publishNotification(userId, message, type = 'info') {
    return await this.publish(
      'banco.exchange',
      `notification.${userId}`,
      {
        type: 'notification',
        userId,
        message,
        notificationType: type,
        timestamp: new Date().toISOString()
      }
    );
  }
}

module.exports = new RabbitMQManager();
