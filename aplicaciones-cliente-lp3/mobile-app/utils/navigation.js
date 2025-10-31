import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

// Importar pantallas
import LoginScreen from '../screens/LoginScreen';
import HomeScreen from '../screens/HomeScreen';
import AccountsScreen from '../screens/AccountsScreen';
import TransactionsScreen from '../screens/TransactionsScreen';
import QRGeneratorScreen from '../screens/QRGeneratorScreen';
import QRScannerScreen from '../screens/QRScannerScreen';
import LoanRequestScreen from '../screens/LoanRequestScreen';
import HistoryScreen from '../screens/HistoryScreen';

// Importar autenticación
import { isAuthenticated } from './auth';

// Importar tema
import { theme } from '../styles/theme';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Componente para verificar autenticación
const AuthChecker = ({ children }) => {
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
      console.error('Error checking auth:', error);
      setIsAuth(false);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return null; // O una pantalla de loading
  }

  return children;
};

// Navegador principal (aplicación autenticada)
const MainTabNavigator = () => (
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

// Stack de autenticación (login y navegación inicial)
const AuthStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerShown: false,
      cardStyle: { backgroundColor: '#fff' }
    }}
  >
    <Stack.Screen name="Login" component={LoginScreen} />
  </Stack.Navigator>
);

// Stack principal de la aplicación
const MainStack = () => (
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
      name="Main"
      component={MainTabNavigator}
      options={{ headerShown: false }}
    />
    <Stack.Screen
      name="Home"
      component={HomeScreen}
      options={{ title: 'Inicio' }}
    />
    <Stack.Screen
      name="Accounts"
      component={AccountsScreen}
      options={{ title: 'Mis Cuentas' }}
    />
    <Stack.Screen
      name="Transactions"
      component={TransactionsScreen}
      options={{ title: 'Transacciones' }}
    />
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
    <Stack.Screen
      name="History"
      component={HistoryScreen}
      options={{ title: 'Historial' }}
    />
  </Stack.Navigator>
);

// Componente principal de navegación
const AppNavigator = () => {
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
    return null; // O una pantalla de loading
  }

  return (
    <NavigationContainer>
      {isAuth ? <MainStack /> : <AuthStack />}
    </NavigationContainer>
  );
};

// Hook para usar en componentes
export const useNavigation = () => {
  return React.useContext(React.createContext());
};

// Configuración de navegación global
export const navigationConfig = {
  // Configuraciones globales de navegación
  defaultNavigationOptions: {
    headerStyle: {
      backgroundColor: theme.colors.primary,
    },
    headerTintColor: '#fff',
    headerTitleStyle: {
      fontWeight: 'bold',
    }
  },
  // Transiciones personalizadas
  transitionConfig: () => ({
    transitionSpec: {
      duration: 300,
      easing: Easing.out(Easing.poly(4)),
      timing: Animated.timing,
    },
    screenInterpolator: sceneProps => {
      const { layout, position, scene } = sceneProps;
      const thisSceneIndex = scene.index;

      const width = layout.initWidth;
      const translateX = position.interpolate({
        inputRange: [thisSceneIndex - 1, thisSceneIndex, thisSceneIndex + 1],
        outputRange: [width, 0, 0],
        extrapolate: 'clamp',
      });

      const opacity = position.interpolate({
        inputRange: [thisSceneIndex - 1, thisSceneIndex - 0.5, thisSceneIndex],
        outputRange: [0, 1, 1],
        extrapolate: 'clamp',
      });

      return { opacity, transform: [{ translateX }] };
    },
  }),
};

export default AppNavigator;