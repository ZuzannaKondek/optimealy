/**
 * Unit Conversion Utilities
 * OptiMeal Mobile App
 * 
 * Converts between metric and imperial units for nutritional display.
 */

type UnitPreference = 'metric' | 'imperial';

/**
 * Convert grams to ounces (for imperial display)
 * 1 oz = 28.3495 g
 */
export const gramsToOunces = (grams: number): number => {
  return grams / 28.3495;
};

/**
 * Convert ounces to grams (for metric display)
 */
export const ouncesToGrams = (ounces: number): number => {
  return ounces * 28.3495;
};

/**
 * Format weight based on unit preference
 * @param grams - Weight in grams
 * @param unit - User's unit preference
 * @returns Formatted string with appropriate unit
 */
export const formatWeight = (grams: number, unit: UnitPreference): string => {
  if (unit === 'imperial') {
    const ounces = gramsToOunces(grams);
    if (ounces >= 16) {
      const pounds = Math.floor(ounces / 16);
      const remainingOz = Math.round(ounces % 16);
      return remainingOz > 0 ? `${pounds} lb ${remainingOz} oz` : `${pounds} lb`;
    }
    return `${Math.round(ounces * 10) / 10} oz`;
  }
  // Metric: display in grams or kilograms
  if (grams >= 1000) {
    const kg = grams / 1000;
    return `${Math.round(kg * 10) / 10} kg`;
  }
  return `${Math.round(grams)}g`;
};

/**
 * Format nutritional value (protein, carbs, fat) based on unit preference
 * For imperial, we still show grams but could convert to ounces if needed
 * Currently keeping grams for macros as it's standard in nutrition
 */
export const formatNutritionalValue = (grams: number, unit: UnitPreference): string => {
  // Macros are typically shown in grams regardless of unit system
  // But we can format the number appropriately
  if (unit === 'imperial') {
    // Show grams with oz equivalent in parentheses for reference
    const ounces = gramsToOunces(grams);
    return `${Math.round(grams)}g (${Math.round(ounces * 10) / 10} oz)`;
  }
  return `${Math.round(grams)}g`;
};

/**
 * Format calories (same for both systems)
 */
export const formatCalories = (calories: number): string => {
  return `${Math.round(calories)} kcal`;
};

/**
 * Get unit label for weight display
 */
export const getWeightUnit = (unit: UnitPreference): string => {
  return unit === 'imperial' ? 'oz' : 'g';
};
