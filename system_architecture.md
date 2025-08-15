# AI Knowledge Base System Architecture

## High-Level System Infrastructure

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Frontend (React + TypeScript)                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  Upload Page    │  │   Chat Page     │  │  Dashboard      │                  │
│  │  - File Upload  │  │  - Q&A Interface│  │  - Doc Management│                 │
│  │  - Progress     │  │  - Chat History │  │  - User Settings│                  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                  HTTP/HTTPS
                                      │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           FastAPI Backend Server                                │
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   Upload API    │  │    Query API    │  │   Management    │                  │
│  │  - PDF Upload   │  │  - Question     │  │  - CRUD Docs    │                  │
│  │  - Validation   │  │  - Context      │  │  - User Auth    │                  │  
│  │  - Processing   │  │  - Response     │  │  - Settings     │                  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                  │
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ PDF Processing  │  │  RAG Pipeline   │  │   Auth Service  │                  │
│  │ - Text Extract  │  │  - Embedding    │  │  - JWT Tokens   │                  │
│  │ - Chunking      │  │  - Retrieval    │  │  - User Session │                  │
│  │ - Embedding     │  │  - Generation   │  │  - Permissions  │                  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                 │                     │                     │
                 │                     │                     │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   File Storage  │    │  Vector Database│    │   PostgreSQL    │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │PDF Files  │  │    │  │ChromaDB/  │  │    │  │User Data  │  │
│  │Uploads    │  │    │  │FAISS      │  │    │  │Documents  │  │
│  │Metadata   │  │    │  │Embeddings │  │    │  │Sessions   │  │
│  └───────────┘  │    │  │Vectors    │  │    │  │Metadata   │  │
│                 │    │  └───────────┘  │    │  └───────────┘  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                            │
│                                                                 │
│  ┌─────────────────┐              ┌─────────────────┐           │
│  │   OpenAI API    │              │   Hugging Face  │           │
│  │  - Embeddings   │              │  - Transformers │           │
│  │  - Chat GPT     │              │  - Local Models │           │
│  │  - Text Gen     │              │  - Embeddings   │           │
│  └─────────────────┘              └─────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
User Uploads PDF → FastAPI Upload Endpoint → File Storage
                                          ↓
                                   PDF Processing Service
                                          ↓
                              Text Extraction & Chunking
                                          ↓
                                 Generate Embeddings
                                          ↓
                                 Store in Vector DB
                                          ↓
                              Update PostgreSQL Metadata

User Asks Question → FastAPI Query Endpoint → Generate Query Embedding
                                          ↓
                                 Search Vector Database
                                          ↓
                                Retrieve Relevant Chunks
                                          ↓
                                 Send to LLM with Context
                                          ↓
                                Generate Response → Return to User
```

## Component Details

### 1. Frontend Layer
- **Technology**: React + TypeScript
- **Components**: Upload interface, Chat interface, Document management
- **Communication**: REST API calls to FastAPI backend

### 2. Backend Layer (FastAPI)
- **API Endpoints**: Upload, Query, Document management, Authentication
- **Services**: PDF processing, Embedding generation, RAG pipeline
- **Middleware**: Authentication, CORS, File validation

### 3. Storage Layer
- **PostgreSQL**: User data, document metadata, session management
- **Vector Database**: Document embeddings for semantic search
- **File Storage**: PDF files and processed content

### 4. AI/ML Layer
- **Embedding Models**: OpenAI or Sentence Transformers
- **LLM**: OpenAI GPT or local models
- **RAG Pipeline**: Retrieval + Generation system

### 5. Processing Pipeline
1. PDF Upload → Validation → Storage
2. Text Extraction → Chunking → Embedding
3. Vector Storage → Indexing
4. Query Processing → Retrieval → Generation