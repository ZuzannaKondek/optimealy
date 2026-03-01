"""Database enums for OptiMeal application."""
import enum


class ThemeType(str, enum.Enum):
    """User theme preference."""

    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class UnitPreference(str, enum.Enum):
    """Unit system preference."""

    METRIC = "metric"
    IMPERIAL = "imperial"


class MealType(str, enum.Enum):
    """Type of meal within a day."""

    BREAKFAST = "breakfast"
    SECOND_BREAKFAST = "second_breakfast"
    DINNER = "dinner"
    DESSERT = "dessert"
    SUPPER = "supper"


class DietaryTag(str, enum.Enum):
    """Dietary restriction or preference tags."""

    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"
    PESCATARIAN = "pescatarian"
    KETO = "keto"
    PALEO = "paleo"
    LOW_CARB = "low_carb"
    HIGH_PROTEIN = "high_protein"


class RecipeDifficulty(str, enum.Enum):
    """Recipe difficulty level."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class OptimizationStatus(str, enum.Enum):
    """Status of meal plan optimization."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Perishability(str, enum.Enum):
    """Product perishability level."""

    HIGHLY_PERISHABLE = "highly_perishable"
    MODERATE = "moderate"
    STABLE = "stable"


class PreferenceType(str, enum.Enum):
    """User ingredient preference type."""

    ALREADY_HAVE = "already_have"
    WANT_TO_USE = "want_to_use"
    MUST_AVOID = "must_avoid"


class GroceryItemStatus(str, enum.Enum):
    """Status of grocery list item."""

    NEEDED = "needed"
    ALREADY_HAVE = "already_have"
    PURCHASED = "purchased"


class ProductCategory(str, enum.Enum):
    """Product/ingredient category."""

    PROTEIN = "protein"
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    GRAIN = "grain"
    DAIRY = "dairy"
    SPICE = "spice"
    CONDIMENT = "condiment"
    OIL = "oil"
    BEVERAGE = "beverage"
    OTHER = "other"
