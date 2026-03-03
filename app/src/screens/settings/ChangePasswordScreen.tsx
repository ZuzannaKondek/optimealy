import React from 'react';
import { View, Text, StyleSheet, Alert } from 'react-native';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { colors, spacing, typography } from '../../theme';
import { authService } from '../../services/authService';

export const ChangePasswordScreen: React.FC = () => {
  const [currentPassword, setCurrentPassword] = React.useState('');
  const [newPassword, setNewPassword] = React.useState('');
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const onSubmit = async () => {
    if (newPassword.length < 8) {
      Alert.alert('Walidacja', 'Nowe hasło musi zawierać co najmniej 8 znaków');
      return;
    }
    setIsSubmitting(true);
    try {
      await authService.updatePassword({ current_password: currentPassword, new_password: newPassword });
      Alert.alert('Sukces', 'Hasło zaktualizowane');
      setCurrentPassword('');
      setNewPassword('');
    } catch (e: any) {
      Alert.alert('Błąd', e?.response?.data?.detail || 'Nie udało się zaktualizować hasła');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Zmień hasło</Text>
      <Text style={styles.subtitle}>Ze względów bezpieczeństwa najpierw wprowadź swoje obecne hasło.</Text>

      <Input
        label="Obecne hasło"
        value={currentPassword}
        onChangeText={setCurrentPassword}
        secureTextEntry
      />
      <Input label="Nowe hasło" value={newPassword} onChangeText={setNewPassword} secureTextEntry />

      <Button title="Zaktualizuj hasło" onPress={onSubmit} loading={isSubmitting} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: spacing.screenPadding,
    paddingTop: spacing.lg,
  },
  title: {
    fontSize: typography.fontSize.xxxl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
  },
});

