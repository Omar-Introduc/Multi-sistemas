import AsyncStorage from '@react-native-async-storage/async-storage';

export class QRGeneratorService {
  static async generateQRCode(options) {
    const {
      type,
      amount,
      description,
      merchant,
      recipientName,
      recipientAccount,
      reference,
      timestamp = Date.now(),
      merchantId = 'demo-merchant'
    } = options;

    // Generate unique transaction ID
    const transactionId = `TXN_${timestamp}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Create base QR data structure
    const qrData = {
      version: '1.0',
      type,
      timestamp,
      transactionId,
      merchantId,
      ...(amount && { amount }),
      ...(description && { description }),
      ...(merchant && { merchant }),
      ...(recipientName && { recipient: { name: recipientName } }),
      ...(recipientAccount && { recipient: { ...(recipientAccount && { account: recipientAccount }) } }),
      ...(reference && { reference }),
    };

    // Add type-specific data
    switch (type) {
      case 'payment':
        qrData.currency = 'USD';
        qrData.expiry = timestamp + (24 * 60 * 60 * 1000); // 24 hours
        break;
        
      case 'transfer':
        qrData.currency = 'USD';
        qrData.transferType = 'internal'; // or 'external'
        break;
        
      case 'request':
        qrData.currency = 'USD';
        qrData.requestId = `REQ_${timestamp}`;
        qrData.expiry = timestamp + (7 * 24 * 60 * 60 * 1000); // 7 days
        break;
        
      default:
        throw new Error('Tipo de QR no válido');
    }

    // Generate QR string
    const qrString = JSON.stringify(qrData);
    
    // Validate QR data
    this.validateQRData(qrData);
    
    // Store QR data for reference
    await this.storeQRHistory(qrData);
    
    return {
      qrString,
      data: qrString,
      ...qrData
    };
  }

  static validateQRData(qrData) {
    // Validate required fields based on type
    switch (qrData.type) {
      case 'payment':
        if (!qrData.amount || qrData.amount <= 0) {
          throw new Error('Monto requerido para pagos');
        }
        if (!qrData.description) {
          throw new Error('Descripción requerida para pagos');
        }
        break;
        
      case 'transfer':
        if (!qrData.recipient?.account) {
          throw new Error('Cuenta de destinatario requerida para transferencias');
        }
        if (!qrData.recipient?.name) {
          throw new Error('Nombre de destinatario requerido para transferencias');
        }
        break;
        
      case 'request':
        if (!qrData.amount || qrData.amount <= 0) {
          throw new Error('Monto requerido para solicitudes de pago');
        }
        break;
    }

    // Validate general fields
    if (!qrData.timestamp || qrData.timestamp <= 0) {
      throw new Error('Timestamp inválido');
    }
    
    if (qrData.amount && (isNaN(qrData.amount) || qrData.amount > 1000000)) {
      throw new Error('Monto excede el límite máximo');
    }
    
    if (qrData.description && qrData.description.length > 255) {
      throw new Error('Descripción muy larga');
    }
    
    return true;
  }

  static async storeQRHistory(qrData) {
    try {
      const history = await this.getQRHistory();
      
      const qrRecord = {
        id: qrData.transactionId || `QR_${Date.now()}`,
        type: qrData.type,
        data: qrData,
        createdAt: new Date().toISOString(),
        processed: false,
      };
      
      // Add to beginning of array
      history.unshift(qrRecord);
      
      // Keep only last 50 QR codes
      const trimmedHistory = history.slice(0, 50);
      
      await AsyncStorage.setItem('qrHistory', JSON.stringify(trimmedHistory));
    } catch (error) {
      console.warn('Could not store QR history:', error);
    }
  }

  static async getQRHistory() {
    try {
      const history = await AsyncStorage.getItem('qrHistory');
      return history ? JSON.parse(history) : [];
    } catch (error) {
      console.warn('Could not get QR history:', error);
      return [];
    }
  }

  static async clearQRHistory() {
    try {
      await AsyncStorage.removeItem('qrHistory');
    } catch (error) {
      console.warn('Could not clear QR history:', error);
    }
  }

  static async processQRCode(qrString) {
    try {
      const qrData = JSON.parse(qrString);
      
      // Validate QR data
      this.validateQRData(qrData);
      
      // Check if QR is expired
      if (qrData.expiry && Date.now() > qrData.expiry) {
        throw new Error('Código QR expirado');
      }
      
      // Process based on type
      let processedData;
      
      switch (qrData.type) {
        case 'payment':
          processedData = await this.processPaymentQR(qrData);
          break;
          
        case 'transfer':
          processedData = await this.processTransferQR(qrData);
          break;
          
        case 'request':
          processedData = await this.processRequestQR(qrData);
          break;
          
        default:
          throw new Error('Tipo de QR no soportado');
      }
      
      // Update QR as processed
      await this.markQRAsProcessed(qrData.transactionId);
      
      return {
        success: true,
        data: qrData,
        processedData,
        timestamp: Date.now()
      };
      
    } catch (error) {
      return {
        success: false,
        error: error.message,
        timestamp: Date.now()
      };
    }
  }

  static async processPaymentQR(qrData) {
    // Simulate payment processing
    return {
      paymentId: `PAY_${Date.now()}`,
      merchantId: qrData.merchantId,
      merchantName: qrData.merchant,
      amount: qrData.amount,
      currency: qrData.currency,
      description: qrData.description,
      status: 'pending'
    };
  }

  static async processTransferQR(qrData) {
    // Simulate transfer processing
    return {
      transferId: `TRF_${Date.now()}`,
      recipientName: qrData.recipient?.name,
      recipientAccount: qrData.recipient?.account,
      amount: qrData.amount,
      description: qrData.description,
      transferType: qrData.transferType,
      status: 'pending'
    };
  }

  static async processRequestQR(qrData) {
    // Simulate request processing
    return {
      requestId: qrData.requestId,
      requestedAmount: qrData.amount,
      description: qrData.description,
      requesterName: qrData.recipient?.name,
      status: 'pending'
    };
  }

  static async markQRAsProcessed(transactionId) {
    try {
      const history = await this.getQRHistory();
      const updatedHistory = history.map(item => 
        item.id === transactionId 
          ? { ...item, processed: true, processedAt: new Date().toISOString() }
          : item
      );
      
      await AsyncStorage.setItem('qrHistory', JSON.stringify(updatedHistory));
    } catch (error) {
      console.warn('Could not mark QR as processed:', error);
    }
  }

  // Utility methods
  static formatAmount(amount, currency = 'USD') {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  }

  static parseAmount(amountString) {
    const amount = parseFloat(amountString.replace(',', '.'));
    if (isNaN(amount) || amount < 0) {
      throw new Error('Monto inválido');
    }
    return amount;
  }

  static isValidAccountNumber(accountNumber) {
    // Basic validation for account numbers
    return /^\d{10,20}$/.test(accountNumber.replace(/\s/g, ''));
  }

  static formatAccountNumber(accountNumber) {
    // Format account number with spaces for readability
    const cleaned = accountNumber.replace(/\s/g, '');
    return cleaned.replace(/(\d{4})(?=\d)/g, '$1 ').trim();
  }

  static generateSecureReference() {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substr(2, 9);
    return `REF_${timestamp}_${random}`.toUpperCase();
  }

  // Validation helpers
  static validateAmount(amount) {
    if (typeof amount !== 'number' || amount <= 0) {
      throw new Error('El monto debe ser un número positivo');
    }
    if (amount > 1000000) {
      throw new Error('El monto excede el límite máximo de $1,000,000');
    }
    return true;
  }

  static validateDescription(description) {
    if (!description || description.trim().length === 0) {
      throw new Error('La descripción es requerida');
    }
    if (description.length > 255) {
      throw new Error('La descripción no puede exceder 255 caracteres');
    }
    return true;
  }

  static validateMerchant(merchant) {
    if (merchant && merchant.length > 100) {
      throw new Error('El nombre del comercio no puede exceder 100 caracteres');
    }
    return true;
  }
}

export default QRGeneratorService;