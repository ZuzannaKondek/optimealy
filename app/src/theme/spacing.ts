/**
 * Spacing System
 * OptiMeal Mobile App Spacing Constants
 * 
 * Consistent spacing values used throughout the app.
 * Based on 8px grid system.
 */

export const spacing = {
  // Base unit (8px)
  base: 8,
  
  // Predefined spacing values
  none: 0,
  xs: 4,     // 0.5x base
  sm: 8,     // 1x base
  md: 16,    // 2x base
  lg: 24,    // 3x base
  xl: 32,    // 4x base
  xxl: 48,   // 6x base
  xxxl: 64,  // 8x base
  
  // Screen padding
  screenPadding: 16,
  screenPaddingLarge: 24,
  
  // Card spacing
  cardPadding: 16,
  cardMargin: 12,
  cardBorderRadius: 12,
  
  // Component spacing
  componentGap: 12,
  sectionGap: 24,
  
  // Icon sizes
  iconSmall: 16,
  iconMedium: 24,
  iconLarge: 32,
  iconXLarge: 48,
  
  // Button height
  buttonHeightSmall: 36,
  buttonHeight: 48,
  buttonHeightLarge: 56,
  
  // Input height
  inputHeight: 48,
  
  // Header heights
  headerHeight: 56,
  tabBarHeight: 64,
  
  // Border radius
  borderRadiusSmall: 4,
  borderRadius: 8,
  borderRadiusMedium: 12,
  borderRadiusLarge: 16,
  borderRadiusRound: 9999,
} as const;

/**
 * Helper function to multiply base spacing.
 * @param multiplier - The multiplier for the base spacing
 * @returns The calculated spacing value
 */
export const getSpacing = (multiplier: number): number => {
  return spacing.base * multiplier;
};

export type SpacingKey = keyof typeof spacing;
