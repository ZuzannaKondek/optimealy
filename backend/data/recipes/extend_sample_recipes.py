#!/usr/bin/env python3
"""
Extend backend/data/recipes/sample-recipes.json with additional recipes.

Goals (minimum totals in the JSON file):
- breakfast: 50
- lunch: 50  (maps to "dinner" eaten midday)
- dinner: 50 (maps to "supper" lighter late meal)
- snack: 30  (used for desserts)

This script appends recipes in the existing seed JSON format and only uses
ingredients that already exist in backend/data/products/sample-products.json.
"""

from __future__ import annotations

import json
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


ROOT = Path(__file__).resolve().parents[1]  # backend/data
RECIPES_FILE = ROOT / "recipes" / "sample-recipes.json"
PRODUCTS_FILE = ROOT / "products" / "sample-products.json"


def load_json(path: Path) -> Any:
    with open(path, "r") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def product_names(products: List[Dict[str, Any]]) -> Set[str]:
    return {p["name"] for p in products if "name" in p}


def meal_type_counts(recipes: List[Dict[str, Any]]) -> Counter:
    c: Counter = Counter()
    for r in recipes:
        for mt in r.get("meal_types", []):
            c[mt] += 1
    return c


def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


def nutrition_for(
    rng: random.Random,
    category: str,
    *,
    high_protein: bool = False,
    high_fiber: bool = False,
) -> Dict[str, float]:
    """
    Lightweight, plausible macro generator.
    Values are approximate and intended for demo/seed usage.
    """
    if category == "breakfast":
        cal = rng.randint(280, 480)
    elif category == "lunch":
        cal = rng.randint(380, 680)
    elif category == "dinner":  # supper = lighter late meal
        cal = rng.randint(280, 520)
    else:  # snack/dessert
        cal = rng.randint(160, 380)

    protein = rng.randint(8, 18)
    if high_protein:
        protein = rng.randint(18, 45)

    fat = rng.randint(6, 18)
    carbs = clamp(int((cal - (protein * 4) - (fat * 9)) / 4), 10, 110)

    fiber = rng.randint(2, 8)
    if high_fiber:
        fiber = rng.randint(6, 16)

    return {
        "calories": float(cal),
        "protein": float(protein),
        "carbs": float(carbs),
        "fat": float(fat),
        "fiber": float(fiber),
    }


def ing(name: str, qty: float, unit: str) -> Dict[str, Any]:
    return {"product_name": name, "quantity": qty, "unit": unit}


def pick2(rng: random.Random, items: List[str]) -> Tuple[str, str]:
    a = rng.choice(items)
    b = rng.choice([x for x in items if x != a])
    return a, b


def ensure_all_products_exist(product_set: Set[str], ingredients: List[Dict[str, Any]]) -> None:
    missing = [i["product_name"] for i in ingredients if i["product_name"] not in product_set]
    if missing:
        raise ValueError(f"Missing products in seed catalog: {sorted(set(missing))}")


_GEN_SUFFIX_RE = re.compile(r"\s#\d+$")


def is_generated_name(name: str) -> bool:
    return bool(_GEN_SUFFIX_RE.search(name))


def normalize_generated_name(name: str) -> str:
    """Remove the old numeric suffix used by an earlier generator run."""
    return _GEN_SUFFIX_RE.sub("", name).strip()


def make_unique_name(base: str, existing: Set[str]) -> str:
    """
    Ensure a stable, user-friendly unique name without using '#'.
    If collision occurs, append ' (Variation N)'.
    """
    if base not in existing:
        return base
    i = 2
    while True:
        candidate = f"{base} (Variation {i})"
        if candidate not in existing:
            return candidate
        i += 1


def make_breakfast(rng: random.Random, product_set: Set[str], n: int) -> Dict[str, Any]:
    fruits = ["Blueberries", "Strawberries", "Bananas", "Apples", "Oranges", "Kiwi", "Mangoes", "Pineapple"]
    nuts = ["Almonds", "Walnuts", "Cashews", "Peanuts", "Pumpkin Seeds", "Sunflower Seeds", "Chia Seeds", "Flax Seeds"]
    veg = ["Spinach", "Tomatoes", "Onion", "Bell Peppers", "Mushrooms", "Kale"]
    cuisines = ["American", "Mediterranean", "Mexican", "French", "Asian", "Indian"]

    style = rng.choice(["oats", "eggs", "yogurt", "toast", "quinoa"])
    cuisine = rng.choice(cuisines)

    if style == "oats":
        f = rng.choice(fruits)
        nut = rng.choice(nuts)
        name = f"{cuisine} Overnight Oats with {f} and {nut}"
        ingredients = [
            ing("Oats", 80, "g"),
            ing(rng.choice(["Milk", "Almond Milk", "Oat Milk"]), 180, "ml"),
            ing(f, 120, "g"),
            ing(nut, 20, "g"),
            ing("Honey", 12, "ml"),
        ]
        instructions = "1. Mix oats and milk. 2. Stir in honey. 3. Refrigerate overnight. 4. Top with fruit and nuts."
        tags = ["vegetarian"]
        if "Milk" not in {ingredients[1]["product_name"]}:
            tags.append("vegan")
        high_fiber = True
        high_protein = False
        prep, cook = 8, 0

    elif style == "eggs":
        v1, v2 = pick2(rng, veg)
        name = f"{cuisine} Veggie Egg Scramble with {v1} and {v2}"
        ingredients = [
            ing("Eggs", 3, "g"),
            ing(v1, 80, "g"),
            ing(v2, 60, "g"),
            ing("Olive Oil", 10, "ml"),
            ing("Salt", 2, "g"),
            ing("Black Pepper", 1, "g"),
        ]
        instructions = "1. Sauté vegetables in oil. 2. Add beaten eggs. 3. Cook gently until set. 4. Season and serve."
        tags = ["vegetarian", "high_protein", "gluten_free"]
        high_fiber = False
        high_protein = True
        prep, cook = 10, 8

    elif style == "yogurt":
        f1, f2 = pick2(rng, fruits)
        nut = rng.choice(nuts)
        name = f"{cuisine} Yogurt Bowl with {f1} and {f2}"
        ingredients = [
            ing("Greek Yogurt", 180, "g"),
            ing(f1, 80, "g"),
            ing(f2, 80, "g"),
            ing(nut, 15, "g"),
            ing("Honey", 10, "ml"),
        ]
        instructions = "1. Add yogurt to a bowl. 2. Top with fruit and nuts. 3. Drizzle with honey."
        tags = ["vegetarian", "high_protein", "gluten_free"]
        high_fiber = False
        high_protein = True
        prep, cook = 6, 0

    elif style == "toast":
        v = rng.choice(veg)
        name = f"{cuisine} Avocado Toast with {v}"
        ingredients = [
            ing("Whole Grain Bread", 60, "g"),
            ing("Avocado", 100, "g"),
            ing(v, 50, "g"),
            ing("Lemon Juice", 8, "ml"),
            ing("Salt", 2, "g"),
            ing("Black Pepper", 1, "g"),
        ]
        instructions = "1. Toast bread. 2. Mash avocado with lemon, salt, and pepper. 3. Spread on toast and top with vegetables."
        tags = ["vegetarian", "vegan"]
        high_fiber = True
        high_protein = False
        prep, cook = 8, 3

    else:  # quinoa
        f = rng.choice(fruits)
        nut = rng.choice(nuts)
        name = f"{cuisine} Breakfast Quinoa with {f} and {nut}"
        ingredients = [
            ing("Quinoa", 70, "g"),
            ing(rng.choice(["Milk", "Almond Milk", "Oat Milk"]), 220, "ml"),
            ing(f, 120, "g"),
            ing(nut, 15, "g"),
            ing("Honey", 12, "ml"),
            ing("Cinnamon", 2, "g"),
        ]
        instructions = "1. Simmer quinoa in milk until tender. 2. Stir in cinnamon and honey. 3. Top with fruit and nuts."
        tags = ["vegetarian", "gluten_free"]
        if ingredients[1]["product_name"] != "Milk":
            tags.append("vegan")
        high_fiber = True
        high_protein = False
        prep, cook = 6, 18

    ensure_all_products_exist(product_set, ingredients)
    return {
        "name": name,
        "description": "A quick, balanced breakfast with mixed flavors.",
        "instructions": instructions,
        "meal_types": ["breakfast"],
        "cuisine_type": cuisine,
        "dietary_tags": tags,
        "prep_time_minutes": prep,
        "cook_time_minutes": cook,
        "total_servings": 1.0,
        "nutritional_info_per_serving": nutrition_for(
            rng, "breakfast", high_protein=("high_protein" in tags), high_fiber=high_fiber
        ),
        "ingredients": ingredients,
    }


def make_lunch(rng: random.Random, product_set: Set[str], n: int) -> Dict[str, Any]:
    cuisines = ["American", "Mediterranean", "Mexican", "Italian", "Asian", "Indian", "French", "Middle Eastern"]
    proteins = ["Chicken Breast", "Turkey Breast", "Tofu", "Tempeh", "Shrimp", "Salmon Fillet", "Cod Fillet", "Chickpeas"]
    grains = ["Brown Rice", "White Rice", "Quinoa", "Couscous", "Bulgur", "Farro", "Barley"]
    greens = ["Lettuce", "Romaine Lettuce", "Arugula", "Kale", "Spinach"]
    veg = ["Tomatoes", "Cucumber", "Bell Peppers", "Onion", "Carrots", "Broccoli", "Zucchini", "Mushrooms"]

    cuisine = rng.choice(cuisines)
    style = rng.choice(["bowl", "salad", "wrap", "soup"])
    protein = rng.choice(proteins)

    tags: List[str] = []
    high_protein = protein in {"Chicken Breast", "Turkey Breast", "Shrimp", "Salmon Fillet", "Cod Fillet", "Tempeh", "Tofu"}
    if protein in {"Tofu", "Tempeh", "Chickpeas"}:
        tags.append("vegetarian")
        if protein != "Chickpeas":
            tags.append("vegan")
    if protein in {"Shrimp", "Salmon Fillet", "Cod Fillet"}:
        tags.append("gluten_free")

    if style == "bowl":
        grain = rng.choice(grains)
        v1, v2 = pick2(rng, veg)
        name = f"{cuisine} {protein} Grain Bowl with {v1} and {v2}"
        ingredients = [
            ing(grain, 130, "g"),
            ing(protein, 150, "g"),
            ing(v1, 100, "g"),
            ing(v2, 80, "g"),
            ing("Olive Oil", 12, "ml"),
            ing(rng.choice(["Lemon Juice", "Soy Sauce", "Tahini"]), 15, "ml"),
        ]
        instructions = "1. Cook grain. 2. Cook protein and vegetables. 3. Assemble bowl and drizzle with dressing."
        prep, cook = 15, 20

    elif style == "salad":
        g = rng.choice(greens)
        v1, v2 = pick2(rng, veg)
        name = f"{cuisine} {protein} Salad with {v1} and {v2}"
        ingredients = [
            ing(g, 120, "g"),
            ing(protein, 150, "g"),
            ing(v1, 90, "g"),
            ing(v2, 90, "g"),
            ing("Olive Oil", 12, "ml"),
            ing("Lemon Juice", 10, "ml"),
        ]
        instructions = "1. Cook protein if needed. 2. Chop vegetables. 3. Toss with olive oil and lemon juice."
        prep, cook = 15, 12

    elif style == "wrap":
        v1, v2 = pick2(rng, veg)
        name = f"{cuisine} {protein} Wrap with {v1} and {v2}"
        ingredients = [
            ing("Tortillas", 80, "g"),
            ing(protein, 140, "g"),
            ing(v1, 70, "g"),
            ing(v2, 70, "g"),
            ing(rng.choice(["Mayonnaise", "Tahini", "Sriracha"]), 12, "ml"),
        ]
        instructions = "1. Cook protein if needed. 2. Warm tortilla. 3. Add fillings and roll into a wrap."
        prep, cook = 12, 10

    else:  # soup (lighter lunch option)
        v1, v2 = pick2(rng, veg)
        broth = rng.choice(["Vegetable Broth", "Chicken Broth", "Beef Broth"])
        name = f"{cuisine} {protein} Vegetable Soup with {v1} and {v2}"
        ingredients = [
            ing(protein, 120, "g"),
            ing(v1, 120, "g"),
            ing(v2, 120, "g"),
            ing("Onion", 80, "g"),
            ing(broth, 450, "ml"),
            ing("Olive Oil", 10, "ml"),
        ]
        instructions = "1. Sauté onion and vegetables. 2. Add broth and protein. 3. Simmer until tender and serve."
        prep, cook = 15, 25

    ensure_all_products_exist(product_set, ingredients)
    # Normalize tags: avoid duplicates, keep stable order-ish
    tags = list(dict.fromkeys(tags + (["high_protein"] if high_protein else [])))
    return {
        "name": name,
        "description": "A satisfying midday meal with mixed cuisines.",
        "instructions": instructions,
        "meal_types": ["lunch"],
        "cuisine_type": cuisine,
        "dietary_tags": tags,
        "prep_time_minutes": prep,
        "cook_time_minutes": cook,
        "total_servings": 1.0,
        "nutritional_info_per_serving": nutrition_for(rng, "lunch", high_protein=high_protein, high_fiber=False),
        "ingredients": ingredients,
    }


def make_light_dinner(rng: random.Random, product_set: Set[str], n: int) -> Dict[str, Any]:
    cuisines = ["American", "Mediterranean", "Mexican", "Italian", "Asian", "Indian", "French", "Japanese", "Thai"]
    proteins = ["Chicken Breast", "Tofu", "Tempeh", "Shrimp", "Salmon Fillet", "Cod Fillet", "Chickpeas", "Greek Yogurt"]
    veg = ["Broccoli", "Bok Choy", "Zucchini", "Mushrooms", "Spinach", "Carrots", "Bell Peppers", "Cauliflower"]
    bases = ["Brown Rice", "Quinoa", "Couscous", "Barley", "Wild Rice"]

    cuisine = rng.choice(cuisines)
    style = rng.choice(["salad", "stirfry", "broth_bowl"])
    protein = rng.choice(proteins)

    tags: List[str] = []
    high_protein = protein in {"Chicken Breast", "Shrimp", "Salmon Fillet", "Cod Fillet", "Tempeh", "Tofu", "Greek Yogurt"}
    if protein in {"Tofu", "Tempeh", "Chickpeas", "Greek Yogurt"}:
        tags.append("vegetarian")
        if protein in {"Tofu", "Tempeh"}:
            tags.append("vegan")

    if style == "salad":
        v1, v2 = pick2(rng, veg)
        greens = rng.choice(["Arugula", "Spinach", "Romaine Lettuce", "Lettuce"])
        name = f"{cuisine} Light {protein} Salad with {v1} and {v2}"
        ingredients = [
            ing(greens, 120, "g"),
            ing(protein, 140, "g"),
            ing(v1, 90, "g"),
            ing(v2, 90, "g"),
            ing("Olive Oil", 10, "ml"),
            ing("Lemon Juice", 10, "ml"),
        ]
        instructions = "1. Cook protein if needed. 2. Chop vegetables. 3. Toss with olive oil and lemon. 4. Serve."
        prep, cook = 12, 10

    elif style == "stirfry":
        v1, v2 = pick2(rng, veg)
        base = rng.choice(bases)
        sauce = rng.choice(["Soy Sauce", "Miso Paste", "Sriracha"])
        oil = rng.choice(["Sesame Oil", "Olive Oil"])
        name = f"{cuisine} Light {protein} Stir Fry with {v1} and {v2}"
        ingredients = [
            ing(base, 120, "g"),
            ing(protein, 150, "g"),
            ing(v1, 120, "g"),
            ing(v2, 100, "g"),
            ing(oil, 10, "ml"),
            ing(sauce, 15, "ml"),
        ]
        instructions = "1. Cook base. 2. Stir-fry vegetables and protein in oil. 3. Add sauce. 4. Serve over base."
        prep, cook = 15, 15

    else:  # broth bowl
        v1, v2 = pick2(rng, veg)
        broth = rng.choice(["Vegetable Broth", "Chicken Broth"])
        name = f"{cuisine} Light Broth Bowl with {protein}, {v1}, and {v2}"
        ingredients = [
            ing(broth, 450, "ml"),
            ing(protein, 140, "g"),
            ing(v1, 120, "g"),
            ing(v2, 120, "g"),
            ing("Ginger", 5, "g"),
            ing("Soy Sauce", 10, "ml"),
        ]
        instructions = "1. Bring broth to a simmer with ginger and soy sauce. 2. Add vegetables and protein. 3. Simmer briefly and serve."
        prep, cook = 12, 15

    ensure_all_products_exist(product_set, ingredients)
    tags = list(dict.fromkeys(tags + (["high_protein"] if high_protein else [])))
    # keep lighter meals often gluten-free (best-effort)
    if "gluten_free" not in tags and rng.random() < 0.35:
        tags.append("gluten_free")

    return {
        "name": name,
        "description": "A lighter late meal (supper) with varied cuisines.",
        "instructions": instructions,
        "meal_types": ["dinner"],
        "cuisine_type": cuisine,
        "dietary_tags": tags,
        "prep_time_minutes": prep,
        "cook_time_minutes": cook,
        "total_servings": 1.0,
        "nutritional_info_per_serving": nutrition_for(rng, "dinner", high_protein=high_protein, high_fiber=False),
        "ingredients": ingredients,
    }


def make_dessert(rng: random.Random, product_set: Set[str], n: int) -> Dict[str, Any]:
    cuisines = ["American", "French", "Mediterranean", "Italian", "Middle Eastern", "Asian"]
    fruits = ["Apples", "Bananas", "Oranges", "Pineapple", "Mangoes", "Pears", "Grapes", "Kiwi", "Strawberries"]
    nuts = ["Almonds", "Walnuts", "Cashews", "Peanuts", "Coconut", "Chia Seeds"]

    cuisine = rng.choice(cuisines)
    style = rng.choice(["baked_fruit", "chia_pudding", "yogurt_parfait", "date_bites"])

    if style == "baked_fruit":
        fruit = rng.choice([f for f in fruits if f in {"Apples", "Pears"}])
        name = f"{cuisine} Baked {fruit[:-1]} with Honey and Cinnamon"
        ingredients = [
            ing(fruit, 200, "g"),
            ing("Honey", 15, "ml"),
            ing("Cinnamon", 2, "g"),
            ing("Walnuts", 15, "g"),
        ]
        instructions = "1. Slice fruit. 2. Bake until tender. 3. Drizzle with honey, sprinkle cinnamon, and top with walnuts."
        prep, cook = 8, 15
        tags = ["vegetarian", "gluten_free"]
        high_fiber = True
        high_protein = False

    elif style == "chia_pudding":
        fruit = rng.choice(fruits)
        name = f"{cuisine} Chia Pudding with {fruit} and Coconut"
        ingredients = [
            ing("Chia Seeds", 35, "g"),
            ing(rng.choice(["Almond Milk", "Oat Milk", "Soy Milk"]), 220, "ml"),
            ing("Honey", 12, "ml"),
            ing(fruit, 120, "g"),
            ing("Coconut", 15, "g"),
        ]
        instructions = "1. Mix chia seeds, milk, and honey. 2. Refrigerate until thick. 3. Top with fruit and coconut."
        prep, cook = 8, 0
        tags = ["vegetarian", "vegan", "gluten_free"]
        high_fiber = True
        high_protein = False

    elif style == "yogurt_parfait":
        f1, f2 = pick2(rng, fruits)
        nut = rng.choice(nuts)
        name = f"{cuisine} Yogurt Parfait with {f1}, {f2}, and {nut}"
        ingredients = [
            ing("Greek Yogurt", 180, "g"),
            ing(f1, 80, "g"),
            ing(f2, 80, "g"),
            ing("Honey", 10, "ml"),
            ing(nut, 15, "g"),
        ]
        instructions = "1. Layer yogurt and fruit. 2. Drizzle with honey. 3. Top with nuts."
        prep, cook = 6, 0
        tags = ["vegetarian", "high_protein", "gluten_free"]
        high_fiber = False
        high_protein = True

    else:  # date bites
        nut = rng.choice(nuts)
        name = f"{cuisine} Date and {nut} Dessert Bites"
        ingredients = [
            ing("Dates", 120, "g"),
            ing(nut, 40, "g"),
            ing("Coconut", 20, "g"),
            ing("Cinnamon", 2, "g"),
        ]
        instructions = "1. Blend dates and nuts. 2. Form into bite-size balls. 3. Roll in coconut and chill."
        prep, cook = 12, 0
        tags = ["vegetarian", "vegan", "gluten_free"]
        high_fiber = True
        high_protein = False

    ensure_all_products_exist(product_set, ingredients)
    return {
        "name": name,
        "description": "A dessert-style snack with a mixed cuisine influence.",
        "instructions": instructions,
        "meal_types": ["snack"],
        "cuisine_type": cuisine,
        "dietary_tags": tags,
        "prep_time_minutes": prep,
        "cook_time_minutes": cook,
        "total_servings": 1.0,
        "nutritional_info_per_serving": nutrition_for(
            rng, "snack", high_protein=high_protein, high_fiber=high_fiber
        ),
        "ingredients": ingredients,
    }


def extend_recipes_to_minimums(
    *,
    target_breakfast: int = 50,
    target_lunch: int = 50,
    target_dinner: int = 50,
    target_snack: int = 30,
    seed: int = 42,
) -> None:
    products = load_json(PRODUCTS_FILE)
    product_set = product_names(products)

    recipes_all: List[Dict[str, Any]] = load_json(RECIPES_FILE)
    # Keep "base" recipes and rebuild previously generated additions (if any).
    base_recipes = [
        r for r in recipes_all if not is_generated_name(str(r.get("name", "")))
    ]
    recipes: List[Dict[str, Any]] = base_recipes

    existing_names: Set[str] = {str(r.get("name")) for r in recipes if r.get("name")}

    rng = random.Random(seed)

    def add_unique(recipe: Dict[str, Any]) -> None:
        base_name = normalize_generated_name(str(recipe["name"]))
        final_name = make_unique_name(base_name, existing_names)
        recipe["name"] = final_name
        recipes.append(recipe)
        existing_names.add(final_name)

    counts = meal_type_counts(recipes)

    # Append breakfast
    i = 1
    while counts["breakfast"] < target_breakfast:
        r = make_breakfast(rng, product_set, i)
        add_unique(r)
        counts = meal_type_counts(recipes)
        i += 1

    # Append lunch (midday dinner)
    i = 1
    while counts["lunch"] < target_lunch:
        r = make_lunch(rng, product_set, i)
        add_unique(r)
        counts = meal_type_counts(recipes)
        i += 1

    # Append dinner (light supper)
    i = 1
    while counts["dinner"] < target_dinner:
        r = make_light_dinner(rng, product_set, i)
        add_unique(r)
        counts = meal_type_counts(recipes)
        i += 1

    # Append snack (desserts)
    i = 1
    while counts["snack"] < target_snack:
        r = make_dessert(rng, product_set, i)
        add_unique(r)
        counts = meal_type_counts(recipes)
        i += 1

    save_json(RECIPES_FILE, recipes)

    final_counts = meal_type_counts(recipes)
    print("✅ Updated sample-recipes.json")
    print(f"Total recipes: {len(recipes)}")
    print("Meal type counts:", dict(final_counts))


if __name__ == "__main__":
    extend_recipes_to_minimums()

