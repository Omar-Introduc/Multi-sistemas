// Módulo de autenticación
class AuthManager {
  constructor() {
    this.currentUser = null;
    this.token = null;
    this.sessionExpiry = null;
  }

  async login(credentials) {
    try {
      // Validar credenciales
      const validation = this.validateCredentials(credentials);
      if (!validation.isValid) {
        throw new Error(validation.message);
      }

      // Simular llamada a API de autenticación
      const response = await this.authenticateWithAPI(credentials);
      
      if (response.success) {
        this.currentUser = response.user;
        this.token = response.token;
        this.sessionExpiry = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 horas

        // Guardar en store seguro
        await window.electronAPI.store.set('authToken', this.token);
        await window.electronAPI.store.set('currentUser', this.currentUser);
        await window.electronAPI.store.set('sessionExpiry', this.sessionExpiry.toISOString());

        return {
          success: true,
          user: this.currentUser,
          token: this.token
        };
      } else {
        throw new Error(response.message || 'Error de autenticación');
      }
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  validateCredentials(credentials) {
    const { username, password } = credentials;

    if (!username || !password) {
      return {
        isValid: false,
        message: 'Usuario y contraseña son requeridos'
      };
    }

    if (username.length < 3) {
      return {
        isValid: false,
        message: 'El usuario debe tener al menos 3 caracteres'
      };
    }

    if (password.length < 6) {
      return {
        isValid: false,
        message: 'La contraseña debe tener al menos 6 caracteres'
      };
    }

    return { isValid: true };
  }

  async authenticateWithAPI(credentials) {
    // Simulación de autenticación con API
    // En una aplicación real, esto sería una llamada HTTP
    
    try {
      // Simular delay de red
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Credenciales de prueba
      const validCredentials = {
        'admin': { password: 'admin123', role: 'admin', name: 'Administrador' },
        'usuario': { password: '123456', role: 'user', name: 'Usuario Demo' },
        'banco': { password: 'banco2023', role: 'admin', name: 'Sistema Bancario' }
      };

      const userData = validCredentials[credentials.username];
      
      if (userData && userData.password === credentials.password) {
        const user = {
          id: this.generateUserId(),
          username: credentials.username,
          name: userData.name,
          role: userData.role,
          email: `${credentials.username}@banco.com`,
          avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(userData.name)}&background=2563eb&color=fff`,
          lastLogin: new Date().toISOString(),
          permissions: this.getPermissions(userData.role)
        };

        const token = this.generateToken(user);

        return {
          success: true,
          user,
          token,
          message: 'Autenticación exitosa'
        };
      } else {
        return {
          success: false,
          message: 'Credenciales inválidas'
        };
      }
    } catch (error) {
      return {
        success: false,
        message: 'Error de conexión: ' + error.message
      };
    }
  }

  async logout() {
    try {
      // Limpiar datos locales
      this.currentUser = null;
      this.token = null;
      this.sessionExpiry = null;

      // Limpiar store
      await window.electronAPI.store.delete('authToken');
      await window.electronAPI.store.delete('currentUser');
      await window.electronAPI.store.delete('sessionExpiry');

      // Notificar logout al servidor si es necesario
      if (this.token) {
        await this.notifyLogoutToServer();
      }

      return {
        success: true,
        message: 'Sesión cerrada exitosamente'
      };
    } catch (error) {
      console.error('Logout error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  async notifyLogoutToServer() {
    try {
      // Simular notificación de logout al servidor
      if (window.electronAPI.http) {
        await window.electronAPI.http.post('/api/auth/logout', {
          token: this.token
        });
      }
    } catch (error) {
      console.warn('Could not notify logout to server:', error);
    }
  }

  async checkSession() {
    try {
      // Verificar token en store
      const token = await window.electronAPI.store.get('authToken');
      const user = await window.electronAPI.store.get('currentUser');
      const expiry = await window.electronAPI.store.get('sessionExpiry');

      if (!token || !user || !expiry) {
        return this.createSessionError('No hay sesión activa');
      }

      // Verificar expiración
      const expiryDate = new Date(expiry);
      if (expiryDate < new Date()) {
        return this.createSessionError('La sesión ha expirado');
      }

      // Validar token con servidor
      const isValid = await this.validateTokenWithServer(token);
      if (!isValid) {
        return this.createSessionError('Token inválido');
      }

      // Restaurar sesión
      this.currentUser = user;
      this.token = token;
      this.sessionExpiry = expiryDate;

      return {
        success: true,
        user: this.currentUser,
        token: this.token
      };
    } catch (error) {
      console.error('Session check error:', error);
      return this.createSessionError('Error verificando sesión');
    }
  }

  async validateTokenWithServer(token) {
    try {
      // Simular validación de token con servidor
      // En una app real, esto sería una llamada HTTP
      await new Promise(resolve => setTimeout(resolve, 500));
      return token && token.length > 10;
    } catch (error) {
      console.warn('Token validation failed:', error);
      return false;
    }
  }

  async refreshSession() {
    try {
      if (!this.token) {
        throw new Error('No hay sesión para renovar');
      }

      // Simular renovación de token
      const response = await this.renewTokenWithServer(this.token);
      
      if (response.success) {
        this.token = response.newToken;
        this.sessionExpiry = new Date(Date.now() + 24 * 60 * 60 * 1000);

        // Actualizar en store
        await window.electronAPI.store.set('authToken', this.token);
        await window.electronAPI.store.set('sessionExpiry', this.sessionExpiry.toISOString());

        return {
          success: true,
          token: this.token,
          expiry: this.sessionExpiry
        };
      } else {
        throw new Error(response.message || 'Error renovando token');
      }
    } catch (error) {
      console.error('Session refresh error:', error);
      
      // Si falla la renovación, cerrar sesión
      await this.logout();
      
      return {
        success: false,
        error: error.message
      };
    }
  }

  async renewTokenWithServer(token) {
    // Simulación de renovación de token
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      return {
        success: true,
        newToken: this.generateToken(this.currentUser),
        message: 'Token renovado exitosamente'
      };
    } catch (error) {
      return {
        success: false,
        message: 'Error renovando token: ' + error.message
      };
    }
  }

  async changePassword(currentPassword, newPassword) {
    try {
      // Validar nueva contraseña
      const validation = this.validateNewPassword(newPassword);
      if (!validation.isValid) {
        throw new Error(validation.message);
      }

      // Verificar contraseña actual
      if (!this.currentUser) {
        throw new Error('Usuario no autenticado');
      }

      // Simular cambio de contraseña
      const response = await this.changePasswordWithServer(currentPassword, newPassword);
      
      if (response.success) {
        return {
          success: true,
          message: 'Contraseña cambiada exitosamente'
        };
      } else {
        throw new Error(response.message);
      }
    } catch (error) {
      console.error('Password change error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  validateNewPassword(password) {
    if (!password || password.length < 8) {
      return {
        isValid: false,
        message: 'La nueva contraseña debe tener al menos 8 caracteres'
      };
    }

    // Validar complejidad
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    if (!hasUpperCase || !hasLowerCase || !hasNumbers || !hasSpecialChar) {
      return {
        isValid: false,
        message: 'La contraseña debe contener mayúsculas, minúsculas, números y caracteres especiales'
      };
    }

    return { isValid: true };
  }

  async changePasswordWithServer(currentPassword, newPassword) {
    // Simular cambio de contraseña con servidor
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // En una app real, esto haría una llamada HTTP
      console.log('Password changed for user:', this.currentUser.username);
      
      return {
        success: true,
        message: 'Contraseña cambiada exitosamente'
      };
    } catch (error) {
      return {
        success: false,
        message: 'Error cambiando contraseña: ' + error.message
      };
    }
  }

  // Métodos auxiliares
  generateUserId() {
    return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  generateToken(user) {
    const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
    const payload = btoa(JSON.stringify({
      sub: user.id,
      username: user.username,
      role: user.role,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60) // 24 horas
    }));
    const signature = btoa(user.username + 'banco2023');
    
    return `${header}.${payload}.${signature}`;
  }

  getPermissions(role) {
    const permissions = {
      admin: [
        'accounts:read',
        'accounts:write',
        'accounts:delete',
        'transactions:read',
        'transactions:write',
        'transactions:delete',
        'loans:read',
        'loans:write',
        'loans:delete',
        'users:read',
        'users:write',
        'users:delete',
        'reports:read',
        'settings:read',
        'settings:write'
      ],
      user: [
        'accounts:read',
        'transactions:read',
        'transactions:write',
        'loans:read'
      ]
    };

    return permissions[role] || permissions.user;
  }

  createSessionError(message) {
    return {
      success: false,
      error: message,
      code: 'SESSION_ERROR'
    };
  }

  // Getters
  getCurrentUser() {
    return this.currentUser;
  }

  getToken() {
    return this.token;
  }

  isLoggedIn() {
    return this.currentUser !== null && this.token !== null;
  }

  hasPermission(permission) {
    if (!this.currentUser) return false;
    return this.currentUser.permissions.includes(permission);
  }

  isAdmin() {
    return this.currentUser && this.currentUser.role === 'admin';
  }

  // Auto-logout en inactividad
  setupAutoLogout() {
    let inactivityTimer;
    const INACTIVITY_LIMIT = 30 * 60 * 1000; // 30 minutos

    const resetTimer = () => {
      clearTimeout(inactivityTimer);
      inactivityTimer = setTimeout(async () => {
        await this.logout();
        if (window.bancoApp) {
          window.bancoApp.showNotification('Sesión cerrada por inactividad', 'warning');
          window.bancoApp.showLoginScreen();
        }
      }, INACTIVITY_LIMIT);
    };

    // Eventos que resetean el timer
    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
      document.addEventListener(event, resetTimer, true);
    });

    resetTimer(); // Inicializar timer
  }
}

// Instancia global del manager de autenticación
window.authManager = new AuthManager();
