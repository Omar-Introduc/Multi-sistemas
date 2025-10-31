import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
  TouchableOpacity
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { styles } from '../styles/styles';
import Card from '../components/Card';
import { getAccounts } from '../utils/api';

const AccountsScreen = ({ navigation }) => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const accountsData = await getAccounts();
      setAccounts(accountsData);
    } catch (error) {
      console.error('Error loading accounts:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadAccounts();
    setRefreshing(false);
  };

  const renderAccountItem = ({ item }) => (
    <TouchableOpacity
      onPress={() => navigation.navigate('Transactions', { accountId: item.id })}
    >
      <Card style={styles.accountCard}>
        <View style={styles.accountHeader}>
          <Text style={styles.accountType}>{item.type}</Text>
          <Text style={styles.accountNumber}>
            ****{item.number?.slice(-4)}
          </Text>
        </View>
        <Text style={styles.accountBalance}>${item.balance?.toLocaleString()}</Text>
        <Text style={styles.accountStatus}>{item.status}</Text>
      </Card>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Mis Cuentas</Text>
      </View>

      <FlatList
        data={accounts}
        renderItem={renderAccountItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <Text style={styles.emptyText}>No tienes cuentas registradas</Text>
        }
      />

      {accounts.length > 0 && (
        <View style={styles.summaryCard}>
          <Card>
            <Text style={styles.summaryTitle}>Resumen Total</Text>
            <Text style={styles.summaryAmount}>
              ${accounts.reduce((sum, acc) => sum + (acc.balance || 0), 0).toLocaleString()}
            </Text>
          </Card>
        </View>
      )}
    </SafeAreaView>
  );
};

export default AccountsScreen;