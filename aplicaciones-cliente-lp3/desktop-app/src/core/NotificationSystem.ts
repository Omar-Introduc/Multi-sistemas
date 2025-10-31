import { EventEmitter } from 'events';
import { NotificationConfig, NotificationAction } from '../types/response.types';

export class NotificationSystem extends EventEmitter {
  private static instance: NotificationSystem;
  private notifications: Map<string, NotificationConfig> = new Map();
  private displayQueue: NotificationConfig[] = [];
  private isProcessingQueue = false;
  private maxVisibleNotifications = 5;
  private defaultDuration = 5000;

  private constructor() {
    super();
    this.loadPersistedNotifications();
  }

  public static getInstance(): NotificationSystem {
    if (!NotificationSystem.instance) {
      NotificationSystem.instance = new NotificationSystem();
    }
    return NotificationSystem.instance;
  }

  /**
   * Muestra una notificación
   */
  public show(notification: Omit<NotificationConfig, 'id'>): string {
    const id = this.generateId();
    const fullNotification: NotificationConfig = {
      ...notification,
      id,
      duration: notification.duration ?? this.defaultDuration,
      persistent: notification.persistent || false
    };

    // Agregar a la cola de visualización
    this.displayQueue.push(fullNotification);
    
    // Procesar cola si no está en proceso
    if (!this.isProcessingQueue) {
      this.processDisplayQueue();
    }

    // Persistir notificación
    this.persistNotification(fullNotification);

    // Emitir evento
    this.emit('notification:added', fullNotification);

    return id;
  }

  /**
   * Muestra notificación de éxito
   */
  public success(title: string, message: string, options?: Partial<NotificationConfig>): string {
    return this.show({
      type: 'success',
      title,
      message,
      ...options
    });
  }

  /**
   * Muestra notificación de error
   */
  public error(title: string, message: string, options?: Partial<NotificationConfig>): string {
    return this.show({
      type: 'error',
      title,
      message,
      persistent: true, // Los errores persisten por defecto
      ...options
    });
  }

  /**
   * Muestra notificación de advertencia
   */
  public warning(title: string, message: string, options?: Partial<NotificationConfig>): string {
    return this.show({
      type: 'warning',
      title,
      message,
      ...options
    });
  }

  /**
   * Muestra notificación informativa
   */
  public info(title: string, message: string, options?: Partial<NotificationConfig>): string {
    return this.show({
      type: 'info',
      title,
      message,
      ...options
    });
  }

  /**
   * Oculta una notificación
   */
  public hide(id: string): void {
    const notification = this.notifications.get(id);
    if (notification) {
      this.notifications.delete(id);
      this.removeFromDisplayQueue(id);
      
      // Emitir evento
      this.emit('notification:hidden', id);
      
      // Limpiar persistencia
      this.unpersistNotification(id);
    }
  }

  /**
   * Oculta todas las notificaciones
   */
  public hideAll(): void {
    const ids = Array.from(this.notifications.keys());
    ids.forEach(id => this.hide(id));
    
    this.displayQueue = [];
    this.emit('notification:hidden:all');
  }

  /**
   * Actualiza una notificación existente
   */
  public update(id: string, updates: Partial<NotificationConfig>): void {
    const notification = this.notifications.get(id);
    if (notification) {
      const updated = { ...notification, ...updates };
      this.notifications.set(id, updated);
      
      // Emitir evento
      this.emit('notification:updated', updated);
      
      // Actualizar persistencia
      this.persistNotification(updated);
    }
  }

  /**
   * Procesa la cola de notificaciones para mostrar
   */
  private async processDisplayQueue(): Promise<void> {
    this.isProcessingQueue = true;

    while (this.displayQueue.length > 0) {
      const notification = this.displayQueue.shift()!;
      
      // Verificar límite de notificaciones visibles
      const visibleCount = Array.from(this.notifications.values())
        .filter(n => n.id !== notification.id).length;
      
      if (visibleCount >= this.maxVisibleNotifications) {
        // Esperar hasta que se oculte una notificación
        await this.waitForAvailableSlot();
      }

      // Mostrar notificación
      this.notifications.set(notification.id, notification);
      this.emit('notification:display', notification);

      // Configurar auto-ocultado si no es persistente
      if (!notification.persistent && notification.duration) {
        setTimeout(() => {
          this.hide(notification.id);
        }, notification.duration);
      }
    }

    this.isProcessingQueue = false;
  }

  /**
   * Espera a que haya espacio para una nueva notificación
   */
  private waitForAvailableSlot(): Promise<void> {
    return new Promise(resolve => {
      const checkAndResolve = () => {
        const visibleCount = this.notifications.size;
        if (visibleCount < this.maxVisibleNotifications) {
          resolve();
        } else {
          setTimeout(checkAndResolve, 100);
        }
      };
      checkAndResolve();
    });
  }

  /**
   * Remueve notificación de la cola de visualización
   */
  private removeFromDisplayQueue(id: string): void {
    const index = this.displayQueue.findIndex(n => n.id === id);
    if (index >= 0) {
      this.displayQueue.splice(index, 1);
    }
  }

  /**
   * Ejecuta una acción de notificación
   */
  public executeAction(notificationId: string, actionIndex: number): void {
    const notification = this.notifications.get(notificationId);
    if (notification && notification.actions && notification.actions[actionIndex]) {
      try {
        notification.actions[actionIndex].action();
        this.emit('notification:action:executed', {
          notificationId,
          actionIndex,
          action: notification.actions[actionIndex]
        });
      } catch (error) {
        console.error('Error ejecutando acción de notificación:', error);
        this.emit('notification:action:error', {
          notificationId,
          actionIndex,
          error
        });
      }
    }
  }

  /**
   * Obtiene todas las notificaciones activas
   */
  public getActiveNotifications(): NotificationConfig[] {
    return Array.from(this.notifications.values());
  }

  /**
   * Obtiene notificación por ID
   */
  public getNotification(id: string): NotificationConfig | undefined {
    return this.notifications.get(id);
  }

  /**
   * Filtra notificaciones por tipo
   */
  public getNotificationsByType(type: NotificationConfig['type']): NotificationConfig[] {
    return Array.from(this.notifications.values()).filter(n => n.type === type);
  }

  /**
   * Obtiene el conteo de notificaciones por tipo
   */
  public getNotificationCount(): Record<string, number> {
    const counts = {
      success: 0,
      error: 0,
      warning: 0,
      info: 0,
      total: 0
    };

    this.notifications.forEach(notification => {
      counts[notification.type]++;
      counts.total++;
    });

    return counts;
  }

  /**
   * Limpia notificaciones de un tipo específico
   */
  public clearByType(type: NotificationConfig['type']): void {
    const ids = Array.from(this.notifications.entries())
      .filter(([_, notification]) => notification.type === type)
      .map(([id]) => id);

    ids.forEach(id => this.hide(id));
  }

  /**
   * Configura notificaciones batch (múltiples a la vez)
   */
  public showBatch(notifications: Omit<NotificationConfig, 'id'>[]): string[] {
    const ids: string[] = [];
    
    notifications.forEach(notification => {
      ids.push(this.show(notification));
    });

    return ids;
  }

  /**
   * Configura notificaciones con template
   */
  public showTemplate(templateName: string, data: any): string | string[] {
    const templates = this.getNotificationTemplates();
    const template = templates[templateName];
    
    if (!template) {
      throw new Error(`Template de notificación '${templateName}' no encontrado`);
    }

    // Procesar template con datos
    const processed = this.processTemplate(template, data);
    
    // Mostrar notificación procesada
    if (Array.isArray(processed)) {
      return this.showBatch(processed);
    } else {
      return this.show(processed);
    }
  }

  /**
   * Obtiene templates de notificaciones predefinidos
   */
  private getNotificationTemplates(): Record<string, any> {
    return {
      // Template para errores de API
      apiError: {
        type: 'error',
        title: 'Error de Conexión',
        message: 'No se pudo conectar con el servidor. Verifica tu conexión a internet.',
        persistent: true,
        actions: [
          {
            label: 'Reintentar',
            action: () => window.location.reload()
          }
        ]
      },
      
      // Template para éxito de operación
      operationSuccess: {
        type: 'success',
        title: 'Operación Exitosa',
        message: 'La operación se completó correctamente.'
      },
      
      // Template para progreso
      progressUpdate: {
        type: 'info',
        title: 'Procesando...',
        message: 'Por favor espera mientras procesamos tu solicitud.'
      },
      
      // Template para actualización disponible
      updateAvailable: {
        type: 'info',
        title: 'Actualización Disponible',
        message: 'Una nueva versión está disponible.',
        actions: [
          {
            label: 'Actualizar',
            action: () => window.location.reload()
          }
        ]
      }
    };
  }

  /**
   * Procesa un template con datos dinámicos
   */
  private processTemplate(template: any, data: any): any {
    // Reemplazar placeholders en el template
    const processed = JSON.parse(JSON.stringify(template));
    
    const replacePlaceholders = (obj: any): any => {
      if (typeof obj === 'string') {
        return obj.replace(/\{\{(\w+)\}\}/g, (match, key) => {
          return data[key] !== undefined ? String(data[key]) : match;
        });
      } else if (Array.isArray(obj)) {
        return obj.map(replacePlaceholders);
      } else if (typeof obj === 'object' && obj !== null) {
        const result: any = {};
        for (const [key, value] of Object.entries(obj)) {
          result[key] = replacePlaceholders(value);
        }
        return result;
      }
      return obj;
    };

    return replacePlaceholders(processed);
  }

  /**
   * Configura notificaciones con progreso
   */
  public showProgress(title: string, message: string, progress: number): string {
    const id = this.show({
      type: 'info',
      title,
      message: `${message} (${Math.round(progress)}%)`,
      persistent: true
    });

    // Actualizar progreso periódicamente
    const updateProgress = (currentProgress: number) => {
      if (currentProgress >= 100) {
        this.update(id, {
          type: 'success',
          message: `${message} (100%)`,
          persistent: false
        });
        setTimeout(() => this.hide(id), 2000);
      } else {
        this.update(id, {
          message: `${message} (${Math.round(currentProgress)}%)`
        });
      }
    };

    return id;
  }

  /**
   * Persiste una notificación en localStorage
   */
  private persistNotification(notification: NotificationConfig): void {
    try {
      const persisted = this.getPersistedNotifications();
      persisted[notification.id] = notification;
      localStorage.setItem('notification_system', JSON.stringify(persisted));
    } catch (error) {
      console.error('Error persistiendo notificación:', error);
    }
  }

  /**
   * Remueve notificación de persistencia
   */
  private unpersistNotification(id: string): void {
    try {
      const persisted = this.getPersistedNotifications();
      delete persisted[id];
      localStorage.setItem('notification_system', JSON.stringify(persisted));
    } catch (error) {
      console.error('Error removiendo notificación persistida:', error);
    }
  }

  /**
   * Obtiene notificaciones persistidas
   */
  private getPersistedNotifications(): Record<string, NotificationConfig> {
    try {
      const stored = localStorage.getItem('notification_system');
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error('Error cargando notificaciones persistidas:', error);
      return {};
    }
  }

  /**
   * Carga notificaciones persistidas
   */
  private loadPersistedNotifications(): void {
    const persisted = this.getPersistedNotifications();
    
    // Restaurar notificaciones persistentes
    Object.values(persisted).forEach(notification => {
      if (notification.persistent) {
        this.notifications.set(notification.id, notification);
        this.emit('notification:restored', notification);
      }
    });
  }

  /**
   * Limpia todas las notificaciones persistidas
   */
  public clearPersistedNotifications(): void {
    localStorage.removeItem('notification_system');
    this.notifications.clear();
    this.displayQueue = [];
    this.emit('notification:cleared');
  }

  /**
   * Genera un ID único para notificaciones
   */
  private generateId(): string {
    return `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Obtiene estadísticas del sistema de notificaciones
   */
  public getStats(): {
    activeNotifications: number;
    queueLength: number;
    notificationsByType: Record<string, number>;
  } {
    return {
      activeNotifications: this.notifications.size,
      queueLength: this.displayQueue.length,
      notificationsByType: this.getNotificationCount()
    };
  }
}