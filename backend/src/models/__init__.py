"""SQLAlchemy models for OptiMeal API."""

# Import all models here for Alembic autogenerate
# When you create new models, add them to this file

from .user import User
from .recipe import Recipe
from .product import Product
from .recipe_ingredient import RecipeIngredient
from .meal_plan import MealPlan, DailyMenu, Meal
from .user_ingredient_preference import UserIngredientPreference
from .grocery import GroceryList, GroceryItem
from .meal_completion import MealCompletion
from .user_pantry_item import UserPantryItem

__all__ = [
    "User",
    "Recipe",
    "Product",
    "RecipeIngredient",
    "MealPlan",
    "DailyMenu",
    "Meal",
    "UserIngredientPreference",
    "GroceryList",
    "GroceryItem",
    "MealCompletion",
    "UserPantryItem",
]
