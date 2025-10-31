import AsyncStorage from '@react-native-async-storage/async-storage';
import { StateSnapshot } from '../types/response.types';

export interface StateStore {
  [key: string]: any;
}

export interface StateOptions {
  persist?: boolean;
  version?: number;
  maxHistorySize?: number;
  storageKey?: string;
  expiry?: number; // Tiempo en ms antes de expirar
}

export class StateManager {
  private static instance: StateManager;
  private store: StateStore = {};
  private history: StateSnapshot[] = [];
  private options: Map<string, StateOptions> = new Map();
  private maxHistorySize = 50;
  private listeners: Map<string, Function[]> = new Map();

  private constructor() {
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
  public async set<T>(key: string, value: T, options?: StateOptions): Promise<void> {
    // Verificar expiración
    if (options?.expiry && Date.now() > (options.expiry || 0)) {
      console.log(`Value for key '${key}' has expired`);
      return;
    }

    const oldValue = this.store[key];
    this.store[key] = value;
    
    // Configurar opciones
    if (options) {
      this.options.set(key, {
        persist: options.persist ?? false,
        version: options.version ?? 1,
        maxHistorySize: options.maxHistorySize ?? this.maxHistorySize,
        storageKey: options.storageKey ?? key,
        expiry: options.expiry
      });
    }

    // Crear snapshot para historial
    this.createSnapshot(key, oldValue, value);
    
    // Persistir si está configurado
    await this.maybePersist(key);
    
    // Emitir evento de cambio
    this.emit('state:changed', { key, oldValue, newValue: value });
    this.emit(`state:${key}:changed`, { oldValue, newValue: value });
  }

  /**
   * Obtiene un valor del estado
   */
  public get<T>(key: string, defaultValue?: T): T | undefined {
    // Verificar expiración
    const keyOptions = this.options.get(key);
    if (keyOptions?.expiry && this.store[key] && keyOptions.expiry < Date.now()) {
      console.log(`Value for key '${key}' has expired, removing`);
      this.remove(key);
      return defaultValue;
    }

    return this.store[key] !== undefined ? this.store[key] : defaultValue;
  }

  /**
   * Obtiene un valor del estado de forma asíncrona (con verificación de expiración)
   */
  public async getAsync<T>(key: string, defaultValue?: T): Promise<T | undefined> {
    // Para valores persistidos, verificar expiración al cargar
    const keyOptions = this.options.get(key);
    if (keyOptions?.persist) {
      try {
        const persisted = await AsyncStorage.getItem(`state_${key}`);
        if (persisted) {
          const { data, expiry } = JSON.parse(persisted);
          if (expiry && Date.now() > expiry) {
            await AsyncStorage.removeItem(`state_${key}`);
            return defaultValue;
          }
          return data;
        }
      } catch (error) {
        console.error(`Error loading persisted state for key '${key}':`, error);
      }
    }

    return this.get(key, defaultValue);
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
  public async remove(key: string): Promise<boolean> {
    if (key in this.store) {
      const oldValue = this.store[key];
      delete this.store[key];
      
      // Remover opciones
      this.options.delete(key);
      
      // Remover del historial
      this.history = this.history.filter(snapshot => snapshot.id !== key);
      
      // Remover de persistencia
      await AsyncStorage.removeItem(`state_${key}`);
      
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
  public async setMultiple(values: Record<string, any>, options?: StateOptions): Promise<void> {
    const promises = Object.entries(values).map(([key, value]) => 
      this.set(key, value, options)
    );
    await Promise.all(promises);
  }

  /**
   * Actualiza una clave existente con una función
   */
  public async update<T>(key: string, updater: (currentValue: T | undefined) => T): Promise<void> {
    const currentValue = this.get<T>(key);
    const newValue = updater(currentValue);
    await this.set(key, newValue);
  }

  /**
   * Merges un objeto con una clave existente
   */
  public async merge(key: string, value: any): Promise<void> {
    await this.update(key, (currentValue: any) => {
      if (typeof currentValue === 'object' && typeof value === 'object') {
        return { ...currentValue, ...value };
      }
      return value;
    });
  }

  /**
   * Limpia todo el estado
   */
  public async clear(): Promise<void> {
    const oldStore = { ...this.store };
    this.store = {};
    this.history = [];
    
    // Limpiar persistencia
    const keys = Array.from(this.options.keys()).filter(
      key => this.options.get(key)?.persist
    );
    await Promise.all(keys.map(key => AsyncStorage.removeItem(`state_${key}`)));
    
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
  public async restore(key: string, timestamp: number): Promise<boolean> {
    const snapshot = this.history.find(
      s => s.id === key && s.timestamp === timestamp
    );
    
    if (snapshot) {
      await this.set(key, snapshot.data);
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
  public async transaction(callback: (state: StateManager) => Promise<void>): Promise<void> {
    const backup = { ...this.store };
    const backupHistory = [...this.history];
    
    try {
      await callback(this);
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
  private createSnapshot(key: string, oldValue: any, newValue: any): void {
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
  private async maybePersist(key: string): Promise<void> {
    const config = this.options.get(key);
    if (config?.persist) {
      try {
        const storageKey = config.storageKey || key;
        const persistedData: any = {
          data: this.store[key],
          timestamp: Date.now(),
          version: config.version ?? 1
        };

        // Agregar expiración si está configurada
        if (config.expiry) {
          persistedData.expiry = config.expiry;
        }

        await AsyncStorage.setItem(`state_${storageKey}`, JSON.stringify(persistedData));
      } catch (error) {
        console.error('Error persistiendo estado:', error);
      }
    }
  }

  /**
   * Carga estado persistido
   */
  private async loadPersistedState(): Promise<void> {
    try {
      // Obtener todas las claves que empiecen con 'state_'
      const keys = await AsyncStorage.getAllKeys();
      const stateKeys = keys.filter(key => key.startsWith('state_'));
      
      if (stateKeys.length > 0) {
        const storedValues = await AsyncStorage.multiGet(stateKeys);
        
        storedValues.forEach(([key, value]) => {
          if (value) {
            try {
              const parsed = JSON.parse(value);
              const cleanKey = key.replace('state_', '');
              
              // Verificar expiración
              if (parsed.expiry && Date.now() > parsed.expiry) {
                AsyncStorage.removeItem(key);
                return;
              }
              
              this.store[cleanKey] = parsed.data;
              
              // Configurar como persistido
              this.options.set(cleanKey, {
                persist: true,
                version: parsed.version ?? 1,
                storageKey: cleanKey,
                expiry: parsed.expiry
              });
            } catch (error) {
              console.error(`Error parsing persisted state for key ${key}:`, error);
            }
          }
        });
      }
    } catch (error) {
      console.error('Error cargando estado persistido:', error);
    }
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
  public async importState(jsonState: string): Promise<void> {
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
  public async clearPersistedState(): Promise<void> {
    const keys = await AsyncStorage.getAllKeys();
    const stateKeys = keys.filter(key => key.startsWith('state_'));
    await AsyncStorage.multiRemove(stateKeys);
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
    expiredValues: number;
  } {
    const persistedKeys = Array.from(this.options.values())
      .filter(opt => opt.persist).length;
    
    const storageSize = new Blob([this.exportState()]).size;
    
    const expiredValues = Array.from(this.options.entries())
      .filter(([key, config]) => config.expiry && Date.now() > config.expiry).length;

    return {
      totalKeys: Object.keys(this.store).length,
      persistedKeys,
      totalSnapshots: this.history.length,
      storageSize,
      expiredValues
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
  public async optimize(): Promise<void> {
    const unusedKeys: string[] = [];
    
    // Encontrar claves que no han cambiado recientemente
    const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000;
    
    this.history.forEach(snapshot => {
      if (snapshot.timestamp < oneDayAgo && !this.has(snapshot.id)) {
        unusedKeys.push(snapshot.id);
      }
    });

    // Remover claves no utilizadas
    await Promise.all(unusedKeys.map(key => this.remove(key)));
    
    this.emit('state:optimized', { removedKeys: unusedKeys.length });
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