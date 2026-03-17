import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  RefreshControl,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { planService } from '../../services/planService';
import { pantryService } from '../../services/pantryService';
import { Screen } from '../../components/layout/Screen';
import { colors, typography, spacing } from '../../theme';

interface TodayMealIngredient {
  product_id: string;
  product_name: string;
  original_quantity_value: number;
  original_quantity_unit: string;
  grams: number;
}

interface TodayMeal {
  id: string;
  meal_type: string;
  recipe_id: string;
  recipe_name: string;
  servings: number;
  is_completed: boolean;
  completed_at: string | null;
  nutritional_info: {
    calories: number;
    protein_g: number;
    carbs_g: number;
    fat_g: number;
  };
  ingredients: TodayMealIngredient[];
}

interface ActivePlan {
  id: string;
  start_date: string;
  duration_days: number;
  execution_status: string;
}

export const TodayScreen: React.FC = () => {
  const [activePlan, setActivePlan] = useState<ActivePlan | null>(null);
  const [todayMeals, setTodayMeals] = useState<TodayMeal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedMealId, setExpandedMealId] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      setError(null);
      
      // Fetch active plan
      const plan = await planService.getActivePlan();
      
      if (!plan) {
        setActivePlan(null);
        setTodayMeals([]);
        setIsLoading(false);
        return;
      }
      
      setActivePlan(plan);
      
      // Fetch today's meals
      const todayMeals = await planService.getTodayMeals(plan.id);
      setTodayMeals(todayMeals);
    } catch (err: any) {
      console.error('Failed to load today data:', err);
      setError(err.message || 'Nie udało się pobrać danych');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  const refreshPantry = useCallback(async () => {
    try {
      await pantryService.getPantry();
    } catch (err: any) {
      console.warn('Failed to refresh pantry after meal toggle', err);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [loadData])
  );

  const onRefresh = useCallback(async () => {
    setIsRefreshing(true);
    await loadData();
  }, [loadData]);

  const handleToggleExpand = useCallback((mealId: string) => {
    setExpandedMealId(prev => prev === mealId ? null : mealId);
  }, []);

  const handleToggleMeal = useCallback(async (meal: TodayMeal) => {
    if (meal.is_completed) {
      // Uncomplete
      try {
        await planService.toggleMealComplete(meal.id, false);
        // Optimistic update
        setTodayMeals(prev =>
          prev.map(m =>
            m.id === meal.id
              ? { ...m, is_completed: false, completed_at: null }
              : m
            )
        );
        await refreshPantry();
      } catch (err: any) {
        Alert.alert('Błąd', err.response?.data?.detail || 'Nie udało się odznaczyć posiłku');
        // Revert on error
        await loadData();
      }
    } else {
      // Complete
      try {
        await planService.toggleMealComplete(meal.id, true);
        // Optimistic update
        setTodayMeals(prev =>
          prev.map(m =>
            m.id === meal.id
              ? { ...m, is_completed: true, completed_at: new Date().toISOString() }
              : m
            )
        );
        await refreshPantry();
      } catch (err: any) {
        Alert.alert('Błąd', err.response?.data?.detail || 'Nie udało się oznaczyć posiłku');
        // Revert on error
        await loadData();
      }
    }
  }, [loadData, refreshPantry]);

  if (isLoading) {
    return (
      <Screen scroll={false}>
        <View style={styles.centered}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      </Screen>
    );
  }

  if (!activePlan) {
    return (
      <Screen scroll={false}>
        <View style={styles.centered}>
          <Text style={styles.emptyTitle}>Brak aktywnego planu</Text>
          <Text style={styles.emptyText}>
            Utwórz i aktywuj plan posiłków, aby zobaczyć dzisiejsze posiłki
          </Text>
        </View>
      </Screen>
    );
  }

  if (error) {
    return (
      <Screen scroll={false}>
        <View style={styles.centered}>
          <Text style={styles.errorText}>Błąd: {error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={loadData}>
            <Text style={styles.retryButtonText}>Spróbuj ponownie</Text>
          </TouchableOpacity>
        </View>
      </Screen>
    );
  }

  if (todayMeals.length === 0) {
    return (
      <Screen
        refreshControl={
          <RefreshControl refreshing={isRefreshing} onRefresh={onRefresh} />
        }
      >
        <View style={styles.header}>
          <Text style={styles.title}>Dzisiaj</Text>
          <Text style={styles.subtitle}>
            {new Date().toLocaleDateString('pl-PL', { 
              weekday: 'long', 
              month: 'long', 
              day: 'numeric' 
            })}
          </Text>
        </View>
        <View style={styles.centered}>
          <Text style={styles.emptyTitle}>Brak posiłków dzisiaj</Text>
          <Text style={styles.emptyText}>
            Ta data jest poza zakresem Twojego planu
          </Text>
        </View>
      </Screen>
    );
  }

  const completedCount = todayMeals.filter(m => m.is_completed).length;
  const totalCalories = todayMeals.reduce((sum, m) => sum + m.nutritional_info.calories, 0);
  const completedCalories = todayMeals
    .filter(m => m.is_completed)
    .reduce((sum, m) => sum + m.nutritional_info.calories, 0);

  return (
    <Screen
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>Dzisiaj</Text>
        <Text style={styles.subtitle}>
          {new Date().toLocaleDateString('pl-PL', { 
            weekday: 'long', 
            month: 'long', 
            day: 'numeric' 
          })}
        </Text>
        <View style={styles.progressContainer}>
          <Text style={styles.progressText}>
            {completedCount} z {todayMeals.length} posiłków ukończonych
          </Text>
          <Text style={styles.caloriesText}>
            {Math.round(completedCalories)} / {Math.round(totalCalories)} kcal
          </Text>
        </View>
      </View>

      <View style={styles.mealsContainer}>
        <Text style={styles.hintText}>Kliknij na posiłek, aby zaznaczyć • Strzałka ▼ aby zobaczyć składniki</Text>
        {todayMeals.map((meal) => (
          <View key={meal.id}>
            <TouchableOpacity
              style={[
                styles.mealCard,
                meal.is_completed && styles.mealCardCompleted,
              ]}
              onPress={() => handleToggleMeal(meal)}
              activeOpacity={0.7}
            >
              <View style={styles.mealCheckbox}>
                {meal.is_completed && (
                  <Text style={styles.checkmark}>✓</Text>
                )}
              </View>
              
              <View style={styles.mealContent}>
                <Text style={[
                  styles.mealType,
                  meal.is_completed && styles.mealTypeCompleted,
                ]}>
                  {formatMealType(meal.meal_type)}
                </Text>
                
                <Text style={[
                  styles.mealTitle,
                  meal.is_completed && styles.mealTitleCompleted,
                ]}>
                  {meal.recipe_name}
                </Text>
                
                <View style={styles.nutritionRow}>
                  <Text style={styles.nutritionText}>
                    {Math.round(meal.nutritional_info.calories)} kcal
                  </Text>
                  <Text style={styles.nutritionDivider}>•</Text>
                  <Text style={styles.nutritionText}>
                    B: {Math.round(meal.nutritional_info.protein_g)}g
                  </Text>
                  <Text style={styles.nutritionDivider}>•</Text>
                  <Text style={styles.nutritionText}>
                    W: {Math.round(meal.nutritional_info.carbs_g)}g
                  </Text>
                  <Text style={styles.nutritionDivider}>•</Text>
                  <Text style={styles.nutritionText}>
                    T: {Math.round(meal.nutritional_info.fat_g)}g
                  </Text>
                </View>
              </View>

              <TouchableOpacity 
                style={styles.expandButton}
                onPress={() => handleToggleExpand(meal.id)}
                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
              >
                <Text style={styles.expandIcon}>
                  {expandedMealId === meal.id ? '▲' : '▼'}
                </Text>
              </TouchableOpacity>
            </TouchableOpacity>

            {expandedMealId === meal.id && meal.ingredients && meal.ingredients.length > 0 && (
              <View style={styles.ingredientsContainer}>
                <Text style={styles.ingredientsTitle}>Składniki:</Text>
                {meal.ingredients.map((ing) => (
                  <View key={ing.product_id} style={styles.ingredientRow}>
                    <Text style={styles.ingredientName}>{ing.product_name}</Text>
                    <Text style={styles.ingredientAmount}>
                      {ing.grams}g
                      {ing.original_quantity_unit && ing.original_quantity_unit !== 'g' && (
                        <Text style={styles.ingredientOriginal}> ({ing.original_quantity_value}{ing.original_quantity_unit})</Text>
                      )}
                    </Text>
                  </View>
                ))}
              </View>
            )}
          </View>
        ))}
      </View>

      {completedCount === todayMeals.length && (
        <View style={styles.celebrationContainer}>
          <Text style={styles.celebrationText}>🎉 Wszystko gotowe na dziś!</Text>
        </View>
      )}
    </Screen>
  );
};

function formatMealType(type: string): string {
  const map: Record<string, string> = {
    'breakfast': 'Śniadanie',
    'second_breakfast': 'Drugie śniadanie',
    'dinner': 'Obiad',
    'dessert': 'Deser',
    'supper': 'Kolacja',
  };
  return map[type] || type;
}

const styles = StyleSheet.create({
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
  },
  header: {
    padding: spacing.lg,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
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
    marginBottom: spacing.md,
  },
  progressContainer: {
    marginTop: spacing.sm,
  },
  progressText: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
  },
  caloriesText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  mealsContainer: {
    padding: spacing.md,
  },
  hintText: {
    fontSize: typography.fontSize.sm,
    color: colors.textTertiary,
    textAlign: 'center',
    marginBottom: spacing.md,
    fontStyle: 'italic',
  },
  mealCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderWidth: 2,
    borderColor: colors.border,
  },
  mealCardCompleted: {
    backgroundColor: colors.backgroundSecondary,
    borderColor: colors.success,
  },
  mealCheckbox: {
    width: 32,
    height: 32,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  checkmark: {
    fontSize: 20,
    color: colors.primary,
    fontWeight: typography.fontWeight.bold,
  },
  mealContent: {
    flex: 1,
  },
  mealType: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  mealTypeCompleted: {
    color: colors.textSecondary,
  },
  mealTitle: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.medium,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  mealTitleCompleted: {
    color: colors.textSecondary,
  },
  nutritionRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  nutritionText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  nutritionDivider: {
    marginHorizontal: spacing.xs,
    color: colors.textTertiary,
  },
  expandButton: {
    padding: spacing.xs,
    marginLeft: spacing.xs,
  },
  expandIcon: {
    fontSize: 20,
  },
  ingredientsContainer: {
    backgroundColor: colors.backgroundSecondary,
    borderRadius: 8,
    padding: spacing.md,
    marginTop: -spacing.sm,
    marginBottom: spacing.md,
    marginLeft: 44,
  },
  ingredientsTitle: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  ingredientRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.xs,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  ingredientName: {
    fontSize: typography.fontSize.sm,
    color: colors.textPrimary,
    flex: 1,
  },
  ingredientAmount: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium,
    color: colors.primary,
  },
  ingredientOriginal: {
    fontSize: typography.fontSize.xs,
    color: colors.textTertiary,
  },
  celebrationContainer: {
    padding: spacing.xl,
    alignItems: 'center',
  },
  celebrationText: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    color: colors.success,
  },
  emptyTitle: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  emptyText: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  errorText: {
    fontSize: typography.fontSize.md,
    color: colors.error,
    marginBottom: spacing.md,
    textAlign: 'center',
  },
  retryButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: 8,
  },
  retryButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
  },
});
