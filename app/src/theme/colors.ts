/**
 * Color Palette - SINGLE SOURCE OF TRUTH
 * OptiMeal Mobile App Theme Colors
 * 
 * All color definitions for the application.
 * DO NOT define colors elsewhere.
 */

export const colors = {
  // Primary Brand Colors
  primary: '#4CAF50',      // Green - represents freshness, health
  primaryDark: '#388E3C',
  primaryLight: '#81C784',
  
  // Secondary Colors
  secondary: '#FF9800',    // Orange - energy, optimization
  secondaryDark: '#F57C00',
  secondaryLight: '#FFB74D',
  
  // Accent
  accent: '#2196F3',       // Blue - trust, technology
  accentDark: '#1976D2',
  accentLight: '#64B5F6',
  
  // Neutrals
  black: '#000000',
  white: '#FFFFFF',
  gray900: '#212121',
  gray800: '#424242',
  gray700: '#616161',
  gray600: '#757575',
  gray500: '#9E9E9E',
  gray400: '#BDBDBD',
  gray300: '#E0E0E0',
  gray200: '#EEEEEE',
  gray100: '#F5F5F5',
  gray50: '#FAFAFA',
  
  // Semantic Colors
  success: '#4CAF50',
  warning: '#FF9800',
  error: '#F44336',
  info: '#2196F3',
  
  // Background Colors (Light Theme)
  background: '#FFFFFF',
  backgroundSecondary: '#F5F5F5',
  surface: '#FFFFFF',
  surfaceVariant: '#FAFAFA',
  
  // Background Colors (Dark Theme)
  backgroundDark: '#121212',
  backgroundSecondaryDark: '#1E1E1E',
  surfaceDark: '#1E1E1E',
  surfaceVariantDark: '#2C2C2C',
  
  // Text Colors (Light Theme)
  textPrimary: '#212121',
  textSecondary: '#757575',
  textTertiary: '#9E9E9E',
  textDisabled: '#BDBDBD',
  textOnPrimary: '#FFFFFF',
  
  // Text Colors (Dark Theme)
  textPrimaryDark: '#FFFFFF',
  textSecondaryDark: '#B0B0B0',
  textTertiaryDark: '#808080',
  textDisabledDark: '#5A5A5A',
  
  // Border Colors
  border: '#E0E0E0',
  borderDark: '#424242',
  divider: '#EEEEEE',
  dividerDark: '#2C2C2C',
  
  // Overlay
  overlay: 'rgba(0, 0, 0, 0.5)',
  overlayLight: 'rgba(0, 0, 0, 0.3)',
  overlayDark: 'rgba(0, 0, 0, 0.7)',
  
  // Transparent
  transparent: 'transparent',
} as const;

export type ColorKey = keyof typeof colors;
