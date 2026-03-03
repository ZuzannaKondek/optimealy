import React from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { useRoute } from '@react-navigation/native';
import { usePlans } from '../../hooks/usePlans';
import { planService } from '../../services/planService';
import { MealCard } from '../../components/plan/MealCard';
import { colors, spacing, typography } from '../../theme';
import type { DailyMenu } from '../../types/models';

type RouteParams = {
  planId: string;
  dayNumber: number;
};

export const DayDetailScreen: React.FC = () => {
  const route = useRoute();
  const { planId, dayNumber } = (route.params as RouteParams) ?? {};

  const { selectedPlan } = usePlans();
  const [day, setDay] = React.useState<DailyMenu | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  // Check if this is a dish-based plan
  // First try from selectedPlan, then fall back to detecting from meal data
  // A plan is dish-based if it has dish_weight_g values (indicates dish-based planning)
  const isDishBasedPlan = 
    (selectedPlan?.dishes_per_day != null && selectedPlan.dishes_per_day > 0) ||
    (day?.meals.some(m => m.dish_weight_g != null) ?? false);

  React.useEffect(() => {
    const existing =
      selectedPlan && selectedPlan.plan_id === planId
        ? selectedPlan.daily_menus.find((d) => d.day_number === dayNumber)
        : undefined;

    if (existing) {
      setDay(existing);
      return;
    }

    let cancelled = false;
    const load = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await planService.getPlanDay(planId, dayNumber);
        if (!cancelled) setDay(response.daily_menu);
      } catch (e: any) {
        if (!cancelled) setError(e?.response?.data?.detail || 'Failed to load day details');
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    if (planId && dayNumber) void load();
    return () => {
      cancelled = true;
    };
  }, [dayNumber, planId, selectedPlan]);

  if (!planId || !dayNumber) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Brak planId/dayNumber</Text>
      </View>
    );
  }

  if (isLoading || !day) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Ładowanie dnia…</Text>
        {error ? <Text style={styles.errorText}>{error}</Text> : null}
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>
        Dzień {day.day_number} • {day.menu_date}
      </Text>
      <Text style={styles.subtitle}>{day.actual_calories} kcal</Text>

      <Text style={styles.sectionTitle}>
        {isDishBasedPlan ? `Dania (${day.meals.length})` : 'Posiłki'}
      </Text>
      {day.meals.map((meal) => (
        <View key={meal.meal_id}>
          <MealCard meal={meal} isDishBasedPlan={isDishBasedPlan} />
          {meal.recipe?.instructions_single_serving && (
            <View style={styles.instructionsContainer}>
              <Text style={styles.instructionsTitle}>Instrukcje przygotowania</Text>
              <Text style={styles.instructionsText}>
                {meal.recipe.instructions_single_serving}
              </Text>
            </View>
          )}
        </View>
      ))}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.screenPadding,
    paddingBottom: spacing.lg,
  },
  center: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.background,
    padding: spacing.lg,
  },
  loadingText: {
    marginTop: spacing.sm,
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
  },
  title: {
    fontSize: typography.fontSize.xxl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  errorText: {
    color: colors.error,
    textAlign: 'center',
  },
  instructionsContainer: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: spacing.borderRadius,
    padding: spacing.md,
    marginTop: spacing.xs,
    marginBottom: spacing.sm,
  },
  instructionsTitle: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  instructionsText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: typography.lineHeight.md,
  },
});

