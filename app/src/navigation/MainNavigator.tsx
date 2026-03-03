/**
 * Main App Navigator
 * OptiMeal Mobile App
 * 
 * Navigation for authenticated users (Tabs: Home, Today, Pantry, Settings).
 * Each tab has its own stack navigator to keep tabs visible on all screens.
 */

import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { colors, spacing, typography } from '../theme';

const Tab = createBottomTabNavigator();

// Home Stack
import { UserPanelScreen } from '../screens/dashboard/UserPanelScreen';
import { PlanCreationScreen } from '../screens/create/PlanCreationScreen';
import { PlanDetailScreen } from '../screens/plans/PlanDetailScreen';
import { DayDetailScreen } from '../screens/plans/DayDetailScreen';
import { GroceryListScreen } from '../screens/grocery/GroceryListScreen';

const HomeStack = createStackNavigator();

const HomeStackScreen = () => (
  <HomeStack.Navigator
    screenOptions={{
      headerStyle: { backgroundColor: colors.primary },
      headerTintColor: colors.white,
      headerTitleStyle: { fontWeight: typography.fontWeight.semiBold },
      headerBackTitleVisible: false,
    }}
  >
    <HomeStack.Screen name="HomeMain" component={UserPanelScreen} options={{ headerShown: false }} />
    <HomeStack.Screen name="CreatePlan" component={PlanCreationScreen} options={{ title: 'Utwórz plan' }} />
    <HomeStack.Screen name="PlanDetail" component={PlanDetailScreen} options={{ title: 'Szczegóły planu' }} />
    <HomeStack.Screen name="DayDetail" component={DayDetailScreen} options={{ title: 'Szczegóły dnia' }} />
    <HomeStack.Screen name="GroceryList" component={GroceryListScreen} options={{ title: 'Lista zakupów' }} />
  </HomeStack.Navigator>
);

// Today Stack
import { TodayScreen } from '../screens/today/TodayScreen';

const TodayStack = createStackNavigator();

const TodayStackScreen = () => (
  <TodayStack.Navigator
    screenOptions={{
      headerStyle: { backgroundColor: colors.primary },
      headerTintColor: colors.white,
      headerTitleStyle: { fontWeight: typography.fontWeight.semiBold },
      headerBackTitleVisible: false,
    }}
  >
    <TodayStack.Screen name="TodayMain" component={TodayScreen} options={{ headerShown: false }} />
  </TodayStack.Navigator>
);

// Pantry Stack
import { PantryScreen } from '../screens/pantry/PantryScreen';

const PantryStack = createStackNavigator();

const PantryStackScreen = () => (
  <PantryStack.Navigator
    screenOptions={{
      headerStyle: { backgroundColor: colors.primary },
      headerTintColor: colors.white,
      headerTitleStyle: { fontWeight: typography.fontWeight.semiBold },
      headerBackTitleVisible: false,
    }}
  >
    <PantryStack.Screen name="PantryMain" component={PantryScreen} options={{ headerShown: false }} />
  </PantryStack.Navigator>
);

// Settings Stack
import { SettingsScreen } from '../screens/settings/SettingsScreen';
import { ChangePasswordScreen } from '../screens/settings/ChangePasswordScreen';
import { AboutScreen } from '../screens/settings/AboutScreen';

const SettingsStack = createStackNavigator();

const SettingsStackScreen = () => (
  <SettingsStack.Navigator
    screenOptions={{
      headerStyle: { backgroundColor: colors.primary },
      headerTintColor: colors.white,
      headerTitleStyle: { fontWeight: typography.fontWeight.semiBold },
      headerBackTitleVisible: false,
    }}
  >
    <SettingsStack.Screen name="SettingsMain" component={SettingsScreen} options={{ headerShown: false }} />
    <SettingsStack.Screen name="ChangePassword" component={ChangePasswordScreen} options={{ title: 'Zmień hasło' }} />
    <SettingsStack.Screen name="About" component={AboutScreen} options={{ title: 'O serwisie' }} />
  </SettingsStack.Navigator>
);

export const MainNavigator: React.FC = () => {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.border,
          height: spacing.tabBarHeight,
          paddingBottom: spacing.sm,
          paddingTop: spacing.sm,
        },
        headerShown: false,
      }}
    >
      <Tab.Screen
        name="Home"
        component={HomeStackScreen}
        options={{
          tabBarLabel: 'Pulpit',
        }}
      />
      <Tab.Screen
        name="Today"
        component={TodayStackScreen}
        options={{
          tabBarLabel: 'Dzisiaj',
        }}
      />
      <Tab.Screen
        name="Pantry"
        component={PantryStackScreen}
        options={{
          tabBarLabel: 'Spiżarnia',
        }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsStackScreen}
        options={{
          tabBarLabel: 'Ustawienia',
        }}
      />
    </Tab.Navigator>
  );
};
