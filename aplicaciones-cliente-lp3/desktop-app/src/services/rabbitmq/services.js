import SocketIORabbitMQClient from './socketio-client';

class DesktopClientServices {
  constructor(socketIOClient) {
    this.client = socketIOClient;
    this.notificationQueue = [];
    this.isProcessingQueue = false;
  }

  // === SERVICIOS DE CUENTAS Y SALDOS ===
  
  /**
   * Obtener saldo de cuenta
   * @param {Object} params - Parámetros de la consulta
   * @param {string} params.accountId - ID de la cuenta
   * @param {string} params.clientId - ID del cliente
   * @returns {Promise<Object>} Datos del saldo
   */
  async getBalance(params = {}) {
    const payload = {
      accountId: params.accountId,
      clientId: params.clientId || 'default',
      operation: 'get_balance',
      includeHistory: params.includeHistory || false,
      currency: params.currency || 'PEN',
      timestamp: Date.now()
    };

    try {
      const response = await this.client.request('balance', payload, {
        timeout: 10000,
        priority: 10
      });

      return {
        success: true,
        data: response.data,
        timestamp: response.timestamp,
        correlationId: response.correlationId
      };
    } catch (error) {
      console.error('❌ Error obteniendo saldo:', error);
      return {
        success: false,
        error: error.message,
        timestamp: Date.now()
      };
    }
  }

  /**
   * Obtener historial de transacciones con filtros avanzados
   * @param {Object} params - Parámetros de filtrado
   * @param {string} params.accountId - ID de la cuenta
   * @param {Date} params.startDate - Fecha inicio
   * @param {Date} params.endDate - Fecha fin
   * @param {string} params.type - Tipo de transacción
   * @param {number} params.amount - Monto
   * @param {string} params.description - Descripción
   * @param {number} params.page - Página
   * @param {number} params.limit - Límite de resultados
   * @param {string} params.sortBy - Campo de ordenamiento
   * @param {string} params.sortOrder - Orden (asc/desc)
   * @returns {Promise<Object>} Historial de transacciones
   */
  async getTransactions(params = {}) {
    const payload = {
      accountId: params.accountId,
      clientId: params.clientId || 'default',
      operation: 'get_transactions',
      filters: {
        startDate: params.startDate?.toISOString(),
        endDate: params.endDate?.toISOString(),
        type: params.type,
        amount: params.amount,
        description: params.description,
        category: params.category,
        merchant: params.merchant
      },
      pagination: {
        page: params.page || 1,
        limit: Math.min(params.limit || 50, 100), // Máximo 100 por página
        sortBy: params.sortBy || 'timestamp',
        sortOrder: params.sortOrder || 'desc'
      },
      includeDetails: params.includeDetails || false,
      includeCategory: params.includeCategory || true,
      timestamp: Date.now()
    };

    try {
      const response = await this.client.request('transactions', payload, {
        timeout: 20000,
        priority: 8
      });

      return {
        success: true,
        data: response.data,
        pagination: response.data.pagination,
        filters: response.data.filters,
        summary: response.data.summary,
        timestamp: response.timestamp,
        correlationId: response.correlationId
      };
    } catch (error) {
      console.error('❌ Error obteniendo transacciones:', error);
      return {
        success: false,
        error: error.message,
        timestamp: Date.now()
      };
    }
  }

  /**
   * Obtener resumen de transacciones
   * @param {Object} params - Parámetros de consulta
   * @param {string} params.accountId - ID de la cuenta
   * @param {Date} params.startDate - Fecha inicio
   * @param {Date} params.endDate - Fecha fin
   * @returns {Promise<Object>} Resumen de transacciones
   */
  async getTransactionSummary(params = {}) {
    const payload = {
      accountId: params.accountId,
      clientId: params.clientId || 'default',
      operation: 'get_transaction_summary',
      period: {
        startDate: params.startDate?.toISOString(),
        endDate: params.endDate?.toISOString()
      },
      groupBy: params.groupBy || 'day', // day, week, month, category
      includeCategories: params.includeCategories || true,
      timestamp: Date.now()
    };

    try {
      const response = await this.client.request('transactions', payload, {
        timeout: 15000,
        priority: 7
      });

      return {
        success: true,
        data: response.data,
        period: response.data.period,
        totals: response.data.totals,
        breakdown: response.data.breakdown,
        timestamp: response.timestamp,
        correlationId: response.correlationId
      };
    } catch (error) {
      console.error('❌ Error obteniendo resumen de transacciones:', error);
      return {
        success: false,
        error: error.message,
        timestamp: Date.now()
      };
    }
  }

  // === SERVICIOS DE PRÉSTAMOS ===

  /**
   * Obtener préstamos del cliente con información detallada
   * @param {Object} params - Parámetros de consulta
   * @param {string} params.clientId - ID del cliente
   * @param {string} params.status - Estado del préstamo
   * @param {string} params.type - Tipo de préstamo
   * @param {boolean} params.includePayments - Incluir información de pagos
   * @returns {Promise<Object>} Lista de préstamos
   */
  async getLoans(params = {}) {
    const payload = {
      clientId: params.clientId || 'default',
      operation: 'get_loans',
      filters: {
        status: params.status,
        type: params.type,
        amount: params.amount,
        startDate: params.startDate?.toISOString(),
        endDate: params.endDate?.toISOString()
      },
      include: {
        payments: params.includePayments || false,
        guarantors: params.includeGuarantors || false,
        documents: params.includeDocuments || false,
        history: params.includeHistory || false
      },
      pagination: {
        page: params.page || 1,
        limit: Math.min(params.limit || 20, 50)
      },
      timestamp: Date.now()
    };

    try {
      const response = await this.client.request('loans', payload, {
        timeout: 45000,
        priority: 5
      });

      return {
        success: true,
        data: response.data,
        summary: response.data.summary,
        totals: response.data.totals,
        timestamp: response.timestamp,
        correlationId: response.correlationId
      };
    } catch (error) {
      console.error('❌ Error obteniendo préstamos:', error);
      return {
        success: false,
        error: error.message,
        timestamp: Date.now()
      };
    }
  }

  /**
   * Solicitar préstamo con documentación
   * @param {Object} loanData - Datos del préstamo
   * @param {number} loanData.amount - Monto solicitado
   * @param {number} loanData.term - Plazo en meses
   * @param {string} loanData.purpose - Propósito del préstamo
   * @param {string} loanData.type - Tipo de préstamo
   * @param {number} loanData.interestRate - Tasa de interés
   * @param {Object} loanData.collateral - Garantías
   * @param {Array} loanData.documents - Documentos adjuntos
   * @param {Array} loanData.guarantors - Avales
   * @returns {Promise<Object>} Resultado de la solicitud
   */
  async requestLoan(loanData) {
    const payload = {
      clientId: loanData.clientId || 'default',
      operation: 'request_loan',
      loanData: {
        amount: loanData.amount,
        term: loanData.term,
        purpose: loanData.purpose,
        type: loanData.type,
        interestRate: loanData.interestRate,
        paymentFrequency: loanData.paymentFrequency || 'monthly',
        collateral: loanData.collateral,
        guarantors: loanData.guarantors,
        documents: loanData.documents,
        additionalInfo: loanData.additionalInfo
      },
      priority: loanData.priority || 'normal',
      estimatedApproval: loanData.estimatedApproval || false,
      timestamp: Date.now()
    };

    try {
      const response = await this.client.request('request_loan', payload, {
        timeout: 30000,
        priority: 7
      });

      return {
        success: true,
        data: response.data,
        requestId: response.data.requestId,
        status: response.data.status,
        estimatedProcessingTime: response.data.estimatedProcessingTime,
        nextSteps: response.data.nextSteps,
        timestamp: response.timestamp,
        correlationId: response.correlationId
      };
    } catch (error) {
      console.error('❌ Error solicitando préstamo:', error);
      return {
        success: false,
        error: error.message,
        timestamp: Date.now()
      };
    }
  }

  /**
   * Obtener detalles completos de un préstamo
   * @param {string} loanId - ID del préstamo
   * @param {string} clientId - ID del cliente
   * @param {Object} options - Opciones adicionales
   * @returns {Promise<Object>} Detalles del préstamo
   */
  async getLoanDetails(loanId, clientId = 'default', options = {}) {
    const payload = {
      loanId,
      clientId,
      operation: 'get_loan_details',
      include: {
        payments: options.includePayments || true,
        schedule: options.includeSchedule || true,
        documents: options.includeDocuments || true,
        history: options.includeHistory || true,
        guarantor: options.includeGuarantor || false
      },
      timestamp: Date.now()
    };

    try {
      const response = await this.client.request('loans', payload, {
        timeout: 20000,
        priority: 6
      });

      return {
        success: true,
        data: response.data,
        loan: response.data.loan,
        payments: response.data.payments,
        schedule: response.data.schedule,
        documents: response.data.documents,
        history: response.data.history,
        timestamp: response.timestamp,
        correlationId: response.correlationId
      };
    } catch (error) {
      console.error('❌ Error obteniendo detalles del préstamo:', error);
      return {
        success: false,
        error: error.message,
        timestamp: Date.now()
      };
    }
  }

  // === SERVICIOS DE PERFIL ===

  /**
   * Actualizar perfil del cliente con validación
   * @param {Object} profileData - Datos del perfil
   * @param {string} profileData.clientId - ID del cliente
   * @param {Object} profileData.updates - Campos a actualizar
   * @param {Array} profileData.documents - Documentos de soporte
   * @returns {Promise<Object>} Resultado de la actualización
   */
  async updateProfile(profileData) {
    const payload = {
      clientId: profileData.clientId || 'default',
      operation: 'update_profile',
      updates: {
        personal: {
          firstName: profileData.firstName,
          lastName: profileData.lastName,
          dateOfBirth: profileData.dateOfBirth,
          gender: profileData.gender,
          maritalStatus: profileData.maritalStatus
        },
        contact: {
          email: profileData.email,
          phone: profileData.phone,
          alternatePhone: profileData.alternatePhone,
          address: profileData.address,
          workAddress: profileData.workAddress
        },
        financial: {
          occupation: profileData.occupation,
          employer: profileData.employer,
          monthlyIncome: profileData.monthlyIncome,
          otherIncome: profileData.otherIncome
        },
        emergency: {
          contactName: profileData.contactName,
          contactPhone: profileData.contactPhone,
          contactRelation: profileData.contactRelation
        }
      },
      documents: profileData.documents || [],
      validateData: profileData.validateData || true,
      timestamp: Date.now()
    };

    try {
      const response = await this.client.request('profile', payload, {
        timeout: 15000,
        priority: 6
      });

      return {
        success: true,
        data: response.data,
        updatedFields: response.data.updatedFields,
        validationResults: response.data.validationResults,
        timestamp: response.timestamp,
        correlationId: response.correlationId
      };
    } catch (error) {
      console.error('❌ Error actualizando perfil:', error);
      return {
        success: false,
        error: error.message,
        timestamp: Date.now()
      };
    }
  }

  /**
   * Obtener perfil completo del cliente
   * @param {string} clientId - ID del cliente
   * @param {Object} options - Opciones de consulta
   * @returns {Promise<Object>} Datos del perfil
   */
  async getProfile(clientId = 'default', options = {}) {
    const payload = {
      clientId,
      operation: 'get_profile',
      include: {
        accounts: options.includeAccounts || false,
        documents: options.includeDocuments || false,
        preferences: options.includePreferences || true,
        history: options.includeHistory || false,
        statistics: options.includeStatistics || false
      },
      timestamp: Date.now()
    };

    try {
      const response = await this.client.request('profile', payload, {
        timeout: 10000,
        priority: 7
      });

      return {
        success: true,
        data: response.data,
        profile: response.data.profile,
        preferences: response.data.preferences,
        statistics: response.data.statistics,
        timestamp: response.timestamp,
        correlationId: response.correlationId
      };
    } catch (error) {
      console.error('❌ Error obteniendo perfil:', error);
      return {
        success: false,
        error: error.message,
        timestamp: Date.now()
      };
    }
  }

  // === SERVICIOS DE NOTIFICACIONES ===

  /**
   * Suscribirse a notificaciones en tiempo real
   * @param {Function} callback - Función de callback
   * @returns {Promise<void>}
   */
  async subscribeToNotifications(callback) {
    try {
      await this.client.subscribe('notifications', callback);
      
      // También suscribirse a actualizaciones específicas
      await this.client.subscribe('transactionUpdate', (data) => {
        this.handleTransactionUpdate(data);
      });
      
      await this.client.subscribe('loanUpdate', (data) => {
        this.handleLoanUpdate(data);
      });
      
      await this.client.subscribe('balanceUpdate', (data) => {
        this.handleBalanceUpdate(data);
      });
      
    } catch (error) {
      console.error('❌ Error suscribiéndose a notificaciones:', error);
      throw error;
    }
  }

  /**
   * Cancelar suscripción a notificaciones
   */
  unsubscribeFromNotifications() {
    try {
      this.client.unsubscribe('notifications');
      this.client.unsubscribe('transactionUpdate');
      this.client.unsubscribe('loanUpdate');
      this.client.unsubscribe('balanceUpdate');
    } catch (error) {
      console.error('❌ Error cancelando suscripción:', error);
    }
  }

  // === MANEJADORES DE ACTUALIZACIONES ===

  /**
   * Manejar actualización de transacciones
   * @param {Object} data - Datos de la actualización
   */
  handleTransactionUpdate(data) {
    console.log('💰 Actualización de transacción recibida:', data);
    
    // Procesar notificación
    this.processNotification({
      type: 'transaction_update',
      title: 'Nueva Transacción',
      message: `Se ha registrado una nueva transacción de ${data.amount} ${data.currency}`,
      data: data,
      priority: 'normal',
      timestamp: Date.now()
    });
  }

  /**
   * Manejar actualización de préstamos
   * @param {Object} data - Datos de la actualización
   */
  handleLoanUpdate(data) {
    console.log('🏦 Actualización de préstamo recibida:', data);
    
    // Procesar notificación
    this.processNotification({
      type: 'loan_update',
      title: 'Actualización de Préstamo',
      message: `Estado de préstamo actualizado: ${data.status}`,
      data: data,
      priority: data.priority || 'normal',
      timestamp: Date.now()
    });
  }

  /**
   * Manejar actualización de saldo
   * @param {Object} data - Datos de la actualización
   */
  handleBalanceUpdate(data) {
    console.log('💳 Actualización de saldo recibida:', data);
    
    // Procesar notificación
    this.processNotification({
      type: 'balance_update',
      title: 'Saldo Actualizado',
      message: `Nuevo saldo: ${data.balance} ${data.currency}`,
      data: data,
      priority: 'high',
      timestamp: Date.now()
    });
  }

  /**
   * Procesar notificación
   * @param {Object} notification - Datos de la notificación
   */
  processNotification(notification) {
    this.notificationQueue.push(notification);
    
    if (!this.isProcessingQueue) {
      this.processNotificationQueue();
    }
  }

  /**
   * Procesar cola de notificaciones
   */
  async processNotificationQueue() {
    this.isProcessingQueue = true;
    
    while (this.notificationQueue.length > 0) {
      const notification = this.notificationQueue.shift();
      
      try {
        // Mostrar notificación desktop
        if (global?.desktop?.notify) {
          global.desktop.notify(notification);
        }
        
        // Emitir evento a la aplicación
        if (global?.app?.emit) {
          global.app.emit('notification', notification);
        }
        
        // Log para debugging
        console.log('🔔 Notificación procesada:', notification.title);
        
      } catch (error) {
        console.error('❌ Error procesando notificación:', error);
      }
    }
    
    this.isProcessingQueue = false;
  }

  // === MÉTODOS DE UTILIDAD ===

  /**
   * Verificar estado de conexión
   * @returns {Object} Estado de la conexión
   */
  getConnectionStatus() {
    return this.client.getStatus();
  }

  /**
   * Obtener estadísticas del cliente
   * @returns {Object} Estadísticas de uso
   */
  getClientStatistics() {
    const status = this.client.getStatus();
    const stats = this.client.getStatistics();
    
    return {
      ...stats,
      services: {
        balance: 'active',
        transactions: 'active',
        loans: 'active',
        profile: 'active',
        notifications: 'active'
      },
      queues: {
        notifications: this.notificationQueue.length,
        isProcessing: this.isProcessingQueue
      }
    };
  }

  /**
   * Obtener configuración del cliente
   * @returns {Object} Configuración actual
   */
  getClientConfig() {
    return {
      version: '1.0.0',
      platform: 'electron',
      features: {
        realTimeNotifications: true,
        offlineMode: false,
        backgroundSync: true,
        notifications: true
      },
      limits: {
        maxTransactionsPerRequest: 100,
        maxLoansPerRequest: 50,
        requestTimeout: 30000
      }
    };
  }
}

export default DesktopClientServices;