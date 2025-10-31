// API del sistema bancario
const API = {
  baseURL: 'http://localhost:3000/api',
  
  // Datos simulados
  mockData: {
    accounts: [
      { id: '1', type: 'Cuenta Corriente', number: '****1234', balance: 15430.50, status: 'active' },
      { id: '2', type: 'Cuenta de Ahorros', number: '****5678', balance: 10000.00, status: 'active' }
    ],
    transactions: [
      { id: 'TXN001', date: new Date(), description: 'Pago - Supermercado ABC', category: 'Alimentación', amount: -45.20, status: 'completed' },
      { id: 'TXN002', date: new Date(Date.now() - 86400000), description: 'Transferencia Recibida', category: 'Transferencia', amount: 1200.00, status: 'completed' }
    ]
  },

  // Autenticación simulada
  async login(username, password) {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    if (username === 'admin' && password === '123456') {
      return {
        token: 'mock-jwt-token',
        user: { id: '1', username: 'admin', name: 'Juan Pérez' }
      };
    }
    throw new Error('Credenciales inválidas');
  },

  // Obtener cuentas
  async getAccounts() {
    await new Promise(resolve => setTimeout(resolve, 500));
    return this.mockData.accounts;
  },

  // Obtener transacciones
  async getTransactions(filters = {}) {
    await new Promise(resolve => setTimeout(resolve, 500));
    return this.mockData.transactions;
  },

  // Crear transacción
  async createTransaction(transaction) {
    await new Promise(resolve => setTimeout(resolve, 1000));
    const newTransaction = {
      id: 'TXN' + Date.now(),
      date: new Date(),
      status: 'pending',
      ...transaction
    };
    this.mockData.transactions.unshift(newTransaction);
    return newTransaction;
  },

  // Procesar pago QR
  async processQRPayment(qrData) {
    await new Promise(resolve => setTimeout(resolve, 1500));
    return { success: true, transactionId: 'TXN' + Date.now() };
  },

  // Solicitar préstamo
  async requestLoan(loanData) {
    await new Promise(resolve => setTimeout(resolve, 2000));
    return { success: true, requestId: 'LOAN' + Date.now(), status: 'pending' };
  }
};

// Exportar para uso global
window.API = API;
