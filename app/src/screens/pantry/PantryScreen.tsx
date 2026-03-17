/**
 * Pantry Management Screen
 * OptiMeal Mobile App
 *
 * Screen for managing user's pantry items (ingredients they already have).
 * Helps reduce waste calculations by accounting for existing inventory.
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Keyboard,
} from 'react-native';
import { Screen } from '../../components/layout/Screen';
import { ScreenHeader } from '../../components/layout/ScreenHeader';
import { Section } from '../../components/layout/Section';
import { PantryToolbar } from '../../features/pantry/ui/PantryToolbar';
import { PantryCategoryBoard } from '../../features/pantry/ui/PantryCategoryBoard';
import { usePantry } from '../../hooks/usePantry';
import { useToast } from '../../hooks/useToast';
import { type ProductSearchResult } from '../../services/productService';
import { colors, spacing, typography } from '../../theme';
import { translateCategory } from '../../features/pantry/utils/translateCategory';

export const PantryScreen: React.FC = () => {
  const { items, staples, isLoading, error, fetchPantry, fetchStaples, updatePantry, searchProducts, deletePantryItem } = usePantry();
  const { showToast, ToastContainer } = useToast();
  
  // Track quantities per product ID with product details
  const [quantities, setQuantities] = useState<Map<string, { quantity: number; expiryDate?: string; productName?: string; category?: string }>>(new Map());
  // Track which items exist in backend (for delete functionality)
  const [existingItemIds, setExistingItemIds] = useState<Set<string>>(new Set());
  const [isSaving, setIsSaving] = useState(false);

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<ProductSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);
  
  // Focus mode: when a product is added from search, show only that product
  const [focusedProductId, setFocusedProductId] = useState<string | null>(null);

  // Load pantry and staples on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        await Promise.all([fetchPantry(), fetchStaples()]);
      } catch (err) {
        console.error('Failed to load pantry data:', err);
      }
    };
    loadData();
  }, [fetchPantry, fetchStaples]);

  // Update quantities map when items load (sync from backend with product details)
  useEffect(() => {
    const newQuantities = new Map<string, { quantity: number; expiryDate?: string; productName?: string; category?: string }>();
    const newExistingIds = new Set<string>();
    items.forEach((item) => {
      newQuantities.set(item.product_id, { 
        quantity: item.quantity_g, 
        expiryDate: item.expiry_date,
        productName: item.product_name,
        category: item.category,
      });
      newExistingIds.add(item.product_id);
    });
    setQuantities(newQuantities);
    setExistingItemIds(newExistingIds);
  }, [items]);

  // Debounced search
  useEffect(() => {
    if (!searchQuery || searchQuery.trim().length < 2) {
      setSearchResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const results = await searchProducts(searchQuery);
        setSearchResults(results);
        setShowSearchResults(true);
      } catch (err) {
        console.error('Search failed:', err);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery, searchProducts]);

  const toggleItem = (productId: string, defaultQuantity: number, productName?: string, category?: string) => {
    setQuantities((prev) => {
      const newMap = new Map(prev);
      if (newMap.has(productId)) {
        newMap.delete(productId);
      } else {
        newMap.set(productId, { quantity: defaultQuantity, productName, category });
      }
      return newMap;
    });
  };

  const updateQuantity = (productId: string, quantity: number) => {
    setQuantities((prev) => {
      const newMap = new Map(prev);
      const existing = newMap.get(productId);
      if (quantity > 0) {
        newMap.set(productId, { quantity, expiryDate: existing?.expiryDate, productName: existing?.productName, category: existing?.category });
      } else {
        newMap.delete(productId);
      }
      return newMap;
    });
  };

  const updateExpiryDate = (productId: string, expiryDate: string) => {
    setQuantities((prev) => {
      const newMap = new Map(prev);
      const existing = newMap.get(productId);
      if (existing) {
        newMap.set(productId, { ...existing, expiryDate: expiryDate || undefined });
      }
      return newMap;
    });
  };

  const handleDeleteItem = (productId: string, isExisting: boolean) => {
    if (isExisting) {
      deletePantryItem(productId);
      return;
    }

    setQuantities((prev) => {
      const newMap = new Map(prev);
      newMap.delete(productId);
      return newMap;
    });
  };

  const addSearchedProduct = (product: ProductSearchResult) => {
    setQuantities((prev) => {
      const newMap = new Map(prev);
      if (!newMap.has(product.product_id)) {
        // Store product details along with quantity
        newMap.set(product.product_id, { quantity: 500, productName: product.product_name, category: product.category });
      }
      return newMap;
    });
    // Focus on this product so user can edit it
    setFocusedProductId(product.product_id);
    setSearchQuery('');
    setSearchResults([]);
    setShowSearchResults(false);
    Keyboard.dismiss();
  };

  const handleSave = async () => {
    setIsSaving(true);
    
    try {
      // Only save items with positive quantity
      const itemsArray = Array.from(quantities.entries())
        .filter(([_, data]) => data.quantity > 0)
        .map(([product_id, data]) => ({
          product_id,
          quantity_g: data.quantity,
          expiry_date: data.expiryDate || undefined,
        }));
      
      console.log('Saving pantry:', JSON.stringify({ items: itemsArray }));
      await updatePantry(itemsArray);
      showToast('Zapisano zmiany', 'success');
    } catch (err: any) {
      console.error('Pantry save error:', err?.response?.data || err.message);
      const errorDetail = err?.response?.data?.detail;
      const errorMessage = errorDetail 
        ? (typeof errorDetail === 'string' ? errorDetail : JSON.stringify(errorDetail))
        : err?.message || 'Nie udało się zaktualizować spiżarni';
      Alert.alert('Błąd', errorMessage);
      showToast('Błąd zapisu', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading && staples.length === 0) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Ładowanie spiżarni...</Text>
      </View>
    );
  }

  if (error && staples.length === 0) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>Błąd: {error}</Text>
      </View>
    );
  }

  // Category to icon mapping
  const getCategoryIcon = (category?: string): string => {
    const iconMap: Record<string, string> = {
      oil: '🫒',
      condiment: '🧂',
      spice: '🌶️',
      herb: '🌿',
      grain: '🌾',
      dairy: '🥛',
      protein: '🥚',
      vegetable: '🥕',
      fruit: '🍎',
      meat: '🥩',
      fish: '🐟',
      beverage: '🥤',
      other: '🥫',
    };
    return iconMap[category || 'other'] || '🥫';
  };

  // Get products that are in the pantry (either from staples or stored product details)
  // If focusedProductId is set, show only that product
  const allPantryProducts = [
    ...staples.filter(s => quantities.has(s.product_id)).map(s => ({
      product_id: s.product_id,
      product_name: s.product_name,
      category: s.category,
      icon: s.icon,
      isStaple: true,
    })),
    ...Array.from(quantities.entries())
      .filter(([id]) => !staples.find(s => s.product_id === id))
      .map(([product_id, data]) => ({
        product_id,
        product_name: data.productName || 'Nieznany',
        category: data.category || 'other',
        icon: getCategoryIcon(data.category),
        isStaple: false,
      }))
  ];
  
  // Filter to show only focused product, or all if no focus
  const pantryProducts = focusedProductId 
    ? allPantryProducts.filter(p => p.product_id === focusedProductId)
    : allPantryProducts;

  // Group products by category
  const groupedByCategory: Record<string, typeof pantryProducts> = {};
  for (const product of pantryProducts) {
    const cat = product.category || 'other';
    if (!groupedByCategory[cat]) groupedByCategory[cat] = [];
    groupedByCategory[cat].push(product);
  }
  const categories = Object.keys(groupedByCategory).sort();

  return (
    <Screen scroll>
      <ToastContainer />
      <ScreenHeader
        title="Spiżarnia"
        subtitle="Dodaj produkty, które masz w domu. To pomoże zmniejszyć marnotrawstwo i koszty zakupów."
      />

      <PantryToolbar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        isSearching={isSearching}
        onSave={handleSave}
        isSaving={isSaving}
      />

      {showSearchResults && searchResults.length > 0 && (
        <View style={styles.searchResultsContainer}>
          {searchResults.map((product) => (
            <TouchableOpacity
              key={product.product_id}
              style={styles.searchResultItem}
              onPress={() => addSearchedProduct(product)}
            >
              <Text style={styles.searchResultName}>{product.product_name}</Text>
              <Text style={styles.searchResultCategory}>{translateCategory(product.category)}</Text>
            </TouchableOpacity>
          ))}
        </View>
      )}

      {focusedProductId && (
        <TouchableOpacity
          style={styles.exitFocusButton}
          onPress={() => setFocusedProductId(null)}
        >
          <Text style={styles.exitFocusText}>Pokaż wszystkie produkty</Text>
        </TouchableOpacity>
      )}

      <View style={styles.counterContainer}>
        <Text style={styles.counterText}>{quantities.size} produktów w spiżarni</Text>
      </View>

      {pantryProducts.length > 0 ? (
        <PantryCategoryBoard
          categories={categories}
          groupedProducts={groupedByCategory}
          quantities={quantities}
          existingItemIds={existingItemIds}
          onToggle={toggleItem}
          onDelete={handleDeleteItem}
          onQuantityChange={updateQuantity}
          onExpiryDateChange={updateExpiryDate}
        />
      ) : (
        <View style={styles.emptyState}>
          <Text style={styles.emptyIcon}>🛒</Text>
          <Text style={styles.emptyText}>
            Wyszukaj produkty powyżej, aby dodać je do spiżarni
          </Text>
        </View>
      )}

      {staples.length > 0 && (
        <Section title="Szybkie dodawanie z produktów podstawowych">
          <View style={styles.staplesGrid}>
            {staples.map((staple) => (
              <TouchableOpacity
                key={staple.product_id}
                style={[
                  styles.stapleChip,
                  quantities.has(staple.product_id) && styles.stapleChipSelected,
                ]}
                onPress={() => toggleItem(staple.product_id, staple.default_quantity_g, staple.product_name, staple.category)}
              >
                <Text style={styles.stapleIcon}>{staple.icon}</Text>
                <Text
                  style={[
                    styles.stapleName,
                    quantities.has(staple.product_id) && styles.stapleNameSelected,
                  ]}
                  numberOfLines={1}
                >
                  {staple.product_name}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </Section>
      )}
    </Screen>
  );
};

const styles = StyleSheet.create({
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
  },
  errorText: {
    fontSize: typography.fontSize.md,
    color: colors.error,
    textAlign: 'center',
    paddingHorizontal: spacing.lg,
  },
  searchResultsContainer: {
    backgroundColor: colors.surface,
    borderRadius: spacing.borderRadius,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: spacing.md,
    maxHeight: 200,
  },
  searchResultItem: {
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  searchResultName: {
    fontSize: typography.fontSize.md,
    color: colors.textPrimary,
    fontWeight: typography.fontWeight.medium,
  },
  searchResultCategory: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  exitFocusButton: {
    backgroundColor: colors.secondary + '20',
    padding: spacing.md,
    borderRadius: spacing.borderRadius,
    marginBottom: spacing.md,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.secondary,
  },
  exitFocusText: {
    color: colors.secondary,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.medium,
  },
  counterContainer: {
    backgroundColor: colors.primary + '15',
    padding: spacing.md,
    borderRadius: spacing.borderRadius,
    marginBottom: spacing.lg,
    alignItems: 'center',
  },
  counterText: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.primary,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: spacing.xl,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: spacing.md,
  },
  emptyText: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  staplesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  stapleChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 20,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    marginRight: spacing.sm,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  stapleChipSelected: {
    backgroundColor: colors.primary + '20',
    borderColor: colors.primary,
  },
  stapleIcon: {
    fontSize: 16,
    marginRight: spacing.xs,
  },
  stapleName: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  stapleNameSelected: {
    color: colors.primary,
    fontWeight: typography.fontWeight.medium,
  },
});
