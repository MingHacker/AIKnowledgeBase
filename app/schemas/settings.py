from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
import uuid


class UserSettingsBase(BaseModel):
    preferred_model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: Decimal = Decimal("0.7")
    chunk_size: int = 1000
    chunk_overlap: int = 200


class UserSettingsCreate(UserSettingsBase):
    default_document_filter: List[uuid.UUID] = []
    ui_preferences: Dict[str, Any] = {}


class UserSettingsUpdate(BaseModel):
    preferred_model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[Decimal] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    default_document_filter: Optional[List[uuid.UUID]] = None
    ui_preferences: Optional[Dict[str, Any]] = None

    @validator('temperature')
    def validate_temperature(cls, v):
        if v is not None and (v < 0 or v > 2):
            raise ValueError('Temperature must be between 0 and 2')
        return v

    @validator('max_tokens')
    def validate_max_tokens(cls, v):
        if v is not None and v < 1:
            raise ValueError('Max tokens must be positive')
        return v


class UserSettingsResponse(UserSettingsBase):
    id: uuid.UUID
    user_id: uuid.UUID
    default_document_filter: List[uuid.UUID]
    ui_preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True