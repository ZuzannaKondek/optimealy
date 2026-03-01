"""Constraint definitions for meal plan optimization."""
from typing import List, Dict, Any, Set
import logging
from ortools.sat.python import cp_model

from src.models.recipe import Recipe
from src.models.product import Product

logger = logging.getLogger(__name__)


class ConstraintBuilder:
    """Builder for optimization constraints."""

    def __init__(
        self,
        model: cp_model.CpModel,
        recipes: List[Recipe],
        days: int,
        target_calories: int,
        target_protein: float | None = None,
        target_carbs: float | None = None,
        target_fat: float | None = None,
        selected_meal_types: List[str] | None = None,
    ):
        """
        Initialize constraint builder.
        
        Args:
            model: CP-SAT model instance
            recipes: List of available recipes
            days: Number of days in the meal plan
            target_calories: Daily calorie target
            target_protein: Daily protein target in grams (optional)
            target_carbs: Daily carbohydrate target in grams (optional)
            target_fat: Daily fat target in grams (optional)
            selected_meal_types: List of course types selected by user (e.g., ["Breakfast", "Dinner", "Supper"])
        """
        self.model = model
        self.recipes = recipes
        self.days = days
        self.target_calories = target_calories
        self.target_protein = target_protein
        self.target_carbs = target_carbs
        self.target_fat = target_fat
        self.selected_meal_types = selected_meal_types
        
        # Recipe variables: recipe_vars[day][recipe_index] = 1 if recipe is selected
        self.recipe_vars: Dict[int, Dict[int, cp_model.IntVar]] = {}
        
        # Servings variables: servings_vars[day][recipe_index] = servings amount
        self.servings_vars: Dict[int, Dict[int, cp_model.IntVar]] = {}
        
        # Initialize variables
        self._initialize_variables()

    def _initialize_variables(self) -> None:
        """Initialize CP-SAT variables for recipes and servings."""
        num_recipes = len(self.recipes)
        
        for day in range(self.days):
            self.recipe_vars[day] = {}
            self.servings_vars[day] = {}
            
            for recipe_idx in range(num_recipes):
                # Binary variable: 1 if recipe is selected for this day
                self.recipe_vars[day][recipe_idx] = self.model.NewBoolVar(
                    f"recipe_day_{day}_recipe_{recipe_idx}"
                )
                
                # Integer variable: servings (0-100, scaled by 10 for precision)
                # e.g., 10 = 1.0 serving, 15 = 1.5 servings
                # For dish-based planning, this will be constrained to exactly 10 when selected
                self.servings_vars[day][recipe_idx] = self.model.NewIntVar(
                    0, 100, f"servings_day_{day}_recipe_{recipe_idx}"
                )
                
                # Constraint: servings can only be > 0 if recipe is selected
                # If recipe is NOT selected, servings must be 0
                self.model.Add(
                    self.servings_vars[day][recipe_idx] == 0
                ).OnlyEnforceIf(self.recipe_vars[day][recipe_idx].Not())
                
                # Note: For dish-based planning (the only supported mode),
                # servings are fixed to exactly 10 (1.0 serving) in add_dish_based_constraints.

    def add_calorie_constraint(
        self,
        lower_tolerance_percent: float = 0.10,
        upper_tolerance_percent: float = 0.15,
    ) -> None:
        """
        Add daily calorie constraint with tolerance bounds.
        
        These are safety-net hard bounds. The objective function handles
        precision (minimising deviation from target). These bounds just
        prevent degenerate solutions.
        
        Args:
            lower_tolerance_percent: Lower bound tolerance (default 0.10 = -10%)
            upper_tolerance_percent: Upper bound tolerance (default 0.15 = +15%)
        """
        # Scaling explanation:
        # servings_vars is scaled by 10 (10 = 1.0 serving, so 2 = 0.2 servings)
        # Actual calories = (servings_vars / 10) * calories_per_serving
        # To avoid division, we scale: calories_scaled = servings_vars * calories_per_serving
        # So if servings_vars = 2 and calories_per_serving = 900:
        #   calories_scaled = 2 * 900 = 1800 (which represents 180 actual calories)
        #   To get actual: 1800 / 10 = 180 ✓
        # Therefore, bounds should be: target_calories * 10
        lower_bound = int(self.target_calories * (1 - lower_tolerance_percent) * 10)
        upper_bound = int(self.target_calories * (1 + upper_tolerance_percent) * 10)
        
        for day in range(self.days):
            # Build total calories expression by summing contributions from all recipes
            # Create an intermediate variable for total calories (scaled by 10)
            max_possible_calories = sum(
                round(r.nutritional_info_per_serving.get("calories", 0)) * 100  # max servings (100) * calories
                for r in self.recipes
            )
            total_calories_var = self.model.NewIntVar(
                0, max_possible_calories, f"total_calories_day_{day}"
            )
            
            # Build calorie contributions list
            daily_calorie_contributions = []
            for recipe_idx, recipe in enumerate(self.recipes):
                calories_per_serving = recipe.nutritional_info_per_serving.get("calories", 0)
                if calories_per_serving <= 0:
                    continue
                # Scale: calories_scaled = servings_vars * calories_per_serving
                # This gives us calories * 10 (since servings_vars is already scaled by 10)
                calories_contribution = (
                    self.servings_vars[day][recipe_idx] * round(calories_per_serving)
                )
                daily_calorie_contributions.append(calories_contribution)
            
            # Set total_calories_var to sum of all contributions
            if daily_calorie_contributions:
                self.model.Add(total_calories_var == sum(daily_calorie_contributions))
                # Enforce calorie bounds (scaled by 10)
                self.model.Add(total_calories_var >= lower_bound)
                self.model.Add(total_calories_var <= upper_bound)
                logger.info(
                    f"Added calorie constraint for day {day + 1}: "
                    f"target={self.target_calories}, bounds=[{lower_bound/10:.0f}, {upper_bound/10:.0f}] "
                    f"({-lower_tolerance_percent*100:.0f}%/+{upper_tolerance_percent*100:.0f}%), "
                    f"(scaled: [{lower_bound}, {upper_bound}])"
                )
            else:
                # If no recipes have calories, this is an error
                raise ValueError(f"No recipes with valid calorie information for day {day + 1}")
            
            # Ensure at least one recipe is selected per day
            selected_recipes = [self.recipe_vars[day][idx] for idx in range(len(self.recipes))]
            self.model.Add(sum(selected_recipes) >= 1)  # At least one recipe per day

    def add_macro_constraints(
        self,
        lower_tolerance_percent: float = 0.30,
        upper_tolerance_percent: float = 0.30,
    ) -> None:
        """
        Add macro nutrient hard-bound constraints.
        
        These are wide safety-net bounds. The objective function handles
        precision (minimising deviation from target). These bounds prevent
        absurd macro distributions without fighting the calorie target.
        
        Args:
            lower_tolerance_percent: Lower bound tolerance (default 0.30 = -30%)
            upper_tolerance_percent: Upper bound tolerance (default 0.30 = +30%)
        """
        if self.target_protein is None and self.target_carbs is None and self.target_fat is None:
            return
        
        # Scale targets by 10 to match servings_vars scaling
        for day in range(self.days):
            daily_protein = []
            daily_carbs = []
            daily_fat = []
            
            for recipe_idx, recipe in enumerate(self.recipes):
                nutrition = recipe.nutritional_info_per_serving
                servings = self.servings_vars[day][recipe_idx]
                
                # Protein
                if self.target_protein is not None:
                    protein_per_serving = nutrition.get("protein", 0)
                    # servings_vars is scaled by 10, so: protein_scaled = servings_vars * protein_per_serving
                    protein_contribution = servings * round(protein_per_serving)
                    daily_protein.append(protein_contribution)
                
                # Carbs
                if self.target_carbs is not None:
                    carbs_per_serving = nutrition.get("carbs", 0)
                    carbs_contribution = servings * round(carbs_per_serving)
                    daily_carbs.append(carbs_contribution)
                
                # Fat
                if self.target_fat is not None:
                    fat_per_serving = nutrition.get("fat", 0)
                    fat_contribution = servings * round(fat_per_serving)
                    daily_fat.append(fat_contribution)
            
            # Protein constraint (scaled by 10)
            if self.target_protein is not None and daily_protein:
                lower = int(self.target_protein * (1 - lower_tolerance_percent) * 10)
                upper = int(self.target_protein * (1 + upper_tolerance_percent) * 10)
                total_protein = sum(daily_protein)
                self.model.Add(total_protein >= lower)
                self.model.Add(total_protein <= upper)
                logger.info(
                    f"Added protein constraint for day {day + 1}: "
                    f"target={self.target_protein}g, bounds=[{lower/10:.0f}, {upper/10:.0f}]g "
                    f"({-lower_tolerance_percent*100:.0f}%/+{upper_tolerance_percent*100:.0f}%)"
                )
            
            # Carbs constraint (scaled by 10)
            if self.target_carbs is not None and daily_carbs:
                lower = int(self.target_carbs * (1 - lower_tolerance_percent) * 10)
                upper = int(self.target_carbs * (1 + upper_tolerance_percent) * 10)
                total_carbs = sum(daily_carbs)
                self.model.Add(total_carbs >= lower)
                self.model.Add(total_carbs <= upper)
                logger.info(
                    f"Added carbs constraint for day {day + 1}: "
                    f"target={self.target_carbs}g, bounds=[{lower/10:.0f}, {upper/10:.0f}]g "
                    f"({-lower_tolerance_percent*100:.0f}%/+{upper_tolerance_percent*100:.0f}%)"
                )
            
            # Fat constraint (scaled by 10)
            if self.target_fat is not None and daily_fat:
                lower = int(self.target_fat * (1 - lower_tolerance_percent) * 10)
                upper = int(self.target_fat * (1 + upper_tolerance_percent) * 10)
                total_fat = sum(daily_fat)
                self.model.Add(total_fat >= lower)
                self.model.Add(total_fat <= upper)
                logger.info(
                    f"Added fat constraint for day {day + 1}: "
                    f"target={self.target_fat}g, bounds=[{lower/10:.0f}, {upper/10:.0f}]g "
                    f"({-lower_tolerance_percent*100:.0f}%/+{upper_tolerance_percent*100:.0f}%)"
                )

    def add_ingredient_exclusion_constraint(self, excluded_product_ids: List[str]) -> None:
        """
        Add constraint to exclude specific ingredients (100% hard constraint).
        
        Args:
            excluded_product_ids: List of product IDs to exclude
        """
        if not excluded_product_ids:
            return
        
        # Find recipes that use excluded ingredients
        excluded_recipe_indices: Set[int] = set()
        
        for recipe_idx, recipe in enumerate(self.recipes):
            for ingredient in recipe.recipe_ingredients:
                if str(ingredient.product_id) in excluded_product_ids:
                    excluded_recipe_indices.add(recipe_idx)
                    break
        
        # Constraint: excluded recipes cannot be selected
        for day in range(self.days):
            for recipe_idx in excluded_recipe_indices:
                self.model.Add(self.recipe_vars[day][recipe_idx] == 0)

    def add_recipe_variety_constraint(self, no_repeat_days: int = 3) -> None:
        """
        Add constraint to prevent recipe repetition within N days.
        
        Args:
            no_repeat_days: Number of days before a recipe can repeat (default 3)
        """
        num_recipes = len(self.recipes)
        
        for day in range(self.days):
            for recipe_idx in range(num_recipes):
                # Look back at previous days
                start_day = max(0, day - no_repeat_days + 1)
                
                # If this recipe was used in any of the previous N-1 days, it cannot be used today
                for prev_day in range(start_day, day):
                    # If recipe was used on prev_day, it cannot be used on day
                    self.model.Add(
                        self.recipe_vars[day][recipe_idx] == 0
                    ).OnlyEnforceIf(self.recipe_vars[prev_day][recipe_idx])

    def add_meal_type_constraint(self) -> None:
        """Add constraint to ensure at least one meal per meal type per day."""
        # Group recipes by meal type
        meal_type_groups: Dict[str, List[int]] = {}
        
        for recipe_idx, recipe in enumerate(self.recipes):
            for meal_type in recipe.meal_types:
                if meal_type not in meal_type_groups:
                    meal_type_groups[meal_type] = []
                meal_type_groups[meal_type].append(recipe_idx)
        
        # For each day, ensure at least one recipe from each required meal type
        # Only enforce constraints for meal types that actually have recipes
        required_meal_types = ["breakfast", "dinner", "supper"]  # Other meal types optional
        
        for day in range(self.days):
            for meal_type in required_meal_types:
                if meal_type in meal_type_groups and len(meal_type_groups[meal_type]) > 0:
                    recipe_indices = meal_type_groups[meal_type]
                    # At least one recipe of this meal type must be selected
                    meal_type_vars = [
                        self.recipe_vars[day][idx] for idx in recipe_indices
                    ]
                    self.model.Add(sum(meal_type_vars) >= 1)

    def get_recipe_vars(self) -> Dict[int, Dict[int, cp_model.IntVar]]:
        """Get recipe selection variables."""
        return self.recipe_vars

    def get_servings_vars(self) -> Dict[int, Dict[int, cp_model.IntVar]]:
        """Get servings variables."""
        return self.servings_vars

    def add_dish_based_constraints(self) -> None:
        """
        Add dish-based planning constraints.
        
        Enforces:
        1. Each dish is exactly 1 serving (servings_vars == 10 when recipe selected)
        2. Exactly N dishes per day (where N = len(selected_meal_types))
        3. No duplicate recipes per day (each recipe can appear at most once)
        4. Exactly one recipe per selected meal type per day
        """
        if self.selected_meal_types is None:
            return
        
        expected_count = len(self.selected_meal_types)
        num_recipes = len(self.recipes)
        
        for day in range(self.days):
            # Constraint 1: Fix servings to exactly 1.0 (10 in scaled units) when recipe is selected
            # Use direct equality constraints with OnlyEnforceIf for both directions
            for recipe_idx in range(num_recipes):
                # If recipe is selected, servings MUST be exactly 10
                self.model.Add(
                    self.servings_vars[day][recipe_idx] == 10
                ).OnlyEnforceIf(self.recipe_vars[day][recipe_idx])
                
                # If recipe is NOT selected, servings MUST be 0
                # (This should already be enforced in _initialize_variables, but we make it explicit)
                self.model.Add(
                    self.servings_vars[day][recipe_idx] == 0
                ).OnlyEnforceIf(self.recipe_vars[day][recipe_idx].Not())
                
                # Note: The two constraints above already ensure servings can only be 0 or 10
                # No additional constraint needed
            
            # Constraint 2: Enforce exactly N dishes per day
            # Sum of all recipe_vars for this day must equal expected_count
            selected_dishes = [self.recipe_vars[day][idx] for idx in range(num_recipes)]
            self.model.Add(sum(selected_dishes) == expected_count)
            
            # Constraint 4: Ensure exactly one recipe per meal type
            for meal_type in self.selected_meal_types:
                # Find recipes that have this meal_type
                # No mapping needed - selected meal types directly match recipe meal_types
                recipe_indices_for_meal_type = []
                for recipe_idx, recipe in enumerate(self.recipes):
                    # Check if recipe has this meal_type
                    if meal_type in recipe.meal_types:
                        recipe_indices_for_meal_type.append(recipe_idx)
                
                if recipe_indices_for_meal_type:
                    # Exactly one recipe from this group must be selected for this meal type
                    meal_type_vars = [self.recipe_vars[day][idx] for idx in recipe_indices_for_meal_type]
                    self.model.Add(sum(meal_type_vars) == 1)
                else:
                    logger.warning(
                        f"No recipes found for meal type '{meal_type}'"
                    )
            
            logger.info(
                f"Added dish-based constraints for day {day + 1}: "
                f"exactly {expected_count} dishes, each exactly 1 serving"
            )
