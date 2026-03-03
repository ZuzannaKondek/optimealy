import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import type { Meal } from '../../types/models';
import { colors, spacing, typography } from '../../theme';
import { formatCalories, formatNutritionalValue } from '../../utils/unitConversion';
import { useAuth } from '../../context/AuthContext';

// Display labels for meal types
const MEAL_TYPE_LABELS: Record<string, string> = {
  breakfast: 'Śniadanie',
  second_breakfast: '2. Śniadanie',
  dinner: 'Obiad',
  dessert: 'Deser',
  supper: 'Kolacja',
};

type Props = {
  meal: Meal;
  isDishBasedPlan?: boolean;
};

export const MealCard: React.FC<Props> = ({ meal, isDishBasedPlan = false }) => {
  const calories = meal.calculated_nutritional_info?.calories ?? null;
  const protein = meal.calculated_nutritional_info?.protein ?? null;
  const carbs = meal.calculated_nutritional_info?.carbs ?? null;
  const fat = meal.calculated_nutritional_info?.fat ?? null;
  const { user } = useAuth();
  const unitPreference = (user?.unit_preference ?? 'metric') as 'metric' | 'imperial';

  // Additional check: if meal has dish_weight_g, it's definitely a dish-based plan
  const isDish = isDishBasedPlan || (meal.dish_weight_g != null);

  // Display meal type using label mapping
  const displayType = (MEAL_TYPE_LABELS[meal.meal_type] || meal.meal_type).toUpperCase();

  // Format quantity display based on plan type
  let quantityText: string;
  if (isDish) {
    quantityText = '1 danie';
  } else {
    // Format servings nicely (remove trailing zeros for decimals)
    const servingsFormatted = meal.servings % 1 === 0 
      ? meal.servings.toString() 
      : meal.servings.toFixed(1).replace(/\.0$/, '');
    quantityText = `${servingsFormatted} porcja${meal.servings !== 1 ? 'e' : ''}`;
  }

  return (
    <View style={styles.card}>
      <View style={styles.headerRow}>
        <Text style={styles.mealType}>{displayType}</Text>
        <Text style={styles.servings}>{quantityText}</Text>
      </View>

      <Text style={styles.title}>{meal.recipe_name}</Text>

      {meal.dish_weight_g != null && (
        <Text style={styles.dishWeight}>Waga dania: {Math.round(meal.dish_weight_g)}g</Text>
      )}

      <View style={styles.metricsRow}>
        <Text style={styles.metric}>
          {calories != null ? formatCalories(calories) : 'kcal —'}
        </Text>
        <Text style={styles.metric}>
          {protein != null ? `P ${formatNutritionalValue(protein, unitPreference)}` : 'P —'} •{' '}
          {carbs != null ? `C ${formatNutritionalValue(carbs, unitPreference)}` : 'C —'} •{' '}
          {fat != null ? `F ${formatNutritionalValue(fat, unitPreference)}` : 'F —'}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: spacing.borderRadius,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  mealType: {
    fontSize: typography.fontSize.xs,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textSecondary,
    letterSpacing: 0.6,
  },
  servings: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  title: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  dishWeight: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  metricsRow: {
    gap: spacing.xs,
  },
  metric: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
});

