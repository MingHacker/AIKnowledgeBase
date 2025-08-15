from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.security import get_current_active_user
from ....models.user import User
from ....models.settings import UserSettings
from ....schemas.settings import UserSettingsResponse, UserSettingsUpdate

router = APIRouter()


@router.get("/", response_model=UserSettingsResponse)
async def get_user_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user settings"""
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        # Create default settings if they don't exist
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


@router.put("/", response_model=UserSettingsResponse)
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user settings"""
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        # Create new settings if they don't exist
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
    
    # Update settings
    update_data = settings_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)
    
    db.commit()
    db.refresh(settings)
    
    return settings


@router.post("/reset", response_model=UserSettingsResponse)
async def reset_user_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reset user settings to defaults"""
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if settings:
        db.delete(settings)
    
    # Create new default settings
    new_settings = UserSettings(user_id=current_user.id)
    db.add(new_settings)
    db.commit()
    db.refresh(new_settings)
    
    return new_settings