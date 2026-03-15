/**
 * Main App Navigator
 * OptiMeal Mobile App
 * 
 * Navigation for authenticated users (Tabs: Home, Today, Pantry, Settings).
 * Each tab has its own stack navigator to keep tabs visible on all screens.
 */

import React, { useState, useEffect } from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { View, ActivityIndicator, Text, StyleSheet } from 'react-native';
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
    <HomeStack.Screen name="GroceryList" component={GroceryListScreen} options={{ title: 'Potrzebne produkty' }} />
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
import { planService } from '../services/planService';
import { ShoppingListScreen } from '../screens/grocery/ShoppingListScreen';

const GroceryStack = createStackNavigator();

// Wrapper to get active plan and navigate to ShoppingList
const GroceryListWrapper: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const getActivePlanAndNavigate = async () => {
      try {
        const activePlan = await planService.getActivePlan();
        if (activePlan) {
          navigation.navigate('ShoppingList', { planId: activePlan.plan_id });
        }
      } catch (e) {
        console.error('Failed to get active plan:', e);
      } finally {
        setIsLoading(false);
      }
    };
    getActivePlanAndNavigate();
  }, [navigation]);

  if (isLoading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Ładowanie...</Text>
      </View>
    );
  }

  return (
    <View style={styles.loading}>
      <Text style={styles.noPlanText}>Brak aktywnego planu</Text>
      <Text style={styles.noPlanSubtext}>Utwórz plan, aby zobaczyć listę produktów</Text>
    </View>
  );
};

// Wrapper to get active plan and navigate to ShoppingList
const ShoppingListWrapper: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const getActivePlanAndNavigate = async () => {
      try {
        const activePlan = await planService.getActivePlan();
        if (activePlan) {
          navigation.navigate('ShoppingList', { planId: activePlan.plan_id });
        }
      } catch (e) {
        console.error('Failed to get active plan:', e);
      } finally {
        setIsLoading(false);
      }
    };
    getActivePlanAndNavigate();
  }, [navigation]);

  if (isLoading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Ładowanie...</Text>
      </View>
    );
  }

  return (
    <View style={styles.loading}>
      <Text style={styles.noPlanText}>Brak aktywnego planu</Text>
      <Text style={styles.noPlanSubtext}>Utwórz plan, aby zobaczyć listę zakupów</Text>
    </View>
  );
};

const GroceryStackScreen = () => (
  <GroceryStack.Navigator
    screenOptions={{
      headerStyle: { backgroundColor: colors.primary },
      headerTintColor: colors.white,
      headerTitleStyle: { fontWeight: typography.fontWeight.semiBold },
      headerBackTitleVisible: false,
    }}
  >
    <GroceryStack.Screen 
      name="ShoppingListMain" 
      component={ShoppingListWrapper} 
      options={{ title: 'Zakupy' }} 
    />
    <GroceryStack.Screen 
      name="ShoppingList" 
      component={ShoppingListScreen} 
      options={{ title: 'Zakupy' }} 
    />
    <GroceryStack.Screen 
      name="GroceryList" 
      component={GroceryListScreen} 
      options={{ title: 'Potrzebne produkty' }} 
    />
  </GroceryStack.Navigator>
);

const styles = StyleSheet.create({
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
    padding: spacing.lg,
  },
  loadingText: {
    marginTop: spacing.sm,
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
  },
  noPlanText: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  noPlanSubtext: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    textAlign: 'center',
  },
});

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
        name="Grocery"
        component={GroceryStackScreen}
        options={{
          tabBarLabel: 'Zakupy',
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
