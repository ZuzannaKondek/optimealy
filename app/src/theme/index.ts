/**
 * Theme Export
 * OptiMeal Mobile App Complete Theme
 * 
 * Exports all theme values as a single source of truth.
 */

import { colors } from './colors';
import { spacing, getSpacing } from './spacing';
import { typography } from './typography';

export const theme = {
  colors,
  spacing,
  typography,
} as const;

// Re-export individual modules for convenience
export { colors } from './colors';
export { spacing, getSpacing } from './spacing';
export { typography } from './typography';

// Export types
export type Theme = typeof theme;

export default theme;
