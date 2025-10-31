import React, { useState } from 'react';
import { useAsyncRequest, useNotification, useStateManager } from '../hooks/useAsyncManager';
import { TransactionFlow, RequestConfig } from '../types/response.types';

interface AsyncRequestDemoProps {
  title?: string;
}

export const AsyncRequestDemo: React.FC<AsyncRequestDemoProps> = ({ 
  title = "Demo de Peticiones Asíncronas" 
}) => {
  const [requestConfig, setRequestConfig] = useState<RequestConfig>({
    url: 'https://jsonplaceholder.typicode.com/posts/1',
    method: 'GET'
  });

  const { data, loading, error, request, reset } = useAsyncRequest({
    showNotification: true,
    persistResult: true,
    context: { source: 'demo_component' }
  });

  const { success, error: showError } = useNotification();
  const [requestCount, setRequestCount] = useStateManager('demo_request_count', 0);

  const executeRequest = async () => {
    const response = await request(requestConfig);
    if (response.success) {
      setRequestCount((requestCount || 0) + 1);
      success('Petición Exitosa', `Solicitud completada. Peticiones realizadas: ${requestCount! + 1}`);
    }
  };

  const executeWithRetry = async () => {
    const response = await request({
      ...requestConfig,
      url: 'https://jsonplaceholder.typicode.com/posts/999' // URL que puede fallar
    });
    if (!response.success) {
      showError('Petición Fallida', `Error: ${response.error}. Intentando automáticamente...`);
    }
  };

  return (
    <div className="async-request-demo p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">{title}</h2>
      
      {/* Configuración de la petición */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4">Configuración de Petición</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">URL:</label>
            <input
              type="text"
              value={requestConfig.url}
              onChange={(e) => setRequestConfig({ ...requestConfig, url: e.target.value })}
              className="w-full p-2 border rounded-md"
              placeholder="https://api.example.com/data"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Método:</label>
            <select
              value={requestConfig.method}
              onChange={(e) => setRequestConfig({ ...requestConfig, method: e.target.value as any })}
              className="w-full p-2 border rounded-md"
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="DELETE">DELETE</option>
            </select>
          </div>
        </div>
      </div>

      {/* Botones de acción */}
      <div className="flex flex-wrap gap-3 mb-6">
        <button
          onClick={executeRequest}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? 'Ejecutando...' : 'Ejecutar Petición'}
        </button>
        
        <button
          onClick={executeWithRetry}
          disabled={loading}
          className="px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600 disabled:opacity-50"
        >
          Petición con Reintento
        </button>
        
        <button
          onClick={reset}
          className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
        >
          Limpiar
        </button>
      </div>

      {/* Estado de la petición */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="font-semibold text-blue-800">Estado</h4>
          <p className="text-blue-600">
            {loading ? 'Cargando...' : error ? 'Error' : 'Listo'}
          </p>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <h4 className="font-semibold text-green-800">Peticiones Exitosas</h4>
          <p className="text-green-600">{requestCount || 0}</p>
        </div>
        
        <div className="bg-purple-50 p-4 rounded-lg">
          <h4 className="font-semibold text-purple-800">Datos Recibidos</h4>
          <p className="text-purple-600">
            {data ? `${JSON.stringify(data).length} caracteres` : 'Ninguno'}
          </p>
        </div>
      </div>

      {/* Mostrar error */}
      {error && (
        <div className="bg-red-50 border border-red-200 p-4 rounded-lg mb-6">
          <h4 className="font-semibold text-red-800">Error</h4>
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Mostrar datos */}
      {data && (
        <div className="bg-gray-50 border p-4 rounded-lg">
          <h4 className="font-semibold mb-2">Datos Recibidos:</h4>
          <pre className="text-sm bg-white p-3 rounded border overflow-auto max-h-60">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default AsyncRequestDemo;