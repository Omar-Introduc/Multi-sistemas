import React, { Component } from 'react';
import { Text, View, StyleSheet } from 'react-native';
import QRCodeScanner from 'react-native-qrcode-scanner';
import RabbitMQClient from '../services/RabbitMQClient';

class QrScanner extends Component {
  onSuccess = e => {
    console.log('Scanned QR code: ', e.data);
    RabbitMQClient.sendMessage('qr_codes', e.data);
  };

  render() {
    return (
      <QRCodeScanner
        onRead={this.onSuccess}
        topContent={<Text style={styles.centerText}>Scan a QR code</Text>}
      />
    );
  }
}

const styles = StyleSheet.create({
  centerText: {
    flex: 1,
    fontSize: 18,
    padding: 32,
    color: '#777',
  },
});

export default QrScanner;
