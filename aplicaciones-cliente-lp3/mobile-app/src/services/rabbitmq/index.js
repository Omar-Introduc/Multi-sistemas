import RabbitMQClient from './client';
import ClientServices from './services';
import RabbitMQInterceptor, { createRabbitMQInterceptor, useRabbitMQInterceptor } from './axios-interceptor';
import { RABBITMQ_CONFIG, OPERATION_PRIORITIES } from './config';

// Factory function para crear cliente completo
export const createRabbitMQClient = async () => {
  const client = new RabbitMQClient();
  await client.connect();
  return client;
};

// Factory function para crear servicios del cliente
export const createClientServices = async () => {
  const client = await createRabbitMQClient();
  return new ClientServices(client);
};

// Hook personalizado para React Native
export { useRabbitMQInterceptor };

// Instancia singleton del interceptor
let singletonInterceptor = null;
let singletonServices = null;

export const initializeRabbitMQ = async () => {
  if (!singletonInterceptor) {
    singletonInterceptor = createRabbitMQInterceptor();
    await singletonInterceptor.initialize();
  }
  
  if (!singletonServices) {
    const client = singletonInterceptor.getClient();
    singletonServices = new ClientServices(client);
  }
  
  return {
    interceptor: singletonInterceptor,
    services: singletonServices
  };
};

// Obtener instancia singleton
export const getRabbitMQInstance = () => {
  return {
    interceptor: singletonInterceptor,
    services: singletonServices
  };
};

// Limpiar instancias
export const cleanupRabbitMQ = () => {
  if (singletonInterceptor) {
    singletonInterceptor.cleanup();
    singletonInterceptor = null;
  }
  singletonServices = null;
};

// Exportar clases y configuraciones
export { 
  RabbitMQClient, 
  ClientServices, 
  RabbitMQInterceptor,
  RABBITMQ_CONFIG,
  OPERATION_PRIORITIES
};

// Export por defecto
export default {
  RabbitMQClient,
  ClientServices,
  RabbitMQInterceptor,
  initializeRabbitMQ,
  getRabbitMQInstance,
  cleanupRabbitMQ,
  createRabbitMQClient,
  createClientServices,
  useRabbitMQInterceptor
};