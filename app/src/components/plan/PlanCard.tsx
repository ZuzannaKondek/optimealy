import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import type { MealPlanSummary } from '../../types/models';
import { colors, spacing, typography } from '../../theme';

type Props = {
  plan: MealPlanSummary;
  onPress?: () => void;
};

export const PlanCard: React.FC<Props> = ({ plan, onPress }) => {
  const wasteText =
    plan.estimated_food_waste_g != null ? `${Math.round(plan.estimated_food_waste_g)}g odpadów` : 'Odpady: —';

  // Display execution status when available (draft/active/completed/cancelled), else optimization status
  const displayStatus =
    plan.execution_status === 'draft'
      ? 'Szkic'
      : plan.execution_status === 'active'
      ? 'Aktywny'
      : plan.execution_status === 'completed'
      ? 'Zakończony'
      : plan.execution_status === 'cancelled'
      ? 'Anulowany'
      : plan.optimization_status;

  // Styling: prefer execution_status for user-facing state, fall back to optimization_status
  const statusStyle =
    plan.execution_status === 'draft'
      ? styles.statusDefault
      : plan.execution_status === 'active'
      ? styles.statusCompleted
      : plan.execution_status === 'completed' || plan.execution_status === 'cancelled'
      ? styles.statusCompleted
      : plan.optimization_status === 'completed'
      ? styles.statusCompleted
      : plan.optimization_status === 'failed'
      ? styles.statusFailed
      : plan.optimization_status === 'in_progress'
      ? styles.statusInProgress
      : styles.statusDefault;

  return (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={0.8}
      style={styles.card}
      accessibilityRole="button"
      accessibilityLabel={plan.name || `Plan posiłków rozpoczynający się ${plan.start_date}`}
    >
      <View style={styles.headerRow}>
        <Text style={styles.title}>
          {plan.name || `${plan.start_date} • ${plan.duration_days} days`}
        </Text>
        <Text style={[styles.status, statusStyle]}>{displayStatus}</Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.meta}>Cel: {plan.target_calories_per_day} kcal/dzień</Text>
      </View>

      <View style={styles.footerRow}>
        <Text style={styles.footerItem}>{wasteText}</Text>
      </View>
    </TouchableOpacity>
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
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  title: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
    flex: 1,
    marginRight: spacing.sm,
  },
  status: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: spacing.borderRadius,
    borderWidth: 1,
    fontSize: typography.fontSize.xs,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    fontWeight: typography.fontWeight.medium,
  },
  statusCompleted: {
    backgroundColor: '#E8F5E9',
    borderColor: '#4CAF50',
    color: '#2E7D32',
  },
  statusFailed: {
    backgroundColor: '#FFEBEE',
    borderColor: '#F44336',
    color: '#C62828',
  },
  statusInProgress: {
    backgroundColor: '#FFF3E0',
    borderColor: '#FF9800',
    color: '#E65100',
  },
  statusDefault: {
    backgroundColor: colors.background,
    borderColor: colors.border,
    color: colors.textSecondary,
  },
  row: {
    marginTop: spacing.xs,
  },
  meta: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  footerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: spacing.sm,
  },
  footerItem: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
});

