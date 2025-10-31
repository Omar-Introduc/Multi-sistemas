import React from 'react';
import SocketIORabbitMQClient from './socketio-client';
import DesktopClientServices from './services';
import { RABBITMQ_CONFIG, OPERATION_PRIORITIES, ELECTRON_CONFIG, UI_CONFIG } from './config';

// Factory function para crear cliente completo
export const createSocketIOClient = async () => {
  const client = new SocketIORabbitMQClient();
  await client.connect();
  return client;
};

// Factory function para crear servicios del cliente desktop
export const createDesktopClientServices = async () => {
  const client = await createSocketIOClient();
  return new DesktopClientServices(client);
};

// Instancia singleton
let singletonClient = null;
let singletonServices = null;

// Inicializar cliente completo
export const initializeDesktopRabbitMQ = async () => {
  if (!singletonClient) {
    singletonClient = new SocketIORabbitMQClient();
    await singletonClient.connect();
  }
  
  if (!singletonServices) {
    singletonServices = new DesktopClientServices(singletonClient);
  }
  
  return {
    client: singletonClient,
    services: singletonServices
  };
};

// Obtener instancia singleton
export const getDesktopRabbitMQInstance = () => {
  return {
    client: singletonClient,
    services: singletonServices
  };
};

// Limpiar instancias
export const cleanupDesktopRabbitMQ = async () => {
  if (singletonClient) {
    await singletonClient.disconnect();
    singletonClient = null;
  }
  singletonServices = null;
};

// Configurar Electron main process
export const setupElectronMain = (mainWindow) => {
  if (!mainWindow) {
    throw new Error('Main window is required for Electron setup');
  }

  // ConfigurarIPC handlers para comunicación entre main y renderer
  const { ipcMain } = require('electron');
  
  // Handler para obtener estado de conexión
  ipcMain.handle('rabbitmq:status', async () => {
    try {
      const instance = getDesktopRabbitMQInstance();
      if (instance.client) {
        return instance.client.getStatus();
      }
      return { connected: false };
    } catch (error) {
      console.error('Error getting RabbitMQ status:', error);
      return { connected: false, error: error.message };
    }
  });

  // Handler para enviar requests
  ipcMain.handle('rabbitmq:request', async (event, type, payload, options) => {
    try {
      const instance = getDesktopRabbitMQInstance();
      if (instance.services) {
        const method = instance.services[type];
        if (typeof method === 'function') {
          return await method.call(instance.services, payload);
        } else {
          // Usar cliente directo para requests genéricos
          return await instance.client.request(type, payload, options);
        }
      }
      throw new Error('Services not initialized');
    } catch (error) {
      console.error('Error making RabbitMQ request:', error);
      throw error;
    }
  });

  // Handler para suscribirse a notificaciones
  ipcMain.on('rabbitmq:subscribe', async (event, eventType) => {
    try {
      const instance = getDesktopRabbitMQInstance();
      if (instance.client) {
        instance.client.subscribe(eventType, (data) => {
          // Enviar datos al renderer
          mainWindow.webContents.send(`rabbitmq:${eventType}`, data);
        });
      }
    } catch (error) {
      console.error('Error subscribing to event:', error);
    }
  });

  // Handler para cancelar suscripción
  ipcMain.on('rabbitmq:unsubscribe', async (event, eventType) => {
    try {
      const instance = getDesktopRabbitMQInstance();
      if (instance.client) {
        instance.client.unsubscribe(eventType);
      }
    } catch (error) {
      console.error('Error unsubscribing from event:', error);
    }
  });

  console.log('✅ Electron IPC handlers configured for RabbitMQ');
};

// Configurar Electron renderer process
export const setupElectronRenderer = () => {
  const { ipcRenderer } = require('electron');
  
  // Cliente para el renderer process
  class RendererRabbitMQClient {
    async request(type, payload, options) {
      return await ipcRenderer.invoke('rabbitmq:request', type, payload, options);
    }

    subscribe(eventType, callback) {
      ipcRenderer.on(`rabbitmq:${eventType}`, (event, data) => {
        callback(data);
      });
    }

    unsubscribe(eventType) {
      ipcRenderer.removeAllListeners(`rabbitmq:${eventType}`);
    }

    async getStatus() {
      return await ipcRenderer.invoke('rabbitmq:status');
    }
  }

  return new RendererRabbitMQClient();
};

// Hook personalizado para React en Electron
export const useDesktopRabbitMQ = () => {
  const [isInitialized, setIsInitialized] = React.useState(false);
  const [error, setError] = React.useState(null);
  const [client, setClient] = React.useState(null);
  const [services, setServices] = React.useState(null);

  React.useEffect(() => {
    const initialize = async () => {
      try {
        const instance = await initializeDesktopRabbitMQ();
        setClient(instance.client);
        setServices(instance.services);
        setIsInitialized(true);
        setError(null);
      } catch (err) {
        setError(err);
        setIsInitialized(false);
      }
    };

    if (typeof window !== 'undefined' && window.require) {
      initialize();
    }

    return () => {
      // Cleanup si es necesario
    };
  }, []);

  return {
    client,
    services,
    isInitialized,
    error,
    getStatus: () => client?.getStatus()
  };
};

// Exportar configuraciones
export { 
  RABBITMQ_CONFIG,
  OPERATION_PRIORITIES,
  ELECTRON_CONFIG,
  UI_CONFIG
};

// Exportar clases principales
export {
  SocketIORabbitMQClient,
  DesktopClientServices
};

// Export por defecto
export default {
  SocketIORabbitMQClient,
  DesktopClientServices,
  initializeDesktopRabbitMQ,
  getDesktopRabbitMQInstance,
  cleanupDesktopRabbitMQ,
  setupElectronMain,
  setupElectronRenderer,
  useDesktopRabbitMQ,
  createSocketIOClient,
  createDesktopClientServices,
  RABBITMQ_CONFIG,
  OPERATION_PRIORITIES,
  ELECTRON_CONFIG,
  UI_CONFIG
};