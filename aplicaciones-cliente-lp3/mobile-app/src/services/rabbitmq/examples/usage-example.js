/**
 * Ejemplo de uso del cliente RabbitMQ en React Native
 * Archivo: /src/services/rabbitmq/examples/usage-example.js
 */

import React, { useState, useEffect } from 'react';
import { View, Text, Button, ScrollView, TextInput, StyleSheet, Alert } from 'react-native';
import { 
  initializeRabbitMQ, 
  getRabbitMQInstance,
  useRabbitMQInterceptor 
} from '../index';

// Hook personalizado para usar RabbitMQ en React Native
const useRabbitMQ = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [services, setServices] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const init = async () => {
      try {
        const instance = await initializeRabbitMQ();
        setServices(instance.services);
        setIsConnected(true);
        setError(null);
      } catch (err) {
        setError(err.message);
        setIsConnected(false);
      }
    };

    init();
  }, []);

  return { services, isConnected, error };
};

// Componente de ejemplo para la aplicación móvil
const RabbitMQExample = () => {
  const { services, isConnected, error } = useRabbitMQ();
  const [balance, setBalance] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(false);

  // Obtener saldo
  const handleGetBalance = async () => {
    if (!services) return;
    
    setLoading(true);
    try {
      const result = await services.getBalance({
        accountId: 'ACC_123',
        clientId: 'CLIENT_456'
      });
      
      if (result.success) {
        setBalance(result.data);
        Alert.alert('Éxito', `Saldo obtenido: ${result.data.balance} ${result.data.currency}`);
      } else {
        Alert.alert('Error', result.error);
      }
    } catch (err) {
      Alert.alert('Error', err.message);
    }
    setLoading(false);
  };

  // Obtener transacciones
  const handleGetTransactions = async () => {
    if (!services) return;
    
    setLoading(true);
    try {
      const result = await services.getTransactions({
        accountId: 'ACC_123',
        startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // Últimos 30 días
        endDate: new Date(),
        limit: 10
      });
      
      if (result.success) {
        setTransactions(result.data.transactions || []);
        Alert.alert('Éxito', `Transacciones obtenidas: ${result.data.transactions?.length || 0}`);
      } else {
        Alert.alert('Error', result.error);
      }
    } catch (err) {
      Alert.alert('Error', err.message);
    }
    setLoading(false);
  };

  // Solicitar préstamo
  const handleRequestLoan = async () => {
    if (!services) return;
    
    setLoading(true);
    try {
      const result = await services.requestLoan({
        amount: 10000,
        term: 12,
        purpose: 'Compra de vehículo',
        interestRate: 0.15,
        clientId: 'CLIENT_456'
      });
      
      if (result.success) {
        Alert.alert('Éxito', `Préstamo solicitado. ID: ${result.requestId}`);
      } else {
        Alert.alert('Error', result.error);
      }
    } catch (err) {
      Alert.alert('Error', err.message);
    }
    setLoading(false);
  };

  // Suscribirse a notificaciones
  const handleSubscribeNotifications = async () => {
    if (!services) return;
    
    try {
      await services.subscribeToNotifications((notification) => {
        Alert.alert(
          'Nueva Notificación',
          notification.message || 'Tienes una nueva notificación',
          [{ text: 'OK' }]
        );
        console.log('🔔 Notificación recibida:', notification);
      });
      
      Alert.alert('Éxito', 'Suscripción a notificaciones activada');
    } catch (err) {
      Alert.alert('Error', err.message);
    }
  };

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.error}>Error: {error}</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>RabbitMQ Cliente - Ejemplo Móvil</Text>
      
      {/* Estado de conexión */}
      <View style={styles.statusContainer}>
        <Text style={[
          styles.status, 
          { color: isConnected ? '#10b981' : '#ef4444' }
        ]}>
          {isConnected ? '✅ Conectado' : '❌ Desconectado'}
        </Text>
      </View>

      {/* Acciones */}
      <View style={styles.actions}>
        <Button 
          title="Obtener Saldo" 
          onPress={handleGetBalance}
          disabled={!isConnected || loading}
        />
        
        <Button 
          title="Obtener Transacciones" 
          onPress={handleGetTransactions}
          disabled={!isConnected || loading}
        />
        
        <Button 
          title="Solicitar Préstamo" 
          onPress={handleRequestLoan}
          disabled={!isConnected || loading}
        />
        
        <Button 
          title="Activar Notificaciones" 
          onPress={handleSubscribeNotifications}
          disabled={!isConnected || loading}
        />
      </View>

      {/* Resultados */}
      {balance && (
        <View style={styles.resultContainer}>
          <Text style={styles.resultTitle}>Saldo:</Text>
          <Text style={styles.resultText}>
            {balance.balance} {balance.currency}
          </Text>
        </View>
      )}

      {transactions.length > 0 && (
        <View style={styles.resultContainer}>
          <Text style={styles.resultTitle}>Transacciones:</Text>
          {transactions.map((tx, index) => (
            <Text key={index} style={styles.resultText}>
              {tx.type}: {tx.amount} {tx.currency}
            </Text>
          ))}
        </View>
      )}

      {loading && (
        <Text style={styles.loading}>Cargando...</Text>
      )}
    </ScrollView>
  );
};

// Ejemplo de uso con interceptor de Axios
const AxiosInterceptorExample = () => {
  const { interceptor, isInitialized } = useRabbitMQInterceptor();

  useEffect(() => {
    if (isInitialized && interceptor) {
      // Configurar interceptor de forma global
      console.log('Interceptor configurado:', interceptor.getStatus());
    }
  }, [isInitialized, interceptor]);

  return null;
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f8fafc'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#1e293b'
  },
  statusContainer: {
    alignItems: 'center',
    marginBottom: 20
  },
  status: {
    fontSize: 18,
    fontWeight: 'bold'
  },
  actions: {
    gap: 10,
    marginBottom: 20
  },
  resultContainer: {
    backgroundColor: '#ffffff',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#e2e8f0'
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
    color: '#1e293b'
  },
  resultText: {
    fontSize: 14,
    color: '#475569',
    marginBottom: 3
  },
  loading: {
    textAlign: 'center',
    fontSize: 16,
    color: '#64748b',
    marginTop: 20
  },
  error: {
    textAlign: 'center',
    fontSize: 16,
    color: '#ef4444',
    marginTop: 50
  }
});

export default RabbitMQExample;
export { AxiosInterceptorExample };