import React from 'react';
import {
  View,
  TextInput,
  TouchableOpacity,
  Text,
  ActivityIndicator,
  StyleSheet,
} from 'react-native';
import { colors, spacing, typography } from '../../../theme';

export interface PantryToolbarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  isSearching: boolean;
  onSave: () => void;
  isSaving: boolean;
}

export const PantryToolbar: React.FC<PantryToolbarProps> = ({
  searchQuery,
  onSearchChange,
  isSearching,
  onSave,
  isSaving,
}) => {
  return (
    <View style={styles.container}>
      <View style={styles.searchInputWrapper}>
        <TextInput
          style={styles.searchInput}
          placeholder="Wyszukaj produkt..."
          placeholderTextColor={colors.textTertiary}
          value={searchQuery}
          onChangeText={onSearchChange}
          returnKeyType="search"
        />
        {isSearching && <ActivityIndicator size="small" color={colors.primary} style={styles.searchLoader} />}
      </View>

      <TouchableOpacity
        style={[styles.saveButton, isSaving && styles.saveButtonDisabled]}
        onPress={onSave}
        disabled={isSaving}
        accessibilityRole="button"
      >
        {isSaving ? (
          <ActivityIndicator size="small" color={colors.white} />
        ) : (
          <Text style={styles.saveButtonText}>Zapisz</Text>
        )}
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.lg,
  },
  searchInputWrapper: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: spacing.borderRadius,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    marginRight: spacing.sm,
  },
  searchInput: {
    flex: 1,
    height: 40,
    fontSize: typography.fontSize.md,
    color: colors.textPrimary,
  },
  searchLoader: {
    marginLeft: spacing.sm,
  },
  saveButton: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.lg,
    backgroundColor: colors.primary,
    borderRadius: spacing.borderRadius,
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 100,
  },
  saveButtonDisabled: {
    opacity: 0.7,
  },
  saveButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
  },
});
