from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(...)
    filename: str = Field(..., max_length=500)
    original_filename: str = Field(..., max_length=500)
    file_path: str = Field(..., max_length=1000)
    file_size_bytes: int = Field(...)
    mime_type: str = Field(..., max_length=100)
    upload_status: str = Field(default="pending", max_length=50)
    processing_status: str = Field(default="pending", max_length=50)
    total_pages: Optional[int] = None
    total_characters: Optional[int] = None
    language: str = Field(default="en", max_length=10)
    doc_metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str = Field(...)
    chunk_index: int = Field(...)
    content: str = Field(...)
    content_type: str = Field(default="text", max_length=50)
    page_number: Optional[int] = None
    character_count: int = Field(...)
    word_count: int = Field(...)
    embedding_id: Optional[str] = Field(None, max_length=255)
    chunk_metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class ProcessingJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str = Field(...)
    job_type: str = Field(..., max_length=50)
    status: str = Field(default="pending", max_length=50)
    progress_percentage: int = Field(default=0)
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True