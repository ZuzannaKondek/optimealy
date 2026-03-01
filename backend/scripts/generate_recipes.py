"""Generate recipes for meal planning system."""
import json
from pathlib import Path
from typing import List, Dict, Any
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.extract_products import load_products


MEAL_TYPE_SPECS = {
    'breakfast': {
        'count': 50,
        'calorie_min': 400,
        'calorie_max': 800,
        'description': 'Hot/cold dishes, eggs, cooked items'
    },
    'second_breakfast': {
        'count': 50,
        'calorie_min': 200,
        'calorie_max': 300,
        'description': 'Cold, light dishes (fruit, yogurt)'
    },
    'dinner': {
        'count': 50,
        'calorie_min': 500,
        'calorie_max': 900,
        'description': 'Hot food, main meal'
    },
    'dessert': {
        'count': 50,
        'calorie_min': 100,
        'calorie_max': 200,
        'description': 'Sweet dishes'
    },
    'supper': {
        'count': 50,
        'calorie_min': 400,
        'calorie_max': 800,
        'description': 'Cold dishes (sandwiches)'
    }
}


def calculate_recipe_calories(ingredients: List[Dict], product_lookup: Dict) -> float:
    """Calculate total calories from ingredients."""
    total_cal = 0.0
    for ing in ingredients:
        product_name = ing['product_name']
        quantity_g = ing['quantity']  # Assume grams
        
        if product_name not in product_lookup:
            raise ValueError(f"Product {product_name} not found in database")
        
        cal_per_100g = product_lookup[product_name]['calories_per_100g']
        total_cal += (quantity_g / 100.0) * cal_per_100g
    
    return total_cal


def validate_recipe(recipe: Dict, meal_type: str, product_lookup: Dict) -> tuple:
    """Validate recipe meets requirements."""
    # Check required fields
    required = ['name', 'instructions', 'meal_types', 'total_servings', 'ingredients']
    for field in required:
        if field not in recipe:
            return False, f"Missing required field: {field}"
    
    # Check meal type
    if meal_type not in recipe['meal_types']:
        return False, f"Meal type {meal_type} not in recipe meal_types"
    
    # Check servings
    if recipe['total_servings'] != 1.0:
        return False, f"total_servings must be 1.0, got {recipe['total_servings']}"
    
    # Check ingredients exist
    for ing in recipe['ingredients']:
        if ing['product_name'] not in product_lookup:
            return False, f"Product {ing['product_name']} not found"
    
    # Check calories
    calories = calculate_recipe_calories(recipe['ingredients'], product_lookup)
    spec = MEAL_TYPE_SPECS[meal_type]
    if not (spec['calorie_min'] - 50 <= calories <= spec['calorie_max'] + 50):
        return False, f"Calories {calories:.0f} outside range {spec['calorie_min']}-{spec['calorie_max']}"
    
    return True, "OK"


def create_recipe_generation_prompt(
    meal_type: str,
    spec: Dict,
    available_products: List[str],
    existing_recipes: List[Dict]
) -> str:
    """Create prompt for AI recipe generation."""
    existing_names = [r['name'] for r in existing_recipes]
    
    prompt = f"""Generate a realistic single-serving recipe for {meal_type}.

Requirements:
- Meal type: {meal_type}
- Calorie range: {spec['calorie_min']}-{spec['calorie_max']} kcal
- Description: {spec['description']}
- Must be realistic and appetizing
- Single serving only (total_servings: 1.0)
- Use only ingredients from available products list
- Do not duplicate these existing names: {', '.join(existing_names[-10:])}

Available products (use exact names):
{', '.join(sorted(available_products)[:100])}

Return JSON only (no other text) in this exact format:
{{
  "name": "Recipe Name",
  "description": "Brief description",
  "instructions": "Step by step cooking instructions",
  "meal_types": ["{meal_type}"],
  "cuisine_type": "Cuisine name",
  "dietary_tags": ["vegetarian", "high_protein"],
  "prep_time_minutes": 10,
  "cook_time_minutes": 15,
  "total_servings": 1.0,
  "ingredients": [
    {{"product_name": "Exact Product Name", "quantity": 100, "unit": "g"}}
  ]
}}

Recipe:"""
    
    return prompt


def generate_recipes_for_meal_type(
    meal_type: str,
    count: int,
    product_lookup: Dict,
    available_products: List[str]
) -> List[Dict]:
    """Generate recipes for a specific meal type."""
    recipes = []
    
    # TODO: Implement AI generation logic
    # For now, placeholder
    print(f"Generating {count} recipes for {meal_type}...")
    print(f"  (AI generation requires ANTHROPIC_API_KEY environment variable)")
    
    return recipes


def main():
    """Main recipe generation logic."""
    print("Loading products...")
    product_lookup, available_products = load_products()
    print(f"Loaded {len(available_products)} products")
    
    all_recipes = []
    
    for meal_type, spec in MEAL_TYPE_SPECS.items():
        print(f"\n=== Generating {spec['count']} {meal_type} recipes ===")
        recipes = generate_recipes_for_meal_type(
            meal_type,
            spec['count'],
            product_lookup,
            available_products
        )
        
        # Validate each recipe
        valid_recipes = []
        for recipe in recipes:
            is_valid, msg = validate_recipe(recipe, meal_type, product_lookup)
            if is_valid:
                valid_recipes.append(recipe)
            else:
                print(f"  WARNING: Invalid recipe '{recipe.get('name', 'unknown')}': {msg}")
        
        print(f"  Generated {len(valid_recipes)}/{spec['count']} valid recipes")
        all_recipes.extend(valid_recipes)
    
    # Save to file
    output_file = Path(__file__).parent.parent / 'data' / 'recipes' / 'recipes-new-meal-types.json'
    with open(output_file, 'w') as f:
        json.dump(all_recipes, f, indent=2)
    
    print(f"\n✓ Saved {len(all_recipes)} recipes to {output_file}")
    
    # Print summary
    print("\n=== Summary ===")
    for meal_type in MEAL_TYPE_SPECS.keys():
        count = len([r for r in all_recipes if meal_type in r['meal_types']])
        print(f"  {meal_type}: {count} recipes")


if __name__ == '__main__':
    main()
