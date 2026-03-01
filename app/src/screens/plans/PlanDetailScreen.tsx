import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity, Alert } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { usePlans } from '../../hooks/usePlans';
import { DayCard } from '../../components/plan/DayCard';
import { colors, spacing, typography } from '../../theme';
import { planService } from '../../services/planService';

type RouteParams = {
  planId: string;
};

export const PlanDetailScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const { planId } = (route.params as RouteParams) ?? {};

  const { selectedPlan, isLoadingDetail, error, fetchPlanDetail } = usePlans();
  const [isActivating, setIsActivating] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);

  const handleActivatePlan = async () => {
    try {
      setIsActivating(true);
      await planService.activatePlan(planId);
      Alert.alert(
        'Plan Activated! 🎉',
        'Your meal plan is now active. All grocery items have been added to your pantry.',
        [
          {
            text: 'View Today',
            onPress: () => navigation.navigate('Today' as never),
          },
          {
            text: 'OK',
            style: 'cancel',
          },
        ]
      );
      // Refresh plan data
      await fetchPlanDetail(planId);
    } catch (err: any) {
      Alert.alert(
        'Error',
        err.response?.data?.detail || 'Failed to activate plan'
      );
    } finally {
      setIsActivating(false);
    }
  };

  const handleCancelPlan = async () => {
    Alert.alert(
      'Cancel Plan?',
      'Your pantry will keep its current state with remaining ingredients.',
      [
        {
          text: 'Keep Plan',
          style: 'cancel',
        },
        {
          text: 'Cancel Plan',
          style: 'destructive',
          onPress: async () => {
              try {
                setIsCancelling(true);
                await planService.cancelPlan(planId);
              Alert.alert('Plan Cancelled', 'Your plan has been cancelled successfully.');
              await fetchPlanDetail(planId);
            } catch (err: any) {
              Alert.alert('Error', err.response?.data?.detail || 'Failed to cancel plan');
            } finally {
              setIsCancelling(false);
            }
          },
        },
      ]
    );
  };

  React.useEffect(() => {
    if (planId) void fetchPlanDetail(planId);
  }, [fetchPlanDetail, planId]);

  if (!planId) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Missing planId</Text>
      </View>
    );
  }

  if (isLoadingDetail || !selectedPlan || selectedPlan.plan_id !== planId) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading plan…</Text>
        {error ? <Text style={styles.errorText}>{error}</Text> : null}
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>
        {selectedPlan.name || `${selectedPlan.start_date} • ${selectedPlan.duration_days} days`}
      </Text>

      <View style={styles.metrics}>
        <Text style={styles.metric}>Target: {selectedPlan.target_calories_per_day} kcal/day</Text>
        {selectedPlan.estimated_food_waste_g != null ? (
          <Text style={styles.metric}>Waste: {Math.round(selectedPlan.estimated_food_waste_g)}g</Text>
        ) : null}
        {selectedPlan.waste_reduction_percentage != null ? (
          <Text style={styles.metric}>Waste reduction: {selectedPlan.waste_reduction_percentage}%</Text>
        ) : null}

        <TouchableOpacity
          style={styles.groceryButton}
          onPress={() => navigation.navigate('GroceryList' as never, { planId: selectedPlan.plan_id } as never)}
        >
          <Text style={styles.groceryButtonText}>View Grocery List</Text>
        </TouchableOpacity>

        {selectedPlan.execution_status === 'draft' && (
          <TouchableOpacity
            style={[styles.activateButton, isActivating && styles.buttonDisabled]}
            onPress={handleActivatePlan}
            disabled={isActivating}
          >
            <Text style={styles.activateButtonText}>
              {isActivating ? 'Activating...' : 'Buy Groceries & Start Plan'}
            </Text>
          </TouchableOpacity>
        )}

        {selectedPlan.execution_status === 'active' && (
          <TouchableOpacity
            style={[styles.cancelButton, isCancelling && styles.buttonDisabled]}
            onPress={handleCancelPlan}
            disabled={isCancelling}
          >
            <Text style={styles.cancelButtonText}>
              {isCancelling ? 'Cancelling...' : 'Cancel Plan'}
            </Text>
          </TouchableOpacity>
        )}

        {(selectedPlan.execution_status === 'completed' || selectedPlan.execution_status === 'cancelled') && (
          <View style={styles.statusBadge}>
            <Text style={styles.statusBadgeText}>
              {selectedPlan.execution_status === 'completed' ? '✓ Completed' : '✕ Cancelled'}
            </Text>
          </View>
        )}
      </View>

      <Text style={styles.sectionTitle}>Days</Text>
      {selectedPlan.daily_menus.map((day) => (
        <DayCard
          key={`${selectedPlan.plan_id}-${day.day_number}`}
          day={day}
          onPress={() =>
            navigation.navigate(
              'DayDetail' as never,
              { planId: selectedPlan.plan_id, dayNumber: day.day_number } as never
            )
          }
        />
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
    marginBottom: spacing.md,
  },
  metrics: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: spacing.borderRadius,
    padding: spacing.md,
    marginBottom: spacing.lg,
    gap: spacing.xs,
  },
  metric: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  groceryButton: {
    marginTop: spacing.sm,
    backgroundColor: colors.primary,
    borderRadius: spacing.borderRadius,
    paddingVertical: spacing.sm,
    alignItems: 'center',
  },
  groceryButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
  },
  activateButton: {
    marginTop: spacing.sm,
    backgroundColor: colors.success,
    borderRadius: spacing.borderRadius,
    paddingVertical: spacing.md,
    alignItems: 'center',
  },
  activateButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.bold,
  },
  cancelButton: {
    marginTop: spacing.sm,
    backgroundColor: colors.error,
    borderRadius: spacing.borderRadius,
    paddingVertical: spacing.sm,
    alignItems: 'center',
  },
  cancelButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  statusBadge: {
    marginTop: spacing.sm,
    padding: spacing.sm,
    backgroundColor: colors.backgroundSecondary,
    borderRadius: spacing.borderRadius,
    alignItems: 'center',
  },
  statusBadgeText: {
    color: colors.textSecondary,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
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
});
