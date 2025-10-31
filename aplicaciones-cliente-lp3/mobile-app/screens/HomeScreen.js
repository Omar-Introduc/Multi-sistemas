import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  RefreshControl
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { styles } from '../styles/styles';
import Card from '../components/Card';
import Button from '../components/Button';

const HomeScreen = ({ navigation }) => {
  const [userData, setUserData] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      const userDataStr = await AsyncStorage.getItem('userData');
      const token = await AsyncStorage.getItem('userToken');
      
      if (userDataStr && token) {
        const user = JSON.parse(userDataStr);
        setUserData(user);
        // Aquí cargarías los datos de las cuentas desde la API
        // setAccounts(user.accounts || []);
      }
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadUserData();
    setRefreshing(false);
  };

  const handleLogout = async () => {
    await AsyncStorage.multiRemove(['userToken', 'userData']);
    navigation.replace('Login');
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <View style={styles.header}>
          <Text style={styles.headerTitle}>
            ¡Hola, {userData?.name || 'Usuario'}!
          </Text>
          <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
            <Text style={styles.logoutText}>Salir</Text>
          </TouchableOpacity>
        </View>

        <Card style={styles.balanceCard}>
          <Text style={styles.balanceTitle}>Saldo Total</Text>
          <Text style={styles.balanceAmount}>$25,430.50</Text>
          <Text style={styles.balanceDate}>Última actualización: hoy</Text>
        </Card>

        <View style={styles.quickActions}>
          <Text style={styles.sectionTitle}>Acciones Rápidas</Text>
          <View style={styles.actionButtons}>
            <Button
              title="Transferir"
              onPress={() => navigation.navigate('Transactions')}
              style={[styles.actionButton, { backgroundColor: '#4CAF50' }]}
            />
            <Button
              title="Pagar QR"
              onPress={() => navigation.navigate('QRScanner')}
              style={[styles.actionButton, { backgroundColor: '#2196F3' }]}
            />
          </View>
          <View style={styles.actionButtons}>
            <Button
              title="Generar QR"
              onPress={() => navigation.navigate('QRGenerator')}
              style={[styles.actionButton, { backgroundColor: '#FF9800' }]}
            />
            <Button
              title="Préstamo"
              onPress={() => navigation.navigate('LoanRequest')}
              style={[styles.actionButton, { backgroundColor: '#9C27B0' }]}
            />
          </View>
        </View>

        <View style={styles.recentActivity}>
          <Text style={styles.sectionTitle}>Actividad Reciente</Text>
          <Card>
            <View style={styles.transactionItem}>
              <Text style={styles.transactionText}>Pago - Supermercado ABC</Text>
              <Text style={styles.transactionAmount}>-$45.20</Text>
            </View>
            <View style={styles.transactionDivider} />
            <View style={styles.transactionItem}>
              <Text style={styles.transactionText}>Transferencia Recibida</Text>
              <Text style={styles.transactionAmountPositive}>+$1,200.00</Text>
            </View>
          </Card>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

export default HomeScreen;