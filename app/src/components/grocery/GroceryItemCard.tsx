import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import type { GroceryItem } from '../../types/models';
import { colors, spacing, typography } from '../../theme';

type Props = {
  item: GroceryItem;
};

export const GroceryItemCard: React.FC<Props> = ({ item }) => {
  const isAlreadyOwned = item.status === 'already_have';
  const statusLabel = isAlreadyOwned ? 'Mam' : item.status === 'purchased' ? 'Kupione' : 'Potrzebne';

  const recipes = item.used_in_recipes ?? [];
  const recipePreview = recipes.slice(0, 2).map((r) => r.recipe_name).join(', ');
  const moreCount = recipes.length > 2 ? recipes.length - 2 : 0;

  const showExactBadge = item.exact_quantity === true;
  const waste = Math.round(item.estimated_item_waste_g);
  const toBuy = Math.max(0, item.purchase_quantity_g - item.estimated_item_waste_g);
  const owned = Math.max(0, Math.round(item.required_quantity_g - toBuy));

  return (
    <View style={[styles.card, isAlreadyOwned && styles.cardOwned]}>
      <View style={styles.headerRow}>
        {isAlreadyOwned && (
          <View style={styles.checkmark}>
            <Text style={styles.checkmarkText}>✓</Text>
          </View>
        )}
        <Text style={[styles.title, isAlreadyOwned && styles.titleOwned]}>{item.product_name}</Text>
        <Text style={[styles.status, isAlreadyOwned && styles.statusOwned]}>{statusLabel}</Text>
      </View>

      <Text style={styles.meta}>
        Kup: {Math.round(item.purchase_quantity_g)} {item.purchase_unit} • Łączne zapotrzebowanie:{' '}
        {Math.round(item.required_quantity_g)}g
        {owned > 0 && <Text style={styles.ownedHint}> • W spiżarni: {owned}g</Text>}
        {showExactBadge && <Text style={styles.exactBadge}> • Dokładna waga</Text>}
      </Text>

      <View style={styles.footerRow}>
        {waste > 0 ? (
          <Text style={styles.wasteText}>Odpady: {waste}g</Text>
        ) : (
          <Text style={styles.noWasteText}>Bez odpadów</Text>
        )}
      </View>

      {recipes.length > 0 ? (
        <Text style={styles.usedIn}>
          Użyte w: {recipePreview}
          {moreCount ? ` +${moreCount} więcej` : ''}
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
  cardOwned: {
    backgroundColor: '#f0fff4',
    borderColor: colors.success,
    borderWidth: 2,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'baseline',
    gap: spacing.sm,
    marginBottom: spacing.xs,
  },
  checkmark: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.success,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.xs,
  },
  checkmarkText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: typography.fontWeight.bold,
  },
  title: {
    flex: 1,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
  },
  titleOwned: {
    color: colors.success,
  },
  status: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  statusOwned: {
    color: colors.success,
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
  wasteText: {
    fontSize: typography.fontSize.sm,
    color: colors.error,
  },
  noWasteText: {
    fontSize: typography.fontSize.sm,
    color: colors.success,
  },
  exactBadge: {
    fontSize: typography.fontSize.xs,
    color: colors.primary,
    fontWeight: typography.fontWeight.semiBold,
  },
  ownedHint: {
    fontSize: typography.fontSize.xs,
    color: colors.textTertiary,
  },
  usedIn: {
    marginTop: spacing.sm,
    fontSize: typography.fontSize.sm,
    color: colors.textTertiary,
  },
});
