"""Pantry Staples Configuration

Curated list of common pantry/fridge items that users typically have.
These are the most common items that cause waste when not tracked.
"""

# Curated list of pantry staple product names
# These should match product names in the database exactly
PANTRY_STAPLES = [
    # Oils & Fats
    "Olive Oil",
    "Vegetable Oil",
    "Sesame Oil",
    "Coconut Oil",
    "Butter",
    
    # Basic Seasonings
    "Salt",
    "Black Pepper",
    "Garlic Powder",
    "Onion Powder",
    "Paprika",
    "Cumin",
    "Oregano",
    "Basil",
    "Thyme",
    "Cinnamon",
    
    # Condiments & Sauces
    "Soy Sauce",
    "Honey",
    "Mustard",
    "Ketchup",
    "Mayonnaise",
    "Tomato Sauce",
    "Olive Oil",
    "Balsamic Vinegar",
    "Lemon Juice",
    
    # Grains & Starches
    "Rice",
    "White Rice",
    "Brown Rice",
    "Flour",
    "Wheat Flour",
    "Pasta",
    "Spaghetti",
    "Bread",
    "Oats",
    
    # Dairy & Eggs
    "Eggs",
    "Milk",
    "Butter",
    "Cheese",
    "Greek Yogurt",
    "Parmesan",
    
    # Common Vegetables (long shelf life)
    "Onion",
    "Garlic",
    "Potatoes",
    "Carrots",
]

# Remove duplicates while preserving order
PANTRY_STAPLES = list(dict.fromkeys(PANTRY_STAPLES))
