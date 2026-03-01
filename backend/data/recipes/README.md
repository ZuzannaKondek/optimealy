# Recipe Data

This directory contains recipe datasets for the OptiMeal meal planning system.

## Files

### recipes-new-meal-types.json (CURRENT)
- **Status:** Active recipe dataset
- **Count:** 250 recipes
- **Generated:** 2026-01-18
- **Structure:** 5 meal types (breakfast, second_breakfast, dinner, dessert, supper)
- **Format:** Single-serving recipes (total_servings: 1.0)
- **Nutrition:** Calculated dynamically from ingredients, NOT hardcoded

#### Recipe Distribution
- Breakfast: 50 recipes (400-800 kcal)
- Second Breakfast: 50 recipes (200-300 kcal)
- Dinner: 50 recipes (500-900 kcal)
- Dessert: 50 recipes (100-200 kcal)
- Supper: 50 recipes (400-800 kcal)

### sample-recipes.json (LEGACY)
- **Status:** Archived/backup
- **Count:** 172 recipes  
- **Structure:** Old 4 meal types (breakfast, lunch, dinner, snack)
- **Note:** Deprecated, kept for reference only

## Recipe Format

```json
{
  "name": "Recipe Name",
  "description": "Brief description",
  "instructions": "Step-by-step instructions",
  "meal_types": ["breakfast"],
  "cuisine_type": "American",
  "dietary_tags": ["vegetarian", "high_protein"],
  "prep_time_minutes": 10,
  "cook_time_minutes": 15,
  "total_servings": 1.0,
  "ingredients": [
    {
      "product_name": "Exact Product Name",
      "quantity": 100,
      "unit": "g"
    }
  ]
}
```

## Meal Type Specifications

| Meal Type | Calorie Range | Description | Characteristics |
|-----------|---------------|-------------|-----------------|
| breakfast | 400-800 kcal | Morning meal | Hot/cold dishes, eggs, cooked items, substantial |
| second_breakfast | 200-300 kcal | Mid-morning snack | Cold, light dishes (fruit, yogurt) |
| dinner | 500-900 kcal | Main meal | Hot food, protein-rich, most substantial meal |
| dessert | 100-200 kcal | Sweet treat | Small portions, satisfying sweet cravings |
| supper | 400-800 kcal | Evening meal | Cold dishes (sandwiches, salads, wraps) |

## Validation

All recipes are validated for:
- Single serving (total_servings = 1.0)
- Ingredient existence in products database
- Calorie range compliance (±50 kcal tolerance)
- Required fields completeness
- Realistic ingredient quantities

## Maintenance

To add new recipes:
1. Follow the format above exactly
2. Ensure product_name matches products database
3. Calculate expected calories manually
4. Validate with validation script
5. Test with optimizer before deployment

## Related Files

- Products: `backend/data/products/sample-products.json`
- Seed Script: `backend/src/database/seed.py`
- Generation Script: `backend/scripts/generate_recipes_direct.py`
