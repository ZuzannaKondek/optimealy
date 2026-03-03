import React from 'react';
import { View, Text, StyleSheet, ScrollView, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { SettingsSection } from '../../components/settings/SettingsSection';
import { SettingRow } from '../../components/settings/SettingRow';
import { Button } from '../../components/common/Button';
import { colors, spacing, typography } from '../../theme';
import { useAuth } from '../../context/AuthContext';
import { settingsService } from '../../services/settingsService';

type UnitPref = 'metric' | 'imperial';

export const SettingsScreen: React.FC = () => {
  const navigation = useNavigation();
  const { user, logout } = useAuth();

  const [unit, setUnit] = React.useState<UnitPref>('metric');

  React.useEffect(() => {
    const load = async () => {
      const local = await settingsService.getLocalSettings();
      if (local.unit_preference === 'metric' || local.unit_preference === 'imperial') setUnit(local.unit_preference);
    };
    void load();
  }, []);

  const update = async (patch: any) => {
    try {
      await settingsService.updateSettings(patch);
    } catch (e: any) {
      Alert.alert('Błąd', e?.response?.data?.detail || 'Nie udało się zapisać ustawień');
    }
  };

  const setUnitPref = async (pref: UnitPref) => {
    setUnit(pref);
    await update({ unit_preference: pref });
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Ustawienia</Text>
      {user ? <Text style={styles.subtitle}>{user.email}</Text> : null}

      <SettingsSection title="Preferencje">
        <SettingRow
          title="Jednostki"
          subtitle={`Aktualne: ${unit}`}
          right={
            <View style={styles.rowButtons}>
              <Button title="Metryczne" variant="secondary" onPress={() => setUnitPref('metric')} disabled={unit === 'metric'} />
              <Button
                title="Imperialne"
                variant="secondary"
                onPress={() => setUnitPref('imperial')}
                disabled={unit === 'imperial'}
              />
            </View>
          }
        />
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
    paddingBottom: spacing.lg,
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
  rowButtons: {
    flexDirection: 'row',
    gap: spacing.xs,
  },
});

