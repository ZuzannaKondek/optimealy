"""JWT authentication middleware."""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import decode_token, validate_token_type
from src.database.connection import get_db
from src.models.user import User
from src.services.auth_service import AuthService

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: The HTTP Bearer token
        db: Database session
        
    Returns:
        The authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        # Validate token type
        if not validate_token_type(payload, "access"):
            raise credentials_exception
        
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = await AuthService.get_user_by_id(db, user_id)
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Dependency to optionally get the current user (for endpoints that work with/without auth).
    
    Args:
        credentials: The HTTP Bearer token (optional)
        db: Database session
        
    Returns:
        The authenticated user if token is valid, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        if not validate_token_type(payload, "access"):
            return None
        
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            return None
        
        user = await AuthService.get_user_by_id(db, user_id)
        return user
        
    except JWTError:
        return None
