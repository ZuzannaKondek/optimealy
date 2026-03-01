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

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import AsyncSessionLocal
from src.models.enums import MealType, RecipeDifficulty, ProductCategory, Perishability


async def load_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """Load data from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


async def seed_products(db: AsyncSession) -> Dict[str, Any]:
    """Seed products from sample-products.json."""
    print("🌱 Seeding products...")
    
    from src.models.product import Product
    from sqlalchemy import select, func
    
    data_dir = Path(__file__).parent.parent.parent / "data" / "products"
    products_file = data_dir / "sample-products.json"
    
    if not products_file.exists():
        print(f"❌ Products file not found: {products_file}")
        return {}
    
    products_data = await load_json_file(products_file)
    
    # Check if products already exist
    result = await db.execute(select(func.count(Product.id)))
    existing_count = result.scalar()
    
    if existing_count > 0:
        print(f"⏭️  {existing_count} products already exist, loading for lookup...")
        # Load existing products for lookup
        result = await db.execute(select(Product))
        existing_products = result.scalars().all()
        return {p.name: p for p in existing_products}
    
    # Create product lookup by name
    product_lookup: Dict[str, Product] = {}
    
    # Track seen names to avoid duplicates within the same batch
    seen_names = set()
    
    for product_data in products_data:
        product_name = product_data["name"]
        
        # Skip if we've already processed this name in this batch
        if product_name in seen_names:
            continue
        seen_names.add(product_name)
        
        # Check if product already exists by name
        result = await db.execute(select(Product).where(Product.name == product_name))
        existing = result.scalar_one_or_none()
        
        if existing:
            product_lookup[product_name] = existing
            continue
        
        # Create new product
        product = Product(
            name=product_name,
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
        product_lookup[product_name] = product
    
    await db.flush()
    print(f"✅ Seeded {len(products_data)} products")
    
    return product_lookup


async def seed_recipes(db: AsyncSession, product_lookup: Dict[str, Any]) -> None:
    """Seed recipes from recipes-new-meal-types.json."""
    print("🌱 Seeding recipes...")
    
    from src.models.recipe import Recipe
    from src.models.recipe_ingredient import RecipeIngredient
    from sqlalchemy import select, func
    
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
        print(f"ℹ️  {existing_count} recipes already exist, adding any missing recipes from seed data...")
    
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
            if product_name not in product_lookup:
                print(f"⚠️  Product '{product_name}' not found, skipping ingredient")
                continue
            
            product = product_lookup[product_name]
            
            # Skip if we already added this product to this recipe in this batch
            if product.id in added_products:
                print(f"⚠️  Duplicate ingredient '{product_name}' in recipe '{recipe.name}', using first occurrence only")
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
    
    await db.flush()
    print(f"✅ Seeded {len(recipes_data)} recipes")


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


if __name__ == "__main__":
    asyncio.run(main())
