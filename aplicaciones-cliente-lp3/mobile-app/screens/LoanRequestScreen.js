import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { styles } from '../styles/styles';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';

const LoanRequestScreen = ({ navigation }) => {
  const [formData, setFormData] = useState({
    amount: '',
    term: '',
    purpose: '',
    income: '',
    employment: ''
  });

  const [loading, setLoading] = useState(false);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateForm = () => {
    const { amount, term, purpose, income, employment } = formData;
    
    if (!amount || parseFloat(amount) <= 0) {
      Alert.alert('Error', 'Por favor ingresa un monto válido');
      return false;
    }

    if (!term || parseInt(term) <= 0) {
      Alert.alert('Error', 'Por favor ingresa un plazo válido');
      return false;
    }

    if (!purpose.trim()) {
      Alert.alert('Error', 'Por favor describe el propósito del préstamo');
      return false;
    }

    if (!income || parseFloat(income) <= 0) {
      Alert.alert('Error', 'Por favor ingresa tus ingresos mensuales');
      return false;
    }

    if (!employment.trim()) {
      Alert.alert('Error', 'Por favor ingresa tu situación laboral');
      return false;
    }

    return true;
  };

  const submitLoanRequest = async () => {
    if (!validateForm()) return;

    setLoading(true);
    try {
      // Aquí enviarías la solicitud a través de la API
      Alert.alert(
        'Solicitud Enviada',
        'Tu solicitud de préstamo ha sido enviada exitosamente. Te contactaremos pronto.',
        [
          {
            text: 'OK',
            onPress: () => {
              navigation.goBack();
            }
          }
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'No se pudo enviar la solicitud. Inténtalo nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  const calculateMonthlyPayment = () => {
    const { amount, term } = formData;
    if (amount && term) {
      const principal = parseFloat(amount);
      const months = parseInt(term);
      const monthlyRate = 0.05 / 12; // 5% anual
      const payment = (principal * monthlyRate) / (1 - Math.pow(1 + monthlyRate, -months));
      return payment.toFixed(2);
    }
    return '0.00';
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Solicitar Préstamo</Text>
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <Card>
          <Text style={styles.formTitle}>Información del Préstamo</Text>
          
          <Input
            placeholder="Monto solicitado (USD)"
            value={formData.amount}
            onChangeText={(value) => handleInputChange('amount', value)}
            keyboardType="numeric"
          />

          <Input
            placeholder="Plazo (meses)"
            value={formData.term}
            onChangeText={(value) => handleInputChange('term', value)}
            keyboardType="numeric"
          />

          <Input
            placeholder="Propósito del préstamo"
            value={formData.purpose}
            onChangeText={(value) => handleInputChange('purpose', value)}
            multiline
            numberOfLines={3}
          />
        </Card>

        <Card>
          <Text style={styles.formTitle}>Información Financiera</Text>
          
          <Input
            placeholder="Ingresos mensuales (USD)"
            value={formData.income}
            onChangeText={(value) => handleInputChange('income', value)}
            keyboardType="numeric"
          />

          <Input
            placeholder="Situación laboral"
            value={formData.employment}
            onChangeText={(value) => handleInputChange('employment', value)}
          />
        </Card>

        {formData.amount && formData.term && (
          <Card style={styles.calculatorCard}>
            <Text style={styles.calculatorTitle}>Simulación de Cuota</Text>
            <Text style={styles.calculatorAmount}>
              ${calculateMonthlyPayment()}/mes
            </Text>
            <Text style={styles.calculatorInfo}>
              Tasa de interés: 5% anual
            </Text>
            <Text style={styles.calculatorInfo}>
              Total a pagar: ${(parseFloat(formData.amount || 0) * 1.05).toFixed(2)}
            </Text>
          </Card>
        )}

        <Card style={styles.infoCard}>
          <Text style={styles.infoTitle}>Requisitos</Text>
          <Text style={styles.infoText}>• Ingresos demostrables</Text>
          <Text style={styles.infoText}>• Edad mínima: 21 años</Text>
          <Text style={styles.infoText}>• Máximo 3 préstamos activos</Text>
          <Text style={styles.infoText}>• Evaluación crediticia requerida</Text>
        </Card>

        <Button
          title={loading ? 'Enviando...' : 'Enviar Solicitud'}
          onPress={submitLoanRequest}
          disabled={loading}
          style={styles.submitButton}
        />
      </ScrollView>
    </SafeAreaView>
  );
};

export default LoanRequestScreen;