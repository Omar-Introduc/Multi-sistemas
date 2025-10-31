import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, TextInput, Alert } from 'react-native';
import { useNotification } from '../hooks/useAsyncManager';

export const NotificationDemo: React.FC = () => {
  const { 
    notifications, 
    success, 
    error, 
    warning, 
    info, 
    alert: showAlert,
    hide, 
    hideAll, 
    clear 
  } = useNotification();

  const [customTitle, setCustomTitle] = useState('');
  const [customMessage, setCustomMessage] = useState('');
  const [notificationType, setNotificationType] = useState<'success' | 'error' | 'warning' | 'info'>('info');

  const showNotification = () => {
    const config = {
      duration: 3000,
      persistent: false,
      vibration: true,
      sound: true
    };

    switch (notificationType) {
      case 'success':
        success(customTitle || 'Éxito', customMessage || 'Operación completada correctamente', config);
        break;
      case 'error':
        error(customTitle || 'Error', customMessage || 'Ha ocurrido un error', { ...config, persistent: true });
        break;
      case 'warning':
        warning(customTitle || 'Advertencia', customMessage || 'Atención requerida', config);
        break;
      case 'info':
        info(customTitle || 'Información', customMessage || 'Mensaje informativo', config);
        break;
    }

    setCustomTitle('');
    setCustomMessage('');
  };

  const showBatchNotifications = () => {
    const batch = [
      { type: 'success', title: 'Lote 1', message: 'Primera notificación del lote' },
      { type: 'info', title: 'Lote 2', message: 'Segunda notificación del lote' },
      { type: 'warning', title: 'Lote 3', message: 'Tercera notificación del lote' },
      { type: 'success', title: 'Lote 4', message: 'Cuarta notificación del lote' }
    ];

    batch.forEach((notif, index) => {
      setTimeout(() => {
        switch (notif.type) {
          case 'success':
            success(notif.title, notif.message);
            break;
          case 'error':
            error(notif.title, notif.message);
            break;
          case 'warning':
            warning(notif.title, notif.message);
            break;
          case 'info':
            info(notif.title, notif.message);
            break;
        }
      }, index * 500);
    });
  };

  const showNotificationWithActions = () => {
    Alert.alert(
      'Actualización Disponible',
      'Hay una nueva versión disponible. ¿Deseas actualizar ahora?',
      [
        {
          text: 'Actualizar',
          onPress: () => {
            info('Actualizando...', 'Descargando la nueva versión...');
            setTimeout(() => {
              success('Actualización Completa', 'La aplicación ha sido actualizada exitosamente');
            }, 2000);
          }
        },
        {
          text: 'Más Tarde',
          onPress: () => {
            info('Actualización Diferida', 'Te recordaremos más tarde');
          }
        },
        {
          text: 'Cancelar',
          style: 'cancel'
        }
      ]
    );
  };

  const showProgressNotification = () => {
    let progress = 0;
    const notificationId = info('Procesando', 'Iniciando proceso...', { persistent: true });

    const interval = setInterval(() => {
      progress += 10;
      
      if (progress <= 100) {
        info('Procesando', `Procesando... (${progress}%)`, { persistent: true });
      } else {
        clearInterval(interval);
        success('Proceso Completado', 'Todas las operaciones se completaron exitosamente');
      }
    }, 500);
  };

  const showOfflineNotification = () => {
    const hasConnection = Math.random() > 0.3; // Simular conectividad
    
    if (!hasConnection) {
      warning('Sin Conexión', 'Trabajando en modo offline. Los datos se sincronizarán cuando恢复es la conexión.');
    } else {
      success('Conexión Restaurada', 'Los datos offline han sido sincronizados exitosamente.');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Demo del Sistema de Notificaciones</Text>

      {/* Estadísticas */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Estadísticas ({notifications.length})</Text>
        
        <View style={styles.statsGrid}>
          <View style={[styles.statItem, { backgroundColor: '#d4edda' }]}>
            <Text style={[styles.statNumber, { color: '#155724' }]}>
              {notifications.filter(n => n.type === 'success').length}
            </Text>
            <Text style={[styles.statLabel, { color: '#155724' }]}>Éxito</Text>
          </View>
          <View style={[styles.statItem, { backgroundColor: '#f8d7da' }]}>
            <Text style={[styles.statNumber, { color: '#721c24' }]}>
              {notifications.filter(n => n.type === 'error').length}
            </Text>
            <Text style={[styles.statLabel, { color: '#721c24' }]}>Error</Text>
          </View>
          <View style={[styles.statItem, { backgroundColor: '#fff3cd' }]}>
            <Text style={[styles.statNumber, { color: '#856404' }]}>
              {notifications.filter(n => n.type === 'warning').length}
            </Text>
            <Text style={[styles.statLabel, { color: '#856404' }]}>Advertencia</Text>
          </View>
          <View style={[styles.statItem, { backgroundColor: '#d1ecf1' }]}>
            <Text style={[styles.statNumber, { color: '#0c5460' }]}>
              {notifications.filter(n => n.type === 'info').length}
            </Text>
            <Text style={[styles.statLabel, { color: '#0c5460' }]}>Info</Text>
          </View>
        </View>
      </View>

      {/* Notificaciones activas */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notificaciones Activas ({notifications.length})</Text>
        
        {notifications.length === 0 ? (
          <Text style={styles.noNotifications}>No hay notificaciones activas</Text>
        ) : (
          <View style={styles.notificationsList}>
            {notifications.map(notification => (
              <View
                key={notification.id}
                style={[
                  styles.notificationItem,
                  { 
                    borderLeftColor: 
                      notification.type === 'success' ? '#28a745' :
                      notification.type === 'error' ? '#dc3545' :
                      notification.type === 'warning' ? '#ffc107' :
                      '#17a2b8'
                  }
                ]}
              >
                <View style={styles.notificationContent}>
                  <Text style={styles.notificationTitle}>{notification.title}</Text>
                  <Text style={styles.notificationMessage}>{notification.message}</Text>
                </View>
                <TouchableOpacity
                  style={styles.closeButton}
                  onPress={() => hide(notification.id)}
                >
                  <Text style={styles.closeButtonText}>✕</Text>
                </TouchableOpacity>
              </View>
            ))}
          </View>
        )}
      </View>

      {/* Configuración personalizada */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notificación Personalizada</Text>
        
        <Text style={styles.label}>Título:</Text>
        <TextInput
          style={styles.input}
          value={customTitle}
          onChangeText={setCustomTitle}
          placeholder="Ingresa el título"
        />
        
        <Text style={styles.label}>Tipo:</Text>
        <View style={styles.typeContainer}>
          {[
            { key: 'success', label: 'Éxito', color: '#28a745' },
            { key: 'error', label: 'Error', color: '#dc3545' },
            { key: 'warning', label: 'Advertencia', color: '#ffc107' },
            { key: 'info', label: 'Información', color: '#17a2b8' }
          ].map(type => (
            <TouchableOpacity
              key={type.key}
              style={[
                styles.typeButton,
                { borderColor: type.color },
                notificationType === type.key && { backgroundColor: type.color }
              ]}
              onPress={() => setNotificationType(type.key as any)}
            >
              <Text style={[
                styles.typeButtonText,
                { color: type.color },
                notificationType === type.key && { color: 'white' }
              ]}>
                {type.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.label}>Mensaje:</Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          value={customMessage}
          onChangeText={setCustomMessage}
          placeholder="Ingresa el mensaje"
          multiline
          numberOfLines={3}
        />

        <TouchableOpacity
          style={[
            styles.button,
            {
              backgroundColor: 
                notificationType === 'success' ? '#28a745' :
                notificationType === 'error' ? '#dc3545' :
                notificationType === 'warning' ? '#ffc107' :
                '#17a2b8'
            }
          ]}
          onPress={showNotification}
        >
          <Text style={styles.buttonText}>Mostrar Notificación</Text>
        </TouchableOpacity>
      </View>

      {/* Ejemplos predefinidos */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Ejemplos Predefinidos</Text>
        
        <TouchableOpacity style={[styles.button, styles.batchButton]} onPress={showBatchNotifications}>
          <Text style={styles.buttonText}>Lote de Notificaciones</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={[styles.button, styles.actionButton]} onPress={showNotificationWithActions}>
          <Text style={styles.buttonText}>Notificación con Acciones</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={[styles.button, styles.progressButton]} onPress={showProgressNotification}>
          <Text style={styles.buttonText}>Notificación de Progreso</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={[styles.button, styles.networkButton]} onPress={showOfflineNotification}>
          <Text style={styles.buttonText}>Simular Estado de Red</Text>
        </TouchableOpacity>

        <View style={styles.actionRow}>
          <TouchableOpacity style={[styles.button, styles.dangerButton]} onPress={hideAll}>
            <Text style={styles.buttonText}>Ocultar Todas</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={[styles.button, styles.clearButton]} onPress={() => clear('success')}>
            <Text style={styles.buttonText}>Limpiar Éxitos</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f8f9fa'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 24,
    textAlign: 'center',
    color: '#2c3e50'
  },
  section: {
    backgroundColor: 'white',
    padding: 16,
    marginBottom: 16,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
    color: '#34495e'
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 8
  },
  statItem: {
    flex: 1,
    padding: 12,
    borderRadius: 6,
    alignItems: 'center'
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold'
  },
  statLabel: {
    fontSize: 12,
    marginTop: 4
  },
  noNotifications: {
    textAlign: 'center',
    color: '#6c757d',
    fontStyle: 'italic',
    padding: 20
  },
  notificationsList: {
    maxHeight: 200
  },
  notificationItem: {
    flexDirection: 'row',
    padding: 12,
    marginBottom: 8,
    backgroundColor: '#f8f9fa',
    borderRadius: 6,
    borderLeftWidth: 4
  },
  notificationContent: {
    flex: 1
  },
  notificationTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 4
  },
  notificationMessage: {
    fontSize: 14,
    color: '#6c757d'
  },
  closeButton: {
    padding: 4,
    marginLeft: 8
  },
  closeButtonText: {
    fontSize: 18,
    color: '#6c757d'
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 8,
    marginTop: 12,
    color: '#5a6c7d'
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 4,
    padding: 12,
    fontSize: 14,
    marginBottom: 8,
    backgroundColor: '#fafafa'
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top'
  },
  typeContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 16
  },
  typeButton: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderRadius: 4,
    backgroundColor: 'white'
  },
  typeButtonText: {
    fontSize: 12,
    fontWeight: '500'
  },
  button: {
    padding: 12,
    borderRadius: 6,
    alignItems: 'center',
    marginBottom: 8
  },
  buttonText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 14
  },
  batchButton: {
    backgroundColor: '#6f42c1'
  },
  actionButton: {
    backgroundColor: '#e83e8c'
  },
  progressButton: {
    backgroundColor: '#20c997'
  },
  networkButton: {
    backgroundColor: '#fd7e14'
  },
  actionRow: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 8
  },
  dangerButton: {
    backgroundColor: '#dc3545',
    flex: 1
  },
  clearButton: {
    backgroundColor: '#28a745',
    flex: 1
  }
});

export default NotificationDemo;