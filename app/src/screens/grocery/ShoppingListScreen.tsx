import React from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, Alert } from 'react-native';
import { useRoute } from '@react-navigation/native';
import { planService } from '../../services/planService';
import { pantryService } from '../../services/pantryService';
import { GroceryItemCard } from '../../components/grocery/GroceryItemCard';
import { ColumnBoard } from '../../components/layout/ColumnBoard';
import { Section } from '../../components/layout/Section';
import { Screen } from '../../components/layout/Screen';
import { ScreenHeader } from '../../components/layout/ScreenHeader';
import { colors, spacing, typography } from '../../theme';
import type { GroceryList, GroceryItem } from '../../types/models';

const categoryTranslations: Record<string, string> = {
  vegetable: 'Warzywa',
  fruit: 'Owoce',
  dairy: 'Nabiał',
  protein: 'Białko',
  grain: 'Zboża',
  spice: 'Przyprawy',
  condiment: 'Przyprawy',
  oil: 'Oleje',
  beverage: 'Napoje',
  bakery: 'Pieczywo',
  frozen: 'Mrożonki',
  snacks: 'Przekąski',
  canned: 'Konserwy',
  other: 'Inne',
};

const translateCategory = (category: string): string => {
  return categoryTranslations[category.toLowerCase()] || category;
};

type RouteParams = {
  planId: string;
};

export const ShoppingListScreen: React.FC<{ planId?: string }> = ({ planId: propPlanId }) => {
  const route = useRoute();
  // Use prop planId if provided (from wrapper), otherwise fall back to route params
  const { planId: routePlanId } = (route.params as RouteParams) ?? {};
  const planId = propPlanId ?? routePlanId;

  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [groceryList, setGroceryList] = React.useState<GroceryList | null>(null);
  const [hiddenProductIds, setHiddenProductIds] = React.useState<Set<string>>(() => new Set());
  const [processingProductIds, setProcessingProductIds] = React.useState<Set<string>>(() => new Set());

  // Load grocery list on mount and when planId changes
  React.useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setIsLoading(true);
      setError(null);
      setHiddenProductIds(new Set());
      setProcessingProductIds(new Set());
      try {
        const list = await planService.getGroceryList(planId, { groupBy: 'category' });
        if (!cancelled) setGroceryList(list);
      } catch (e: any) {
        if (!cancelled) setError(e?.response?.data?.detail || 'Nie udało się pobrać listy zakupów');
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    if (planId) void load();
    return () => {
      cancelled = true;
    };
  }, [planId]);

  const handleItemBought = async (item: GroceryItem) => {
    if (!planId || processingProductIds.has(item.product_id)) return;

    setHiddenProductIds((current) => {
      const next = new Set(current);
      next.add(item.product_id);
      return next;
    });
    setProcessingProductIds((current) => {
      const next = new Set(current);
      next.add(item.product_id);
      return next;
    });

    try {
      await pantryService.updatePantry([
        {
          product_id: item.product_id,
          quantity_g: item.purchase_quantity_g,
        },
      ]);
      Alert.alert('Sukces', `Dodano "${item.product_name}" do spiżarni`);
    } catch (e: any) {
      setHiddenProductIds((current) => {
        const next = new Set(current);
        next.delete(item.product_id);
        return next;
      });
      Alert.alert('Błąd', e?.response?.data?.detail || 'Nie udało się dodać produktu do spiżarni');
      return;
    } finally {
      setProcessingProductIds((current) => {
        const next = new Set(current);
        next.delete(item.product_id);
        return next;
      });
    }

    try {
      const list = await planService.getGroceryList(planId, { groupBy: 'category' });
      setGroceryList(list);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Nie udało się odświeżyć listy zakupów');
    }
  };

  // If no planId provided, show empty state with option to select a plan
  if (!planId) {
    return (
      <View style={styles.center}>
        <Text style={styles.emptyTitle}>Wybierz plan</Text>
        <Text style={styles.emptySubtext}>Przejdź do szczegółów planu, aby zobaczyć listę zakupów</Text>
      </View>
    );
  }

  if (isLoading || !groceryList) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Generowanie listy zakupów…</Text>
        {error ? <Text style={styles.errorText}>{error}</Text> : null}
      </View>
    );
  }

  // Only show items that need to be bought (not already in pantry) - consistent with GroceryListScreen
  const allItems = groceryList.items.filter(
    (item: GroceryItem) => item.status !== 'already_have' && !hiddenProductIds.has(item.product_id)
  );

  // Group by category
  const grouped: Record<string, GroceryItem[]> = {};
  for (const item of allItems) {
    const key = item.category || 'other';
    grouped[key] = grouped[key] ? [...grouped[key], item] : [item];
  }

  const categories = Object.keys(grouped).sort();

  // Count items still needed to buy (allItems already filtered to exclude 'already_have')
  const itemsToBuyCount = allItems.length;

  // Check if items exist but are already in pantry
  const hasItemsInPantry = groceryList.items.some((item: GroceryItem) => item.status !== 'needed');

  if (allItems.length === 0) {
    return (
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <Text style={styles.title}>Zakupy</Text>
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>
            {hasItemsInPantry ? 'Wszystko masz w spiżarni!' : 'Brak produktów na liście'}
          </Text>
          <Text style={styles.emptySubtext}>
            {hasItemsInPantry ? 'Produkty z Twojego planu są już w spiżarni' : 'Wygeneruj listę zakupów z planu posiłków'}
          </Text>
        </View>
      </ScrollView>
    );
  }

  return (
    <Screen>
      <ScreenHeader
        title="Zakupy"
        subtitle={itemsToBuyCount > 0 ? `Do kupienia: ${itemsToBuyCount} produktów` : 'Wszystko masz w spiżarni!'}
      />
      <Section title="Wskazówki">
        <Text style={styles.sectionText}>
          Stuknij w produkt gdy masz go w koszyku, aby przenieść do spiżarni
        </Text>
      </Section>
      <ColumnBoard
        categories={categories}
        groupedItems={grouped}
        translateCategory={translateCategory}
        renderItem={(item) => (
          <GroceryItemCard
            key={item.item_id}
            item={item}
            onPress={() => handleItemBought(item)}
          />
        )}
      />
    </Screen>
  );
};

// Simple shopping item card without add button
// Removed - now using GroceryItemCard from components

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
  errorText: {
    color: colors.error,
    textAlign: 'center',
  },
  emptyTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
    textAlign: 'center',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: spacing.xxl * 2,
  },
  emptyText: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  emptySubtext: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
  },
  sectionText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  card: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: spacing.borderRadius,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  titleText: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  meta: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  usedIn: {
    marginTop: spacing.sm,
    fontSize: typography.fontSize.sm,
    color: colors.textTertiary,
  },
});
