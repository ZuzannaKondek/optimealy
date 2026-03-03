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
      newErrors.name = 'Nazwa planu jest wymagana';
    } else if (trimmedName.length > 255) {
      newErrors.name = 'Nazwa planu może mieć maksymalnie 255 znaków';
    }

    if (formData.durationDays < 1 || formData.durationDays > 30) {
      newErrors.durationDays = 'Czas trwania musi być między 1 a 30 dni';
    }

    if (formData.targetCalories < 800 || formData.targetCalories > 5000) {
      newErrors.targetCalories = 'Kalorie muszą być między 800 a 5000';
    }

    if (formData.targetProtein !== undefined && formData.targetProtein < 0) {
      newErrors.targetProtein = 'Białko musi być dodatnie';
    }

    if (formData.targetCarbs !== undefined && formData.targetCarbs < 0) {
      newErrors.carbs = 'Węglowodany muszą być dodatnie';
    }

    if (formData.targetFat !== undefined && formData.targetFat < 0) {
      newErrors.fat = 'Tłuszcze muszą być dodatnie';
    }

    // Validate selected meal types
    if (!formData.selectedMealTypes || formData.selectedMealTypes.length === 0) {
      newErrors.selectedMealTypes = 'Wybierz co najmniej jeden typ posiłku';
    } else {
      const requiredTypes = ['breakfast', 'dinner', 'supper'];
      const selectedSet = new Set(formData.selectedMealTypes);
      const missing = requiredTypes.filter((type) => !selectedSet.has(type));
      if (missing.length > 0) {
        newErrors.selectedMealTypes = `Brakujące typy posiłków: ${missing.join(', ')}`;
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
        'Napraw następujące błędy:\n\n• ' +
        Object.values(formErrors).join('\n• ');
      Alert.alert(
        'Nieprawidłowe dane',
        message,
        [{ text: 'OK' }]
      );
      return;
    }

    const planName = (formData.name ?? '').trim();
    if (!planName) {
      setErrors((prev) => ({ ...prev, name: 'Nazwa planu jest wymagana' }));
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
    } catch (error: any) {
      const message = getApiErrorMessage(error);
      const suggestion =
        'Spróbuj dostosować swoje cele lub ograniczenia (np. kalorie 800–5000, czas trwania 1–30 dni, co najmniej śniadanie/obiad/kolacja).';
      Alert.alert(
        'Nie udało się utworzyć planu',
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
        message={creationState.error || 'Optymalizator nie mógł znaleźć planu spełniającego Twoje ograniczenia.'}
        onDismiss={resetCreationState}
      />
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Utwórz plan posiłków</Text>
      <Text style={styles.subtitle}>
        Wygeneruj zoptymalizowany plan posiłków, który zminimalizuje marnotrawstwo żywności
      </Text>

      {/* Plan name */}
      <View style={styles.section}>
        <Text style={styles.label}>Nazwa planu</Text>
        <TextInput
          style={[styles.input, errors.name && styles.inputError]}
          value={formData.name}
          onChangeText={(text) => setFormData((prev) => ({ ...prev, name: text }))}
          placeholder="np. Tydzień 13 lutego"
          maxLength={255}
          accessibilityLabel="Plan name"
        />
        {errors.name && (
          <Text style={styles.errorText}>{errors.name}</Text>
        )}
      </View>

      {/* Duration */}
      <View style={styles.section}>
        <Text style={styles.label}>Czas trwania (dni)</Text>
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
        <Text style={styles.label}>Dzienny cel kaloryczny</Text>
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
        <Text style={styles.label}>Dzienny cel białkowy (g)</Text>
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
          placeholder="Obliczone automatycznie"
        />
        {errors.targetProtein && (
          <Text style={styles.errorText}>{errors.targetProtein}</Text>
        )}
        {!macroTouched.protein && (
          <Text style={styles.helpText}>Obliczone automatycznie (20% kalorii)</Text>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>Dzienny cel węglowodanów (g)</Text>
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
          placeholder="Obliczone automatycznie"
        />
        {errors.carbs && <Text style={styles.errorText}>{errors.carbs}</Text>}
        {!macroTouched.carbs && (
          <Text style={styles.helpText}>Obliczone automatycznie (50% kalorii)</Text>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>Dzienny cel tłuszczowy (g)</Text>
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
          placeholder="Obliczone automatycznie"
        />
        {errors.fat && <Text style={styles.errorText}>{errors.fat}</Text>}
        {!macroTouched.fat && (
          <Text style={styles.helpText}>Obliczone automatycznie (30% kalorii)</Text>
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
            Optymalizowanie planu posiłków... {creationState.progress}%
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
          <Text style={styles.submitButtonText}>Utwórz plan posiłków</Text>
        )}
      </TouchableOpacity>

      {/* Note about ingredient preferences */}
      <Text style={styles.note}>
        Uwaga: Preferencje składników (mieć/chcieć/unikać) i tagi dietetyczne mogą być
        dodane w przyszłej aktualizacji. Na razie algorytm użyje wszystkich dostępnych
        przepisów.
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
