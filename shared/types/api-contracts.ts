/**
 * Shared TypeScript API Contract Types
 * OptiMeal - Meal Planning Optimization Application
 * 
 * These types define the contract between frontend (React Native)
 * and backend (FastAPI) for type-safe API communication.
 */

// ============================================================================
// Common Types
// ============================================================================

export type UUID = string;
export type ISODateString = string;
export type ISODateTimeString = string;

// ============================================================================
// Authentication Types
// ============================================================================

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface RegisterResponse {
  message: string;
  user_id: UUID;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  refresh_token?: string;
}

export interface RefreshRequest {
  refresh_token: string;
}

export interface RefreshResponse {
  access_token: string;
  token_type: "bearer";
}

export interface UserProfile {
  user_id: UUID;
  email: string;
  language_preference: string;
  theme_preference: "light" | "dark" | "system";
  unit_preference: "metric" | "imperial";
  notification_settings: Record<string, boolean>;
  created_at: ISODateTimeString;
}

// ============================================================================
// Meal Plan Types
// ============================================================================

export interface IngredientConstraint {
  product_id: UUID;
  quantity_g: number;
}

export interface CreateMealPlanRequest {
  name: string;
  duration_days: number;
  target_calories_per_day: number;
  target_protein_g?: number;
  target_carbs_g?: number;
  target_fat_g?: number;
  start_date?: ISODateString;
  // Meal types: "breakfast", "second_breakfast", "dinner", "dessert", "supper"
  selected_meal_types?: string[];
  ingredients_to_have?: IngredientConstraint[];
  ingredients_to_want?: UUID[];
  ingredients_to_exclude?: UUID[];
  dietary_tags?: string[];
  cuisine_types?: string[];
}

export interface CreateMealPlanResponse {
  message: string;
  plan_id: UUID;
  status_url: string;
}

export interface NutritionalInfo {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber?: number;
}

export interface RecipeDetail {
  id: UUID;
  name: string;
  description?: string | null;
  image_url?: string | null;
  cooking_time_minutes?: number | null;
  prep_time_minutes?: number | null;
  difficulty_level?: string | null;
  instructions_single_serving?: string | null;
  ingredients?: Array<{ name: string; quantity: number; unit: string }> | null;
}

export interface Meal {
  meal_id: UUID;
  meal_type: "breakfast" | "second_breakfast" | "dinner" | "dessert" | "supper";
  recipe_id: UUID;
  recipe_name: string;
  servings: number;
  dish_weight_g?: number | null;
  calculated_nutritional_info: NutritionalInfo;
  recipe?: RecipeDetail | null;
}

export interface VarianceFromTarget {
  calorie_variance_pct: number | null;
  protein_variance_pct: number | null;
  carbs_variance_pct: number | null;
  fat_variance_pct: number | null;
}

export interface DailyMenu {
  day_number: number;
  menu_date: ISODateString;
  actual_calories: number;
  actual_protein_g: number;
  actual_carbs_g: number;
  actual_fat_g: number;
  variance_from_target?: VarianceFromTarget | null;
  meals: Meal[];
}

export interface MealPlanSummary {
  plan_id: UUID;
  name?: string | null;
  created_at: ISODateTimeString;
  start_date: ISODateString;
  duration_days: number;
  target_calories_per_day: number;
  dishes_per_day?: number | null;
  optimization_status: "pending" | "in_progress" | "completed" | "failed";
  /** Plan execution state: draft (not yet started), active, completed, cancelled */
  execution_status?: "draft" | "active" | "completed" | "cancelled";
  estimated_food_waste_g: number | null;
  waste_reduction_percentage: number | null;
  estimated_total_cost: number | null;
}

export interface MealPlanDetail extends MealPlanSummary {
  user_id: UUID;
  target_protein_g: number | null;
  target_carbs_g: number | null;
  target_fat_g: number | null;
  dishes_per_day?: number | null;
  user_constraints: Record<string, any>;
  algorithm_execution_time_s: number | null;
  daily_menus: DailyMenu[];
}

export interface MealPlanDayDetail {
  plan_id: UUID;
  daily_menu: DailyMenu;
}

export interface OptimizationStatus {
  plan_id: UUID;
  status: "pending" | "in_progress" | "completed" | "failed";
  progress_percentage?: number;
  message?: string;
}

// ============================================================================
// Grocery List Types
// ============================================================================

export interface GroceryItem {
  item_id: UUID;
  product_id: UUID;
  product_name: string;
  category: string;
  required_quantity_g: number;
  purchase_quantity_g: number;
  purchase_unit: string;
  estimated_item_cost: number | null;
  estimated_item_waste_g: number;
  status: "needed" | "already_have" | "purchased";
  used_in_recipes?: Array<{ recipe_id: UUID; recipe_name: string }> | null;
  exact_quantity?: boolean;
}

export interface GroceryList {
  grocery_list_id: UUID;
  meal_plan_id: UUID;
  generated_at: ISODateTimeString;
  total_items: number;
  estimated_total_cost: number | null;
  estimated_total_waste_g: number;
  items: GroceryItem[];
}

export interface UpdateGroceryItemStatusRequest {
  status: "needed" | "already_have" | "purchased";
}

// ============================================================================
// Settings Types
// ============================================================================

export interface UpdatePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface UpdateSettingsRequest {
  language_preference?: string;
  theme_preference?: "light" | "dark" | "system";
  unit_preference?: "metric" | "imperial";
  notification_settings?: Record<string, boolean>;
}

// ============================================================================
// Error Response Type
// ============================================================================

export interface ErrorResponse {
  detail: string;
}
