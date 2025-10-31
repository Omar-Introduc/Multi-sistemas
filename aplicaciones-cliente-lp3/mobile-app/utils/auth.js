import AsyncStorage from '@react-native-async-storage/async-storage';
import { api, rabbitMQService } from './api';

// Claves para AsyncStorage
const TOKEN_KEY = 'userToken';
const USER_DATA_KEY = 'userData';

// Configuración de autenticación
const AUTH_CONFIG = {
  tokenExpirationTime: 24 * 60 * 60 * 1000, // 24 horas en millisegundos
  maxLoginAttempts: 3,
  lockoutDuration: 30 * 60 * 1000 // 30 minutos en millisegundos
};

// Credenciales de prueba (en producción esto estaría en el backend)
const TEST_USERS = [
  {
    id: '1',
    email: 'usuario@banco.com',
    password: '123456',
    name: 'Juan Pérez',
    phone: '+1234567890',
    createdAt: '2025-01-01T00:00:00Z'
  },
  {
    id: '2',
    email: 'maria@banco.com',
    password: '654321',
    name: 'María García',
    phone: '+0987654321',
    createdAt: '2025-01-01T00:00:00Z'
  }
];

class AuthService {
  constructor() {
    this.loginAttempts = 0;
    this.lockoutTime = null;
  }

  // Verificar si el usuario está bloqueado
  isLockedOut() {
    if (!this.lockoutTime) return false;
    return Date.now() < this.lockoutTime;
  }

  // Obtener tiempo restante de bloqueo
  getLockoutTimeRemaining() {
    if (!this.lockoutTime) return 0;
    return Math.max(0, this.lockoutTime - Date.now());
  }

  // Simular incremento de intentos fallidos
  incrementLoginAttempts() {
    this.loginAttempts++;
    if (this.loginAttempts >= AUTH_CONFIG.maxLoginAttempts) {
      this.lockoutTime = Date.now() + AUTH_CONFIG.lockoutDuration;
    }
  }

  // Reiniciar intentos de login
  resetLoginAttempts() {
    this.loginAttempts = 0;
    this.lockoutTime = null;
  }

  // Generar token simulado
  generateToken(user) {
    const token = `token_${user.id}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    return {
      token,
      expiresAt: Date.now() + AUTH_CONFIG.tokenExpirationTime
    };
  }

  // Verificar si el token es válido
  async isTokenValid(token) {
    try {
      // En una implementación real, esto verificaría con el backend
      if (!token) return false;

      // Verificar con el backend si el token es válido
      await apiClient.post('/auth/verify', { token });
      return true;
    } catch (error) {
      console.error('Error verifying token:', error);
      return false;
    }
  }

  // Iniciar sesión
  async login(email, password) {
    try {
      // Verificar si está bloqueado
      if (this.isLockedOut()) {
        const remainingTime = this.getLockoutTimeRemaining();
        const minutes = Math.ceil(remainingTime / (1000 * 60));
        throw new Error(`Cuenta bloqueada. Intenta nuevamente en ${minutes} minutos.`);
      }

      // Buscar usuario en credenciales de prueba
      const user = TEST_USERS.find(u => u.email === email && u.password === password);
      
      if (!user) {
        this.incrementLoginAttempts();
        throw new Error('Credenciales inválidas');
      }

      // Generar token
      const tokenData = this.generateToken(user);
      const userData = {
        id: user.id,
        email: user.email,
        name: user.name,
        phone: user.phone,
        ...tokenData
      };

      // Guardar en AsyncStorage
      await this.saveAuthData(tokenData.token, userData);

      // Conectar a RabbitMQ
      await rabbitMQService.connect();
      await rabbitMQService.sendMessage('USER_LOGIN', {
        userId: user.id,
        email: user.email,
        timestamp: new Date().toISOString()
      });

      // Resetear intentos de login
      this.resetLoginAttempts();

      return userData;
    } catch (error) {
      console.error('Error in login:', error);
      throw error;
    }
  }

  // Cerrar sesión
  async logout() {
    try {
      // Obtener datos del usuario actual
      const userData = await this.getCurrentUser();
      
      if (userData) {
        // Enviar mensaje de logout a RabbitMQ
        await rabbitMQService.sendMessage('USER_LOGOUT', {
          userId: userData.id,
          timestamp: new Date().toISOString()
        });
      }

      // Limpiar datos de autenticación
      await this.clearAuthData();

      console.log('User logged out successfully');
    } catch (error) {
      console.error('Error in logout:', error);
      // Limpiar datos localmente incluso si hay error
      await this.clearAuthData();
    }
  }

  // Verificar si el usuario está autenticado
  async isAuthenticated() {
    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      if (!token) return false;

      // Verificar si el token ha expirado
      const userData = await AsyncStorage.getItem(USER_DATA_KEY);
      if (!userData) return false;

      const parsedUserData = JSON.parse(userData);
      const expiresAt = parsedUserData.expiresAt;
      
      if (Date.now() >= expiresAt) {
        // Token expirado, limpiar datos
        await this.clearAuthData();
        return false;
      }

      // Verificar token con backend (opcional)
      const isValid = await this.isTokenValid(token);
      if (!isValid) {
        await this.clearAuthData();
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error checking authentication:', error);
      await this.clearAuthData();
      return false;
    }
  }

  // Obtener datos del usuario actual
  async getCurrentUser() {
    try {
      const userDataStr = await AsyncStorage.getItem(USER_DATA_KEY);
      if (!userDataStr) return null;
      
      const userData = JSON.parse(userDataStr);
      
      // Verificar si el token ha expirado
      if (Date.now() >= userData.expiresAt) {
        await this.clearAuthData();
        return null;
      }

      return userData;
    } catch (error) {
      console.error('Error getting current user:', error);
      return null;
    }
  }

  // Obtener token del usuario actual
  async getCurrentToken() {
    try {
      return await AsyncStorage.getItem(TOKEN_KEY);
    } catch (error) {
      console.error('Error getting current token:', error);
      return null;
    }
  }

  // Guardar datos de autenticación
  async saveAuthData(token, userData) {
    try {
      await AsyncStorage.multiSet([
        [TOKEN_KEY, token],
        [USER_DATA_KEY, JSON.stringify(userData)]
      ]);
    } catch (error) {
      console.error('Error saving auth data:', error);
      throw error;
    }
  }

  // Limpiar datos de autenticación
  async clearAuthData() {
    try {
      await AsyncStorage.multiRemove([TOKEN_KEY, USER_DATA_KEY]);
    } catch (error) {
      console.error('Error clearing auth data:', error);
    }
  }

  // Actualizar perfil de usuario
  async updateProfile(updates) {
    try {
      const userData = await this.getCurrentUser();
      if (!userData) throw new Error('No user logged in');

      const updatedUserData = {
        ...userData,
        ...updates,
        updatedAt: new Date().toISOString()
      };

      await AsyncStorage.setItem(USER_DATA_KEY, JSON.stringify(updatedUserData));

      // Enviar actualización a RabbitMQ
      await rabbitMQService.sendMessage('USER_PROFILE_UPDATE', {
        userId: userData.id,
        updates,
        timestamp: new Date().toISOString()
      });

      return updatedUserData;
    } catch (error) {
      console.error('Error updating profile:', error);
      throw error;
    }
  }

  // Cambiar contraseña
  async changePassword(currentPassword, newPassword) {
    try {
      const userData = await this.getCurrentUser();
      if (!userData) throw new Error('No user logged in');

      // En una implementación real, esto verificaría con el backend
      // Por ahora simulamos el cambio de contraseña
      await rabbitMQService.sendMessage('USER_PASSWORD_CHANGE', {
        userId: userData.id,
        timestamp: new Date().toISOString()
      });

      return { success: true, message: 'Contraseña actualizada exitosamente' };
    } catch (error) {
      console.error('Error changing password:', error);
      throw error;
    }
  }
}

const authService = new AuthService();

// Funciones de conveniencia para usar en la app
export const authenticateUser = authService.login.bind(authService);
export const logoutUser = authService.logout.bind(authService);
export const isAuthenticated = authService.isAuthenticated.bind(authService);
export const getCurrentUser = authService.getCurrentUser.bind(authService);
export const getCurrentToken = authService.getCurrentToken.bind(authService);
export const updateUserProfile = authService.updateProfile.bind(authService);
export const changeUserPassword = authService.changePassword.bind(authService);

export default authService;