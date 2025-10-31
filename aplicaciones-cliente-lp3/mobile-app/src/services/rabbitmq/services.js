import RabbitMQClient from './client';

class ClientServices {
  constructor(rabbitMQClient) {
    this.client = rabbitMQClient;
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
        timestamp: response.timestamp
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
   * Obtener historial de transacciones
   * @param {Object} params - Parámetros de filtrado
   * @param {string} params.accountId - ID de la cuenta
   * @param {Date} params.startDate - Fecha inicio
   * @param {Date} params.endDate - Fecha fin
   * @param {string} params.type - Tipo de transacción
   * @param {number} params.page - Página
   * @param {number} params.limit - Límite de resultados
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
        amount: params.amount
      },
      pagination: {
        page: params.page || 1,
        limit: params.limit || 20
      },
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
        timestamp: response.timestamp
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

  // === SERVICIOS DE PRÉSTAMOS ===

  /**
   * Obtener préstamos del cliente
   * @param {Object} params - Parámetros de consulta
   * @param {string} params.clientId - ID del cliente
   * @param {string} params.status - Estado del préstamo
   * @returns {Promise<Object>} Lista de préstamos
   */
  async getLoans(params = {}) {
    const payload = {
      clientId: params.clientId || 'default',
      operation: 'get_loans',
      filters: {
        status: params.status,
        type: params.type
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
        timestamp: response.timestamp
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
   * Solicitar préstamo
   * @param {Object} loanData - Datos del préstamo
   * @param {number} loanData.amount - Monto solicitado
   * @param {number} loanData.term - Plazo en meses
   * @param {string} loanData.purpose - Propósito del préstamo
   * @param {string} loanData.clientId - ID del cliente
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
        interestRate: loanData.interestRate,
        collateral: loanData.collateral,
        guarantor: loanData.guarantor
      },
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
        timestamp: response.timestamp
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
   * Obtener detalles de un préstamo específico
   * @param {string} loanId - ID del préstamo
   * @param {string} clientId - ID del cliente
   * @returns {Promise<Object>} Detalles del préstamo
   */
  async getLoanDetails(loanId, clientId = 'default') {
    const payload = {
      loanId,
      clientId,
      operation: 'get_loan_details',
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
        timestamp: response.timestamp
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
   * Actualizar perfil del cliente
   * @param {Object} profileData - Datos del perfil
   * @param {string} profileData.clientId - ID del cliente
   * @param {Object} profileData.updates - Campos a actualizar
   * @returns {Promise<Object>} Resultado de la actualización
   */
  async updateProfile(profileData) {
    const payload = {
      clientId: profileData.clientId || 'default',
      operation: 'update_profile',
      updates: {
        email: profileData.email,
        phone: profileData.phone,
        address: profileData.address,
        emergencyContact: profileData.emergencyContact
      },
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
        timestamp: response.timestamp
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
   * Obtener perfil del cliente
   * @param {string} clientId - ID del cliente
   * @returns {Promise<Object>} Datos del perfil
   */
  async getProfile(clientId = 'default') {
    const payload = {
      clientId,
      operation: 'get_profile',
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
        timestamp: response.timestamp
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
      await this.client.subscribeNotifications(callback);
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
      this.client.unsubscribeNotifications();
    } catch (error) {
      console.error('❌ Error cancelando suscripción:', error);
    }
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
    return {
      ...status,
      services: {
        balance: 'active',
        transactions: 'active',
        loans: 'active',
        profile: 'active',
        notifications: 'active'
      }
    };
  }
}

export default ClientServices;