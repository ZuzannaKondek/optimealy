"""Utility functions for optimization."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.recipe import Recipe


def calculate_dish_weight(recipe: "Recipe") -> float:
    """
    Calculate total weight of one serving of a dish in grams.
    
    Sums all ingredient quantities from recipe_ingredients.
    Converts quantities to grams if needed.
    
    Args:
        recipe: Recipe model with recipe_ingredients relationship
        
    Returns:
        Total weight in grams (rounded to 1 decimal place)
    """
    total_weight = 0.0
    
    for ingredient in recipe.recipe_ingredients:
        # Get quantity value and unit
        quantity_value = float(ingredient.quantity_value) if ingredient.quantity_value else 0.0
        quantity_unit = ingredient.quantity_unit.lower() if ingredient.quantity_unit else "g"
        
        # Convert to grams (simplified - assumes most units are already in grams)
        # For more sophisticated conversion, would need product database unit conversions
        if quantity_unit in ["g", "gram", "grams"]:
            weight_g = quantity_value
        elif quantity_unit in ["kg", "kilogram", "kilograms"]:
            weight_g = quantity_value * 1000.0
        elif quantity_unit in ["mg", "milligram", "milligrams"]:
            weight_g = quantity_value / 1000.0
        else:
            # Default to grams (assume unit is grams if not recognized)
            weight_g = quantity_value
        
        total_weight += weight_g
    
    # Round to 1 decimal place for display
    return round(total_weight, 1)
