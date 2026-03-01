/**
 * Main App Navigator
 * OptiMeal Mobile App
 * 
 * Navigation for authenticated users (Tabs: Home, Today, Pantry, Settings).
 */

import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { View, Text, StyleSheet } from 'react-native';
import { colors, spacing, typography } from '../theme';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

import { UserPanelScreen } from '../screens/dashboard/UserPanelScreen';

import { PlanCreationScreen } from '../screens/create/PlanCreationScreen';
import { PlanDetailScreen } from '../screens/plans/PlanDetailScreen';
import { DayDetailScreen } from '../screens/plans/DayDetailScreen';
import { GroceryListScreen } from '../screens/grocery/GroceryListScreen';
import { SettingsScreen } from '../screens/settings/SettingsScreen';
import { ChangePasswordScreen } from '../screens/settings/ChangePasswordScreen';
import { AboutScreen } from '../screens/settings/AboutScreen';
import { PantryScreen } from '../screens/pantry/PantryScreen';
import { TodayScreen } from '../screens/today/TodayScreen';

const Tabs: React.FC = () => {
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
        headerStyle: {
          backgroundColor: colors.primary,
        },
        headerTintColor: colors.white,
        headerTitleStyle: {
          fontWeight: typography.fontWeight.semiBold,
        },
      }}
    >
      <Tab.Screen
        name="Home"
        component={UserPanelScreen}
        options={{
          title: 'Home',
          tabBarLabel: 'Home',
        }}
      />
      <Tab.Screen
        name="Today"
        component={TodayScreen}
        options={{
          title: 'Today',
          tabBarLabel: 'Today',
        }}
      />
      <Tab.Screen
        name="Pantry"
        component={PantryScreen}
        options={{
          title: 'My Pantry',
          tabBarLabel: 'Pantry',
        }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{
          title: 'Settings',
          tabBarLabel: 'Settings',
        }}
      />
    </Tab.Navigator>
  );
};

export const MainNavigator: React.FC = () => {
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
        headerBackTitleVisible: false,
      }}
    >
      <Stack.Screen name="Tabs" component={Tabs} options={{ headerShown: false }} />
      <Stack.Screen 
        name="CreatePlan" 
        component={PlanCreationScreen} 
        options={{ 
          title: 'Create Plan',
          headerBackTitle: 'Back',
        }} 
      />
      <Stack.Screen 
        name="PlanDetail" 
        component={PlanDetailScreen} 
        options={{ 
          title: 'Plan Details',
          headerBackTitle: 'Back',
        }} 
      />
      <Stack.Screen 
        name="DayDetail" 
        component={DayDetailScreen} 
        options={{ 
          title: 'Day Details',
          headerBackTitle: 'Back',
        }} 
      />
      <Stack.Screen 
        name="GroceryList" 
        component={GroceryListScreen} 
        options={{ 
          title: 'Grocery List',
          headerBackTitle: 'Back',
        }} 
      />
      <Stack.Screen 
        name="ChangePassword" 
        component={ChangePasswordScreen} 
        options={{ 
          title: 'Change Password',
          headerBackTitle: 'Back',
        }} 
      />
      <Stack.Screen 
        name="Pantry" 
        component={PantryScreen} 
        options={{ 
          title: 'My Pantry',
          headerBackTitle: 'Back',
        }} 
      />
      <Stack.Screen 
        name="About" 
        component={AboutScreen} 
        options={{ 
          title: 'O serwisie',
          headerBackTitle: 'Back',
        }} 
      />
    </Stack.Navigator>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
    padding: spacing.lg,
  },
  title: {
    fontSize: typography.fontSize.xxl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    textAlign: 'center',
  },
});
