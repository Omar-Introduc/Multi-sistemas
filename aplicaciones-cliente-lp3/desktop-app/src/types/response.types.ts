// Tipos para el manejo de respuestas asíncronas

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
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  createdAt: number;
  updatedAt: number;
  result?: any;
  error?: string;
}

export interface TransactionStep {
  id: string;
  name: string;
  action: () => Promise<any>;
  rollback?: () => Promise<void>;
  dependencies?: string[];
  timeout?: number;
  retryConfig?: Partial<RetryConfig>;
}

export interface StateSnapshot {
  id: string;
  timestamp: number;
  data: any;
  version: number;
}

export interface WebSocketMessage {
  type: string;
  payload: any;
  timestamp: number;
  requestId?: string;
}

export interface ErrorInfo {
  message: string;
  code?: string | number;
  details?: any;
  timestamp: number;
  requestId?: string;
  stack?: string;
}