import ApiService from './apiService';

export class TransactionService {
  static async getTransactions(accountId, filters = {}) {
    try {
      return await ApiService.getTransactions(accountId, filters);
    } catch (error) {
      console.warn('Could not fetch transactions:', error);
      return this.getMockTransactions();
    }
  }

  static async createTransaction(transactionData) {
    try {
      this.validateTransactionData(transactionData);
      const response = await ApiService.createTransaction(transactionData);
      
      return {
        success: true,
        data: response,
        message: 'Transacción creada exitosamente'
      };
    } catch (error) {
      console.error('Transaction creation error:', error);
      return {
        success: false,
        error: error.message || 'Error al crear transacción'
      };
    }
  }

  static async getTransactionStats(accountId, period = '30d') {
    try {
      const transactions = await this.getTransactions(accountId);
      return this.calculateStats(transactions, period);
    } catch (error) {
      console.warn('Could not fetch transaction stats:', error);
      return this.getMockStats();
    }
  }

  static calculateStats(transactions, period = '30d') {
    const now = new Date();
    let startDate;
    
    switch (period) {
      case '7d':
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case '30d':
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      case '90d':
        startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
        break;
      case '1y':
        startDate = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
        break;
      default:
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    }

    const filteredTransactions = transactions.filter(t => 
      new Date(t.date) >= startDate
    );

    const income = filteredTransactions
      .filter(t => t.amount > 0)
      .reduce((sum, t) => sum + t.amount, 0);

    const expenses = filteredTransactions
      .filter(t => t.amount < 0)
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);

    const net = income - expenses;
    const transactionCount = filteredTransactions.length;

    // Group by category
    const categoryBreakdown = {};
    filteredTransactions.forEach(t => {
      if (!categoryBreakdown[t.category]) {
        categoryBreakdown[t.category] = { income: 0, expenses: 0 };
      }
      if (t.amount > 0) {
        categoryBreakdown[t.category].income += t.amount;
      } else {
        categoryBreakdown[t.category].expenses += Math.abs(t.amount);
      }
    });

    // Group by month for trend analysis
    const monthlyTrend = {};
    filteredTransactions.forEach(t => {
      const month = new Date(t.date).toISOString().slice(0, 7); // YYYY-MM
      if (!monthlyTrend[month]) {
        monthlyTrend[month] = { income: 0, expenses: 0 };
      }
      if (t.amount > 0) {
        monthlyTrend[month].income += t.amount;
      } else {
        monthlyTrend[month].expenses += Math.abs(t.amount);
      }
    });

    return {
      period,
      startDate: startDate.toISOString(),
      endDate: now.toISOString(),
      income,
      expenses,
      net,
      transactionCount,
      averageTransaction: transactionCount > 0 ? Math.abs(net) / transactionCount : 0,
      categoryBreakdown,
      monthlyTrend,
      dailyAverage: filteredTransactions.length > 0 ? transactionCount / ((now - startDate) / (1000 * 60 * 60 * 24)) : 0
    };
  }

  static validateTransactionData(data) {
    const { type, amount, description, accountId, recipient } = data;

    if (!type || !['transfer', 'payment', 'deposit', 'withdrawal'].includes(type)) {
      throw new Error('Tipo de transacción inválido');
    }

    if (!amount || amount <= 0) {
      throw new Error('El monto debe ser mayor a 0');
    }

    if (amount > 1000000) {
      throw new Error('El monto excede el límite máximo de $1,000,000');
    }

    if (!description || description.trim().length === 0) {
      throw new Error('La descripción es requerida');
    }

    if (!accountId) {
      throw new Error('ID de cuenta requerido');
    }

    // Additional validations for specific types
    if (type === 'transfer' && !recipient?.account) {
      throw new Error('Cuenta de destino requerida para transferencias');
    }

    return true;
  }

  static getMockTransactions() {
    return [
      {
        id: '1',
        date: '2025-10-29T14:30:00Z',
        description: 'Pago - Supermercado ABC',
        amount: -45.20,
        type: 'debit',
        balance: 25430.50,
        category: 'Alimentación',
        status: 'completado',
        reference: 'TXN001234',
        merchant: 'Supermercado ABC',
        paymentMethod: 'Tarjeta de Débito'
      },
      {
        id: '2',
        date: '2025-10-28T09:15:00Z',
        description: 'Transferencia Recibida',
        amount: 1200.00,
        type: 'credit',
        balance: 25475.70,
        category: 'Transferencias',
        status: 'completado',
        reference: 'TXN001233',
        sender: 'Juan Pérez',
        senderAccount: '****1234'
      },
      {
        id: '3',
        date: '2025-10-27T16:45:00Z',
        description: 'Depósito en efectivo',
        amount: 500.00,
        type: 'credit',
        balance: 24275.70,
        category: 'Depósitos',
        status: 'completado',
        reference: 'TXN001232',
        branch: 'Sucursal Centro'
      },
      {
        id: '4',
        date: '2025-10-26T08:20:00Z',
        description: 'Pago luz - Empresa Eléctrica',
        amount: -125.80,
        type: 'debit',
        balance: 23775.70,
        category: 'Servicios',
        status: 'completado',
        reference: 'TXN001231',
        serviceProvider: 'Empresa Eléctrica Nacional',
        billNumber: 'ELE-2025-10-001'
      },
      {
        id: '5',
        date: '2025-10-25T13:10:00Z',
        description: 'Transferencia enviada',
        amount: -200.00,
        type: 'debit',
        balance: 23901.50,
        category: 'Transferencias',
        status: 'completado',
        reference: 'TXN001230',
        recipient: 'María González',
        recipientAccount: '****5678'
      },
      {
        id: '6',
        date: '2025-10-24T11:00:00Z',
        description: 'Pago - Gasolinera Shell',
        amount: -75.50,
        type: 'debit',
        balance: 24101.50,
        category: 'Transporte',
        status: 'completado',
        reference: 'TXN001229',
        merchant: 'Gasolinera Shell',
        liters: 25.5,
        pricePerLiter: 2.96
      },
      {
        id: '7',
        date: '2025-10-23T19:30:00Z',
        description: 'Retiro en cajero',
        amount: -100.00,
        type: 'debit',
        balance: 24177.00,
        category: 'Retiros',
        status: 'completado',
        reference: 'TXN001228',
        atm: 'Cajero automático - Centro Comercial'
      },
      {
        id: '8',
        date: '2025-10-22T12:15:00Z',
        description: 'Pago internet - Proveedor ABC',
        amount: -45.99,
        type: 'debit',
        balance: 24277.00,
        category: 'Servicios',
        status: 'completado',
        reference: 'TXN001227',
        serviceProvider: 'Proveedor ABC',
        plan: 'Internet 100 Mbps'
      }
    ];
  }

  static getMockStats() {
    return {
      period: '30d',
      income: 1700.00,
      expenses: -692.49,
      net: 1007.51,
      transactionCount: 8,
      averageTransaction: 125.94,
      categoryBreakdown: {
        'Alimentación': { income: 0, expenses: 45.20 },
        'Transferencias': { income: 1200.00, expenses: 200.00 },
        'Depósitos': { income: 500.00, expenses: 0 },
        'Servicios': { income: 0, expenses: 171.79 },
        'Transporte': { income: 0, expenses: 75.50 },
        'Retiros': { income: 0, expenses: 100.00 }
      },
      monthlyTrend: {
        '2025-10': { income: 1700.00, expenses: 692.49 }
      },
      dailyAverage: 0.27
    };
  }

  static formatAmount(amount, currency = 'USD') {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  }

  static formatDate(dateString, format = 'short') {
    const date = new Date(dateString);
    
    switch (format) {
      case 'short':
        return date.toLocaleDateString('es-ES', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric'
        });
      case 'long':
        return date.toLocaleDateString('es-ES', {
          weekday: 'long',
          day: 'numeric',
          month: 'long',
          year: 'numeric'
        });
      case 'time':
        return date.toLocaleTimeString('es-ES', {
          hour: '2-digit',
          minute: '2-digit'
        });
      case 'datetime':
        return date.toLocaleString('es-ES', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      default:
        return date.toISOString().split('T')[0];
    }
  }

  static getTransactionIcon(type) {
    switch (type) {
      case 'credit':
      case 'income':
      case 'deposit':
        return '💰';
      case 'debit':
      case 'expense':
      case 'withdrawal':
        return '💳';
      case 'transfer':
        return '🔄';
      case 'payment':
        return '💳';
      default:
        return '💼';
    }
  }

  static getCategoryIcon(category) {
    switch (category?.toLowerCase()) {
      case 'alimentación':
      case 'comida':
        return '🍽️';
      case 'transporte':
        return '🚗';
      case 'servicios':
        return '⚡';
      case 'entretenimiento':
        return '🎬';
      case 'salud':
        return '🏥';
      case 'educación':
        return '📚';
      case 'ropa':
        return '👕';
      case 'viajes':
        return '✈️';
      case 'transferencias':
        return '🔄';
      case 'depósitos':
        return '🏦';
      case 'retiros':
        return '💵';
      default:
        return '💼';
    }
  }

  static generateTransactionId() {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substr(2, 9);
    return `TXN_${timestamp}_${random}`.toUpperCase();
  }

  static isRecentTransaction(dateString, hours = 24) {
    const transactionDate = new Date(dateString);
    const now = new Date();
    const diffHours = (now - transactionDate) / (1000 * 60 * 60);
    
    return diffHours <= hours;
  }

  static categorizeTransaction(description, merchant) {
    const text = (description + ' ' + (merchant || '')).toLowerCase();
    
    if (text.includes('supermercado') || text.includes('comida') || text.includes('restaurant')) {
      return 'Alimentación';
    }
    if (text.includes('gasolinera') || text.includes('taxi') || text.includes('transporte')) {
      return 'Transporte';
    }
    if (text.includes('luz') || text.includes('agua') || text.includes('internet') || text.includes('teléfono')) {
      return 'Servicios';
    }
    if (text.includes('farmacia') || text.includes('hospital') || text.includes('médico')) {
      return 'Salud';
    }
    if (text.includes('transferencia') || text.includes('envío')) {
      return 'Transferencias';
    }
    if (text.includes('depósito') || text.includes('cash')) {
      return 'Depósitos';
    }
    if (text.includes('retiro') || text.includes('cajero')) {
      return 'Retiros';
    }
    
    return 'Otros';
  }
}

export default TransactionService;