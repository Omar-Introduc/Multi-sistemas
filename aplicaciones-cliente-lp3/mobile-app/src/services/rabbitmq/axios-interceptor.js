import React from 'react';
import axios from 'axios';
import RabbitMQClient from './client';

class RabbitMQInterceptor {
  constructor() {
    this.rabbitMQClient = new RabbitMQClient();
    this.isInitialized = false;
    this.requestInterceptors = [];
    this.responseInterceptors = [];
  }

  // Inicializar cliente RabbitMQ
  async initialize() {
    if (this.isInitialized) return;

    try {
      await this.rabbitMQClient.connect();
      this.setupAxiosInterceptors();
      this.isInitialized = true;
      console.log('✅ Interceptor RabbitMQ inicializado');
    } catch (error) {
      console.error('❌ Error inicializando interceptor RabbitMQ:', error);
      throw error;
    }
  }

  // Configurar interceptors de Axios
  setupAxiosInterceptors() {
    // Request interceptor
    const requestInterceptor = axios.interceptors.request.use(
      async (config) => {
        // Verificar si la request debe usar RabbitMQ
        if (this.shouldUseRabbitMQ(config)) {
          try {
            const response = await this.handleRequestWithRabbitMQ(config);
            return response;
          } catch (error) {
            // En caso de error con RabbitMQ, intentar fallback a HTTP
            console.warn('⚠️ RabbitMQ fallido, usando HTTP:', error.message);
            return config;
          }
        }
        return config;
      },
      (error) => {
        console.error('❌ Error en request interceptor:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    const responseInterceptor = axios.interceptors.response.use(
      (response) => {
        return response;
      },
      async (error) => {
        // En caso de error HTTP, intentar RabbitMQ si es aplicable
        if (error.config && this.shouldUseRabbitMQ(error.config)) {
          try {
            const response = await this.handleRequestWithRabbitMQ(error.config);
            return response;
          } catch (rabbitMQError) {
            console.error('❌ Error tanto en HTTP como en RabbitMQ:', rabbitMQError);
          }
        }
        return Promise.reject(error);
      }
    );

    this.requestInterceptors.push(requestInterceptor);
    this.responseInterceptors.push(responseInterceptor);
  }

  // Determinar si una request debe usar RabbitMQ
  shouldUseRabbitMQ(config) {
    const rabbitMQEndpoints = [
      '/api/balance',
      '/api/transactions',
      '/api/loans',
      '/api/profile'
    ];

    return rabbitMQEndpoints.some(endpoint => config.url?.includes(endpoint));
  }

  // Manejar request con RabbitMQ
  async handleRequestWithRabbitMQ(config) {
    const method = config.method?.toLowerCase();
    const url = config.url;
    
    let requestType, payload;
    
    // Mapear endpoints HTTP a tipos de RabbitMQ
    if (url?.includes('/balance')) {
      requestType = 'balance';
      payload = {
        operation: 'get_balance',
        clientId: config.data?.clientId || 'default',
        accountId: config.data?.accountId
      };
    } else if (url?.includes('/transactions')) {
      requestType = 'transactions';
      payload = {
        operation: 'get_transactions',
        clientId: config.data?.clientId || 'default',
        filters: config.data?.filters || {},
        pagination: config.data?.pagination
      };
    } else if (url?.includes('/loans')) {
      if (method === 'post') {
        requestType = 'request_loan';
        payload = {
          operation: 'request_loan',
          clientId: config.data?.clientId || 'default',
          loanData: config.data
        };
      } else {
        requestType = 'loans';
        payload = {
          operation: 'get_loans',
          clientId: config.data?.clientId || 'default'
        };
      }
    } else if (url?.includes('/profile')) {
      if (method === 'put') {
        requestType = 'profile';
        payload = {
          operation: 'update_profile',
          clientId: config.data?.clientId || 'default',
          profileData: config.data
        };
      }
    } else {
      throw new Error(`Endpoint no soportado para RabbitMQ: ${url}`);
    }

    // Configurar timeout según el tipo
    const timeoutConfig = {
      balance: 10000,
      transactions: 20000,
      loans: 45000,
      request_loan: 30000,
      profile: 15000
    };

    // Enviar request a RabbitMQ
    const response = await this.rabbitMQClient.request(requestType, payload, {
      timeout: timeoutConfig[requestType] || 30000,
      priority: this.getPriorityForType(requestType)
    });

    // Convertir respuesta de RabbitMQ a formato Axios
    return {
      data: response.data,
      status: 200,
      statusText: 'OK',
      headers: response.headers || {},
      config
    };
  }

  // Obtener prioridad para cada tipo de operación
  getPriorityForType(type) {
    const priorities = {
      balance: 10,
      transactions: 8,
      loans: 5,
      request_loan: 7,
      profile: 6
    };
    return priorities[type] || 5;
  }

  // Limpiar interceptors
  cleanup() {
    // Remover interceptors
    this.requestInterceptors.forEach(interceptorId => {
      axios.interceptors.request.eject(interceptorId);
    });
    
    this.responseInterceptors.forEach(interceptorId => {
      axios.interceptors.response.eject(interceptorId);
    });

    // Desconectar RabbitMQ
    if (this.rabbitMQClient) {
      this.rabbitMQClient.disconnect();
    }

    this.requestInterceptors = [];
    this.responseInterceptors = [];
    this.isInitialized = false;
    
    console.log('🧹 Interceptor RabbitMQ limpiado');
  }

  // Obtener instancia del cliente RabbitMQ
  getClient() {
    return this.rabbitMQClient;
  }

  // Verificar estado
  getStatus() {
    return {
      initialized: this.isInitialized,
      rabbitMQStatus: this.rabbitMQClient.getStatus()
    };
  }
}

// Singleton instance
let rabbitMQInterceptor = null;

// Factory function
export const createRabbitMQInterceptor = () => {
  if (!rabbitMQInterceptor) {
    rabbitMQInterceptor = new RabbitMQInterceptor();
  }
  return rabbitMQInterceptor;
};

// Hook personalizado para React Native
export const useRabbitMQInterceptor = () => {
  const [interceptor, setInterceptor] = React.useState(null);
  const [isInitialized, setIsInitialized] = React.useState(false);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    const init = async () => {
      try {
        const clientInterceptor = createRabbitMQInterceptor();
        await clientInterceptor.initialize();
        setInterceptor(clientInterceptor);
        setIsInitialized(true);
        setError(null);
      } catch (err) {
        setError(err);
        setIsInitialized(false);
      }
    };

    init();

    return () => {
      if (interceptor) {
        interceptor.cleanup();
      }
    };
  }, []);

  return {
    interceptor,
    isInitialized,
    error,
    getClient: () => interceptor?.getClient()
  };
};

export default RabbitMQInterceptor;