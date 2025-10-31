import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, TextInput, Alert } from 'react-native';
import { 
  useAsyncRequest, 
  useNotification, 
  useStateManager,
  useAsyncOperations 
} from '../hooks/useAsyncManager';
import { RequestConfig } from '../types/response.types';

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
    showNotifications: true,
    persistResults: true,
    cacheKey: 'demo_posts',
    cacheExpiry: 300000 // 5 minutos
  });

  const { success, error: showError } = useNotification();
  const [requestCount, setRequestCount] = useStateManager('demo_request_count', 0);
  const { executeRequest } = useAsyncOperations();

  const executeSimpleRequest = async () => {
    const response = await request(requestConfig);
    if (response.success) {
      setRequestCount((requestCount || 0) + 1);
      success('Petición Exitosa', `Solicitud completada. Peticiones realizadas: ${requestCount! + 1}`);
    }
  };

  const executeWithRetry = async () => {
    const response = await executeRequest({
      ...requestConfig,
      url: 'https://jsonplaceholder.typicode.com/posts/999' // URL que puede fallar
    }, {
      showSuccessMessage: 'Petición con reintentos exitosa',
      showErrorMessage: false
    });
    
    if (!response) {
      showError('Petición Fallida', 'La petición falló pero se reintentó automáticamente');
    }
  };

  const executeCachedRequest = async () => {
    // Esta petición debería usar el cache
    const response = await request({
      ...requestConfig,
      url: 'https://jsonplaceholder.typicode.com/posts/1'
    });
    
    if (response.success && response.requestId === 'cache_hit') {
      success('Cache Hit', 'Datos obtenidos desde caché');
    }
  };

  const clearCache = async () => {
    await executeRequest.clearCache?.();
    success('Cache Limpiado', 'El caché ha sido limpiado');
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>{title}</Text>

      {/* Configuración de la petición */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Configuración de Petición</Text>
        
        <Text style={styles.label}>URL:</Text>
        <TextInput
          style={styles.input}
          value={requestConfig.url}
          onChangeText={(url) => setRequestConfig({ ...requestConfig, url })}
          placeholder="https://api.example.com/data"
          autoCapitalize="none"
        />
        
        <Text style={styles.label}>Método:</Text>
        <View style={styles.methodContainer}>
          {['GET', 'POST', 'PUT', 'DELETE'].map(method => (
            <TouchableOpacity
              key={method}
              style={[
                styles.methodButton,
                requestConfig.method === method && styles.methodButtonActive
              ]}
              onPress={() => setRequestConfig({ ...requestConfig, method: method as any })}
            >
              <Text style={[
                styles.methodButtonText,
                requestConfig.method === method && styles.methodButtonTextActive
              ]}>
                {method}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Botones de acción */}
      <View style={styles.section}>
        <View style={styles.buttonRow}>
          <TouchableOpacity
            style={[styles.button, styles.primaryButton, loading && styles.buttonDisabled]}
            onPress={executeSimpleRequest}
            disabled={loading}
          >
            <Text style={styles.buttonText}>
              {loading ? 'Ejecutando...' : 'Ejecutar Petición'}
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.button, styles.secondaryButton, loading && styles.buttonDisabled]}
            onPress={executeWithRetry}
            disabled={loading}
          >
            <Text style={[styles.buttonText, styles.secondaryButtonText]}>
              Con Reintento
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.buttonRow}>
          <TouchableOpacity
            style={[styles.button, styles.tertiaryButton]}
            onPress={executeCachedRequest}
          >
            <Text style={styles.buttonText}>Usar Cache</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.button, styles.warningButton]}
            onPress={clearCache}
          >
            <Text style={styles.buttonText}>Limpiar Cache</Text>
          </TouchableOpacity>
        </View>
        
        <TouchableOpacity
          style={[styles.button, styles.resetButton]}
          onPress={reset}
        >
          <Text style={styles.buttonText}>Limpiar</Text>
        </TouchableOpacity>
      </View>

      {/* Estado de la petición */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Estado</Text>
        
        <View style={styles.statusContainer}>
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Estado:</Text>
            <Text style={[
              styles.statusValue,
              { color: loading ? '#f39c12' : error ? '#e74c3c' : '#27ae60' }
            ]}>
              {loading ? 'Cargando...' : error ? 'Error' : 'Listo'}
            </Text>
          </View>
          
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Peticiones Exitosas:</Text>
            <Text style={styles.statusValue}>{requestCount || 0}</Text>
          </View>
          
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Datos Recibidos:</Text>
            <Text style={styles.statusValue}>
              {data ? `${JSON.stringify(data).length} caracteres` : 'Ninguno'}
            </Text>
          </View>
        </View>
      </View>

      {/* Mostrar error */}
      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>Error</Text>
          <Text style={styles.errorMessage}>{error}</Text>
        </View>
      )}

      {/* Mostrar datos */}
      {data && (
        <View style={styles.dataContainer}>
          <Text style={styles.dataTitle}>Datos Recibidos:</Text>
          <Text style={styles.dataContent}>
            {JSON.stringify(data, null, 2)}
          </Text>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f8f9fa'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 24,
    textAlign: 'center',
    color: '#2c3e50'
  },
  section: {
    backgroundColor: 'white',
    padding: 16,
    marginBottom: 16,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
    color: '#34495e'
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 8,
    color: '#5a6c7d'
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 4,
    padding: 12,
    fontSize: 14,
    marginBottom: 16,
    backgroundColor: '#fafafa'
  },
  methodContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between'
  },
  methodButton: {
    flex: 1,
    padding: 10,
    marginHorizontal: 4,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 4,
    backgroundColor: '#f8f9fa',
    alignItems: 'center'
  },
  methodButtonActive: {
    backgroundColor: '#007bff',
    borderColor: '#007bff'
  },
  methodButtonText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#6c757d'
  },
  methodButtonTextActive: {
    color: 'white'
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8
  },
  button: {
    padding: 12,
    borderRadius: 6,
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 4
  },
  primaryButton: {
    backgroundColor: '#007bff'
  },
  secondaryButton: {
    backgroundColor: '#6c757d'
  },
  tertiaryButton: {
    backgroundColor: '#17a2b8'
  },
  warningButton: {
    backgroundColor: '#ffc107'
  },
  resetButton: {
    backgroundColor: '#6c757d',
    marginTop: 8
  },
  buttonDisabled: {
    opacity: 0.6
  },
  buttonText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 14
  },
  secondaryButtonText: {
    color: 'white'
  },
  statusContainer: {
    gap: 12
  },
  statusItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  statusLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#6c757d'
  },
  statusValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#495057'
  },
  errorContainer: {
    backgroundColor: '#f8d7da',
    borderWidth: 1,
    borderColor: '#f5c6cb',
    borderRadius: 6,
    padding: 12,
    marginBottom: 16
  },
  errorTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#721c24',
    marginBottom: 4
  },
  errorMessage: {
    fontSize: 14,
    color: '#721c24'
  },
  dataContainer: {
    backgroundColor: '#e9ecef',
    borderRadius: 6,
    padding: 12
  },
  dataTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#495057',
    marginBottom: 8
  },
  dataContent: {
    fontSize: 12,
    color: '#6c757d',
    fontFamily: 'monospace'
  }
});

export default AsyncRequestDemo;