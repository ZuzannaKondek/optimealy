import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { usePlans } from '../../hooks/usePlans';
import { PlanCard } from '../../components/plan/PlanCard';
import { Button } from '../../components/common/Button';
import { colors, spacing, typography } from '../../theme';

export const UserPanelScreen: React.FC = () => {
  const navigation = useNavigation();
  const { plans, isLoading, fetchPlans } = usePlans();

  React.useEffect(() => {
    void fetchPlans({ limit: 5, offset: 0, append: false });
  }, [fetchPlans]);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Dashboard</Text>
      <Text style={styles.subtitle}>Your recent meal plans and quick actions.</Text>

      <View style={styles.actions}>
        <Button title="Create New Plan" onPress={() => navigation.navigate('Create' as never)} />
        <Button
          title="Settings"
          variant="secondary"
          onPress={() => navigation.navigate('Settings' as never)}
          style={{ marginTop: spacing.sm }}
        />
      </View>

      <Text style={styles.sectionTitle}>Recent Plans</Text>
      {isLoading && plans.length === 0 ? (
        <Text style={styles.loadingText}>Loading…</Text>
      ) : plans.length === 0 ? (
        <Text style={styles.emptyText}>No plans yet. Create one to get started.</Text>
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

