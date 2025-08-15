import PyPDF2
import pdfplumber
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from ..models.document import Document, ProcessingJob
from ..core.config import settings


class PDFService:
    def __init__(self):
        pass
    
    def extract_text_pypdf2(self, file_path: str) -> tuple[str, int, Dict[str, Any]]:
        """Extract text using PyPDF2 (faster but less accurate)"""
        text_content = ""
        metadata = {}
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                # Extract metadata
                if pdf_reader.metadata:
                    metadata = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': str(pdf_reader.metadata.get('/CreationDate', '')),
                        'modification_date': str(pdf_reader.metadata.get('/ModDate', ''))
                    }
                
                # Extract text from all pages
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += f"\n--- Page {page_num + 1} ---\n"
                            text_content += page_text
                    except Exception as e:
                        print(f"Error extracting text from page {page_num + 1}: {e}")
                        continue
                
                return text_content, page_count, metadata
                
        except Exception as e:
            raise Exception(f"Failed to extract text with PyPDF2: {str(e)}")
    
    def extract_text_pdfplumber(self, file_path: str) -> tuple[str, int, Dict[str, Any]]:
        """Extract text using pdfplumber (more accurate but slower)"""
        text_content = ""
        metadata = {}
        
        try:
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                
                # Extract metadata
                if pdf.metadata:
                    metadata = {
                        'title': pdf.metadata.get('Title', ''),
                        'author': pdf.metadata.get('Author', ''),
                        'subject': pdf.metadata.get('Subject', ''),
                        'creator': pdf.metadata.get('Creator', ''),
                        'producer': pdf.metadata.get('Producer', ''),
                        'creation_date': str(pdf.metadata.get('CreationDate', '')),
                        'modification_date': str(pdf.metadata.get('ModDate', ''))
                    }
                
                # Extract text from all pages
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += f"\n--- Page {page_num + 1} ---\n"
                            text_content += page_text
                    except Exception as e:
                        print(f"Error extracting text from page {page_num + 1}: {e}")
                        continue
                
                return text_content, page_count, metadata
                
        except Exception as e:
            raise Exception(f"Failed to extract text with pdfplumber: {str(e)}")
    
    def extract_text(self, file_path: str, method: str = "pdfplumber") -> tuple[str, int, Dict[str, Any]]:
        """Extract text from PDF using specified method"""
        if method == "pypdf2":
            return self.extract_text_pypdf2(file_path)
        elif method == "pdfplumber":
            return self.extract_text_pdfplumber(file_path)
        else:
            raise ValueError(f"Unknown extraction method: {method}")
    
    def create_processing_job(
        self, 
        db: Session, 
        document_id: uuid.UUID, 
        job_type: str
    ) -> ProcessingJob:
        """Create a processing job record"""
        job = ProcessingJob(
            document_id=document_id,
            job_type=job_type,
            status="pending"
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    
    def update_processing_job(
        self,
        db: Session,
        job: ProcessingJob,
        status: str,
        progress: int = None,
        error_message: str = None
    ):
        """Update processing job status"""
        job.status = status
        if progress is not None:
            job.progress_percentage = progress
        if error_message:
            job.error_message = error_message
        
        if status == "running" and not job.started_at:
            job.started_at = datetime.utcnow()
        elif status in ["completed", "failed"]:
            job.completed_at = datetime.utcnow()
            if status == "completed":
                job.progress_percentage = 100
        
        db.commit()
    
    def process_document(self, db: Session, document: Document) -> bool:
        """Process a document: extract text and update metadata"""
        # Create processing job
        job = self.create_processing_job(db, document.id, "extract_text")
        
        try:
            # Update job status to running
            self.update_processing_job(db, job, "running", 0)
            
            # Update document status
            document.processing_status = "extracting"
            db.commit()
            
            # Extract text
            text_content, page_count, pdf_metadata = self.extract_text(document.file_path)
            
            # Update progress
            self.update_processing_job(db, job, "running", 50)
            
            # Update document with extracted information
            document.total_pages = page_count
            document.total_characters = len(text_content)
            document.doc_metadata = pdf_metadata
            document.processing_status = "completed"
            document.processed_at = datetime.utcnow()
            
            # Complete the job
            self.update_processing_job(db, job, "completed", 100)
            
            db.commit()
            return True
            
        except Exception as e:
            # Update job with error
            self.update_processing_job(db, job, "failed", error_message=str(e))
            
            # Update document status
            document.processing_status = "failed"
            db.commit()
            
            return False
    
    def get_document_text(self, document: Document) -> Optional[str]:
        """Get extracted text from a processed document"""
        if document.processing_status != "completed":
            return None
        
        try:
            text_content, _, _ = self.extract_text(document.file_path)
            return text_content
        except Exception:
            return None