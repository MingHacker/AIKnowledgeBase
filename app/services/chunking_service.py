import re
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from ..models.document import Document, DocumentChunk, ProcessingJob
from ..core.config import settings


class ChunkingService:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page markers
        text = re.sub(r'\n--- Page \d+ ---\n', '\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def split_text_by_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (can be improved with NLP libraries)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def create_chunks_sliding_window(self, text: str) -> List[Dict[str, Any]]:
        """Create chunks using sliding window approach"""
        chunks = []
        sentences = self.split_text_by_sentences(text)
        
        if not sentences:
            return chunks
        
        current_chunk = ""
        current_chunk_sentences = []
        chunk_index = 0
        
        for i, sentence in enumerate(sentences):
            # Check if adding this sentence would exceed chunk size
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
                current_chunk_sentences.append(sentence)
            else:
                # Save current chunk if it has content
                if current_chunk:
                    chunks.append({
                        'index': chunk_index,
                        'content': current_chunk.strip(),
                        'character_count': len(current_chunk),
                        'word_count': len(current_chunk.split()),
                        'sentence_count': len(current_chunk_sentences)
                    })
                    chunk_index += 1
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0 and len(current_chunk_sentences) > 1:
                    # Calculate how many sentences to keep for overlap
                    overlap_chars = 0
                    overlap_sentences = []
                    
                    for j in range(len(current_chunk_sentences) - 1, -1, -1):
                        sentence_to_add = current_chunk_sentences[j]
                        if overlap_chars + len(sentence_to_add) <= self.chunk_overlap:
                            overlap_sentences.insert(0, sentence_to_add)
                            overlap_chars += len(sentence_to_add)
                        else:
                            break
                    
                    current_chunk = " ".join(overlap_sentences)
                    current_chunk_sentences = overlap_sentences
                else:
                    current_chunk = ""
                    current_chunk_sentences = []
                
                # Add the sentence that didn't fit
                current_chunk = current_chunk + " " + sentence if current_chunk else sentence
                current_chunk_sentences.append(sentence)
        
        # Add the last chunk
        if current_chunk:
            chunks.append({
                'index': chunk_index,
                'content': current_chunk.strip(),
                'character_count': len(current_chunk),
                'word_count': len(current_chunk.split()),
                'sentence_count': len(current_chunk_sentences)
            })
        
        return chunks
    
    def create_chunks_paragraph_based(self, text: str) -> List[Dict[str, Any]]:
        """Create chunks based on paragraphs"""
        chunks = []
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        current_chunk = ""
        chunk_index = 0
        
        for paragraph in paragraphs:
            test_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            
            if len(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                # Save current chunk if it has content
                if current_chunk:
                    chunks.append({
                        'index': chunk_index,
                        'content': current_chunk.strip(),
                        'character_count': len(current_chunk),
                        'word_count': len(current_chunk.split()),
                        'paragraph_count': current_chunk.count('\n\n') + 1
                    })
                    chunk_index += 1
                
                # Start new chunk with current paragraph
                current_chunk = paragraph
        
        # Add the last chunk
        if current_chunk:
            chunks.append({
                'index': chunk_index,
                'content': current_chunk.strip(),
                'character_count': len(current_chunk),
                'word_count': len(current_chunk.split()),
                'paragraph_count': current_chunk.count('\n\n') + 1
            })
        
        return chunks
    
    def extract_page_info(self, text: str, chunk_content: str) -> int:
        """Extract page number information for a chunk"""
        # Find page markers in the original text
        page_pattern = r'--- Page (\d+) ---'
        pages = re.findall(page_pattern, text)
        
        if not pages:
            return 1
        
        # Find where this chunk appears in the text
        chunk_position = text.find(chunk_content)
        if chunk_position == -1:
            return 1
        
        # Find the last page marker before this chunk
        text_before_chunk = text[:chunk_position]
        page_matches = list(re.finditer(page_pattern, text_before_chunk))
        
        if page_matches:
            return int(page_matches[-1].group(1))
        else:
            return 1
    
    def create_document_chunks(
        self, 
        db: Session, 
        document: Document, 
        text: str, 
        method: str = "sliding_window"
    ) -> List[DocumentChunk]:
        """Create and save document chunks"""
        # Create processing job
        job = ProcessingJob(
            document_id=document.id,
            job_type="generate_chunks",
            status="running",
            started_at=datetime.utcnow()
        )
        db.add(job)
        db.commit()
        
        try:
            # Clean text
            cleaned_text = self.clean_text(text)
            
            # Create chunks
            if method == "sliding_window":
                chunks_data = self.create_chunks_sliding_window(cleaned_text)
            elif method == "paragraph":
                chunks_data = self.create_chunks_paragraph_based(cleaned_text)
            else:
                raise ValueError(f"Unknown chunking method: {method}")
            
            # Create DocumentChunk objects
            document_chunks = []
            for chunk_data in chunks_data:
                page_number = self.extract_page_info(text, chunk_data['content'])
                
                chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_index=chunk_data['index'],
                    content=chunk_data['content'],
                    content_type="text",
                    page_number=page_number,
                    character_count=chunk_data['character_count'],
                    word_count=chunk_data['word_count'],
                    chunk_metadata={
                        'chunking_method': method,
                        'chunk_size': self.chunk_size,
                        'chunk_overlap': self.chunk_overlap,
                        **{k: v for k, v in chunk_data.items() if k not in ['index', 'content', 'character_count', 'word_count']}
                    }
                )
                
                document_chunks.append(chunk)
                db.add(chunk)
            
            # Update job status
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.progress_percentage = 100
            
            # Update document status
            document.processing_status = "chunking_completed"
            
            db.commit()
            return document_chunks
            
        except Exception as e:
            # Update job with error
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            
            # Update document status
            document.processing_status = "chunking_failed"
            
            db.commit()
            raise e
    
    def get_document_chunks(self, db: Session, document_id: uuid.UUID) -> List[DocumentChunk]:
        """Get all chunks for a document"""
        return db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index).all()