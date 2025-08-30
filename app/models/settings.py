from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid


class UserSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(...)
    preferred_model: str = Field(default="gpt-3.5-turbo", max_length=100)
    max_tokens: int = Field(default=1000)
    temperature: float = Field(default=0.7)
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    default_document_filter: List[str] = Field(default_factory=list)
    ui_preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @validator('temperature')
    def validate_temperature(cls, v):
        if not (0 <= v <= 2):
            raise ValueError('temperature must be between 0 and 2')
        return v

    class Config:
        from_attributes = True