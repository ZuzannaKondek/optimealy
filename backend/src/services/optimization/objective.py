"""Objective function for dish-based meal plan optimization.

Minimizes deviation from calorie and macro targets, with a small
variety tiebreaker to prefer diverse recipe selections.
"""

from typing import List, Dict, Optional
import logging
from ortools.sat.python import cp_model

from src.models.recipe import Recipe

logger = logging.getLogger(__name__)

# Objective weights — calorie deviation is the dominant term.
# Calorie values are ~2000 scale, macros ~50-250g scale.
# Weight 10 on calories makes it ~proportionally dominant.
CALORIE_DEVIATION_WEIGHT = 10
PROTEIN_DEVIATION_WEIGHT = 1
CARBS_DEVIATION_WEIGHT = 1
FAT_DEVIATION_WEIGHT = 1

# Variety penalty: cost per extra day a recipe is reused beyond its first use.
# Sized as a meaningful tiebreaker (~5-10 % of typical calorie deviation)
# without overriding nutritional accuracy.
VARIETY_REUSE_PENALTY = 200


class ObjectiveBuilder:
    """Build a deviation-minimizing objective for dish-based planning."""

    def __init__(
        self,
        model: cp_model.CpModel,
        recipes: List[Recipe],
        recipe_vars: Dict[int, Dict[int, cp_model.IntVar]],
        servings_vars: Dict[int, Dict[int, cp_model.IntVar]],
        days: int,
        target_calories: int,
        target_protein: Optional[float] = None,
        target_carbs: Optional[float] = None,
        target_fat: Optional[float] = None,
    ):
        self.model = model
        self.recipes = recipes
        self.recipe_vars = recipe_vars
        self.servings_vars = servings_vars
        self.days = days
        self.target_calories = target_calories
        self.target_protein = target_protein
        self.target_carbs = target_carbs
        self.target_fat = target_fat

    def build_objective(self) -> cp_model.IntVar:
        """Build and return the objective variable to minimize.

        The objective is the weighted sum of per-day absolute deviations
        from calorie and macro targets, plus a variety penalty that
        discourages reusing the same recipe across multiple days.

        Returns:
            An IntVar representing the total weighted deviation to minimize.
        """
        day_deviations: List[cp_model.IntVar] = []

        for day in range(self.days):
            day_dev = self._build_day_deviation(day)
            day_deviations.append(day_dev)

        # Variety penalty: discourage reusing the same recipe on many days.
        variety_penalty = self._build_variety_penalty()

        # Sum all daily deviations + variety penalty into a single objective.
        num_recipes = len(self.recipes)
        max_possible = (
            self.days * self._estimate_max_deviation()
            + num_recipes * self.days * VARIETY_REUSE_PENALTY
        )
        total_objective = self.model.NewIntVar(0, max_possible, "total_objective")
        self.model.Add(total_objective == sum(day_deviations) + variety_penalty)

        return total_objective

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_day_deviation(self, day: int) -> cp_model.IntVar:
        """Compute weighted deviation for a single day.

        Returns an IntVar equal to the weighted sum of calorie + macro
        deviations for *day*.
        """
        components: List[cp_model.IntVar] = []

        # --- Calorie deviation (always present) ---
        cal_dev = self._absolute_deviation_for_nutrient(
            day=day,
            nutrient_key="calories",
            target=self.target_calories,
            weight=CALORIE_DEVIATION_WEIGHT,
            label="cal",
        )
        components.append(cal_dev)

        # --- Macro deviations (optional) ---
        if self.target_protein is not None:
            components.append(self._absolute_deviation_for_nutrient(
                day=day,
                nutrient_key="protein",
                target=self.target_protein,
                weight=PROTEIN_DEVIATION_WEIGHT,
                label="prot",
            ))

        if self.target_carbs is not None:
            components.append(self._absolute_deviation_for_nutrient(
                day=day,
                nutrient_key="carbs",
                target=self.target_carbs,
                weight=CARBS_DEVIATION_WEIGHT,
                label="carbs",
            ))

        if self.target_fat is not None:
            components.append(self._absolute_deviation_for_nutrient(
                day=day,
                nutrient_key="fat",
                target=self.target_fat,
                weight=FAT_DEVIATION_WEIGHT,
                label="fat",
            ))

        # Combine into a single day-level variable.
        max_day_dev = self._estimate_max_deviation()
        day_dev = self.model.NewIntVar(0, max_day_dev, f"day_{day}_deviation")
        self.model.Add(day_dev == sum(components))
        return day_dev

    def _build_variety_penalty(self) -> cp_model.IntVar:
        """Build a penalty term that discourages recipe reuse across days.

        For each recipe the first use is free; every additional day it
        appears adds ``VARIETY_REUSE_PENALTY`` to the objective.  This
        nudges the solver toward more diverse plans when multiple recipes
        have similar nutritional profiles.
        """
        num_recipes = len(self.recipes)
        reuse_vars: List[cp_model.IntVar] = []

        for recipe_idx in range(num_recipes):
            total_usage = sum(
                self.recipe_vars[day][recipe_idx] for day in range(self.days)
            )
            # reuse_r = max(0, usage - 1).  Since we minimise, the solver
            # will push reuse_r to its lower bound automatically.
            reuse = self.model.NewIntVar(0, self.days, f"reuse_{recipe_idx}")
            self.model.Add(reuse >= total_usage - 1)
            reuse_vars.append(reuse)

        max_penalty = num_recipes * self.days * VARIETY_REUSE_PENALTY
        penalty = self.model.NewIntVar(0, max_penalty, "variety_penalty")

        if reuse_vars:
            self.model.Add(penalty == VARIETY_REUSE_PENALTY * sum(reuse_vars))
        else:
            self.model.Add(penalty == 0)

        return penalty

    def _absolute_deviation_for_nutrient(
        self,
        day: int,
        nutrient_key: str,
        target: float,
        weight: int,
        label: str,
    ) -> cp_model.IntVar:
        """Model weighted |actual - target| for one nutrient on one day.

        Uses the standard CP-SAT absolute-value pattern:
            dev >= actual - target
            dev >= target - actual

        All values are in the *scaled* domain (×10) to match servings_vars.
        The returned variable is ``weight * dev``.
        """
        # Build the expression: sum of (servings_vars * nutrient_per_serving)
        # servings_vars is scaled ×10, so the sum is also ×10.
        contributions = []
        for recipe_idx, recipe in enumerate(self.recipes):
            nutrient_per_serving = recipe.nutritional_info_per_serving.get(nutrient_key, 0)
            if nutrient_per_serving <= 0:
                continue
            coeff = round(nutrient_per_serving)  # round, not truncate
            contributions.append(self.servings_vars[day][recipe_idx] * coeff)

        # Target in scaled domain.
        target_scaled = round(target * 10)

        # Upper bound for the nutrient sum (all recipes at max servings).
        max_nutrient = sum(
            round(r.nutritional_info_per_serving.get(nutrient_key, 0)) * 100
            for r in self.recipes
        )

        actual_var = self.model.NewIntVar(0, max(max_nutrient, 1), f"actual_{label}_day_{day}")
        if contributions:
            self.model.Add(actual_var == sum(contributions))
        else:
            self.model.Add(actual_var == 0)

        # Absolute deviation: dev >= |actual - target_scaled|
        # dev can be at most max(max_nutrient, target_scaled)
        max_dev = max(max_nutrient, target_scaled)
        dev = self.model.NewIntVar(0, max_dev, f"dev_{label}_day_{day}")
        self.model.Add(dev >= actual_var - target_scaled)
        self.model.Add(dev >= target_scaled - actual_var)

        # Weighted deviation
        weighted = self.model.NewIntVar(0, max_dev * weight, f"wdev_{label}_day_{day}")
        self.model.Add(weighted == dev * weight)

        return weighted

    def _estimate_max_deviation(self) -> int:
        """Conservative upper bound for total deviation across all components."""
        # Calorie deviation upper bound: target × 10 (scaled) × weight
        cal_max = self.target_calories * 10 * CALORIE_DEVIATION_WEIGHT

        macro_max = 0
        if self.target_protein is not None:
            macro_max += round(self.target_protein * 10) * PROTEIN_DEVIATION_WEIGHT
        if self.target_carbs is not None:
            macro_max += round(self.target_carbs * 10) * CARBS_DEVIATION_WEIGHT
        if self.target_fat is not None:
            macro_max += round(self.target_fat * 10) * FAT_DEVIATION_WEIGHT

        return cal_max + macro_max
