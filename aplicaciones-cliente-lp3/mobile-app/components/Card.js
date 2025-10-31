import React from 'react';
import { View, StyleSheet } from 'react-native';
import { theme } from '../styles/theme';

const Card = ({ children, style, onPress }) => {
  const cardStyle = [
    styles.card,
    style
  ];

  if (onPress) {
    return (
      <View style={cardStyle} onTouchEnd={onPress}>
        {children}
      </View>
    );
  }

  return (
    <View style={cardStyle}>
      {children}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
    borderWidth: 1,
    borderColor: theme.colors.border
  }
});

export default Card;