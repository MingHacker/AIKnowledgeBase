from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from supabase import Client
import logging

from ....core.database import get_supabase
from ....schemas.user import Token

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str = None
    full_name: str = None


@router.post("/login", response_model=Token)
async def login_for_access_token(
    login_data: LoginRequest,
    supabase: Client = Depends(get_supabase)
):
    """Login using Supabase Auth"""
    try:
        logger.info(f"Attempting login for email: {login_data.email}")
        
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": login_data.email,
            "password": login_data.password
        })
        
        logger.info(f"Supabase auth response: {auth_response}")
        
        if not auth_response.user or not auth_response.session:
            logger.warning(f"Login failed for {login_data.email}: Invalid credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Login successful for user: {auth_response.user.id}")
        
        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer",
            "refresh_token": auth_response.session.refresh_token
        }
        
    except Exception as e:
        logger.error(f"Login error for {login_data.email}: {str(e)}")
        
        # 检查是否是Supabase特定的错误
        if hasattr(e, 'status_code'):
            if e.status_code == 400:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email or password format"
                )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/register")
async def register(
    register_data: RegisterRequest,
    supabase: Client = Depends(get_supabase)
):
    """Register using Supabase Auth and create user profile"""
    try:
        logger.info(f"Attempting registration for email: {register_data.email}")
        
        # Create user with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": register_data.email,
            "password": register_data.password,
            "options": {
                "data": {
                    "username": register_data.username or register_data.email.split("@")[0],
                    "full_name": register_data.full_name or ""
                }
            }
        })
        
        if not auth_response.user:
            logger.error(f"Registration failed for {register_data.email}: No user created")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create account"
            )
        
        # Create user profile in user_profiles table
        try:
            user_profile = {
                "id": auth_response.user.id,
                "username": register_data.username or register_data.email.split("@")[0],
                "full_name": register_data.full_name or "",
                "bio": "",
                "avatar_url": "",
                "preferences": {}
            }
            
            profile_result = supabase.table("user_profiles").insert(user_profile).execute()
            logger.info(f"User profile created: {profile_result.data}")
            
            # Create default user settings
            user_settings = {
                "user_id": auth_response.user.id,
                "preferred_model": "gpt-3.5-turbo",
                "max_tokens": 1000,
                "temperature": 0.7,
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "default_document_filter": [],
                "ui_preferences": {}
            }
            
            settings_result = supabase.table("user_settings").insert(user_settings).execute()
            logger.info(f"User settings created: {settings_result.data}")
            
        except Exception as profile_error:
            logger.warning(f"Could not create user profile/settings: {profile_error}")
            # Don't fail registration if profile creation fails
        
        logger.info(f"Registration successful for user: {auth_response.user.id}")
        
        return {
            "message": "Account created successfully. Please check your email for verification.",
            "user_id": auth_response.user.id
        }
        
    except Exception as e:
        logger.error(f"Register error for {register_data.email}: {str(e)}")
        if "already registered" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create account"
        )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    supabase: Client = Depends(get_supabase)
):
    """Refresh access token"""
    try:
        auth_response = supabase.auth.refresh_session(refresh_token)
        
        if not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer",
            "refresh_token": auth_response.session.refresh_token
        }
        
    except Exception as e:
        logger.error(f"Refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(supabase: Client = Depends(get_supabase)):
    """Logout from Supabase Auth"""
    try:
        supabase.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return {"message": "Logged out successfully"}