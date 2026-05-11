"""mysql initial schema

Revision ID: 20260506_2135
Revises:
Create Date: 2026-05-06 21:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260506_2135"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("canonical_key", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("nutritional_info_per_100g", sa.JSON(), nullable=False),
        sa.Column("common_package_sizes", sa.JSON(), nullable=False),
        sa.Column("allows_exact_quantity", sa.Boolean(), nullable=False),
        sa.Column("standard_unit", sa.String(length=20), nullable=False),
        sa.Column("price_per_unit", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("shelf_life_days", sa.Integer(), nullable=True),
        sa.Column("perishability", sa.String(length=20), nullable=False),
        sa.Column("storage_requirements", sa.Text(), nullable=True),
        sa.Column("unit_conversions", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_product_perishability", "products", ["perishability"], unique=False)
    op.create_index(op.f("ix_products_canonical_key"), "products", ["canonical_key"], unique=True)
    op.create_index(op.f("ix_products_category"), "products", ["category"], unique=False)
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)
    op.create_index(op.f("ix_products_name"), "products", ["name"], unique=True)

    op.create_table(
        "recipes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("meal_types", sa.JSON(), nullable=False),
        sa.Column("cuisine_type", sa.String(length=50), nullable=True),
        sa.Column("dietary_tags", sa.JSON(), nullable=False),
        sa.Column("prep_time_minutes", sa.Integer(), nullable=True),
        sa.Column("cook_time_minutes", sa.Integer(), nullable=True),
        sa.Column("total_servings", sa.Float(), nullable=False),
        sa.Column("serving_size_unit", sa.String(length=20), nullable=True),
        sa.Column("serving_size_value", sa.Float(), nullable=True),
        sa.Column("instructions_single_serving", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.String(length=20), nullable=False),
        sa.Column("popularity_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_recipe_popularity", "recipes", ["popularity_score"], unique=False)
    op.create_index(op.f("ix_recipes_id"), "recipes", ["id"], unique=False)
    op.create_index(op.f("ix_recipes_name"), "recipes", ["name"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("language_preference", sa.String(length=10), nullable=False),
        sa.Column("theme_preference", sa.Enum("LIGHT", "DARK", "SYSTEM", name="themetype"), nullable=False),
        sa.Column("unit_preference", sa.Enum("METRIC", "IMPERIAL", name="unitpreference"), nullable=False),
        sa.Column("notification_settings", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "meal_plans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("dishes_per_day", sa.Integer(), nullable=True),
        sa.Column("target_calories_per_day", sa.Integer(), nullable=False),
        sa.Column("target_protein_g", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("target_carbs_g", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("target_fat_g", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("user_constraints", sa.JSON(), nullable=False),
        sa.Column("optimization_status", sa.String(length=50), nullable=False),
        sa.Column("execution_status", sa.String(length=20), nullable=False, comment="Plan execution state: draft, active, completed, cancelled"),
        sa.Column("algorithm_execution_time_s", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("estimated_food_waste_g", sa.Numeric(precision=10, scale=2), nullable=True, comment="Perishable food waste in grams"),
        sa.Column("waste_reduction_percentage", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("pantry_additions_g", sa.Numeric(precision=10, scale=2), nullable=True, comment="Shelf-stable leftovers auto-added to pantry in grams"),
        sa.Column("estimated_total_cost", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meal_plans_created_at"), "meal_plans", ["created_at"], unique=False)
    op.create_index(op.f("ix_meal_plans_id"), "meal_plans", ["id"], unique=False)
    op.create_index(op.f("ix_meal_plans_optimization_status"), "meal_plans", ["optimization_status"], unique=False)
    op.create_index(op.f("ix_meal_plans_user_id"), "meal_plans", ["user_id"], unique=False)

    op.create_table(
        "product_aliases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("alias", sa.String(length=100), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_aliases_alias"), "product_aliases", ["alias"], unique=True)
    op.create_index(op.f("ix_product_aliases_product_id"), "product_aliases", ["product_id"], unique=False)

    op.create_table(
        "recipe_ingredients",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("recipe_id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("quantity_value", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("quantity_unit", sa.String(length=20), nullable=False),
        sa.Column("is_essential", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("recipe_id", "product_id", name="uq_recipe_product"),
    )
    op.create_index(op.f("ix_recipe_ingredients_product_id"), "recipe_ingredients", ["product_id"], unique=False)
    op.create_index(op.f("ix_recipe_ingredients_recipe_id"), "recipe_ingredients", ["recipe_id"], unique=False)

    op.create_table(
        "user_ingredient_preferences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("preference_type", sa.String(length=20), nullable=False),
        sa.Column("quantity_g", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_user_ingredient_preferences_product_id", "user_ingredient_preferences", ["product_id"], unique=False)
    op.create_index(op.f("ix_user_ingredient_preferences_user_id"), "user_ingredient_preferences", ["user_id"], unique=False)

    op.create_table(
        "user_pantry_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("quantity_g", sa.Numeric(precision=10, scale=2), nullable=False, comment="Quantity in grams (or ml for liquids)"),
        sa.Column("expiry_date", sa.Date(), nullable=True, comment="Optional expiry date for the item"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_pantry_items_user_id"), "user_pantry_items", ["user_id"], unique=False)

    op.create_table(
        "daily_menus",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("meal_plan_id", sa.Uuid(), nullable=False),
        sa.Column("day_number", sa.Integer(), nullable=False),
        sa.Column("menu_date", sa.Date(), nullable=False),
        sa.Column("actual_calories", sa.Integer(), nullable=False),
        sa.Column("actual_protein_g", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("actual_carbs_g", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("actual_fat_g", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["meal_plan_id"], ["meal_plans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_daily_menu_day_number", "daily_menus", ["day_number"], unique=False)
    op.create_index(op.f("ix_daily_menus_meal_plan_id"), "daily_menus", ["meal_plan_id"], unique=False)

    op.create_table(
        "grocery_lists",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("meal_plan_id", sa.Uuid(), nullable=False),
        sa.Column("total_items", sa.Integer(), nullable=False),
        sa.Column("estimated_total_cost", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("estimated_total_waste_g", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["meal_plan_id"], ["meal_plans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_grocery_lists_meal_plan_id"), "grocery_lists", ["meal_plan_id"], unique=True)

    op.create_table(
        "meals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("daily_menu_id", sa.Uuid(), nullable=False),
        sa.Column("recipe_id", sa.Uuid(), nullable=False),
        sa.Column("meal_type", sa.String(length=50), nullable=False, comment="Type of meal: breakfast, second_breakfast, dinner, dessert, or supper"),
        sa.Column("servings", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("dish_weight_g", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("calculated_nutritional_info", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["daily_menu_id"], ["daily_menus.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_meals_recipe_id", "meals", ["recipe_id"], unique=False)
    op.create_index(op.f("ix_meals_daily_menu_id"), "meals", ["daily_menu_id"], unique=False)

    op.create_table(
        "grocery_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("grocery_list_id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("required_quantity_g", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("purchase_quantity_g", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("purchase_unit", sa.String(length=20), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("estimated_item_cost", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("estimated_item_waste_g", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["grocery_list_id"], ["grocery_lists.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_grocery_items_product_id", "grocery_items", ["product_id"], unique=False)
    op.create_index(op.f("ix_grocery_items_grocery_list_id"), "grocery_items", ["grocery_list_id"], unique=False)

    op.create_table(
        "meal_completions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("meal_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ingredients_deducted", sa.JSON(), nullable=False, comment="Snapshot of ingredient quantities deducted: {product_id: quantity_g}"),
        sa.ForeignKeyConstraint(["meal_id"], ["meals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meal_completions_id"), "meal_completions", ["id"], unique=False)
    op.create_index(op.f("ix_meal_completions_meal_id"), "meal_completions", ["meal_id"], unique=False)
    op.create_index(op.f("ix_meal_completions_user_id"), "meal_completions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_meal_completions_user_id"), table_name="meal_completions")
    op.drop_index(op.f("ix_meal_completions_meal_id"), table_name="meal_completions")
    op.drop_index(op.f("ix_meal_completions_id"), table_name="meal_completions")
    op.drop_table("meal_completions")
    op.drop_index(op.f("ix_grocery_items_grocery_list_id"), table_name="grocery_items")
    op.drop_index("idx_grocery_items_product_id", table_name="grocery_items")
    op.drop_table("grocery_items")
    op.drop_index(op.f("ix_meals_daily_menu_id"), table_name="meals")
    op.drop_index("idx_meals_recipe_id", table_name="meals")
    op.drop_table("meals")
    op.drop_index(op.f("ix_grocery_lists_meal_plan_id"), table_name="grocery_lists")
    op.drop_table("grocery_lists")
    op.drop_index(op.f("ix_daily_menus_meal_plan_id"), table_name="daily_menus")
    op.drop_index("idx_daily_menu_day_number", table_name="daily_menus")
    op.drop_table("daily_menus")
    op.drop_index(op.f("ix_user_pantry_items_user_id"), table_name="user_pantry_items")
    op.drop_table("user_pantry_items")
    op.drop_index(op.f("ix_user_ingredient_preferences_user_id"), table_name="user_ingredient_preferences")
    op.drop_index("idx_user_ingredient_preferences_product_id", table_name="user_ingredient_preferences")
    op.drop_table("user_ingredient_preferences")
    op.drop_index(op.f("ix_recipe_ingredients_recipe_id"), table_name="recipe_ingredients")
    op.drop_index(op.f("ix_recipe_ingredients_product_id"), table_name="recipe_ingredients")
    op.drop_table("recipe_ingredients")
    op.drop_index(op.f("ix_product_aliases_product_id"), table_name="product_aliases")
    op.drop_index(op.f("ix_product_aliases_alias"), table_name="product_aliases")
    op.drop_table("product_aliases")
    op.drop_index(op.f("ix_meal_plans_user_id"), table_name="meal_plans")
    op.drop_index(op.f("ix_meal_plans_optimization_status"), table_name="meal_plans")
    op.drop_index(op.f("ix_meal_plans_id"), table_name="meal_plans")
    op.drop_index(op.f("ix_meal_plans_created_at"), table_name="meal_plans")
    op.drop_table("meal_plans")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_recipes_name"), table_name="recipes")
    op.drop_index(op.f("ix_recipes_id"), table_name="recipes")
    op.drop_index("idx_recipe_popularity", table_name="recipes")
    op.drop_table("recipes")
    op.drop_index(op.f("ix_products_name"), table_name="products")
    op.drop_index(op.f("ix_products_id"), table_name="products")
    op.drop_index(op.f("ix_products_category"), table_name="products")
    op.drop_index(op.f("ix_products_canonical_key"), table_name="products")
    op.drop_index("idx_product_perishability", table_name="products")
    op.drop_table("products")
