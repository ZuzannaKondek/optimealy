#!/usr/bin/env python3
"""Local test script for optimization algorithm - test until calories are correct."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ortools.sat.python import cp_model
from uuid import uuid4
from typing import Dict, List
import json

# Mock models for testing
class MockProduct:
    def __init__(self, name: str, product_id: str = None):
        self.id = product_id or uuid4()
        self.name = name
        self.perishability = "moderate"

class MockIngredient:
    def __init__(self, product_id: str, quantity_value: float, quantity_unit: str = "g"):
        self.product_id = product_id
        self.quantity_value = quantity_value
        self.quantity_unit = quantity_unit

class MockRecipe:
    def __init__(self, name: str, ingredients: List[MockIngredient], nutritional_info: Dict, meal_types: List[str] = None):
        self.id = uuid4()
        self.name = name
        self.recipe_ingredients = ingredients
        self.nutritional_info_per_serving = nutritional_info
        self.meal_types = meal_types or ["lunch", "dinner"]


def load_recipes_from_json() -> List[MockRecipe]:
    """Load recipes from sample-recipes.json file."""
    data_dir = Path(__file__).parent / "data" / "recipes"
    recipes_file = data_dir / "sample-recipes.json"
    
    if not recipes_file.exists():
        raise FileNotFoundError(f"Recipes file not found: {recipes_file}")
    
    with open(recipes_file, 'r') as f:
        recipes_data = json.load(f)
    
    # Create a simple product lookup (we'll use product names as IDs for testing)
    product_names = set()
    for recipe_data in recipes_data:
        for ingredient in recipe_data.get("ingredients", []):
            product_names.add(ingredient.get("product_name", "unknown"))
    
    product_lookup = {name: str(uuid4()) for name in product_names}
    
    recipes = []
    for recipe_data in recipes_data:
        # Create mock ingredients
        ingredients = []
        for ing_data in recipe_data.get("ingredients", []):
            product_name = ing_data.get("product_name", "unknown")
            product_id = product_lookup.get(product_name, str(uuid4()))
            ingredients.append(MockIngredient(
                product_id=product_id,
                quantity_value=float(ing_data.get("quantity", 0)),
                quantity_unit=ing_data.get("unit", "g")
            ))
        
        # Create mock recipe
        recipe = MockRecipe(
            name=recipe_data["name"],
            ingredients=ingredients,
            nutritional_info=recipe_data.get("nutritional_info_per_serving", {}),
            meal_types=recipe_data.get("meal_types", [])
        )
        recipes.append(recipe)
    
    return recipes, [MockProduct(name, pid) for name, pid in product_lookup.items()]

def test_optimization_with_calorie_constraint():
    """Test the full optimization with calorie constraint."""
    print("=" * 60)
    print("Testing Full Optimization with Calorie Constraint")
    print("=" * 60)
    
    from src.services.optimization.constraints import ConstraintBuilder
    from src.services.optimization.objective import ObjectiveBuilder
    from src.services.optimization.solver import OptimizationSolver
    
    # Load recipes from JSON file
    print("📂 Loading recipes from sample-recipes.json...")
    try:
        recipes, products = load_recipes_from_json()
        print(f"✅ Loaded {len(recipes)} recipes and {len(products)} products")
        
        # Show some recipe info
        print("\n📋 Sample recipes:")
        for i, recipe in enumerate(recipes[:5]):
            calories = recipe.nutritional_info_per_serving.get("calories", 0)
            meal_types = ", ".join(recipe.meal_types) if recipe.meal_types else "none"
            print(f"  {i+1}. {recipe.name}: {calories} cal ({meal_types})")
        
    except Exception as e:
        print(f"❌ Failed to load recipes: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test with target of 2000 calories
    target_calories = 2000
    days = 2
    
    print(f"\nTarget: {target_calories} calories per day for {days} days")
    print(f"Available recipes: {len(recipes)}")
    
    # Check recipe distribution by meal type
    meal_type_counts = {}
    for recipe in recipes:
        for meal_type in recipe.meal_types:
            meal_type_counts[meal_type] = meal_type_counts.get(meal_type, 0) + 1
    print(f"Recipe distribution by meal type: {meal_type_counts}")
    
    try:
        # Create solver
        solver_obj = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=days,
            target_calories=target_calories,
            target_protein=70.0,
            target_carbs=None,
            target_fat=54.0,
            excluded_product_ids=[],
            timeout_seconds=30,
        )
        
        print("\n🧪 Running optimization...")
        solution, status, error_message = solver_obj.solve()
        
        if solution is None:
            print(f"❌ Optimization failed: {status}")
            if error_message:
                print(f"   Error: {error_message}")
            return False
        
        print(f"✅ Optimization completed with status: {status}")
        print(f"   Execution time: {solution.get('execution_time_s', 0):.2f}s")
        
        # Check results
        all_good = True
        for day_key, day_data in solution.get("days", {}).items():
            total_cals = day_data.get("total_calories", 0)
            total_protein = day_data.get("total_protein_g", 0)
            total_fat = day_data.get("total_fat_g", 0)
            recipes_list = day_data.get("recipes", [])
            
            percent_of_target = (total_cals / target_calories * 100) if target_calories > 0 else 0
            
            print(f"\n📅 {day_key.upper()}:")
            print(f"   Calories: {total_cals} / {target_calories} ({percent_of_target:.1f}%)")
            print(f"   Protein: {total_protein:.1f}g")
            print(f"   Fat: {total_fat:.1f}g")
            print(f"   Recipes selected: {len(recipes_list)}")
            
            for recipe_data in recipes_list:
                print(f"     - {recipe_data['recipe_name']}: {recipe_data['servings']:.2f} servings "
                      f"({recipe_data['calories']} cal)")
            
            # Check if calories are reasonable (within 90-110% of target)
            if total_cals < target_calories * 0.9:
                print(f"   ⚠️  WARNING: Calories too low! Expected ~{target_calories}, got {total_cals}")
                all_good = False
            elif total_cals > target_calories * 1.1:
                print(f"   ⚠️  WARNING: Calories too high! Expected ~{target_calories}, got {total_cals}")
                all_good = False
            else:
                print(f"   ✅ Calories are within acceptable range")
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_constraint_directly():
    """Test the constraint builder directly to see what's happening."""
    print("\n" + "=" * 60)
    print("Testing Constraint Builder Directly")
    print("=" * 60)
    
    from src.services.optimization.constraints import ConstraintBuilder
    
    model = cp_model.CpModel()
    
    # Use recipes with enough calories to meet target
    # Target is 2000, so we need recipes that can sum to ~2000
    recipes = [
        MockRecipe("Breakfast", [MockIngredient("p1", 100)], {"calories": 400}, ["breakfast"]),
        MockRecipe("Lunch", [MockIngredient("p2", 150)], {"calories": 600}, ["lunch"]),
        MockRecipe("Dinner", [MockIngredient("p3", 200)], {"calories": 800}, ["dinner"]),
        # Add more options
        MockRecipe("Breakfast2", [MockIngredient("p4", 120)], {"calories": 500}, ["breakfast"]),
        MockRecipe("Lunch2", [MockIngredient("p5", 180)], {"calories": 700}, ["lunch"]),
        MockRecipe("Dinner2", [MockIngredient("p6", 250)], {"calories": 900}, ["dinner"]),
    ]
    
    target_calories = 2000
    
    builder = ConstraintBuilder(
        model=model,
        recipes=recipes,
        days=1,
        target_calories=target_calories,
        target_protein=70.0,
        target_carbs=None,
        target_fat=54.0,
    )
    
    print(f"Testing with {len(recipes)} recipes, target: {target_calories} calories")
    
    # Test calorie constraint only first
    print("\n1. Testing calorie constraint only...")
    print(f"   Target: {target_calories} calories")
    print(f"   Lower bound (90%): {target_calories * 0.9}")
    print(f"   Upper bound (110%): {target_calories * 1.1}")
    builder.add_calorie_constraint(tolerance_percent=0.10)  # Use 10% tolerance for testing
    
    # Get variables
    recipe_vars = builder.get_recipe_vars()
    servings_vars = builder.get_servings_vars()
    
    # Add a simple objective (minimize servings to test constraint)
    total_servings = []
    for day in range(1):
        for recipe_idx in range(len(recipes)):
            total_servings.append(servings_vars[day][recipe_idx])
    
    model.Minimize(sum(total_servings))
    
    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    status = solver.Solve(model)
    
    print(f"Solver status: {status} (OPTIMAL=4, FEASIBLE=2, INFEASIBLE=3)")
    
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("\n✅ Solution found with calorie constraint only!")
        total_cals = 0
        selected = []
        for recipe_idx in range(len(recipes)):
            if solver.Value(recipe_vars[0][recipe_idx]) == 1:
                servings = solver.Value(servings_vars[0][recipe_idx]) / 10.0
                calories = recipes[recipe_idx].nutritional_info_per_serving["calories"] * servings
                total_cals += calories
                selected.append((recipes[recipe_idx].name, servings, calories))
                print(f"  {recipes[recipe_idx].name}: {servings:.2f} servings = {calories:.0f} cal")
        
        print(f"\nTotal calories: {total_cals} / {target_calories} ({total_cals/target_calories*100:.1f}%)")
        
        if total_cals < target_calories * 0.9:
            print("❌ Calories too low!")
            return False
        elif total_cals > target_calories * 1.1:
            print("❌ Calories too high!")
            return False
        else:
            print("✅ Calories are correct!")
            return True
    else:
        print(f"❌ No solution found with calorie constraint only. Status: {status}")
        print("   This suggests the calorie constraint logic has an issue.")
        return False


if __name__ == "__main__":
    print("Testing Optimization Algorithm Locally")
    print("=" * 60)
    
    # First test the constraint directly
    constraint_ok = test_constraint_directly()
    
    if constraint_ok:
        # Then test the full optimization
        optimization_ok = test_optimization_with_calorie_constraint()
        
        if optimization_ok:
            print("\n" + "=" * 60)
            print("✅ All tests passed! Optimization is working correctly.")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("❌ Optimization test failed. Need to fix the algorithm.")
            print("=" * 60)
            sys.exit(1)
    else:
        print("\n" + "=" * 60)
        print("❌ Constraint test failed. Need to fix constraints first.")
        print("=" * 60)
        sys.exit(1)
