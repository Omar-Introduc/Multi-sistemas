import AsyncStorage from '@react-native-async-storage/async-storage';
import { ApiResponse, RequestConfig, RetryConfig, ProgressInfo, WebSocketMessage, ErrorInfo } from '../types/response.types';

export class ResponseManager {
  private static instance: ResponseManager;
  private activeRequests: Map<string, RequestConfig> = new Map();
  private requestHistory: Array<{ config: RequestConfig; response: ApiResponse; timestamp: number }> = [];
  private retryConfigs: Map<string, Partial<RetryConfig>> = new Map();
  private isOnline: boolean = true;
  private listeners: Map<string, Function[]> = new Map();

  private constructor() {
    this.loadPersistedState();
    this.setupNetworkListener();
  }

  public static getInstance(): ResponseManager {
    if (!ResponseManager.instance) {
      ResponseManager.instance = new ResponseManager();
    }
    return ResponseManager.instance;
  }

  /**
   * Realiza una petición HTTP con manejo completo de respuestas
   */
  public async request<T = any>(config: RequestConfig): Promise<ApiResponse<T>> {
    if (!this.isOnline) {
      const offlineResponse: ApiResponse<T> = {
        success: false,
        error: 'Sin conexión a internet',
        timestamp: Date.now(),
        requestId: this.generateRequestId()
      };
      return offlineResponse;
    }

    const requestId = this.generateRequestId();
    const startTime = Date.now();
    
    try {
      // Validar configuración
      this.validateConfig(config);
      
      // Registrar petición activa
      this.activeRequests.set(requestId, config);
      this.emit('request:started', { requestId, config });

      // Ejecutar petición con reintentos
      const response = await this.executeWithRetry<T>(config, requestId);
      
      // Registrar en historial
      this.requestHistory.push({
        config,
        response,
        timestamp: Date.now()
      });

      // Limpiar petición activa
      this.activeRequests.delete(requestId);
      this.emit('request:completed', { requestId, response, duration: Date.now() - startTime });

      // Persistir estado
      await this.persistState();

      return response;

    } catch (error) {
      const errorResponse: ApiResponse<T> = {
        success: false,
        error: error instanceof Error ? error.message : 'Error desconocido',
        timestamp: Date.now(),
        requestId
      };

      // Registrar en historial
      this.requestHistory.push({
        config,
        response: errorResponse,
        timestamp: Date.now()
      });

      // Limpiar petición activa
      this.activeRequests.delete(requestId);
      this.emit('request:failed', { requestId, error, duration: Date.now() - startTime });

      // Persistir estado
      await this.persistState();

      return errorResponse;
    }
  }

  /**
   * Ejecuta una petición con mecanismo de reintentos
   */
  private async executeWithRetry<T>(
    config: RequestConfig, 
    requestId: string,
    attempt = 1
  ): Promise<ApiResponse<T>> {
    const retryConfig = this.getRetryConfig(config);
    
    try {
      // Ejecutar petición
      const response = await this.performRequest<T>(config, requestId);
      
      // Si es exitosa, devolver respuesta
      if (response.success) {
        return response;
      }

      // Si falla y se pueden hacer reintentos
      const shouldRetry = this.shouldRetry(response, retryConfig, attempt);
      if (shouldRetry && attempt <= retryConfig.maxRetries) {
        const delay = this.calculateRetryDelay(retryConfig, attempt);
        this.emit('request:retry', { requestId, attempt, delay, error: response.error });
        
        await this.delay(delay);
        return this.executeWithRetry<T>(config, requestId, attempt + 1);
      }

      return response;

    } catch (error) {
      const shouldRetry = attempt <= retryConfig.maxRetries;
      if (shouldRetry) {
        const delay = this.calculateRetryDelay(retryConfig, attempt);
        this.emit('request:retry', { requestId, attempt, delay, error });
        
        await this.delay(delay);
        return this.executeWithRetry<T>(config, requestId, attempt + 1);
      }

      throw error;
    }
  }

  /**
   * Realiza la petición HTTP real
   */
  private async performRequest<T>(
    config: RequestConfig, 
    requestId: string
  ): Promise<ApiResponse<T>> {
    try {
      const fetchConfig: RequestInit = {
        method: config.method,
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': requestId,
          ...config.headers
        }
      };

      if (config.data && ['POST', 'PUT', 'PATCH'].includes(config.method)) {
        fetchConfig.body = JSON.stringify(config.data);
      }

      const response = await fetch(config.url, fetchConfig);

      // Procesar respuesta
      let data: any;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      const apiResponse: ApiResponse<T> = {
        success: response.ok,
        data,
        code: response.status,
        message: response.statusText,
        timestamp: Date.now(),
        requestId
      };

      this.emit('request:response', { requestId, response: apiResponse });
      return apiResponse;

    } catch (error) {
      const apiResponse: ApiResponse<T> = {
        success: false,
        error: error instanceof Error ? error.message : 'Error de red',
        timestamp: Date.now(),
        requestId
      };

      return apiResponse;
    }
  }

  /**
   * Determina si se debe reintentar la petición
   */
  private shouldRetry(
    response: ApiResponse, 
    retryConfig: RetryConfig, 
    attempt: number
  ): boolean {
    // No reintentar si la respuesta es exitosa
    if (response.success) return false;

    // Reintentar por errores de red o códigos específicos
    if (response.code) {
      return retryConfig.retryableStatuses.includes(response.code);
    }

    // Reintentar por errores de conectividad
    return true;
  }

  /**
   * Calcula el delay para el siguiente reintento
   */
  private calculateRetryDelay(retryConfig: RetryConfig, attempt: number): number {
    const exponentialDelay = retryConfig.retryDelay * 
      Math.pow(retryConfig.backoffMultiplier, attempt - 1);
    
    return Math.min(exponentialDelay, retryConfig.maxRetryDelay);
  }

  /**
   * Configura listeners de red
   */
  private setupNetworkListener(): void {
    // En React Native, aquí usarías NetInfo o similar
    // Por ahora simulamos la funcionalidad
    this.isOnline = true;
    
    this.emit('network:status', { isOnline: true });
  }

  /**
   * Configura reintentos personalizados para una URL
   */
  public setRetryConfig(url: string, config: Partial<RetryConfig>): void {
    this.retryConfigs.set(url, config);
  }

  /**
   * Obtiene configuración de reintentos
   */
  private getRetryConfig(config: RequestConfig): RetryConfig {
    const customConfig = this.retryConfigs.get(config.url);
    
    return {
      maxRetries: customConfig?.maxRetries || 3,
      retryDelay: customConfig?.retryDelay || 1000,
      backoffMultiplier: customConfig?.backoffMultiplier || 2,
      maxRetryDelay: customConfig?.maxRetryDelay || 30000,
      retryableStatuses: customConfig?.retryableStatuses || [408, 429, 500, 502, 503, 504]
    };
  }

  /**
   * Obtiene el estado actual de las peticiones activas
   */
  public getActiveRequests(): Array<{ id: string; config: RequestConfig }> {
    return Array.from(this.activeRequests.entries()).map(([id, config]) => ({
      id,
      config
    }));
  }

  /**
   * Obtiene el historial de peticiones
   */
  public getRequestHistory(limit = 100): Array<{
    config: RequestConfig;
    response: ApiResponse;
    timestamp: number;
  }> {
    return this.requestHistory.slice(-limit);
  }

  /**
   * Cancela una petición activa
   */
  public cancelRequest(requestId: string): boolean {
    return this.activeRequests.delete(requestId);
  }

  /**
   * Cancela todas las peticiones activas
   */
  public cancelAllRequests(): void {
    this.activeRequests.clear();
    this.emit('requests:cancelled');
  }

  /**
   * Valida la configuración de la petición
   */
  private validateConfig(config: RequestConfig): void {
    if (!config.url) {
      throw new Error('URL es requerida');
    }
    
    if (!config.method) {
      throw new Error('Método HTTP es requerido');
    }
  }

  /**
   * Genera un ID único para la petición
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Delay helper
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Persiste el estado en AsyncStorage
   */
  private async persistState(): Promise<void> {
    try {
      const state = {
        requestHistory: this.requestHistory.slice(-50), // Mantener solo las últimas 50
        retryConfigs: Array.from(this.retryConfigs.entries())
      };
      
      await AsyncStorage.setItem('responseManager_state', JSON.stringify(state));
    } catch (error) {
      console.error('Error persistiendo estado:', error);
    }
  }

  /**
   * Carga el estado persistido
   */
  private async loadPersistedState(): Promise<void> {
    try {
      const persisted = await AsyncStorage.getItem('responseManager_state');
      if (persisted) {
        const state = JSON.parse(persisted);
        this.requestHistory = state.requestHistory || [];
        this.retryConfigs = new Map(state.retryConfigs || []);
      }
    } catch (error) {
      console.error('Error cargando estado persistido:', error);
    }
  }

  /**
   * Limpia el estado persistido
   */
  public async clearPersistedState(): Promise<void> {
    await AsyncStorage.removeItem('responseManager_state');
    this.requestHistory = [];
    this.retryConfigs.clear();
  }

  /**
   * Obtiene estadísticas del manager
   */
  public getStats(): {
    activeRequests: number;
    totalRequests: number;
    successRate: number;
    averageResponseTime: number;
    isOnline: boolean;
  } {
    const totalRequests = this.requestHistory.length;
    const successfulRequests = this.requestHistory.filter(r => r.response.success).length;
    
    const responseTimes = this.requestHistory.map(r => 
      r.timestamp - (r.config as any).startTime || 0
    ).filter(t => t > 0);
    
    const averageResponseTime = responseTimes.length > 0 
      ? responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length 
      : 0;

    return {
      activeRequests: this.activeRequests.size,
      totalRequests,
      successRate: totalRequests > 0 ? (successfulRequests / totalRequests) * 100 : 0,
      averageResponseTime,
      isOnline: this.isOnline
    };
  }

  /**
   * Event emitter methods
   */
  public on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  public off(event: string, callback: Function): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      const index = eventListeners.indexOf(callback);
      if (index >= 0) {
        eventListeners.splice(index, 1);
      }
    }
  }

  public emit(event: string, ...args: any[]): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(callback => {
        try {
          callback(...args);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      });
    }
  }
}