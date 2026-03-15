"""Pantry Management API

Endpoints for managing user pantry items (ingredients they already have).
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db
from src.models.user_pantry_item import UserPantryItem
from src.models.product import Product
from src.models.user import User
from src.api.middleware.auth import get_current_user
from src.config.pantry_staples import PANTRY_STAPLES
from src.services.product_service import ProductService


router = APIRouter(prefix="/pantry", tags=["pantry"])


# Request/Response Models
class PantryItemResponse(BaseModel):
    """Response model for a pantry item"""

    product_id: str
    product_name: str
    quantity_g: float
    category: str
    expiry_date: Optional[str] = None

    class Config:
        from_attributes = True


class PantryStapleResponse(BaseModel):
    """Response model for available pantry staples"""

    product_id: str
    product_name: str
    category: str
    default_quantity_g: float
    icon: str  # Emoji or icon identifier


class ProductSearchResult(BaseModel):
    """Response model for product search results"""

    product_id: str
    product_name: str
    category: str
    unit: str


class PantryItemInput(BaseModel):
    """Input model for a pantry item"""

    product_id: str
    quantity_g: float
    expiry_date: Optional[str] = None


class UpdatePantryRequest(BaseModel):
    """Request to update user's pantry"""

    items: List[PantryItemInput]  # List of pantry items with quantities


@router.get("", response_model=List[PantryItemResponse])
async def get_user_pantry(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Get current user's pantry items.

    Returns list of products the user has marked as available in their pantry.
    """
    # Query user's pantry items with product details
    query = (
        select(UserPantryItem, Product)
        .join(Product, UserPantryItem.product_id == Product.id)
        .where(UserPantryItem.user_id == current_user.id)
    )

    result = await db.execute(query)
    items = result.all()

    return [
        PantryItemResponse(
            product_id=str(pantry_item.product_id),
            product_name=product.name,
            quantity_g=float(pantry_item.quantity_g),
            category=product.category,
            expiry_date=pantry_item.expiry_date.isoformat() if pantry_item.expiry_date else None,
        )
        for pantry_item, product in items
    ]


@router.get("/staples", response_model=List[PantryStapleResponse])
async def get_pantry_staples(
    db: AsyncSession = Depends(get_db),
):
    """
    Get curated list of common pantry staples.

    Returns pre-selected common items that users typically have in their pantry.
    """
    # Query products that match our staples list
    query = select(Product).where(Product.name.in_(PANTRY_STAPLES))
    result = await db.execute(query)
    products = result.scalars().all()

    # Map to response with default quantities
    staples = []
    for product in products:
        # Use first common package size as default
        default_qty = product.common_package_sizes[0] if product.common_package_sizes else 500.0

        # Simple icon mapping based on category
        icon_map = {
            "oil": "🫒",
            "condiment": "🧂",
            "spice": "🌶️",
            "herb": "🌿",
            "grain": "🌾",
            "dairy": "🥛",
            "protein": "🥚",
            "vegetable": "🥕",
        }
        icon = icon_map.get(product.category, "🥫")

        staples.append(
            PantryStapleResponse(
                product_id=str(product.id),
                product_name=product.name,
                category=product.category,
                default_quantity_g=float(default_qty),
                icon=icon,
            )
        )

    return staples


@router.put("", response_model=dict)
async def update_user_pantry(
    request: UpdatePantryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user's pantry items with quantities.

    Merges the provided items with existing pantry items (adds quantities for items
    that already exist, adds new items for those that don't).
    """
    # Validate that all product IDs exist
    product_ids = [UUID(item.product_id) for item in request.items]
    query = select(Product).where(Product.id.in_(product_ids))
    result = await db.execute(query)
    products = {str(p.id): p for p in result.scalars().all()}

    if len(products) != len(product_ids):
        raise HTTPException(status_code=400, detail="One or more invalid product IDs")

    # Validate quantities are positive
    for item in request.items:
        if item.quantity_g <= 0:
            raise HTTPException(
                status_code=400, detail=f"Quantity must be positive for product {item.product_id}"
            )

    # Get existing pantry items for this user
    existing_stmt = select(UserPantryItem).where(UserPantryItem.user_id == current_user.id)
    existing_result = await db.execute(existing_stmt)
    existing_items = {str(item.product_id): item for item in existing_result.scalars().all()}

    # Process items: merge quantities for existing items, add new items
    from datetime import date

    # Track product IDs that were in the request
    requested_product_ids = {item.product_id for item in request.items}

    for item in request.items:
        product_id = item.product_id
        expiry = None
        if item.expiry_date:
            try:
                expiry = date.fromisoformat(item.expiry_date)
            except ValueError:
                pass  # Ignore invalid dates

        if product_id in existing_items:
            # Update existing pantry item - REPLACE the quantity (not add)
            existing_item = existing_items[product_id]
            existing_item.quantity_g = float(item.quantity_g)
            if expiry:
                existing_item.expiry_date = expiry
        else:
            # Add new pantry item
            pantry_item = UserPantryItem(
                user_id=current_user.id,
                product_id=UUID(product_id),
                quantity_g=item.quantity_g,
                expiry_date=expiry,
            )
            db.add(pantry_item)

    # Remove items that were deleted on the client (not in request)
    for product_id, existing_item in existing_items.items():
        if product_id not in requested_product_ids:
            await db.delete(existing_item)

    await db.commit()

    return {"message": "Pantry updated successfully", "items_count": len(request.items)}


@router.get("/products/search", response_model=List[ProductSearchResult])
async def search_products(q: str, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """
    Search for products by name.

    Returns a list of products matching the search query.
    """
    if not q or len(q.strip()) < 2:
        return []

    products = await ProductService.search_products(db, q.strip(), limit)

    return [
        ProductSearchResult(
            product_id=str(product.id),
            product_name=product.name,
            category=product.category,
            unit=product.standard_unit or "g",
        )
        for product in products
    ]
