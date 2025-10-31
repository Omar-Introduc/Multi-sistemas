import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import QRCode from 'react-native-qrcode-svg';
import Card from './Card';
import Button from './Button';
import Input from './Input';
import { QRGeneratorService } from '../services/qrGeneratorService';

const QRGeneratorComponent = ({ onClose, onGenerate }) => {
  const [qrType, setQrType] = useState('payment');
  const [loading, setLoading] = useState(false);
  const [generatedQR, setGeneratedQR] = useState(null);
  const [formData, setFormData] = useState({
    amount: '',
    description: '',
    merchant: '',
    recipientName: '',
    recipientAccount: '',
    reference: '',
  });

  const qrTypes = [
    { key: 'payment', label: 'Pago', icon: '💳' },
    { key: 'transfer', label: 'Transferencia', icon: '💸' },
    { key: 'request', label: 'Solicitud de Pago', icon: '📥' },
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateForm = () => {
    if (qrType === 'payment') {
      if (!formData.amount || parseFloat(formData.amount) <= 0) {
        Alert.alert('Error', 'Por favor ingresa un monto válido');
        return false;
      }
      if (!formData.description.trim()) {
        Alert.alert('Error', 'Por favor ingresa una descripción');
        return false;
      }
    }
    
    if (qrType === 'transfer') {
      if (!formData.recipientAccount.trim()) {
        Alert.alert('Error', 'Por favor ingresa el número de cuenta del destinatario');
        return false;
      }
      if (!formData.recipientName.trim()) {
        Alert.alert('Error', 'Por favor ingresa el nombre del destinatario');
        return false;
      }
    }
    
    if (qrType === 'request') {
      if (!formData.amount || parseFloat(formData.amount) <= 0) {
        Alert.alert('Error', 'Por favor ingresa un monto válido');
        return false;
      }
    }
    
    return true;
  };

  const generateQR = async () => {
    if (!validateForm()) return;
    
    setLoading(true);
    try {
      const qrData = await QRGeneratorService.generateQRCode({
        type: qrType,
        ...formData,
        amount: formData.amount ? parseFloat(formData.amount) : undefined,
        timestamp: Date.now(),
        merchantId: 'demo-merchant',
      });
      
      setGeneratedQR(qrData);
      
      if (onGenerate) {
        onGenerate(qrData);
      }
      
    } catch (error) {
      Alert.alert('Error', 'No se pudo generar el código QR');
      console.error('QR Generation Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const clearForm = () => {
    setFormData({
      amount: '',
      description: '',
      merchant: '',
      recipientName: '',
      recipientAccount: '',
      reference: '',
    });
    setGeneratedQR(null);
  };

  const copyToClipboard = async () => {
    if (!generatedQR?.data) return;
    
    try {
      // Note: react-native-clipboard is not imported, so we'll show the data
      Alert.alert(
        'Código QR Data',
        'Copia este texto:',
        [
          { text: generatedQR.data, style: 'default' },
          { text: 'Cerrar', style: 'cancel' }
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'No se pudo copiar al portapapeles');
    }
  };

  const renderPaymentForm = () => (
    <View style={styles.formSection}>
      <Input
        label="Monto (USD)"
        value={formData.amount}
        onChangeText={(value) => handleInputChange('amount', value)}
        placeholder="0.00"
        keyboardType="numeric"
      />
      
      <Input
        label="Descripción"
        value={formData.description}
        onChangeText={(value) => handleInputChange('description', value)}
        placeholder="Descripción del pago"
      />
      
      <Input
        label="Comercio (Opcional)"
        value={formData.merchant}
        onChangeText={(value) => handleInputChange('merchant', value)}
        placeholder="Nombre del comercio"
      />
      
      <Input
        label="Referencia (Opcional)"
        value={formData.reference}
        onChangeText={(value) => handleInputChange('reference', value)}
        placeholder="Número de referencia"
      />
    </View>
  );

  const renderTransferForm = () => (
    <View style={styles.formSection}>
      <Input
        label="Nombre del Destinatario"
        value={formData.recipientName}
        onChangeText={(value) => handleInputChange('recipientName', value)}
        placeholder="Nombre completo"
      />
      
      <Input
        label="Número de Cuenta"
        value={formData.recipientAccount}
        onChangeText={(value) => handleInputChange('recipientAccount', value)}
        placeholder="Número de cuenta"
        keyboardType="numeric"
      />
      
      <Input
        label="Descripción (Opcional)"
        value={formData.description}
        onChangeText={(value) => handleInputChange('description', value)}
        placeholder="Descripción de la transferencia"
      />
      
      <Input
        label="Referencia (Opcional)"
        value={formData.reference}
        onChangeText={(value) => handleInputChange('reference', value)}
        placeholder="Número de referencia"
      />
    </View>
  );

  const renderRequestForm = () => (
    <View style={styles.formSection}>
      <Input
        label="Monto Solicitado (USD)"
        value={formData.amount}
        onChangeText={(value) => handleInputChange('amount', value)}
        placeholder="0.00"
        keyboardType="numeric"
      />
      
      <Input
        label="Concepto"
        value={formData.description}
        onChangeText={(value) => handleInputChange('description', value)}
        placeholder="Concepto del pago solicitado"
      />
      
      <Input
        label="Destinatario (Opcional)"
        value={formData.recipientName}
        onChangeText={(value) => handleInputChange('recipientName', value)}
        placeholder="Nombre de quien debe pagar"
      />
    </View>
  );

  const renderQRDisplay = () => {
    if (!generatedQR) return null;
    
    return (
      <Card style={styles.qrDisplayCard}>
        <Text style={styles.qrTitle}>Código QR Generado</Text>
        
        <View style={styles.qrContainer}>
          <QRCode
            value={generatedQR.data}
            size={200}
            color="#000000"
            backgroundColor="#FFFFFF"
            logoBackgroundColor="#FFFFFF"
          />
        </View>
        
        <Text style={styles.qrType}>
          Tipo: {qrTypes.find(t => t.key === qrType)?.label}
        </Text>
        
        {generatedQR.amount && (
          <Text style={styles.qrAmount}>
            Monto: ${generatedQR.amount}
          </Text>
        )}
        
        <View style={styles.qrActions}>
          <TouchableOpacity
            style={styles.copyButton}
            onPress={copyToClipboard}
          >
            <Text style={styles.copyButtonText}>Copiar Data</Text>
          </TouchableOpacity>
          
          <Button
            title="Limpiar"
            onPress={clearForm}
            style={styles.clearButton}
          />
        </View>
      </Card>
    );
  };

  return (
    <View style={styles.container}>
      <Card style={styles.headerCard}>
        <Text style={styles.title}>Generador de Códigos QR</Text>
        <Text style={styles.subtitle}>
          Genera códigos QR para pagos, transferencias y solicitudes
        </Text>
      </Card>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* QR Type Selection */}
        <Card style={styles.typeSelector}>
          <Text style={styles.sectionTitle}>Tipo de QR</Text>
          <View style={styles.typeButtons}>
            {qrTypes.map(type => (
              <TouchableOpacity
                key={type.key}
                style={[
                  styles.typeButton,
                  qrType === type.key && styles.typeButtonActive
                ]}
                onPress={() => setQrType(type.key)}
              >
                <Text style={styles.typeIcon}>{type.icon}</Text>
                <Text style={[
                  styles.typeLabel,
                  qrType === type.key && styles.typeLabelActive
                ]}>
                  {type.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </Card>

        {/* Form */}
        <Card style={styles.formCard}>
          <Text style={styles.sectionTitle}>
            Información {qrTypes.find(t => t.key === qrType)?.label}
          </Text>
          
          {qrType === 'payment' && renderPaymentForm()}
          {qrType === 'transfer' && renderTransferForm()}
          {qrType === 'request' && renderRequestForm()}
          
          <Button
            title={loading ? 'Generando...' : 'Generar Código QR'}
            onPress={generateQR}
            disabled={loading}
            style={styles.generateButton}
          />
        </Card>

        {/* Generated QR Display */}
        {renderQRDisplay()}
      </ScrollView>

      <View style={styles.footer}>
        <Button
          title="Cerrar"
          onPress={onClose}
          style={styles.closeButton}
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  headerCard: {
    margin: 15,
    marginBottom: 5,
    padding: 20,
    backgroundColor: '#2196F3',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 14,
    color: '#fff',
    textAlign: 'center',
    marginTop: 5,
  },
  scrollView: {
    flex: 1,
  },
  typeSelector: {
    margin: 15,
    marginTop: 5,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  typeButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  typeButton: {
    flex: 1,
    padding: 15,
    marginHorizontal: 5,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
  },
  typeButtonActive: {
    backgroundColor: '#2196F3',
  },
  typeIcon: {
    fontSize: 24,
    marginBottom: 5,
  },
  typeLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  typeLabelActive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  formCard: {
    margin: 15,
    marginTop: 5,
  },
  formSection: {
    marginBottom: 20,
  },
  generateButton: {
    backgroundColor: '#4CAF50',
    marginTop: 20,
  },
  qrDisplayCard: {
    margin: 15,
    marginTop: 5,
    alignItems: 'center',
    padding: 20,
  },
  qrTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
  },
  qrContainer: {
    marginVertical: 20,
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  qrType: {
    fontSize: 14,
    color: '#666',
    marginTop: 15,
  },
  qrAmount: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 5,
  },
  qrActions: {
    flexDirection: 'row',
    marginTop: 20,
    gap: 10,
  },
  copyButton: {
    padding: 10,
    backgroundColor: '#2196F3',
    borderRadius: 6,
  },
  copyButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  clearButton: {
    backgroundColor: '#f44336',
    flex: 1,
  },
  footer: {
    padding: 15,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  closeButton: {
    backgroundColor: '#666',
  },
});

export default QRGeneratorComponent;