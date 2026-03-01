/**
 * Meal Plan Service
 * OptiMeal Mobile App
 * 
 * API client for meal plan operations.
 */

import apiClient from './api';
import type {
  CreateMealPlanRequest,
  CreateMealPlanResponse,
  MealPlanSummary,
  MealPlanDetail,
  MealPlanDayDetail,
  OptimizationStatus,
  GroceryList,
} from '../../shared/types/api-contracts';

export const planService = {
  /**
   * Create a new optimized meal plan.
   * Builds the request body explicitly so required fields (e.g. name) are never dropped.
   */
  async createPlan(request: CreateMealPlanRequest): Promise<CreateMealPlanResponse> {
    const name = typeof request.name === 'string' ? request.name.trim() : '';
    if (!name) {
      throw new Error('Plan name is required');
    }
    const body: CreateMealPlanRequest = {
      name,
      duration_days: request.duration_days,
      target_calories_per_day: request.target_calories_per_day,
      target_protein_g: request.target_protein_g,
      target_carbs_g: request.target_carbs_g,
      target_fat_g: request.target_fat_g,
      start_date: request.start_date,
      selected_meal_types: request.selected_meal_types,
      ingredients_to_have: request.ingredients_to_have,
      ingredients_to_want: request.ingredients_to_want,
      ingredients_to_exclude: request.ingredients_to_exclude,
      dietary_tags: request.dietary_tags,
      cuisine_types: request.cuisine_types,
    };
    const response = await apiClient.post<CreateMealPlanResponse>('/meal-plans', body);
    return response.data;
  },

  /**
   * Get all meal plans for the current user.
   */
  async getPlans(
    status?: string,
    limit: number = 10,
    offset: number = 0
  ): Promise<MealPlanSummary[]> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    const response = await apiClient.get<MealPlanSummary[]>(`/meal-plans?${params.toString()}`);
    return response.data;
  },

  /**
   * Get detailed information for a specific meal plan.
   */
  async getPlanById(planId: string): Promise<MealPlanDetail> {
    const response = await apiClient.get<MealPlanDetail>(`/meal-plans/${planId}`);
    return response.data;
  },

  /**
   * Get detailed information for a specific day in a meal plan.
   */
  async getPlanDay(planId: string, dayNumber: number): Promise<MealPlanDayDetail> {
    const response = await apiClient.get<MealPlanDayDetail>(
      `/meal-plans/${planId}/days/${dayNumber}`
    );
    return response.data;
  },

  /**
   * Get optimization status for a meal plan.
   */
  async getOptimizationStatus(planId: string): Promise<OptimizationStatus> {
    const response = await apiClient.get<OptimizationStatus>(`/meal-plans/${planId}/status`);
    return response.data;
  },

  /**
   * Delete a meal plan.
   */
  async deletePlan(planId: string): Promise<void> {
    await apiClient.delete(`/meal-plans/${planId}`);
  },

  /**
   * Get grocery list for a meal plan.
   */
  async getGroceryList(
    planId: string,
    options?: { groupBy?: 'category' | 'aisle' | 'recipe'; excludeOwned?: boolean }
  ): Promise<GroceryList> {
    const params = new URLSearchParams();
    if (options?.groupBy) params.append('group_by', options.groupBy);
    if (options?.excludeOwned) params.append('exclude_owned', 'true');

    const suffix = params.toString() ? `?${params.toString()}` : '';
    const response = await apiClient.get<GroceryList>(`/meal-plans/${planId}/grocery${suffix}`);
    return response.data;
  },
};
