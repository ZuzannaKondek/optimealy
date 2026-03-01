import React from 'react';
import { View, Text, StyleSheet, ScrollView, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { SettingsSection } from '../../components/settings/SettingsSection';
import { SettingRow } from '../../components/settings/SettingRow';
import { Button } from '../../components/common/Button';
import { colors, spacing, typography } from '../../theme';
import { useTheme } from '../../context/ThemeContext';
import { useAuth } from '../../context/AuthContext';
import { settingsService } from '../../services/settingsService';

type ThemeMode = 'light' | 'dark' | 'system';
type UnitPref = 'metric' | 'imperial';

export const SettingsScreen: React.FC = () => {
  const navigation = useNavigation();
  const { themeMode, setThemeMode } = useTheme();
  const { user, logout } = useAuth();

  const [language, setLanguage] = React.useState<'en' | 'es'>('en');
  const [unit, setUnit] = React.useState<UnitPref>('metric');
  const [notificationSettings, setNotificationSettings] = React.useState<{
    enabled?: boolean;
    plan_reminders?: boolean;
    grocery_reminders?: boolean;
  }>({
    enabled: true,
    plan_reminders: true,
    grocery_reminders: false,
  });

  React.useEffect(() => {
    const load = async () => {
      const local = await settingsService.getLocalSettings();
      if (local.language_preference === 'en' || local.language_preference === 'es') setLanguage(local.language_preference);
      if (local.unit_preference === 'metric' || local.unit_preference === 'imperial') setUnit(local.unit_preference);
      if (local.notification_settings) {
        setNotificationSettings({
          enabled: local.notification_settings.enabled ?? true,
          plan_reminders: local.notification_settings.plan_reminders ?? true,
          grocery_reminders: local.notification_settings.grocery_reminders ?? false,
        });
      }
    };
    void load();
  }, []);

  const update = async (patch: any) => {
    try {
      await settingsService.updateSettings(patch);
    } catch (e: any) {
      Alert.alert('Error', e?.response?.data?.detail || 'Failed to save settings');
    }
  };

  const setTheme = async (mode: ThemeMode) => {
    await setThemeMode(mode);
    await update({ theme_preference: mode });
  };

  const setLang = async (lang: 'en' | 'es') => {
    setLanguage(lang);
    await update({ language_preference: lang });
  };

  const setUnitPref = async (pref: UnitPref) => {
    setUnit(pref);
    await update({ unit_preference: pref });
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Settings</Text>
      {user ? <Text style={styles.subtitle}>{user.email}</Text> : null}

      <SettingsSection title="Appearance">
        <SettingRow
          title="Theme"
          subtitle={`Current: ${themeMode}`}
          right={
            <View style={styles.rowButtons}>
              <Button title="Light" variant="secondary" onPress={() => setTheme('light')} disabled={themeMode === 'light'} />
              <Button title="Dark" variant="secondary" onPress={() => setTheme('dark')} disabled={themeMode === 'dark'} />
              <Button
                title="System"
                variant="secondary"
                onPress={() => setTheme('system')}
                disabled={themeMode === 'system'}
              />
            </View>
          }
        />
      </SettingsSection>

      <SettingsSection title="Preferences">
        <SettingRow
          title="Language"
          subtitle={`Current: ${language}`}
          right={
            <View style={styles.rowButtons}>
              <Button title="EN" variant="secondary" onPress={() => setLang('en')} disabled={language === 'en'} />
              <Button title="ES" variant="secondary" onPress={() => setLang('es')} disabled={language === 'es'} />
            </View>
          }
        />
        <SettingRow
          title="Units"
          subtitle={`Current: ${unit}`}
          right={
            <View style={styles.rowButtons}>
              <Button title="Metric" variant="secondary" onPress={() => setUnitPref('metric')} disabled={unit === 'metric'} />
              <Button
                title="Imperial"
                variant="secondary"
                onPress={() => setUnitPref('imperial')}
                disabled={unit === 'imperial'}
              />
            </View>
          }
        />
        <SettingRow
          title="Change password"
          subtitle="Update your account password"
          onPress={() => navigation.navigate('ChangePassword' as never)}
        />
      </SettingsSection>

      <SettingsSection title="Meal Planning">
        <SettingRow
          title="My Pantry"
          subtitle="Manage items you already have"
          onPress={() => navigation.navigate('Pantry' as never)}
        />
      </SettingsSection>

      <SettingsSection title="Info">
        <SettingRow
          title="O serwisie"
          subtitle="Informacja o pracy licencjackiej (EPI, UJ)"
          onPress={() => navigation.navigate('About' as never)}
        />
      </SettingsSection>

      <SettingsSection title="Notifications">
        <SettingRow
          title="Enable Notifications"
          subtitle={notificationSettings.enabled ? 'Notifications are enabled' : 'Notifications are disabled'}
          right={
            <Button
              title={notificationSettings.enabled ? 'ON' : 'OFF'}
              variant={notificationSettings.enabled ? 'primary' : 'secondary'}
              onPress={async () => {
                const newValue = !notificationSettings.enabled;
                setNotificationSettings({ ...notificationSettings, enabled: newValue });
                await update({
                  notification_settings: {
                    ...notificationSettings,
                    enabled: newValue,
                  },
                });
              }}
            />
          }
        />
        <SettingRow
          title="Plan Reminders"
          subtitle="Remind me about meal plans"
          right={
            <Button
              title={notificationSettings.plan_reminders ? 'ON' : 'OFF'}
              variant={notificationSettings.plan_reminders ? 'primary' : 'secondary'}
              onPress={async () => {
                const newValue = !notificationSettings.plan_reminders;
                setNotificationSettings({ ...notificationSettings, plan_reminders: newValue });
                await update({
                  notification_settings: {
                    ...notificationSettings,
                    plan_reminders: newValue,
                  },
                });
              }}
              disabled={!notificationSettings.enabled}
            />
          }
        />
        <SettingRow
          title="Grocery Reminders"
          subtitle="Remind me about grocery lists"
          right={
            <Button
              title={notificationSettings.grocery_reminders ? 'ON' : 'OFF'}
              variant={notificationSettings.grocery_reminders ? 'primary' : 'secondary'}
              onPress={async () => {
                const newValue = !notificationSettings.grocery_reminders;
                setNotificationSettings({ ...notificationSettings, grocery_reminders: newValue });
                await update({
                  notification_settings: {
                    ...notificationSettings,
                    grocery_reminders: newValue,
                  },
                });
              }}
              disabled={!notificationSettings.enabled}
            />
          }
        />
      </SettingsSection>

      <Button title="Logout" onPress={() => void logout()} variant="secondary" />
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

