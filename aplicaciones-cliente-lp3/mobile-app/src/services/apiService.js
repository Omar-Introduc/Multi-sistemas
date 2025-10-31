import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://localhost:8080/api';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });

    // Request interceptor
    this.client.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem('userToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        config.headers['Content-Type'] = 'application/json';
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response.data,
      async (error) => {
        if (error.response?.status === 401) {
          await AsyncStorage.multiRemove(['userToken', 'userData']);
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(credentials) {
    try {
      const response = await this.client.post('/auth/login', credentials);
      if (response.token) {
        await AsyncStorage.setItem('userToken', response.token);
        await AsyncStorage.setItem('userData', JSON.stringify(response.user));
      }
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async logout() {
    await AsyncStorage.multiRemove(['userToken', 'userData']);
  }

  // Accounts
  async getAccounts() {
    try {
      const response = await this.client.get('/cuentas');
      return response.data || [];
    } catch (error) {
      // Fallback to mock data for demo
      return this.getMockAccounts();
    }
  }

  async getAccountBalance(accountId) {
    try {
      const response = await this.client.get(`/cuentas/${accountId}/saldo`);
      return response.data;
    } catch (error) {
      // Fallback to mock data
      const accounts = await this.getMockAccounts();
      const account = accounts.find(acc => acc.id === accountId);
      return account ? { balance: account.balance } : { balance: 0 };
    }
  }

  // Transactions
  async getTransactions(accountId, filters = {}) {
    try {
      const params = new URLSearchParams(filters);
      const response = await this.client.get(`/cuentas/${accountId}/transacciones?${params}`);
      return response.data || [];
    } catch (error) {
      return this.getMockTransactions();
    }
  }

  async createTransaction(transactionData) {
    try {
      const response = await this.client.post('/transacciones', transactionData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // QR Code functionality
  async generateQRCode(data) {
    try {
      const response = await this.client.post('/qr/generar', data);
      return response.data;
    } catch (error) {
      // Generate QR client-side for demo
      return this.generateMockQR(data);
    }
  }

  async processQRCode(qrData) {
    try {
      const response = await this.client.post('/qr/procesar', { qrData });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Loans
  async getLoans() {
    try {
      const response = await this.client.get('/prestamos');
      return response.data || [];
    } catch (error) {
      return this.getMockLoans();
    }
  }

  async requestLoan(loanData) {
    try {
      const response = await this.client.post('/prestamos/solicitar', loanData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getLoanDetails(loanId) {
    try {
      const response = await this.client.get(`/prestamos/${loanId}`);
      return response.data;
    } catch (error) {
      return this.getMockLoanDetails(loanId);
    }
  }

  // Profile
  async getProfile() {
    try {
      const response = await this.client.get('/perfil');
      return response.data;
    } catch (error) {
      const userDataStr = await AsyncStorage.getItem('userData');
      return userDataStr ? JSON.parse(userDataStr) : null;
    }
  }

  async updateProfile(profileData) {
    try {
      const response = await this.client.put('/perfil', profileData);
      await AsyncStorage.setItem('userData', JSON.stringify(response.data));
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Error handling
  handleError(error) {
    if (error.response) {
      // Server responded with error status
      return {
        message: error.response.data?.message || 'Error del servidor',
        status: error.response.status,
        data: error.response.data
      };
    } else if (error.request) {
      // Network error
      return {
        message: 'Error de conexión. Verifica tu conexión a internet.',
        status: 0,
        data: null
      };
    } else {
      // Other error
      return {
        message: error.message || 'Error desconocido',
        status: 0,
        data: null
      };
    }
  }

  // Mock data for demo purposes
  getMockAccounts() {
    return [
      {
        id: '1',
        type: 'Cuenta de Ahorros',
        number: '1234567890',
        balance: 25430.50,
        status: 'Activa',
        currency: 'USD',
        createdAt: '2023-01-15'
      },
      {
        id: '2',
        type: 'Cuenta Corriente',
        number: '9876543210',
        balance: 15750.25,
        status: 'Activa',
        currency: 'USD',
        createdAt: '2023-03-20'
      }
    ];
  }

  getMockTransactions() {
    return [
      {
        id: '1',
        date: '2025-10-29',
        description: 'Pago - Supermercado ABC',
        amount: -45.20,
        type: 'debit',
        balance: 25430.50,
        category: 'Alimentación',
        reference: 'TXN001'
      },
      {
        id: '2',
        date: '2025-10-28',
        description: 'Transferencia Recibida',
        amount: 1200.00,
        type: 'credit',
        balance: 25475.70,
        category: 'Transferencias',
        reference: 'TXN002'
      },
      {
        id: '3',
        date: '2025-10-27',
        description: 'Depósito en efectivo',
        amount: 500.00,
        type: 'credit',
        balance: 24275.70,
        category: 'Depósitos',
        reference: 'TXN003'
      },
      {
        id: '4',
        date: '2025-10-26',
        description: 'Pago luz - Empresa Eléctrica',
        amount: -125.80,
        type: 'debit',
        balance: 23775.70,
        category: 'Servicios',
        reference: 'TXN004'
      },
      {
        id: '5',
        date: '2025-10-25',
        description: 'Transferencia enviada',
        amount: -200.00,
        type: 'debit',
        balance: 23901.50,
        category: 'Transferencias',
        reference: 'TXN005'
      }
    ];
  }

  getMockLoans() {
    return [
      {
        id: '1',
        type: 'Préstamo Personal',
        amount: 15000.00,
        interestRate: 12.5,
        term: 24,
        monthlyPayment: 712.50,
        status: 'activo',
        startDate: '2024-01-15',
        nextPayment: '2025-11-15',
        remainingAmount: 8970.50
      },
      {
        id: '2',
        type: 'Préstamo Hipotecario',
        amount: 120000.00,
        interestRate: 8.5,
        term: 240,
        monthlyPayment: 1037.25,
        status: 'activo',
        startDate: '2023-06-01',
        nextPayment: '2025-11-01',
        remainingAmount: 114250.75
      }
    ];
  }

  getMockLoanDetails(loanId) {
    const loans = this.getMockLoans();
    const loan = loans.find(l => l.id === loanId);
    if (loan) {
      return {
        ...loan,
        payments: [
          { date: '2025-10-15', amount: 712.50, status: 'pagado' },
          { date: '2025-09-15', amount: 712.50, status: 'pagado' },
          { date: '2025-08-15', amount: 712.50, status: 'pagado' },
          { date: '2025-11-15', amount: 712.50, status: 'pendiente' }
        ]
      };
    }
    return null;
  }

  generateMockQR(data) {
    // Generate a simple mock QR code data URL
    const qrData = JSON.stringify({
      ...data,
      timestamp: Date.now(),
      mock: true
    });
    return {
      qrCode: `data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==`,
      data: qrData
    };
  }
}

export default new ApiService();