import AsyncStorage from '@react-native-async-storage/async-storage';
import apiClient, { clearAuthTokens, setAuthToken, setRefreshToken } from './api';
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  UpdatePasswordRequest,
  UserProfile,
} from '../../shared/types/api-contracts';

const REMEMBER_ME_KEY = '@optimeal:remember_me';

export const authService = {
  async register(request: RegisterRequest): Promise<RegisterResponse> {
    try {
      const response = await apiClient.post<RegisterResponse>('/auth/register', request);
      return response.data;
    } catch (error: any) {
      // Re-throw with better error information
      if (error.response) {
        // Server responded with error status
        throw error;
      } else if (error.request) {
        // Request was made but no response received
        throw new Error('Network error: Could not reach the server. Please check your connection.');
      } else {
        // Something else happened
        throw new Error(error.message || 'An unexpected error occurred during registration.');
      }
    }
  },

  async login(request: LoginRequest, rememberMe: boolean): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', request);
    await setAuthToken(response.data.access_token);
    await setRefreshToken(response.data.refresh_token);
    await AsyncStorage.setItem(REMEMBER_ME_KEY, rememberMe ? 'true' : 'false');
    return response.data;
  },

  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>('/auth/profile');
    return response.data;
  },

  async logout(): Promise<void> {
    await clearAuthTokens();
    await AsyncStorage.removeItem(REMEMBER_ME_KEY);
  },

  async updatePassword(request: UpdatePasswordRequest): Promise<void> {
    await apiClient.patch('/auth/password', request);
  },

  async shouldRestoreSession(): Promise<boolean> {
    const remember = await AsyncStorage.getItem(REMEMBER_ME_KEY);
    return remember === null || remember === 'true';
  },
};

