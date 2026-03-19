import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  TextInput,
} from 'react-native';
import { colors, spacing, typography } from '../../../theme';
import { translateCategory } from '../utils/translateCategory';

type PantryProduct = {
  product_id: string;
  product_name: string;
  category: string;
  icon: string;
  isStaple: boolean;
};

interface QuantityDetails {
  quantity: number;
  expiryDate?: string;
  productName?: string;
  category?: string;
}

export interface PantryCategoryBoardProps {
  categories: string[];
  groupedProducts: Record<string, PantryProduct[]>;
  quantities: Map<string, QuantityDetails>;
  existingItemIds: Set<string>;
  onToggle: (productId: string, defaultQuantity: number, productName?: string, category?: string) => void;
  onDelete: (productId: string, isExisting: boolean) => void;
  onQuantityChange: (productId: string, quantity: number) => void;
  onExpiryDateChange: (productId: string, date: string) => void;
}

export const PantryCategoryBoard: React.FC<PantryCategoryBoardProps> = ({
  categories,
  groupedProducts,
  quantities,
  existingItemIds,
  onToggle,
  onDelete,
  onQuantityChange,
  onExpiryDateChange,
}) => {
  if (!categories.length) {
    return null;
  }

  return (
    <View style={styles.boardContainer}>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {categories.map((category) => {
          const products = groupedProducts[category] || [];
          if (!products.length) return null;
          return (
            <View key={category} style={styles.column}>
              <Text style={styles.columnTitle}>{translateCategory(category)}</Text>
              {products.map((product) => {
                const details = quantities.get(product.product_id);
                const isExistingItem = existingItemIds.has(product.product_id);
                const handleDelete = () => {
                  if (isExistingItem) {
                    onDelete(product.product_id, true);
                  } else {
                    onToggle(product.product_id, 500, product.product_name, product.category);
                  }
                };

                return (
                  <PantryItemCard
                    key={product.product_id}
                    productId={product.product_id}
                    productName={product.product_name}
                    category={product.category}
                    icon={product.icon}
                    quantity={details?.quantity}
                    expiryDate={details?.expiryDate}
                    onDelete={handleDelete}
                    onQuantityChange={(qty) => onQuantityChange(product.product_id, qty)}
                    onExpiryDateChange={(date) => onExpiryDateChange(product.product_id, date)}
                  />
                );
              })}
            </View>
          );
        })}
      </ScrollView>
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
  onDelete: () => void;
  onQuantityChange: (quantity: number) => void;
  onExpiryDateChange: (date: string) => void;
}

const PantryItemCard: React.FC<PantryItemCardProps> = ({
  productName,
  category,
  icon,
  quantity,
  expiryDate,
  onDelete,
  onQuantityChange,
  onExpiryDateChange,
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
          <Text style={styles.itemCategory}>{translateCategory(category)}</Text>
        </View>
        <TouchableOpacity onPress={onDelete} style={styles.removeButton}>
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
  boardContainer: {
    marginBottom: spacing.lg,
  },
  scrollContent: {
    paddingVertical: spacing.sm,
  },
  column: {
    minWidth: 180,
    marginRight: spacing.md,
    padding: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: spacing.borderRadius,
    borderWidth: 1,
    borderColor: colors.border,
  },
  columnTitle: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
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
});
