/**
 * Plan Creation Loading Modal
 * Shown while the optimizer is creating a meal plan.
 * Prevents user confusion by clearly indicating the process is in progress.
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  ActivityIndicator,
} from 'react-native';
import { colors, spacing, typography } from '../../theme';

export interface PlanCreationLoadingModalProps {
  visible: boolean;
  planName?: string;
}

export const PlanCreationLoadingModal: React.FC<PlanCreationLoadingModalProps> = ({
  visible,
  planName,
}) => {
  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      // Prevent dismissing by hardware back button
      onRequestClose={() => {}}
    >
      <View style={styles.overlay}>
        <View style={styles.card}>
          <ActivityIndicator size="large" color={colors.primary} />
          
          <Text style={styles.title}>Tworzenie planu posiłków</Text>
          
          <Text style={styles.message}>
            {planName 
              ? `Optymalizacja planu "${planName}"...`
              : 'Optymalizacja planu posiłków...'
            }
          </Text>
          
          <Text style={styles.hint}>
            To może chwilę potrwać. Algorytm dobiera najlepsze przepisy, 
            aby zminimalizować marnotrawstwo żywności.
          </Text>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: colors.overlay,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.lg,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: spacing.borderRadius * 1.5,
    padding: spacing.xl,
    maxWidth: 340,
    width: '100%',
    alignItems: 'center',
  },
  title: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginTop: spacing.lg,
    textAlign: 'center',
  },
  message: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    marginTop: spacing.sm,
    textAlign: 'center',
  },
  hint: {
    fontSize: typography.fontSize.sm,
    color: colors.textTertiary,
    textAlign: 'center',
    marginTop: spacing.lg,
    lineHeight: 20,
  },
});
