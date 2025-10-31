import React, { useState } from 'react';
import { View, Text, StyleSheet, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import QRScannerComponent from '../components/QRScannerComponent';
import { styles } from '../styles/styles';
import { QRGeneratorService } from '../services/qrGeneratorService';

const QRScannerScreen = ({ navigation }) => {
  const handleScanSuccess = async (qrData) => {
    try {
      // Process the QR code
      const result = await QRGeneratorService.processQRCode(JSON.stringify(qrData));
      
      if (result.success) {
        showSuccessAlert(result);
      } else {
        showErrorAlert(result.error || 'No se pudo procesar el código QR');
      }
    } catch (error) {
      showErrorAlert('Ocurrió un error al procesar el código QR');
      console.error('QR Processing Error:', error);
    }
  };

  const showSuccessAlert = (result) => {
    const { data } = result;
    let title = 'QR Procesado';
    let message = '';
    
    switch (data.type) {
      case 'payment':
        title = 'Pago Procesado';
        message = `Pago de $${data.amount} a ${data.merchant || 'Comercio'} exitoso`;
        break;
      case 'transfer':
        title = 'Transferencia Procesada';
        message = `Transferencia a ${data.recipient?.name} procesada exitosamente`;
        break;
      case 'request':
        title = 'Solicitud Procesada';
        message = `Solicitud de pago de $${data.amount} procesada`;
        break;
    }
    
    Alert.alert(title, message, [
      {
        text: 'Ver Detalles',
        onPress: () => showTransactionDetails(result)
      },
      {
        text: 'OK',
        onPress: () => navigation.goBack()
      }
    ]);
  };

  const showErrorAlert = (message) => {
    Alert.alert('Error', message, [
      { text: 'OK', onPress: () => navigation.goBack() }
    ]);
  };

  const showTransactionDetails = (result) => {
    const { data } = result;
    let details = '';
    
    switch (data.type) {
      case 'payment':
        details = `Tipo: Pago\nMonto: $${data.amount}\nComercio: ${data.merchant || 'No especificado'}\nDescripción: ${data.description}`;
        break;
      case 'transfer':
        details = `Tipo: Transferencia\nDestinatario: ${data.recipient?.name}\nCuenta: ${data.recipient?.account}\nDescripción: ${data.description}`;
        break;
      case 'request':
        details = `Tipo: Solicitud\nMonto: $${data.amount}\nConcepto: ${data.description}\nSolicitante: ${data.recipient?.name || 'No especificado'}`;
        break;
    }
    
    Alert.alert('Detalles de la Transacción', details, [
      { text: 'OK', onPress: () => navigation.goBack() }
    ]);
  };

  const handleCancel = () => {
    navigation.goBack();
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Escanear Código QR</Text>
        <Text style={styles.subtitle}>
          Apunta la cámara al código QR para procesar la transacción
        </Text>
      </View>
      
      <QRScannerComponent
        onScanSuccess={handleScanSuccess}
        onCancel={handleCancel}
      />
    </SafeAreaView>
  );
};

export default QRScannerScreen;