from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from supabase import Client
import jwt as jose_jwt
import requests

from .config import settings
from .database import get_supabase
from ..models.user import User

security = HTTPBearer()


def get_current_user(supabase: Client = Depends(get_supabase), token: str = Depends(security)):
    """Get current user from Supabase Auth token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from Bearer scheme
        if hasattr(token, 'credentials'):
            access_token = token.credentials
        else:
            access_token = token

        # Try official client first
        try:
            user_response = supabase.auth.get_user(jwt=access_token)
            if not user_response.user:
                raise ValueError("No user in response")

            # Optional profile fetch
            try:
                profile_response = supabase.table("user_profiles").select("*").eq("id", user_response.user.id).execute()
                profile_data = profile_response.data[0] if profile_response.data else {}
            except Exception as e:
                print(f"Warning: Could not fetch profile data: {e}")
                profile_data = {}

            user_data = {
                "id": user_response.user.id,
                "email": user_response.user.email,
                "username": profile_data.get("username") or user_response.user.user_metadata.get("username", user_response.user.email.split("@")[0]),
                "full_name": profile_data.get("full_name") or user_response.user.user_metadata.get("full_name", ""),
                "password_hash": "",
                "is_active": True,
                "is_superuser": False,
                "created_at": datetime.fromisoformat(user_response.user.created_at.replace('Z', '+00:00')) if getattr(user_response.user, 'created_at', None) else datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            return User(**user_data)
        except Exception as inner_e:
            print(f"Supabase client get_user failed, falling back to REST: {inner_e}")

        # Fallback: direct REST call
        auth_user_url = f"{settings.supabase_url}/auth/v1/user"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "apikey": settings.supabase_key,
        }
        resp = requests.get(auth_user_url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"Auth REST /user failed: {resp.status_code} {resp.text}")
            raise credentials_exception

        payload = resp.json() or {}
        user_metadata = payload.get("user_metadata") or {}
        created_at_raw = payload.get("created_at") or payload.get("createdAt")
        try:
            created_at = datetime.fromisoformat(created_at_raw.replace('Z', '+00:00')) if created_at_raw else datetime.utcnow()
        except Exception:
            created_at = datetime.utcnow()

        user_data = {
            "id": payload.get("id"),
            "email": payload.get("email"),
            "username": user_metadata.get("username", (payload.get("email") or "").split("@")[0]),
            "full_name": user_metadata.get("full_name", ""),
            "password_hash": "",
            "is_active": True,
            "is_superuser": False,
            "created_at": created_at,
            "updated_at": datetime.utcnow(),
        }
        return User(**user_data)

    except Exception as e:
        print(f"Auth error: {e}")
        if hasattr(e, 'status_code'):
            print(f"Error status code: {e.status_code}")
        if hasattr(e, 'message'):
            print(f"Error message: {e.message}")
        raise credentials_exception


def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Legacy functions for backward compatibility (if needed)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Deprecated: Use Supabase Auth instead"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Deprecated: Use Supabase Auth instead"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Deprecated: Use Supabase Auth tokens instead"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jose_jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt