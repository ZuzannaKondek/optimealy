/**
 * About / O serwisie — mandatory notice for EPI thesis (struktura.prd).
 * Replace AUTHOR_NAME and PROMOTOR_TITLE_NAME with your details.
 */
import React from 'react';
import { Text, StyleSheet } from 'react-native';
import { Screen } from '../../components/layout/Screen';
import { ScreenHeader } from '../../components/layout/ScreenHeader';
import { Section } from '../../components/layout/Section';
import { colors, spacing, typography } from '../../theme';

const AUTHOR_NAME = '[Imię Nazwisko]';
const PROMOTOR_TITLE_NAME = '[tytuł, imię i nazwisko promotora]';

export const AboutScreen: React.FC = () => {
  return (
    <Screen>
      <ScreenHeader title="O serwisie" />
      <Section title="O serwisie">
        <Text style={styles.paragraph}>
          Autorem niniejszego serwisu jest {AUTHOR_NAME}.
        </Text>
        <Text style={styles.paragraph}>
          Serwis ten stanowi integralną część pracy licencjackiej (kierunek:
          elektroniczne przetwarzanie informacji), przygotowanej pod kierunkiem{' '}
          {PROMOTOR_TITLE_NAME} na Wydziale Zarządzania i Komunikacji Społecznej
          Uniwersytetu Jagiellońskiego.
        </Text>
      </Section>
    </Screen>
  );
};

const styles = StyleSheet.create({
  paragraph: {
    fontSize: typography.fontSize.md,
    color: colors.textPrimary,
    lineHeight: 24,
    marginBottom: spacing.md,
    textAlign: 'left',
  },
});
