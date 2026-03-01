import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import type { GroceryItem } from '../../types/models';
import { colors, spacing, typography } from '../../theme';

type Props = {
  item: GroceryItem;
};

export const GroceryItemCard: React.FC<Props> = ({ item }) => {
  const statusLabel = item.status === 'already_have' ? 'Already have' : item.status === 'purchased' ? 'Purchased' : 'Needed';

  const recipes = item.used_in_recipes ?? [];
  const recipePreview = recipes.slice(0, 2).map((r) => r.recipe_name).join(', ');
  const moreCount = recipes.length > 2 ? recipes.length - 2 : 0;

  return (
    <View style={styles.card}>
      <View style={styles.headerRow}>
        <Text style={styles.title}>{item.product_name}</Text>
        <Text style={styles.status}>{statusLabel}</Text>
      </View>

      <Text style={styles.meta}>
        Buy: {Math.round(item.purchase_quantity_g)} {item.purchase_unit} • Need:{' '}
        {Math.round(item.required_quantity_g)}g
      </Text>

      <View style={styles.footerRow}>
        <Text style={styles.footerText}>
          Waste: {Math.round(item.estimated_item_waste_g)}g
        </Text>
        <Text style={styles.footerText}>
          {item.estimated_item_cost != null ? `$${Number(item.estimated_item_cost).toFixed(2)}` : 'Cost: —'}
        </Text>
      </View>

      {recipes.length > 0 ? (
        <Text style={styles.usedIn}>
          Used in: {recipePreview}
          {moreCount ? ` +${moreCount} more` : ''}
        </Text>
      ) : null}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: spacing.borderRadius,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'baseline',
    gap: spacing.sm,
    marginBottom: spacing.xs,
  },
  title: {
    flex: 1,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
  },
  status: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  meta: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  footerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: spacing.sm,
  },
  footerText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  usedIn: {
    marginTop: spacing.sm,
    fontSize: typography.fontSize.sm,
    color: colors.textTertiary,
  },
});

