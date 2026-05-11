"""
Database seeding script for OptiMeal application.

Loads sample recipes and products from JSON files into the database.

Usage:
    python -m src.database.seed
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import AsyncSessionLocal, close_db
from src.models.enums import MealType, RecipeDifficulty, ProductCategory, Perishability
from src.models.product import Product
from src.models.product_alias import ProductAlias
from src.services.product_service import ProductService
from src.utils.canonical import canonicalize_string


async def load_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """Load data from a JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)


async def _ensure_alias(db: AsyncSession, alias_value: str, product_id: UUID) -> None:
    """Ensure an alias entry exists for the provided value."""

    alias_key = canonicalize_string(alias_value)
    if not alias_key:
        return

    stmt = select(ProductAlias).where(ProductAlias.alias == alias_key)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        return

    db.add(ProductAlias(alias=alias_key, product_id=product_id))


async def seed_products(db: AsyncSession) -> Dict[str, Any]:
    """Seed products from sample-products.json."""
    print("🌱 Seeding products...")

    data_dir = Path(__file__).parent.parent.parent / "data" / "products"
    products_file = data_dir / "sample-products.json"
    if not products_file.exists():
        print(f"❌ Products file not found: {products_file}")
        return {}

    products_data = await load_json_file(products_file)

    result = await db.execute(select(func.count(Product.id)))
    existing_count = result.scalar() or 0

    if existing_count > 0:
        print(f"⏭️  {existing_count} products already exist, loading for lookup...")
        result = await db.execute(select(Product))
        existing_products = result.scalars().all()
        lookup: Dict[str, Product] = {}

        for product in existing_products:
            canonical = product.canonical_key or canonicalize_string(product.name)
            if not product.canonical_key:
                product.canonical_key = canonical
            await _ensure_alias(db, product.name, product.id)
            lookup[canonical] = product

        await db.flush()
        return lookup

    product_lookup: Dict[str, Product] = {}
    seen_names = set()
    inserted_count = 0

    for product_data in products_data:
        product_name = product_data["name"]
        if product_name in seen_names:
            continue
        seen_names.add(product_name)

        canonical = canonicalize_string(product_name)
        if canonical in product_lookup:
            continue

        result = await db.execute(select(Product).where(Product.canonical_key == canonical))
        existing = result.scalar_one_or_none()

        if existing:
            product_lookup[canonical] = existing
            continue

        product = Product(
            name=product_name,
            canonical_key=canonical,
            category=product_data["category"],
            nutritional_info_per_100g=product_data["nutritional_info_per_100g"],
            common_package_sizes=product_data.get("common_package_sizes", []),
            standard_unit=product_data.get("standard_unit", "g"),
            shelf_life_days=product_data.get("shelf_life_days", 7),
            perishability=product_data.get("perishability", "moderate"),
            storage_requirements=product_data.get("storage_requirements"),
            unit_conversions=product_data.get("unit_conversions", {}),
            price_per_unit=product_data.get("price_per_unit"),
        )
        db.add(product)
        await db.flush()

        await _ensure_alias(db, product_name, product.id)
        for alias_value in product_data.get("aliases", []):
            await _ensure_alias(db, alias_value, product.id)

        product_lookup[canonical] = product
        inserted_count += 1

    await db.flush()
    print(f"✅ Seeded {inserted_count} products")

    return product_lookup


async def seed_recipes(db: AsyncSession, product_lookup: Dict[str, Any]) -> None:
    """Seed recipes from recipes-new-meal-types.json."""
    print("🌱 Seeding recipes...")

    from src.models.recipe import Recipe
    from src.models.recipe_ingredient import RecipeIngredient

    data_dir = Path(__file__).parent.parent.parent / "data" / "recipes"
    recipes_file = data_dir / "recipes-new-meal-types.json"
    if not recipes_file.exists():
        print(f"❌ Recipes file not found: {recipes_file}")
        return

    recipes_data = await load_json_file(recipes_file)

    # If recipes already exist, we still want to add any new ones from the JSON
    # (seed should be additive, like products seeding).
    result = await db.execute(select(func.count(Recipe.id)))
    existing_count = result.scalar() or 0
    if existing_count > 0:
        print(
            f"ℹ️  {existing_count} recipes already exist, adding any missing recipes from seed data..."
        )

    inserted_count = 0

    for recipe_data in recipes_data:
        # Check if recipe already exists
        result = await db.execute(select(Recipe).where(Recipe.name == recipe_data["name"]))
        existing = result.scalar_one_or_none()

        if existing:
            continue

        # Create recipe (nutritional_info_per_serving is now calculated dynamically from ingredients)
        recipe = Recipe(
            name=recipe_data["name"],
            description=recipe_data.get("description"),
            instructions=recipe_data.get("instructions", ""),
            meal_types=recipe_data.get("meal_types", []),
            cuisine_type=recipe_data.get("cuisine_type"),
            dietary_tags=recipe_data.get("dietary_tags", []),
            prep_time_minutes=recipe_data.get("prep_time_minutes"),
            cook_time_minutes=recipe_data.get("cook_time_minutes"),
            total_servings=float(recipe_data.get("total_servings", 1.0)),
            serving_size_unit=recipe_data.get("serving_size_unit"),
            serving_size_value=recipe_data.get("serving_size_value"),
            difficulty=recipe_data.get("difficulty", "medium"),
            popularity_score=float(recipe_data.get("popularity_score", 0.5)),
        )
        db.add(recipe)
        await db.flush()

        # Create recipe ingredients
        # Track added ingredients to avoid duplicates within the same recipe
        added_products = set()

        for ingredient_data in recipe_data.get("ingredients", []):
            product_name = ingredient_data.get("product_name")
            if not product_name:
                raise ValueError(
                    f"Recipe '{recipe_data.get('name')}' contains an ingredient without a product_name"
                )

            canonical = canonicalize_string(product_name)
            product = product_lookup.get(canonical)

            if not product:
                product = await ProductService.resolve_product_identifier(db, product_name)

            if not product:
                raise ValueError(
                    f"Product '{product_name}' not found while seeding recipe '{recipe_data.get('name')}'"
                )

            product_lookup[canonical] = product

            # Skip if we already added this product to this recipe in this batch
            if product.id in added_products:
                print(
                    f"⚠️  Duplicate ingredient '{product_name}' in recipe '{recipe.name}', using first occurrence only"
                )
                continue

            # Check if ingredient link already exists in database
            result = await db.execute(
                select(RecipeIngredient).where(
                    RecipeIngredient.recipe_id == recipe.id,
                    RecipeIngredient.product_id == product.id,
                )
            )
            existing_ingredient = result.scalar_one_or_none()

            if existing_ingredient:
                added_products.add(product.id)
                continue

            ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                product_id=product.id,
                quantity_value=float(ingredient_data.get("quantity", 0)),
                quantity_unit=ingredient_data.get("unit", "g"),
                is_essential=True,
            )
            db.add(ingredient)
            added_products.add(product.id)

        inserted_count += 1

    await db.flush()
    print(f"✅ Seeded {inserted_count} recipes")


async def main() -> None:
    """Main seeding function."""
    print("🚀 Starting database seeding...")

    async with AsyncSessionLocal() as db:
        try:
            product_lookup = await seed_products(db)
            await seed_recipes(db, product_lookup or {})

            await db.commit()
            print("✅ Database seeding completed successfully!")

        except Exception as e:
            await db.rollback()
            print(f"❌ Error during seeding: {e}")
            import traceback

            traceback.print_exc()
            raise
        finally:
            await close_db()


if __name__ == "__main__":
    asyncio.run(main())
