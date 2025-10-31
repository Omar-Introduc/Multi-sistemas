/**
 * Ejemplo de uso del cliente RabbitMQ en Electron Desktop
 * Archivo: /src/services/rabbitmq/examples/usage-example.js
 */

import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Text, 
  VStack, 
  HStack, 
  TextInput, 
  Card, 
  Badge,
  ScrollView,
  Divider,
  Alert,
  CircularProgress
} from '@chakra-ui/react';
import { 
  initializeDesktopRabbitMQ,
  useDesktopRabbitMQ,
  getDesktopRabbitMQInstance
} from '../index';

// Hook personalizado para usar RabbitMQ en Electron
const useDesktopRabbitMQ = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [services, setServices] = useState(null);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const init = async () => {
      try {
        const instance = await initializeDesktopRabbitMQ();
        setServices(instance.services);
        setIsConnected(true);
        setError(null);
        
        // Actualizar estadísticas cada 30 segundos
        const interval = setInterval(() => {
          if (instance.services) {
            setStats(instance.services.getClientStatistics());
          }
        }, 30000);
        
        return () => clearInterval(interval);
      } catch (err) {
        setError(err.message);
        setIsConnected(false);
      }
    };

    init();
  }, []);

  return { services, isConnected, error, stats };
};

// Componente de ejemplo para la aplicación desktop
const DesktopRabbitMQExample = () => {
  const { services, isConnected, error, stats } = useDesktopRabbitMQ();
  const [balance, setBalance] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loans, setLoans] = useState([]);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [requestId, setRequestId] = useState('');

  // Obtener saldo
  const handleGetBalance = async () => {
    if (!services) return;
    
    setLoading(true);
    try {
      const result = await services.getBalance({
        accountId: 'ACC_123',
        clientId: 'CLIENT_456',
        includeHistory: true
      });
      
      if (result.success) {
        setBalance(result.data);
        showAlert('Éxito', `Saldo obtenido: ${result.data.balance} ${result.data.currency}`);
      } else {
        showAlert('Error', result.error);
      }
    } catch (err) {
      showAlert('Error', err.message);
    }
    setLoading(false);
  };

  // Obtener transacciones con filtros
  const handleGetTransactions = async () => {
    if (!services) return;
    
    setLoading(true);
    try {
      const result = await services.getTransactions({
        accountId: 'ACC_123',
        startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
        endDate: new Date(),
        limit: 20,
        sortBy: 'timestamp',
        sortOrder: 'desc',
        includeDetails: true
      });
      
      if (result.success) {
        setTransactions(result.data.transactions || []);
        showAlert('Éxito', `Transacciones obtenidas: ${result.data.transactions?.length || 0}`);
      } else {
        showAlert('Error', result.error);
      }
    } catch (err) {
      showAlert('Error', err.message);
    }
    setLoading(false);
  };

  // Obtener resumen de transacciones
  const handleGetTransactionSummary = async () => {
    if (!services) return;
    
    setLoading(true);
    try {
      const result = await services.getTransactionSummary({
        accountId: 'ACC_123',
        startDate: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000),
        endDate: new Date(),
        groupBy: 'category'
      });
      
      if (result.success) {
        showAlert('Éxito', 'Resumen de transacciones obtenido');
        console.log('Resumen:', result.data);
      } else {
        showAlert('Error', result.error);
      }
    } catch (err) {
      showAlert('Error', err.message);
    }
    setLoading(false);
  };

  // Obtener préstamos
  const handleGetLoans = async () => {
    if (!services) return;
    
    setLoading(true);
    try {
      const result = await services.getLoans({
        clientId: 'CLIENT_456',
        includePayments: true,
        includeDocuments: true
      });
      
      if (result.success) {
        setLoans(result.data.loans || []);
        showAlert('Éxito', `Préstamos obtenidos: ${result.data.loans?.length || 0}`);
      } else {
        showAlert('Error', result.error);
      }
    } catch (err) {
      showAlert('Error', err.message);
    }
    setLoading(false);
  };

  // Solicitar préstamo
  const handleRequestLoan = async () => {
    if (!services) return;
    
    setLoading(true);
    try {
      const result = await services.requestLoan({
        amount: 25000,
        term: 24,
        purpose: 'Renovación de negocio',
        type: 'comercial',
        interestRate: 0.18,
        paymentFrequency: 'monthly',
        clientId: 'CLIENT_456',
        priority: 'high'
      });
      
      if (result.success) {
        setRequestId(result.requestId);
        showAlert('Éxito', `Préstamo solicitado. ID: ${result.requestId}`);
      } else {
        showAlert('Error', result.error);
      }
    } catch (err) {
      showAlert('Error', err.message);
    }
    setLoading(false);
  };

  // Actualizar perfil
  const handleUpdateProfile = async () => {
    if (!services) return;
    
    setLoading(true);
    try {
      const result = await services.updateProfile({
        clientId: 'CLIENT_456',
        firstName: 'Juan',
        lastName: 'Pérez',
        email: 'juan.perez@email.com',
        phone: '+51 999 888 777',
        occupation: 'Ingeniero',
        monthlyIncome: 5000,
        contactName: 'María Pérez',
        contactPhone: '+51 999 777 666',
        contactRelation: 'Esposa'
      });
      
      if (result.success) {
        showAlert('Éxito', 'Perfil actualizado correctamente');
      } else {
        showAlert('Error', result.error);
      }
    } catch (err) {
      showAlert('Error', err.message);
    }
    setLoading(false);
  };

  // Obtener perfil
  const handleGetProfile = async () => {
    if (!services) return;
    
    setLoading(true);
    try {
      const result = await services.getProfile('CLIENT_456', {
        includePreferences: true,
        includeStatistics: true
      });
      
      if (result.success) {
        setProfile(result.data.profile);
        showAlert('Éxito', 'Perfil obtenido correctamente');
      } else {
        showAlert('Error', result.error);
      }
    } catch (err) {
      showAlert('Error', err.message);
    }
    setLoading(false);
  };

  // Suscribirse a notificaciones
  const handleSubscribeNotifications = async () => {
    if (!services) return;
    
    try {
      await services.subscribeToNotifications((notification) => {
        // Mostrar notificación desktop
        if (window.electronAPI?.showNotification) {
          window.electronAPI.showNotification(notification.title, notification.message);
        }
        
        console.log('🔔 Notificación recibida:', notification);
      });
      
      showAlert('Éxito', 'Suscripción a notificaciones activada');
    } catch (err) {
      showAlert('Error', err.message);
    }
  };

  // Mostrar alerta
  const showAlert = (title, message) => {
    if (window.electronAPI?.showMessageBox) {
      window.electronAPI.showMessageBox({
        type: title === 'Error' ? 'error' : 'info',
        title: title,
        message: message
      });
    } else {
      console.log(`${title}: ${message}`);
    }
  };

  if (error) {
    return (
      <Box p={4}>
        <Text color="red.500" fontSize="lg" textAlign="center">
          Error: {error}
        </Text>
      </Box>
    );
  }

  return (
    <ScrollView p={4} bg="gray.50">
      <VStack spacing={6}>
        {/* Header */}
        <Box textAlign="center">
          <Text fontSize="2xl" fontWeight="bold" color="gray.800">
            RabbitMQ Cliente - Ejemplo Desktop
          </Text>
          <Text fontSize="sm" color="gray.600">
            Sistema Bancario - Aplicación Electron
          </Text>
        </Box>

        {/* Estado de conexión */}
        <Card p={4} bg="white">
          <HStack justify="space-between" align="center">
            <VStack align="start">
              <Text fontWeight="bold">Estado de Conexión</Text>
              <Badge 
                colorScheme={isConnected ? 'green' : 'red'} 
                fontSize="sm"
              >
                {isConnected ? 'Conectado' : 'Desconectado'}
              </Badge>
            </VStack>
            {isConnected && stats && (
              <VStack align="end">
                <Text fontSize="sm" color="gray.600">
                  Requests pendientes: {stats.connection.pendingRequests}
                </Text>
                <Text fontSize="sm" color="gray.600">
                  Reconexiones: {stats.connection.reconnectAttempts}
                </Text>
              </VStack>
            )}
          </HStack>
        </Card>

        {/* Acciones principales */}
        <Card p={4} bg="white">
          <Text fontSize="lg" fontWeight="bold" mb={4}>Operaciones de Cuenta</Text>
          <VStack spacing={3}>
            <Button 
              colorScheme="blue" 
              onPress={handleGetBalance}
              isDisabled={!isConnected || loading}
            >
              {loading ? 'Cargando...' : 'Obtener Saldo'}
            </Button>
            <Button 
              colorScheme="green" 
              onPress={handleGetTransactions}
              isDisabled={!isConnected || loading}
            >
              Obtener Transacciones
            </Button>
            <Button 
              colorScheme="purple" 
              onPress={handleGetTransactionSummary}
              isDisabled={!isConnected || loading}
            >
              Resumen de Transacciones
            </Button>
          </VStack>
        </Card>

        {/* Operaciones de préstamos */}
        <Card p={4} bg="white">
          <Text fontSize="lg" fontWeight="bold" mb={4}>Operaciones de Préstamos</Text>
          <VStack spacing={3}>
            <Button 
              colorScheme="orange" 
              onPress={handleGetLoans}
              isDisabled={!isConnected || loading}
            >
              Obtener Préstamos
            </Button>
            <Button 
              colorScheme="red" 
              onPress={handleRequestLoan}
              isDisabled={!isConnected || loading}
            >
              Solicitar Préstamo
            </Button>
          </VStack>
          
          {requestId && (
            <Box mt={3} p={2} bg="green.50" borderRadius="md">
              <Text fontSize="sm" color="green.700">
                ID de solicitud: {requestId}
              </Text>
            </Box>
          )}
        </Card>

        {/* Operaciones de perfil */}
        <Card p={4} bg="white">
          <Text fontSize="lg" fontWeight="bold" mb={4}>Gestión de Perfil</Text>
          <VStack spacing={3}>
            <Button 
              colorScheme="teal" 
              onPress={handleGetProfile}
              isDisabled={!isConnected || loading}
            >
              Obtener Perfil
            </Button>
            <Button 
              colorScheme="cyan" 
              onPress={handleUpdateProfile}
              isDisabled={!isConnected || loading}
            >
              Actualizar Perfil
            </Button>
          </VStack>
        </Card>

        {/* Notificaciones */}
        <Card p={4} bg="white">
          <Text fontSize="lg" fontWeight="bold" mb={4}>Notificaciones</Text>
          <Button 
            colorScheme="yellow" 
            onPress={handleSubscribeNotifications}
            isDisabled={!isConnected}
          >
            Activar Notificaciones en Tiempo Real
          </Button>
        </Card>

        {/* Resultados */}
        {balance && (
          <Card p={4} bg="white">
            <Text fontSize="lg" fontWeight="bold" mb={2}>Saldo Actual</Text>
            <Text fontSize="2xl" color="green.600" fontWeight="bold">
              {balance.balance} {balance.currency}
            </Text>
            <Text fontSize="sm" color="gray.600" mt={1}>
              Última actualización: {new Date(balance.lastUpdate).toLocaleString()}
            </Text>
          </Card>
        )}

        {transactions.length > 0 && (
          <Card p={4} bg="white">
            <Text fontSize="lg" fontWeight="bold" mb={2}>
              Transacciones Recientes ({transactions.length})
            </Text>
            <VStack spacing={2}>
              {transactions.slice(0, 5).map((tx, index) => (
                <HStack key={index} justify="space-between" w="full" p={2} bg="gray.50" borderRadius="md">
                  <VStack align="start">
                    <Text fontSize="sm" fontWeight="medium">{tx.type}</Text>
                    <Text fontSize="xs" color="gray.600">{tx.description}</Text>
                  </VStack>
                  <VStack align="end">
                    <Text fontSize="sm" fontWeight="bold" color={tx.amount > 0 ? 'green.600' : 'red.600'}>
                      {tx.amount > 0 ? '+' : ''}{tx.amount} {tx.currency}
                    </Text>
                    <Text fontSize="xs" color="gray.500">
                      {new Date(tx.timestamp).toLocaleDateString()}
                    </Text>
                  </VStack>
                </HStack>
              ))}
            </VStack>
          </Card>
        )}

        {loans.length > 0 && (
          <Card p={4} bg="white">
            <Text fontSize="lg" fontWeight="bold" mb={2}>
              Préstamos ({loans.length})
            </Text>
            <VStack spacing={2}>
              {loans.map((loan, index) => (
                <HStack key={index} justify="space-between" w="full" p={2} bg="gray.50" borderRadius="md">
                  <VStack align="start">
                    <Text fontSize="sm" fontWeight="medium">ID: {loan.id}</Text>
                    <Text fontSize="xs" color="gray.600">{loan.purpose}</Text>
                  </VStack>
                  <VStack align="end">
                    <Text fontSize="sm" fontWeight="bold">
                      {loan.amount} {loan.currency}
                    </Text>
                    <Badge colorScheme={loan.status === 'active' ? 'green' : 'orange'} fontSize="xs">
                      {loan.status}
                    </Badge>
                  </VStack>
                </HStack>
              ))}
            </VStack>
          </Card>
        )}

        {profile && (
          <Card p={4} bg="white">
            <Text fontSize="lg" fontWeight="bold" mb={2}>Perfil del Cliente</Text>
            <VStack spacing={1} align="start">
              <Text><strong>Nombre:</strong> {profile.firstName} {profile.lastName}</Text>
              <Text><strong>Email:</strong> {profile.email}</Text>
              <Text><strong>Teléfono:</strong> {profile.phone}</Text>
              <Text><strong>Ocupación:</strong> {profile.occupation}</Text>
              <Text><strong>Ingreso mensual:</strong> {profile.monthlyIncome}</Text>
            </VStack>
          </Card>
        )}
      </VStack>
    </ScrollView>
  );
};

export default DesktopRabbitMQExample;