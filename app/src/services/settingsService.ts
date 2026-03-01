import AsyncStorage from '@react-native-async-storage/async-storage';
import apiClient from './api';
import type { UpdateSettingsRequest } from '../../shared/types/api-contracts';

const SETTINGS_KEY = '@optimeal:settings';

export const settingsService = {
  async updateSettings(request: UpdateSettingsRequest): Promise<void> {
    await apiClient.patch('/users/settings', request);
    const existing = await settingsService.getLocalSettings();
    const merged = { ...existing, ...request };
    await AsyncStorage.setItem(SETTINGS_KEY, JSON.stringify(merged));
  },

  async getLocalSettings(): Promise<UpdateSettingsRequest> {
    const raw = await AsyncStorage.getItem(SETTINGS_KEY);
    if (!raw) return {};
    try {
      return JSON.parse(raw) as UpdateSettingsRequest;
    } catch {
      return {};
    }
  },
};

