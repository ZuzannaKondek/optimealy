"""Product service for querying products."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.product import Product


class ProductService:
    """Service for handling product queries."""

    @staticmethod
    async def get_all_products(
        db: AsyncSession,
        limit: int = 1000,
        offset: int = 0,
    ) -> List[Product]:
        """
        Get all products with pagination.
        
        Args:
            db: Database session
            limit: Maximum number of products to return
            offset: Number of products to skip
            
        Returns:
            List of Product objects
        """
        stmt = (
            select(Product)
            .limit(limit)
            .offset(offset)
            .order_by(Product.name)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_product_by_id(
        db: AsyncSession,
        product_id: str,
    ) -> Optional[Product]:
        """
        Get a product by its ID.
        
        Args:
            db: Database session
            product_id: UUID of the product
            
        Returns:
            Product object if found, None otherwise
        """
        stmt = select(Product).where(Product.id == product_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_products_by_ids(
        db: AsyncSession,
        product_ids: List[str],
    ) -> List[Product]:
        """
        Get multiple products by their IDs.
        
        Args:
            db: Database session
            product_ids: List of product UUIDs
            
        Returns:
            List of Product objects
        """
        if not product_ids:
            return []
        
        stmt = select(Product).where(Product.id.in_(product_ids))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_products_by_category(
        db: AsyncSession,
        category: str,
        limit: int = 100,
    ) -> List[Product]:
        """
        Get products by category.
        
        Args:
            db: Database session
            category: Product category
            limit: Maximum number of products to return
            
        Returns:
            List of Product objects
        """
        stmt = (
            select(Product)
            .where(Product.category == category)
            .limit(limit)
            .order_by(Product.name)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def search_products(
        db: AsyncSession,
        search_term: str,
        limit: int = 50,
    ) -> List[Product]:
        """
        Search products by name.
        
        Args:
            db: Database session
            search_term: Search term to match against product names
            limit: Maximum number of products to return
            
        Returns:
            List of Product objects matching the search term
        """
        stmt = (
            select(Product)
            .where(Product.name.ilike(f"%{search_term}%"))
            .limit(limit)
            .order_by(Product.name)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
