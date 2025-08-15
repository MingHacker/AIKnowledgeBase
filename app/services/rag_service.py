from openai import OpenAI
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
import time

from ..models.user import User
from ..models.document import Document, DocumentChunk
from ..models.chat import ChatSession, ChatMessage
from ..core.config import settings
from .embedding_service import EmbeddingService
from .vector_service import VectorService


class RAGService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
        self.default_model = settings.default_model
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature
    
    def create_context_prompt(
        self,
        question: str,
        relevant_chunks: List[Dict[str, Any]],
        chat_history: Optional[List[ChatMessage]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Create a context-rich prompt for the LLM"""
        
        # Default system prompt
        if not system_prompt:
            system_prompt = """You are a helpful AI assistant that answers questions based on provided document context. 
            Use the following context to answer the user's question. If the answer cannot be found in the context, 
            clearly state that the information is not available in the provided documents.
            
            Guidelines:
            - Be accurate and only use information from the provided context
            - Cite specific sections or documents when possible
            - If multiple sources support your answer, mention them
            - Be concise but thorough
            - If uncertain, express that uncertainty"""
        
        # Build context from relevant chunks
        context_parts = []
        for i, chunk_data in enumerate(relevant_chunks, 1):
            chunk = chunk_data['chunk']
            document = chunk_data['document']
            similarity = chunk_data['similarity']
            
            context_parts.append(
                f"[Source {i}: {document.original_filename}, Page {chunk.page_number}, Similarity: {similarity:.3f}]\n"
                f"{chunk.content}\n"
            )
        
        context = "\n---\n".join(context_parts)
        
        # Build chat history context
        history_context = ""
        if chat_history:
            recent_history = chat_history[-6:]  # Last 6 messages for context
            history_parts = []
            for msg in recent_history:
                role = "User" if msg.message_type == "user" else "Assistant"
                history_parts.append(f"{role}: {msg.content}")
            
            if history_parts:
                history_context = f"\n\nPrevious conversation:\n" + "\n".join(history_parts)
        
        # Combine everything
        prompt = f"""{system_prompt}

CONTEXT FROM DOCUMENTS:
{context}
{history_context}

QUESTION: {question}

ANSWER:"""
        
        return prompt
    
    def generate_answer(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate answer using OpenAI API"""
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                stream=False
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Calculate response time
            response_time = int((time.time() - start_time) * 1000)
            
            # Extract token usage
            token_usage = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
            
            return answer, {
                'token_usage': token_usage,
                'response_time_ms': response_time,
                'model_used': model or self.default_model
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate answer: {str(e)}")
    
    def answer_question(
        self,
        db: Session,
        user: User,
        question: str,
        session_id: Optional[uuid.UUID] = None,
        document_filter: Optional[List[uuid.UUID]] = None,
        use_history: bool = True,
        model_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Main RAG pipeline: retrieve context and generate answer"""
        
        try:
            # Get or create chat session
            if session_id:
                session = db.query(ChatSession).filter(
                    ChatSession.id == session_id,
                    ChatSession.user_id == user.id
                ).first()
                if not session:
                    raise Exception("Chat session not found")
            else:
                # Create new session
                session = ChatSession(
                    user_id=user.id,
                    title=question[:100] + "..." if len(question) > 100 else question,
                    document_filter=document_filter or []
                )
                db.add(session)
                db.commit()
                db.refresh(session)
            
            # Apply document filter (session filter takes precedence)
            effective_filter = session.document_filter if session.document_filter else document_filter
            
            # Search for relevant chunks
            relevant_chunks = self.embedding_service.search_similar_chunks(
                db=db,
                query_text=question,
                vector_service=self.vector_service,
                document_ids=effective_filter,
                user_id=user.id,
                limit=5,
                similarity_threshold=0.6
            )
            
            if not relevant_chunks:
                # No relevant context found
                answer = "I couldn't find relevant information in your uploaded documents to answer this question. Please make sure you have uploaded documents that contain information about your query."
                sources = []
                metadata = {
                    'token_usage': None,
                    'response_time_ms': 0,
                    'model_used': None
                }
            else:
                # Get chat history for context
                chat_history = []
                if use_history and session_id:
                    chat_history = db.query(ChatMessage).filter(
                        ChatMessage.session_id == session_id
                    ).order_by(ChatMessage.created_at.desc()).limit(10).all()
                    chat_history.reverse()  # Oldest first
                
                # Create context prompt
                prompt = self.create_context_prompt(
                    question=question,
                    relevant_chunks=relevant_chunks,
                    chat_history=chat_history,
                    system_prompt=session.system_prompt
                )
                
                # Generate answer
                model_config = model_settings or {}
                answer, metadata = self.generate_answer(
                    prompt=prompt,
                    model=model_config.get('model'),
                    max_tokens=model_config.get('max_tokens'),
                    temperature=model_config.get('temperature')
                )
                
                # Prepare sources information
                sources = []
                for chunk_data in relevant_chunks:
                    chunk = chunk_data['chunk']
                    document = chunk_data['document']
                    sources.append({
                        'document_id': str(document.id),
                        'document_name': document.original_filename,
                        'chunk_id': str(chunk.id),
                        'page_number': chunk.page_number,
                        'similarity': chunk_data['similarity'],
                        'content_preview': chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
                    })
            
            # Save user message
            user_message = ChatMessage(
                session_id=session.id,
                message_type="user",
                content=question
            )
            db.add(user_message)
            
            # Save assistant response
            assistant_message = ChatMessage(
                session_id=session.id,
                message_type="assistant",
                content=answer,
                source_chunks=[uuid.UUID(chunk_data['chunk'].id) for chunk_data in relevant_chunks],
                token_usage=metadata.get('token_usage'),
                model_used=metadata.get('model_used'),
                response_time_ms=metadata.get('response_time_ms')
            )
            db.add(assistant_message)
            
            # Update session
            session.last_message_at = datetime.utcnow()
            
            db.commit()
            db.refresh(assistant_message)
            
            return {
                'answer': answer,
                'sources': sources,
                'session_id': session.id,
                'message_id': assistant_message.id,
                'token_usage': metadata.get('token_usage'),
                'response_time_ms': metadata.get('response_time_ms'),
                'relevant_chunks_found': len(relevant_chunks)
            }
            
        except Exception as e:
            db.rollback()
            raise Exception(f"RAG pipeline failed: {str(e)}")
    
    def get_conversation_history(
        self,
        db: Session,
        user: User,
        session_id: uuid.UUID,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user.id
        ).first()
        
        if not session:
            raise Exception("Chat session not found")
        
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.asc()).limit(limit).all()
        
        history = []
        for message in messages:
            msg_data = {
                'id': message.id,
                'type': message.message_type,
                'content': message.content,
                'created_at': message.created_at,
                'token_usage': message.token_usage,
                'response_time_ms': message.response_time_ms
            }
            
            # Add sources for assistant messages
            if message.message_type == "assistant" and message.source_chunks:
                sources = []
                for chunk_id in message.source_chunks:
                    chunk = db.query(DocumentChunk).filter(
                        DocumentChunk.id == chunk_id
                    ).first()
                    if chunk:
                        document = db.query(Document).filter(
                            Document.id == chunk.document_id
                        ).first()
                        if document:
                            sources.append({
                                'document_name': document.original_filename,
                                'page_number': chunk.page_number,
                                'chunk_id': str(chunk.id)
                            })
                msg_data['sources'] = sources
            
            history.append(msg_data)
        
        return history
    
    def suggest_questions(
        self,
        db: Session,
        user: User,
        document_ids: Optional[List[uuid.UUID]] = None,
        limit: int = 5
    ) -> List[str]:
        """Generate suggested questions based on document content"""
        # This is a simplified implementation
        # In a production system, you might use the LLM to generate better suggestions
        
        # Get some sample chunks from the documents
        query = db.query(DocumentChunk).join(Document).filter(
            Document.user_id == user.id
        )
        
        if document_ids:
            query = query.filter(Document.id.in_(document_ids))
        
        sample_chunks = query.limit(20).all()
        
        if not sample_chunks:
            return []
        
        # Generate basic questions based on content patterns
        suggestions = [
            "What are the main topics covered in these documents?",
            "Can you summarize the key points?",
            "What are the most important findings mentioned?",
            "Are there any recommendations or conclusions?",
            "What data or statistics are presented?"
        ]
        
        return suggestions[:limit]