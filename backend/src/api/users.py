"""User API endpoints."""

from typing import Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.database.connection import get_db
from src.models.enums import ThemeType, UnitPreference
from src.models.user import User
from src.services.auth_service import AuthService


router = APIRouter(prefix="/users", tags=["Users"])


class UpdateUserSettingsRequest(BaseModel):
    language_preference: str | None = None
    theme_preference: ThemeType | None = None
    unit_preference: UnitPreference | None = None
    notification_settings: Dict[str, bool] | None = None


@router.patch("/settings")
async def update_user_settings(
    request: UpdateUserSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    settings_dict = request.model_dump(exclude_unset=True)
    await AuthService.update_settings(db=db, user=current_user, settings=settings_dict)
    return {"message": "Settings updated successfully"}

