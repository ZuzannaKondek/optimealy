"""Authentication API endpoints."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.database.connection import get_db
from src.core.config import settings
from src.models.user import User
from src.models.enums import ThemeType, UnitPreference
from src.services.auth_service import AuthService
from src.api.middleware.auth import get_current_user
from src.core.security import decode_token, validate_token_type, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Request/Response Models
class RegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class RegisterResponse(BaseModel):
    """User registration response."""

    message: str
    user_id: str


class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """User login response."""

    access_token: str
    refresh_token: str
    token_type: str


class RefreshRequest(BaseModel):
    """Token refresh request."""

    refresh_token: str


class RefreshResponse(BaseModel):
    """Token refresh response."""

    access_token: str
    token_type: str


class UserProfileResponse(BaseModel):
    """User profile response."""

    user_id: str
    email: str
    language_preference: str
    theme_preference: ThemeType
    unit_preference: UnitPreference
    notification_settings: Dict[str, Any]
    created_at: str

    class Config:
        from_attributes = True


class UpdatePasswordRequest(BaseModel):
    """Update password request."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UpdateSettingsRequest(BaseModel):
    """Update user settings request."""

    language_preference: str | None = None
    theme_preference: ThemeType | None = None
    unit_preference: UnitPreference | None = None
    notification_settings: Dict[str, bool] | None = None


# Endpoints
@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    """
    Register a new user account.
    
    - **email**: Valid email address (must be unique)
    - **password**: Password (min 8 characters)
    """
    # Normalize email (lowercase, trimmed)
    email_normalized = request.email.lower().strip()
    
    try:
        user = await AuthService.register_user(
            db=db,
            email=email_normalized,
            password=request.password,
        )
        
        return RegisterResponse(
            message="User registered successfully",
            user_id=str(user.id),
        )
        
    except ValueError as e:
        error_message = str(e)
        # Make error message more user-friendly
        if "already registered" in error_message.lower() or "already exists" in error_message.lower():
            error_message = "This email address is already registered. Please use a different email or try logging in."
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_message,
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """
    Authenticate and get access token.
    
    - **email**: User's email address
    - **password**: User's password
    """
    # Normalize email for login (case-insensitive)
    email_normalized = request.email.lower().strip()
    user = await AuthService.authenticate_user(
        db=db,
        email=email_normalized,
        password=request.password,
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    tokens = AuthService.create_tokens(str(user.id))
    
    return LoginResponse(**tokens)


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(request: RefreshRequest) -> RefreshResponse:
    """
    Exchange a refresh token for a new access token.
    """
    try:
        payload = decode_token(request.refresh_token)
        if not validate_token_type(payload, "refresh"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        access_token = create_access_token(data={"sub": str(user_id)})
        return RefreshResponse(access_token=access_token, token_type="bearer")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
) -> UserProfileResponse:
    """
    Get current user's profile.
    
    Requires authentication.
    """
    return UserProfileResponse(
        user_id=str(current_user.id),
        email=current_user.email,
        language_preference=current_user.language_preference,
        theme_preference=current_user.theme_preference,
        unit_preference=current_user.unit_preference,
        notification_settings=current_user.notification_settings,
        created_at=current_user.created_at.isoformat(),
    )


@router.put("/password")
async def update_password(
    request: UpdatePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """
    Update user's password.
    
    Requires authentication and current password verification.
    """
    success = await AuthService.update_password(
        db=db,
        user=current_user,
        current_password=request.current_password,
        new_password=request.new_password,
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )
    
    return {"message": "Password updated successfully"}


@router.patch("/password")
async def patch_password(
    request: UpdatePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """
    PATCH alias for updating user's password.
    """
    return await update_password(request=request, current_user=current_user, db=db)


@router.put("/settings")
async def update_settings(
    request: UpdateSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """
    Update user settings.
    
    Requires authentication.
    """
    settings_dict = request.model_dump(exclude_unset=True)
    
    await AuthService.update_settings(
        db=db,
        user=current_user,
        settings=settings_dict,
    )
    
    return {"message": "Settings updated successfully"}


# Debug endpoint (only in development)
@router.get("/debug/users", include_in_schema=False)
async def debug_list_users(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Debug endpoint to list all users (development only).
    """
    if settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    
    result = await db.execute(select(User.email, User.created_at).order_by(User.created_at.desc()))
    users = result.all()
    
    # Also check for similar emails
    test_emails = ["test3@test.com", "test4@test.com", "test5@test.com"]
    similar_users = {}
    for test_email in test_emails:
        email_lower = test_email.lower()
        result = await db.execute(select(User).where(func.lower(User.email) == email_lower))
        user = result.scalar_one_or_none()
        if user:
            similar_users[test_email] = {"found": user.email, "id": str(user.id)}
    
    return {
        "total_users": len(users),
        "users": [{"email": u.email, "created_at": u.created_at.isoformat()} for u in users],
        "test_email_check": similar_users,
    }
