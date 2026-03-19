import React from 'react';
import { Text, StyleSheet } from 'react-native';
import { useFocusEffect, useNavigation } from '@react-navigation/native';
import type { NavigationProp } from '@react-navigation/native';
import { usePlans } from '../../hooks/usePlans';
import { PlanCard } from '../../components/plan/PlanCard';
import { colors, spacing, typography } from '../../theme';

// Import new layout primitives
import { Screen } from '../../components/layout/Screen';
import { ScreenHeader } from '../../components/layout/ScreenHeader';
import { Section } from '../../components/layout/Section';
import { HorizontalRow } from '../../components/layout/HorizontalRow';
import { TwoUpRow } from '../../components/layout/TwoUpRow';
import { MetricCard } from '../../components/dashboard/MetricCard';
import { CaloriesChart } from '../../components/dashboard/CaloriesChart';
import { WasteChart } from '../../components/dashboard/WasteChart';

type RootStackParamList = {
  CreatePlan: undefined;
  PlanDetail: { planId: number };
};

export const UserPanelScreen: React.FC = () => {
  const navigation = useNavigation<NavigationProp<RootStackParamList>>();
  const { plans, isLoading, fetchPlans } = usePlans();

  useFocusEffect(
    React.useCallback(() => {
      void fetchPlans({ limit: 100, offset: 0, append: false });
    }, [fetchPlans])
  );

  const handleCreatePlan = () => {
    navigation.navigate('CreatePlan');
  };

  const handlePlanPress = (planId: number) => {
    navigation.navigate('PlanDetail', { planId });
  };

  // Sort plans: active first, then by date (newest first)
  const sortedPlans = [...plans].sort((a, b) => {
    const aActive = a.execution_status === 'active' ? 0 : 1;
    const bActive = b.execution_status === 'active' ? 0 : 1;
    if (aActive !== bActive) return aActive - bActive;
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  // Get target calories from first (active) plan for chart data
  const targetCalories = sortedPlans[0]?.target_calories_per_day || 2000;
  const chartData = [
    { day: 'Pn', calories: Math.round(targetCalories * 0.95) },
    { day: 'Wt', calories: Math.round(targetCalories * 1.02) },
    { day: 'Śr', calories: Math.round(targetCalories * 0.88) },
    { day: 'Czw', calories: Math.round(targetCalories * 1.05) },
    { day: 'Pt', calories: Math.round(targetCalories * 0.92) },
    { day: 'Sob', calories: Math.round(targetCalories * 1.1) },
    { day: 'Ndz', calories: Math.round(targetCalories * 0.85) },
  ];

  // Generate sample waste data showing low waste (real app would use actual waste data)
  const wasteData = [
    { day: 'Pn', wasteGrams: 25 },
    { day: 'Wt', wasteGrams: 18 },
    { day: 'Śr', wasteGrams: 32 },
    { day: 'Czw', wasteGrams: 15 },
    { day: 'Pt', wasteGrams: 22 },
    { day: 'Sob', wasteGrams: 28 },
    { day: 'Ndz', wasteGrams: 12 },
  ];

  return (
    <Screen scroll>
      <ScreenHeader
        title="Pulpit"
        subtitle="Twoje ostatnie plany posiłków i szybkie akcje."
        rightAction={{
          label: 'Utwórz nowy plan',
          onPress: handleCreatePlan,
        }}
      />

      <Section title="Ostatnie plany">
        {isLoading && sortedPlans.length === 0 ? (
          <Text style={styles.loadingText}>Ładowanie…</Text>
        ) : sortedPlans.length === 0 ? (
          <Text style={styles.emptyText}>Brak planów. Utwórz pierwszy, aby zacząć.</Text>
        ) : (
          <HorizontalRow>
            {sortedPlans.map((p) => (
              <PlanCard
                key={p.plan_id}
                plan={p}
                onPress={() => handlePlanPress(p.plan_id)}
              />
            ))}
          </HorizontalRow>
        )}
      </Section>

      <Section title="Statystyki">
        <TwoUpRow>
          <CaloriesChart data={chartData} title="Kalorie (7 dni)" />
          <WasteChart data={wasteData} title="Odpady (7 dni)" />
        </TwoUpRow>
      </Section>
    </Screen>
  );
};

const styles = StyleSheet.create({
  loadingText: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
  },
  emptyText: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
  },
});
