// Tipos para el manejo de respuestas asíncronas en React Native

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  code?: number;
  timestamp: number;
  requestId: string;
}

export interface RequestConfig {
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  data?: any;
  headers?: Record<string, string>;
  timeout?: number;
  retryCount?: number;
  retryDelay?: number;
}

export interface RetryConfig {
  maxRetries: number;
  retryDelay: number;
  backoffMultiplier: number;
  maxRetryDelay: number;
  retryableStatuses: number[];
}

export interface ProgressInfo {
  percentage: number;
  loaded: number;
  total: number;
  speed?: number;
  eta?: number;
  message?: string;
}

export interface NotificationConfig {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  persistent?: boolean;
  actions?: NotificationAction[];
  vibration?: boolean;
  sound?: boolean;
}

export interface NotificationAction {
  label: string;
  action: () => void;
}

export interface TransactionFlow {
  id: string;
  name: string;
  steps: TransactionStep[];
  currentStep: number;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled' | 'paused';
  createdAt: number;
  updatedAt: number;
  result?: any;
  error?: string;
  backgroundCapable?: boolean; // Permite ejecutarse en segundo plano
}

export interface TransactionStep {
  id: string;
  name: string;
  action: () => Promise<any>;
  rollback?: () => Promise<void>;
  dependencies?: string[];
  timeout?: number;
  retryConfig?: Partial<RetryConfig>;
  backgroundTask?: boolean; // Puede ejecutarse en segundo plano
  networkRequired?: boolean; // Requiere conexión de red
}

export interface StateSnapshot {
  id: string;
  timestamp: number;
  data: any;
  version: number;
}

export interface PushNotification {
  id: string;
  title: string;
  body: string;
  data?: any;
  category?: string;
  priority?: 'low' | 'normal' | 'high';
}

export interface NetworkStatus {
  isConnected: boolean;
  connectionType: 'wifi' | 'cellular' | 'ethernet' | 'vpn' | 'unknown';
  isInternetReachable: boolean;
}

export interface BackgroundTask {
  id: string;
  name: string;
  task: () => Promise<void>;
  interval?: number;
  conditions?: {
    networkRequired?: boolean;
    batteryLevel?: number; // Ejecutar solo si batería > nivel especificado
  };
}

export interface ErrorInfo {
  message: string;
  code?: string | number;
  details?: any;
  timestamp: number;
  requestId?: string;
  stack?: string;
  context?: string;
}

export interface StorageData {
  key: string;
  value: any;
  timestamp: number;
  expiry?: number; // Tiempo en ms antes de expirar
}

export interface AppState {
  isActive: boolean;
  networkStatus: NetworkStatus;
  notifications: NotificationConfig[];
  runningFlows: TransactionFlow[];
  errorCount: number;
  lastActivity: number;
}

export interface SyncConfig {
  autoSync: boolean;
  syncInterval: number; // en ms
  maxRetries: number;
  conflictResolution: 'local' | 'remote' | 'manual';
  backgroundSync: boolean;
}

export interface SyncStatus {
  isSyncing: boolean;
  lastSyncTime: number;
  pendingItems: number;
  conflicts: number;
  errors: string[];
}

// Context API types
export interface AsyncContextValue {
  // Managers
  responseManager: ResponseManager;
  notificationSystem: NotificationSystem;
  stateManager: StateManager;
  errorHandler: ErrorHandler;
  flowManager: TransactionFlowManager;
  
  // State
  isLoading: boolean;
  currentFlows: TransactionFlow[];
  activeNotifications: NotificationConfig[];
  networkStatus: NetworkStatus;
  appState: AppState;
  
  // Actions
  request: <T>(config: RequestConfig, options?: any) => Promise<ApiResponse<T>>;
  executeFlow: (flow: TransactionFlow) => Promise<ApiResponse>;
  showNotification: (notification: Omit<NotificationConfig, 'id'>) => string;
  clearNotifications: () => void;
  syncData: () => Promise<void>;
}

// React Native specific types
export interface ComponentProps {
  children?: React.ReactNode;
  style?: any;
  testID?: string;
}

export interface HookOptions {
  immediate?: boolean;
  persistResults?: boolean;
  showNotifications?: boolean;
  trackErrors?: boolean;
}

export interface ServiceConfig {
  baseURL?: string;
  timeout?: number;
  retryConfig?: Partial<RetryConfig>;
  headers?: Record<string, string>;
  enableOffline?: boolean;
  enableCache?: boolean;
}

// Mobile-specific constants
export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
} as const;

export const NETWORK_TYPES = {
  WIFI: 'wifi',
  CELLULAR: 'cellular',
  ETHERNET: 'ethernet',
  VPN: 'vpn',
  UNKNOWN: 'unknown'
} as const;

export const FLOW_STATUS = {
  PENDING: 'pending',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
  PAUSED: 'paused'
} as const;

export type NotificationType = typeof NOTIFICATION_TYPES[keyof typeof NOTIFICATION_TYPES];
export type NetworkType = typeof NETWORK_TYPES[keyof typeof NETWORK_TYPES];
export type FlowStatus = typeof FLOW_STATUS[keyof typeof FLOW_STATUS];