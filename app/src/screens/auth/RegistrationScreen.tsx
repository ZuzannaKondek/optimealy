import React from 'react';
import { View, Text, StyleSheet, Alert } from 'react-native';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { colors, spacing, typography } from '../../theme';
import { authService } from '../../services/authService';
import { useAuth } from '../../context/AuthContext';

function validatePassword(password: string): string | null {
  if (password.length < 8) return 'Password must be at least 8 characters';
  if (!/[A-Z]/.test(password)) return 'Include at least one uppercase letter';
  if (!/[a-z]/.test(password)) return 'Include at least one lowercase letter';
  if (!/[0-9]/.test(password)) return 'Include at least one number';
  return null;
}

export const RegistrationScreen: React.FC = () => {
  const { login } = useAuth();

  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [confirmPassword, setConfirmPassword] = React.useState('');
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [errors, setErrors] = React.useState<{ email?: string; password?: string; confirmPassword?: string }>({});

  const validate = () => {
    const next: typeof errors = {};
    if (!email.includes('@')) next.email = 'Enter a valid email address';
    const pwError = validatePassword(password);
    if (pwError) next.password = pwError;
    if (confirmPassword !== password) next.confirmPassword = 'Passwords do not match';
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const onSubmit = async () => {
    if (!validate()) return;
    setIsSubmitting(true);
    try {
      await authService.register({ email, password });
      const tokens = await authService.login({ email, password }, true);
      const profile = await authService.getProfile();
      await login(tokens.access_token, tokens.refresh_token, {
        id: profile.user_id,
        email: profile.email,
        language_preference: profile.language_preference,
        theme_preference: profile.theme_preference,
        unit_preference: profile.unit_preference,
      });
    } catch (e: any) {
      // Extract error message from server response
      const serverMessage = e?.response?.data?.detail || e?.response?.data?.message;
      const errorMessage = serverMessage || e?.message || 'Could not create account';
      
      // Log error details for debugging (only in development)
      if (__DEV__) {
        console.error('Registration error:', {
          status: e?.response?.status,
          message: errorMessage,
          serverResponse: e?.response?.data,
        });
      }
      
      // Handle 409 Conflict (email already exists) with better UX
      if (e?.response?.status === 409) {
        // Use server message if available, otherwise use default
        const message = serverMessage || 'This email address is already registered. Please use a different email or try logging in instead.';
        setErrors({ email: message });
        Alert.alert('Email already exists', message);
      } else {
        // For other errors, show alert and set form errors if applicable
        Alert.alert('Registration failed', errorMessage);
        if (errorMessage.toLowerCase().includes('email')) {
          setErrors({ email: errorMessage });
        } else if (errorMessage.toLowerCase().includes('password')) {
          setErrors({ password: errorMessage });
        } else {
          // Clear previous errors for non-field-specific errors
          setErrors({});
        }
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Create account</Text>
      <Text style={styles.subtitle}>Create an OptiMeal account to save and manage your plans.</Text>

      <Input
        label="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
        error={errors.email}
      />
      <Input label="Password" value={password} onChangeText={setPassword} secureTextEntry error={errors.password} />
      <Input
        label="Confirm password"
        value={confirmPassword}
        onChangeText={setConfirmPassword}
        secureTextEntry
        error={errors.confirmPassword}
      />

      <Button title="Create account" onPress={onSubmit} loading={isSubmitting} />
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

