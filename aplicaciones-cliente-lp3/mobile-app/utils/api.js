import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Configuración base de la API
const API_BASE_URL = 'http://localhost:3000/api'; // Cambiar por la URL real del backend
const RABBITMQ_CONFIG = {
  url: 'amqp://localhost',
  exchange: 'banking-exchange',
  queue: 'mobile-app-queue'
};

// Crear instancia de axios con configuración por defecto
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para agregar token de autenticación
apiClient.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('userToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar respuestas
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      AsyncStorage.multiRemove(['userToken', 'userData']);
    }
    return Promise.reject(error);
  }
);

// Funciones de comunicación con RabbitMQ
class RabbitMQService {
  constructor() {
    this.connection = null;
    this.channel = null;
  }

  async connect() {
    try {
      // En una implementación real, esto se conectaría a RabbitMQ
      // Por ahora simulamos la conexión
      console.log('Conectando a RabbitMQ...');
      return true;
    } catch (error) {
      console.error('Error conectando a RabbitMQ:', error);
      return false;
    }
  }

  async sendMessage(messageType, data) {
    try {
      // Simular envío de mensaje a RabbitMQ
      console.log(`Enviando mensaje ${messageType}:`, data);
      
      const message = {
        type: messageType,
        data: data,
        timestamp: new Date().toISOString(),
        source: 'mobile-app'
      };

      // En una implementación real, aquí enviarías a RabbitMQ
      return { success: true, messageId: Date.now().toString() };
    } catch (error) {
      console.error('Error enviando mensaje:', error);
      throw error;
    }
  }

  async subscribeMessage(messageType, callback) {
    try {
      // Simular suscripción a mensajes de RabbitMQ
      console.log(`Suscrito a mensajes ${messageType}`);
      
      // En una implementación real, aquí te suscribirías a RabbitMQ
      // Por ahora simulamos con setTimeout
      setTimeout(() => {
        callback({
          type: messageType,
          data: { status: 'processed' },
          timestamp: new Date().toISOString()
        });
      }, 1000);
    } catch (error) {
      console.error('Error suscribiéndose a mensajes:', error);
    }
  }
}

const rabbitMQService = new RabbitMQService();

// Funciones de API
export const api = {
  // Autenticación
  login: async (email, password) => {
    const response = await apiClient.post('/auth/login', { email, password });
    return response;
  },

  // Cuentas
  getAccounts: async () => {
    try {
      await rabbitMQService.connect();
      await rabbitMQService.sendMessage('GET_ACCOUNTS', {});
      
      const response = await apiClient.get('/accounts');
      return response;
    } catch (error) {
      console.error('Error fetching accounts:', error);
      // Devolver datos simulados en caso de error
      return [
        {
          id: '1',
          type: 'Cuenta Corriente',
          number: '1234567890',
          balance: 15430.50,
          status: 'Activa'
        },
        {
          id: '2',
          type: 'Cuenta de Ahorros',
          number: '0987654321',
          balance: 10000.00,
          status: 'Activa'
        }
      ];
    }
  },

  // Transacciones
  getTransactions: async (accountId) => {
    try {
      await rabbitMQService.sendMessage('GET_TRANSACTIONS', { accountId });
      
      const response = await apiClient.get(`/transactions${accountId ? `?accountId=${accountId}` : ''}`);
      return response;
    } catch (error) {
      console.error('Error fetching transactions:', error);
      // Devolver transacciones simuladas
      return [
        {
          id: '1',
          description: 'Pago - Supermercado ABC',
          amount: 45.20,
          type: 'expense',
          date: '2025-10-30T10:30:00Z',
          category: 'Alimentación',
          status: 'Completado'
        },
        {
          id: '2',
          description: 'Transferencia Recibida',
          amount: 1200.00,
          type: 'income',
          date: '2025-10-29T15:45:00Z',
          category: 'Transferencia',
          status: 'Completado'
        }
      ];
    }
  },

  // Crear transacción
  createTransaction: async (transactionData) => {
    try {
      await rabbitMQService.sendMessage('CREATE_TRANSACTION', transactionData);
      
      const response = await apiClient.post('/transactions', transactionData);
      return response;
    } catch (error) {
      console.error('Error creating transaction:', error);
      throw error;
    }
  },

  // Historial
  getHistory: async (filterType = 'all') => {
    try {
      await rabbitMQService.sendMessage('GET_HISTORY', { filterType });
      
      const response = await apiClient.get(`/history?type=${filterType}`);
      return response;
    } catch (error) {
      console.error('Error fetching history:', error);
      // Devolver historial simulado
      return [
        {
          id: '1',
          type: 'transaction',
          title: 'Pago realizado',
          description: 'Pago - Supermercado ABC',
          date: '2025-10-30T10:30:00Z',
          amount: 45.20,
          status: 'completado',
          additionalInfo: 'ID: TXN-001'
        },
        {
          id: '2',
          type: 'qr_generated',
          title: 'QR Generado',
          description: 'Código QR para pago',
          date: '2025-10-30T09:15:00Z',
          status: 'exitoso',
          additionalInfo: 'Monto: $100.00'
        },
        {
          id: '3',
          type: 'loan',
          title: 'Solicitud de préstamo',
          description: 'Préstamo personal - $5,000',
          date: '2025-10-29T14:20:00Z',
          status: 'pendiente',
          additionalInfo: 'Plazo: 12 meses'
        }
      ];
    }
  },

  // Solicitar préstamo
  requestLoan: async (loanData) => {
    try {
      await rabbitMQService.sendMessage('REQUEST_LOAN', loanData);
      
      const response = await apiClient.post('/loans', loanData);
      return response;
    } catch (error) {
      console.error('Error requesting loan:', error);
      throw error;
    }
  },

  // Pagos QR
  processQRPayment: async (qrData) => {
    try {
      await rabbitMQService.sendMessage('PROCESS_QR_PAYMENT', qrData);
      
      const response = await apiClient.post('/payments/qr', qrData);
      return response;
    } catch (error) {
      console.error('Error processing QR payment:', error);
      throw error;
    }
  },

  // Perfil de usuario
  getUserProfile: async () => {
    try {
      await rabbitMQService.sendMessage('GET_USER_PROFILE', {});
      
      const response = await apiClient.get('/profile');
      return response;
    } catch (error) {
      console.error('Error fetching user profile:', error);
      throw error;
    }
  }
};

export const getAccounts = api.getAccounts;
export const getTransactions = api.getTransactions;
export const getHistory = api.getHistory;
export { rabbitMQService };