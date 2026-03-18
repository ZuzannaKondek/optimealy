import React from 'react';
import { ScrollView, View, Text, StyleSheet, Dimensions } from 'react-native';
import { colors, spacing, typography } from '../../theme';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

type Props<T> = {
  categories: string[];
  groupedItems: Record<string, T[]>;
  renderItem: (item: T) => React.ReactNode;
  translateCategory: (category: string) => string;
};

export const ColumnBoard = <T,>({
  categories,
  groupedItems,
  renderItem,
  translateCategory,
}: Props<T>) => {
  if (categories.length === 0) {
    return null;
  }

  const columnWidth = (SCREEN_WIDTH - spacing.md * 2 - spacing.md * (categories.length - 1)) / categories.length;

  return (
    <View style={styles.board}>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {categories.map((category) => {
          const items = groupedItems[category] ?? [];
          return (
            <View key={category} style={[styles.column, { width: columnWidth }]}>
              <Text style={styles.columnTitle}>{translateCategory(category)}</Text>
              <View style={styles.columnBody}>
                {items.length > 0 ? (
                  items.map((item) => renderItem(item))
                ) : (
                  <Text style={styles.emptyText}>Brak produktów</Text>
                )}
              </View>
            </View>
          );
        })}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  board: {
    marginTop: spacing.md,
  },
  scrollContent: {
    paddingBottom: spacing.sm,
  },
  column: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: spacing.borderRadius,
    padding: spacing.md,
    marginRight: spacing.md,
  },
  columnTitle: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  columnBody: {
    minHeight: 80,
  },
  emptyText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
});
