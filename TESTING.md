# API Testing Guide

This guide will help you test the AI Knowledge Base backend API to ensure everything is working correctly.

## 🚀 Prerequisites

1. **Start the server**:
   ```bash
   python start.py
   ```

2. **Verify server is running**:
   - Visit: http://localhost:8000
   - Should see: `{"message": "AI Knowledge Base API", "version": "1.0.0"}`

3. **Check API documentation**:
   - Visit: http://localhost:8000/docs
   - Interactive Swagger UI should load

## 🧪 Automated Testing

Run the comprehensive test suite:

```bash
python test_api.py
```

This will test all major endpoints and functionality.

## 🔧 Manual Testing Steps

### 1. Health Check
```bash
curl http://localhost:8000/health
```
Expected: `{"status": "healthy", "environment": "development"}`

### 2. Create User Account
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "secure123",
    "full_name": "Test User"
  }'
```

### 3. Login & Get Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=secure123"
```

Save the `access_token` from the response for subsequent requests.

### 4. Upload PDF Document
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@/path/to/your/document.pdf"
```

Save the `id` from the response (document ID).

### 5. Process Document
```bash
curl -X POST "http://localhost:8000/api/v1/documents/DOCUMENT_ID/process" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 6. Check Processing Status
```bash
curl -X GET "http://localhost:8000/api/v1/documents/DOCUMENT_ID/status" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 7. Ask a Question
```bash
curl -X POST "http://localhost:8000/api/v1/chat/ask" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main topics in this document?",
    "use_history": true
  }'
```

### 8. List Documents
```bash
curl -X GET "http://localhost:8000/api/v1/documents/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 9. List Chat Sessions
```bash
curl -X GET "http://localhost:8000/api/v1/chat/sessions" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 10. Get User Settings
```bash
curl -X GET "http://localhost:8000/api/v1/settings/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🔍 Testing with Postman/Insomnia

### Import Collection
1. Open Postman/Insomnia
2. Import the following environment variables:
   - `base_url`: `http://localhost:8000`
   - `token`: (will be set after login)

### Test Sequence
1. **Health Check**: `GET {{base_url}}/health`
2. **Register User**: `POST {{base_url}}/api/v1/users/`
3. **Login**: `POST {{base_url}}/api/v1/auth/login` (save token)
4. **Upload Document**: `POST {{base_url}}/api/v1/documents/upload`
5. **Process Document**: `POST {{base_url}}/api/v1/documents/{id}/process`
6. **Ask Question**: `POST {{base_url}}/api/v1/chat/ask`

## 🐛 Common Issues & Solutions

### 1. Authentication Errors
- **Issue**: `401 Unauthorized`
- **Solution**: Ensure token is included in `Authorization: Bearer {token}` header

### 2. Document Processing Fails
- **Issue**: Processing returns errors
- **Solutions**:
  - Check if OpenAI API key is set correctly
  - Verify PDF is not corrupted
  - Check database connectivity

### 3. Database Connection Errors
- **Issue**: `Connection refused` errors
- **Solutions**:
  - Verify PostgreSQL is running
  - Check `DATABASE_URL` in `.env`
  - Run `alembic upgrade head`

### 4. ChromaDB Issues
- **Issue**: Vector search fails
- **Solutions**:
  - Check `CHROMA_PERSIST_DIRECTORY` exists
  - Verify ChromaDB permissions
  - Try deleting and recreating ChromaDB directory

### 5. OpenAI API Errors
- **Issue**: Embedding generation fails
- **Solutions**:
  - Verify `OPENAI_API_KEY` is valid
  - Check API quota/billing
  - Test with a smaller document

## 📊 Expected Test Results

### Successful Flow:
1. ✅ Health check returns 200
2. ✅ User registration returns 201
3. ✅ Login returns 200 with token
4. ✅ Document upload returns 201
5. ✅ Processing returns 202 with success
6. ✅ Question answering returns 200 with answer
7. ✅ All endpoints return proper JSON responses

### Performance Expectations:
- **Document upload**: < 1 second for typical PDFs
- **Text extraction**: 1-5 seconds depending on PDF size
- **Embedding generation**: 2-10 seconds depending on content
- **Question answering**: 2-5 seconds for typical queries

## 🛠️ Debugging Tips

1. **Check server logs** for detailed error messages
2. **Use the interactive docs** at `/docs` for easier testing
3. **Verify environment variables** are loaded correctly
4. **Test with small PDFs first** before using large documents
5. **Check network connectivity** if using external APIs

## 📈 Performance Testing

For load testing, you can use tools like:
- **Apache Bench**: `ab -n 100 -c 10 http://localhost:8000/health`
- **wrk**: `wrk -t12 -c400 -d30s http://localhost:8000/health`
- **Postman Runner**: For API workflow testing

Remember to test with realistic document sizes and user loads to ensure your system performs well under expected usage.