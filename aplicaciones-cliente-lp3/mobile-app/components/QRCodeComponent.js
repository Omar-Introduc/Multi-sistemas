import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Modal } from 'react-native';
import QRCode from 'react-native-qrcode-svg';
import { theme } from '../styles/theme';
import Button from './Button';

const QRCodeComponent = ({
  value,
  size = 200,
  showButtons = true,
  onShare,
  onDownload
}) => {
  const [modalVisible, setModalVisible] = React.useState(false);

  if (!value) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>No hay código QR para mostrar</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <TouchableOpacity
        onPress={() => setModalVisible(true)}
        style={styles.qrContainer}
      >
        <QRCode
          value={value}
          size={size}
          color="black"
          backgroundColor="white"
          logo={require('../assets/logo.png')}
          logoSize={size * 0.2}
          logoBackgroundColor="white"
          logoBorderRadius={size * 0.1}
        />
      </TouchableOpacity>

      {showButtons && (
        <View style={styles.buttonContainer}>
          <Button
            title="Ver Completo"
            onPress={() => setModalVisible(true)}
            variant="outline"
            style={styles.qrButton}
          />
          {onShare && (
            <Button
              title="Compartir"
              onPress={onShare}
              style={styles.qrButton}
            />
          )}
          {onDownload && (
            <Button
              title="Descargar"
              onPress={onDownload}
              style={styles.qrButton}
            />
          )}
        </View>
      )}

      <Modal
        visible={modalVisible}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Código QR</Text>
            <View style={styles.qrCodeModal}>
              <QRCode
                value={value}
                size={size * 1.2}
                color="black"
                backgroundColor="white"
              />
            </View>
            <Button
              title="Cerrar"
              onPress={() => setModalVisible(false)}
              style={styles.closeButton}
            />
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    padding: 16
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 32,
    backgroundColor: theme.colors.backgroundLight,
    borderRadius: 8
  },
  emptyText: {
    color: theme.colors.textLight,
    fontSize: 16,
    textAlign: 'center'
  },
  qrContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    backgroundColor: 'white',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.border
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 16,
    gap: 8
  },
  qrButton: {
    minWidth: 100
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    maxWidth: '90%'
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
    color: theme.colors.text
  },
  qrCodeModal: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 8,
    marginBottom: 16
  },
  closeButton: {
    minWidth: 120
  }
});

export default QRCodeComponent;