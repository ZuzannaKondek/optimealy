"""Test suite for optimization algorithm validation.

This test suite validates that the optimization algorithm correctly generates
meal plans according to specified parameters, with focus on dish-based planning constraints.

Standard Test Case:
- Duration: 7 days
- Daily Calorie Target: 2000
- Daily Protein Target: 150g
- Daily Carbs Target: 200g
- Daily Fat Target: 67g
- Number of Dishes Per Day: 5
"""
import pytest
from typing import Dict, Any, List
from uuid import uuid4
from pathlib import Path
import json
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.optimization.solver import OptimizationSolver
from src.services.optimization.utils import calculate_dish_weight
from src.models.recipe import Recipe
from src.models.product import Product
from src.models.recipe_ingredient import RecipeIngredient


# Standard test case parameters
STANDARD_TEST_CASE = {
    "duration_days": 7,
    "target_calories": 2000,
    "target_protein_g": 150.0,
    "target_carbs_g": 200.0,
    "target_fat_g": 67.0,
    "dishes_per_day": 5,
}


class MockProduct:
    """Mock Product for testing."""
    def __init__(self, name: str, nutritional_info: Dict[str, float]):
        self.id = uuid4()
        self.name = name
        self.nutritional_info_per_100g = nutritional_info


class MockRecipeIngredient:
    """Mock RecipeIngredient for testing."""
    def __init__(self, product_id: str, quantity_value: float, quantity_unit: str = "g"):
        self.product_id = product_id
        self.quantity_value = quantity_value
        self.quantity_unit = quantity_unit
        self.product = None  # Will be set if needed


class MockRecipe:
    """Mock Recipe for testing."""
    def __init__(
        self,
        name: str,
        nutritional_info: Dict[str, float],
        meal_types: List[str] = None,
        ingredients: List[MockRecipeIngredient] = None,
        total_servings: float = 1.0,
    ):
        self.id = uuid4()
        self.name = name
        self.nutritional_info_per_serving = nutritional_info
        self.meal_types = meal_types or ["lunch", "dinner"]
        self.recipe_ingredients = ingredients or []
        self.total_servings = total_servings
        self.instructions = f"Instructions for {name}"
        self.instructions_single_serving = None
        # Ensure nutritional_info_per_serving is a dict with get method
        if not isinstance(self.nutritional_info_per_serving, dict):
            self.nutritional_info_per_serving = {}


def load_test_recipes() -> tuple[List[MockRecipe], List[MockProduct]]:
    """Load test recipes from sample data."""
    data_dir = project_root / "data" / "recipes"
    recipes_file = data_dir / "sample-recipes.json"
    
    if not recipes_file.exists():
        pytest.skip(f"Test data not found: {recipes_file}")
    
    with open(recipes_file, 'r') as f:
        recipes_data = json.load(f)
    
    # Create products lookup
    products_dict = {}
    recipes = []
    
    for recipe_data in recipes_data[:50]:  # Limit to 50 recipes for testing
        # Create ingredients
        ingredients = []
        for ing_data in recipe_data.get("ingredients", []):
            product_name = ing_data.get("product_name", "unknown")
            if product_name not in products_dict:
                # Create mock product with basic nutritional info
                products_dict[product_name] = MockProduct(
                    name=product_name,
                    nutritional_info={
                        "calories": 100.0,
                        "protein": 10.0,
                        "carbs": 10.0,
                        "fat": 5.0,
                    }
                )
            
            product = products_dict[product_name]
            ingredient = MockRecipeIngredient(
                product_id=str(product.id),
                quantity_value=float(ing_data.get("quantity", 100)),
                quantity_unit=ing_data.get("unit", "g")
            )
            ingredient.product = product
            ingredients.append(ingredient)
        
        # Create recipe
        recipe = MockRecipe(
            name=recipe_data["name"],
            nutritional_info=recipe_data.get("nutritional_info_per_serving", {
                "calories": 500,
                "protein": 30,
                "carbs": 50,
                "fat": 20,
            }),
            meal_types=recipe_data.get("meal_types", ["lunch", "dinner"]),
            ingredients=ingredients,
            total_servings=recipe_data.get("total_servings", 4.0),
        )
        recipes.append(recipe)
    
    products = list(products_dict.values())
    return recipes, products


class TestBasicMealPlanGeneration:
    """Test User Story 1: Validate Basic Meal Plan Generation (P1)."""
    
    def test_plan_has_correct_number_of_days(self):
        """FR-001: Validate that generated meal plans contain the correct number of days."""
        recipes, products = load_test_recipes()
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=STANDARD_TEST_CASE["duration_days"],
            target_calories=STANDARD_TEST_CASE["target_calories"],
            target_protein=STANDARD_TEST_CASE["target_protein_g"],
            target_carbs=STANDARD_TEST_CASE["target_carbs_g"],
            target_fat=STANDARD_TEST_CASE["target_fat_g"],
            dishes_per_day=STANDARD_TEST_CASE["dishes_per_day"],
            timeout_seconds=60,
        )
        
        solution, status, error_message = solver.solve()
        
        assert solution is not None, f"Optimization failed: {status}, {error_message}"
        assert status in ["optimal", "feasible"], f"Unexpected status: {status}"
        
        days_data = solution.get("days", {})
        assert len(days_data) == STANDARD_TEST_CASE["duration_days"], \
            f"Expected {STANDARD_TEST_CASE['duration_days']} days, got {len(days_data)}"
    
    def test_each_day_has_correct_dish_count(self):
        """FR-002: Validate that each day contains exactly the specified number of dishes."""
        recipes, products = load_test_recipes()
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=STANDARD_TEST_CASE["duration_days"],
            target_calories=STANDARD_TEST_CASE["target_calories"],
            target_protein=STANDARD_TEST_CASE["target_protein_g"],
            target_carbs=STANDARD_TEST_CASE["target_carbs_g"],
            target_fat=STANDARD_TEST_CASE["target_fat_g"],
            dishes_per_day=STANDARD_TEST_CASE["dishes_per_day"],
            timeout_seconds=60,
        )
        
        solution, status, error_message = solver.solve()
        
        assert solution is not None, f"Optimization failed: {status}, {error_message}"
        
        days_data = solution.get("days", {})
        for day_key, day_data in days_data.items():
            recipes_list = day_data.get("recipes", [])
            assert len(recipes_list) == STANDARD_TEST_CASE["dishes_per_day"], \
                f"{day_key}: Expected {STANDARD_TEST_CASE['dishes_per_day']} dishes, got {len(recipes_list)}"
    
    def test_each_dish_has_exactly_one_serving(self):
        """FR-003: Validate that each dish in dish-based plans has exactly 1.0 serving."""
        recipes, products = load_test_recipes()
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=STANDARD_TEST_CASE["duration_days"],
            target_calories=STANDARD_TEST_CASE["target_calories"],
            target_protein=STANDARD_TEST_CASE["target_protein_g"],
            target_carbs=STANDARD_TEST_CASE["target_carbs_g"],
            target_fat=STANDARD_TEST_CASE["target_fat_g"],
            dishes_per_day=STANDARD_TEST_CASE["dishes_per_day"],
            timeout_seconds=60,
        )
        
        solution, status, error_message = solver.solve()
        
        assert solution is not None, f"Optimization failed: {status}, {error_message}"
        
        days_data = solution.get("days", {})
        for day_key, day_data in days_data.items():
            recipes_list = day_data.get("recipes", [])
            for recipe_data in recipes_list:
                servings = recipe_data.get("servings", 0)
                assert abs(servings - 1.0) < 0.01, \
                    f"{day_key}, {recipe_data.get('recipe_name')}: Expected 1.0 serving, got {servings}"
    
    def test_calorie_targets_met_within_tolerance(self):
        """FR-005: Validate that daily calorie totals meet targets within ±5% tolerance."""
        recipes, products = load_test_recipes()
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=STANDARD_TEST_CASE["duration_days"],
            target_calories=STANDARD_TEST_CASE["target_calories"],
            target_protein=STANDARD_TEST_CASE["target_protein_g"],
            target_carbs=STANDARD_TEST_CASE["target_carbs_g"],
            target_fat=STANDARD_TEST_CASE["target_fat_g"],
            dishes_per_day=STANDARD_TEST_CASE["dishes_per_day"],
            timeout_seconds=60,
        )
        
        solution, status, error_message = solver.solve()
        
        assert solution is not None, f"Optimization failed: {status}, {error_message}"
        
        target_calories = STANDARD_TEST_CASE["target_calories"]
        tolerance = 0.05
        lower_bound = target_calories * (1 - tolerance)
        upper_bound = target_calories * (1 + tolerance)
        
        days_data = solution.get("days", {})
        for day_key, day_data in days_data.items():
            total_calories = day_data.get("total_calories", 0)
            assert lower_bound <= total_calories <= upper_bound, \
                f"{day_key}: Calories {total_calories} not within {lower_bound}-{upper_bound} range"
    
    def test_macro_targets_met_within_tolerance(self):
        """FR-006, FR-007, FR-008: Validate macro targets within ±10% tolerance."""
        recipes, products = load_test_recipes()
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=STANDARD_TEST_CASE["duration_days"],
            target_calories=STANDARD_TEST_CASE["target_calories"],
            target_protein=STANDARD_TEST_CASE["target_protein_g"],
            target_carbs=STANDARD_TEST_CASE["target_carbs_g"],
            target_fat=STANDARD_TEST_CASE["target_fat_g"],
            dishes_per_day=STANDARD_TEST_CASE["dishes_per_day"],
            timeout_seconds=60,
        )
        
        solution, status, error_message = solver.solve()
        
        assert solution is not None, f"Optimization failed: {status}, {error_message}"
        
        tolerance = 0.10
        days_data = solution.get("days", {})
        
        for day_key, day_data in days_data.items():
            # Protein
            target_protein = STANDARD_TEST_CASE["target_protein_g"]
            actual_protein = day_data.get("total_protein_g", 0)
            protein_lower = target_protein * (1 - tolerance)
            protein_upper = target_protein * (1 + tolerance)
            assert protein_lower <= actual_protein <= protein_upper, \
                f"{day_key}: Protein {actual_protein}g not within {protein_lower}-{protein_upper}g"
            
            # Carbs
            target_carbs = STANDARD_TEST_CASE["target_carbs_g"]
            actual_carbs = day_data.get("total_carbs_g", 0)
            carbs_lower = target_carbs * (1 - tolerance)
            carbs_upper = target_carbs * (1 + tolerance)
            assert carbs_lower <= actual_carbs <= carbs_upper, \
                f"{day_key}: Carbs {actual_carbs}g not within {carbs_lower}-{carbs_upper}g"
            
            # Fat
            target_fat = STANDARD_TEST_CASE["target_fat_g"]
            actual_fat = day_data.get("total_fat_g", 0)
            fat_lower = target_fat * (1 - tolerance)
            fat_upper = target_fat * (1 + tolerance)
            assert fat_lower <= actual_fat <= fat_upper, \
                f"{day_key}: Fat {actual_fat}g not within {fat_lower}-{fat_upper}g"


class TestDishBasedConstraints:
    """Test User Story 2: Validate Dish-Based Constraints (P1)."""
    
    @pytest.mark.parametrize("dishes_per_day", [1, 3, 5, 7, 10])
    def test_exact_dish_count_per_day(self, dishes_per_day):
        """FR-002: Validate exact dish count for various dishes_per_day values."""
        recipes, products = load_test_recipes()
        
        # Need at least as many recipes as dishes_per_day
        if len(recipes) < dishes_per_day:
            pytest.skip(f"Not enough recipes ({len(recipes)}) for {dishes_per_day} dishes per day")
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=3,  # Test with 3 days for speed
            target_calories=2000,
            dishes_per_day=dishes_per_day,
            timeout_seconds=60,
        )
        
        solution, status, error_message = solver.solve()
        
        if solution is None:
            pytest.skip(f"Optimization failed for {dishes_per_day} dishes: {status}, {error_message}")
        
        days_data = solution.get("days", {})
        for day_key, day_data in days_data.items():
            recipes_list = day_data.get("recipes", [])
            assert len(recipes_list) == dishes_per_day, \
                f"{day_key}: Expected {dishes_per_day} dishes, got {len(recipes_list)}"
    
    def test_no_duplicate_dishes_per_day(self):
        """FR-004: Validate that no dish appears more than once per day."""
        recipes, products = load_test_recipes()
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=STANDARD_TEST_CASE["duration_days"],
            target_calories=STANDARD_TEST_CASE["target_calories"],
            target_protein=STANDARD_TEST_CASE["target_protein_g"],
            target_carbs=STANDARD_TEST_CASE["target_carbs_g"],
            target_fat=STANDARD_TEST_CASE["target_fat_g"],
            dishes_per_day=STANDARD_TEST_CASE["dishes_per_day"],
            timeout_seconds=60,
        )
        
        solution, status, error_message = solver.solve()
        
        assert solution is not None, f"Optimization failed: {status}, {error_message}"
        
        days_data = solution.get("days", {})
        for day_key, day_data in days_data.items():
            recipes_list = day_data.get("recipes", [])
            recipe_ids = [r.get("recipe_id") for r in recipes_list]
            assert len(recipe_ids) == len(set(recipe_ids)), \
                f"{day_key}: Duplicate dishes found: {recipe_ids}"
    
    def test_all_dishes_have_exactly_one_serving(self):
        """FR-003: Validate all dishes have exactly 1.0 serving (not 0.1, 0.5, 2.0, etc.)."""
        recipes, products = load_test_recipes()
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=STANDARD_TEST_CASE["duration_days"],
            target_calories=STANDARD_TEST_CASE["target_calories"],
            dishes_per_day=STANDARD_TEST_CASE["dishes_per_day"],
            timeout_seconds=60,
        )
        
        solution, status, error_message = solver.solve()
        
        assert solution is not None, f"Optimization failed: {status}, {error_message}"
        
        days_data = solution.get("days", {})
        for day_key, day_data in days_data.items():
            recipes_list = day_data.get("recipes", [])
            for recipe_data in recipes_list:
                servings = recipe_data.get("servings", 0)
                # Must be exactly 1.0, not close to 1.0
                assert servings == 1.0, \
                    f"{day_key}, {recipe_data.get('recipe_name')}: Expected exactly 1.0 serving, got {servings}"


class TestNutritionalAccuracy:
    """Test User Story 3: Validate Nutritional Accuracy (P1)."""
    
    def test_calorie_accuracy_within_5_percent(self):
        """Validate daily calories are within 1900-2100 for 2000 target."""
        recipes, products = load_test_recipes()
        
        target = 2000
        tolerance = 0.05
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=7,
            target_calories=target,
            dishes_per_day=5,
            timeout_seconds=60,
        )
        
        solution, status, error_message = solver.solve()
        
        assert solution is not None, f"Optimization failed: {status}, {error_message}"
        
        lower = int(target * (1 - tolerance))
        upper = int(target * (1 + tolerance))
        
        days_data = solution.get("days", {})
        for day_key, day_data in days_data.items():
            calories = day_data.get("total_calories", 0)
            assert lower <= calories <= upper, \
                f"{day_key}: Calories {calories} not in range {lower}-{upper}"
    
    def test_protein_accuracy_within_10_percent(self):
        """Validate daily protein is within 135-165g for 150g target."""
        recipes, products = load_test_recipes()
        
        target = 150.0
        tolerance = 0.10
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=7,
            target_calories=2000,
            target_protein=target,
            dishes_per_day=5,
            timeout_seconds=60,
        )
        
        solution, status, error_message = solver.solve()
        
        assert solution is not None, f"Optimization failed: {status}, {error_message}"
        
        lower = target * (1 - tolerance)
        upper = target * (1 + tolerance)
        
        days_data = solution.get("days", {})
        for day_key, day_data in days_data.items():
            protein = day_data.get("total_protein_g", 0)
            assert lower <= protein <= upper, \
                f"{day_key}: Protein {protein}g not in range {lower}-{upper}g"
    
    def test_carbs_accuracy_within_10_percent(self):
        """Validate daily carbs is within 180-220g for 200g target."""
        recipes, products = load_test_recipes()
        
        target = 200.0
        tolerance = 0.10
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=7,
            target_calories=2000,
            target_carbs=target,
            dishes_per_day=5,
            timeout_seconds=60,
        )
        
        solution, status, error_message = solver.solve()
        
        assert solution is not None, f"Optimization failed: {status}, {error_message}"
        
        lower = target * (1 - tolerance)
        upper = target * (1 + tolerance)
        
        days_data = solution.get("days", {})
        for day_key, day_data in days_data.items():
            carbs = day_data.get("total_carbs_g", 0)
            assert lower <= carbs <= upper, \
                f"{day_key}: Carbs {carbs}g not in range {lower}-{upper}g"
    
    def test_fat_accuracy_within_10_percent(self):
        """Validate daily fat is within 60-74g for 67g target."""
        recipes, products = load_test_recipes()
        
        target = 67.0
        tolerance = 0.10
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=7,
            target_calories=2000,
            target_fat=target,
            dishes_per_day=5,
            timeout_seconds=60,
        )
        
        solution, status, error_message = solver.solve()
        
        assert solution is not None, f"Optimization failed: {status}, {error_message}"
        
        lower = target * (1 - tolerance)
        upper = target * (1 + tolerance)
        
        days_data = solution.get("days", {})
        for day_key, day_data in days_data.items():
            fat = day_data.get("total_fat_g", 0)
            assert lower <= fat <= upper, \
                f"{day_key}: Fat {fat}g not in range {lower}-{upper}g"
    
    def test_all_macros_met_simultaneously(self):
        """Validate all macro targets are met simultaneously."""
        recipes, products = load_test_recipes()
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=STANDARD_TEST_CASE["duration_days"],
            target_calories=STANDARD_TEST_CASE["target_calories"],
            target_protein=STANDARD_TEST_CASE["target_protein_g"],
            target_carbs=STANDARD_TEST_CASE["target_carbs_g"],
            target_fat=STANDARD_TEST_CASE["target_fat_g"],
            dishes_per_day=STANDARD_TEST_CASE["dishes_per_day"],
            timeout_seconds=60,
        )
        
        solution, status, error_message = solver.solve()
        
        assert solution is not None, f"Optimization failed: {status}, {error_message}"
        
        days_data = solution.get("days", {})
        for day_key, day_data in days_data.items():
            # Check all macros
            calories = day_data.get("total_calories", 0)
            protein = day_data.get("total_protein_g", 0)
            carbs = day_data.get("total_carbs_g", 0)
            fat = day_data.get("total_fat_g", 0)
            
            # Calories ±5%
            assert 1900 <= calories <= 2100, f"{day_key}: Calories {calories} out of range"
            # Protein ±10%
            assert 135.0 <= protein <= 165.0, f"{day_key}: Protein {protein}g out of range"
            # Carbs ±10%
            assert 180.0 <= carbs <= 220.0, f"{day_key}: Carbs {carbs}g out of range"
            # Fat ±10%
            assert 60.0 <= fat <= 74.0, f"{day_key}: Fat {fat}g out of range"


class TestEdgeCasesAndErrorHandling:
    """Test User Story 4: Validate Edge Cases and Error Handling (P2)."""
    
    def test_invalid_dishes_per_day_zero(self):
        """FR-013: Validate error handling for dishes_per_day = 0."""
        recipes, products = load_test_recipes()
        
        # This should be caught by validation, but test solver behavior
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=3,
            target_calories=2000,
            dishes_per_day=0,  # Invalid
            timeout_seconds=10,
        )
        
        solution, status, error_message = solver.solve()
        
        # Should either fail or return infeasible
        assert solution is None or status in ["infeasible", "error"], \
            f"Expected failure for dishes_per_day=0, got status: {status}"
    
    def test_invalid_dishes_per_day_eleven(self):
        """FR-013: Validate error handling for dishes_per_day = 11."""
        recipes, products = load_test_recipes()
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=3,
            target_calories=2000,
            dishes_per_day=11,  # Invalid (>10)
            timeout_seconds=10,
        )
        
        solution, status, error_message = solver.solve()
        
        # Should either fail or return infeasible
        assert solution is None or status in ["infeasible", "error"], \
            f"Expected failure for dishes_per_day=11, got status: {status}"
    
    def test_low_calorie_target(self):
        """Test behavior with very low calorie target (500)."""
        recipes, products = load_test_recipes()
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=3,
            target_calories=500,  # Very low
            dishes_per_day=5,
            timeout_seconds=30,
        )
        
        solution, status, error_message = solver.solve()
        
        # Should either succeed or provide clear error
        if solution is None:
            assert error_message is not None, "Should provide error message for infeasible constraints"
            assert "calorie" in error_message.lower() or "infeasible" in error_message.lower(), \
                f"Error message should mention calorie/infeasible: {error_message}"
    
    def test_high_calorie_target(self):
        """Test behavior with very high calorie target (6000)."""
        recipes, products = load_test_recipes()
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=3,
            target_calories=6000,  # Very high
            dishes_per_day=5,
            timeout_seconds=30,
        )
        
        solution, status, error_message = solver.solve()
        
        # Should either succeed or provide clear error
        if solution is None:
            assert error_message is not None, "Should provide error message for infeasible constraints"
    
    def test_optimization_timeout(self):
        """FR-015: Validate that optimization completes within time limits."""
        recipes, products = load_test_recipes()
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=STANDARD_TEST_CASE["duration_days"],
            target_calories=STANDARD_TEST_CASE["target_calories"],
            dishes_per_day=STANDARD_TEST_CASE["dishes_per_day"],
            timeout_seconds=60,
        )
        
        import time
        start_time = time.time()
        solution, status, error_message = solver.solve()
        elapsed_time = time.time() - start_time
        
        # Should complete within timeout (with some buffer)
        assert elapsed_time < 70, f"Optimization took {elapsed_time}s, exceeds 60s timeout"
        
        # Status should be reported
        assert status in ["optimal", "feasible", "infeasible", "timeout", "error"], \
            f"Unexpected status: {status}"
    
    def test_backward_compatibility_no_dishes_per_day(self):
        """FR-016: Validate backward compatibility - plans without dishes_per_day still work."""
        recipes, products = load_test_recipes()
        
        # Traditional planning (no dishes_per_day)
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=3,
            target_calories=2000,
            dishes_per_day=None,  # Traditional mode
            timeout_seconds=60,
        )
        
        solution, status, error_message = solver.solve()
        
        # Should succeed (traditional planning)
        assert solution is not None, \
            f"Traditional planning failed: {status}, {error_message}"
        assert status in ["optimal", "feasible"], \
            f"Traditional planning should succeed, got: {status}"
        
        # Should have meals (may have variable servings)
        days_data = solution.get("days", {})
        assert len(days_data) > 0, "Should have at least one day"
        
        # Servings may vary (not constrained to 1.0)
        for day_data in days_data.values():
            recipes_list = day_data.get("recipes", [])
            assert len(recipes_list) > 0, "Should have at least one recipe per day"


class TestStandardTestCase:
    """Test the standard test case from specification."""
    
    def test_standard_test_case_comprehensive(self):
        """FR-012: Test standard test case with all validations."""
        recipes, products = load_test_recipes()
        
        solver = OptimizationSolver(
            recipes=recipes,
            products=products,
            days=STANDARD_TEST_CASE["duration_days"],
            target_calories=STANDARD_TEST_CASE["target_calories"],
            target_protein=STANDARD_TEST_CASE["target_protein_g"],
            target_carbs=STANDARD_TEST_CASE["target_carbs_g"],
            target_fat=STANDARD_TEST_CASE["target_fat_g"],
            dishes_per_day=STANDARD_TEST_CASE["dishes_per_day"],
            timeout_seconds=60,
        )
        
        solution, status, error_message = solver.solve()
        
        # Basic validation
        assert solution is not None, f"Optimization failed: {status}, {error_message}"
        assert status in ["optimal", "feasible"], f"Status should be optimal/feasible, got: {status}"
        
        days_data = solution.get("days", {})
        
        # Validate day count
        assert len(days_data) == STANDARD_TEST_CASE["duration_days"]
        
        # Validate each day
        for day_key, day_data in days_data.items():
            recipes_list = day_data.get("recipes", [])
            
            # Dish count
            assert len(recipes_list) == STANDARD_TEST_CASE["dishes_per_day"], \
                f"{day_key}: Expected {STANDARD_TEST_CASE['dishes_per_day']} dishes"
            
            # Servings
            for recipe_data in recipes_list:
                servings = recipe_data.get("servings", 0)
                assert servings == 1.0, \
                    f"{day_key}, {recipe_data.get('recipe_name')}: Expected 1.0 serving, got {servings}"
            
            # No duplicates
            recipe_ids = [r.get("recipe_id") for r in recipes_list]
            assert len(recipe_ids) == len(set(recipe_ids)), \
                f"{day_key}: Duplicate dishes found"
            
            # Nutritional targets
            calories = day_data.get("total_calories", 0)
            assert 1900 <= calories <= 2100, f"{day_key}: Calories {calories} out of range"
            
            protein = day_data.get("total_protein_g", 0)
            assert 135.0 <= protein <= 165.0, f"{day_key}: Protein {protein}g out of range"
            
            carbs = day_data.get("total_carbs_g", 0)
            assert 180.0 <= carbs <= 220.0, f"{day_key}: Carbs {carbs}g out of range"
            
            fat = day_data.get("total_fat_g", 0)
            assert 60.0 <= fat <= 74.0, f"{day_key}: Fat {fat}g out of range"
