import AsyncStorage from '@react-native-async-storage/async-storage';
import { ErrorInfo, ApiResponse } from '../types/response.types';
import { Alert } from 'react-native';

export interface ErrorHandler {
  (error: ErrorInfo): void;
}

export interface ErrorFilter {
  (error: ErrorInfo): boolean;
}

export interface ErrorMetrics {
  totalErrors: number;
  errorsByType: Record<string, number>;
  errorsByCode: Record<string, number>;
  lastErrorTime: number;
  errorRate: number; // errores por minuto
  criticalErrors: number;
  resolvedErrors: number;
}

export class ErrorHandler {
  private static instance: ErrorHandler;
  private errorHistory: ErrorInfo[] = [];
  private handlers: ErrorHandler[] = [];
  private filters: ErrorFilter[] = [];
  private metrics: ErrorMetrics = {
    totalErrors: 0,
    errorsByType: {},
    errorsByCode: {},
    lastErrorTime: 0,
    errorRate: 0,
    criticalErrors: 0,
    resolvedErrors: 0
  };
  private maxHistorySize = 100;
  private recentErrors: ErrorInfo[] = []; // Para cálculo de rate
  private listeners: Map<string, Function[]> = new Map();

  private constructor() {
    this.setupPeriodicMetricsUpdate();
    this.loadPersistedErrors();
  }

  public static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }

  /**
   * Maneja un error
   */
  public handle(error: Error | ErrorInfo, context?: any): void {
    const errorInfo: ErrorInfo = this.normalizeError(error, context);
    
    // Aplicar filtros
    if (!this.shouldProcessError(errorInfo)) {
      return;
    }

    // Registrar error
    this.recordError(errorInfo);

    // Ejecutar handlers personalizados
    this.executeHandlers(errorInfo);

    // Emitir eventos
    this.emit('error:occurred', errorInfo);
    this.emit(`error:${this.getErrorCategory(errorInfo)}`, errorInfo);

    // Persistir si es crítico
    if (this.isCriticalError(errorInfo)) {
      this.persistError(errorInfo);
      this.showCriticalErrorAlert(errorInfo);
    }

    // Auto-resolución para errores conocidos
    this.attemptAutoResolution(errorInfo);
  }

  /**
   * Maneja errores de API específicamente
   */
  public handleApiError(response: ApiResponse, context?: any): void {
    const errorInfo: ErrorInfo = {
      message: response.error || 'Error de API desconocido',
      code: response.code,
      details: response,
      timestamp: Date.now(),
      requestId: response.requestId,
      context: { ...context, type: 'api_error', response }
    };

    this.handle(errorInfo, context);
  }

  /**
   * Maneja errores de red
   */
  public handleNetworkError(error: Error, context?: any): void {
    const errorInfo: ErrorInfo = {
      message: `Error de red: ${error.message}`,
      code: 'NETWORK_ERROR',
      details: error,
      timestamp: Date.now(),
      stack: error.stack,
      context: { ...context, type: 'network_error' }
    };

    this.handle(errorInfo, context);
  }

  /**
   * Maneja errores de validación
   */
  public handleValidationError(message: string, details?: any, context?: any): void {
    const errorInfo: ErrorInfo = {
      message: `Error de validación: ${message}`,
      code: 'VALIDATION_ERROR',
      details,
      timestamp: Date.now(),
      context: { ...context, type: 'validation_error' }
    };

    this.handle(errorInfo, context);
  }

  /**
   * Registra un error personalizado
   */
  public recordCustomError(
    message: string, 
    code?: string | number, 
    details?: any,
    context?: any
  ): void {
    const errorInfo: ErrorInfo = {
      message,
      code,
      details,
      timestamp: Date.now(),
      context
    };

    this.handle(errorInfo, context);
  }

  /**
   * Reporta un error a un servicio de monitoreo externo
   */
  public async reportToService(errorInfo: ErrorInfo, serviceConfig?: any): Promise<void> {
    try {
      const errorReport = {
        message: errorInfo.message,
        code: errorInfo.code,
        timestamp: errorInfo.timestamp,
        stack: errorInfo.stack,
        context: errorInfo.context,
        deviceInfo: {
          platform: 'react-native',
          // Aquí podrías agregar información del dispositivo
        }
      };

      // En una implementación real, aquí enviarías el error a un servicio como Sentry, Bugsnag, etc.
      console.log('Error reportado al servicio:', errorReport);
      
      // Por ejemplo, con Sentry:
      // Sentry.captureException(errorInfo);

      this.emit('error:reported', { errorInfo, serviceConfig });
    } catch (reportError) {
      console.error('Error reportando a servicio externo:', reportError);
    }
  }

  /**
   * Agrega un handler personalizado
   */
  public addHandler(handler: ErrorHandler): void {
    this.handlers.push(handler);
  }

  /**
   * Remueve un handler
   */
  public removeHandler(handler: ErrorHandler): void {
    const index = this.handlers.indexOf(handler);
    if (index >= 0) {
      this.handlers.splice(index, 1);
    }
  }

  /**
   * Agrega un filtro para errores
   */
  public addFilter(filter: ErrorFilter): void {
    this.filters.push(filter);
  }

  /**
   * Remueve un filtro
   */
  public removeFilter(filter: ErrorFilter): void {
    const index = this.filters.indexOf(filter);
    if (index >= 0) {
      this.filters.splice(index, 1);
    }
  }

  /**
   * Marca un error como resuelto
   */
  public markAsResolved(errorId: string): boolean {
    const errorIndex = this.errorHistory.findIndex(
      e => e.timestamp.toString() === errorId || e.requestId === errorId
    );
    
    if (errorIndex >= 0) {
      const error = this.errorHistory[errorIndex];
      error.details = { ...error.details, resolved: true, resolvedAt: Date.now() };
      this.metrics.resolvedErrors++;
      
      this.emit('error:resolved', { error, errorId });
      return true;
    }
    
    return false;
  }

  /**
   * Obtiene el historial de errores
   */
  public getErrorHistory(limit = 50): ErrorInfo[] {
    return this.errorHistory.slice(-limit);
  }

  /**
   * Obtiene errores por tipo
   */
  public getErrorsByType(type: string): ErrorInfo[] {
    return this.errorHistory.filter(error => 
      this.getErrorCategory(error) === type
    );
  }

  /**
   * Obtiene errores recientes (últimos N minutos)
   */
  public getRecentErrors(minutes = 60): ErrorInfo[] {
    const cutoff = Date.now() - (minutes * 60 * 1000);
    return this.errorHistory.filter(error => error.timestamp > cutoff);
  }

  /**
   * Obtiene errores críticos no resueltos
   */
  public getCriticalUnresolvedErrors(): ErrorInfo[] {
    return this.errorHistory.filter(error => 
      this.isCriticalError(error) && !error.details?.resolved
    );
  }

  /**
   * Limpia el historial de errores
   */
  public async clearHistory(): Promise<void> {
    this.errorHistory = [];
    this.recentErrors = [];
    this.metrics.totalErrors = 0;
    this.metrics.errorsByType = {};
    this.metrics.errorsByCode = {};
    this.metrics.criticalErrors = 0;
    this.metrics.resolvedErrors = 0;
    
    await AsyncStorage.removeItem('error_handler_history');
    this.emit('history:cleared');
  }

  /**
   * Obtiene métricas de errores
   */
  public getMetrics(): ErrorMetrics {
    return { ...this.metrics };
  }

  /**
   * Normaliza diferentes tipos de errores a ErrorInfo
   */
  private normalizeError(error: Error | ErrorInfo, context?: any): ErrorInfo {
    if ('timestamp' in error) {
      return error as ErrorInfo;
    }

    return {
      message: error.message,
      stack: error.stack,
      timestamp: Date.now(),
      context
    };
  }

  /**
   * Determina si se debe procesar el error
   */
  private shouldProcessError(errorInfo: ErrorInfo): boolean {
    // Aplicar filtros
    for (const filter of this.filters) {
      if (!filter(errorInfo)) {
        return false;
      }
    }
    return true;
  }

  /**
   * Registra el error en el historial
   */
  private recordError(errorInfo: ErrorInfo): void {
    // Agregar al historial principal
    this.errorHistory.push(errorInfo);
    
    // Agregar a errores recientes para rate calculation
    this.recentErrors.push(errorInfo);
    
    // Mantener tamaño máximo
    if (this.errorHistory.length > this.maxHistorySize) {
      this.errorHistory = this.errorHistory.slice(-this.maxHistorySize);
    }
    
    // Limpiar errores antiguos de recentErrors (más de 1 hora)
    const oneHourAgo = Date.now() - 60 * 60 * 1000;
    this.recentErrors = this.recentErrors.filter(e => e.timestamp > oneHourAgo);

    // Actualizar métricas
    this.updateMetrics(errorInfo);
  }

  /**
   * Actualiza las métricas de errores
   */
  private updateMetrics(errorInfo: ErrorInfo): void {
    this.metrics.totalErrors++;
    this.metrics.lastErrorTime = errorInfo.timestamp;

    const category = this.getErrorCategory(errorInfo);
    this.metrics.errorsByType[category] = (this.metrics.errorsByType[category] || 0) + 1;

    if (errorInfo.code) {
      const codeStr = String(errorInfo.code);
      this.metrics.errorsByCode[codeStr] = (this.metrics.errorsByCode[codeStr] || 0) + 1;
    }

    // Contar errores críticos
    if (this.isCriticalError(errorInfo)) {
      this.metrics.criticalErrors++;
    }

    // Calcular tasa de errores
    this.calculateErrorRate();
  }

  /**
   * Calcula la tasa de errores
   */
  private calculateErrorRate(): void {
    const now = Date.now();
    const recentCount = this.recentErrors.length;
    const timeSpanMinutes = recentCount > 0 ? 
      (now - this.recentErrors[0].timestamp) / (60 * 1000) : 1;
    
    this.metrics.errorRate = timeSpanMinutes > 0 ? recentCount / timeSpanMinutes : 0;
  }

  /**
   * Ejecuta todos los handlers personalizados
   */
  private executeHandlers(errorInfo: ErrorInfo): void {
    this.handlers.forEach(handler => {
      try {
        handler(errorInfo);
      } catch (handlerError) {
        console.error('Error en handler personalizado:', handlerError);
      }
    });
  }

  /**
   * Obtiene la categoría del error
   */
  private getErrorCategory(errorInfo: ErrorInfo): string {
    if (errorInfo.details?.type) {
      return errorInfo.details.type;
    }

    if (errorInfo.code) {
      const code = String(errorInfo.code);
      if (code.startsWith('4')) return 'client_error';
      if (code.startsWith('5')) return 'server_error';
      if (code === 'NETWORK_ERROR') return 'network_error';
      if (code === 'VALIDATION_ERROR') return 'validation_error';
    }

    if (errorInfo.message.includes('network') || errorInfo.message.includes('fetch')) {
      return 'network_error';
    }

    if (errorInfo.message.includes('validation') || errorInfo.message.includes('invalid')) {
      return 'validation_error';
    }

    return 'unknown_error';
  }

  /**
   * Determina si es un error crítico
   */
  private isCriticalError(errorInfo: ErrorInfo): boolean {
    const criticalCodes = ['500', '502', '503', 'FATAL_ERROR', 'CRITICAL_ERROR'];
    return criticalCodes.includes(String(errorInfo.code)) || 
           errorInfo.message.toLowerCase().includes('fatal');
  }

  /**
   * Muestra alerta para errores críticos
   */
  private showCriticalErrorAlert(errorInfo: ErrorInfo): void {
    Alert.alert(
      'Error Crítico',
      errorInfo.message,
      [
        {
          text: 'Reportar',
          onPress: () => this.reportToService(errorInfo)
        },
        {
          text: 'Cerrar',
          style: 'cancel'
        }
      ]
    );
  }

  /**
   * Persiste errores críticos
   */
  private async persistError(errorInfo: ErrorInfo): Promise<void> {
    try {
      const persisted = await this.getPersistedErrors();
      persisted[errorInfo.timestamp] = errorInfo;
      
      // Mantener solo los últimos 10 errores críticos
      const sortedPersisted = Object.entries(persisted)
        .sort(([a], [b]) => Number(b) - Number(a))
        .slice(0, 10);
      
      await AsyncStorage.setItem('error_handler_critical', JSON.stringify(
        Object.fromEntries(sortedPersisted)
      ));
    } catch (error) {
      console.error('Error persistiendo error crítico:', error);
    }
  }

  /**
   * Obtiene errores persistidos
   */
  private async getPersistedErrors(): Promise<Record<string, ErrorInfo>> {
    try {
      const stored = await AsyncStorage.getItem('error_handler_critical');
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error('Error cargando errores persistidos:', error);
      return {};
    }
  }

  /**
   * Carga errores persistidos
   */
  private async loadPersistedErrors(): Promise<void> {
    try {
      const criticalErrors = await this.getPersistedErrors();
      Object.values(criticalErrors).forEach(errorInfo => {
        this.errorHistory.push(errorInfo);
      });
    } catch (error) {
      console.error('Error cargando errores persistidos:', error);
    }
  }

  /**
   * Intenta auto-resolución para errores conocidos
   */
  private attemptAutoResolution(errorInfo: ErrorInfo): void {
    // Auto-reconexión para errores de red
    if (this.getErrorCategory(errorInfo) === 'network_error') {
      this.emit('error:auto_retry', errorInfo);
    }

    // Auto-refresh para errores de API 5xx
    if (errorInfo.code && String(errorInfo.code).startsWith('5')) {
      setTimeout(() => {
        this.emit('error:auto_refresh', errorInfo);
      }, 5000);
    }
  }

  /**
   * Configura actualización periódica de métricas
   */
  private setupPeriodicMetricsUpdate(): void {
    setInterval(() => {
      this.calculateErrorRate();
      this.emit('metrics:updated', this.metrics);
    }, 60000); // Cada minuto
  }

  /**
   * Obtiene estadísticas de errores
   */
  public getErrorStats(): {
    total: number;
    byType: Record<string, number>;
    byCode: Record<string, number>;
    recent: number;
    rate: number;
    critical: number;
    resolved: number;
    trend: 'increasing' | 'decreasing' | 'stable';
  } {
    const recentErrors = this.getRecentErrors(60);
    const previousErrors = this.getRecentErrors(120);
    
    let trend: 'increasing' | 'decreasing' | 'stable' = 'stable';
    if (recentErrors.length > previousErrors.length * 1.2) {
      trend = 'increasing';
    } else if (recentErrors.length < previousErrors.length * 0.8) {
      trend = 'decreasing';
    }

    return {
      total: this.metrics.totalErrors,
      byType: { ...this.metrics.errorsByType },
      byCode: { ...this.metrics.errorsByCode },
      recent: recentErrors.length,
      rate: this.metrics.errorRate,
      critical: this.metrics.criticalErrors,
      resolved: this.metrics.resolvedErrors,
      trend
    };
  }

  /**
   * Exporta errores para debugging
   */
  public exportErrors(): string {
    return JSON.stringify({
      errors: this.errorHistory,
      metrics: this.metrics,
      exportedAt: new Date().toISOString()
    }, null, 2);
  }

  /**
   * Limpia errores persistidos
   */
  public async clearPersistedErrors(): Promise<void> {
    await AsyncStorage.removeItem('error_handler_critical');
    this.emit('persisted:cleared');
  }

  /**
   * Event emitter methods
   */
  private on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  private off(event: string, callback: Function): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      const index = eventListeners.indexOf(callback);
      if (index >= 0) {
        eventListeners.splice(index, 1);
      }
    }
  }

  private emit(event: string, ...args: any[]): void {
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