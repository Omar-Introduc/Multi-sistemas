import React from 'react';
import {
  View,
  Text,
  Modal,
  TouchableOpacity,
  StyleSheet
} from 'react-native';
import { theme } from '../styles/theme';
import Button from './Button';

const CustomAlert = ({
  visible,
  title,
  message,
  buttons = [],
  type = 'info' // info, success, warning, error
}) => {
  const getIcon = () => {
    switch (type) {
      case 'success':
        return '✅';
      case 'warning':
        return '⚠️';
      case 'error':
        return '❌';
      default:
        return 'ℹ️';
    }
  };

  const getTitleColor = () => {
    switch (type) {
      case 'success':
        return theme.colors.success;
      case 'warning':
        return theme.colors.warning;
      case 'error':
        return theme.colors.error;
      default:
        return theme.colors.primary;
    }
  };

  const defaultButtons = buttons.length > 0 ? buttons : [
    {
      text: 'OK',
      onPress: () => {}
    }
  ];

  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="fade"
      onRequestClose={() => {}}
    >
      <View style={styles.overlay}>
        <View style={styles.container}>
          <View style={styles.iconContainer}>
            <Text style={styles.icon}>{getIcon()}</Text>
          </View>

          {title && (
            <Text style={[styles.title, { color: getTitleColor() }]}>
              {title}
            </Text>
          )}

          {message && (
            <Text style={styles.message}>
              {message}
            </Text>
          )}

          <View style={styles.buttonContainer}>
            {defaultButtons.map((button, index) => (
              <Button
                key={index}
                title={button.text}
                onPress={button.onPress}
                variant={button.style || 'primary'}
                style={[
                  styles.button,
                  index < defaultButtons.length - 1 && styles.buttonSpacing
                ]}
              />
            ))}
          </View>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20
  },
  container: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    maxWidth: '90%',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 4.65,
    elevation: 8
  },
  iconContainer: {
    marginBottom: 16
  },
  icon: {
    fontSize: 48
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
    textAlign: 'center'
  },
  message: {
    fontSize: 16,
    color: theme.colors.text,
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 22
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 12
  },
  button: {
    minWidth: 100
  },
  buttonSpacing: {
    marginRight: 8
  }
});

export default CustomAlert;