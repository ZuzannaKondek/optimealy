/**
 * Plans Hook with Zustand Store
 * OptiMeal Mobile App
 * 
 * State management for meal plans.
 */

import { create } from 'zustand';
import { planService } from '../services/planService';
import { getApiErrorMessage } from '../utils/apiErrors';
import type { MealPlanSummary, MealPlanDetail, PlanCreationState } from '../types/models';

interface PlansState {
  // Plans list
  plans: MealPlanSummary[];
  isLoading: boolean;
  error: string | null;

  // Selected plan
  selectedPlan: MealPlanDetail | null;
  isLoadingDetail: boolean;

  // Plan creation
  creationState: PlanCreationState;

  // Actions
  fetchPlans: (options?: {
    status?: string;
    limit?: number;
    offset?: number;
    append?: boolean;
  }) => Promise<void>;
  fetchPlanDetail: (planId: string) => Promise<void>;
  createPlan: (request: any) => Promise<string | null>;
  deletePlan: (planId: string) => Promise<void>;
  clearError: () => void;
  resetCreationState: () => void;
}

const initialCreationState: PlanCreationState = {
  isCreating: false,
  progress: 0,
  status: 'idle',
  error: null,
  createdPlanId: null,
};

export const usePlans = create<PlansState>((set, get) => ({
  // Initial state
  plans: [],
  isLoading: false,
  error: null,
  selectedPlan: null,
  isLoadingDetail: false,
  creationState: initialCreationState,

  // Fetch plans list
  fetchPlans: async (options) => {
    set({ isLoading: true, error: null });
    try {
      const status = options?.status;
      const limit = options?.limit ?? 10;
      const offset = options?.offset ?? 0;
      const append = options?.append ?? false;
      // By default, exclude failed plans unless explicitly requested
      // Pass undefined to get all plans, then filter out failed ones client-side
      const statusFilter = status;

      const plans = await planService.getPlans(statusFilter, limit, offset);
      // Filter out failed plans by default unless status is explicitly set
      const filteredPlans = status === undefined 
        ? plans.filter(p => p.optimization_status !== 'failed')
        : plans;
      
      set((state) => ({
        plans: append ? [...state.plans, ...filteredPlans] : filteredPlans,
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch plans',
        isLoading: false,
      });
    }
  },

  // Fetch plan detail
  fetchPlanDetail: async (planId: string) => {
    set({ isLoadingDetail: true, error: null });
    try {
      const plan = await planService.getPlanById(planId);
      set({ selectedPlan: plan, isLoadingDetail: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch plan details',
        isLoadingDetail: false,
      });
    }
  },

  // Create plan
  createPlan: async (request: any) => {
    set({
      creationState: {
        ...initialCreationState,
        isCreating: true,
        status: 'creating',
        progress: 0,
      },
    });

    try {
      const response = await planService.createPlan(request);
      const planId = response.plan_id;

      // Poll for status
      const pollStatus = async () => {
        try {
          const status = await planService.getOptimizationStatus(planId);
          
          // Update progress percentage
          const progressValue = status.progress_percentage ?? 0;
          
          if (status.status === 'completed') {
            set({
              creationState: {
                isCreating: false,
                progress: 100,
                status: 'completed',
                error: null,
                createdPlanId: planId,
              },
            });
            return;
          }

          if (status.status === 'failed') {
            set({
              creationState: {
                isCreating: false,
                progress: 0,
                status: 'failed',
                error: status.message || 'Optimization failed',
                createdPlanId: null,
              },
            });
            return;
          }

          // Still in progress
          set({
            creationState: {
              ...get().creationState,
              progress: progressValue,
            },
          });

          // Poll again after 1.5 seconds
          setTimeout(pollStatus, 1500);
        } catch (error: any) {
          set({
            creationState: {
              isCreating: false,
              progress: 0,
              status: 'failed',
              error: getApiErrorMessage(error),
              createdPlanId: null,
            },
          });
        }
      };

      // Start polling immediately
      setTimeout(pollStatus, 500);

      return planId;
    } catch (error: any) {
      set({
        creationState: {
          isCreating: false,
          progress: 0,
          status: 'failed',
          error: getApiErrorMessage(error),
          createdPlanId: null,
        },
      });
      return null;
    }
  },

  // Delete plan
  deletePlan: async (planId: string) => {
    try {
      await planService.deletePlan(planId);
      // Remove from list
      set((state) => ({
        plans: state.plans.filter((p) => p.plan_id !== planId),
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to delete plan',
      });
      throw error;
    }
  },

  // Clear error
  clearError: () => {
    set({ error: null });
  },

  // Reset creation state
  resetCreationState: () => {
    set({ creationState: initialCreationState });
  },
}));
