import React from 'react';
import { Alert } from 'react-native';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { Screen } from '../../components/layout/Screen';
import { ScreenHeader } from '../../components/layout/ScreenHeader';
import { Section } from '../../components/layout/Section';
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
    <Screen>
      <ScreenHeader
        title="Zmień hasło"
        subtitle="Ze względów bezpieczeństwa najpierw wprowadź swoje obecne hasło."
      />
      <Section title="Zmiana hasła">
        <Input
          label="Obecne hasło"
          value={currentPassword}
          onChangeText={setCurrentPassword}
          secureTextEntry
        />
        <Input label="Nowe hasło" value={newPassword} onChangeText={setNewPassword} secureTextEntry />
        <Button title="Zaktualizuj hasło" onPress={onSubmit} loading={isSubmitting} />
      </Section>
    </Screen>
  );
};

