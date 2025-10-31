import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { AsyncResponseManager } from '../core/AsyncResponseManager';
import { 
  TransactionFlow, 
  NotificationConfig, 
  NetworkStatus, 
  AppState,
  AsyncContextValue 
} from '../types/response.types';

// Estado inicial
interface AsyncState {
  isLoading: boolean;
  currentFlows: TransactionFlow[];
  activeNotifications: NotificationConfig[];
  networkStatus: NetworkStatus;
  appState: AppState;
  error: string | null;
}

const initialState: AsyncState = {
  isLoading: false,
  currentFlows: [],
  activeNotifications: [],
  networkStatus: {
    isConnected: true,
    connectionType: 'unknown',
    isInternetReachable: true
  },
  appState: {
    isActive: true,
    networkStatus: {
      isConnected: true,
      connectionType: 'unknown',
      isInternetReachable: true
    },
    notifications: [],
    runningFlows: [],
    errorCount: 0,
    lastActivity: Date.now()
  },
  error: null
};

// Tipos de acciones
type AsyncAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'ADD_NOTIFICATION'; payload: NotificationConfig }
  | { type: 'REMOVE_NOTIFICATION'; payload: string }
  | { type: 'CLEAR_NOTIFICATIONS' }
  | { type: 'START_FLOW'; payload: TransactionFlow }
  | { type: 'UPDATE_FLOW'; payload: { id: string; updates: Partial<TransactionFlow> } }
  | { type: 'COMPLETE_FLOW'; payload: { id: string; result: any } }
  | { type: 'FAIL_FLOW'; payload: { id: string; error: string } }
  | { type: 'CANCEL_FLOW'; payload: string }
  | { type: 'SET_NETWORK_STATUS'; payload: NetworkStatus }
  | { type: 'SET_APP_STATE'; payload: Partial<AppState> }
  | { type: 'RESET_STATE' };

// Reducer
function asyncReducer(state: AsyncState, action: AsyncAction): AsyncState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };

    case 'SET_ERROR':
      return { 
        ...state, 
        error: action.payload,
        appState: {
          ...state.appState,
          errorCount: action.payload ? state.appState.errorCount + 1 : state.appState.errorCount
        }
      };

    case 'ADD_NOTIFICATION':
      return {
        ...state,
        activeNotifications: [...state.activeNotifications, action.payload],
        appState: {
          ...state.appState,
          notifications: [...state.appState.notifications, action.payload]
        }
      };

    case 'REMOVE_NOTIFICATION':
      return {
        ...state,
        activeNotifications: state.activeNotifications.filter(n => n.id !== action.payload),
        appState: {
          ...state.appState,
          notifications: state.appState.notifications.filter(n => n.id !== action.payload)
        }
      };

    case 'CLEAR_NOTIFICATIONS':
      return {
        ...state,
        activeNotifications: [],
        appState: {
          ...state.appState,
          notifications: []
        }
      };

    case 'START_FLOW':
      return {
        ...state,
        currentFlows: [...state.currentFlows, action.payload],
        appState: {
          ...state.appState,
          runningFlows: [...state.appState.runningFlows, action.payload]
        }
      };

    case 'UPDATE_FLOW':
      return {
        ...state,
        currentFlows: state.currentFlows.map(flow =>
          flow.id === action.payload.id
            ? { ...flow, ...action.payload.updates }
            : flow
        ),
        appState: {
          ...state.appState,
          runningFlows: state.appState.runningFlows.map(flow =>
            flow.id === action.payload.id
              ? { ...flow, ...action.payload.updates }
              : flow
          )
        }
      };

    case 'COMPLETE_FLOW':
      return {
        ...state,
        currentFlows: state.currentFlows.filter(flow => flow.id !== action.payload.id),
        appState: {
          ...state.appState,
          runningFlows: state.appState.runningFlows.filter(flow => flow.id !== action.payload.id),
          lastActivity: Date.now()
        }
      };

    case 'FAIL_FLOW':
    case 'CANCEL_FLOW':
      return {
        ...state,
        currentFlows: state.currentFlows.filter(flow => flow.id !== action.payload),
        appState: {
          ...state.appState,
          runningFlows: state.appState.runningFlows.filter(flow => flow.id !== action.payload),
          lastActivity: Date.now()
        }
      };

    case 'SET_NETWORK_STATUS':
      return {
        ...state,
        networkStatus: action.payload,
        appState: {
          ...state.appState,
          networkStatus: action.payload
        }
      };

    case 'SET_APP_STATE':
      return {
        ...state,
        appState: { ...state.appState, ...action.payload }
      };

    case 'RESET_STATE':
      return initialState;

    default:
      return state;
  }
}

// Crear contexto
const AsyncContext = createContext<AsyncContextValue | undefined>(undefined);

// Provider
interface AsyncProviderProps {
  children: ReactNode;
  options?: {
    autoConnect?: boolean;
    persistUserSession?: boolean;
    enableBackgroundSync?: boolean;
  };
}

export const AsyncProvider: React.FC<AsyncProviderProps> = ({ 
  children, 
  options = {} 
}) => {
  const [state, dispatch] = useReducer(asyncReducer, initialState);
  const manager = AsyncResponseManager.getInstance();

  useEffect(() => {
    // Configurar listeners de eventos
    const setupEventListeners = () => {
      // Listeners para notificaciones
      manager.notifications.on('notification:added', (notification: NotificationConfig) => {
        dispatch({ type: 'ADD_NOTIFICATION', payload: notification });
      });

      manager.notifications.on('notification:hidden', (id: string) => {
        dispatch({ type: 'REMOVE_NOTIFICATION', payload: id });
      });

      manager.notifications.on('notification:hidden:all', () => {
        dispatch({ type: 'CLEAR_NOTIFICATIONS' });
      });

      // Listeners para flujos
      manager.flows.on('flow:started', ({ flow }: { flow: TransactionFlow }) => {
        dispatch({ type: 'START_FLOW', payload: flow });
      });

      manager.flows.on('flow:progress', ({ flowId, progress }: any) => {
        dispatch({ 
          type: 'UPDATE_FLOW', 
          payload: { 
            id: flowId, 
            updates: { currentStep: progress.loaded } 
          } 
        });
      });

      manager.flows.on('flow:completed', ({ flow, results }: any) => {
        dispatch({ 
          type: 'COMPLETE_FLOW', 
          payload: { id: flow.id, result: results } 
        });
      });

      manager.flows.on('flow:failed', ({ flow }: any) => {
        dispatch({ 
          type: 'FAIL_FLOW', 
          payload: { id: flow.id, error: flow.error || 'Error desconocido' } 
        });
      });

      manager.flows.on('flow:cancelled', ({ flowId }: any) => {
        dispatch({ type: 'CANCEL_FLOW', payload: flowId });
      });

      // Listeners para red
      manager.on('network:status:changed', (networkStatus: NetworkStatus) => {
        dispatch({ type: 'SET_NETWORK_STATUS', payload: networkStatus });
      });

      // Listeners para errores
      manager.errors.on('error:occurred', (errorInfo: any) => {
        dispatch({ type: 'SET_ERROR', payload: errorInfo.message });
      });

      // Listeners para estado de la app
      manager.on('request:started', () => {
        dispatch({ type: 'SET_LOADING', payload: true });
      });

      manager.on('request:completed', () => {
        dispatch({ type: 'SET_LOADING', payload: false });
      });

      manager.on('request:failed', () => {
        dispatch({ type: 'SET_LOADING', payload: false });
      });
    };

    setupEventListeners();

    // Configurar monitoreo de estado de la app
    const handleAppStateChange = (nextAppState: string) => {
      const isActive = nextAppState === 'active';
      dispatch({ 
        type: 'SET_APP_STATE', 
        payload: { 
          isActive,
          lastActivity: isActive ? Date.now() : state.appState.lastActivity
        } 
      });
    };

    // En React Native, usarías AppState.addEventListener('change', handleAppStateChange)
    // Por ahora simulamos la funcionalidad
    const appStateInterval = setInterval(() => {
      handleAppStateChange('active');
    }, 30000);

    return () => {
      clearInterval(appStateInterval);
      // Limpiar event listeners si es necesario
    };
  }, []);

  // Funciones del contexto
  const contextValue: AsyncContextValue = {
    // Managers
    responseManager: manager.response,
    notificationSystem: manager.notifications,
    stateManager: manager.state,
    errorHandler: manager.errors,
    flowManager: manager.flows,
    
    // State
    isLoading: state.isLoading,
    currentFlows: state.currentFlows,
    activeNotifications: state.activeNotifications,
    networkStatus: state.networkStatus,
    appState: state.appState,
    
    // Actions
    request: async <T>(config: any, requestOptions?: any): Promise<any> => {
      dispatch({ type: 'SET_LOADING', payload: true });
      try {
        const result = await manager.request<T>(config, requestOptions);
        return result;
      } finally {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    },

    executeFlow: async (flow: TransactionFlow): Promise<any> => {
      return await manager.executeTransactionFlow(flow, { showProgress: true });
    },

    showNotification: (notification: Omit<NotificationConfig, 'id'>): string => {
      return manager.notifications.show(notification);
    },

    clearNotifications: (): void => {
      manager.notifications.hideAll();
      dispatch({ type: 'CLEAR_NOTIFICATIONS' });
    },

    syncData: async (): Promise<void> => {
      await manager.syncOfflineData();
    }
  };

  return (
    <AsyncContext.Provider value={contextValue}>
      {children}
    </AsyncContext.Provider>
  );
};

// Hook personalizado para usar el contexto
export const useAsyncContext = (): AsyncContextValue => {
  const context = useContext(AsyncContext);
  if (context === undefined) {
    throw new Error('useAsyncContext must be used within an AsyncProvider');
  }
  return context;
};

// Hook adicional para estado de loading
export const useAsyncLoading = () => {
  const { isLoading } = useAsyncContext();
  return isLoading;
};

// Hook para notificaciones
export const useAsyncNotifications = () => {
  const { activeNotifications, showNotification, clearNotifications } = useAsyncContext();
  
  return {
    notifications: activeNotifications,
    showSuccess: (title: string, message: string) => showNotification({ type: 'success', title, message }),
    showError: (title: string, message: string) => showNotification({ type: 'error', title, message }),
    showWarning: (title: string, message: string) => showNotification({ type: 'warning', title, message }),
    showInfo: (title: string, message: string) => showNotification({ type: 'info', title, message }),
    clearAll: clearNotifications
  };
};

// Hook para flujos de transacciones
export const useAsyncFlows = () => {
  const { currentFlows, executeFlow } = useAsyncContext();
  
  return {
    flows: currentFlows,
    executeFlow,
    hasRunningFlows: currentFlows.length > 0
  };
};

// Hook para estado de red
export const useAsyncNetwork = () => {
  const { networkStatus, syncData } = useAsyncContext();
  
  return {
    networkStatus,
    isOnline: networkStatus.isConnected,
    isInternetReachable: networkStatus.isInternetReachable,
    connectionType: networkStatus.connectionType,
    syncData
  };
};

// Hook para errores
export const useAsyncErrors = () => {
  const { appState, errorHandler } = useAsyncContext();
  
  return {
    errorCount: appState.errorCount,
    recentErrors: errorHandler.getRecentErrors(10),
    clearErrors: () => errorHandler.clearHistory()
  };
};

// Hook combinado para operaciones asíncronas comunes
export const useAsyncOperations = () => {
  const { request, executeFlow } = useAsyncContext();
  const { showSuccess, showError } = useAsyncNotifications();
  
  const executeRequest = async <T>(
    config: any, 
    options?: { 
      showSuccessMessage?: string; 
      showErrorMessage?: boolean;
      onSuccess?: (data: T) => void;
      onError?: (error: string) => void;
    }
  ): Promise<T | null> => {
    try {
      const response = await request<T>(config);
      
      if (response.success) {
        if (options?.showSuccessMessage) {
          showSuccess('Éxito', options.showSuccessMessage);
        }
        options?.onSuccess?.(response.data!);
        return response.data;
      } else {
        if (options?.showErrorMessage) {
          showError('Error', response.error || 'Error desconocido');
        }
        options?.onError?.(response.error || 'Error desconocido');
        return null;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error inesperado';
      showError('Error', errorMessage);
      options?.onError?.(errorMessage);
      return null;
    }
  };

  const executeTransaction = async (
    flow: TransactionFlow,
    options?: {
      showSuccessMessage?: string;
      showErrorMessage?: boolean;
      onSuccess?: (result: any) => void;
      onError?: (error: string) => void;
    }
  ) => {
    try {
      const response = await executeFlow(flow);
      
      if (response.success) {
        if (options?.showSuccessMessage) {
          showSuccess('Transacción Completada', options.showSuccessMessage);
        }
        options?.onSuccess?.(response.data);
        return response.data;
      } else {
        if (options?.showErrorMessage) {
          showError('Error', response.error || 'Error desconocido');
        }
        options?.onError?.(response.error || 'Error desconocido');
        return null;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error inesperado';
      showError('Error', errorMessage);
      options?.onError?.(errorMessage);
      return null;
    }
  };

  return {
    executeRequest,
    executeTransaction
  };
};