import React from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity, Alert, Animated, Dimensions } from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { planService } from '../../services/planService';
import { pantryService } from '../../services/pantryService';
import { GroceryItemCard } from '../../components/grocery/GroceryItemCard';
import { CategorySection } from '../../components/grocery/CategorySection';
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

export const GroceryListScreen: React.FC = () => {
  const route = useRoute();
  const navigation = useNavigation<any>();
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
        if (!cancelled) setError(e?.response?.data?.detail || 'Nie udało się pobrać listy produktów');
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    if (planId) void load();
    return () => {
      cancelled = true;
    };
  }, [planId]);

  const handleAddToShoppingList = () => {
    // Get all items that are not already in pantry
    const itemsToAdd = groceryList.items.filter((item: GroceryItem) => item.status !== 'already_have');
    
    if (itemsToAdd.length === 0) {
      Alert.alert('Info', 'Wszystkie produkty są już w spiżarni');
      return;
    }

    // Navigate to Zakupy tab with the planId
    navigation.navigate('Grocery', {
      screen: 'ShoppingList',
      params: { planId },
    });
  };

  const handleItemBought = async (item: GroceryItem) => {
    if (item.status === 'already_have') return;
    
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
        <Text style={styles.loadingText}>Generowanie listy produktów…</Text>
        {error ? <Text style={styles.errorText}>{error}</Text> : null}
      </View>
    );
  }

  const itemsToBuy = groceryList.items.filter((item: GroceryItem) => item.status !== 'already_have');

  const grouped: Record<string, GroceryItem[]> = {};
  for (const item of groceryList.items) {
    const key = item.category || 'other';
    grouped[key] = grouped[key] ? [...grouped[key], item] : [item];
  }

  // Sort items: needed (not already owned) first, then owned
  for (const key of Object.keys(grouped)) {
    grouped[key].sort((a, b) => {
      const aNeeded = a.status !== 'already_have';
      const bNeeded = b.status !== 'already_have';
      if (aNeeded && !bNeeded) return -1;
      if (!aNeeded && bNeeded) return 1;
      return 0;
    });
  }

  const categories = Object.keys(grouped).sort();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Potrzebne produkty</Text>
      <Text style={styles.subtitle}>
        Produkty: {groceryList.total_items} • Do kupienia: {itemsToBuy.length} • Odpady: {Math.round(groceryList.estimated_total_waste_g)}g
      </Text>

      {itemsToBuy.length > 0 && (
        <TouchableOpacity style={styles.addAllButton} onPress={handleAddToShoppingList}>
          <Text style={styles.addAllButtonText}>Dodaj do listy zakupów</Text>
        </TouchableOpacity>
      )}

      {categories.map((category) => (
        <CategorySection key={category} title={category}>
          {grouped[category].map((item) => {
            const isRemoving = removingItem?.item_id === item.item_id;
            if (isRemoving) {
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
              <GroceryItemCard 
                key={item.item_id} 
                item={item} 
                onPress={item.status !== 'already_have' ? () => handleItemBought(item) : undefined} 
              />
            );
          })}
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
});

