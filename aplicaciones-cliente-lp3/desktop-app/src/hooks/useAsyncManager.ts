import { useState, useEffect, useCallback, useRef } from 'react';
import { AsyncResponseManager } from '../core/AsyncResponseManager';
import { ApiResponse, ProgressInfo, TransactionFlow, RequestConfig } from '../types/response.types';

interface UseAsyncRequestOptions {
  immediate?: boolean;
  showNotification?: boolean;
  persistResult?: boolean;
  context?: any;
}

interface UseAsyncRequestReturn<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  request: (config: RequestConfig) => Promise<ApiResponse<T>>;
  reset: () => void;
  retry: () => Promise<void>;
}

export function useAsyncRequest<T = any>(
  options: UseAsyncRequestOptions = {}
): UseAsyncRequestReturn<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const manager = AsyncResponseManager.getInstance();
  const lastRequestRef = useRef<RequestConfig | null>(null);

  const request = useCallback(async (config: RequestConfig): Promise<ApiResponse<T>> => {
    setLoading(true);
    setError(null);
    lastRequestRef.current = config;

    try {
      const response = await manager.request<T>(config, {
        showNotification: options.showNotification,
        persistResult: options.persistResult,
        context: options.context
      });

      if (response.success) {
        setData(response.data || null);
        setError(null);
      } else {
        setError(response.error || 'Error desconocido');
        setData(null);
      }

      return response;

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      setData(null);
      
      return {
        success: false,
        error: errorMessage,
        timestamp: Date.now(),
        requestId: `error_${Date.now()}`
      };
    } finally {
      setLoading(false);
    }
  }, [manager, options.showNotification, options.persistResult, options.context]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
    lastRequestRef.current = null;
  }, []);

  const retry = useCallback(async () => {
    if (lastRequestRef.current) {
      await request(lastRequestRef.current);
    }
  }, [request]);

  // Ejecutar automáticamente si está habilitado
  useEffect(() => {
    if (options.immediate && lastRequestRef.current) {
      request(lastRequestRef.current);
    }
  }, [options.immediate, request]);

  return {
    data,
    loading,
    error,
    request,
    reset,
    retry
  };
}

// Hook para transacciones
interface UseTransactionFlowOptions {
  showProgress?: boolean;
  autoStart?: boolean;
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
}

interface UseTransactionFlowReturn {
  executing: boolean;
  progress: number;
  currentStep: string | null;
  error: string | null;
  result: any;
  startFlow: (flow: TransactionFlow) => Promise<void>;
  cancelFlow: () => void;
}

export function useTransactionFlow(
  options: UseTransactionFlowOptions = {}
): UseTransactionFlowReturn {
  const [executing, setExecuting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  
  const manager = AsyncResponseManager.getInstance();
  const activeFlowRef = useRef<string | null>(null);

  const startFlow = useCallback(async (flow: TransactionFlow) => {
    if (executing) return;

    setExecuting(true);
    setProgress(0);
    setCurrentStep(null);
    setError(null);
    setResult(null);
    activeFlowRef.current = flow.id;

    try {
      const response = await manager.executeTransactionFlow(flow, {
        showProgress: options.showProgress,
        context: { flowId: flow.id }
      });

      if (response.success) {
        setResult(response.data);
        setProgress(100);
        options.onComplete?.(response.data);
      } else {
        setError(response.error || 'Error en transacción');
        options.onError?.(response.error || 'Error en transacción');
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      options.onError?.(errorMessage);
    } finally {
      setExecuting(false);
      activeFlowRef.current = null;
    }
  }, [executing, manager, options]);

  const cancelFlow = useCallback(() => {
    if (activeFlowRef.current) {
      manager.flows.cancelFlow(activeFlowRef.current);
      setExecuting(false);
      setProgress(0);
      setCurrentStep(null);
      activeFlowRef.current = null;
    }
  }, [manager]);

  // Configurar listeners de progreso
  useEffect(() => {
    const handleProgress = (progressInfo: ProgressInfo) => {
      setProgress(progressInfo.percentage);
    };

    const handleStepProgress = ({ stepName }: { flowId: string; stepName: string }) => {
      setCurrentStep(stepName);
    };

    const handleFlowComplete = ({ results }: { flowId: string; results: any }) => {
      setResult(results);
    };

    manager.on('progress:update', handleProgress);
    manager.on('step:progress', handleStepProgress);
    manager.on('flow:completed', handleFlowComplete);

    return () => {
      manager.off('progress:update', handleProgress);
      manager.off('step:progress', handleStepProgress);
      manager.off('flow:completed', handleFlowComplete);
    };
  }, [manager]);

  // Ejecutar automáticamente si está habilitado
  useEffect(() => {
    if (options.autoStart && !executing && !activeFlowRef.current) {
      // Aquí podrías ejecutar un flujo por defecto si está configurado
    }
  }, [options.autoStart, executing]);

  return {
    executing,
    progress,
    currentStep,
    error,
    result,
    startFlow,
    cancelFlow
  };
}

// Hook para notificaciones
interface UseNotificationOptions {
  maxVisible?: number;
  defaultDuration?: number;
}

interface UseNotificationReturn {
  notifications: any[];
  success: (title: string, message: string, options?: any) => string;
  error: (title: string, message: string, options?: any) => string;
  warning: (title: string, message: string, options?: any) => string;
  info: (title: string, message: string, options?: any) => string;
  hide: (id: string) => void;
  hideAll: () => void;
  clear: (type: string) => void;
}

export function useNotification(
  options: UseNotificationOptions = {}
): UseNotificationReturn {
  const [notifications, setNotifications] = useState<any[]>([]);
  
  const manager = AsyncResponseManager.getInstance();

  const updateNotifications = useCallback(() => {
    const activeNotifications = manager.notifications.getActiveNotifications();
    setNotifications(activeNotifications);
  }, [manager]);

  useEffect(() => {
    updateNotifications();

    const handleNotificationAdded = () => updateNotifications();
    const handleNotificationHidden = () => updateNotifications();
    const handleNotificationUpdated = () => updateNotifications();

    manager.notifications.on('notification:added', handleNotificationAdded);
    manager.notifications.on('notification:hidden', handleNotificationHidden);
    manager.notifications.on('notification:updated', handleNotificationUpdated);

    return () => {
      manager.notifications.off('notification:added', handleNotificationAdded);
      manager.notifications.off('notification:hidden', handleNotificationHidden);
      manager.notifications.off('notification:updated', handleNotificationUpdated);
    };
  }, [manager, updateNotifications]);

  const success = useCallback((title: string, message: string, config = {}) => {
    return manager.notifications.success(title, message, config);
  }, [manager]);

  const error = useCallback((title: string, message: string, config = {}) => {
    return manager.notifications.error(title, message, config);
  }, [manager]);

  const warning = useCallback((title: string, message: string, config = {}) => {
    return manager.notifications.warning(title, message, config);
  }, [manager]);

  const info = useCallback((title: string, message: string, config = {}) => {
    return manager.notifications.info(title, message, config);
  }, [manager]);

  const hide = useCallback((id: string) => {
    manager.notifications.hide(id);
  }, [manager]);

  const hideAll = useCallback(() => {
    manager.notifications.hideAll();
  }, [manager]);

  const clear = useCallback((type: string) => {
    manager.notifications.clearByType(type);
  }, [manager]);

  return {
    notifications,
    success,
    error,
    warning,
    info,
    hide,
    hideAll,
    clear
  };
}

// Hook para estado global
interface UseStateManagerOptions {
  persist?: boolean;
}

interface UseStateManagerReturn<T> {
  value: T | undefined;
  setValue: (value: T) => void;
  updateValue: (updater: (current: T | undefined) => T) => void;
  removeValue: () => void;
  subscribe: (callback: (value: T | undefined) => void) => () => void;
}

export function useStateManager<T = any>(
  key: string,
  defaultValue?: T,
  options: UseStateManagerOptions = {}
): UseStateManagerReturn<T> {
  const [value, setValueState] = useState<T | undefined>(
    () => AsyncResponseManager.getInstance().state.get(key, defaultValue)
  );

  const manager = AsyncResponseManager.getInstance();

  const setValue = useCallback((newValue: T) => {
    setValueState(newValue);
    manager.state.set(key, newValue, { persist: options.persist });
  }, [key, manager, options.persist]);

  const updateValue = useCallback((updater: (current: T | undefined) => T) => {
    const currentValue = manager.state.get(key);
    const newValue = updater(currentValue);
    setValue(newValue);
  }, [key, manager]);

  const removeValue = useCallback(() => {
    setValueState(undefined);
    manager.state.remove(key);
  }, [key, manager]);

  const subscribe = useCallback((callback: (value: T | undefined) => void) => {
    return manager.state.subscribe(key, callback);
  }, [key, manager]);

  // Sincronizar con cambios externos
  useEffect(() => {
    const unsubscribe = manager.state.subscribe(key, (newValue) => {
      setValueState(newValue);
    });

    return unsubscribe;
  }, [key, manager]);

  return {
    value,
    setValue,
    updateValue,
    removeValue,
    subscribe
  };
}

// Hook para errores
interface UseErrorHandlerReturn {
  errors: any[];
  clearErrors: () => void;
  handleError: (error: Error | string, context?: any) => void;
  handleApiError: (response: ApiResponse, context?: any) => void;
  errorStats: any;
}

export function useErrorHandler(): UseErrorHandlerReturn {
  const [errors, setErrors] = useState<any[]>([]);
  
  const manager = AsyncResponseManager.getInstance();

  const updateErrors = useCallback(() => {
    const recentErrors = manager.errors.getErrorHistory(10);
    setErrors(recentErrors);
  }, [manager]);

  useEffect(() => {
    updateErrors();

    const handleError = () => updateErrors();

    manager.errors.on('error:occurred', handleError);
    manager.errors.on('history:cleared', handleError);

    return () => {
      manager.errors.off('error:occurred', handleError);
      manager.errors.off('history:cleared', handleError);
    };
  }, [manager, updateErrors]);

  const clearErrors = useCallback(() => {
    manager.errors.clearHistory();
  }, [manager]);

  const handleError = useCallback((error: Error | string, context?: any) => {
    const errorInfo = typeof error === 'string' 
      ? { message: error, timestamp: Date.now() }
      : { 
          message: error.message, 
          stack: error.stack, 
          timestamp: Date.now() 
        };
    
    manager.errors.handle(errorInfo as any, context);
  }, [manager]);

  const handleApiError = useCallback((response: ApiResponse, context?: any) => {
    manager.errors.handleApiError(response, context);
  }, [manager]);

  return {
    errors,
    clearErrors,
    handleError,
    handleApiError,
    errorStats: manager.errors.getMetrics()
  };
}