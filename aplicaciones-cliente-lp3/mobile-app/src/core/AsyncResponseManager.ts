import { ResponseManager } from './ResponseManager';
import { NotificationSystem } from './NotificationSystem';
import { StateManager } from './StateManager';
import { ErrorHandler } from './ErrorHandler';
import { TransactionFlowManager } from './TransactionFlowManager';
import { ApiResponse, RequestConfig, NotificationConfig, TransactionFlow, ProgressInfo, NetworkStatus } from '../types/response.types';

export interface AsyncManagerOptions {
  enableNotifications?: boolean;
  enableStatePersistence?: boolean;
  enableErrorTracking?: boolean;
  enableFlowTracking?: boolean;
  autoRetry?: boolean;
  defaultTimeout?: number;
  enableOffline?: boolean;
  enableBackgroundTasks?: boolean;
}

export interface ManagerStats {
  response: any;
  notification: any;
  state: any;
  error: any;
  flow: any;
  network: NetworkStatus;
  uptime: number;
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
  private networkStatus: NetworkStatus = {
    isConnected: true,
    connectionType: 'unknown',
    isInternetReachable: true
  };
  private listeners: Map<string, Function[]> = new Map();

  private constructor(options: AsyncManagerOptions = {}) {
    this.options = {
      enableNotifications: true,
      enableStatePersistence: true,
      enableErrorTracking: true,
      enableFlowTracking: true,
      autoRetry: true,
      defaultTimeout: 30000,
      enableOffline: true,
      enableBackgroundTasks: true,
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
    this.setupNetworkMonitoring();
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
      offlineFallback?: boolean;
    } = {}
  ): Promise<ApiResponse<T>> {
    const requestId = `async_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    try {
      // Verificar conectividad si está habilitado el modo offline
      if (this.options.enableOffline && !this.networkStatus.isConnected) {
        if (options.offlineFallback) {
          return await this.handleOfflineRequest<T>(config, requestId);
        } else {
          const offlineResponse: ApiResponse<T> = {
            success: false,
            error: 'Sin conexión a internet',
            timestamp: Date.now(),
            requestId
          };
          
          if (this.options.enableErrorTracking) {
            this.errorHandler.handleNetworkError(
              new Error('Petición offline bloqueada'),
              { requestId, config, ...options.context }
            );
          }
          
          return offlineResponse;
        }
      }

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
          await this.stateManager.set(`request_${requestId}`, response.data, {
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
   * Maneja peticiones cuando está offline
   */
  private async handleOfflineRequest<T>(
    config: RequestConfig, 
    requestId: string
  ): Promise<ApiResponse<T>> {
    try {
      // Intentar obtener datos cacheados
      const cachedData = await this.stateManager.getAsync(`offline_${config.url}`);
      
      if (cachedData) {
        return {
          success: true,
          data: cachedData,
          message: 'Datos desde caché offline',
          timestamp: Date.now(),
          requestId
        };
      } else {
        // Guardar petición para sync posterior
        await this.stateManager.set(`offline_queue_${requestId}`, {
          config,
          timestamp: Date.now()
        }, { persist: true });

        if (this.options.enableNotifications) {
          this.notificationSystem.info(
            'Modo Offline',
            'Petición guardada para sincronizar cuando恢复es la conexión'
          );
        }

        return {
          success: false,
          error: 'Sin datos en caché y sin conexión',
          timestamp: Date.now(),
          requestId
        };
      }
    } catch (error) {
      return {
        success: false,
        error: 'Error manejando petición offline',
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
      backgroundExecution?: boolean;
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

      // Ejecutar flujo (normal o en segundo plano)
      let result: ApiResponse;
      
      if (options.backgroundExecution && this.options.enableBackgroundTasks) {
        result = await this.flowManager.executeBackgroundFlow(flow, flowId);
      } else {
        result = await this.flowManager.executeFlow(flow, {
          rollbackOnError: true,
          autoCleanup: true,
          backgroundCapable: flow.backgroundCapable
        });
      }

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
        this.notificationSystem.updateProgress(`flow_${flowId}`, progress.percentage);
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
   * Sincroniza datos cuando se recupera la conexión
   */
  public async syncOfflineData(): Promise<void> {
    try {
      if (!this.networkStatus.isConnected) {
        return;
      }

      // Obtener peticiones offline pendientes
      const offlineKeys = await this.stateManager.getAsync('offline_queue_keys', []);
      
      for (const requestId of offlineKeys) {
        const offlineRequest = await this.stateManager.getAsync(`offline_queue_${requestId}`);
        
        if (offlineRequest) {
          try {
            await this.request(offlineRequest.config, {
              showNotification: false,
              context: { source: 'offline_sync' }
            });
            
            // Remover de la cola
            await this.stateManager.remove(`offline_queue_${requestId}`);
          } catch (error) {
            console.error(`Error sincronizando petición ${requestId}:`, error);
          }
        }
      }

      // Limpiar claves de la cola
      await this.stateManager.remove('offline_queue_keys');

      if (this.options.enableNotifications) {
        this.notificationSystem.success(
          'Sincronización Completada',
          'Todos los datos offline han sido sincronizados'
        );
      }

      this.emit('sync:completed', { timestamp: Date.now() });

    } catch (error) {
      console.error('Error sincronizando datos offline:', error);
      
      if (this.options.enableNotifications) {
        this.notificationSystem.error(
          'Error de Sincronización',
          'No se pudieron sincronizar todos los datos offline'
        );
      }
    }
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

    this.responseManager.on('network:status', (status) => {
      this.updateNetworkStatus(status);
    });

    // Error Handler events
    this.errorHandler.on('error:auto_retry', (errorInfo) => {
      this.emit('error:auto_retry', errorInfo);
    });

    this.errorHandler.on('error:auto_refresh', (errorInfo) => {
      if (this.options.enableNotifications) {
        this.notificationSystem.info(
          'Auto-Actualización',
          'La aplicación se actualizará automáticamente'
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
   * Configura monitoreo de red para React Native
   */
  private setupNetworkMonitoring(): void {
    // En React Native, aquí usarías NetInfo o similar
    // Por ahora simulamos la funcionalidad
    
    // Simular cambios de conectividad
    setInterval(() => {
      // En una implementación real, esto vendría de NetInfo
      const isOnline = Math.random() > 0.1; // 90% uptime simulado
      
      if (isOnline !== this.networkStatus.isConnected) {
        this.networkStatus.isConnected = isOnline;
        this.networkStatus.isInternetReachable = isOnline;
        
        this.emit('network:status:changed', this.networkStatus);
        
        if (isOnline) {
          // Recuperó la conexión, intentar sincronizar
          this.syncOfflineData();
        } else {
          // Se perdió la conexión
          if (this.options.enableNotifications) {
            this.notificationSystem.warning(
              'Sin Conexión',
              'Trabajando en modo offline'
            );
          }
        }
      }
    }, 10000); // Verificar cada 10 segundos
  }

  /**
   * Actualiza estado de red
   */
  private updateNetworkStatus(status: any): void {
    this.networkStatus = {
      ...this.networkStatus,
      ...status
    };
    
    this.emit('network:updated', this.networkStatus);
  }

  /**
   * Configura notificaciones personalizadas
   */
  public configureNotifications(notifications: Record<string, Partial<NotificationConfig>>): void {
    Object.entries(notifications).forEach(([name, config]) => {
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
      network: this.networkStatus,
      uptime: Date.now() - this.startTime
    };
  }

  /**
   * Obtiene estado de red
   */
  public getNetworkStatus(): NetworkStatus {
    return { ...this.networkStatus };
  }

  /**
   * Limpia todos los recursos
   */
  public async cleanup(): Promise<void> {
    // Limpiar managers
    this.responseManager.cancelAllRequests();
    await this.notificationSystem.clearPersistedNotifications();
    await this.stateManager.clearPersistedState();
    this.errorHandler.clearHistory();
    this.flowManager.clearHistory();

    // Emitir evento de cleanup
    this.emit('manager:cleanup', { duration: Date.now() - this.startTime });
  }

  /**
   * Resetea el manager a estado inicial
   */
  public async reset(): Promise<void> {
    await this.cleanup();
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
      networkStatus: this.networkStatus,
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