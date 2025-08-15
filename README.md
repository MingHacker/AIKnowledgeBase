# AI Knowledge Base

A complete FastAPI-based application that allows users to upload PDF documents and ask questions about their content using AI-powered retrieval augmented generation (RAG).

## ✨ Features

**Core Features:**
- **📄 PDF Upload & Processing**: Drag-and-drop PDF upload with automatic text extraction and chunking
- **🔍 Semantic Search**: Vector-based similarity search through document content  
- **🤖 AI-Powered Q&A**: Ask questions and get contextual answers from your documents
- **👤 User Management**: JWT authentication with user registration and login
- **💬 Chat Sessions**: Interactive chat interface with conversation history
- **📊 Processing Pipeline**: Real-time document processing status tracking

**Frontend Features:**
- **📱 Responsive Web App**: Modern React interface with Tailwind CSS
- **🔐 Authentication**: Login/register forms with session management
- **📂 Document Management**: Upload, view, and manage document collection
- **💭 Interactive Chat**: Real-time Q&A interface with message history
- **⚙️ Settings Dashboard**: User account and preferences management
- **🎨 Professional UI**: Clean, intuitive interface with loading states and notifications

## 🏗️ Architecture

```
Frontend (React) ←→ FastAPI Backend ←→ PostgreSQL (metadata)
                        ↓
                   ChromaDB (vectors) ←→ OpenAI API (embeddings/chat)
```

## 🛠️ Tech Stack

**Backend:**
- **Backend**: Python FastAPI with async support
- **Database**: PostgreSQL for metadata + ChromaDB for vector storage
- **AI/ML**: OpenAI API for embeddings and chat completion
- **Authentication**: JWT tokens with bcrypt password hashing
- **File Processing**: PyPDF2 & pdfplumber for text extraction

**Frontend:**
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS + Heroicons
- **Forms**: React Hook Form
- **HTTP Client**: Axios
- **Notifications**: React Hot Toast
- **File Upload**: React Dropzone

## 🚀 Quick Start

### Prerequisites

**Backend:**
- Python 3.8+
- PostgreSQL database
- OpenAI API key

**Frontend:**
- Node.js 16+ and npm

### Installation

#### Backend Setup

1. **Clone and setup backend**
```bash
git clone <repository-url>
cd AIKnowledgeBase
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings:
# - DATABASE_URL=postgresql://user:password@localhost/ai_knowledgebase
# - OPENAI_API_KEY=your_openai_api_key
# - SECRET_KEY=your_secret_key_for_jwt
```

3. **Initialize database**
```bash
alembic upgrade head
```

4. **Start the backend**
```bash
python start.py
# OR
python main.py
```

The API will be available at `http://localhost:8000`

#### Frontend Setup

1. **Install frontend dependencies**
```bash
cd frontend
npm install
```

2. **Start the frontend development server**
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

> **Note**: The frontend is configured to proxy API requests to `http://localhost:8000`

### 📖 API Documentation

- **Interactive Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

## 📱 Usage

### Web Application (Recommended)

1. **Access the Application**
   - Open `http://localhost:3000` in your browser
   - Create a new account or login with existing credentials

2. **Upload Documents**
   - Navigate to the "Documents" tab
   - Drag and drop PDF files or click to select files
   - Wait for processing to complete (text extraction and embedding generation)

3. **Ask Questions**
   - Navigate to the "Chat" tab
   - Start a new chat session
   - Ask questions about your uploaded documents
   - Optionally filter by specific documents using the sidebar

4. **Manage Settings**
   - Visit the "Settings" tab to view account information
   - Monitor document processing statistics

### API Usage (Advanced)

### 1. Create User Account
```bash
POST /api/v1/users/
{
  "email": "user@example.com",
  "username": "testuser",
  "password": "secure_password",
  "full_name": "Test User"
}
```

### 2. Login & Get Token
```bash
POST /api/v1/auth/login
{
  "username": "testuser",
  "password": "secure_password"
}
```

### 3. Upload PDF Document
```bash
POST /api/v1/documents/upload
Content-Type: multipart/form-data
Authorization: Bearer <your_token>

file: <pdf_file>
```

### 4. Process Document
```bash
POST /api/v1/documents/{document_id}/process
Authorization: Bearer <your_token>
```

### 5. Ask Questions
```bash
POST /api/v1/chat/ask
Authorization: Bearer <your_token>
{
  "question": "What are the main topics in this document?",
  "use_history": true
}
```

## 📁 Project Structure

### Backend
```
app/
├── api/
│   └── api_v1/
│       ├── endpoints/     # API route handlers
│       └── api.py         # API router setup
├── core/
│   ├── config.py          # Application settings
│   ├── database.py        # Database connection
│   └── security.py        # Authentication utilities
├── models/                # SQLAlchemy database models
├── schemas/               # Pydantic request/response models
├── services/              # Business logic services
│   ├── pdf_service.py     # PDF processing
│   ├── embedding_service.py # OpenAI embeddings
│   └── rag_service.py     # RAG pipeline
└── main.py               # FastAPI application setup
```

### Frontend
```
frontend/
├── public/                # Static assets
├── src/
│   ├── components/        # React components
│   │   ├── Auth/          # Login/register forms
│   │   ├── Chat/          # Chat interface
│   │   ├── Dashboard/     # Main dashboard
│   │   └── Documents/     # Document management
│   ├── contexts/          # React contexts (auth)
│   ├── services/          # API service layer
│   ├── types/             # TypeScript interfaces
│   └── App.tsx           # Main app component
├── package.json
└── tailwind.config.js
```

## Database Schema

The application uses PostgreSQL with the following main tables:
- `users` - User accounts and authentication
- `documents` - PDF file metadata and processing status
- `document_chunks` - Processed text segments with embeddings
- `chat_sessions` - Conversation contexts
- `chat_messages` - Q&A history with source tracking
- `user_settings` - User preferences and AI model settings

## Environment Variables

Create a `.env` file with:

```
DATABASE_URL=postgresql://username:password@localhost/ai_knowledgebase
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
CHROMA_PERSIST_DIRECTORY=./chroma_db
UPLOAD_DIRECTORY=./uploads
```

## 🚧 Development

### Backend Development
```bash
# Run in development mode with auto-reload
python main.py

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Run tests
python test_api.py
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server (with hot reload)
npm start

# Run type checking
npm run build

# Run tests
npm test
```

## 🚀 Production Deployment

### Backend Production Build
```bash
# Install production dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://..."
export OPENAI_API_KEY="..."
export SECRET_KEY="..."

# Run database migrations
alembic upgrade head

# Start with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Production Build
```bash
cd frontend

# Build for production
npm run build

# Serve static files (example with serve)
npm install -g serve
serve -s build -l 3000
```

## 🐳 Docker Support

*Docker configuration coming soon...*

## ❓ FAQ

**Q: How do I reset my password?**
A: Currently password reset is not implemented. You can manually update the password hash in the database or recreate the user.

**Q: What PDF formats are supported?**
A: The system supports standard PDF files with extractable text. Scanned PDFs (images) require OCR processing which is not currently implemented.

**Q: How do I change the AI model used?**
A: Currently the system uses OpenAI's text-embedding-ada-002 for embeddings and gpt-3.5-turbo for chat. Model selection via settings is planned for future releases.

**Q: Can I upload documents other than PDFs?**
A: Currently only PDF files are supported. Support for other document formats (Word, PowerPoint, etc.) may be added in future versions.

## 🔧 Troubleshooting

### Backend Issues

**Database Connection Errors:**
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify database exists
psql -h localhost -U username -d ai_knowledgebase -c "\dt"
```

**OpenAI API Errors:**
- Verify your API key is valid and has sufficient credits
- Check rate limits if getting 429 errors
- Ensure OPENAI_API_KEY is properly set in .env

**ChromaDB Issues:**
- Clear ChromaDB directory: `rm -rf ./chroma_db`
- Restart the application to reinitialize

### Frontend Issues

**Development Server Won't Start:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Build Failures:**
```bash
# Check TypeScript errors
npm run build

# Update dependencies
npm update
```

**API Connection Issues:**
- Verify backend is running on port 8000
- Check proxy configuration in package.json
- Confirm CORS settings in backend

## 📝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.