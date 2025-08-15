from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class ChatSessionBase(BaseModel):
    title: Optional[str] = None
    system_prompt: Optional[str] = None


class ChatSessionCreate(ChatSessionBase):
    document_filter: List[uuid.UUID] = []


class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None
    document_filter: Optional[List[uuid.UUID]] = None
    system_prompt: Optional[str] = None


class ChatSessionResponse(ChatSessionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    is_active: bool
    document_filter: List[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatMessageBase(BaseModel):
    content: str


class ChatMessageCreate(ChatMessageBase):
    message_type: str = "user"


class ChatMessageResponse(ChatMessageBase):
    id: uuid.UUID
    session_id: uuid.UUID
    message_type: str
    source_chunks: List[uuid.UUID]
    token_usage: Optional[Dict[str, Any]] = None
    model_used: Optional[str] = None
    response_time_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[uuid.UUID] = None
    document_filter: Optional[List[uuid.UUID]] = None
    use_history: bool = True


class QuestionResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    session_id: uuid.UUID
    message_id: uuid.UUID
    token_usage: Optional[Dict[str, Any]] = None
    response_time_ms: int