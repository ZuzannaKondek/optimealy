"""Authentication service for user registration and login."""
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
)


class AuthService:
    """Service for handling user authentication operations."""

    @staticmethod
    async def register_user(db: AsyncSession, email: str, password: str) -> User:
        """
        Register a new user.
        
        Args:
            db: Database session
            email: User's email address
            password: User's plain text password
            
        Returns:
            The created user
            
        Raises:
            ValueError: If email already exists
        """
        # Check if user already exists (case-insensitive check)
        # Normalize email to lowercase for comparison
        email_lower = email.lower().strip()
        
        # Use func.lower for case-insensitive comparison
        from sqlalchemy import func
        result = await db.execute(
            select(User).where(func.lower(User.email) == email_lower)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            # Log for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Registration attempt with existing email: {email_lower} "
                f"(found in DB: {existing_user.email}, id: {existing_user.id})"
            )
            raise ValueError("Email already registered")
        
        # Create new user (normalize email to lowercase)
        hashed_password = get_password_hash(password)
        new_user = User(
            email=email_lower,  # Store normalized email
            password_hash=hashed_password,
        )
        
        db.add(new_user)
        await db.flush()
        await db.refresh(new_user)
        
        return new_user

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str,
    ) -> Optional[User]:
        """
        Authenticate a user with email and password.
        
        Args:
            db: Database session
            email: User's email
            password: User's plain text password
            
        Returns:
            The authenticated user if credentials are valid, None otherwise
        """
        # Normalize email for lookup (case-insensitive)
        email_lower = email.lower().strip()
        from sqlalchemy import func
        result = await db.execute(
            select(User).where(func.lower(User.email) == email_lower)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user

    @staticmethod
    def create_tokens(user_id: str) -> Dict[str, str]:
        """
        Create access and refresh tokens for a user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Dictionary with access_token and refresh_token
        """
        access_token = create_access_token(data={"sub": str(user_id)})
        refresh_token = create_refresh_token(data={"sub": str(user_id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """
        Get a user by their ID.
        
        Args:
            db: Database session
            user_id: The user's ID
            
        Returns:
            The user if found, None otherwise
        """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_password(
        db: AsyncSession,
        user: User,
        current_password: str,
        new_password: str,
    ) -> bool:
        """
        Update a user's password.
        
        Args:
            db: Database session
            user: The user to update
            current_password: The current password for verification
            new_password: The new password
            
        Returns:
            True if password was updated, False if current password is incorrect
        """
        if not verify_password(current_password, user.password_hash):
            return False
        
        user.password_hash = get_password_hash(new_password)
        await db.flush()
        
        return True

    @staticmethod
    async def update_settings(
        db: AsyncSession,
        user: User,
        settings: Dict[str, Any],
    ) -> User:
        """
        Update user settings.
        
        Args:
            db: Database session
            user: The user to update
            settings: Dictionary of settings to update
            
        Returns:
            The updated user
        """
        for key, value in settings.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        await db.flush()
        await db.refresh(user)
        
        return user
