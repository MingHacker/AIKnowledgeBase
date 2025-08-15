from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class DocumentBase(BaseModel):
    filename: str
    original_filename: str
    language: str = "en"


class DocumentCreate(DocumentBase):
    file_path: str
    file_size_bytes: int
    mime_type: str


class DocumentUpdate(BaseModel):
    filename: Optional[str] = None
    language: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(DocumentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    file_size_bytes: int
    mime_type: str
    upload_status: str
    processing_status: str
    total_pages: Optional[int] = None
    total_characters: Optional[int] = None
    doc_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentChunkBase(BaseModel):
    content: str
    content_type: str = "text"
    page_number: Optional[int] = None


class DocumentChunkCreate(DocumentChunkBase):
    document_id: uuid.UUID
    chunk_index: int
    character_count: int
    word_count: int
    embedding_id: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = None


class DocumentChunkResponse(DocumentChunkBase):
    id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    character_count: int
    word_count: int
    embedding_id: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProcessingJobResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    job_type: str
    status: str
    progress_percentage: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True