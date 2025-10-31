// Tema de la aplicación
export const theme = {
  colors: {
    // Colores principales
    primary: '#2E7D32',      // Verde oscuro (banco)
    primaryLight: '#4CAF50', // Verde claro
    primaryDark: '#1B5E20',  // Verde más oscuro

    // Colores secundarios
    secondary: '#1976D2',    // Azul
    accent: '#FF9800',       // Naranja

    // Colores de estado
    success: '#4CAF50',      // Verde para éxito
    warning: '#FF9800',      // Naranja para advertencia
    error: '#F44336',        // Rojo para error
    info: '#2196F3',         // Azul para información

    // Colores neutros
    background: '#F5F5F5',   // Fondo principal
    backgroundLight: '#FAFAFA',
    surface: '#FFFFFF',      // Superficies de tarjetas
    text: '#212121',         // Texto principal
    textSecondary: '#757575', // Texto secundario
    textLight: '#9E9E9E',    // Texto claro
    placeholder: '#BDBDBD',  // Placeholders

    // Colores de borde
    border: '#E0E0E0',
    divider: '#E0E0E0',

    // Colores interactivos
    disabled: '#E0E0E0',
    focus: '#2196F3',

    // Colores específicos de la app
    cardBackground: '#FFFFFF',
    inputBackground: '#FFFFFF',
    buttonPrimary: '#2E7D32',
    buttonSecondary: '#1976D2',
    
    // Colores de balance
    positive: '#4CAF50',     // Saldos positivos
    negative: '#F44336',     // Saldos negativos
    
    // Colores de estado de transacción
    transactionIncome: '#4CAF50',
    transactionExpense: '#F44336',
    transactionPending: '#FF9800'
  },

  // Tipografía
  typography: {
    // Tamaños de fuente
    fontSize: {
      xs: 10,
      sm: 12,
      md: 14,
      lg: 16,
      xl: 18,
      '2xl': 20,
      '3xl': 24,
      '4xl': 32
    },

    // Pesos de fuente
    fontWeight: {
      light: '300',
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700'
    },

    // Alturas de línea
    lineHeight: {
      tight: 1.2,
      normal: 1.4,
      relaxed: 1.6
    },

    // Familias de fuente
    fontFamily: {
      primary: 'System',
      secondary: 'System',
      mono: 'System'
    }
  },

  // Espaciado
  spacing: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 20,
    '2xl': 24,
    '3xl': 32,
    '4xl': 40
  },

  // Bordes
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
    round: 50
  },

  // Sombras
  shadows: {
    small: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.1,
      shadowRadius: 2,
      elevation: 2
    },
    medium: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 3,
      elevation: 4
    },
    large: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.1,
      shadowRadius: 5,
      elevation: 8
    }
  },

  // Tamaños de componentes
  componentSizes: {
    // Botones
    buttonHeight: {
      small: 36,
      medium: 48,
      large: 56
    },
    buttonPadding: {
      small: 12,
      medium: 16,
      large: 20
    },

    // Inputs
    inputHeight: {
      small: 36,
      medium: 48,
      large: 56
    },

    // Tarjetas
    cardPadding: {
      small: 12,
      medium: 16,
      large: 20
    },

    // Iconos
    iconSize: {
      small: 16,
      medium: 24,
      large: 32,
      xlarge: 48
    }
  },

  // Z-index
  zIndex: {
    modal: 1000,
    dropdown: 100,
    header: 10,
    overlay: 5
  },

  // Breakpoints para responsive design (si se necesita)
  breakpoints: {
    small: 320,
    medium: 768,
    large: 1024
  },

  // Configuraciones específicas de la app
  app: {
    // Configuración de header
    header: {
      height: 56,
      backgroundColor: '#2E7D32',
      titleColor: '#FFFFFF'
    },

    // Configuración de tab bar
    tabBar: {
      height: 60,
      backgroundColor: '#FFFFFF',
      activeColor: '#2E7D32',
      inactiveColor: '#757575'
    },

    // Configuración de animaciones
    animations: {
      duration: {
        fast: 150,
        normal: 300,
        slow: 500
      },
      easing: 'ease-in-out'
    }
  }
};

// Funciones de utilidad para el tema
export const getThemeColor = (colorName) => {
  return theme.colors[colorName] || theme.colors.text;
};

export const getFontSize = (size) => {
  return theme.typography.fontSize[size] || theme.typography.fontSize.md;
};

export const getSpacing = (spacing) => {
  return theme.spacing[spacing] || theme.spacing.md;
};

export const getBorderRadius = (radius) => {
  return theme.borderRadius[radius] || theme.borderRadius.md;
};

export default theme;
