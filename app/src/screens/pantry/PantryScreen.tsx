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
  ScrollView,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { usePantry, type PantryStaple } from '../../hooks/usePantry';
import { colors, spacing, typography } from '../../theme';

export const PantryScreen: React.FC = () => {
  const { items, staples, isLoading, error, fetchPantry, fetchStaples, updatePantry } = usePantry();
  
  // Track quantities per product ID
  const [quantities, setQuantities] = useState<Map<string, number>>(new Map());
  const [isSaving, setIsSaving] = useState(false);

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

  // Update quantities map when items load
  useEffect(() => {
    const newQuantities = new Map<string, number>();
    items.forEach((item) => {
      newQuantities.set(item.product_id, item.quantity_g);
    });
    setQuantities(newQuantities);
  }, [items]);

  const toggleItem = (productId: string, defaultQuantity: number) => {
    setQuantities((prev) => {
      const newMap = new Map(prev);
      if (newMap.has(productId)) {
        newMap.delete(productId);
      } else {
        newMap.set(productId, defaultQuantity);
      }
      return newMap;
    });
  };

  const updateQuantity = (productId: string, quantity: number) => {
    setQuantities((prev) => {
      const newMap = new Map(prev);
      if (quantity > 0) {
        newMap.set(productId, quantity);
      } else {
        newMap.delete(productId);
      }
      return newMap;
    });
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const itemsArray = Array.from(quantities.entries()).map(([product_id, quantity_g]) => ({
        product_id,
        quantity_g,
      }));
      
      await updatePantry(itemsArray);
      Alert.alert('Success', 'Pantry updated successfully!');
    } catch (err: any) {
      Alert.alert('Error', err.message || 'Failed to update pantry');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading && staples.length === 0) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading pantry...</Text>
      </View>
    );
  }

  if (error && staples.length === 0) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>Error: {error}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        <Text style={styles.title}>My Pantry</Text>
        <Text style={styles.subtitle}>
          Select items you currently have. This helps reduce waste calculations.
        </Text>

        <View style={styles.counterContainer}>
          <Text style={styles.counterText}>
            {quantities.size} items in pantry
          </Text>
        </View>

        <View style={styles.grid}>
          {staples.map((staple) => (
            <PantryItemCard
              key={staple.product_id}
              staple={staple}
              quantity={quantities.get(staple.product_id)}
              onToggle={() => toggleItem(staple.product_id, staple.default_quantity_g)}
              onQuantityChange={(qty) => updateQuantity(staple.product_id, qty)}
            />
          ))}
        </View>
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
            <Text style={styles.saveButtonText}>Save Changes</Text>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
};

interface PantryItemCardProps {
  staple: PantryStaple;
  quantity: number | undefined;
  onToggle: () => void;
  onQuantityChange: (quantity: number) => void;
}

const PantryItemCard: React.FC<PantryItemCardProps> = ({ 
  staple, 
  quantity, 
  onToggle, 
  onQuantityChange 
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [tempValue, setTempValue] = useState('');
  const isSelected = quantity !== undefined && quantity > 0;

  const handleQuantityPress = () => {
    if (isSelected) {
      setTempValue(quantity?.toString() || '');
      setIsEditing(true);
    }
  };

  const handleQuantitySubmit = () => {
    const newQty = parseFloat(tempValue);
    if (!isNaN(newQty) && newQty > 0) {
      onQuantityChange(newQty);
    }
    setIsEditing(false);
  };

  return (
    <TouchableOpacity
      style={[styles.card, isSelected && styles.cardSelected]}
      onPress={isEditing ? undefined : onToggle}
      activeOpacity={0.7}
    >
      <Text style={styles.icon}>{staple.icon}</Text>
      <Text style={[styles.productName, isSelected && styles.productNameSelected]} numberOfLines={1}>
        {staple.product_name}
      </Text>
      
      {isSelected ? (
        <>
          {isEditing ? (
            <TextInput
              style={styles.quantityInput}
              value={tempValue}
              onChangeText={setTempValue}
              onBlur={handleQuantitySubmit}
              onSubmitEditing={handleQuantitySubmit}
              keyboardType="numeric"
              autoFocus
              selectTextOnFocus
            />
          ) : (
            <TouchableOpacity onPress={handleQuantityPress}>
              <Text style={styles.quantityText}>{Math.round(quantity || 0)}g</Text>
            </TouchableOpacity>
          )}
          <TouchableOpacity 
            style={styles.checkmarkContainer}
            onPress={(e) => {
              e.stopPropagation();
              onToggle();
            }}
          >
            <Text style={styles.checkmark}>✓</Text>
          </TouchableOpacity>
        </>
      ) : (
        <Text style={styles.addText}>Add</Text>
      )}
    </TouchableOpacity>
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
  counterContainer: {
    backgroundColor: colors.surface,
    padding: spacing.md,
    borderRadius: spacing.borderRadius,
    marginBottom: spacing.lg,
    alignItems: 'center',
  },
  counterText: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.medium,
    color: colors.primary,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: spacing.xl,
  },
  card: {
    width: '48%',
    backgroundColor: colors.surface,
    borderRadius: spacing.borderRadius,
    padding: spacing.md,
    marginBottom: spacing.md,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: colors.border,
    minHeight: 100,
    justifyContent: 'center',
  },
  cardSelected: {
    borderColor: colors.primary,
    backgroundColor: `${colors.primary}10`,
  },
  icon: {
    fontSize: 32,
    marginBottom: spacing.xs,
  },
  productName: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    textAlign: 'center',
    fontWeight: typography.fontWeight.medium,
  },
  productNameSelected: {
    color: colors.textPrimary,
    fontWeight: typography.fontWeight.semiBold,
  },
  checkmarkContainer: {
    position: 'absolute',
    top: spacing.xs,
    right: spacing.xs,
    backgroundColor: colors.primary,
    borderRadius: 12,
    width: 24,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkmark: {
    color: colors.white,
    fontSize: 16,
    fontWeight: typography.fontWeight.bold,
  },
  quantityText: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontWeight: typography.fontWeight.semiBold,
    marginTop: spacing.xs,
    textAlign: 'center',
  },
  quantityInput: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontWeight: typography.fontWeight.semiBold,
    marginTop: spacing.xs,
    textAlign: 'center',
    borderBottomWidth: 1,
    borderBottomColor: colors.primary,
    paddingVertical: 2,
    minWidth: 50,
  },
  addText: {
    fontSize: typography.fontSize.xs,
    color: colors.textTertiary,
    marginTop: spacing.xs,
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
