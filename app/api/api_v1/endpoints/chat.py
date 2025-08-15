from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ....core.database import get_db
from ....core.security import get_current_active_user
from ....models.user import User
from ....models.chat import ChatSession, ChatMessage
from ....schemas.chat import (
    ChatSessionCreate, ChatSessionResponse, ChatSessionUpdate,
    ChatMessageResponse, QuestionRequest, QuestionResponse
)
from ....services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Ask a question and get an AI-powered answer based on uploaded documents"""
    try:
        result = rag_service.answer_question(
            db=db,
            user=current_user,
            question=request.question,
            session_id=request.session_id,
            document_filter=request.document_filter,
            use_history=request.use_history
        )
        
        return QuestionResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new chat session"""
    session = ChatSession(
        user_id=current_user.id,
        title=session_data.title,
        system_prompt=session_data.system_prompt,
        document_filter=session_data.document_filter
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_chat_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List user's chat sessions"""
    query = db.query(ChatSession).filter(ChatSession.user_id == current_user.id)
    
    if active_only:
        query = query.filter(ChatSession.is_active == True)
    
    sessions = query.order_by(ChatSession.last_message_at.desc().nullslast(), 
                             ChatSession.created_at.desc()).offset(skip).limit(limit).all()
    
    return sessions


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific chat session"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return session


@router.put("/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_chat_session(
    session_id: uuid.UUID,
    session_update: ChatSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a chat session"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    update_data = session_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(session, key, value)
    
    db.commit()
    db.refresh(session)
    
    return session


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a chat session"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    db.delete(session)
    db.commit()


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get messages for a chat session"""
    # Verify session ownership
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).offset(skip).limit(limit).all()
    
    return messages


@router.get("/sessions/{session_id}/history")
async def get_conversation_history(
    session_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get formatted conversation history with sources"""
    try:
        history = rag_service.get_conversation_history(
            db=db,
            user=current_user,
            session_id=session_id,
            limit=limit
        )
        
        return {"history": history}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/suggestions")
async def get_question_suggestions(
    document_ids: Optional[List[uuid.UUID]] = Query(None),
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get suggested questions based on uploaded documents"""
    try:
        suggestions = rag_service.suggest_questions(
            db=db,
            user=current_user,
            document_ids=document_ids,
            limit=limit
        )
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats")
async def get_chat_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get chat statistics for the user"""
    # Count total sessions
    total_sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).count()
    
    # Count active sessions
    active_sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id,
        ChatSession.is_active == True
    ).count()
    
    # Count total messages
    total_messages = db.query(ChatMessage).join(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).count()
    
    # Count user questions
    user_questions = db.query(ChatMessage).join(ChatSession).filter(
        ChatSession.user_id == current_user.id,
        ChatMessage.message_type == "user"
    ).count()
    
    return {
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "total_messages": total_messages,
        "user_questions": user_questions
    }