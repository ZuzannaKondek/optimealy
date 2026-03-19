/**
 * Plan Creation Error Modal
 * Shown when the optimizer cannot find a satisfactory plan.
 * Explains the error and gives clear next steps.
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  TouchableOpacity,
  ScrollView,
  Pressable,
} from 'react-native';
import { colors, spacing, typography } from '../../theme';

const WHAT_YOU_CAN_DO = [
  'Złóż swój dzienny cel kaloryczny (np. 800–5000 kcal).',
  'Złagodź lub usuń ścisłe cele makroskładników (białko/węglowodany/tłuszcze).',
  'Skróć czas trwania planu (np. 1–7 dni), aby zmniejszyć ograniczenia.',
  'Wybierz mniej typów posiłków (np. tylko śniadanie i obiad), jeśli masz ograniczoną liczbę przepisów.',
  'Zmniejsz liczbę wykluczonych składników, aby było więcej dostępnych przepisów.',
  'Dodaj więcej przepisów w ustawieniach, aby algorytm miał więcej opcji.',
];

export interface PlanCreationErrorModalProps {
  visible: boolean;
  message: string;
  onDismiss: () => void;
}

export const PlanCreationErrorModal: React.FC<PlanCreationErrorModalProps> = ({
  visible,
  message,
  onDismiss,
}) => {
  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onDismiss}
    >
      <Pressable style={styles.overlay} onPress={onDismiss}>
        <Pressable style={styles.card} onPress={(e) => e.stopPropagation()}>
          <ScrollView
            style={styles.scroll}
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
          >
            <Text style={styles.title}>Nie udało się utworzyć planu</Text>
            <Text style={styles.message}>{message}</Text>
            <Text style={styles.sectionTitle}>Co możesz zrobić</Text>
            {WHAT_YOU_CAN_DO.map((item, i) => (
              <Text key={i} style={styles.bullet}>
                • {item}
              </Text>
            ))}
          </ScrollView>
          <TouchableOpacity
            style={styles.button}
            onPress={onDismiss}
            activeOpacity={0.8}
          >
            <Text style={styles.buttonText}>Spróbuj ponownie</Text>
          </TouchableOpacity>
        </Pressable>
      </Pressable>
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
    maxWidth: 400,
    width: '100%',
    maxHeight: '80%',
  },
  scroll: {
    maxHeight: 360,
  },
  scrollContent: {
    padding: spacing.lg,
    paddingBottom: spacing.sm,
  },
  title: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  message: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    lineHeight: 22,
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  bullet: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: spacing.xs,
  },
  button: {
    backgroundColor: colors.primary,
    marginHorizontal: spacing.lg,
    marginVertical: spacing.md,
    padding: spacing.md,
    borderRadius: spacing.borderRadius,
    alignItems: 'center',
  },
  buttonText: {
    color: colors.white,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
  },
});
