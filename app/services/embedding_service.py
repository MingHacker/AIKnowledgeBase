from openai import OpenAI
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
import numpy as np

from ..models.document import Document, DocumentChunk, ProcessingJob
from ..core.config import settings


class EmbeddingService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            raise Exception(f"Failed to generate batch embeddings: {str(e)}")
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def process_document_embeddings(
        self, 
        db: Session, 
        document: Document,
        vector_service  # Will be ChromaDB service
    ) -> bool:
        """Generate embeddings for all chunks of a document"""
        # Create processing job
        job = ProcessingJob(
            document_id=document.id,
            job_type="create_embeddings",
            status="running",
            started_at=datetime.utcnow()
        )
        db.add(job)
        db.commit()
        
        try:
            # Get all chunks for the document
            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document.id
            ).order_by(DocumentChunk.chunk_index).all()
            
            if not chunks:
                raise Exception("No chunks found for document")
            
            # Prepare texts for batch processing
            chunk_texts = [chunk.content for chunk in chunks]
            total_chunks = len(chunks)
            
            # Process in batches to avoid API limits
            batch_size = 10  # Adjust based on API limits
            all_embeddings = []
            
            for i in range(0, len(chunk_texts), batch_size):
                batch_texts = chunk_texts[i:i + batch_size]
                batch_embeddings = self.generate_embeddings_batch(batch_texts)
                all_embeddings.extend(batch_embeddings)
                
                # Update progress
                progress = min(100, int((i + batch_size) / total_chunks * 50))
                job.progress_percentage = progress
                db.commit()
            
            # Store embeddings in vector database and update chunks
            for i, (chunk, embedding) in enumerate(zip(chunks, all_embeddings)):
                # Store in vector database
                embedding_id = vector_service.add_document(
                    document_id=str(chunk.document_id),
                    chunk_id=str(chunk.id),
                    text=chunk.content,
                    embedding=embedding,
                    metadata={
                        'page_number': chunk.page_number,
                        'chunk_index': chunk.chunk_index,
                        'document_filename': document.original_filename,
                        'user_id': str(document.user_id)
                    }
                )
                
                # Update chunk with embedding ID
                chunk.embedding_id = embedding_id
                
                # Update progress
                progress = 50 + int((i + 1) / total_chunks * 50)
                job.progress_percentage = progress
                db.commit()
            
            # Complete the job
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.progress_percentage = 100
            
            # Update document status
            document.processing_status = "completed"
            
            db.commit()
            return True
            
        except Exception as e:
            # Update job with error
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            
            # Update document status
            document.processing_status = "embedding_failed"
            
            db.commit()
            return False
    
    def search_similar_chunks(
        self,
        db: Session,
        query_text: str,
        vector_service,
        document_ids: Optional[List[uuid.UUID]] = None,
        user_id: Optional[uuid.UUID] = None,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks using vector similarity"""
        try:
            # Generate embedding for query
            query_embedding = self.generate_embedding(query_text)
            
            # Search in vector database
            search_results = vector_service.search(
                query_embedding=query_embedding,
                limit=limit * 2,  # Get more results to filter
                document_ids=[str(doc_id) for doc_id in document_ids] if document_ids else None,
                user_id=str(user_id) if user_id else None
            )
            
            # Filter by similarity threshold and get chunk details
            results = []
            for result in search_results:
                if result['similarity'] >= similarity_threshold:
                    chunk_id = uuid.UUID(result['chunk_id'])
                    chunk = db.query(DocumentChunk).filter(
                        DocumentChunk.id == chunk_id
                    ).first()
                    
                    if chunk:
                        document = db.query(Document).filter(
                            Document.id == chunk.document_id
                        ).first()
                        
                        results.append({
                            'chunk': chunk,
                            'document': document,
                            'similarity': result['similarity'],
                            'metadata': result.get('metadata', {})
                        })
            
            # Sort by similarity and limit results
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            raise Exception(f"Failed to search similar chunks: {str(e)}")
    
    def get_embedding_stats(self, db: Session, user_id: uuid.UUID) -> Dict[str, Any]:
        """Get embedding statistics for a user"""
        # Count total chunks with embeddings
        total_chunks = db.query(DocumentChunk).join(Document).filter(
            Document.user_id == user_id,
            DocumentChunk.embedding_id.isnot(None)
        ).count()
        
        # Count total documents with completed processing
        total_documents = db.query(Document).filter(
            Document.user_id == user_id,
            Document.processing_status == "completed"
        ).count()
        
        # Count processing jobs
        pending_jobs = db.query(ProcessingJob).join(Document).filter(
            Document.user_id == user_id,
            ProcessingJob.status == "pending"
        ).count()
        
        running_jobs = db.query(ProcessingJob).join(Document).filter(
            Document.user_id == user_id,
            ProcessingJob.status == "running"
        ).count()
        
        return {
            'total_chunks_with_embeddings': total_chunks,
            'total_processed_documents': total_documents,
            'pending_jobs': pending_jobs,
            'running_jobs': running_jobs
        }