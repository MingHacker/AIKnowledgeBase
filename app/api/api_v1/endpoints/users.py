from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from typing import List

from ....core.database import get_supabase
from ....core.security import get_current_active_user
from ....models.user import User
from ....models.settings import UserSettings
from ....schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, supabase: Client = Depends(get_supabase)):
    """Create user profile after Supabase Auth registration"""
    # Check if user already exists in user_profiles table
    existing_user = supabase.table("user_profiles").select("*").eq("username", user.username).execute()
    
    if existing_user.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user profile (auth is handled by Supabase Auth)
    new_user_profile = {
        "id": user.id,  # This should be the auth.users.id from registration
        "username": user.username,
        "full_name": user.full_name,
        "bio": "",
        "avatar_url": "",
        "preferences": {}
    }
    
    user_result = supabase.table("user_profiles").insert(new_user_profile).execute()
    if not user_result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user profile"
        )
    
    created_user = User(**user_result.data[0])
    
    # Create default user settings
    try:
        user_settings = {
            "user_id": created_user.id,
            "preferred_model": "gpt-3.5-turbo",
            "max_tokens": 1000,
            "temperature": 0.7,
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "default_document_filter": [],
            "ui_preferences": {}
        }
        supabase.table("user_settings").insert(user_settings).execute()
    except Exception as e:
        print(f"Warning: Could not create user settings: {e}")
    
    return created_user


@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    supabase: Client = Depends(get_supabase)
):
    """Update current user profile"""
    update_data = user_update.dict(exclude_unset=True)
    
    # Remove password-related fields as they're handled by Supabase Auth
    if "password" in update_data:
        update_data.pop("password")
    
    # Check for unique constraints
    if "username" in update_data:
        existing_user = supabase.table("user_profiles").select("*").eq("username", update_data["username"]).neq("id", current_user.id).execute()
        
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Update the user profile
    result = supabase.table("user_profiles").update(update_data).eq("id", current_user.id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
    
    return User(**result.data[0])