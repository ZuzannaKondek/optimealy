import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { colors, spacing, typography } from '../../theme';

type DayData = {
  day: string; // Short day name like 'Pn', 'Wt', 'Śr'
  wasteGrams: number;
};

type Props = {
  data: DayData[];
  title?: string;
  unit?: string;
};

export const WasteChart: React.FC<Props> = ({ 
  data, 
  title = 'Odpady żywności', 
  unit = 'g' 
}) => {
  const maxWaste = Math.max(...data.map(d => d.wasteGrams), 1);
  
  // For waste, we want to show it's low - use different scale
  const displayMax = Math.max(maxWaste * 1.2, 50); // Minimum scale of 50g
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{title}</Text>
      
      <View style={styles.chartContainer}>
        {data.map((item, index) => {
          const heightPercent = (item.wasteGrams / displayMax) * 100;
          const isLowWaste = item.wasteGrams <= 30;
          
          return (
            <View key={index} style={styles.barWrapper}>
              <Text style={styles.value}>{item.wasteGrams}{unit}</Text>
              <View style={styles.barContainer}>
                <View 
                  style={[
                    styles.bar, 
                    { height: `${Math.max(heightPercent, 5)}%` },
                    isLowWaste ? styles.barLow : styles.barHigh
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
          <View style={[styles.legendDot, styles.legendDotLow]} />
          <Text style={styles.legendText}>Niskie (&lt;30g)</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, styles.legendDotHigh]} />
          <Text style={styles.legendText}>Wyższe</Text>
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
    flex: 1,
  } as ViewStyle,
  title: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium,
    color: colors.textSecondary,
    marginBottom: spacing.md,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  } as ViewStyle,
  chartContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    height: 100,
    marginBottom: spacing.sm,
  } as ViewStyle,
  barWrapper: {
    flex: 1,
    alignItems: 'center',
  } as ViewStyle,
  value: {
    fontSize: typography.fontSize.xs,
    color: colors.textTertiary,
    marginBottom: spacing.xs,
  } as ViewStyle,
  barContainer: {
    width: '60%',
    height: 80,
    justifyContent: 'flex-end',
    backgroundColor: colors.gray100,
    borderRadius: spacing.borderRadiusSmall,
    overflow: 'hidden',
  } as ViewStyle,
  bar: {
    width: '100%',
    borderRadius: spacing.borderRadiusSmall,
    minHeight: 4,
  } as ViewStyle,
  barLow: {
    backgroundColor: colors.success,
  } as ViewStyle,
  barHigh: {
    backgroundColor: colors.warning,
  } as ViewStyle,
  label: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    fontWeight: typography.fontWeight.medium,
  } as ViewStyle,
  legend: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: spacing.md,
    marginTop: spacing.sm,
  } as ViewStyle,
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
  } as ViewStyle,
  legendDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: spacing.xs,
  } as ViewStyle,
  legendDotLow: {
    backgroundColor: colors.success,
  } as ViewStyle,
  legendDotHigh: {
    backgroundColor: colors.warning,
  } as ViewStyle,
  legendText: {
    fontSize: typography.fontSize.xs,
    color: colors.textTertiary,
  } as ViewStyle,
});
