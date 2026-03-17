import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { colors, spacing, typography } from '../../theme';

type DayData = {
  day: string; // Short day name like 'Pn', 'Wt', 'Śr'
  calories: number;
  target?: number;
};

type Props = {
  data: DayData[];
  title?: string;
  unit?: string;
};

export const CaloriesChart: React.FC<Props> = ({
  data,
  title = 'Kalorie',
  unit = 'kcal'
}) => {
  const maxCalories = Math.max(...data.map(d => d.calories), 1);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{title}</Text>

      <View style={styles.chartContainer}>
        {data.map((item, index) => {
          const heightPercent = (item.calories / maxCalories) * 100;
          const isOverTarget = item.target && item.calories > item.target;

          return (
            <View key={index} style={styles.barWrapper}>
              <Text style={styles.value}>{item.calories}</Text>
              <View style={styles.barContainer}>
                <View
                  style={[
                    styles.bar,
                    { height: `${heightPercent}%` },
                    isOverTarget && styles.barOverTarget
                  ]}
                />
              </View>
              <Text style={styles.label}>{item.day}</Text>
            </View>
          );
        })}
      </View>

      <View style={styles.legend}>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, styles.legendDotActual]} />
          <Text style={styles.legendText}>Kalorie</Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: spacing.borderRadius,
    padding: spacing.md,
    height: 210,
    overflow: 'hidden'
  } as ViewStyle,
  title: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium,
    color: colors.textSecondary,
    marginBottom: spacing.md,
    textTransform: 'uppercase',
    letterSpacing: 0.5
  } as ViewStyle,
  chartContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    height: 100,
    marginBottom: spacing.sm
  } as ViewStyle,
  barWrapper: {
    flex: 1,
    alignItems: 'center'
  } as ViewStyle,
  value: {
    fontSize: typography.fontSize.xs,
    color: colors.textTertiary,
    marginBottom: spacing.xs
  } as ViewStyle,
  barContainer: {
    width: '60%',
    height: 80,
    justifyContent: 'flex-end',
    backgroundColor: colors.gray100,
    borderRadius: spacing.borderRadiusSmall,
    overflow: 'hidden'
  } as ViewStyle,
  bar: {
    width: '100%',
    backgroundColor: colors.primary,
    borderRadius: spacing.borderRadiusSmall,
    minHeight: 4
  } as ViewStyle,
  barOverTarget: {
    backgroundColor: colors.warning
  } as ViewStyle,
  label: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    fontWeight: typography.fontWeight.medium
  } as ViewStyle,
  legend: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: spacing.sm
  } as ViewStyle,
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center'
  } as ViewStyle,
  legendDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: spacing.xs
  } as ViewStyle,
  legendDotActual: {
    backgroundColor: colors.primary
  } as ViewStyle,
  legendText: {
    fontSize: typography.fontSize.xs,
    color: colors.textTertiary
  } as ViewStyle,
});
