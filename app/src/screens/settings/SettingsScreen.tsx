import React from 'react';
import { useNavigation } from '@react-navigation/native';
import { SettingsSection } from '../../components/settings/SettingsSection';
import { SettingRow } from '../../components/settings/SettingRow';
import { Button } from '../../components/common/Button';
import { Screen } from '../../components/layout/Screen';
import { ScreenHeader } from '../../components/layout/ScreenHeader';
import { useAuth } from '../../context/AuthContext';

export const SettingsScreen: React.FC = () => {
  const navigation = useNavigation();
  const { user, logout } = useAuth();

  return (
    <Screen>
      <ScreenHeader
        title="Ustawienia"
        subtitle={user?.email}
      />

      <SettingsSection title="Ustawienia konta">
        <SettingRow
          title="Zmień hasło"
          subtitle="Zaktualizuj hasło swojego konta"
          onPress={() => navigation.navigate('ChangePassword' as never)}
        />
      </SettingsSection>

      <SettingsSection title="Informacje">
        <SettingRow
          title="O serwisie"
          subtitle="Informacja o pracy licencjackiej (EPI, UJ)"
          onPress={() => navigation.navigate('About' as never)}
        />
      </SettingsSection>

      <Button title="Wyloguj się" onPress={() => void logout()} variant="secondary" />
    </Screen>
  );
};

