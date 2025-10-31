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
import { getHistory } from '../utils/api';

const HistoryScreen = ({ navigation, route }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filterType, setFilterType] = useState('all'); // all, transactions, payments, loans

  useEffect(() => {
    loadHistory();
  }, [filterType]);

  const loadHistory = async () => {
    try {
      const historyData = await getHistory(filterType);
      setHistory(historyData);
    } catch (error) {
      console.error('Error loading history:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadHistory();
    setRefreshing(false);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const getHistoryIcon = (type) => {
    switch (type) {
      case 'transaction':
        return '💸';
      case 'payment':
        return '💳';
      case 'loan':
        return '🏦';
      case 'qr_generated':
        return '📱';
      case 'qr_scanned':
        return '📷';
      default:
        return '📋';
    }
  };

  const renderHistoryItem = ({ item }) => (
    <TouchableOpacity
      onPress={() => {
        if (item.type === 'transaction') {
          navigation.navigate('Transactions');
        } else if (item.type === 'loan') {
          navigation.navigate('LoanRequest');
        }
      }}
    >
      <Card style={styles.historyCard}>
        <View style={styles.historyHeader}>
          <Text style={styles.historyIcon}>
            {getHistoryIcon(item.type)}
          </Text>
          <View style={styles.historyInfo}>
            <Text style={styles.historyTitle}>{item.title}</Text>
            <Text style={styles.historyDate}>{formatDate(item.date)}</Text>
          </View>
          <View style={styles.historyStatus}>
            <Text style={[
              styles.historyStatusText,
              { color: getStatusColor(item.status) }
            ]}>
              {item.status}
            </Text>
          </View>
        </View>
        
        <View style={styles.historyDetails}>
          <Text style={styles.historyDescription}>{item.description}</Text>
          {item.amount && (
            <Text style={[
              styles.historyAmount,
              item.type === 'income' ? styles.amountPositive : styles.amountNegative
            ]}>
              {item.type === 'income' ? '+' : '-'}${Math.abs(item.amount).toLocaleString()}
            </Text>
          )}
        </View>

        {item.additionalInfo && (
          <View style={styles.historyAdditional}>
            <Text style={styles.additionalInfo}>{item.additionalInfo}</Text>
          </View>
        )}
      </Card>
    </TouchableOpacity>
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'completado':
      case 'exitoso':
        return '#4CAF50';
      case 'pendiente':
        return '#FF9800';
      case 'rechazado':
      case 'fallido':
        return '#F44336';
      default:
        return '#757575';
    }
  };

  const renderFilterButton = (type, label) => (
    <TouchableOpacity
      style={[
        styles.filterButton,
        filterType === type && styles.filterButtonActive
      ]}
      onPress={() => setFilterType(type)}
    >
      <Text style={[
        styles.filterButtonText,
        filterType === type && styles.filterButtonTextActive
      ]}>
        {label}
      </Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Historial</Text>
      </View>

      <View style={styles.filterContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {renderFilterButton('all', 'Todo')}
          {renderFilterButton('transactions', 'Transacciones')}
          {renderFilterButton('payments', 'Pagos')}
          {renderFilterButton('loans', 'Préstamos')}
          {renderFilterButton('qr', 'QR')}
        </ScrollView>
      </View>

      <FlatList
        data={history}
        renderItem={renderHistoryItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyIcon}>📊</Text>
            <Text style={styles.emptyText}>No hay historial disponible</Text>
          </View>
        }
      />

      {history.length > 0 && (
        <View style={styles.summaryContainer}>
          <Card style={styles.summaryCard}>
            <Text style={styles.summaryTitle}>Resumen del Período</Text>
            <Text style={styles.summaryText}>
              Total de actividades: {history.length}
            </Text>
          </Card>
        </View>
      )}
    </SafeAreaView>
  );
};

export default HistoryScreen;