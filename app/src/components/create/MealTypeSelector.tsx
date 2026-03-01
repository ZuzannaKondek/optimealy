/**
 * Meal Type Selector Component
 * OptiMeal Mobile App
 * 
 * Icon-based selector for meal types (Breakfast, 2nd Breakfast, Dinner, Dessert, Supper)
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { colors, spacing, typography } from '../../theme';

export type MealType = 'breakfast' | 'second_breakfast' | 'dinner' | 'dessert' | 'supper';

const MEAL_TYPES: MealType[] = ['breakfast', 'second_breakfast', 'dinner', 'dessert', 'supper'];
const REQUIRED_MEAL_TYPES: MealType[] = ['breakfast', 'dinner', 'supper'];
const OPTIONAL_MEAL_TYPES: MealType[] = ['second_breakfast', 'dessert'];

// Display labels for meal types
const MEAL_TYPE_LABELS: Record<MealType, string> = {
  breakfast: 'Breakfast',
  second_breakfast: '2nd Breakfast',
  dinner: 'Dinner',
  dessert: 'Dessert',
  supper: 'Supper',
};

type Props = {
  selectedMealTypes: MealType[];
  onSelectionChange: (selected: MealType[]) => void;
};

export const MealTypeSelector: React.FC<Props> = ({
  selectedMealTypes,
  onSelectionChange,
}) => {
  const toggleMealType = (mealType: MealType) => {
    const isRequired = REQUIRED_MEAL_TYPES.includes(mealType);
    
    // Cannot deselect required meal types
    if (isRequired && selectedMealTypes.includes(mealType)) {
      return;
    }
    
    // Toggle selection
    if (selectedMealTypes.includes(mealType)) {
      onSelectionChange(selectedMealTypes.filter((type) => type !== mealType));
    } else {
      onSelectionChange([...selectedMealTypes, mealType]);
    }
  };

  const isSelected = (mealType: MealType) => selectedMealTypes.includes(mealType);
  const isRequired = (mealType: MealType) => REQUIRED_MEAL_TYPES.includes(mealType);

  return (
    <View style={styles.container}>
      <Text style={styles.label}>Select Meal Types</Text>
      <Text style={styles.helpText}>
        Minimum: Breakfast, Dinner, Supper (required)
      </Text>
      
      <View style={styles.grid}>
        {MEAL_TYPES.map((mealType) => {
          const selected = isSelected(mealType);
          const required = isRequired(mealType);
          
          return (
            <TouchableOpacity
              key={mealType}
              style={[
                styles.mealTypeButton,
                selected && styles.mealTypeButtonSelected,
                required && !selected && styles.mealTypeButtonRequired,
              ]}
              onPress={() => toggleMealType(mealType)}
              disabled={required && selected} // Cannot deselect required types
              activeOpacity={0.7}
            >
              <Text
                style={[
                  styles.mealTypeText,
                  selected && styles.mealTypeTextSelected,
                  required && styles.mealTypeTextRequired,
                ]}
              >
                {MEAL_TYPE_LABELS[mealType]}
              </Text>
              {required && (
                <Text style={styles.requiredIndicator}>*</Text>
              )}
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing.md,
  },
  label: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.medium,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  helpText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: spacing.md,
    fontStyle: 'italic',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  mealTypeButton: {
    flex: 1,
    minWidth: '45%',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
    borderRadius: spacing.borderRadius,
    borderWidth: 2,
    borderColor: colors.border,
    backgroundColor: colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  mealTypeButtonSelected: {
    borderColor: colors.primary,
    backgroundColor: colors.primary + '20', // 20% opacity
  },
  mealTypeButtonRequired: {
    borderColor: colors.primary + '60', // 60% opacity
  },
  mealTypeText: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.medium,
    color: colors.textPrimary,
    textAlign: 'center',
  },
  mealTypeTextSelected: {
    color: colors.primary,
    fontWeight: typography.fontWeight.semiBold,
  },
  mealTypeTextRequired: {
    color: colors.primary,
  },
  requiredIndicator: {
    position: 'absolute',
    top: spacing.xs,
    right: spacing.xs,
    fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontWeight: typography.fontWeight.bold,
  },
});
