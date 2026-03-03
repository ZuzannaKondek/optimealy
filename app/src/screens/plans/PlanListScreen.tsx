import React from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl, ActivityIndicator, TouchableOpacity } from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { usePlans } from '../../hooks/usePlans';
import { PlanCard } from '../../components/plan/PlanCard';
import { colors, spacing, typography } from '../../theme';

const PAGE_SIZE = 10;

export const PlanListScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const { plans, isLoading, error, fetchPlans } = usePlans();

  const [isRefreshing, setIsRefreshing] = React.useState(false);
  const [hasMore, setHasMore] = React.useState(true);

  const loadInitial = React.useCallback(async () => {
    setHasMore(true);
    await fetchPlans({ limit: PAGE_SIZE, offset: 0, append: false });
  }, [fetchPlans]);

  // Refetch when screen gains focus so newly created plans appear (e.g. after Create flow)
  useFocusEffect(
    React.useCallback(() => {
      void loadInitial();
    }, [loadInitial])
  );

  const onRefresh = async () => {
    setIsRefreshing(true);
    await loadInitial();
    setIsRefreshing(false);
  };

  const onEndReached = async () => {
    if (isLoading || !hasMore) return;

    const prevLen = usePlans.getState().plans.length;
    await fetchPlans({ limit: PAGE_SIZE, offset: prevLen, append: true });
    const newLen = usePlans.getState().plans.length;
    setHasMore(newLen - prevLen === PAGE_SIZE);
  };

  React.useLayoutEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <TouchableOpacity
          onPress={() => navigation.navigate('CreatePlan')}
          style={styles.headerButton}
        >
          <Text style={styles.headerButtonText}>+ Utwórz</Text>
        </TouchableOpacity>
      ),
    });
  }, [navigation]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Moje plany</Text>

      {error ? <Text style={styles.errorText}>{error}</Text> : null}

      {isLoading && plans.length === 0 ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.loadingText}>Ładowanie planów…</Text>
        </View>
      ) : (
        <FlatList
          data={plans}
          keyExtractor={(item) => item.plan_id}
          contentContainerStyle={styles.listContent}
          refreshControl={<RefreshControl refreshing={isRefreshing} onRefresh={onRefresh} />}
          renderItem={({ item }) => (
            <PlanCard
              plan={item}
              onPress={() => navigation.navigate('PlanDetail' as never, { planId: item.plan_id } as never)}
            />
          )}
          onEndReached={onEndReached}
          onEndReachedThreshold={0.5}
          ListFooterComponent={
            isLoading && plans.length > 0 ? (
              <View style={styles.footer}>
                <ActivityIndicator color={colors.primary} />
              </View>
            ) : null
          }
          ListEmptyComponent={
            !isLoading ? (
              <View style={styles.center}>
                <Text style={styles.emptyText}>Brak planów posiłków.</Text>
                <TouchableOpacity
                  onPress={() => navigation.navigate('CreatePlan')}
                  style={styles.createButton}
                >
                  <Text style={styles.createButtonText}>Utwórz pierwszy plan</Text>
                </TouchableOpacity>
              </View>
            ) : null
          }
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  title: {
    fontSize: typography.fontSize.xxl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    paddingHorizontal: spacing.screenPadding,
    paddingTop: spacing.md,
    paddingBottom: spacing.sm,
  },
  listContent: {
    paddingHorizontal: spacing.screenPadding,
    paddingBottom: spacing.lg,
  },
  center: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.lg,
  },
  loadingText: {
    marginTop: spacing.sm,
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
  },
  emptyText: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  errorText: {
    color: colors.error,
    paddingHorizontal: spacing.screenPadding,
    paddingBottom: spacing.sm,
  },
  footer: {
    paddingVertical: spacing.md,
    alignItems: 'center',
  },
  headerButton: {
    marginRight: spacing.md,
  },
  headerButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
  },
  createButton: {
    marginTop: spacing.md,
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: 8,
  },
  createButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
  },
});

