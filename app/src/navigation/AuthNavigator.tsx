/**
 * Authentication Navigator
 * OptiMeal Mobile App
 * 
 * Navigation for unauthenticated users (Login, Registration).
 */

import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { colors, typography } from '../theme';
import { HomepageScreen } from '../screens/home/HomepageScreen';
import { LoginScreen } from '../screens/auth/LoginScreen';
import { RegistrationScreen } from '../screens/auth/RegistrationScreen';

const Stack = createStackNavigator();

export const AuthNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: colors.primary,
        },
        headerTintColor: colors.white,
        headerTitleStyle: {
          fontWeight: typography.fontWeight.semiBold,
        },
      }}
    >
      <Stack.Screen
        name="Homepage"
        component={HomepageScreen}
        options={{ headerShown: false }}
      />
      <Stack.Screen
        name="Login"
        component={LoginScreen}
        options={{ title: 'Zaloguj się' }}
      />
      <Stack.Screen
        name="Registration"
        component={RegistrationScreen}
        options={{ title: 'Utwórz konto' }}
      />
    </Stack.Navigator>
  );
};
