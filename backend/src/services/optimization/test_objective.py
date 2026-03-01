#!/usr/bin/env python3
"""Local test script for ObjectiveBuilder."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from ortools.sat.python import cp_model
from uuid import uuid4
from typing import Dict, List

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

def test_objective_builder():
    """Test ObjectiveBuilder with simple data."""
    print("🧪 Testing ObjectiveBuilder...")
    
    from src.services.optimization.objective import ObjectiveBuilder
    
    # Create a simple model
    model = cp_model.CpModel()
    
    # Create mock products
    products = [
        MockProduct("Chicken", "prod1"),
        MockProduct("Rice", "prod2"),
        MockProduct("Broccoli", "prod3"),
    ]
    
    # Create mock recipes
    recipes = [
        MockRecipe(
            "Chicken and Rice",
            [
                MockIngredient("prod1", 150.0, "g"),
                MockIngredient("prod2", 100.0, "g"),
            ],
            {"calories": 450, "protein": 35, "carbs": 45, "fat": 12}
        ),
        MockRecipe(
            "Chicken and Broccoli",
            [
                MockIngredient("prod1", 120.0, "g"),
                MockIngredient("prod3", 150.0, "g"),
            ],
            {"calories": 320, "protein": 38, "carbs": 20, "fat": 10}
        ),
    ]
    
    # Create recipe and servings variables (simplified)
    days = 2
    recipe_vars: Dict[int, Dict[int, cp_model.IntVar]] = {}
    servings_vars: Dict[int, Dict[int, cp_model.IntVar]] = {}
    
    for day in range(days):
        recipe_vars[day] = {}
        servings_vars[day] = {}
        for recipe_idx in range(len(recipes)):
            recipe_vars[day][recipe_idx] = model.NewBoolVar(f"recipe_d{day}_r{recipe_idx}")
            servings_vars[day][recipe_idx] = model.NewIntVar(0, 100, f"servings_d{day}_r{recipe_idx}")
    
    # Create ObjectiveBuilder
    try:
        builder = ObjectiveBuilder(
            model=model,
            recipes=recipes,
            products=products,
            recipe_vars=recipe_vars,
            servings_vars=servings_vars,
            days=days,
        )
        print("✅ ObjectiveBuilder initialized successfully")
        
        # Test building the objective
        try:
            objective = builder.build_waste_minimization_objective()
            print(f"✅ Objective built successfully: {objective}")
            print(f"   Objective name: {objective.Name()}")
            print(f"   Objective bounds: [{objective.Proto().domain[0]}, {objective.Proto().domain[1]}]")
        except Exception as e:
            print(f"❌ Error building objective: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test with a simple solver
        try:
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = 5.0
            
            # Add some simple constraints
            # At least one recipe per day
            for day in range(days):
                model.Add(sum(recipe_vars[day].values()) >= 1)
            
            # Minimize the objective
            model.Minimize(objective)
            
            print("✅ Model constraints added, solving...")
            status = solver.Solve(model)
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                print(f"✅ Solution found! Status: {status}")
                print(f"   Objective value: {solver.Value(objective)}")
                print(f"   Wall time: {solver.WallTime():.2f}s")
                
                # Show selected recipes
                for day in range(days):
                    print(f"\n   Day {day + 1}:")
                    for recipe_idx, recipe_var in recipe_vars[day].items():
                        if solver.Value(recipe_var) == 1:
                            servings = solver.Value(servings_vars[day][recipe_idx]) / 10.0
                            print(f"     - {recipes[recipe_idx].name}: {servings:.1f} servings")
                return True
            else:
                print(f"⚠️  No solution found. Status: {status}")
                return False
                
        except Exception as e:
            print(f"❌ Error solving: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error creating ObjectiveBuilder: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_constraint_builder():
    """Test ConstraintBuilder with simple data."""
    print("\n🧪 Testing ConstraintBuilder...")
    
    from src.services.optimization.constraints import ConstraintBuilder
    
    # Create a simple model
    model = cp_model.CpModel()
    
    # Create mock recipes
    recipes = [
        MockRecipe(
            "Breakfast Oatmeal",
            [MockIngredient("prod1", 80.0)],
            {"calories": 350, "protein": 12, "carbs": 65, "fat": 7},
            meal_types=["breakfast"]
        ),
        MockRecipe(
            "Lunch Salad",
            [MockIngredient("prod2", 150.0)],
            {"calories": 450, "protein": 45, "carbs": 20, "fat": 22},
            meal_types=["lunch"]
        ),
        MockRecipe(
            "Dinner Pasta",
            [MockIngredient("prod3", 200.0)],
            {"calories": 600, "protein": 35, "carbs": 75, "fat": 18},
            meal_types=["dinner"]
        ),
    ]
    
    try:
        builder = ConstraintBuilder(
            model=model,
            recipes=recipes,
            days=2,
            target_calories=2000,
            target_protein=70.0,
            target_carbs=None,
            target_fat=54.0,
        )
        print("✅ ConstraintBuilder initialized successfully")
        
        # Test adding constraints
        try:
            builder.add_calorie_constraint(tolerance_percent=0.05)
            print("✅ Calorie constraint added")
            
            builder.add_macro_constraints(tolerance_percent=0.10)
            print("✅ Macro constraints added")
            
            builder.add_meal_type_constraint()
            print("✅ Meal type constraint added")
            
            # Get variables
            recipe_vars = builder.get_recipe_vars()
            servings_vars = builder.get_servings_vars()
            print(f"✅ Variables retrieved: {len(recipe_vars)} days, {len(servings_vars)} days")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding constraints: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error creating ConstraintBuilder: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Optimization Components")
    print("=" * 60)
    
    success1 = test_constraint_builder()
    success2 = test_objective_builder()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
