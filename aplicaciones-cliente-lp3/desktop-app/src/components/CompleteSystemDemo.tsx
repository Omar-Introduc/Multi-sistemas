import React, { useState } from 'react';
import { AsyncResponseManager } from '../core/AsyncResponseManager';
import { createCheckoutFlow, createUserRegistrationFlow } from '../services/transactionFlows';
import { userService, postService } from '../services/apiServices';

export const CompleteSystemDemo: React.FC = () => {
  const [activeDemo, setActiveDemo] = useState<string>('overview');
  const [stats, setStats] = useState<any>(null);
  const manager = AsyncResponseManager.getInstance();

  const refreshStats = () => {
    const currentStats = manager.getStats();
    setStats(currentStats);
  };

  React.useEffect(() => {
    refreshStats();
    const interval = setInterval(refreshStats, 2000);
    return () => clearInterval(interval);
  }, []);

  const runCompleteDemo = async () => {
    try {
      // 1. Ejecutar petición simple
      console.log('1. Ejecutando petición simple...');
      const userResponse = await userService.getUsers();
      console.log('Usuarios obtenidos:', userResponse.success ? userResponse.data?.length : 'Error');
      
      if (userResponse.success && userResponse.data?.length > 0) {
        // 2. Ejecutar flujo de registro
        console.log('2. Ejecutando flujo de registro...');
        const registrationFlow = createUserRegistrationFlow({
          email: `test${Date.now()}@example.com`,
          password: 'test123',
          name: 'Usuario Demo',
          source: 'demo'
        });
        
        const registrationResult = await manager.executeTransactionFlow(registrationFlow, {
          showProgress: true
        });
        
        console.log('Registro completado:', registrationResult.success);
        
        // 3. Ejecutar flujo de checkout
        console.log('3. Ejecutando flujo de checkout...');
        const checkoutFlow = createCheckoutFlow({
          items: [
            { id: 1, name: 'Producto Demo', price: 29.99, quantity: 2 },
            { id: 2, name: 'Artículo de Prueba', price: 15.50, quantity: 1 }
          ],
          user: {
            id: 'demo_user',
            email: 'demo@example.com',
            name: 'Usuario Demo'
          },
          shipping: {
            method: 'standard',
            address: 'Calle Demo 123, Ciudad Demo'
          }
        });
        
        const checkoutResult = await manager.executeTransactionFlow(checkoutFlow, {
          showProgress: true
        });
        
        console.log('Checkout completado:', checkoutResult.success);
        
        // 4. Mostrar estadísticas finales
        refreshStats();
        
        if (registrationResult.success && checkoutResult.success) {
          manager.notifications.success(
            'Demo Completado',
            'Todas las operaciones se ejecutaron exitosamente'
          );
        }
      }
      
    } catch (error) {
      console.error('Error en demo completo:', error);
      manager.notifications.error(
        'Error en Demo',
        'Ocurrió un error durante la ejecución'
      );
    }
  };

  const runParallelRequests = async () => {
    try {
      manager.notifications.info('Ejecutando Peticiones Paralelas', 'Iniciando...');
      
      // Ejecutar múltiples peticiones en paralelo
      const promises = [
        userService.getUsers(),
        postService.getPosts(),
        userService.getUser(1),
        postService.getPost(1)
      ];

      const results = await Promise.allSettled(promises);
      
      const successful = results.filter(r => r.status === 'fulfilled' && r.value.success).length;
      const failed = results.length - successful;
      
      if (failed === 0) {
        manager.notifications.success(
          'Peticiones Paralelas Completadas',
          `${successful} peticiones ejecutadas exitosamente`
        );
      } else {
        manager.notifications.warning(
          'Peticiones Completadas con Errores',
          `${successful} exitosas, ${failed} fallidas`
        );
      }
      
    } catch (error) {
      console.error('Error en peticiones paralelas:', error);
    }
  };

  const simulateSystemLoad = async () => {
    try {
      manager.notifications.info('Simulando Carga del Sistema', 'Generando peticiones...');
      
      // Simular carga con múltiples peticiones
      const requests = Array.from({ length: 10 }, (_, i) => 
        userService.getUser(Math.floor(Math.random() * 10) + 1)
      );

      const results = await Promise.allSettled(requests);
      
      const stats = {
        total: results.length,
        successful: results.filter(r => r.status === 'fulfilled' && r.value.success).length,
        failed: results.filter(r => r.status === 'rejected' || 
          (r.status === 'fulfilled' && !r.value.success)).length
      };
      
      manager.notifications.info(
        'Carga del Sistema Completada',
        `${stats.successful}/${stats.total} peticiones exitosas`
      );
      
      refreshStats();
      
    } catch (error) {
      console.error('Error simulando carga:', error);
    }
  };

  const clearAllData = () => {
    manager.cleanup();
    manager.notifications.info('Sistema Limpiado', 'Todos los datos han sido limpiados');
    refreshStats();
  };

  return (
    <div className="complete-system-demo p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-8 text-center">
        Demo Completo del Sistema de Manejo de Respuestas Asíncronas
      </h1>

      {/* Estadísticas del Sistema */}
      {stats && (
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <h2 className="text-xl font-semibold mb-4">Estadísticas del Sistema</h2>
          
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
            <div className="bg-blue-50 p-3 rounded text-center">
              <div className="text-2xl font-bold text-blue-600">
                {stats.response.activeRequests}
              </div>
              <div className="text-sm text-blue-700">Peticiones Activas</div>
            </div>
            
            <div className="bg-green-50 p-3 rounded text-center">
              <div className="text-2xl font-bold text-green-600">
                {Math.round(stats.response.successRate)}%
              </div>
              <div className="text-sm text-green-700">Tasa de Éxito</div>
            </div>
            
            <div className="bg-purple-50 p-3 rounded text-center">
              <div className="text-2xl font-bold text-purple-600">
                {stats.notification.activeNotifications}
              </div>
              <div className="text-sm text-purple-700">Notificaciones</div>
            </div>
            
            <div className="bg-orange-50 p-3 rounded text-center">
              <div className="text-2xl font-bold text-orange-600">
                {stats.error.totalErrors}
              </div>
              <div className="text-sm text-orange-700">Total Errores</div>
            </div>
            
            <div className="bg-teal-50 p-3 rounded text-center">
              <div className="text-2xl font-bold text-teal-600">
                {Math.round(stats.flow.averageDuration / 1000)}s
              </div>
              <div className="text-sm text-teal-700">Tiempo Promedio</div>
            </div>
          </div>

          <div className="text-sm text-gray-600">
            Uptime: {Math.round(stats.uptime / 1000)}s | 
            Memoria: {Math.round(stats.memoryUsage / 1024)}KB
          </div>
        </div>
      )}

      {/* Navegación */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-8">
        <h3 className="text-lg font-semibold mb-4">Navegación del Demo</h3>
        
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setActiveDemo('overview')}
            className={`px-4 py-2 rounded-md ${
              activeDemo === 'overview'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Resumen General
          </button>
          
          <button
            onClick={() => setActiveDemo('demo_completo')}
            className={`px-4 py-2 rounded-md ${
              activeDemo === 'demo_completo'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Demo Completo
          </button>
          
          <button
            onClick={() => setActiveDemo('flujos')}
            className={`px-4 py-2 rounded-md ${
              activeDemo === 'flujos'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Flujos de Transacción
          </button>
          
          <button
            onClick={() => setActiveDemo('rendimiento')}
            className={`px-4 py-2 rounded-md ${
              activeDemo === 'rendimiento'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Pruebas de Rendimiento
          </button>
        </div>
      </div>

      {/* Contenido Principal */}
      {activeDemo === 'overview' && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Resumen del Sistema</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium mb-3">Componentes Principales</h3>
              <ul className="space-y-2 text-sm">
                <li><strong>ResponseManager:</strong> Manejo de peticiones HTTP con reintentos</li>
                <li><strong>NotificationSystem:</strong> Sistema de notificaciones inteligentes</li>
                <li><strong>StateManager:</strong> Gestión de estado con persistencia</li>
                <li><strong>ErrorHandler:</strong> Manejo y tracking de errores</li>
                <li><strong>TransactionFlowManager:</strong> Flujos de transacciones complejos</li>
                <li><strong>AsyncResponseManager:</strong> Integración de todos los sistemas</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-medium mb-3">Características</h3>
              <ul className="space-y-2 text-sm">
                <li>✅ Reintentos automáticos con backoff exponencial</li>
                <li>✅ Notificaciones con templates personalizables</li>
                <li>✅ Persistencia de estado en localStorage</li>
                <li>✅ Tracking y métricas de errores</li>
                <li>✅ Flujos de transacciones con rollback</li>
                <li>✅ WebSocket para actualizaciones en tiempo real</li>
                <li>✅ Hooks React para integración sencilla</li>
                <li>✅ Manejo robusto de estados de carga</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {activeDemo === 'demo_completo' && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Demo Completo del Sistema</h2>
          <p className="text-gray-600 mb-6">
            Este demo ejecuta una secuencia completa que demuestra todos los componentes trabajando juntos:
          </p>
          
          <ol className="list-decimal list-inside space-y-2 mb-6 text-sm">
            <li>Petición HTTP simple (obtener usuarios)</li>
            <li>Flujo de registro de usuario completo con validaciones</li>
            <li>Flujo de checkout con múltiples pasos y rollback</li>
            <li>Muestra estadísticas del sistema en tiempo real</li>
          </ol>

          <button
            onClick={runCompleteDemo}
            className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 font-semibold"
          >
            Ejecutar Demo Completo
          </button>
        </div>
      )}

      {activeDemo === 'flujos' && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Flujos de Transacción</h2>
          <p className="text-gray-600 mb-6">
            Los flujos de transacción permiten ejecutar operaciones complejas con múltiples pasos,
            dependencias, rollback automático y seguimiento de progreso.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-2">Flujo de Checkout</h3>
              <p className="text-sm text-gray-600 mb-4">
                Proceso completo de compra con validación, pago, inventario y confirmaciones.
              </p>
              <ul className="text-xs text-gray-500 space-y-1">
                <li>• Validación de carrito</li>
                <li>• Verificación de inventario</li>
                <li>• Procesamiento de pago</li>
                <li>• Creación de orden</li>
                <li>• Actualización de inventario</li>
                <li>• Envío de confirmaciones</li>
              </ul>
            </div>

            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-2">Registro de Usuario</h3>
              <p className="text-sm text-gray-600 mb-4">
                Proceso completo de registro con verificaciones y configuración inicial.
              </p>
              <ul className="text-xs text-gray-500 space-y-1">
                <li>• Validación de datos</li>
                <li>• Verificación de email único</li>
                <li>• Creación de cuenta</li>
                <li>• Email de verificación</li>
                <li>• Configuración de preferencias</li>
                <li>• Secuencia de bienvenida</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {activeDemo === 'rendimiento' && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Pruebas de Rendimiento</h2>
          <p className="text-gray-600 mb-6">
            Simula cargas de trabajo y múltiples peticiones para evaluar el comportamiento del sistema.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={runParallelRequests}
              className="px-4 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600"
            >
              Ejecutar Peticiones Paralelas
            </button>
            
            <button
              onClick={simulateSystemLoad}
              className="px-4 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
            >
              Simular Carga del Sistema
            </button>
          </div>

          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold mb-2">Métricas de Rendimiento</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="font-medium">Peticiones Totales</div>
                <div className="text-gray-600">{stats?.response.totalRequests || 0}</div>
              </div>
              <div>
                <div className="font-medium">Tiempo Promedio</div>
                <div className="text-gray-600">
                  {Math.round(stats?.response.averageResponseTime || 0)}ms
                </div>
              </div>
              <div>
                <div className="font-medium">Tasa de Errores</div>
                <div className="text-gray-600">
                  {Math.round((1 - (stats?.response.successRate || 0) / 100) * 100)}%
                </div>
              </div>
              <div>
                <div className="font-medium">Flujos Completados</div>
                <div className="text-gray-600">{stats?.flow.completedFlows || 0}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Botones de Control */}
      <div className="flex justify-center gap-4 mt-8">
        <button
          onClick={refreshStats}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          Actualizar Estadísticas
        </button>
        
        <button
          onClick={() => manager.exportDebugInfo() && console.log('Debug info exported')}
          className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
        >
          Exportar Debug Info
        </button>
        
        <button
          onClick={clearAllData}
          className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
        >
          Limpiar Sistema
        </button>
      </div>
    </div>
  );
};

export default CompleteSystemDemo;