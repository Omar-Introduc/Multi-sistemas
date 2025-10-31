import { ResponseManager } from './ResponseManager';
import { NotificationSystem } from './NotificationSystem';
import { StateManager } from './StateManager';
import { ErrorHandler } from './ErrorHandler';
import { TransactionFlowManager } from './TransactionFlowManager';
import { ApiResponse, RequestConfig, NotificationConfig, TransactionFlow, ProgressInfo } from '../types/response.types';

export interface AsyncManagerOptions {
  enableNotifications?: boolean;
  enableStatePersistence?: boolean;
  enableErrorTracking?: boolean;
  enableFlowTracking?: boolean;
  webSocketUrl?: string;
  autoRetry?: boolean;
  defaultTimeout?: number;
}

export interface ManagerStats {
  response: any;
  notification: any;
  state: any;
  error: any;
  flow: any;
  uptime: number;
  memoryUsage: number;
}

export class AsyncResponseManager {
  private static instance: AsyncResponseManager;
  
  private responseManager: ResponseManager;
  private notificationSystem: NotificationSystem;
  private stateManager: StateManager;
  private errorHandler: ErrorHandler;
  private flowManager: TransactionFlowManager;
  
  private startTime: number;
  private options: AsyncManagerOptions;

  private constructor(options: AsyncManagerOptions = {}) {
    this.options = {
      enableNotifications: true,
      enableStatePersistence: true,
      enableErrorTracking: true,
      enableFlowTracking: true,
      autoRetry: true,
      defaultTimeout: 30000,
      ...options
    };
    
    this.startTime = Date.now();
    
    // Inicializar managers
    this.responseManager = ResponseManager.getInstance();
    this.notificationSystem = NotificationSystem.getInstance();
    this.stateManager = StateManager.getInstance();
    this.errorHandler = ErrorHandler.getInstance();
    this.flowManager = TransactionFlowManager.getInstance();

    this.initializeEventListeners();
    this.connectWebSocketIfConfigured();
  }

  public static getInstance(options?: AsyncManagerOptions): AsyncResponseManager {
    if (!AsyncResponseManager.instance) {
      AsyncResponseManager.instance = new AsyncResponseManager(options);
    }
    return AsyncResponseManager.instance;
  }

  /**
   * Realiza una petición HTTP completa con todos los sistemas integrados
   */
  public async request<T = any>(
    config: RequestConfig,
    options: {
      showNotification?: boolean;
      persistResult?: boolean;
      trackAsFlow?: boolean;
      context?: any;
    } = {}
  ): Promise<ApiResponse<T>> {
    const requestId = `async_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    try {
      // Mostrar notificación de inicio si está habilitado
      if (this.options.enableNotifications && options.showNotification !== false) {
        this.notificationSystem.info('Solicitud Iniciada', 'Procesando tu solicitud...');
      }

      // Ejecutar petición
      const response = await this.responseManager.request({
        ...config,
        timeout: config.timeout || this.options.defaultTimeout
      });

      // Manejar resultado
      if (response.success) {
        // Éxito
        if (this.options.enableNotifications && options.showNotification !== false) {
          this.notificationSystem.success(
            'Éxito',
            options.context?.successMessage || 'Operación completada exitosamente'
          );
        }

        // Persistir resultado si está habilitado
        if (this.options.enableStatePersistence && options.persistResult) {
          this.stateManager.set(`request_${requestId}`, response.data, {
            persist: true
          });
        }

        // Emitir evento de éxito
        this.emit('request:success', { requestId, response, config });

      } else {
        // Error
        if (this.options.enableErrorTracking) {
          this.errorHandler.handleApiError(response, { requestId, config, ...options.context });
        }

        if (this.options.enableNotifications && options.showNotification !== false) {
          this.notificationSystem.error(
            'Error',
            response.error || 'Error desconocido en la operación'
          );
        }

        // Emitir evento de error
        this.emit('request:error', { requestId, response, config });
      }

      return response;

    } catch (error) {
      // Error no controlado
      if (this.options.enableErrorTracking) {
        this.errorHandler.handleNetworkError(error as Error, { requestId, config, ...options.context });
      }

      if (this.options.enableNotifications && options.showNotification !== false) {
        this.notificationSystem.error(
          'Error Crítico',
          'Error inesperado. Por favor intenta nuevamente.'
        );
      }

      this.emit('request:exception', { requestId, error, config });

      return {
        success: false,
        error: error instanceof Error ? error.message : 'Error desconocido',
        timestamp: Date.now(),
        requestId
      };
    }
  }

  /**
   * Ejecuta un flujo de transacción completo
   */
  public async executeTransactionFlow(
    flow: TransactionFlow,
    options: {
      showProgress?: boolean;
      autoRetry?: boolean;
      context?: any;
    } = {}
  ): Promise<ApiResponse> {
    const flowId = flow.id;

    try {
      // Mostrar notificación de inicio
      if (this.options.enableNotifications && options.showProgress !== false) {
        this.notificationSystem.info(
          'Transacción Iniciada',
          `Ejecutando: ${flow.name}`
        );
      }

      // Configurar listeners de progreso
      this.setupFlowProgressTracking(flowId, options.showProgress !== false);

      // Ejecutar flujo
      const result = await this.flowManager.executeFlow(flow, {
        rollbackOnError: true,
        autoCleanup: true
      });

      // Manejar resultado del flujo
      if (result.success) {
        if (this.options.enableNotifications) {
          this.notificationSystem.success(
            'Transacción Completada',
            `El flujo '${flow.name}' se completó exitosamente`
          );
        }
      } else {
        if (this.options.enableNotifications) {
          this.notificationSystem.error(
            'Transacción Fallida',
            result.error || 'Error desconocido en la transacción'
          );
        }
      }

      return result;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido';
      
      if (this.options.enableErrorTracking) {
        this.errorHandler.recordCustomError(
          `Error en flujo ${flow.name}: ${errorMessage}`,
          'FLOW_ERROR',
          { flowId, flow, error }
        );
      }

      if (this.options.enableNotifications) {
        this.notificationSystem.error(
          'Error en Transacción',
          `Error ejecutando el flujo: ${errorMessage}`
        );
      }

      return {
        success: false,
        error: errorMessage,
        timestamp: Date.now(),
        requestId: flowId
      };
    }
  }

  /**
   * Configura seguimiento de progreso para un flujo
   */
  private setupFlowProgressTracking(flowId: string, showNotifications: boolean): void {
    this.flowManager.on('flow:progress', ({ flow, progress }) => {
      if (showNotifications) {
        this.notificationSystem.update(
          `flow_${flowId}`,
          {
            message: progress.message,
            // Aquí podrías actualizar la notificación existente si tienes su ID
          }
        );
      }

      this.emit('flow:progress', { flowId, progress });
    });

    this.flowManager.on('step:completed', ({ step, progress }) => {
      this.emit('step:progress', { 
        flowId, 
        stepId: step.id, 
        stepName: step.name, 
        progress 
      });
    });
  }

  /**
   * Configura listeners de eventos
   */
  private initializeEventListeners(): void {
    // Response Manager events
    this.responseManager.on('request:retry', ({ requestId, attempt, delay }) => {
      if (this.options.enableNotifications) {
        this.notificationSystem.info(
          'Reintentando',
          `Reintento ${attempt} en ${delay}ms`
        );
      }
      this.emit('request:retry', { requestId, attempt, delay });
    });

    this.responseManager.on('progress:update', (progress: ProgressInfo) => {
      this.emit('progress:update', progress);
    });

    this.responseManager.on('websocket:message', (message) => {
      this.emit('websocket:message', message);
    });

    // Error Handler events
    this.errorHandler.on('error:auto_retry', (errorInfo) => {
      this.emit('error:auto_retry', errorInfo);
    });

    this.errorHandler.on('error:auto_refresh', (errorInfo) => {
      if (this.options.enableNotifications) {
        this.notificationSystem.info(
          'Auto-Actualización',
          'La página se actualizará automáticamente'
        );
      }
    });

    // State Manager events
    this.stateManager.on('state:changed', ({ key, oldValue, newValue }) => {
      this.emit('state:changed', { key, oldValue, newValue });
    });

    this.stateManager.on('state:transaction:failed', ({ error }) => {
      if (this.options.enableErrorTracking) {
        this.errorHandler.recordCustomError(
          'Error en transacción de estado',
          'STATE_TRANSACTION_ERROR',
          { error }
        );
      }
    });

    // Flow Manager events
    this.flowManager.on('flow:started', ({ flow, context }) => {
      this.emit('flow:started', { flow, context });
    });

    this.flowManager.on('flow:completed', ({ flow, results }) => {
      this.emit('flow:completed', { flow, results });
    });

    this.flowManager.on('flow:failed', ({ flow, error }) => {
      this.emit('flow:failed', { flow, error });
    });
  }

  /**
   * Conecta al WebSocket si está configurado
   */
  private connectWebSocketIfConfigured(): void {
    if (this.options.webSocketUrl) {
      this.responseManager.connectWebSocket(this.options.webSocketUrl);
    }
  }

  /**
   * Configura notificaciones personalizadas
   */
  public configureNotifications(notifications: Record<string, Partial<NotificationConfig>>): void {
    // Los templates se configuran en el NotificationSystem
    // Esta es una interfaz para configuración global
    Object.entries(notifications).forEach(([name, config]) => {
      // Aquí podrías almacenar configuraciones personalizadas
      this.stateManager.set(`notification_template_${name}`, config, {
        persist: true
      });
    });
  }

  /**
   * Configura estrategias de retry personalizadas
   */
  public configureRetryStrategy(url: string, config: any): void {
    this.responseManager.setRetryConfig(url, config);
  }

  /**
   * Obtiene estadísticas consolidadas
   */
  public getStats(): ManagerStats {
    return {
      response: this.responseManager.getStats(),
      notification: this.notificationSystem.getStats(),
      state: this.stateManager.getStats(),
      error: this.errorHandler.getMetrics(),
      flow: this.flowManager.getFlowStats(),
      uptime: Date.now() - this.startTime,
      memoryUsage: this.getMemoryUsage()
    };
  }

  /**
   * Obtiene uso de memoria aproximado
   */
  private getMemoryUsage(): number {
    try {
      // @ts-ignore - performance.memory es específico de Chrome
      if (performance.memory) {
        // @ts-ignore
        return performance.memory.usedJSHeapSize;
      }
    } catch (error) {
      // Ignorar si no está disponible
    }
    return 0;
  }

  /**
   * Limpia todos los recursos
   */
  public cleanup(): void {
    // Limpiar managers
    this.responseManager.cancelAllRequests();
    this.notificationSystem.clearPersistedNotifications();
    this.stateManager.clearPersistedState();
    this.errorHandler.clearHistory();
    this.flowManager.clearHistory();

    // Emitir evento de cleanup
    this.emit('manager:cleanup', { duration: Date.now() - this.startTime });
  }

  /**
   * Resetea el manager a estado inicial
   */
  public reset(): void {
    this.cleanup();
    this.startTime = Date.now();
    
    // Emitir evento de reset
    this.emit('manager:reset', { timestamp: this.startTime });
  }

  /**
   * Exporta toda la información para debugging
   */
  public exportDebugInfo(): string {
    return JSON.stringify({
      stats: this.getStats(),
      timestamp: new Date().toISOString(),
      uptime: Date.now() - this.startTime,
      options: this.options
    }, null, 2);
  }

  /**
   * Métodos de acceso directo a managers (para casos avanzados)
   */
  public get response(): ResponseManager {
    return this.responseManager;
  }

  public get notifications(): NotificationSystem {
    return this.notificationSystem;
  }

  public get state(): StateManager {
    return this.stateManager;
  }

  public get errors(): ErrorHandler {
    return this.errorHandler;
  }

  public get flows(): TransactionFlowManager {
    return this.flowManager;
  }

  // Métodos de EventEmitter
  public on(event: string, listener: (...args: any[]) => void): this {
    // Implementación mínima de EventEmitter
    if (!this.listeners) {
      // @ts-ignore
      this.listeners = new Map();
    }
    // @ts-ignore
    const eventListeners = this.listeners.get(event) || [];
    eventListeners.push(listener);
    // @ts-ignore
    this.listeners.set(event, eventListeners);
    return this;
  }

  public off(event: string, listener: (...args: any[]) => void): this {
    // @ts-ignore
    const eventListeners = this.listeners?.get(event) || [];
    const index = eventListeners.indexOf(listener);
    if (index >= 0) {
      eventListeners.splice(index, 1);
      // @ts-ignore
      this.listeners.set(event, eventListeners);
    }
    return this;
  }

  public emit(event: string, ...args: any[]): boolean {
    // @ts-ignore
    const eventListeners = this.listeners?.get(event) || [];
    eventListeners.forEach(listener => {
      try {
        listener(...args);
      } catch (error) {
        console.error(`Error en listener de evento ${event}:`, error);
      }
    });
    return eventListeners.length > 0;
  }

  private listeners?: Map<string, any[]>;
}