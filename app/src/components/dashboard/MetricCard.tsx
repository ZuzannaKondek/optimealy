import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { colors, spacing, typography } from '../../theme';

type Props = {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: {
    value: string;
    isPositive: boolean;
  };
};

export const MetricCard: React.FC<Props> = ({ title, value, subtitle, trend }) => {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.value}>{value}</Text>
      {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
      {trend && (
        <View style={styles.trendContainer}>
          <Text style={[styles.trend, trend.isPositive ? styles.trendPositive : styles.trendNegative]}>
            {trend.isPositive ? '↑' : '↓'} {trend.value}
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: spacing.borderRadius,
    padding: spacing.md,
    flex: 1,
  } as ViewStyle,
  title: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  } as ViewStyle,
  value: {
    fontSize: typography.fontSize.xxl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  } as ViewStyle,
  subtitle: {
    fontSize: typography.fontSize.sm,
    color: colors.textTertiary,
  } as ViewStyle,
  trendContainer: {
    marginTop: spacing.sm,
  } as ViewStyle,
  trend: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium,
  } as ViewStyle,
  trendPositive: {
    color: colors.success,
  } as ViewStyle,
  trendNegative: {
    color: colors.error,
  } as ViewStyle,
});
