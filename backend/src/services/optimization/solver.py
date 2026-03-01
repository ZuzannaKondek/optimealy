"""OR-Tools CP-SAT solver for dish-based meal plan optimization.

Selects one recipe per meal-type slot per day, with fixed 1.0 serving,
minimising deviation from calorie and macro targets.
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
import time
from ortools.sat.python import cp_model

from src.models.recipe import Recipe
from src.models.product import Product
from src.services.optimization.constraints import ConstraintBuilder
from src.services.optimization.objective import ObjectiveBuilder

logger = logging.getLogger(__name__)


class OptimizationSolver:
    """Solver for dish-based meal plan optimization using OR-Tools CP-SAT."""

    def __init__(
        self,
        recipes: List[Recipe],
        products: List[Product],
        days: int,
        target_calories: int,
        target_protein: Optional[float] = None,
        target_carbs: Optional[float] = None,
        target_fat: Optional[float] = None,
        excluded_product_ids: Optional[List[str]] = None,
        timeout_seconds: int = 60,
        selected_meal_types: Optional[List[str]] = None,
    ):
        """
        Initialize optimization solver.

        Args:
            recipes: List of available recipes
            products: List of available products
            days: Number of days in the meal plan
            target_calories: Daily calorie target
            target_protein: Daily protein target in grams (optional)
            target_carbs: Daily carbohydrate target in grams (optional)
            target_fat: Daily fat target in grams (optional)
            excluded_product_ids: List of product IDs to exclude
            timeout_seconds: Maximum time to spend solving (default 60)
            selected_meal_types: List of course types (e.g. ["breakfast", "dinner", "supper"])
        """
        self.recipes = recipes
        self.products = products
        self.days = days
        self.target_calories = target_calories
        self.target_protein = target_protein
        self.target_carbs = target_carbs
        self.target_fat = target_fat
        self.excluded_product_ids = excluded_product_ids or []
        self.timeout_seconds = timeout_seconds
        self.selected_meal_types = selected_meal_types

    def solve(self) -> Tuple[Optional[Dict[str, Any]], str, Optional[str]]:
        """
        Solve the optimization problem.

        Returns:
            Tuple of (solution_dict, status, error_message)
            - solution_dict: Dictionary with selected recipes and servings, or None if failed
            - status: 'optimal', 'feasible', 'infeasible', 'timeout', or 'error'
            - error_message: Error message if status is 'error' or 'infeasible'
        """
        t_total = time.perf_counter()
        num_recipes = len(self.recipes)

        logger.info(
            "=== SOLVER START === "
            f"recipes={num_recipes}, days={self.days}, "
            f"cal_target={self.target_calories}, "
            f"meal_types={self.selected_meal_types}, "
            f"timeout={self.timeout_seconds}s"
        )

        # --- Model & variables ---
        t0 = time.perf_counter()
        model = cp_model.CpModel()

        constraint_builder = ConstraintBuilder(
            model=model,
            recipes=self.recipes,
            days=self.days,
            target_calories=self.target_calories,
            target_protein=self.target_protein,
            target_carbs=self.target_carbs,
            target_fat=self.target_fat,
            selected_meal_types=self.selected_meal_types,
        )
        logger.info(
            f"[solver] Variables initialised in {time.perf_counter() - t0:.3f}s  "
            f"({num_recipes} recipes × {self.days} days = "
            f"{num_recipes * self.days} binary + {num_recipes * self.days} serving vars)"
        )

        # --- Constraints ---
        t0 = time.perf_counter()
        constraint_builder.add_calorie_constraint(
            lower_tolerance_percent=0.10,
            upper_tolerance_percent=0.15,
        )
        constraint_builder.add_macro_constraints(
            lower_tolerance_percent=0.30,
            upper_tolerance_percent=0.30,
        )
        constraint_builder.add_ingredient_exclusion_constraint(self.excluded_product_ids)
        no_repeat_window = self._compute_variety_window()
        constraint_builder.add_recipe_variety_constraint(no_repeat_days=no_repeat_window)
        constraint_builder.add_meal_type_constraint()

        if self.selected_meal_types is not None:
            constraint_builder.add_dish_based_constraints()
        logger.info(f"[solver] Constraints built in {time.perf_counter() - t0:.3f}s")

        # --- Objective ---
        t0 = time.perf_counter()
        objective_builder = ObjectiveBuilder(
            model=model,
            recipes=self.recipes,
            recipe_vars=constraint_builder.get_recipe_vars(),
            servings_vars=constraint_builder.get_servings_vars(),
            days=self.days,
            target_calories=self.target_calories,
            target_protein=self.target_protein,
            target_carbs=self.target_carbs,
            target_fat=self.target_fat,
        )
        objective = objective_builder.build_objective()
        model.Minimize(objective)
        logger.info(f"[solver] Objective built in {time.perf_counter() - t0:.3f}s")

        # --- Model stats ---
        proto = model.Proto()
        logger.info(
            f"[solver] Model size: "
            f"{len(proto.variables)} variables, "
            f"{len(proto.constraints)} constraints"
        )

        # --- Solver configuration ---
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = float(self.timeout_seconds)
        solver.parameters.num_search_workers = 8
        solver.parameters.log_search_progress = True
        solver.parameters.cp_model_presolve = True

        # --- Solve ---
        logger.info(f"[solver] Starting CP-SAT solve (timeout={self.timeout_seconds}s) ...")
        t0 = time.perf_counter()
        status = solver.Solve(model)
        solve_time = time.perf_counter() - t0

        status_name = solver.StatusName(status)
        logger.info(
            f"[solver] Solve finished in {solve_time:.2f}s — "
            f"status={status_name}, "
            f"objective={solver.ObjectiveValue() if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else 'N/A'}, "
            f"wall_time={solver.WallTime():.2f}s"
        )

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            t0 = time.perf_counter()
            solution = self._extract_solution(
                solver,
                constraint_builder.get_recipe_vars(),
                constraint_builder.get_servings_vars(),
            )
            logger.info(f"[solver] Solution extracted in {time.perf_counter() - t0:.3f}s")

            # Validate dish-based constraints
            if self.selected_meal_types is not None:
                validation_error = self._validate_dish_based_solution(solution)
                if validation_error:
                    logger.error(f"[solver] Validation failed: {validation_error}")
                    return None, "error", validation_error

            # Log per-day calorie accuracy
            for day_key, day_data in solution.get("days", {}).items():
                total_cals = day_data.get("total_calories", 0)
                pct = (total_cals / self.target_calories * 100) if self.target_calories else 0
                recipes_summary = ", ".join(
                    r["recipe_name"] for r in day_data.get("recipes", [])
                )
                logger.info(
                    f"  {day_key}: {total_cals} kcal ({pct:.1f}%) — {recipes_summary}"
                )

            status_label = "optimal" if status == cp_model.OPTIMAL else "feasible"
            total_elapsed = time.perf_counter() - t_total
            logger.info(
                f"=== SOLVER DONE === status={status_label}, "
                f"total_elapsed={total_elapsed:.2f}s (solve={solve_time:.2f}s)"
            )
            return solution, status_label, None

        elif status == cp_model.INFEASIBLE:
            error_msg = self._analyze_infeasibility()
            logger.warning(
                f"=== SOLVER INFEASIBLE === elapsed={time.perf_counter() - t_total:.2f}s — {error_msg}"
            )
            return None, "infeasible", error_msg

        elif status == cp_model.MODEL_INVALID:
            logger.error("=== SOLVER MODEL INVALID ===")
            return None, "error", "Invalid model"

        else:
            logger.warning(
                f"=== SOLVER TIMEOUT === after {solve_time:.2f}s "
                f"(limit={self.timeout_seconds}s)"
            )
            return None, "timeout", f"Optimization timed out after {self.timeout_seconds} seconds"

    # ------------------------------------------------------------------
    # Variety window
    # ------------------------------------------------------------------

    def _compute_variety_window(self) -> int:
        """Compute the no-repeat window size based on available recipes.

        The window is set to the smallest recipe pool across the selected
        meal types (after ingredient exclusions), capped at the plan length.
        This prevents infeasibility while maximising forced variety.

        A window of N means each recipe must have at least N-1 clear days
        before it can appear again.
        """
        if not self.selected_meal_types:
            return min(3, self.days)

        # Build set of recipe indices that are excluded due to ingredients
        excluded_indices: set[int] = set()
        for idx, recipe in enumerate(self.recipes):
            for ing in recipe.recipe_ingredients:
                if str(ing.product_id) in self.excluded_product_ids:
                    excluded_indices.add(idx)
                    break

        # Find the meal type with the fewest eligible recipes
        min_available = self.days
        for meal_type in self.selected_meal_types:
            count = sum(
                1 for idx, r in enumerate(self.recipes)
                if meal_type in r.meal_types and idx not in excluded_indices
            )
            if count > 0:
                min_available = min(min_available, count)

        window = max(2, min(min_available, self.days))
        logger.info(
            f"Variety window: {window} days "
            f"(min recipes per meal type: {min_available}, plan days: {self.days})"
        )
        return window

    # ------------------------------------------------------------------
    # Solution extraction
    # ------------------------------------------------------------------

    def _extract_solution(
        self,
        solver: cp_model.CpSolver,
        recipe_vars: Dict[int, Dict[int, cp_model.IntVar]],
        servings_vars: Dict[int, Dict[int, cp_model.IntVar]],
    ) -> Dict[str, Any]:
        """Extract solution from solver into a result dictionary."""
        solution: Dict[str, Any] = {
            "days": {},
            "execution_time_s": solver.WallTime(),
        }

        for day in range(self.days):
            day_solution: Dict[str, Any] = {
                "recipes": [],
                "total_calories": 0,
                "total_protein_g": 0.0,
                "total_carbs_g": 0.0,
                "total_fat_g": 0.0,
            }

            for recipe_idx, recipe_var in recipe_vars[day].items():
                if solver.Value(recipe_var) != 1:
                    continue

                servings_raw = solver.Value(servings_vars[day][recipe_idx])

                # Dish-based: enforce exactly 1.0 serving
                if self.selected_meal_types is not None:
                    if servings_raw != 10:
                        logger.error(
                            f"Day {day + 1}, recipe {recipe_idx}: "
                            f"servings_vars={servings_raw} (expected 10)"
                        )
                    servings = 1.0
                else:
                    servings = servings_raw / 10.0

                if servings <= 0:
                    continue

                recipe = self.recipes[recipe_idx]
                nutrition = recipe.nutritional_info_per_serving

                day_solution["recipes"].append({
                    "recipe_id": str(recipe.id),
                    "recipe_name": recipe.name,
                    "meal_type": recipe.meal_types[0] if recipe.meal_types else "unknown",
                    "servings": servings,
                    "calories": int(nutrition.get("calories", 0) * servings),
                    "protein_g": float(nutrition.get("protein", 0) * servings),
                    "carbs_g": float(nutrition.get("carbs", 0) * servings),
                    "fat_g": float(nutrition.get("fat", 0) * servings),
                })

                day_solution["total_calories"] += int(nutrition.get("calories", 0) * servings)
                day_solution["total_protein_g"] += float(nutrition.get("protein", 0) * servings)
                day_solution["total_carbs_g"] += float(nutrition.get("carbs", 0) * servings)
                day_solution["total_fat_g"] += float(nutrition.get("fat", 0) * servings)

            solution["days"][f"day_{day + 1}"] = day_solution

        return solution

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_dish_based_solution(self, solution: Dict[str, Any]) -> Optional[str]:
        """Validate that solution meets dish-based constraints."""
        if self.selected_meal_types is None:
            return None

        expected_count = len(self.selected_meal_types)
        days_data = solution.get("days", {})

        for day_num in range(self.days):
            day_key = f"day_{day_num + 1}"
            day_data = days_data.get(day_key, {})
            recipes = day_data.get("recipes", [])

            if len(recipes) != expected_count:
                return (
                    f"Day {day_num + 1} has {len(recipes)} dishes, "
                    f"but expected exactly {expected_count} dishes"
                )

            for recipe in recipes:
                servings = recipe.get("servings", 0)
                if abs(servings - 1.0) > 0.01:
                    return (
                        f"Day {day_num + 1}, recipe '{recipe.get('recipe_name', 'unknown')}' "
                        f"has {servings} servings, but must be exactly 1.0"
                    )

        return None

    # ------------------------------------------------------------------
    # Infeasibility analysis
    # ------------------------------------------------------------------

    def _analyze_infeasibility(self) -> str:
        """Analyze why the problem is infeasible and return a helpful message."""
        if self.selected_meal_types is not None:
            expected_count = len(self.selected_meal_types)

            # Check recipe availability per meal type
            for meal_type in self.selected_meal_types:
                count = sum(
                    1 for r in self.recipes
                    if meal_type in r.meal_types
                    and not any(
                        str(ing.product_id) in self.excluded_product_ids
                        for ing in r.recipe_ingredients
                    )
                )
                if count == 0:
                    return (
                        f"No recipes available for meal type '{meal_type}'. "
                        f"Please add recipes with this meal type or deselect it."
                    )

            # Check if calorie target is reachable with single servings
            max_total = 0
            details = []
            for meal_type in self.selected_meal_types:
                max_cal = max(
                    (r.nutritional_info_per_serving.get("calories", 0)
                     for r in self.recipes if meal_type in r.meal_types),
                    default=0,
                )
                max_total += max_cal
                details.append(f"{meal_type}: max {max_cal:.0f} cal")

            lower_bound = self.target_calories * 0.90
            if max_total < lower_bound:
                return (
                    f"Cannot meet calorie target of {self.target_calories} kcal "
                    f"with {expected_count} dishes per day. "
                    f"Maximum possible: {max_total:.0f} kcal. "
                    f"Details: {', '.join(details)}. "
                    f"Try adding more meal types or reducing the calorie target."
                )

            # Macro constraints may be too strict
            if self.target_protein or self.target_carbs or self.target_fat:
                return (
                    "Constraints are unsatisfiable. "
                    "Macro constraints (protein/carbs/fat) may be too strict "
                    "when combined with calorie targets and available recipes. "
                    "Try adjusting macro targets or calorie target."
                )

        # Generic fallback
        if self.target_calories < 800 or self.target_calories > 5000:
            return f"Calorie target {self.target_calories} is outside reasonable range (800-5000)"

        return (
            "Constraints are unsatisfiable. "
            "Try relaxing dietary restrictions or calorie targets."
        )
