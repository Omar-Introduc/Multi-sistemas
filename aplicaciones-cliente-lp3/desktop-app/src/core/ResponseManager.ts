import { EventEmitter } from 'events';
import {
  ApiResponse,
  RequestConfig,
  RetryConfig,
  ProgressInfo,
  WebSocketMessage,
  ErrorInfo
} from '../types/response.types';

export class ResponseManager extends EventEmitter {
  private static instance: ResponseManager;
  private activeRequests: Map<string, RequestConfig> = new Map();
  private requestHistory: Array<{ config: RequestConfig; response: ApiResponse; timestamp: number }> = [];
  private retryConfigs: Map<string, Partial<RetryConfig>> = new Map();
  private webSocket: WebSocket | null = null;
  private webSocketUrl: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  private constructor() {
    super();
    this.loadPersistedState();
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
      this.persistState();

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
      this.persistState();

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
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), config.timeout || 30000);

    try {
      const fetchConfig: RequestInit = {
        method: config.method,
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': requestId,
          ...config.headers
        },
        signal: controller.signal
      };

      if (config.data && ['POST', 'PUT', 'PATCH'].includes(config.method)) {
        fetchConfig.body = JSON.stringify(config.data);
      }

      const response = await fetch(config.url, fetchConfig);
      clearTimeout(timeoutId);

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
      clearTimeout(timeoutId);
      
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
   * Conecta al WebSocket para actualizaciones en tiempo real
   */
  public connectWebSocket(url: string): void {
    this.webSocketUrl = url;
    this.establishWebSocketConnection();
  }

  /**
   * Establece la conexión WebSocket
   */
  private establishWebSocketConnection(): void {
    if (!this.webSocketUrl) return;

    try {
      this.webSocket = new WebSocket(this.webSocketUrl);

      this.webSocket.onopen = () => {
        console.log('WebSocket conectado');
        this.reconnectAttempts = 0;
        this.emit('websocket:connected');
      };

      this.webSocket.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.emit('websocket:message', message);
          
          // Procesar mensaje según el tipo
          this.processWebSocketMessage(message);
        } catch (error) {
          console.error('Error procesando mensaje WebSocket:', error);
        }
      };

      this.webSocket.onclose = () => {
        console.log('WebSocket desconectado');
        this.emit('websocket:disconnected');
        this.handleWebSocketReconnect();
      };

      this.webSocket.onerror = (error) => {
        console.error('Error en WebSocket:', error);
        this.emit('websocket:error', error);
      };

    } catch (error) {
      console.error('Error estableciendo conexión WebSocket:', error);
      this.handleWebSocketReconnect();
    }
  }

  /**
   * Maneja la reconexión automática del WebSocket
   */
  private handleWebSocketReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Máximo número de intentos de reconexión alcanzado');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * this.reconnectAttempts;
    
    setTimeout(() => {
      console.log(`Intentando reconectar WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      this.establishWebSocketConnection();
    }, delay);
  }

  /**
   * Procesa mensajes WebSocket según su tipo
   */
  private processWebSocketMessage(message: WebSocketMessage): void {
    switch (message.type) {
      case 'progress':
        this.emit('progress:update', message.payload as ProgressInfo);
        break;
      case 'notification':
        this.emit('notification:receive', message.payload);
        break;
      case 'transaction_update':
        this.emit('transaction:update', message.payload);
        break;
      default:
        this.emit('websocket:custom', message);
    }
  }

  /**
   * Envía mensaje por WebSocket
   */
  public sendWebSocketMessage(message: any): void {
    if (this.webSocket && this.webSocket.readyState === WebSocket.OPEN) {
      this.webSocket.send(JSON.stringify(message));
    }
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
   * Persiste el estado en localStorage
   */
  private persistState(): void {
    try {
      const state = {
        requestHistory: this.requestHistory.slice(-50), // Mantener solo las últimas 50
        retryConfigs: Array.from(this.retryConfigs.entries())
      };
      
      localStorage.setItem('responseManager_state', JSON.stringify(state));
    } catch (error) {
      console.error('Error persistiendo estado:', error);
    }
  }

  /**
   * Carga el estado persistido
   */
  private loadPersistedState(): void {
    try {
      const persisted = localStorage.getItem('responseManager_state');
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
  public clearPersistedState(): void {
    localStorage.removeItem('responseManager_state');
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
      averageResponseTime
    };
  }
}