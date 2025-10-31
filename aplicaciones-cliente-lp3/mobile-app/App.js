import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

// Importar pantallas
import LoginScreen from './screens/LoginScreen';
import HomeScreen from './screens/HomeScreen';
import AccountsScreen from './screens/AccountsScreen';
import TransactionsScreen from './screens/TransactionsScreen';
import QRGeneratorScreen from './screens/QRGeneratorScreen';
import QRScannerScreen from './screens/QRScannerScreen';
import LoanRequestScreen from './screens/LoanRequestScreen';
import HistoryScreen from './screens/HistoryScreen';

// Importar utilidades
import { isAuthenticated } from './utils/auth';
import { theme } from './styles/theme';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Componente de navegación principal
export default function App() {
  const [isAuth, setIsAuth] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const authenticated = await isAuthenticated();
      setIsAuth(authenticated);
    } catch (error) {
      console.error('Error checking authentication:', error);
      setIsAuth(false);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return null; // O una pantalla de loading personalizada
  }

  return (
    <>
      <StatusBar style="light" backgroundColor={theme.colors.primary} />
      <NavigationContainer>
        {isAuth ? <MainApp /> : <AuthApp />}
      </NavigationContainer>
    </>
  );
}

// Stack de autenticación
const AuthApp = () => (
  <Stack.Navigator
    screenOptions={{
      headerShown: false,
      cardStyle: { backgroundColor: '#fff' }
    }}
  >
    <Stack.Screen 
      name="Login" 
      component={LoginScreen}
      options={{
        cardStyleInterpolator: ({ current }) => ({
          cardStyle: {
            opacity: current.progress,
          },
        }),
      }}
    />
  </Stack.Navigator>
);

// Navegador principal con tabs
const MainApp = () => (
  <Tab.Navigator
    screenOptions={({ route }) => ({
      tabBarIcon: ({ focused, color, size }) => {
        let iconName;

        switch (route.name) {
          case 'HomeTab':
            iconName = focused ? 'home' : 'home-outline';
            break;
          case 'AccountsTab':
            iconName = focused ? 'card' : 'card-outline';
            break;
          case 'TransactionsTab':
            iconName = focused ? 'swap-horizontal' : 'swap-horizontal-outline';
            break;
          case 'HistoryTab':
            iconName = focused ? 'time' : 'time-outline';
            break;
          default:
            iconName = 'home-outline';
        }

        return <Ionicons name={iconName} size={size} color={color} />;
      },
      tabBarActiveTintColor: theme.colors.primary,
      tabBarInactiveTintColor: theme.colors.textLight,
      tabBarStyle: {
        backgroundColor: '#fff',
        borderTopWidth: 1,
        borderTopColor: theme.colors.border,
        paddingBottom: 5,
        paddingTop: 5,
        height: 60
      },
      headerShown: false
    })}
  >
    <Tab.Screen 
      name="HomeTab" 
      component={HomeScreen} 
      options={{ title: 'Inicio' }}
    />
    <Tab.Screen 
      name="AccountsTab" 
      component={AccountsScreen} 
      options={{ title: 'Cuentas' }}
    />
    <Tab.Screen 
      name="TransactionsTab" 
      component={TransactionsScreen} 
      options={{ title: 'Transacciones' }}
    />
    <Tab.Screen 
      name="HistoryTab" 
      component={HistoryScreen} 
      options={{ title: 'Historial' }}
    />
  </Tab.Navigator>
);

// Stack adicional para funcionalidades específicas
const AdditionalStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerStyle: {
        backgroundColor: theme.colors.primary,
        shadowOpacity: 0,
        elevation: 0
      },
      headerTintColor: '#fff',
      headerTitleStyle: {
        fontWeight: 'bold',
        fontSize: 18
      },
      cardStyle: { backgroundColor: '#fff' }
    }}
  >
    <Stack.Screen
      name="QRGenerator"
      component={QRGeneratorScreen}
      options={{
        title: 'Generar QR',
        headerShown: true
      }}
    />
    <Stack.Screen
      name="QRScanner"
      component={QRScannerScreen}
      options={{
        title: 'Escanear QR',
        headerShown: false // La cámara necesita pantalla completa
      }}
    />
    <Stack.Screen
      name="LoanRequest"
      component={LoanRequestScreen}
      options={{
        title: 'Solicitar Préstamo',
        headerShown: true
      }}
    />
  </Stack.Navigator>
);