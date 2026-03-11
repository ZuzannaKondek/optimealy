import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useFocusEffect, useNavigation } from '@react-navigation/native';
import { usePlans } from '../../hooks/usePlans';
import { PlanCard } from '../../components/plan/PlanCard';
import { Button } from '../../components/common/Button';
import { colors, spacing, typography } from '../../theme';

export const UserPanelScreen: React.FC = () => {
  const navigation = useNavigation();
  const { plans, isLoading, fetchPlans } = usePlans();

  useFocusEffect(
    React.useCallback(() => {
      void fetchPlans({ limit: 5, offset: 0, append: false });
    }, [fetchPlans])
  );

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Pulpit</Text>
      <Text style={styles.subtitle}>Twoje ostatnie plany posiłków i szybkie akcje.</Text>

      <View style={styles.actions}>
        <Button title="Utwórz nowy plan" onPress={() => navigation.navigate('CreatePlan' as never)} />
      </View>

      <Text style={styles.sectionTitle}>Ostatnie plany</Text>
      {isLoading && plans.length === 0 ? (
        <Text style={styles.loadingText}>Ładowanie…</Text>
      ) : plans.length === 0 ? (
        <Text style={styles.emptyText}>Brak planów. Utwórz pierwszy, aby zacząć.</Text>
      ) : (
        plans.map((p) => (
          <PlanCard
            key={p.plan_id}
            plan={p}
            onPress={() => navigation.navigate('PlanDetail' as never, { planId: p.plan_id } as never)}
          />
        ))
      )}
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
  title: {
    fontSize: typography.fontSize.xxxl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
  },
  actions: {
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  loadingText: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
  },
  emptyText: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
  },
});
