/**
 * Authentication Context
 * OptiMeal Mobile App
 * 
 * Manages user authentication state across the application.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { setAuthToken, setRefreshToken, clearAuthTokens, getAuthToken } from '../services/api';
import { authService } from '../services/authService';
import { settingsService } from '../services/settingsService';

interface User {
  id: string;
  email: string;
  language_preference: string;
  theme_preference: 'light' | 'dark' | 'system';
  unit_preference: 'metric' | 'imperial';
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (accessToken: string, refreshToken: string, user: User) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Check for existing token on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const shouldRestore = await authService.shouldRestoreSession();
      if (!shouldRestore) {
        await clearAuthTokens();
        setUser(null);
        return;
      }

      const token = await getAuthToken();
      
      if (token) {
        const profile = await authService.getProfile();
        setUser({
          id: profile.user_id,
          email: profile.email,
          language_preference: profile.language_preference,
          theme_preference: profile.theme_preference,
          unit_preference: profile.unit_preference,
        });
        
        // Sync settings from backend to local storage on startup
        try {
          const backendSettings: any = {
            language_preference: profile.language_preference,
            theme_preference: profile.theme_preference,
            unit_preference: profile.unit_preference,
          };
          // Add notification_settings if available from profile
          if (profile.notification_settings) {
            backendSettings.notification_settings = profile.notification_settings;
          }
          // Update local storage with backend settings
          const local = await settingsService.getLocalSettings();
          const merged = { ...local, ...backendSettings };
          // Only sync to backend if there are actual changes, otherwise just update local
          await settingsService.updateSettings(merged);
        } catch (error) {
          console.error('Error syncing settings on startup:', error);
        }
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      await clearAuthTokens();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (accessToken: string, refreshToken: string, userData: User) => {
    await setAuthToken(accessToken);
    await setRefreshToken(refreshToken);
    setUser(userData);
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  const updateUser = (userData: User) => {
    setUser(userData);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: user !== null,
    isLoading,
    login,
    logout,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};
