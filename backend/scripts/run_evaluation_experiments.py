#!/usr/bin/env python3
"""
Thesis evaluation: run solver under several scenarios and record feasibility,
solve time, and objective value. Outputs JSON and a short summary for the thesis.

Run from backend directory: python scripts/run_evaluation_experiments.py
Requires: backend/data/recipes/sample-recipes.json (or recipes-new-meal-types.json
          with nutritional_info_per_serving if present).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from uuid import uuid4

# Add backend to path
backend = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend))

from src.services.optimization.solver import OptimizationSolver


class MockProduct:
    def __init__(self, name: str, nutritional_info: dict):
        self.id = uuid4()
        self.name = name
        self.nutritional_info_per_100g = nutritional_info


class MockRecipeIngredient:
    def __init__(self, product_id, quantity_value: float, quantity_unit: str = "g"):
        self.product_id = product_id
        self.quantity_value = quantity_value
        self.quantity_unit = quantity_unit
        self.product = None


class MockRecipe:
    def __init__(
        self,
        name: str,
        nutritional_info: dict,
        meal_types: list[str] | None = None,
        ingredients: list | None = None,
        total_servings: float = 1.0,
    ):
        self.id = uuid4()
        self.name = name
        self.nutritional_info_per_serving = nutritional_info or {}
        self.meal_types = meal_types or ["breakfast", "dinner", "supper"]
        self.recipe_ingredients = ingredients or []
        self.total_servings = total_servings


def load_recipes_from_json(recipes_path: Path, limit: int = 200) -> tuple[list, list]:
    """Load recipes and products from JSON; returns (recipes, products)."""
    if not recipes_path.exists():
        return [], []

    with open(recipes_path) as f:
        data = json.load(f)
    if isinstance(data, dict) and "recipes" in data:
        recipes_data = data["recipes"]
    else:
        recipes_data = data if isinstance(data, list) else []

    products_dict: dict = {}
    recipes = []

    for recipe_data in recipes_data[:limit]:
        ingredients = []
        for ing in recipe_data.get("ingredients", []):
            name = ing.get("product_name", "Unknown")
            if name not in products_dict:
                products_dict[name] = MockProduct(
                    name=name,
                    nutritional_info={
                        "calories": 100.0,
                        "protein": 10.0,
                        "carbs": 10.0,
                        "fat": 5.0,
                    },
                )
            prod = products_dict[name]
            ing_obj = MockRecipeIngredient(
                product_id=str(prod.id),
                quantity_value=float(ing.get("quantity", 100)),
                quantity_unit=ing.get("unit", "g"),
            )
            ing_obj.product = prod
            ingredients.append(ing_obj)

        nutr = recipe_data.get("nutritional_info_per_serving") or {
            "calories": 500,
            "protein": 25,
            "carbs": 50,
            "fat": 20,
        }
        if not isinstance(nutr, dict):
            nutr = {"calories": 500, "protein": 25, "carbs": 50, "fat": 20}
        meal_types = recipe_data.get("meal_types", ["breakfast", "dinner", "supper"])
        if not meal_types:
            meal_types = ["dinner"]
        r = MockRecipe(
            name=recipe_data.get("name", "Recipe"),
            nutritional_info=nutr,
            meal_types=meal_types,
            ingredients=ingredients,
            total_servings=float(recipe_data.get("total_servings", 1.0)),
        )
        recipes.append(r)

    return recipes, list(products_dict.values())


def run_scenario(
    recipes: list,
    products: list,
    days: int,
    target_calories: int,
    target_protein: float | None,
    target_carbs: float | None,
    target_fat: float | None,
    selected_meal_types: list[str],
    timeout_seconds: int,
) -> dict:
    """Run one solver scenario; return dict with status, time_s, objective, error."""
    solver = OptimizationSolver(
        recipes=recipes,
        products=products,
        days=days,
        target_calories=target_calories,
        target_protein=target_protein,
        target_carbs=target_carbs,
        target_fat=target_fat,
        excluded_product_ids=[],
        timeout_seconds=timeout_seconds,
        selected_meal_types=selected_meal_types,
    )
    t0 = time.perf_counter()
    solution, status, error_message = solver.solve()
    elapsed = time.perf_counter() - t0

    objective = None
    if solution is not None and status in ("optimal", "feasible"):
        # Solver doesn't return objective in solution dict; we only have elapsed time
        objective = "N/A (see solver logs for objective value)"

    return {
        "status": status,
        "time_s": round(elapsed, 3),
        "objective": objective,
        "error_message": error_message,
        "feasible": status in ("optimal", "feasible"),
    }


def main() -> None:
    data_dir = backend / "data" / "recipes"
    recipes_file = data_dir / "sample-recipes.json"
    if not recipes_file.exists():
        recipes_file = data_dir / "recipes-new-meal-types.json"
    if not recipes_file.exists():
        print("No recipe JSON found in backend/data/recipes/; skipping experiments.")
        return

    recipes, products = load_recipes_from_json(recipes_file, limit=150)
    if len(recipes) < 10:
        print("Too few recipes loaded; need at least 10.")
        return

    print(f"Loaded {len(recipes)} recipes, {len(products)} products from {recipes_file.name}")

    # Infer meal types present in recipe set
    meal_type_counts: dict[str, int] = {}
    for r in recipes:
        for mt in r.meal_types:
            meal_type_counts[mt] = meal_type_counts.get(mt, 0) + 1
    all_meal_types = sorted(meal_type_counts.keys())
    three_meal_types = [t for t in ["breakfast", "dinner", "supper"] if t in meal_type_counts]
    if not three_meal_types:
        three_meal_types = all_meal_types[:3] if len(all_meal_types) >= 3 else all_meal_types

    scenarios = [
        {
            "id": "baseline_7d_2000_5meals",
            "days": 7,
            "target_calories": 2000,
            "target_protein": 150.0,
            "target_carbs": 200.0,
            "target_fat": 67.0,
            "selected_meal_types": all_meal_types,
            "timeout_seconds": 60,
        },
        {
            "id": "7d_1800_5meals",
            "days": 7,
            "target_calories": 1800,
            "target_protein": None,
            "target_carbs": None,
            "target_fat": None,
            "selected_meal_types": all_meal_types,
            "timeout_seconds": 60,
        },
        {
            "id": "7d_2200_5meals",
            "days": 7,
            "target_calories": 2200,
            "target_protein": None,
            "target_carbs": None,
            "target_fat": None,
            "selected_meal_types": all_meal_types,
            "timeout_seconds": 60,
        },
        {
            "id": "5d_2000_5meals",
            "days": 5,
            "target_calories": 2000,
            "target_protein": 150.0,
            "target_carbs": 200.0,
            "target_fat": 67.0,
            "selected_meal_types": all_meal_types,
            "timeout_seconds": 60,
        },
        {
            "id": "7d_2000_3meals",
            "days": 7,
            "target_calories": 2000,
            "target_protein": None,
            "target_carbs": None,
            "target_fat": None,
            "selected_meal_types": three_meal_types,
            "timeout_seconds": 60,
        },
        {
            "id": "7d_2000_5meals_timeout30",
            "days": 7,
            "target_calories": 2000,
            "target_protein": 150.0,
            "target_carbs": 200.0,
            "target_fat": 67.0,
            "selected_meal_types": all_meal_types,
            "timeout_seconds": 30,
        },
    ]

    results = []
    for sc in scenarios:
        r = run_scenario(
            recipes=recipes,
            products=products,
            days=sc["days"],
            target_calories=sc["target_calories"],
            target_protein=sc.get("target_protein"),
            target_carbs=sc.get("target_carbs"),
            target_fat=sc.get("target_fat"),
            selected_meal_types=sc["selected_meal_types"],
            timeout_seconds=sc["timeout_seconds"],
        )
        row = {"scenario_id": sc["id"], **sc, **r}
        results.append(row)
        print(f"  {sc['id']}: status={r['status']}, time_s={r['time_s']}, feasible={r['feasible']}")

    feasible_count = sum(1 for r in results if r["feasible"])
    times = [r["time_s"] for r in results if r["feasible"]]
    summary = {
        "n_scenarios": len(results),
        "feasible_count": feasible_count,
        "feasibility_rate": round(feasible_count / len(results), 2) if results else 0,
        "solve_time_s_median": round(sorted(times)[len(times) // 2], 2) if times else None,
        "solve_time_s_max": round(max(times), 2) if times else None,
    }

    out_dir = backend.parent / "docs" / "thesis"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "evaluation_results.json"
    with open(out_json, "w") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)
    print(f"\nWrote {out_json}")
    print("Summary:", summary)


if __name__ == "__main__":
    main()
