import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  RefreshControl,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { planService } from '../../services/planService';
import { colors, typography, spacing } from '../../theme';

interface TodayMeal {
  id: string;
  meal_type: string;
  recipe_id: string;
  servings: number;
  is_completed: boolean;
  completed_at: string | null;
  nutritional_info: {
    calories: number;
    protein_g: number;
    carbs_g: number;
    fat_g: number;
  };
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

  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [loadData])
  );

  const onRefresh = useCallback(async () => {
    setIsRefreshing(true);
    await loadData();
  }, [loadData]);

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
      } catch (err: any) {
        Alert.alert('Błąd', err.response?.data?.detail || 'Nie udało się oznaczyć posiłku');
        // Revert on error
        await loadData();
      }
    }
  }, [loadData]);

  if (isLoading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (!activePlan) {
    return (
      <View style={styles.centered}>
        <Text style={styles.emptyTitle}>Brak aktywnego planu</Text>
        <Text style={styles.emptyText}>
          Utwórz i aktywuj plan posiłków, aby zobaczyć dzisiejsze posiłki
        </Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>Błąd: {error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={loadData}>
          <Text style={styles.retryButtonText}>Spróbuj ponownie</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (todayMeals.length === 0) {
    return (
      <ScrollView
        style={styles.container}
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
      </ScrollView>
    );
  }

  const completedCount = todayMeals.filter(m => m.is_completed).length;
  const totalCalories = todayMeals.reduce((sum, m) => sum + m.nutritional_info.calories, 0);
  const completedCalories = todayMeals
    .filter(m => m.is_completed)
    .reduce((sum, m) => sum + m.nutritional_info.calories, 0);

  return (
    <ScrollView
      style={styles.container}
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
        {todayMeals.map((meal) => (
          <TouchableOpacity
            key={meal.id}
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
          </TouchableOpacity>
        ))}
      </View>

      {completedCount === todayMeals.length && (
        <View style={styles.celebrationContainer}>
          <Text style={styles.celebrationText}>🎉 Wszystko gotowe na dziś!</Text>
        </View>
      )}
    </ScrollView>
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
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
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
    color: colors.text,
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
    color: colors.text,
  },
  caloriesText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  mealsContainer: {
    padding: spacing.md,
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
    color: colors.text,
    marginBottom: spacing.xs,
  },
  mealTypeCompleted: {
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
    color: colors.text,
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
