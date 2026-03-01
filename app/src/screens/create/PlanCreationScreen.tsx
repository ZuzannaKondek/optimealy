/**
 * Plan Creation Screen
 * OptiMeal Mobile App
 * 
 * Screen for creating optimized meal plans.
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { usePlans } from '../../hooks/usePlans';
import { colors, spacing, typography } from '../../theme';
import type { PlanCreationFormData } from '../../types/models';
import { MealTypeSelector, type MealType } from '../../components/create/MealTypeSelector';
import { PlanCreationErrorModal } from '../../components/create/PlanCreationErrorModal';
import { getApiErrorMessage } from '../../utils/apiErrors';

/**
 * Calculate macro targets based on calories using balanced diet ratios:
 * - Protein: 20% of calories (4 cal/g)
 * - Carbs: 50% of calories (4 cal/g)
 * - Fat: 30% of calories (9 cal/g)
 */
const calculateMacros = (calories: number) => {
  return {
    protein: Math.round((calories * 0.20) / 4),
    carbs: Math.round((calories * 0.50) / 4),
    fat: Math.round((calories * 0.30) / 9),
  };
};

export const PlanCreationScreen: React.FC = () => {
  const navigation = useNavigation();
  const { createPlan, creationState, resetCreationState } = usePlans();

  const [formData, setFormData] = useState<PlanCreationFormData>(() => {
    // Initialize with calculated macros for default calories
    const defaultCalories = 2000;
    const defaultMacros = calculateMacros(defaultCalories);
    
    return {
      name: '',
      durationDays: 7,
      targetCalories: defaultCalories,
      targetProtein: defaultMacros.protein,
      targetCarbs: defaultMacros.carbs,
      targetFat: defaultMacros.fat,
      startDate: undefined,
      selectedMealTypes: ['breakfast', 'dinner', 'supper'], // Default minimum selection
      ingredientsToHave: [],
      ingredientsToWant: [],
      ingredientsToExclude: [],
      dietaryTags: [],
      cuisineTypes: [],
    };
  });

  // Track which macro fields have been manually edited by the user
  const [macroTouched, setMacroTouched] = useState({
    protein: false,
    carbs: false,
    fat: false,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Auto-calculate macros when calories change (only for untouched fields)
  useEffect(() => {
    const calculated = calculateMacros(formData.targetCalories);
    
    setFormData((prev) => ({
      ...prev,
      targetProtein: macroTouched.protein ? prev.targetProtein : calculated.protein,
      targetCarbs: macroTouched.carbs ? prev.targetCarbs : calculated.carbs,
      targetFat: macroTouched.fat ? prev.targetFat : calculated.fat,
    }));
  }, [formData.targetCalories, macroTouched.protein, macroTouched.carbs, macroTouched.fat]);

  // Validation – returns error map so caller can show summary (also updates state for inline display)
  const validateForm = (): Record<string, string> => {
    const newErrors: Record<string, string> = {};

    const trimmedName = (formData.name || '').trim();
    if (!trimmedName) {
      newErrors.name = 'Plan name is required';
    } else if (trimmedName.length > 255) {
      newErrors.name = 'Plan name must be 255 characters or less';
    }

    if (formData.durationDays < 1 || formData.durationDays > 30) {
      newErrors.durationDays = 'Duration must be between 1 and 30 days';
    }

    if (formData.targetCalories < 800 || formData.targetCalories > 5000) {
      newErrors.targetCalories = 'Calories must be between 800 and 5000';
    }

    if (formData.targetProtein !== undefined && formData.targetProtein < 0) {
      newErrors.targetProtein = 'Protein must be positive';
    }

    if (formData.targetCarbs !== undefined && formData.targetCarbs < 0) {
      newErrors.carbs = 'Carbs must be positive';
    }

    if (formData.targetFat !== undefined && formData.targetFat < 0) {
      newErrors.fat = 'Fat must be positive';
    }

    // Validate selected meal types
    if (!formData.selectedMealTypes || formData.selectedMealTypes.length === 0) {
      newErrors.selectedMealTypes = 'At least one meal type must be selected';
    } else {
      const requiredTypes = ['breakfast', 'dinner', 'supper'];
      const selectedSet = new Set(formData.selectedMealTypes);
      const missing = requiredTypes.filter((type) => !selectedSet.has(type));
      if (missing.length > 0) {
        newErrors.selectedMealTypes = `Required meal types missing: ${missing.join(', ')}`;
      }
    }

    setErrors(newErrors);
    return newErrors;
  };

  // Handle form submission
  const handleSubmit = async () => {
    const formErrors = validateForm();
    if (Object.keys(formErrors).length > 0) {
      const message =
        'Fix the following so you can submit:\n\n• ' +
        Object.values(formErrors).join('\n• ');
      Alert.alert(
        'Invalid input',
        message,
        [{ text: 'OK' }]
      );
      return;
    }

    const planName = (formData.name ?? '').trim();
    if (!planName) {
      setErrors((prev) => ({ ...prev, name: 'Plan name is required' }));
      return;
    }

    try {
      await createPlan({
        name: planName,
        duration_days: formData.durationDays,
        target_calories_per_day: formData.targetCalories,
        target_protein_g: formData.targetProtein,
        target_carbs_g: formData.targetCarbs,
        target_fat_g: formData.targetFat,
        start_date: formData.startDate?.toISOString().split('T')[0],
        selected_meal_types: formData.selectedMealTypes,
        ingredients_to_have: formData.ingredientsToHave.map((item) => ({
          product_id: item.productId,
          quantity_g: item.quantityG,
        })),
        ingredients_to_want: formData.ingredientsToWant,
        ingredients_to_exclude: formData.ingredientsToExclude,
        dietary_tags: formData.dietaryTags,
        cuisine_types: formData.cuisineTypes,
      });
      // Don't navigate here - let the useEffect handle it after polling completes
    } catch (error: any) {
      const message = getApiErrorMessage(error);
      const suggestion =
        'Try adjusting your targets or constraints (e.g. calories 800–5000, duration 1–30 days, at least breakfast/dinner/supper).';
      Alert.alert(
        'Couldn’t create plan',
        message + '\n\n' + suggestion,
        [{ text: 'OK' }]
      );
    }
  };

  // Watch for completion – navigate when plan is ready; failure is shown in PlanCreationErrorModal
  React.useEffect(() => {
    if (creationState.status === 'completed' && creationState.createdPlanId) {
      navigation.navigate('PlanDetail' as never, {
        planId: creationState.createdPlanId,
      } as never);
      setTimeout(() => resetCreationState(), 500);
    }
  }, [creationState.status, creationState.createdPlanId, navigation, resetCreationState]);

  return (
    <>
      <PlanCreationErrorModal
        visible={creationState.status === 'failed'}
        message={creationState.error || 'The optimizer could not find a plan that meets your constraints.'}
        onDismiss={resetCreationState}
      />
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Create Meal Plan</Text>
      <Text style={styles.subtitle}>
        Generate an optimized meal plan that minimizes food waste
      </Text>

      {/* Plan name */}
      <View style={styles.section}>
        <Text style={styles.label}>Plan name</Text>
        <TextInput
          style={[styles.input, errors.name && styles.inputError]}
          value={formData.name}
          onChangeText={(text) => setFormData((prev) => ({ ...prev, name: text }))}
          placeholder="e.g. Week of Feb 13"
          maxLength={255}
          accessibilityLabel="Plan name"
        />
        {errors.name && (
          <Text style={styles.errorText}>{errors.name}</Text>
        )}
      </View>

      {/* Duration */}
      <View style={styles.section}>
        <Text style={styles.label}>Duration (days)</Text>
        <TextInput
          style={[styles.input, errors.durationDays && styles.inputError]}
          value={formData.durationDays.toString()}
          onChangeText={(text) => {
            const value = parseInt(text, 10) || 0;
            setFormData({ ...formData, durationDays: value });
          }}
          keyboardType="numeric"
          placeholder="7"
        />
        {errors.durationDays && (
          <Text style={styles.errorText}>{errors.durationDays}</Text>
        )}
      </View>

      {/* Calories */}
      <View style={styles.section}>
        <Text style={styles.label}>Daily Calorie Target</Text>
        <TextInput
          style={[styles.input, errors.targetCalories && styles.inputError]}
          value={formData.targetCalories.toString()}
          onChangeText={(text) => {
            const value = parseInt(text, 10) || 0;
            setFormData({ ...formData, targetCalories: value });
          }}
          keyboardType="numeric"
          placeholder="2000"
        />
        {errors.targetCalories && (
          <Text style={styles.errorText}>{errors.targetCalories}</Text>
        )}
      </View>

      {/* Macros (Auto-calculated, editable) */}
      <View style={styles.section}>
        <Text style={styles.label}>Daily Protein Target (g)</Text>
        <TextInput
          style={[styles.input, errors.targetProtein && styles.inputError]}
          value={formData.targetProtein?.toString() || ''}
          onChangeText={(text) => {
            const value = text ? parseFloat(text) : undefined;
            setFormData({ ...formData, targetProtein: value });
            setMacroTouched({ ...macroTouched, protein: true });
          }}
          onFocus={() => setMacroTouched({ ...macroTouched, protein: true })}
          keyboardType="numeric"
          placeholder="Auto-calculated"
        />
        {errors.targetProtein && (
          <Text style={styles.errorText}>{errors.targetProtein}</Text>
        )}
        {!macroTouched.protein && (
          <Text style={styles.helpText}>Auto-calculated (20% of calories)</Text>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>Daily Carbs Target (g)</Text>
        <TextInput
          style={[styles.input, errors.carbs && styles.inputError]}
          value={formData.targetCarbs?.toString() || ''}
          onChangeText={(text) => {
            const value = text ? parseFloat(text) : undefined;
            setFormData({ ...formData, targetCarbs: value });
            setMacroTouched({ ...macroTouched, carbs: true });
          }}
          onFocus={() => setMacroTouched({ ...macroTouched, carbs: true })}
          keyboardType="numeric"
          placeholder="Auto-calculated"
        />
        {errors.carbs && <Text style={styles.errorText}>{errors.carbs}</Text>}
        {!macroTouched.carbs && (
          <Text style={styles.helpText}>Auto-calculated (50% of calories)</Text>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>Daily Fat Target (g)</Text>
        <TextInput
          style={[styles.input, errors.fat && styles.inputError]}
          value={formData.targetFat?.toString() || ''}
          onChangeText={(text) => {
            const value = text ? parseFloat(text) : undefined;
            setFormData({ ...formData, targetFat: value });
            setMacroTouched({ ...macroTouched, fat: true });
          }}
          onFocus={() => setMacroTouched({ ...macroTouched, fat: true })}
          keyboardType="numeric"
          placeholder="Auto-calculated"
        />
        {errors.fat && <Text style={styles.errorText}>{errors.fat}</Text>}
        {!macroTouched.fat && (
          <Text style={styles.helpText}>Auto-calculated (30% of calories)</Text>
        )}
      </View>

      {/* Meal Type Selection */}
      <View style={styles.section}>
        <MealTypeSelector
          selectedMealTypes={(formData.selectedMealTypes || []) as MealType[]}
          onSelectionChange={(selected) => {
            setFormData({ ...formData, selectedMealTypes: selected });
          }}
        />
        {errors.selectedMealTypes && (
          <Text style={styles.errorText}>{errors.selectedMealTypes}</Text>
        )}
      </View>

      {/* Progress Indicator */}
      {creationState.isCreating && (
        <View style={styles.progressContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.progressText}>
            Optimizing meal plan... {creationState.progress}%
          </Text>
        </View>
      )}

      {/* Submit Button */}
      <TouchableOpacity
        style={[
          styles.submitButton,
          creationState.isCreating && styles.submitButtonDisabled,
        ]}
        onPress={handleSubmit}
        disabled={creationState.isCreating}
      >
        {creationState.isCreating ? (
          <ActivityIndicator color={colors.white} />
        ) : (
          <Text style={styles.submitButtonText}>Create Meal Plan</Text>
        )}
      </TouchableOpacity>

      {/* Note about ingredient preferences */}
      <Text style={styles.note}>
        Note: Ingredient preferences (have/want/avoid) and dietary tags can be
        added in a future update. For now, the algorithm will use all available
        recipes.
      </Text>
    </ScrollView>
    </>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.screenPadding,
  },
  title: {
    fontSize: typography.fontSize.xxxl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
  },
  section: {
    marginBottom: spacing.md,
  },
  label: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.medium,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: spacing.borderRadius,
    padding: spacing.md,
    fontSize: typography.fontSize.md,
    backgroundColor: colors.surface,
    color: colors.textPrimary,
  },
  inputError: {
    borderColor: colors.error,
  },
  errorText: {
    color: colors.error,
    fontSize: typography.fontSize.sm,
    marginTop: spacing.xs,
  },
  helpText: {
    color: colors.textTertiary,
    fontSize: typography.fontSize.sm,
    marginTop: spacing.xs,
    fontStyle: 'italic',
  },
  progressContainer: {
    alignItems: 'center',
    marginVertical: spacing.lg,
  },
  progressText: {
    marginTop: spacing.md,
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
  },
  submitButton: {
    backgroundColor: colors.primary,
    borderRadius: spacing.borderRadius,
    padding: spacing.md,
    alignItems: 'center',
    marginTop: spacing.lg,
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
  },
  note: {
    marginTop: spacing.lg,
    fontSize: typography.fontSize.sm,
    color: colors.textTertiary,
    fontStyle: 'italic',
  },
});
