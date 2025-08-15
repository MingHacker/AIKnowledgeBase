import os
import uuid
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.document import Document
from ..models.user import User


class FileService:
    def __init__(self):
        self.upload_dir = Path(settings.upload_directory)
        self.upload_dir.mkdir(exist_ok=True)
        
    def validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file"""
        # Check file size
        if file.size and file.size > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
            )
        
        # Check file extension
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )
            
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.allowed_file_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} is not allowed. Allowed types: {settings.allowed_file_types}"
            )
        
        # Check MIME type
        if file.content_type not in ["application/pdf"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed"
            )
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate unique filename while preserving extension"""
        file_ext = Path(original_filename).suffix
        unique_name = f"{uuid.uuid4()}{file_ext}"
        return unique_name
    
    async def save_file(self, file: UploadFile) -> tuple[str, int]:
        """Save uploaded file and return (file_path, file_size)"""
        unique_filename = self.generate_unique_filename(file.filename)
        file_path = self.upload_dir / unique_filename
        
        try:
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Get file size
            file_size = file_path.stat().st_size
            
            return str(file_path), file_size
            
        except Exception as e:
            # Clean up if save failed
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from filesystem"""
        try:
            Path(file_path).unlink(missing_ok=True)
            return True
        except Exception:
            return False
    
    def create_document_record(
        self, 
        db: Session, 
        user: User, 
        file: UploadFile, 
        file_path: str, 
        file_size: int
    ) -> Document:
        """Create document record in database"""
        document = Document(
            user_id=user.id,
            filename=self.generate_unique_filename(file.filename),
            original_filename=file.filename,
            file_path=file_path,
            file_size_bytes=file_size,
            mime_type=file.content_type,
            upload_status="completed",
            processing_status="pending"
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return document
    
    async def upload_document(
        self, 
        db: Session, 
        user: User, 
        file: UploadFile
    ) -> Document:
        """Complete upload process: validate, save file, create DB record"""
        # Validate file
        self.validate_file(file)
        
        try:
            # Save file
            file_path, file_size = await self.save_file(file)
            
            # Create database record
            document = self.create_document_record(db, user, file, file_path, file_size)
            
            return document
            
        except Exception as e:
            # Clean up on failure
            if 'file_path' in locals():
                self.delete_file(file_path)
            raise e