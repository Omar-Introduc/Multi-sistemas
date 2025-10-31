import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  Modal,
  Alert,
  TextInput
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { styles } from '../styles/styles';
import Card from '../components/Card';
import Button from '../components/Button';
import ApiService from '../services/apiService';
import { TransactionService } from '../services/transactionService';

const TransactionsScreen = ({ navigation, route }) => {
  const [transactions, setTransactions] = useState([]);
  const [filteredTransactions, setFilteredTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [filters, setFilters] = useState({
    dateFrom: '',
    dateTo: '',
    type: 'all',
    category: 'all',
    minAmount: '',
    maxAmount: ''
  });
  
  const accountId = route.params?.accountId;

  useEffect(() => {
    loadTransactions();
  }, [accountId]);

  useEffect(() => {
    applyFilters();
  }, [transactions, searchText, filters]);

  const loadTransactions = async () => {
    try {
      const transactionsData = await ApiService.getTransactions(accountId);
      setTransactions(transactionsData);
    } catch (error) {
      console.error('Error loading transactions:', error);
      // Use mock data if API fails
      setTransactions(TransactionService.getMockTransactions());
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadTransactions();
    setRefreshing(false);
  };

  const applyFilters = () => {
    let filtered = [...transactions];

    // Search filter
    if (searchText) {
      const searchLower = searchText.toLowerCase();
      filtered = filtered.filter(transaction =>
        transaction.description.toLowerCase().includes(searchLower) ||
        transaction.category.toLowerCase().includes(searchLower) ||
        (transaction.reference && transaction.reference.toLowerCase().includes(searchLower))
      );
    }

    // Date filters
    if (filters.dateFrom) {
      filtered = filtered.filter(transaction =>
        new Date(transaction.date) >= new Date(filters.dateFrom)
      );
    }

    if (filters.dateTo) {
      filtered = filtered.filter(transaction =>
        new Date(transaction.date) <= new Date(filters.dateTo)
      );
    }

    // Type filter
    if (filters.type !== 'all') {
      filtered = filtered.filter(transaction =>
        filters.type === 'income' ? transaction.type === 'credit' || transaction.amount > 0 :
        filters.type === 'expense' ? transaction.type === 'debit' || transaction.amount < 0 :
        true
      );
    }

    // Category filter
    if (filters.category !== 'all') {
      filtered = filtered.filter(transaction =>
        transaction.category === filters.category
      );
    }

    // Amount filters
    if (filters.minAmount) {
      filtered = filtered.filter(transaction =>
        Math.abs(transaction.amount) >= parseFloat(filters.minAmount)
      );
    }

    if (filters.maxAmount) {
      filtered = filtered.filter(transaction =>
        Math.abs(transaction.amount) <= parseFloat(filters.maxAmount)
      );
    }

    // Sort by date (newest first)
    filtered.sort((a, b) => new Date(b.date) - new Date(a.date));

    setFilteredTransactions(filtered);
  };

  const clearFilters = () => {
    setFilters({
      dateFrom: '',
      dateTo: '',
      type: 'all',
      category: 'all',
      minAmount: '',
      maxAmount: ''
    });
    setSearchText('');
  };

  const getUniqueCategories = () => {
    const categories = [...new Set(transactions.map(t => t.category))];
    return categories.map(category => ({ label: category, value: category }));
  };

  const getTransactionStats = () => {
    const income = filteredTransactions
      .filter(t => t.type === 'credit' || t.amount > 0)
      .reduce((sum, t) => sum + t.amount, 0);
    
    const expenses = filteredTransactions
      .filter(t => t.type === 'debit' || t.amount < 0)
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);

    return {
      total: filteredTransactions.length,
      income,
      expenses,
      net: income - expenses
    };
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderTransactionItem = ({ item }) => (
    <TouchableOpacity
      onPress={() => showTransactionDetails(item)}
      style={styles.transactionCard}
    >
      <Card style={{ padding: 15 }}>
        <View style={styles.transactionHeader}>
          <View style={styles.transactionInfo}>
            <Text style={styles.transactionDescription}>{item.description}</Text>
            <Text style={styles.transactionDate}>
              {formatDate(item.date)} a las {formatTime(item.date)}
            </Text>
            {item.reference && (
              <Text style={styles.transactionReference}>
                Ref: {item.reference}
              </Text>
            )}
          </View>
          <View style={styles.transactionAmountContainer}>
            <Text
              style={[
                styles.transactionAmount,
                item.amount >= 0 ? styles.amountPositive : styles.amountNegative
              ]}
            >
              {item.amount >= 0 ? '+' : '-'}${Math.abs(item.amount).toLocaleString()}
            </Text>
            <Text style={styles.transactionBalance}>
              Saldo: ${item.balance?.toLocaleString()}
            </Text>
          </View>
        </View>
        <View style={styles.transactionFooter}>
          <View style={styles.categoryContainer}>
            <Text style={styles.transactionCategory}>{item.category}</Text>
          </View>
          <View style={styles.statusContainer}>
            <View style={[
              styles.statusIndicator,
              { backgroundColor: getStatusColor(item.status) }
            ]} />
            <Text style={styles.transactionStatus}>{item.status}</Text>
          </View>
        </View>
      </Card>
    </TouchableOpacity>
  );

  const showTransactionDetails = (transaction) => {
    Alert.alert(
      'Detalles de Transacción',
      `Descripción: ${transaction.description}\n` +
      `Monto: $${transaction.amount.toLocaleString()}\n` +
      `Fecha: ${formatDate(transaction.date)}\n` +
      `Categoría: ${transaction.category}\n` +
      `Estado: ${transaction.status}\n` +
      (transaction.reference ? `Referencia: ${transaction.reference}` : ''),
      [{ text: 'OK' }]
    );
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completado':
      case 'completada':
        return '#4CAF50';
      case 'pendiente':
        return '#FF9800';
      case 'rechazado':
        return '#f44336';
      default:
        return '#9E9E9E';
    }
  };

  const renderFilterModal = () => (
    <Modal
      visible={showFilters}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <SafeAreaView style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Filtros de Transacciones</Text>
          <TouchableOpacity onPress={() => setShowFilters(false)}>
            <Text style={styles.modalClose}>Cerrar</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.modalContent}>
          <Card style={styles.filterSection}>
            <Text style={styles.filterSectionTitle}>Búsqueda</Text>
            <TextInput
              style={styles.searchInput}
              placeholder="Buscar transacciones..."
              value={searchText}
              onChangeText={setSearchText}
            />
          </Card>

          <Card style={styles.filterSection}>
            <Text style={styles.filterSectionTitle}>Filtros</Text>
            
            <View style={styles.dateFilters}>
              <View style={styles.dateInput}>
                <Text style={styles.inputLabel}>Desde</Text>
                <TextInput
                  style={styles.dateTextInput}
                  placeholder="YYYY-MM-DD"
                  value={filters.dateFrom}
                  onChangeText={(value) => setFilters(prev => ({ ...prev, dateFrom: value }))}
                />
              </View>
              <View style={styles.dateInput}>
                <Text style={styles.inputLabel}>Hasta</Text>
                <TextInput
                  style={styles.dateTextInput}
                  placeholder="YYYY-MM-DD"
                  value={filters.dateTo}
                  onChangeText={(value) => setFilters(prev => ({ ...prev, dateTo: value }))}
                />
              </View>
            </View>

            <View style={styles.amountFilters}>
              <View style={styles.amountInput}>
                <Text style={styles.inputLabel}>Monto Mínimo</Text>
                <TextInput
                  style={styles.textInput}
                  placeholder="0.00"
                  value={filters.minAmount}
                  onChangeText={(value) => setFilters(prev => ({ ...prev, minAmount: value }))}
                  keyboardType="numeric"
                />
              </View>
              <View style={styles.amountInput}>
                <Text style={styles.inputLabel}>Monto Máximo</Text>
                <TextInput
                  style={styles.textInput}
                  placeholder="1000.00"
                  value={filters.maxAmount}
                  onChangeText={(value) => setFilters(prev => ({ ...prev, maxAmount: value }))}
                  keyboardType="numeric"
                />
              </View>
            </View>
          </Card>

          <View style={styles.modalActions}>
            <Button
              title="Limpiar Filtros"
              onPress={clearFilters}
              style={styles.clearButton}
            />
            <Button
              title="Aplicar"
              onPress={() => setShowFilters(false)}
              style={styles.applyButton}
            />
          </View>
        </View>
      </SafeAreaView>
    </Modal>
  );

  const stats = getTransactionStats();

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>
          {accountId ? 'Transacciones' : 'Todas las Transacciones'}
        </Text>
        <View style={styles.headerActions}>
          <TouchableOpacity
            style={styles.filterButton}
            onPress={() => setShowFilters(true)}
          >
            <Text style={styles.filterText}>Filtrar</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.refreshButton}
            onPress={onRefresh}
          >
            <Text style={styles.filterText}>Actualizar</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Stats Card */}
      <Card style={styles.statsCard}>
        <View style={styles.statsRow}>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Total</Text>
            <Text style={styles.statValue}>{stats.total}</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Ingresos</Text>
            <Text style={[styles.statValue, styles.incomeText]}>
              +${stats.income.toLocaleString()}
            </Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Gastos</Text>
            <Text style={[styles.statValue, styles.expenseText]}>
              -${stats.expenses.toLocaleString()}
            </Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Neto</Text>
            <Text style={[styles.statValue, stats.net >= 0 ? styles.incomeText : styles.expenseText]}>
              ${stats.net.toLocaleString()}
            </Text>
          </View>
        </View>
      </Card>

      <FlatList
        data={filteredTransactions}
        renderItem={renderTransactionItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <Card style={styles.emptyCard}>
            <Text style={styles.emptyText}>
              {searchText || Object.values(filters).some(f => f !== '' && f !== 'all') 
                ? 'No se encontraron transacciones con los filtros aplicados'
                : 'No hay transacciones disponibles'
              }
            </Text>
          </Card>
        }
      />

      <TouchableOpacity
        style={styles.newTransactionButton}
        onPress={() => Alert.alert('Nueva Transacción', 'Próximamente disponible')}
      >
        <Text style={styles.newTransactionButtonText}>+ Nueva Transacción</Text>
      </TouchableOpacity>

      {renderFilterModal()}
    </SafeAreaView>
  );
};

export default TransactionsScreen;