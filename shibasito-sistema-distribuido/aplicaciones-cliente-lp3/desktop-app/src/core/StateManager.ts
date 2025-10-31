import { EventEmitter } from 'events';
import { StateSnapshot } from '../types/response.types';

export interface StateStore {
  [key: string]: any;
}

export interface StateOptions {
  persist?: boolean;
  version?: number;
  maxHistorySize?: number;
  storageKey?: string;
}

export class StateManager extends EventEmitter {
  private static instance: StateManager;
  private store: StateStore = {};
  private history: StateSnapshot[] = [];
  private options: Map<string, StateOptions> = new Map();
  private maxHistorySize = 50;

  private constructor() {
    super();
    this.loadPersistedState();
  }

  public static getInstance(): StateManager {
    if (!StateManager.instance) {
      StateManager.instance = new StateManager();
    }
    return StateManager.instance;
  }

  /**
   * Establece un valor en el estado
   */
  public set<T>(key: string, value: T, options?: StateOptions): void {
    const oldValue = this.store[key];
    this.store[key] = value;
    
    // Configurar opciones
    if (options) {
      this.options.set(key, {
        persist: options.persist ?? false,
        version: options.version ?? 1,
        maxHistorySize: options.maxHistorySize ?? this.maxHistorySize,
        storageKey: options.storageKey ?? key
      });
    }

    // Crear snapshot para historial
    this.createSnapshot(key, oldValue, value);
    
    // Persistir si está configurado
    this.maybePersist(key);
    
    // Emitir evento de cambio
    this.emit('state:changed', { key, oldValue, newValue: value });
    this.emit(`state:${key}:changed`, { oldValue, newValue: value });
  }

  /**
   * Obtiene un valor del estado
   */
  public get<T>(key: string, defaultValue?: T): T | undefined {
    return this.store[key] !== undefined ? this.store[key] : defaultValue;
  }

  /**
   * Verifica si una clave existe en el estado
   */
  public has(key: string): boolean {
    return key in this.store;
  }

  /**
   * Elimina una clave del estado
   */
  public remove(key: string): boolean {
    if (key in this.store) {
      const oldValue = this.store[key];
      delete this.store[key];
      
      // Remover opciones
      this.options.delete(key);
      
      // Remover del historial
      this.history = this.history.filter(snapshot => snapshot.id !== key);
      
      // Emitir evento
      this.emit('state:removed', { key, oldValue });
      
      return true;
    }
    return false;
  }

  /**
   * Obtiene múltiples valores del estado
   */
  public getMultiple(keys: string[]): Record<string, any> {
    const result: Record<string, any> = {};
    keys.forEach(key => {
      result[key] = this.get(key);
    });
    return result;
  }

  /**
   * Establece múltiples valores en el estado
   */
  public setMultiple(values: Record<string, any>, options?: StateOptions): void {
    Object.entries(values).forEach(([key, value]) => {
      this.set(key, value, options);
    });
  }

  /**
   * Actualiza una clave existente con una función
   */
  public update<T>(key: string, updater: (currentValue: T | undefined) => T): void {
    const currentValue = this.get<T>(key);
    const newValue = updater(currentValue);
    this.set(key, newValue);
  }

  /**
   * Merges un objeto con una clave existente
   */
  public merge(key: string, value: any): void {
    this.update(key, (currentValue: any) => {
      if (typeof currentValue === 'object' && typeof value === 'object') {
        return { ...currentValue, ...value };
      }
      return value;
    });
  }

  /**
   * Limpia todo el estado
   */
  public clear(): void {
    const oldStore = { ...this.store };
    this.store = {};
    this.history = [];
    
    this.emit('state:cleared', { oldStore });
  }

  /**
   * Obtiene todo el estado
   */
  public getAll(): StateStore {
    return { ...this.store };
  }

  /**
   * Obtiene el historial de una clave
   */
  public getHistory(key: string, limit = 10): StateSnapshot[] {
    return this.history
      .filter(snapshot => snapshot.id === key)
      .slice(-limit);
  }

  /**
   * Restaura una versión anterior del estado
   */
  public restore(key: string, timestamp: number): boolean {
    const snapshot = this.history.find(
      s => s.id === key && s.timestamp === timestamp
    );
    
    if (snapshot) {
      this.set(key, snapshot.data);
      this.emit('state:restored', { key, timestamp, value: snapshot.data });
      return true;
    }
    
    return false;
  }

  /**
   * Obtiene la versión más reciente del estado
   */
  public getLatestVersion(key: string): StateSnapshot | null {
    const snapshots = this.getHistory(key, 1);
    return snapshots.length > 0 ? snapshots[0] : null;
  }

  /**
   * Obtiene todos los snapshots de una clave con timestamps específicos
   */
  public getVersions(key: string): Array<{ timestamp: number; data: any; version: number }> {
    return this.history
      .filter(snapshot => snapshot.id === key)
      .map(snapshot => ({
        timestamp: snapshot.timestamp,
        data: snapshot.data,
        version: snapshot.version
      }));
  }

  /**
   * Suscribe a cambios en una clave específica
   */
  public subscribe(key: string, callback: (value: any, oldValue: any) => void): () => void {
    const eventName = `state:${key}:changed`;
    this.on(eventName, callback);
    
    // Retornar función para desuscribirse
    return () => {
      this.off(eventName, callback);
    };
  }

  /**
   * Suscribe a todos los cambios de estado
   */
  public subscribeAll(callback: (change: { key: string; oldValue: any; newValue: any }) => void): () => void {
    this.on('state:changed', callback);
    
    return () => {
      this.off('state:changed', callback);
    };
  }

  /**
   * Transacciones atómicas de estado
   */
  public transaction(callback: (state: StateManager) => void): void {
    const backup = { ...this.store };
    const backupHistory = [...this.history];
    
    try {
      callback(this);
      this.emit('state:transaction:completed');
    } catch (error) {
      // Restaurar estado en caso de error
      this.store = backup;
      this.history = backupHistory;
      this.emit('state:transaction:failed', { error, backup });
      throw error;
    }
  }

  /**
   * Calcula la diferencia entre dos estados
   */
  public diff(oldState: StateStore, newState: StateStore): {
    added: Record<string, any>;
    removed: Record<string, any>;
    changed: Record<string, { old: any; new: any }>;
  } {
    const added: Record<string, any> = {};
    const removed: Record<string, any> = {};
    const changed: Record<string, { old: any; new: any }> = {};

    // Encontrar cambios
    const allKeys = new Set([...Object.keys(oldState), ...Object.keys(newState)]);
    
    allKeys.forEach(key => {
      const oldVal = oldState[key];
      const newVal = newState[key];
      
      if (oldVal === undefined && newVal !== undefined) {
        added[key] = newVal;
      } else if (oldVal !== undefined && newVal === undefined) {
        removed[key] = oldVal;
      } else if (JSON.stringify(oldVal) !== JSON.stringify(newVal)) {
        changed[key] = { old: oldVal, new: newVal };
      }
    });

    return { added, removed, changed };
  }

  /**
   * Crea un snapshot del estado actual
   */
  public createSnapshot(key: string, oldValue: any, newValue: any): void {
    const config = this.options.get(key);
    const maxSize = config?.maxHistorySize ?? this.maxHistorySize;
    
    const snapshot: StateSnapshot = {
      id: key,
      timestamp: Date.now(),
      data: newValue,
      version: config?.version ?? 1
    };

    // Agregar al historial
    this.history.push(snapshot);
    
    // Mantener solo los snapshots más recientes
    if (this.history.length > maxSize * 10) { // Multiplicador para permitir múltiples claves
      this.history = this.history.slice(-maxSize * 5);
    }
  }

  /**
   * Persiste estado si está configurado
   */
  private maybePersist(key: string): void {
    const config = this.options.get(key);
    if (config?.persist) {
      try {
        const storageKey = config.storageKey || key;
        const persistedData = this.getPersistedState();
        persistedData[storageKey] = {
          data: this.store[key],
          timestamp: Date.now(),
          version: config.version ?? 1
        };
        localStorage.setItem('state_manager', JSON.stringify(persistedData));
      } catch (error) {
        console.error('Error persistiendo estado:', error);
      }
    }
  }

  /**
   * Obtiene el estado persistido
   */
  private getPersistedState(): Record<string, any> {
    try {
      const stored = localStorage.getItem('state_manager');
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error('Error cargando estado persistido:', error);
      return {};
    }
  }

  /**
   * Carga estado persistido
   */
  private loadPersistedState(): void {
    const persistedData = this.getPersistedState();
    
    Object.entries(persistedData).forEach(([key, value]) => {
      if (typeof value === 'object' && value !== null && 'data' in value) {
        this.store[key] = (value as any).data;
        
        // Configurar como persistido
        this.options.set(key, {
          persist: true,
          version: (value as any).version ?? 1,
          storageKey: key
        });
      }
    });
  }

  /**
   * Exporta el estado actual como JSON
   */
  public exportState(): string {
    return JSON.stringify({
      store: this.store,
      options: Object.fromEntries(this.options),
      exportedAt: Date.now()
    }, null, 2);
  }

  /**
   * Importa estado desde JSON
   */
  public importState(jsonState: string): void {
    try {
      const parsed = JSON.parse(jsonState);
      
      if (parsed.store && typeof parsed.store === 'object') {
        this.store = { ...parsed.store };
        
        if (parsed.options) {
          Object.entries(parsed.options).forEach(([key, value]) => {
            if (typeof value === 'object') {
              this.options.set(key, value as StateOptions);
            }
          });
        }
        
        this.emit('state:imported', { timestamp: Date.now() });
      }
    } catch (error) {
      console.error('Error importando estado:', error);
      throw new Error('Formato de estado inválido');
    }
  }

  /**
   * Limpia todo el estado persistido
   */
  public clearPersistedState(): void {
    localStorage.removeItem('state_manager');
    this.emit('state:persisted:cleared');
  }

  /**
   * Obtiene estadísticas del estado
   */
  public getStats(): {
    totalKeys: number;
    persistedKeys: number;
    totalSnapshots: number;
    storageSize: number;
  } {
    const persistedKeys = Array.from(this.options.values())
      .filter(opt => opt.persist).length;
    
    const storageSize = new Blob([this.exportState()]).size;

    return {
      totalKeys: Object.keys(this.store).length,
      persistedKeys,
      totalSnapshots: this.history.length,
      storageSize
    };
  }

  /**
   * Valida la integridad del estado
   */
  public validate(): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Verificar tipos de datos
    Object.entries(this.store).forEach(([key, value]) => {
      if (value === undefined) {
        errors.push(`Clave '${key}' tiene valor undefined`);
      }
      
      // Verificar funciones no serializables
      if (typeof value === 'function') {
        errors.push(`Clave '${key}' contiene una función no serializable`);
      }
      
      // Verificar objetos muy grandes
      if (typeof value === 'object' && JSON.stringify(value).length > 1000000) {
        errors.push(`Clave '${key}' es demasiado grande (${JSON.stringify(value).length} bytes)`);
      }
    });

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Optimiza el estado removiendo claves no utilizadas
   */
  public optimize(): void {
    const unusedKeys: string[] = [];
    
    // Encontrar claves que no han cambiado recientemente
    const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000;
    
    this.history.forEach(snapshot => {
      if (snapshot.timestamp < oneDayAgo && !this.has(snapshot.id)) {
        unusedKeys.push(snapshot.id);
      }
    });

    // Remover claves no utilizadas
    unusedKeys.forEach(key => this.remove(key));
    
    this.emit('state:optimized', { removedKeys: unusedKeys.length });
  }
}