/**
 * Frontend Type Definitions
 * OptiMeal Mobile App
 * 
 * Type definitions for frontend models (extending shared API contracts).
 */

import type {
  MealPlanSummary,
  MealPlanDetail,
  DailyMenu,
  Meal,
  MealPlanDayDetail,
  CreateMealPlanRequest,
  GroceryList,
  GroceryItem,
} from '../../shared/types/api-contracts';

// Re-export shared types
export type {
  MealPlanSummary,
  MealPlanDetail,
  DailyMenu,
  Meal,
  MealPlanDayDetail,
  CreateMealPlanRequest,
  GroceryList,
  GroceryItem,
};

// Extended types for frontend-specific use
export interface PlanCreationFormData {
  name: string;
  durationDays: number;
  targetCalories: number;
  targetProtein?: number;
  targetCarbs?: number;
  targetFat?: number;
  startDate?: Date;
  selectedMealTypes?: string[];
  ingredientsToHave: Array<{ productId: string; quantityG: number }>;
  ingredientsToWant: string[];
  ingredientsToExclude: string[];
  dietaryTags: string[];
  cuisineTypes: string[];
}

export interface PlanCreationState {
  isCreating: boolean;
  progress: number;
  status: 'idle' | 'creating' | 'completed' | 'failed';
  error: string | null;
  createdPlanId: string | null;
}
