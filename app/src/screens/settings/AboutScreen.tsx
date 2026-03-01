/**
 * About / O serwisie — mandatory notice for EPI thesis (struktura.prd).
 * Replace AUTHOR_NAME and PROMOTOR_TITLE_NAME with your details.
 */
import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { colors, spacing, typography } from '../../theme';

const AUTHOR_NAME = '[Imię Nazwisko]';
const PROMOTOR_TITLE_NAME = '[tytuł, imię i nazwisko promotora]';

export const AboutScreen: React.FC = () => {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>O serwisie</Text>
      <Text style={styles.paragraph}>
        Autorem niniejszego serwisu jest {AUTHOR_NAME}.
      </Text>
      <Text style={styles.paragraph}>
        Serwis ten stanowi integralną część pracy licencjackiej (kierunek:
        elektroniczne przetwarzanie informacji), przygotowanej pod kierunkiem{' '}
        {PROMOTOR_TITLE_NAME} na Wydziale Zarządzania i Komunikacji Społecznej
        Uniwersytetu Jagiellońskiego.
      </Text>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.screenPadding,
    paddingBottom: spacing.xl,
  },
  title: {
    fontSize: typography.fontSize.xxl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  paragraph: {
    fontSize: typography.fontSize.md,
    color: colors.textPrimary,
    lineHeight: 24,
    marginBottom: spacing.md,
    textAlign: 'left',
  },
});
