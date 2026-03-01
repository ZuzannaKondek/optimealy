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
      Alert.alert('Validation', 'New password must be at least 8 characters');
      return;
    }
    setIsSubmitting(true);
    try {
      await authService.updatePassword({ current_password: currentPassword, new_password: newPassword });
      Alert.alert('Success', 'Password updated');
      setCurrentPassword('');
      setNewPassword('');
    } catch (e: any) {
      Alert.alert('Error', e?.response?.data?.detail || 'Failed to update password');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Change Password</Text>
      <Text style={styles.subtitle}>For security, enter your current password first.</Text>

      <Input
        label="Current password"
        value={currentPassword}
        onChangeText={setCurrentPassword}
        secureTextEntry
      />
      <Input label="New password" value={newPassword} onChangeText={setNewPassword} secureTextEntry />

      <Button title="Update password" onPress={onSubmit} loading={isSubmitting} />
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

