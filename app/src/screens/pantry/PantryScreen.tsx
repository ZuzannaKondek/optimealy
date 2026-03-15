/**
 * Pantry Management Screen
 * OptiMeal Mobile App
 *
 * Screen for managing user's pantry items (ingredients they already have).
 * Helps reduce waste calculations by accounting for existing inventory.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  FlatList,
  Keyboard,
} from 'react-native';
import { usePantry, type PantryStaple } from '../../hooks/usePantry';
import { productService, type ProductSearchResult } from '../../services/productService';
import { colors, spacing, typography } from '../../theme';

export const PantryScreen: React.FC = () => {
  const { items, staples, isLoading, error, fetchPantry, fetchStaples, updatePantry, searchProducts } = usePantry();
  
  // Track quantities per product ID with product details
  const [quantities, setQuantities] = useState<Map<string, { quantity: number; expiryDate?: string; productName?: string; category?: string }>>(new Map());
  const [isSaving, setIsSaving] = useState(false);

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<ProductSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);

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
    items.forEach((item) => {
      newQuantities.set(item.product_id, { 
        quantity: item.quantity_g, 
        expiryDate: item.expiry_date,
        productName: item.product_name,
        category: item.category,
      });
    });
    setQuantities(newQuantities);
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

  const addSearchedProduct = (product: ProductSearchResult) => {
    setQuantities((prev) => {
      const newMap = new Map(prev);
      if (!newMap.has(product.product_id)) {
        // Store product details along with quantity
        newMap.set(product.product_id, { quantity: 500, productName: product.product_name, category: product.category });
      }
      return newMap;
    });
    setSearchQuery('');
    setSearchResults([]);
    setShowSearchResults(false);
    Keyboard.dismiss();
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const itemsArray = Array.from(quantities.entries()).map(([product_id, data]) => ({
        product_id,
        quantity_g: data.quantity,
        expiry_date: data.expiryDate,
      }));
      
      await updatePantry(itemsArray);
      Alert.alert('Sukces', 'Spiżarnia zaktualizowana pomyślnie!');
    } catch (err: any) {
      Alert.alert('Błąd', err.message || 'Nie udało się zaktualizować spiżarni');
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
  const pantryProducts = [
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

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        <Text style={styles.title}>Moja spiżarnia</Text>
        <Text style={styles.subtitle}>
          Dodaj produkty, które masz w domu. To pomoże zmniejszyć marnotrawstwo i koszty zakupów.
        </Text>

        {/* Search Bar */}
        <View style={styles.searchContainer}>
          <TextInput
            style={styles.searchInput}
            placeholder="Wyszukaj produkt..."
            placeholderTextColor={colors.textTertiary}
            value={searchQuery}
            onChangeText={setSearchQuery}
            onFocus={() => searchResults.length > 0 && setShowSearchResults(true)}
          />
          {isSearching && <ActivityIndicator size="small" color={colors.primary} style={styles.searchLoader} />}
        </View>

        {/* Search Results Dropdown */}
        {showSearchResults && searchResults.length > 0 && (
          <View style={styles.searchResultsContainer}>
            {searchResults.map((product) => (
              <TouchableOpacity
                key={product.product_id}
                style={styles.searchResultItem}
                onPress={() => addSearchedProduct(product)}
              >
                <Text style={styles.searchResultName}>{product.product_name}</Text>
                <Text style={styles.searchResultCategory}>{product.category}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}

        <View style={styles.counterContainer}>
          <Text style={styles.counterText}>
            {quantities.size} produktów w spiżarni
          </Text>
        </View>

        {/* Pantry Items */}
        {pantryProducts.length > 0 ? (
          <View style={styles.itemsList}>
            {pantryProducts.map((product) => (
              <PantryItemCard
                key={product.product_id}
                productId={product.product_id}
                productName={product.product_name}
                category={product.category}
                icon={product.icon}
                quantity={quantities.get(product.product_id)?.quantity}
                expiryDate={quantities.get(product.product_id)?.expiryDate}
                onToggle={() => toggleItem(product.product_id, 500, product.product_name, product.category)}
                onQuantityChange={(qty) => updateQuantity(product.product_id, qty)}
                onExpiryDateChange={(date) => updateExpiryDate(product.product_id, date)}
              />
            ))}
          </View>
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyIcon}>🛒</Text>
            <Text style={styles.emptyText}>
              Wyszukaj produkty powyżej, aby dodać je do spiżarni
            </Text>
          </View>
        )}

        {/* Quick Add Section - Available Staples */}
        {staples.length > 0 && (
          <View style={styles.staplesSection}>
            <Text style={styles.sectionTitle}>Szybkie dodawanie z produktów podstawowych</Text>
            <View style={styles.staplesGrid}>
              {staples.map((staple) => (
                <TouchableOpacity
                  key={staple.product_id}
                  style={[
                    styles.stapleChip,
                    quantities.has(staple.product_id) && styles.stapleChipSelected
                  ]}
                  onPress={() => toggleItem(staple.product_id, staple.default_quantity_g, staple.product_name, staple.category)}
                >
                  <Text style={styles.stapleIcon}>{staple.icon}</Text>
                  <Text 
                    style={[
                      styles.stapleName,
                      quantities.has(staple.product_id) && styles.stapleNameSelected
                    ]}
                    numberOfLines={1}
                  >
                    {staple.product_name}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}
      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity
          style={[styles.saveButton, isSaving && styles.saveButtonDisabled]}
          onPress={handleSave}
          disabled={isSaving}
        >
          {isSaving ? (
            <ActivityIndicator color={colors.white} />
          ) : (
            <Text style={styles.saveButtonText}>Zapisz zmiany</Text>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
};

interface PantryItemCardProps {
  productId: string;
  productName: string;
  category: string;
  icon: string;
  quantity: number | undefined;
  expiryDate: string | undefined;
  onToggle: () => void;
  onQuantityChange: (quantity: number) => void;
  onExpiryDateChange: (date: string) => void;
}

const PantryItemCard: React.FC<PantryItemCardProps> = ({ 
  productName,
  category,
  icon,
  quantity,
  expiryDate,
  onToggle, 
  onQuantityChange,
  onExpiryDateChange 
}) => {
  const [isEditingQty, setIsEditingQty] = useState(false);
  const [tempQty, setTempQty] = useState('');
  const [isEditingExpiry, setIsEditingExpiry] = useState(false);
  const [tempExpiry, setTempExpiry] = useState('');
  const isSelected = quantity !== undefined && quantity > 0;

  const handleQtyPress = () => {
    if (isSelected) {
      setTempQty(quantity?.toString() || '');
      setIsEditingQty(true);
    }
  };

  const handleQtySubmit = () => {
    const newQty = parseFloat(tempQty);
    if (!isNaN(newQty) && newQty > 0) {
      onQuantityChange(newQty);
    }
    setIsEditingQty(false);
  };

  const handleExpiryPress = () => {
    if (isSelected) {
      setTempExpiry(expiryDate || '');
      setIsEditingExpiry(true);
    }
  };

  const handleExpirySubmit = () => {
    // Validate date format (YYYY-MM-DD)
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (dateRegex.test(tempExpiry)) {
      onExpiryDateChange(tempExpiry);
    } else if (tempExpiry === '') {
      onExpiryDateChange('');
    }
    setIsEditingExpiry(false);
  };

  return (
    <View style={[styles.itemCard, isSelected && styles.itemCardSelected]}>
      <View style={styles.itemHeader}>
        <Text style={styles.itemIcon}>{icon}</Text>
        <View style={styles.itemInfo}>
          <Text style={styles.itemName} numberOfLines={1}>{productName}</Text>
          <Text style={styles.itemCategory}>{category}</Text>
        </View>
        <TouchableOpacity onPress={onToggle} style={styles.removeButton}>
          <Text style={styles.removeButtonText}>×</Text>
        </TouchableOpacity>
      </View>

      {isSelected && (
        <View style={styles.itemDetails}>
          <View style={styles.quantityRow}>
            <Text style={styles.detailLabel}>Ilość:</Text>
            {isEditingQty ? (
              <TextInput
                style={styles.detailInput}
                value={tempQty}
                onChangeText={setTempQty}
                onBlur={handleQtySubmit}
                onSubmitEditing={handleQtySubmit}
                keyboardType="numeric"
                autoFocus
                selectTextOnFocus
              />
            ) : (
              <TouchableOpacity onPress={handleQtyPress}>
                <Text style={styles.detailValue}>{Math.round(quantity || 0)}g</Text>
              </TouchableOpacity>
            )}
          </View>

          <View style={styles.expiryRow}>
            <Text style={styles.detailLabel}>Data przydatności:</Text>
            {isEditingExpiry ? (
              <TextInput
                style={styles.detailInput}
                value={tempExpiry}
                onChangeText={setTempExpiry}
                onBlur={handleExpirySubmit}
                onSubmitEditing={handleExpirySubmit}
                placeholder="RRRR-MM-DD"
                placeholderTextColor={colors.textTertiary}
              />
            ) : (
              <TouchableOpacity onPress={handleExpiryPress}>
                <Text style={[styles.detailValue, !expiryDate && styles.detailPlaceholder]}>
                  {expiryDate || 'Dodaj datę'}
                </Text>
              </TouchableOpacity>
            )}
          </View>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: spacing.screenPadding,
    paddingBottom: spacing.xl,
  },
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
  title: {
    fontSize: typography.fontSize.xxxl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: spacing.borderRadius,
    paddingHorizontal: spacing.md,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  searchInput: {
    flex: 1,
    height: 44,
    fontSize: typography.fontSize.md,
    color: colors.textPrimary,
  },
  searchLoader: {
    marginLeft: spacing.sm,
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
  itemsList: {
    marginBottom: spacing.lg,
  },
  itemCard: {
    backgroundColor: colors.surface,
    borderRadius: spacing.borderRadius,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderWidth: 2,
    borderColor: colors.border,
  },
  itemCardSelected: {
    borderColor: colors.primary,
  },
  itemHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  itemIcon: {
    fontSize: 28,
    marginRight: spacing.sm,
  },
  itemInfo: {
    flex: 1,
  },
  itemName: {
    fontSize: typography.fontSize.md,
    color: colors.textPrimary,
    fontWeight: typography.fontWeight.semiBold,
  },
  itemCategory: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    textTransform: 'capitalize',
  },
  removeButton: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.error + '20',
    justifyContent: 'center',
    alignItems: 'center',
  },
  removeButtonText: {
    fontSize: 20,
    color: colors.error,
    fontWeight: typography.fontWeight.bold,
  },
  itemDetails: {
    marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  quantityRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  expiryRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  detailLabel: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    width: 60,
  },
  detailValue: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontWeight: typography.fontWeight.semiBold,
  },
  detailPlaceholder: {
    color: colors.textTertiary,
    fontStyle: 'italic',
  },
  detailInput: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontWeight: typography.fontWeight.semiBold,
    borderBottomWidth: 1,
    borderBottomColor: colors.primary,
    paddingVertical: 2,
    minWidth: 80,
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
  staplesSection: {
    marginTop: spacing.md,
  },
  sectionTitle: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
    marginBottom: spacing.md,
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
  footer: {
    padding: spacing.screenPadding,
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  saveButton: {
    backgroundColor: colors.primary,
    borderRadius: spacing.borderRadius,
    padding: spacing.md,
    alignItems: 'center',
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
  },
});
