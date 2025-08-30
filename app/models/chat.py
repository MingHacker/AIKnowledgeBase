from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(...)
    title: Optional[str] = Field(None, max_length=255)
    is_active: bool = Field(default=True)
    document_filter: List[str] = Field(default_factory=list)
    system_prompt: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(...)
    message_type: str = Field(..., max_length=20)
    content: str = Field(...)
    source_chunks: List[str] = Field(default_factory=list)
    token_usage: Optional[Dict[str, Any]] = None
    model_used: Optional[str] = Field(None, max_length=100)
    response_time_ms: Optional[int] = None
    msg_metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @validator('message_type')
    def validate_message_type(cls, v):
        if v not in ['user', 'assistant', 'system']:
            raise ValueError('message_type must be one of: user, assistant, system')
        return v

    class Config:
        from_attributes = True