const QRCode = require('qrcode');
const axios = require('axios');
const os = require('os');
const path = require('path');
const crypto = require('crypto');
const { spawn } = require('child_process');

class Utils {
  // QR Code generation
  async generateQRCode(data, options = {}) {
    try {
      const defaultOptions = {
        type: 'png',
        quality: 0.92,
        margin: 1,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        },
        ...options
      };

      const qrCodeDataURL = await QRCode.toDataURL(data, defaultOptions);
      return { success: true, data: qrCodeDataURL };
    } catch (error) {
      console.error('Error generating QR code:', error);
      return { success: false, error: error.message };
    }
  }

  // HTTP requests with axios
  async httpRequest(method, url, data = null, config = {}) {
    try {
      const axiosConfig = {
        method,
        url,
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'BancoDesktop/1.0.0',
          ...config.headers
        },
        ...config
      };

      if (data && (method === 'post' || method === 'put')) {
        axiosConfig.data = data;
      }

      const response = await axios(axiosConfig);
      return {
        success: true,
        data: response.data,
        status: response.status,
        headers: response.headers
      };
    } catch (error) {
      console.error(`HTTP ${method.toUpperCase()} request error:`, error);
      return {
        success: false,
        error: error.message,
        status: error.response?.status,
        data: error.response?.data
      };
    }
  }

  // Utility functions
  formatCurrency(amount, currency = 'PEN') {
    return new Intl.NumberFormat('es-PE', {
      style: 'currency',
      currency: currency
    }).format(amount);
  }

  formatDate(date, format = 'short') {
    const d = new Date(date);
    const options = {
      short: { year: 'numeric', month: 'short', day: 'numeric' },
      long: { year: 'numeric', month: 'long', day: 'numeric' },
      datetime: { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }
    };

    return d.toLocaleDateString('es-PE', options[format] || options.short);
  }

  generateAccountNumber() {
    const timestamp = Date.now().toString();
    const random = Math.random().toString(36).substring(2, 8).toUpperCase();
    return `20${timestamp.slice(-8)}${random}`;
  }

  generateTransactionReference() {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 6).toUpperCase();
    return `TXN${timestamp}${random}`;
  }

  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  validateDNI(dni) {
    const dniRegex = /^\d{8}$/;
    return dniRegex.test(dni);
  }

  validatePhone(phone) {
    const phoneRegex = /^(\+51)?[9]\d{8}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
  }

  // Encryption utilities
  encrypt(text, key) {
    try {
      const cipher = crypto.createCipher('aes-256-cbc', key);
      let encrypted = cipher.update(text, 'utf8', 'hex');
      encrypted += cipher.final('hex');
      return encrypted;
    } catch (error) {
      console.error('Encryption error:', error);
      return null;
    }
  }

  decrypt(encryptedText, key) {
    try {
      const decipher = crypto.createDecipher('aes-256-cbc', key);
      let decrypted = decipher.update(encryptedText, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      return decrypted;
    } catch (error) {
      console.error('Decryption error:', error);
      return null;
    }
  }

  // File utilities
  getAppDataPath() {
    return path.join(os.homedir(), 'BancoDesktop');
  }

  createBackup(filename) {
    // Implementación de respaldo de datos
    return path.join(this.getAppDataPath(), 'backups', filename);
  }

  // System utilities
  getSystemInfo() {
    return {
      platform: os.platform(),
      arch: os.arch(),
      release: os.release(),
      hostname: os.hostname(),
      cpus: os.cpus().length,
      totalMemory: os.totalmem(),
      freeMemory: os.freemem()
    };
  }

  // Process utilities
  executeCommand(command, args = [], options = {}) {
    return new Promise((resolve, reject) => {
      const child = spawn(command, args, {
        ...options,
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let stdout = '';
      let stderr = '';

      child.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      child.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      child.on('close', (code) => {
        if (code === 0) {
          resolve({ stdout, stderr, code });
        } else {
          reject(new Error(`Command failed with code ${code}: ${stderr}`));
        }
      });

      child.on('error', (error) => {
        reject(error);
      });

      return child;
    });
  }

  // Validation utilities
  sanitizeInput(input) {
    if (typeof input !== 'string') return input;
    return input.trim().replace(/[<>]/g, '');
  }

  validateAmount(amount) {
    const num = parseFloat(amount);
    return !isNaN(num) && num > 0 && num <= 1000000;
  }

  // Date utilities
  addDays(date, days) {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
  }

  calculateInterest(principal, rate, timeInDays) {
    return (principal * rate * timeInDays) / (365 * 100);
  }

  // String utilities
  generateRandomString(length = 10) {
    return crypto.randomBytes(length).toString('hex').substring(0, length);
  }

  maskAccountNumber(accountNumber) {
    if (accountNumber.length < 4) return accountNumber;
    return '****' + accountNumber.slice(-4);
  }

  // Logging utilities
  log(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
    
    if (data) {
      console.log(logMessage, data);
    } else {
      console.log(logMessage);
    }

    // Aquí se puede implementar guardado en archivo de log
  }

  // Notification utilities
  showNotification(title, body, icon = 'info') {
    // Implementación de notificaciones del sistema
    // Se puede usar el sistema de notificaciones nativo o web notifications
    if ('Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification(title, { body, icon });
      } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then(permission => {
          if (permission === 'granted') {
            new Notification(title, { body, icon });
          }
        });
      }
    }
  }
}

module.exports = new Utils();
