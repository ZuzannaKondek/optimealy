/**
 * Root App Navigator
 * OptiMeal Mobile App
 * 
 * Determines whether to show Auth or Main navigation based on authentication state.
 */

import React from 'react';
import { NavigationContainer, LinkingOptions } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { useAuth } from '../context/AuthContext';
import { AuthNavigator } from './AuthNavigator';
import { MainNavigator } from './MainNavigator';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { colors, spacing } from '../theme';

const Stack = createStackNavigator();

// Deep linking configuration
const linking: LinkingOptions<ReactNavigation.RootParamList> = {
  prefixes: ['optimealy://', 'https://optimealy.app'],
  config: {
    screens: {
      Main: {
        screens: {
          Tabs: {
            screens: {
              Home: 'home',
              Plans: 'plans',
              Create: 'create',
              Settings: 'settings',
            },
          },
          PlanDetail: {
            path: 'plans/:planId',
            parse: {
              planId: (planId: string) => planId,
            },
          },
          DayDetail: {
            path: 'plans/:planId/days/:dayNumber',
            parse: {
              planId: (planId: string) => planId,
              dayNumber: (dayNumber: string) => parseInt(dayNumber, 10),
            },
          },
          GroceryList: {
            path: 'plans/:planId/grocery',
            parse: {
              planId: (planId: string) => planId,
            },
          },
        },
      },
      Auth: {
        screens: {
          Homepage: '',
          Login: 'login',
          Registration: 'register',
        },
      },
    },
  },
};

export const AppNavigator: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading OptiMeal...</Text>
      </View>
    );
  }

  return (
    <NavigationContainer linking={linking}>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <Stack.Screen name="Main" component={MainNavigator} />
        ) : (
          <Stack.Screen name="Auth" component={AuthNavigator} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: 16,
    color: colors.textSecondary,
  },
});
