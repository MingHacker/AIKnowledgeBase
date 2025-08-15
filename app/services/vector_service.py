import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import uuid
import json

from ..core.config import settings


class VectorService:
    def __init__(self):
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="document_chunks",
            metadata={"description": "Document chunks with embeddings for RAG"}
        )
    
    def add_document(
        self,
        document_id: str,
        chunk_id: str,
        text: str,
        embedding: List[float],
        metadata: Dict[str, Any] = None
    ) -> str:
        """Add a document chunk to the vector database"""
        try:
            # Prepare metadata
            chunk_metadata = {
                'document_id': document_id,
                'chunk_id': chunk_id,
                'text_length': len(text),
                **(metadata or {})
            }
            
            # Add to collection
            self.collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[chunk_metadata]
            )
            
            return chunk_id
            
        except Exception as e:
            raise Exception(f"Failed to add document to vector database: {str(e)}")
    
    def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        document_ids: Optional[List[str]] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Prepare where clause for filtering
            where_clause = {}
            if document_ids:
                where_clause["document_id"] = {"$in": document_ids}
            if user_id:
                where_clause["user_id"] = user_id
            
            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause if where_clause else None,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            search_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    # Convert distance to similarity (ChromaDB uses squared L2 distance)
                    distance = results['distances'][0][i]
                    similarity = 1 / (1 + distance)  # Convert distance to similarity
                    
                    search_results.append({
                        'chunk_id': results['ids'][0][i],
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity': similarity,
                        'distance': distance
                    })
            
            return search_results
            
        except Exception as e:
            raise Exception(f"Failed to search vector database: {str(e)}")
    
    def delete_document(self, chunk_id: str) -> bool:
        """Delete a document chunk from the vector database"""
        try:
            self.collection.delete(ids=[chunk_id])
            return True
        except Exception as e:
            print(f"Failed to delete chunk {chunk_id}: {str(e)}")
            return False
    
    def delete_document_chunks(self, document_id: str) -> bool:
        """Delete all chunks for a document"""
        try:
            # Get all chunk IDs for the document
            results = self.collection.get(
                where={"document_id": document_id},
                include=['metadatas']
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
            
            return True
        except Exception as e:
            print(f"Failed to delete chunks for document {document_id}: {str(e)}")
            return False
    
    def update_chunk_metadata(self, chunk_id: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata for a chunk"""
        try:
            # ChromaDB doesn't support direct metadata updates
            # We need to get the existing data and re-add it
            existing = self.collection.get(
                ids=[chunk_id],
                include=['embeddings', 'documents', 'metadatas']
            )
            
            if existing['ids']:
                # Update metadata
                updated_metadata = existing['metadatas'][0].copy()
                updated_metadata.update(metadata)
                
                # Delete and re-add
                self.collection.delete(ids=[chunk_id])
                self.collection.add(
                    ids=[chunk_id],
                    embeddings=existing['embeddings'][0],
                    documents=existing['documents'][0],
                    metadatas=[updated_metadata]
                )
                
                return True
            return False
            
        except Exception as e:
            print(f"Failed to update metadata for chunk {chunk_id}: {str(e)}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database"""
        try:
            count = self.collection.count()
            
            # Get sample of metadata to understand data structure
            sample = self.collection.peek(limit=5)
            
            return {
                'total_chunks': count,
                'collection_name': self.collection.name,
                'sample_metadata': sample['metadatas'] if sample['metadatas'] else []
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def search_by_document(
        self,
        document_id: str,
        query_embedding: List[float],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search within a specific document"""
        return self.search(
            query_embedding=query_embedding,
            limit=limit,
            document_ids=[document_id]
        )
    
    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document"""
        try:
            results = self.collection.get(
                where={"document_id": document_id},
                include=['documents', 'metadatas']
            )
            
            chunks = []
            if results['ids']:
                for i in range(len(results['ids'])):
                    chunks.append({
                        'chunk_id': results['ids'][i],
                        'document': results['documents'][i],
                        'metadata': results['metadatas'][i]
                    })
            
            return chunks
            
        except Exception as e:
            raise Exception(f"Failed to get document chunks: {str(e)}")
    
    def reset_collection(self) -> bool:
        """Reset the entire collection (use with caution)"""
        try:
            self.client.delete_collection("document_chunks")
            self.collection = self.client.get_or_create_collection(
                name="document_chunks",
                metadata={"description": "Document chunks with embeddings for RAG"}
            )
            return True
        except Exception as e:
            print(f"Failed to reset collection: {str(e)}")
            return False