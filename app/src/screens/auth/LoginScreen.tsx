import React from 'react';
import { View, Text, StyleSheet, Switch, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { colors, spacing, typography } from '../../theme';
import { authService } from '../../services/authService';
import { useAuth } from '../../context/AuthContext';

export const LoginScreen: React.FC = () => {
  const navigation = useNavigation();
  const { login } = useAuth();

  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [rememberMe, setRememberMe] = React.useState(true);
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [errors, setErrors] = React.useState<{ email?: string; password?: string }>({});

  const validate = () => {
    const next: typeof errors = {};
    if (!email.includes('@')) next.email = 'Enter a valid email address';
    if (!password) next.password = 'Password is required';
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const onSubmit = async () => {
    if (!validate()) return;
    setIsSubmitting(true);
    try {
      const tokens = await authService.login({ email, password }, rememberMe);
      const profile = await authService.getProfile();
      await login(tokens.access_token, tokens.refresh_token, {
        id: profile.user_id,
        email: profile.email,
        language_preference: profile.language_preference,
        theme_preference: profile.theme_preference,
        unit_preference: profile.unit_preference,
      });
    } catch (e: any) {
      Alert.alert('Login failed', e?.response?.data?.detail || 'Invalid credentials');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Login</Text>
      <Text style={styles.subtitle}>Welcome back — sign in to continue.</Text>

      <Input
        label="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
        error={errors.email}
      />
      <Input
        label="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        error={errors.password}
      />

      <View style={styles.rememberRow}>
        <Text style={styles.rememberText}>Remember me</Text>
        <Switch value={rememberMe} onValueChange={setRememberMe} />
      </View>

      <Button title="Login" onPress={onSubmit} loading={isSubmitting} />
      <Button
        title="Create account"
        onPress={() => navigation.navigate('Registration' as never)}
        variant="secondary"
        style={{ marginTop: spacing.sm }}
      />
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
  rememberRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  rememberText: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
  },
});

