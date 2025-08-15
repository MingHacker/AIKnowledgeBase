from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid

from ..models.document import Document
from .pdf_service import PDFService
from .chunking_service import ChunkingService
from .embedding_service import EmbeddingService
from .vector_service import VectorService


class DocumentProcessor:
    def __init__(self):
        self.pdf_service = PDFService()
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
    
    def process_document_full_pipeline(
        self, 
        db: Session, 
        document: Document,
        chunking_method: str = "sliding_window"
    ) -> Dict[str, Any]:
        """Run the complete document processing pipeline"""
        results = {
            'document_id': document.id,
            'text_extraction': False,
            'chunking': False,
            'embedding_generation': False,
            'total_chunks': 0,
            'errors': []
        }
        
        try:
            # Step 1: Extract text from PDF
            print(f"Processing document: {document.original_filename}")
            document.processing_status = "extracting"
            db.commit()
            
            success = self.pdf_service.process_document(db, document)
            if not success:
                results['errors'].append("Text extraction failed")
                return results
            
            results['text_extraction'] = True
            
            # Step 2: Get extracted text and create chunks
            text_content = self.pdf_service.get_document_text(document)
            if not text_content:
                results['errors'].append("No text content extracted")
                return results
            
            print(f"Creating chunks for document: {document.original_filename}")
            document.processing_status = "chunking"
            db.commit()
            
            chunks = self.chunking_service.create_document_chunks(
                db, document, text_content, method=chunking_method
            )
            
            if not chunks:
                results['errors'].append("No chunks created")
                return results
            
            results['chunking'] = True
            results['total_chunks'] = len(chunks)
            
            # Step 3: Generate embeddings and store in vector database
            print(f"Generating embeddings for document: {document.original_filename}")
            document.processing_status = "embedding"
            db.commit()
            
            success = self.embedding_service.process_document_embeddings(
                db, document, self.vector_service
            )
            
            if not success:
                results['errors'].append("Embedding generation failed")
                return results
            
            results['embedding_generation'] = True
            
            # Final status update
            document.processing_status = "completed"
            db.commit()
            
            print(f"Document processing completed: {document.original_filename}")
            return results
            
        except Exception as e:
            error_msg = f"Document processing failed: {str(e)}"
            results['errors'].append(error_msg)
            
            # Update document status
            document.processing_status = "failed"
            db.commit()
            
            print(error_msg)
            return results
    
    def reprocess_document(
        self, 
        db: Session, 
        document_id: uuid.UUID,
        chunking_method: str = "sliding_window"
    ) -> Dict[str, Any]:
        """Reprocess an existing document"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return {'error': 'Document not found'}
        
        # Clean up existing chunks and embeddings
        self.cleanup_document_data(db, document)
        
        # Reset document status
        document.processing_status = "pending"
        db.commit()
        
        # Run full pipeline
        return self.process_document_full_pipeline(db, document, chunking_method)
    
    def cleanup_document_data(self, db: Session, document: Document):
        """Clean up chunks and vector embeddings for a document"""
        try:
            # Delete from vector database
            self.vector_service.delete_document_chunks(str(document.id))
            
            # Delete chunks from PostgreSQL (cascades will handle this)
            # The foreign key cascade should automatically delete chunks
            
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
    
    def get_processing_status(self, db: Session, document_id: uuid.UUID) -> Dict[str, Any]:
        """Get detailed processing status for a document"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return {'error': 'Document not found'}
        
        # Get processing jobs
        from ..models.document import ProcessingJob, DocumentChunk
        jobs = db.query(ProcessingJob).filter(
            ProcessingJob.document_id == document_id
        ).order_by(ProcessingJob.created_at.desc()).all()
        
        # Get chunk count
        chunk_count = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).count()
        
        # Get chunks with embeddings
        embedded_chunks = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id,
            DocumentChunk.embedding_id.isnot(None)
        ).count()
        
        return {
            'document': {
                'id': document.id,
                'filename': document.original_filename,
                'upload_status': document.upload_status,
                'processing_status': document.processing_status,
                'total_pages': document.total_pages,
                'total_characters': document.total_characters,
                'processed_at': document.processed_at
            },
            'chunks': {
                'total': chunk_count,
                'with_embeddings': embedded_chunks,
                'embedding_progress': (embedded_chunks / chunk_count * 100) if chunk_count > 0 else 0
            },
            'jobs': [
                {
                    'id': job.id,
                    'type': job.job_type,
                    'status': job.status,
                    'progress': job.progress_percentage,
                    'error': job.error_message,
                    'started_at': job.started_at,
                    'completed_at': job.completed_at
                }
                for job in jobs
            ]
        }
    
    def bulk_process_documents(
        self, 
        db: Session, 
        user_id: uuid.UUID,
        chunking_method: str = "sliding_window"
    ) -> Dict[str, Any]:
        """Process all pending documents for a user"""
        # Get all pending documents
        pending_docs = db.query(Document).filter(
            Document.user_id == user_id,
            Document.processing_status.in_(["pending", "failed"])
        ).all()
        
        results = {
            'total_documents': len(pending_docs),
            'processed': 0,
            'failed': 0,
            'details': []
        }
        
        for document in pending_docs:
            result = self.process_document_full_pipeline(db, document, chunking_method)
            
            if result['errors']:
                results['failed'] += 1
            else:
                results['processed'] += 1
            
            results['details'].append({
                'document_id': document.id,
                'filename': document.original_filename,
                'success': not bool(result['errors']),
                'chunks_created': result['total_chunks'],
                'errors': result['errors']
            })
        
        return results