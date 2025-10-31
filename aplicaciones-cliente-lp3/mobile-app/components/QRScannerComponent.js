import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Alert, Linking, ActivityIndicator } from 'react-native';
import { BarCodeScanner } from 'expo-barcode-scanner';
import Button from './Button';
import Card from './Card';

const QRScannerComponent = ({ onScanSuccess, onCancel }) => {
  const [hasPermission, setHasPermission] = useState(null);
  const [scanned, setScanned] = useState(false);
  const [loading, setLoading] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const scannerRef = useRef(null);

  useEffect(() => {
    getBarCodeScannerPermissions();
  }, []);

  const getBarCodeScannerPermissions = async () => {
    const { status } = await BarCodeScanner.requestPermissionsAsync();
    setHasPermission(status === 'granted');
  };

  const handleBarCodeScanned = async ({ type, data }) => {
    setScanned(true);
    setLoading(true);
    
    try {
      // Parse QR data
      let qrData;
      try {
        qrData = JSON.parse(data);
      } catch (error) {
        // If not JSON, treat as simple payment code
        qrData = { type: 'payment', code: data };
      }

      // Validate QR data
      const validation = validateQRData(qrData);
      if (!validation.isValid) {
        Alert.alert('QR Inválido', validation.message, [
          { text: 'Reintentar', onPress: () => setScanned(false) },
          { text: 'Cancelar', onPress: onCancel }
        ]);
        setLoading(false);
        return;
      }

      setScanResult(qrData);
      
      if (onScanSuccess) {
        await onScanSuccess(qrData);
      }
      
    } catch (error) {
      Alert.alert('Error', 'No se pudo procesar el código QR', [
        { text: 'Reintentar', onPress: () => setScanned(false) },
        { text: 'Cancelar', onPress: onCancel }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const validateQRData = (data) => {
    // Validate payment QR codes
    if (data.type === 'payment') {
      if (!data.account && !data.merchant && !data.code) {
        return { isValid: false, message: 'Código de pago inválido' };
      }
      if (data.amount && (isNaN(data.amount) || data.amount <= 0)) {
        return { isValid: false, message: 'Monto inválido' };
      }
    }
    
    // Validate transfer QR codes
    if (data.type === 'transfer') {
      if (!data.recipient || !data.recipient.account) {
        return { isValid: false, message: 'Datos de destinatario incompletos' };
      }
    }
    
    return { isValid: true, message: '' };
  };

  const resetScanner = () => {
    setScanned(false);
    setScanResult(null);
    setLoading(false);
  };

  if (hasPermission === null) {
    return (
      <View style={styles.container}>
        <Card style={styles.permissionCard}>
          <Text style={styles.permissionText}>Solicitando permisos de cámara...</Text>
          <ActivityIndicator size="large" color="#2196F3" />
        </Card>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={styles.container}>
        <Card style={styles.permissionCard}>
          <Text style={styles.permissionText}>
            Se requieren permisos de cámara para escanear códigos QR
          </Text>
          <Button
            title="Configurar Permisos"
            onPress={() => Linking.openSettings()}
            style={styles.permissionButton}
          />
          <Button
            title="Cancelar"
            onPress={onCancel}
            style={[styles.permissionButton, styles.cancelButton]}
          />
        </Card>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {!scanned && (
        <View style={styles.scannerContainer}>
          <BarCodeScanner
            ref={scannerRef}
            onBarCodeScanned={scanned ? undefined : handleBarCodeScanned}
            style={styles.scanner}
          />
          <View style={styles.overlay}>
            <View style={styles.cornerTL} />
            <View style={styles.cornerTR} />
            <View style={styles.cornerBL} />
            <View style={styles.cornerBR} />
          </View>
          <Text style={styles.instructionText}>
            Apunta la cámara al código QR
          </Text>
        </View>
      )}

      {scanned && (
        <View style={styles.resultContainer}>
          <Card style={styles.resultCard}>
            <Text style={styles.resultTitle}>
              {loading ? 'Procesando...' : 'Código QR Escaneado'}
            </Text>
            
            {loading && <ActivityIndicator size="large" color="#2196F3" />}
            
            {!loading && scanResult && (
              <View style={styles.resultContent}>
                {scanResult.type === 'payment' && (
                  <View style={styles.paymentInfo}>
                    <Text style={styles.infoLabel}>Tipo:</Text>
                    <Text style={styles.infoValue}>Pago</Text>
                    
                    {scanResult.merchant && (
                      <>
                        <Text style={styles.infoLabel}>Comercio:</Text>
                        <Text style={styles.infoValue}>{scanResult.merchant}</Text>
                      </>
                    )}
                    
                    {scanResult.amount && (
                      <>
                        <Text style={styles.infoLabel}>Monto:</Text>
                        <Text style={styles.infoValue}>${scanResult.amount}</Text>
                      </>
                    )}
                    
                    {scanResult.reference && (
                      <>
                        <Text style={styles.infoLabel}>Referencia:</Text>
                        <Text style={styles.infoValue}>{scanResult.reference}</Text>
                      </>
                    )}
                  </View>
                )}
                
                {scanResult.type === 'transfer' && (
                  <View style={styles.transferInfo}>
                    <Text style={styles.infoLabel}>Tipo:</Text>
                    <Text style={styles.infoValue}>Transferencia</Text>
                    
                    <Text style={styles.infoLabel}>Destinatario:</Text>
                    <Text style={styles.infoValue}>
                      {scanResult.recipient?.name || 'No disponible'}
                    </Text>
                  </View>
                )}
                
                <View style={styles.buttonContainer}>
                  <Button
                    title="Procesar"
                    onPress={() => onScanSuccess && onScanSuccess(scanResult)}
                    style={styles.processButton}
                  />
                  <Button
                    title="Cancelar"
                    onPress={onCancel}
                    style={[styles.processButton, styles.cancelButton]}
                  />
                </View>
              </View>
            )}
            
            <View style={styles.actionButtons}>
              <Button
                title="Escanear Otro"
                onPress={resetScanner}
                style={styles.actionButton}
              />
            </View>
          </Card>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  permissionCard: {
    margin: 20,
    padding: 20,
    alignItems: 'center',
  },
  permissionText: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
    color: '#333',
  },
  permissionButton: {
    marginVertical: 5,
  },
  cancelButton: {
    backgroundColor: '#f44336',
  },
  scannerContainer: {
    flex: 1,
    position: 'relative',
  },
  scanner: {
    flex: 1,
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cornerTL: {
    position: 'absolute',
    top: '25%',
    left: '15%',
    width: 50,
    height: 50,
    borderTopWidth: 4,
    borderLeftWidth: 4,
    borderColor: '#fff',
  },
  cornerTR: {
    position: 'absolute',
    top: '25%',
    right: '15%',
    width: 50,
    height: 50,
    borderTopWidth: 4,
    borderRightWidth: 4,
    borderColor: '#fff',
  },
  cornerBL: {
    position: 'absolute',
    bottom: '25%',
    left: '15%',
    width: 50,
    height: 50,
    borderBottomWidth: 4,
    borderLeftWidth: 4,
    borderColor: '#fff',
  },
  cornerBR: {
    position: 'absolute',
    bottom: '25%',
    right: '15%',
    width: 50,
    height: 50,
    borderBottomWidth: 4,
    borderRightWidth: 4,
    borderColor: '#fff',
  },
  instructionText: {
    position: 'absolute',
    bottom: 100,
    left: 0,
    right: 0,
    textAlign: 'center',
    color: '#fff',
    fontSize: 16,
    backgroundColor: 'rgba(0,0,0,0.5)',
    paddingVertical: 10,
    marginHorizontal: 20,
    borderRadius: 8,
  },
  resultContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  resultCard: {
    width: '100%',
    maxWidth: 400,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#333',
  },
  resultContent: {
    marginBottom: 20,
  },
  paymentInfo: {
    marginBottom: 20,
  },
  transferInfo: {
    marginBottom: 20,
  },
  infoLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginTop: 10,
  },
  infoValue: {
    fontSize: 16,
    color: '#333',
    marginBottom: 5,
  },
  buttonContainer: {
    marginVertical: 10,
  },
  processButton: {
    marginVertical: 5,
  },
  actionButtons: {
    marginTop: 20,
  },
  actionButton: {
    backgroundColor: '#2196F3',
  },
});

export default QRScannerComponent;