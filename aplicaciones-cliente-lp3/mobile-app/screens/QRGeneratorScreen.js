import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import QRGeneratorComponent from '../components/QRGeneratorComponent';
import { styles } from '../styles/styles';

const QRGeneratorScreen = ({ navigation }) => {
  const handleGenerate = (qrData) => {
    console.log('QR Generated:', qrData);
    // QR has been generated successfully
  };

  const handleClose = () => {
    navigation.goBack();
  };

  return (
    <SafeAreaView style={styles.container}>
      <QRGeneratorComponent
        onGenerate={handleGenerate}
        onClose={handleClose}
      />
    </SafeAreaView>
  );
};

export default QRGeneratorScreen;