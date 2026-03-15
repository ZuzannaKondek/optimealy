import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import type { DailyMenu } from '../../types/models';
import { colors, spacing, typography } from '../../theme';
import { formatCalories, formatNutritionalValue } from '../../utils/unitConversion';
import { useAuth } from '../../context/AuthContext';

type Props = {
  day: DailyMenu;
  onPress?: () => void;
};

function formatPct(value: number | null | undefined): string {
  if (value == null) return '—';
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}%`;
}

export const DayCard: React.FC<Props> = ({ day, onPress }) => {
  const calVar = day.variance_from_target?.calorie_variance_pct ?? null;
  const { user } = useAuth();
  const unitPreference = (user?.unit_preference ?? 'metric') as 'metric' | 'imperial';

  return (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={0.8}
      style={styles.card}
      accessibilityRole="button"
      accessibilityLabel={`Dzień ${day.day_number} szczegóły`}
    >
      <View style={styles.headerRow}>
        <Text style={styles.title}>Dzień {day.day_number}</Text>
        <Text style={styles.date}>{day.menu_date}</Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.meta}>
          {formatCalories(day.actual_calories)} ({formatPct(calVar)})
        </Text>
        <Text style={styles.meta}>
          B {formatNutritionalValue(day.actual_protein_g, unitPreference)} • W{' '}
          {formatNutritionalValue(day.actual_carbs_g, unitPreference)} • T{' '}
          {formatNutritionalValue(day.actual_fat_g, unitPreference)}
        </Text>
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
    alignItems: 'baseline',
    marginBottom: spacing.xs,
  },
  title: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
  },
  date: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  row: {
    gap: spacing.xs,
  },
  meta: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
});

