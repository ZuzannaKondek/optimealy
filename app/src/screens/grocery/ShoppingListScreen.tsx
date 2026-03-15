import React from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity, Alert, Animated, Dimensions } from 'react-native';
import { useRoute } from '@react-navigation/native';
import { planService } from '../../services/planService';
import { pantryService } from '../../services/pantryService';
import { CategorySection } from '../../components/grocery/CategorySection';
import { GroceryItemCard } from '../../components/grocery/GroceryItemCard';
import { colors, spacing, typography } from '../../theme';
import type { GroceryList, GroceryItem } from '../../types/models';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

type RouteParams = {
  planId: string;
};

// Animated item wrapper for slide-out effect
const AnimatedGroceryItem: React.FC<{
  item: GroceryItem;
  onPress: () => void;
  onAnimationComplete: () => void;
}> = ({ item, onPress, onAnimationComplete }) => {
  const slideAnim = React.useRef(new Animated.Value(0)).current;
  const opacityAnim = React.useRef(new Animated.Value(1)).current;

  React.useEffect(() => {
    Animated.parallel([
      Animated.timing(slideAnim, {
        toValue: -SCREEN_WIDTH,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(opacityAnim, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start(() => {
      onAnimationComplete();
    });
  }, [slideAnim, opacityAnim, onAnimationComplete]);

  return (
    <Animated.View
      style={[
        { transform: [{ translateX: slideAnim }], opacity: opacityAnim },
      ]}
    >
      <GroceryItemCard item={item} onPress={onPress} />
    </Animated.View>
  );
};

export const ShoppingListScreen: React.FC = () => {
  const route = useRoute();
  const { planId } = (route.params as RouteParams) ?? {};

  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [groceryList, setGroceryList] = React.useState<GroceryList | null>(null);
  const [removingItem, setRemovingItem] = React.useState<GroceryItem | null>(null);

  React.useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setIsLoading(true);
      setError(null);
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

  const handleAddAllToPantry = async () => {
    if (itemsToBuy.length === 0) {
      Alert.alert('Info', 'Wszystkie produkty są już w spiżarni');
      return;
    }

    try {
      await pantryService.updatePantry(
        itemsToBuy.map((item: GroceryItem) => ({
          product_id: item.product_id,
          quantity_g: item.required_quantity_g,
        }))
      );
      Alert.alert('Sukces', `Dodano ${itemsToBuy.length} produktów do spiżarni`);
      // Reload the list
      const list = await planService.getGroceryList(planId, { groupBy: 'category' });
      setGroceryList(list);
    } catch (e: any) {
      Alert.alert('Błąd', e?.response?.data?.detail || 'Nie udało się dodać produktów do spiżarni');
    }
  };

  const handleItemBought = async (item: GroceryItem) => {
    // Start animation - don't refresh list yet
    setRemovingItem(item);
  };

  const handleAnimationComplete = async () => {
    if (!removingItem) return;
    
    try {
      await pantryService.updatePantry([
        {
          product_id: removingItem.product_id,
          quantity_g: removingItem.required_quantity_g,
        },
      ]);
      Alert.alert('Sukces', `Dodano "${removingItem.product_name}" do spiżarni`);
    } catch (e: any) {
      Alert.alert('Błąd', e?.response?.data?.detail || 'Nie udało się dodać produktu do spiżarni');
    } finally {
      setRemovingItem(null);
      // Reload the list
      const list = await planService.getGroceryList(planId, { groupBy: 'category' });
      setGroceryList(list);
    }
  };

  if (!planId) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Brak planId</Text>
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

  // Filter to only items NOT in pantry (to buy)
  const itemsToBuy = groceryList.items.filter((item: GroceryItem) => item.status !== 'already_have');

  // Group by category
  const grouped: Record<string, GroceryItem[]> = {};
  for (const item of itemsToBuy) {
    const key = item.category || 'other';
    grouped[key] = grouped[key] ? [...grouped[key], item] : [item];
  }

  const categories = Object.keys(grouped).sort();

  if (itemsToBuy.length === 0) {
    return (
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <Text style={styles.title}>Zakupy</Text>
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>Wszystko masz w spiżarni!</Text>
          <Text style={styles.emptySubtext}>Nie musisz niczego kupować</Text>
        </View>
      </ScrollView>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Zakupy</Text>
      <Text style={styles.subtitle}>
        Do kupienia: {itemsToBuy.length} produktów
      </Text>

      <TouchableOpacity style={styles.addAllButton} onPress={handleAddAllToPantry}>
        <Text style={styles.addAllButtonText}>Dodaj wszystkie do spiżarni</Text>
      </TouchableOpacity>

      {categories.map((category) => (
        <CategorySection key={category} title={category}>
          {grouped[category].map((item) => {
            if (removingItem?.item_id === item.item_id) {
              return (
                <AnimatedGroceryItem
                  key={item.item_id}
                  item={item}
                  onPress={() => {}}
                  onAnimationComplete={handleAnimationComplete}
                />
              );
            }
            return (
              <GroceryItemCard key={item.item_id} item={item} onPress={() => handleItemBought(item)} />
            );
          })}
        </CategorySection>
      ))}
    </ScrollView>
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
  subtitle: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
  },
  errorText: {
    color: colors.error,
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
  addAllButton: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: spacing.borderRadius,
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  addAllButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
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
