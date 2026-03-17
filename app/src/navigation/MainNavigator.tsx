/**
 * Main App Navigator
 * OptiMeal Mobile App
 * 
 * Navigation for authenticated users (Tabs: Home, Today, Pantry, Settings).
 * Each tab has its own stack navigator to keep tabs visible on all screens.
 * 
 * Feature 6: Navigation Chrome - Adds sidebar layout on wide screens (web/tablet)
 */

import React, { useState, useCallback } from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { StyleSheet, ActivityIndicator, View, useWindowDimensions, TouchableOpacity, Text } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { colors, spacing, typography } from '../theme';
import { planService } from '../services/planService';

// Sidebar breakpoint for wide screens (web/tablet)
const SIDEBAR_BREAKPOINT = 768;

// Tab configuration
type TabRoute = 'Home' | 'Today' | 'Pantry' | 'Grocery' | 'Settings';

interface TabConfig {
  name: TabRoute;
  label: string;
  icon: string;
}

const TAB_CONFIG: TabConfig[] = [
  { name: 'Home', label: 'Pulpit', icon: '🏠' },
  { name: 'Today', label: 'Dzisiaj', icon: '📅' },
  { name: 'Pantry', label: 'Spiżarnia', icon: '🗄️' },
  { name: 'Grocery', label: 'Zakupy', icon: '🛒' },
  { name: 'Settings', label: 'Ustawienia', icon: '⚙️' },
];

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
      headerStyle: { backgroundColor: colors.surface },
      headerTintColor: colors.textPrimary,
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
      headerStyle: { backgroundColor: colors.surface },
      headerTintColor: colors.textPrimary,
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
      headerStyle: { backgroundColor: colors.surface },
      headerTintColor: colors.textPrimary,
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
import { ShoppingListScreen } from '../screens/grocery/ShoppingListScreen';

const GroceryStack = createStackNavigator();

// Wrapper that auto-loads active plan's shopping list when accessed directly
const ShoppingListWrapper: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [activePlanId, setActivePlanId] = useState<string | undefined>(undefined);

  useFocusEffect(
    useCallback(() => {
      let cancelled = false;

      const fetchActivePlan = async () => {
        setIsLoading(true);
        try {
          const plan = await planService.getActivePlan();
          if (!cancelled) {
            setActivePlanId(plan?.id);
          }
        } catch (e) {
          if (!cancelled) {
            setActivePlanId(undefined);
          }
        } finally {
          if (!cancelled) {
            setIsLoading(false);
          }
        }
      };

      fetchActivePlan();

      return () => {
        cancelled = true;
      };
    }, [])
  );

  if (isLoading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return <ShoppingListScreen planId={activePlanId} />;
};

const GroceryStackScreen = () => (
  <GroceryStack.Navigator
    screenOptions={{
      headerStyle: { backgroundColor: colors.surface },
      headerTintColor: colors.textPrimary,
      headerTitleStyle: { fontWeight: typography.fontWeight.semiBold },
      headerBackTitleVisible: false,
    }}
  >
    <GroceryStack.Screen 
      name="ShoppingListMain" 
      component={ShoppingListWrapper} 
      options={{ headerShown: false }} 
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

const SettingsStack = createStackNavigator();

const SettingsStackScreen = () => (
  <SettingsStack.Navigator
    screenOptions={{
      headerStyle: { backgroundColor: colors.surface },
      headerTintColor: colors.textPrimary,
      headerTitleStyle: { fontWeight: typography.fontWeight.semiBold },
      headerBackTitleVisible: false,
    }}
  >
    <SettingsStack.Screen name="SettingsMain" component={SettingsScreen} options={{ headerShown: false }} />
    <SettingsStack.Screen name="ChangePassword" component={ChangePasswordScreen} options={{ title: 'Zmień hasło' }} />
    <SettingsStack.Screen name="About" component={AboutScreen} options={{ title: 'O serwisie' }} />
  </SettingsStack.Navigator>
);

const Tab = createBottomTabNavigator();

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
  // Wide screen layout: sidebar + content
  wideContainer: {
    flex: 1,
    flexDirection: 'row',
  },
  sidebar: {
    width: 240,
    backgroundColor: colors.surface,
    borderRightWidth: 1,
    borderRightColor: colors.border,
  },
  sidebarHeader: {
    padding: spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    backgroundColor: colors.primary,
  },
  sidebarLogo: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    color: colors.white,
  },
  sidebarContent: {
    flex: 1,
    paddingVertical: spacing.md,
  },
  sidebarItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    marginHorizontal: spacing.sm,
    borderRadius: 8,
  },
  sidebarItemActive: {
    backgroundColor: colors.primaryLight || colors.primary + '20',
  },
  sidebarIcon: {
    fontSize: 20,
    marginRight: spacing.md,
  },
  sidebarLabel: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    fontWeight: typography.fontWeight.medium,
  },
  sidebarLabelActive: {
    color: colors.primary,
    fontWeight: typography.fontWeight.semiBold,
  },
  contentArea: {
    flex: 1,
  },
});

// Sidebar component for wide screens - integrates with Tab.Navigator
const Sidebar: React.FC<{ currentTab: TabRoute; onNavigate: (tab: TabRoute) => void }> = ({ 
  currentTab, 
  onNavigate 
}) => {
  return (
    <View style={styles.sidebar}>
      <View style={styles.sidebarHeader}>
        <Text style={styles.sidebarLogo}>OptiMeal</Text>
      </View>
      <View style={styles.sidebarContent}>
        {TAB_CONFIG.map((tab) => {
          const isFocused = currentTab === tab.name;
          return (
            <TouchableOpacity
              key={tab.name}
              style={[
                styles.sidebarItem,
                isFocused && styles.sidebarItemActive,
              ]}
              onPress={() => onNavigate(tab.name)}
              accessibilityRole="button"
              accessibilityLabel={tab.label}
            >
              <Text style={styles.sidebarIcon}>{tab.icon}</Text>
              <Text
                style={[
                  styles.sidebarLabel,
                  isFocused && styles.sidebarLabelActive,
                ]}
              >
                {tab.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
};

// Main app with responsive layout
export const MainNavigator: React.FC = () => {
  const { width } = useWindowDimensions();
  const isWideScreen = width >= SIDEBAR_BREAKPOINT;

  if (isWideScreen) {
    return <WideScreenNavigator />;
  }

  // Narrow screens: standard bottom tabs
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
        options={{ tabBarLabel: 'Pulpit' }}
      />
      <Tab.Screen
        name="Today"
        component={TodayStackScreen}
        options={{ tabBarLabel: 'Dzisiaj' }}
      />
      <Tab.Screen
        name="Pantry"
        component={PantryStackScreen}
        options={{ tabBarLabel: 'Spiżarnia' }}
      />
      <Tab.Screen
        name="Grocery"
        component={GroceryStackScreen}
        options={{ tabBarLabel: 'Zakupy' }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsStackScreen}
        options={{ tabBarLabel: 'Ustawienia' }}
      />
    </Tab.Navigator>
  );
};

// Wide screen navigator with sidebar on left
const WideScreenNavigator: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<TabRoute>('Home');

  const navigateToTab = (tab: TabRoute) => {
    setCurrentTab(tab);
  };

  const renderStack = () => {
    switch (currentTab) {
      case 'Home':
        return <HomeStackScreen />;
      case 'Today':
        return <TodayStackScreen />;
      case 'Pantry':
        return <PantryStackScreen />;
      case 'Grocery':
        return <GroceryStackScreen />;
      case 'Settings':
        return <SettingsStackScreen />;
      default:
        return <HomeStackScreen />;
    }
  };

  return (
    <View style={styles.wideContainer}>
      <Sidebar currentTab={currentTab} onNavigate={navigateToTab} />
      <View style={styles.contentArea}>
        {renderStack()}
      </View>
    </View>
  );
};
