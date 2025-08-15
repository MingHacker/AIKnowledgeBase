# PostgreSQL Database Schema

## Schema Overview

The database consists of 7 main tables with relationships to support user management, document storage, and chat functionality.

```sql
-- Users table for authentication and user management
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Documents table for PDF metadata
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    original_filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    upload_status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    processing_status VARCHAR(50) DEFAULT 'pending', -- pending, extracting, chunking, embedding, completed, failed
    total_pages INTEGER,
    total_characters INTEGER,
    language VARCHAR(10) DEFAULT 'en',
    metadata JSONB, -- Additional file metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Document chunks for storing processed text segments
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL, -- Order within the document
    content TEXT NOT NULL,
    content_type VARCHAR(50) DEFAULT 'text', -- text, table, image_caption, etc.
    page_number INTEGER,
    character_count INTEGER NOT NULL,
    word_count INTEGER NOT NULL,
    embedding_id VARCHAR(255), -- Reference to vector database ID
    metadata JSONB, -- Chunk-specific metadata (position, formatting, etc.)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(document_id, chunk_index)
);

-- Chat sessions for conversation management
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    document_filter UUID[] DEFAULT '{}', -- Array of document IDs to filter search
    system_prompt TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP WITH TIME ZONE
);

-- Chat messages for storing Q&A history
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    source_chunks UUID[] DEFAULT '{}', -- Array of chunk IDs used for context
    token_usage JSONB, -- Track token consumption
    model_used VARCHAR(100),
    response_time_ms INTEGER,
    metadata JSONB, -- Additional message metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Processing jobs for async document processing
CREATE TABLE processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL, -- extract_text, generate_chunks, create_embeddings
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User settings and preferences
CREATE TABLE user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    preferred_model VARCHAR(100) DEFAULT 'gpt-3.5-turbo',
    max_tokens INTEGER DEFAULT 1000,
    temperature DECIMAL(3,2) DEFAULT 0.7 CHECK (temperature >= 0 AND temperature <= 2),
    chunk_size INTEGER DEFAULT 1000,
    chunk_overlap INTEGER DEFAULT 200,
    default_document_filter UUID[] DEFAULT '{}',
    ui_preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Indexes for Performance

```sql
-- Performance indexes
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_status ON documents(upload_status, processing_status);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);

CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_document_chunks_page ON document_chunks(page_number);
CREATE INDEX idx_document_chunks_embedding ON document_chunks(embedding_id);

CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_active ON chat_sessions(is_active, last_message_at DESC);

CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at DESC);
CREATE INDEX idx_chat_messages_type ON chat_messages(message_type);

CREATE INDEX idx_processing_jobs_document_id ON processing_jobs(document_id);
CREATE INDEX idx_processing_jobs_status ON processing_jobs(status, created_at);

-- Full-text search index for document content
CREATE INDEX idx_document_chunks_content_fts ON document_chunks USING gin(to_tsvector('english', content));
```

## Entity Relationships

```
Users (1) ←→ (N) Documents
Users (1) ←→ (N) ChatSessions  
Users (1) ←→ (1) UserSettings

Documents (1) ←→ (N) DocumentChunks
Documents (1) ←→ (N) ProcessingJobs

ChatSessions (1) ←→ (N) ChatMessages

ChatMessages (N) ←→ (N) DocumentChunks (via source_chunks array)
```

## Table Details

### Users Table
- **Purpose**: User authentication and profile management
- **Key Fields**: email, username, password_hash, permissions
- **Security**: Stores hashed passwords, supports role-based access

### Documents Table
- **Purpose**: PDF file metadata and processing status
- **Key Fields**: filename, file_path, upload_status, processing_status
- **Status Tracking**: Monitors upload and processing pipeline stages

### Document_Chunks Table
- **Purpose**: Stores processed text segments with embeddings
- **Key Fields**: content, chunk_index, embedding_id, page_number
- **Vector Link**: embedding_id references ChromaDB/FAISS storage

### Chat_Sessions Table
- **Purpose**: Manages conversation contexts and settings
- **Key Fields**: title, document_filter, system_prompt
- **Filtering**: Supports document-specific conversations

### Chat_Messages Table
- **Purpose**: Stores Q&A history with context tracking
- **Key Fields**: message_type, content, source_chunks
- **Analytics**: Tracks token usage and response times

### Processing_Jobs Table
- **Purpose**: Async job tracking for document processing
- **Key Fields**: job_type, status, progress_percentage
- **Monitoring**: Enables progress tracking and error handling

### User_Settings Table
- **Purpose**: Personalized preferences and configurations
- **Key Fields**: preferred_model, chunk_size, temperature
- **Customization**: User-specific AI model parameters

## Data Flow Examples

### Document Upload Flow:
1. Insert into `documents` (status: pending)
2. Insert into `processing_jobs` (extract_text)
3. Update `documents` (status: processing)
4. Insert into `document_chunks` (after text extraction)
5. Update `processing_jobs` (completed)
6. Update `documents` (status: completed)

### Chat Query Flow:
1. Query `chat_sessions` for active session
2. Insert user message into `chat_messages`
3. Search `document_chunks` for relevant content
4. Generate AI response with source tracking
5. Insert assistant message with `source_chunks` references
6. Update `chat_sessions.last_message_at`