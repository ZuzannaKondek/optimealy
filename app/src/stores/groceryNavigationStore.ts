import { create } from 'zustand';
import type { TabRoute } from '../navigation/MainNavigator';

interface GroceryNavigationState {
  pendingPlanId: string | null;
  setPendingPlanId: (planId: string | null) => void;
  clearPendingPlanId: () => void;
  targetTab: TabRoute | null;
  setTargetTab: (tab: TabRoute | null) => void;
  clearTargetTab: () => void;
}

export const useGroceryNavigation = create<GroceryNavigationState>((set) => ({
  pendingPlanId: null,
  setPendingPlanId: (planId) => set({ pendingPlanId: planId }),
  clearPendingPlanId: () => set({ pendingPlanId: null }),
  targetTab: null,
  setTargetTab: (tab) => set({ targetTab: tab }),
  clearTargetTab: () => set({ targetTab: null }),
}));
