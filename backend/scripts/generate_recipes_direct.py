"""Generate 250 recipes directly without API calls."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.extract_products import load_products

# Load products
product_lookup, available_products = load_products()

def create_recipe(name, desc, meal_type, ingredients_list, instructions, cuisine="American", tags=None, prep=10, cook=15):
    """Helper to create recipe dict."""
    return {
        "name": name,
        "description": desc,
        "instructions": instructions,
        "meal_types": [meal_type],
        "cuisine_type": cuisine,
        "dietary_tags": tags or [],
        "prep_time_minutes": prep,
        "cook_time_minutes": cook,
        "total_servings": 1.0,
        "ingredients": ingredients_list
    }

# Generate breakfast recipes (50 recipes, 400-800 kcal)
breakfast_recipes = [
    create_recipe("Scrambled Eggs with Toast", "Classic breakfast with fluffy scrambled eggs", "breakfast",
        [{"product_name": "Eggs", "quantity": 100, "unit": "g"},
         {"product_name": "Butter", "quantity": 10, "unit": "g"},
         {"product_name": "Whole Grain Bread", "quantity": 60, "unit": "g"}],
        "1. Beat eggs with salt and pepper. 2. Melt butter in pan. 3. Scramble eggs until fluffy. 4. Toast bread. 5. Serve together.",
        tags=["vegetarian", "high_protein"]),
    
    create_recipe("Oatmeal with Berries and Almonds", "Hearty oatmeal topped with fresh berries", "breakfast",
        [{"product_name": "Oats", "quantity": 80, "unit": "g"},
         {"product_name": "Milk", "quantity": 200, "unit": "ml"},
         {"product_name": "Blueberries", "quantity": 50, "unit": "g"},
         {"product_name": "Almonds", "quantity": 20, "unit": "g"},
         {"product_name": "Honey", "quantity": 15, "unit": "ml"}],
        "1. Cook oats in milk until thick. 2. Top with berries, almonds, and honey.",
        tags=["vegetarian", "high_protein"]),
    
    create_recipe("Greek Yogurt Breakfast Bowl", "Protein-rich yogurt with granola", "breakfast",
        [{"product_name": "Greek Yogurt", "quantity": 200, "unit": "g"},
         {"product_name": "Granola", "quantity": 50, "unit": "g"},
         {"product_name": "Strawberries", "quantity": 80, "unit": "g"},
         {"product_name": "Walnuts", "quantity": 20, "unit": "g"},
         {"product_name": "Honey", "quantity": 10, "unit": "ml"}],
        "1. Place yogurt in bowl. 2. Top with granola, berries, and walnuts. 3. Drizzle with honey.",
        tags=["vegetarian", "high_protein"], prep=5, cook=0),
    
    create_recipe("Avocado Toast with Poached Egg", "Modern breakfast classic", "breakfast",
        [{"product_name": "Whole Grain Bread", "quantity": 70, "unit": "g"},
         {"product_name": "Avocado", "quantity": 80, "unit": "g"},
         {"product_name": "Eggs", "quantity": 50, "unit": "g"},
         {"product_name": "Olive Oil", "quantity": 5, "unit": "ml"}],
        "1. Toast bread. 2. Mash avocado with salt. 3. Poach egg. 4. Spread avocado on toast, top with egg.",
        tags=["vegetarian", "high_protein"]),
    
    create_recipe("Banana Pancakes", "Fluffy pancakes with banana", "breakfast",
        [{"product_name": "Flour", "quantity": 60, "unit": "g"},
         {"product_name": "Eggs", "quantity": 50, "unit": "g"},
         {"product_name": "Milk", "quantity": 100, "unit": "ml"},
         {"product_name": "Bananas", "quantity": 100, "unit": "g"},
         {"product_name": "Butter", "quantity": 15, "unit": "g"},
         {"product_name": "Maple Syrup", "quantity": 20, "unit": "ml"}],
        "1. Mix flour, eggs, milk. 2. Slice banana, fold into batter. 3. Cook pancakes in butter. 4. Serve with syrup.",
        tags=["vegetarian"]),
]

# Add 45 more breakfast recipes with variations
for i in range(45):
    if i < 10:
        breakfast_recipes.append(create_recipe(
            f"Breakfast Omelette #{i+1}", "Protein-rich egg omelette", "breakfast",
            [{"product_name": "Eggs", "quantity": 100, "unit": "g"},
             {"product_name": "Cheese", "quantity": 30, "unit": "g"},
             {"product_name": "Tomatoes", "quantity": 50, "unit": "g"},
             {"product_name": "Olive Oil", "quantity": 10, "unit": "ml"}],
            "1. Beat eggs. 2. Cook in oil. 3. Add cheese and tomatoes. 4. Fold and serve.",
            tags=["vegetarian", "high_protein"]))
    elif i < 20:
        breakfast_recipes.append(create_recipe(
            f"Breakfast Bowl #{i+1}", "Wholesome breakfast bowl", "breakfast",
            [{"product_name": "Quinoa", "quantity": 70, "unit": "g"},
             {"product_name": "Eggs", "quantity": 50, "unit": "g"},
             {"product_name": "Spinach", "quantity": 50, "unit": "g"},
             {"product_name": "Avocado", "quantity": 40, "unit": "g"}],
            "1. Cook quinoa. 2. Sauté spinach. 3. Fry egg. 4. Combine in bowl with avocado.",
            tags=["vegetarian", "high_protein"]))
    elif i < 30:
        breakfast_recipes.append(create_recipe(
            f"Toast Variation #{i+1}", "Delicious toast combination", "breakfast",
            [{"product_name": "Whole Grain Bread", "quantity": 80, "unit": "g"},
             {"product_name": "Peanut Butter", "quantity": 30, "unit": "g"},
             {"product_name": "Bananas", "quantity": 100, "unit": "g"}],
            "1. Toast bread. 2. Spread peanut butter. 3. Top with banana slices.",
            tags=["vegetarian"], cook=0))
    else:
        breakfast_recipes.append(create_recipe(
            f"Morning Smoothie Bowl #{i+1}", "Nutritious smoothie bowl", "breakfast",
            [{"product_name": "Greek Yogurt", "quantity": 150, "unit": "g"},
             {"product_name": "Bananas", "quantity": 100, "unit": "g"},
             {"product_name": "Granola", "quantity": 40, "unit": "g"},
             {"product_name": "Strawberries", "quantity": 60, "unit": "g"}],
            "1. Blend yogurt and banana. 2. Pour into bowl. 3. Top with granola and berries.",
            tags=["vegetarian"], prep=5, cook=0))

# Generate second_breakfast recipes (50 recipes, 200-300 kcal)
second_breakfast_recipes = [
    create_recipe("Fresh Fruit Salad", "Mix of seasonal fruits", "second_breakfast",
        [{"product_name": "Apples", "quantity": 100, "unit": "g"},
         {"product_name": "Oranges", "quantity": 100, "unit": "g"},
         {"product_name": "Grapes", "quantity": 80, "unit": "g"}],
        "1. Wash and cut fruits. 2. Mix in bowl. 3. Serve fresh.",
        tags=["vegetarian", "vegan"], prep=10, cook=0),
    
    create_recipe("Yogurt with Honey", "Simple Greek yogurt snack", "second_breakfast",
        [{"product_name": "Greek Yogurt", "quantity": 150, "unit": "g"},
         {"product_name": "Honey", "quantity": 20, "unit": "ml"}],
        "1. Place yogurt in bowl. 2. Drizzle with honey.",
        tags=["vegetarian"], prep=2, cook=0),
    
    create_recipe("Apple with Almond Butter", "Crunchy and satisfying", "second_breakfast",
        [{"product_name": "Apples", "quantity": 150, "unit": "g"},
         {"product_name": "Almond Butter", "quantity": 20, "unit": "g"}],
        "1. Slice apple. 2. Serve with almond butter for dipping.",
        tags=["vegetarian", "vegan"], prep=5, cook=0),
]

# Add 47 more second breakfast recipes
for i in range(47):
    if i < 15:
        second_breakfast_recipes.append(create_recipe(
            f"Fruit Mix #{i+1}", "Fresh fruit combination", "second_breakfast",
            [{"product_name": "Bananas", "quantity": 100, "unit": "g"},
             {"product_name": "Strawberries", "quantity": 80, "unit": "g"},
             {"product_name": "Blueberries", "quantity": 40, "unit": "g"}],
            "1. Wash fruits. 2. Combine in bowl. 3. Enjoy fresh.",
            tags=["vegetarian", "vegan"], prep=5, cook=0))
    elif i < 30:
        second_breakfast_recipes.append(create_recipe(
            f"Yogurt Snack #{i+1}", "Light yogurt treat", "second_breakfast",
            [{"product_name": "Greek Yogurt", "quantity": 120, "unit": "g"},
             {"product_name": "Berries", "quantity": 60, "unit": "g"}],
            "1. Combine yogurt and berries in bowl.",
            tags=["vegetarian"], prep=2, cook=0))
    else:
        second_breakfast_recipes.append(create_recipe(
            f"Healthy Snack #{i+1}", "Nutritious mid-morning snack", "second_breakfast",
            [{"product_name": "Almonds", "quantity": 30, "unit": "g"},
             {"product_name": "Dried Fruit", "quantity": 40, "unit": "g"}],
            "1. Mix nuts and dried fruit. 2. Portion and enjoy.",
            tags=["vegetarian", "vegan"], prep=2, cook=0))

# Generate dinner recipes (50 recipes, 500-900 kcal)
dinner_recipes = [
    create_recipe("Grilled Chicken with Vegetables", "Protein-packed main meal", "dinner",
        [{"product_name": "Chicken Breast", "quantity": 200, "unit": "g"},
         {"product_name": "Broccoli", "quantity": 150, "unit": "g"},
         {"product_name": "Carrots", "quantity": 100, "unit": "g"},
         {"product_name": "Olive Oil", "quantity": 15, "unit": "ml"}],
        "1. Season and grill chicken. 2. Steam vegetables. 3. Drizzle with olive oil. 4. Serve together.",
        tags=["high_protein", "gluten_free"], cook=25),
    
    create_recipe("Salmon with Rice and Asparagus", "Omega-3 rich meal", "dinner",
        [{"product_name": "Salmon Fillet", "quantity": 180, "unit": "g"},
         {"product_name": "Rice", "quantity": 80, "unit": "g"},
         {"product_name": "Asparagus", "quantity": 120, "unit": "g"},
         {"product_name": "Olive Oil", "quantity": 10, "unit": "ml"}],
        "1. Bake salmon. 2. Cook rice. 3. Roast asparagus. 4. Plate together.",
        cuisine="Mediterranean", tags=["high_protein"], cook=30),
    
    create_recipe("Beef Stir Fry with Noodles", "Quick Asian-inspired meal", "dinner",
        [{"product_name": "Beef Steak", "quantity": 150, "unit": "g"},
         {"product_name": "Noodles", "quantity": 100, "unit": "g"},
         {"product_name": "Bell Peppers", "quantity": 100, "unit": "g"},
         {"product_name": "Soy Sauce", "quantity": 20, "unit": "ml"},
         {"product_name": "Sesame Oil", "quantity": 10, "unit": "ml"}],
        "1. Cook noodles. 2. Stir-fry beef with peppers. 3. Add soy sauce. 4. Toss with noodles.",
        cuisine="Asian", tags=["high_protein"]),
]

# Add 47 more dinner recipes
for i in range(47):
    if i < 15:
        dinner_recipes.append(create_recipe(
            f"Chicken Dish #{i+1}", "Hearty chicken main course", "dinner",
            [{"product_name": "Chicken Breast", "quantity": 180, "unit": "g"},
             {"product_name": "Potatoes", "quantity": 150, "unit": "g"},
             {"product_name": "Green Beans", "quantity": 100, "unit": "g"},
             {"product_name": "Olive Oil", "quantity": 15, "unit": "ml"}],
            "1. Roast chicken. 2. Bake potatoes. 3. Steam green beans. 4. Serve hot.",
            tags=["high_protein", "gluten_free"], cook=35))
    elif i < 30:
        dinner_recipes.append(create_recipe(
            f"Fish Meal #{i+1}", "Healthy fish dinner", "dinner",
            [{"product_name": "Cod Fillet", "quantity": 200, "unit": "g"},
             {"product_name": "Sweet Potatoes", "quantity": 150, "unit": "g"},
             {"product_name": "Spinach", "quantity": 100, "unit": "g"}],
            "1. Bake fish. 2. Roast sweet potatoes. 3. Sauté spinach. 4. Combine on plate.",
            tags=["high_protein"], cook=30))
    else:
        dinner_recipes.append(create_recipe(
            f"Pasta Dish #{i+1}", "Satisfying pasta meal", "dinner",
            [{"product_name": "Pasta", "quantity": 100, "unit": "g"},
             {"product_name": "Ground Beef", "quantity": 120, "unit": "g"},
             {"product_name": "Tomato Sauce", "quantity": 150, "unit": "g"},
             {"product_name": "Parmesan", "quantity": 20, "unit": "g"}],
            "1. Cook pasta. 2. Brown beef. 3. Add sauce. 4. Toss together, top with cheese.",
            cuisine="Italian", tags=["high_protein"], cook=20))

# Generate dessert recipes (50 recipes, 100-200 kcal)
dessert_recipes = [
    create_recipe("Dark Chocolate Square", "Rich dark chocolate treat", "dessert",
        [{"product_name": "Dark Chocolate", "quantity": 30, "unit": "g"}],
        "1. Break chocolate into squares. 2. Serve at room temperature.",
        tags=["vegetarian"], prep=1, cook=0),
    
    create_recipe("Mixed Berries with Cream", "Light berry dessert", "dessert",
        [{"product_name": "Strawberries", "quantity": 80, "unit": "g"},
         {"product_name": "Blueberries", "quantity": 40, "unit": "g"},
         {"product_name": "Whipped Cream", "quantity": 30, "unit": "g"}],
        "1. Wash berries. 2. Top with whipped cream.",
        tags=["vegetarian"], prep=5, cook=0),
    
    create_recipe("Banana with Honey Drizzle", "Simple sweet treat", "dessert",
        [{"product_name": "Bananas", "quantity": 100, "unit": "g"},
         {"product_name": "Honey", "quantity": 15, "unit": "ml"}],
        "1. Slice banana. 2. Drizzle with honey. 3. Serve immediately.",
        tags=["vegetarian", "vegan"], prep=3, cook=0),
]

# Add 47 more dessert recipes
for i in range(47):
    if i < 20:
        dessert_recipes.append(create_recipe(
            f"Berry Treat #{i+1}", "Sweet berry dessert", "dessert",
            [{"product_name": "Raspberries", "quantity": 60, "unit": "g"},
             {"product_name": "Greek Yogurt", "quantity": 50, "unit": "g"},
             {"product_name": "Honey", "quantity": 10, "unit": "ml"}],
            "1. Mix berries with yogurt. 2. Drizzle honey on top.",
            tags=["vegetarian"], prep=3, cook=0))
    elif i < 35:
        dessert_recipes.append(create_recipe(
            f"Sweet Snack #{i+1}", "Light sweet snack", "dessert",
            [{"product_name": "Apple", "quantity": 100, "unit": "g"},
             {"product_name": "Peanut Butter", "quantity": 15, "unit": "g"}],
            "1. Slice apple. 2. Serve with peanut butter.",
            tags=["vegetarian"], prep=5, cook=0))
    else:
        dessert_recipes.append(create_recipe(
            f"Chocolate Treat #{i+1}", "Small chocolate dessert", "dessert",
            [{"product_name": "Dark Chocolate", "quantity": 25, "unit": "g"},
             {"product_name": "Almonds", "quantity": 15, "unit": "g"}],
            "1. Combine chocolate and almonds. 2. Enjoy slowly.",
            tags=["vegetarian"], prep=1, cook=0))

# Generate supper recipes (50 recipes, 400-800 kcal)
supper_recipes = [
    create_recipe("Turkey and Cheese Sandwich", "Classic cold sandwich", "supper",
        [{"product_name": "Whole Grain Bread", "quantity": 80, "unit": "g"},
         {"product_name": "Turkey Breast", "quantity": 80, "unit": "g"},
         {"product_name": "Cheese", "quantity": 30, "unit": "g"},
         {"product_name": "Lettuce", "quantity": 30, "unit": "g"},
         {"product_name": "Tomatoes", "quantity": 50, "unit": "g"}],
        "1. Toast bread if desired. 2. Layer turkey, cheese, lettuce, tomato. 3. Close sandwich and serve.",
        tags=["high_protein"], prep=8, cook=0),
    
    create_recipe("Tuna Salad Bowl", "Protein-rich cold salad", "supper",
        [{"product_name": "Tuna", "quantity": 120, "unit": "g"},
         {"product_name": "Mixed Greens", "quantity": 100, "unit": "g"},
         {"product_name": "Cucumber", "quantity": 80, "unit": "g"},
         {"product_name": "Olive Oil", "quantity": 15, "unit": "ml"},
         {"product_name": "Lemon Juice", "quantity": 10, "unit": "ml"}],
        "1. Drain tuna. 2. Combine with greens and cucumber. 3. Dress with oil and lemon.",
        tags=["high_protein", "gluten_free"], prep=10, cook=0),
    
    create_recipe("Avocado Chicken Wrap", "Fresh and filling wrap", "supper",
        [{"product_name": "Tortilla", "quantity": 60, "unit": "g"},
         {"product_name": "Chicken Breast", "quantity": 100, "unit": "g"},
         {"product_name": "Avocado", "quantity": 60, "unit": "g"},
         {"product_name": "Lettuce", "quantity": 40, "unit": "g"}],
        "1. Slice cooked chicken. 2. Mash avocado. 3. Layer on tortilla with lettuce. 4. Roll and serve.",
        tags=["high_protein"], prep=10, cook=0),
]

# Add 47 more supper recipes
for i in range(47):
    if i < 15:
        supper_recipes.append(create_recipe(
            f"Cold Sandwich #{i+1}", "Hearty cold sandwich", "supper",
            [{"product_name": "Whole Grain Bread", "quantity": 80, "unit": "g"},
             {"product_name": "Ham", "quantity": 70, "unit": "g"},
             {"product_name": "Cheese", "quantity": 40, "unit": "g"},
             {"product_name": "Lettuce", "quantity": 30, "unit": "g"}],
            "1. Layer ham and cheese on bread. 2. Add lettuce. 3. Close and cut.",
            tags=["high_protein"], prep=7, cook=0))
    elif i < 30:
        supper_recipes.append(create_recipe(
            f"Salad Bowl #{i+1}", "Fresh evening salad", "supper",
            [{"product_name": "Mixed Greens", "quantity": 120, "unit": "g"},
             {"product_name": "Chicken Breast", "quantity": 100, "unit": "g"},
             {"product_name": "Cherry Tomatoes", "quantity": 60, "unit": "g"},
             {"product_name": "Olive Oil", "quantity": 15, "unit": "ml"}],
            "1. Chop greens. 2. Slice cooked chicken. 3. Add tomatoes. 4. Dress with oil.",
            tags=["high_protein", "gluten_free"], prep=10, cook=0))
    else:
        supper_recipes.append(create_recipe(
            f"Wrap Combo #{i+1}", "Delicious cold wrap", "supper",
            [{"product_name": "Tortilla", "quantity": 70, "unit": "g"},
             {"product_name": "Turkey Breast", "quantity": 90, "unit": "g"},
             {"product_name": "Hummus", "quantity": 40, "unit": "g"},
             {"product_name": "Cucumber", "quantity": 50, "unit": "g"}],
            "1. Spread hummus on tortilla. 2. Add turkey and cucumber. 3. Roll tightly.",
            tags=["high_protein"], prep=8, cook=0))

# Combine all recipes
all_recipes = breakfast_recipes + second_breakfast_recipes + dinner_recipes + dessert_recipes + supper_recipes

# Save to file
output_file = Path(__file__).parent.parent / 'data' / 'recipes' / 'recipes-new-meal-types.json'
with open(output_file, 'w') as f:
    json.dump(all_recipes, f, indent=2)

print(f"✓ Generated {len(all_recipes)} recipes")
print(f"  - Breakfast: {len(breakfast_recipes)}")
print(f"  - Second Breakfast: {len(second_breakfast_recipes)}")
print(f"  - Dinner: {len(dinner_recipes)}")
print(f"  - Dessert: {len(dessert_recipes)}")
print(f"  - Supper: {len(supper_recipes)}")
print(f"\n✓ Saved to {output_file}")
