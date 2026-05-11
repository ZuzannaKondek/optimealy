import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Button } from '../../components/common/Button';
import { colors, spacing, typography } from '../../theme';

export const HomepageScreen: React.FC = () => {
  const navigation = useNavigation();

  return (
    <View 
      style={styles.container}
      accessibilityRole="main"
      accessibilityLabel="Strona główna"
    >
      <View style={styles.content}>
        <Text 
          style={styles.title}
          accessibilityRole="header"
          accessibilityLevel={1}
        >
          OptiMeal
        </Text>
        <Text style={styles.subtitle}>
          Stwórz zoptymalizowany plan posiłków, który spełni Twoje cele żywieniowe i zminimalizuje marnotrawstwo żywności.
        </Text>
      </View>

      <View style={styles.buttonContainer}>
        <Button
          title="Załóż konto"
          onPress={() => navigation.navigate('Registration' as never)}
          variant="primary"
          style={styles.primaryButton}
          accessibilityLabel="Załóż nowe konto"
          accessibilityHint="Przejdź do formularza rejestracji"
        />
        <Button
          title="Zaloguj się"
          onPress={() => navigation.navigate('Login' as never)}
          variant="secondary"
          style={styles.secondaryButton}
          accessibilityLabel="Zaloguj się do istniejącego konta"
          accessibilityHint="Przejdź do formularza logowania"
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: spacing.screenPadding,
    paddingTop: spacing.lg,
    justifyContent: 'space-between',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
  },
  title: {
    fontSize: typography.fontSize.xxxl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: typography.fontSize.md * 1.5,
  },
  buttonContainer: {
    paddingBottom: spacing.lg,
  },
  primaryButton: {
    marginBottom: spacing.md,
  },
  secondaryButton: {
    // No additional margin needed
  },
});

