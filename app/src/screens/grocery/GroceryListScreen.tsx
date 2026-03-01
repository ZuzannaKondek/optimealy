import React from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { useRoute } from '@react-navigation/native';
import { planService } from '../../services/planService';
import { GroceryItemCard } from '../../components/grocery/GroceryItemCard';
import { CategorySection } from '../../components/grocery/CategorySection';
import { colors, spacing, typography } from '../../theme';
import type { GroceryList, GroceryItem } from '../../types/models';

type RouteParams = {
  planId: string;
};

export const GroceryListScreen: React.FC = () => {
  const route = useRoute();
  const { planId } = (route.params as RouteParams) ?? {};

  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [groceryList, setGroceryList] = React.useState<GroceryList | null>(null);

  React.useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const list = await planService.getGroceryList(planId, { groupBy: 'category' });
        if (!cancelled) setGroceryList(list);
      } catch (e: any) {
        if (!cancelled) setError(e?.response?.data?.detail || 'Failed to load grocery list');
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    if (planId) void load();
    return () => {
      cancelled = true;
    };
  }, [planId]);

  if (!planId) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Missing planId</Text>
      </View>
    );
  }

  if (isLoading || !groceryList) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Generating grocery list…</Text>
        {error ? <Text style={styles.errorText}>{error}</Text> : null}
      </View>
    );
  }

  const grouped: Record<string, GroceryItem[]> = {};
  for (const item of groceryList.items) {
    const key = item.category || 'other';
    grouped[key] = grouped[key] ? [...grouped[key], item] : [item];
  }

  const categories = Object.keys(grouped).sort();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Grocery List</Text>
      <Text style={styles.subtitle}>
        Items: {groceryList.total_items} • Waste: {Math.round(groceryList.estimated_total_waste_g)}g
      </Text>

      {categories.map((category) => (
        <CategorySection key={category} title={category}>
          {grouped[category].map((item) => (
            <GroceryItemCard key={item.item_id} item={item} />
          ))}
        </CategorySection>
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
    marginBottom: spacing.lg,
  },
  errorText: {
    color: colors.error,
    textAlign: 'center',
  },
});

