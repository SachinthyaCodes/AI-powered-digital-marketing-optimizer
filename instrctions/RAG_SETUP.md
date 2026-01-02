# RAG System & Chatbot Setup Guide

## Overview
This guide walks you through setting up the RAG (Retrieval-Augmented Generation) system with Ollama for the MarketMatic chatbot.

## Prerequisites
1. Python 3.9 or higher
2. Ollama installed on your system
3. MongoDB connection
4. Sufficient disk space (~4GB for Ollama models)

## Step 1: Install Ollama

### Windows:
1. Download Ollama from https://ollama.ai/download
2. Run the installer
3. Verify installation:
```powershell
ollama --version
```

### Linux/Mac:
```bash
curl https://ollama.ai/install.sh | sh
```

## Step 2: Pull Required Models

### Pull Embedding Model (Required for RAG):
```powershell
ollama pull nomic-embed-text
```
This model is used to create vector embeddings of your documents (~274MB)

### Pull Chat Model (Required for Responses):
Choose ONE of the following based on your needs:

**Option 1: Llama 2 (Recommended for testing - 3.8GB)**
```powershell
ollama pull llama2
```

**Option 2: Llama 3 (Better quality - 4.7GB)**
```powershell
ollama pull llama3
```

**Option 3: Mistral (Good balance - 4.1GB)**
```powershell
ollama pull mistral
```

**Option 4: Gemma (Smaller, faster - 1.7GB)**
```powershell
ollama pull gemma:2b
```

Update `.env` with your chosen model:
```
OLLAMA_CHAT_MODEL=llama2
```

## Step 3: Verify Ollama is Running

Ollama should start automatically. Verify:
```powershell
ollama list
```

You should see your downloaded models.

## Step 4: Install Python Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

This will install:
- `langchain` - LLM framework
- `chromadb` - Vector database
- `ollama` - Ollama Python client
- `pypdf` - PDF processing
- `openpyxl` - Excel processing
- `python-docx` - Word processing
- And other dependencies

## Step 5: Test the Setup

### Test 1: Check Ollama API
```powershell
curl http://localhost:11434
```
Should return: `Ollama is running`

### Test 2: Start Backend
```powershell
cd backend
python app.py
```

### Test 3: Check RAG Status
```powershell
curl http://localhost:5000/api/rag/status
```

Expected response:
```json
{
  "status": "operational",
  "models": {
    "embedding_model": true,
    "chat_model": true,
    "available_models": ["nomic-embed-text", "llama2"]
  }
}
```

## Step 6: How It Works

### 1. Document Upload Flow:
```
Admin uploads PDF/Excel → 
Extract text → 
Split into chunks → 
Generate embeddings with Ollama → 
Store in ChromaDB
```

### 2. Chat Query Flow:
```
User sends message → 
Generate query embedding → 
Search ChromaDB for similar chunks → 
Retrieve top 5 relevant contexts → 
Send to Ollama with context → 
Generate response → 
Return to user
```

## API Endpoints

### Document Management (Admin Only)

**Upload Document:**
```http
POST /api/rag/upload-document
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data

file: <PDF/Excel/Word/Text file>
```

**Sync FAQs:**
```http
POST /api/rag/sync-faqs
Authorization: Bearer <admin_token>
```

**Sync Products:**
```http
POST /api/rag/sync-products
Authorization: Bearer <admin_token>
```

**Sync Policies:**
```http
POST /api/rag/sync-policies
Authorization: Bearer <admin_token>
```

**Sync All:**
```http
POST /api/rag/sync-all
Authorization: Bearer <admin_token>
```

**Get Documents:**
```http
GET /api/rag/documents
Authorization: Bearer <admin_token>
```

**Delete Document:**
```http
DELETE /api/rag/documents/<doc_id>
Authorization: Bearer <admin_token>
```

**Test Query (Admin Testing):**
```http
POST /api/rag/test-query
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "query": "What are your return policies?"
}
```

### Chatbot API (Public)

**Chat:**
```http
POST /api/rag/chat
Content-Type: application/json

{
  "service_token": "<service_token>",
  "message": "What products do you have?",
  "session_id": "optional-session-id",
  "channel": "website"
}
```

**Get Chat History:**
```http
GET /api/rag/chat/history/<session_id>?limit=20
```

## Usage Flow

### For SuperAdmin:
1. Create services with `service_token`
2. Assign admins to services

### For Admin (SME Owner):
1. Login to dashboard
2. Go to Bot Management
3. Upload documents:
   - Product catalogs (PDF/Excel)
   - FAQs (use FAQ manager or upload Excel)
   - Policies (PDF/Word documents)
   - Any other relevant documents
4. Click "Sync All" to process documents
5. Test chatbot using test interface
6. Share `service_token` for integration

### For End Users:
1. Access chatbot via website widget
2. Ask questions in English/Sinhala
3. Chatbot retrieves relevant context
4. Receives accurate answers from uploaded documents

## Troubleshooting

### Issue: "Error generating embedding"
**Solution:** 
```powershell
ollama pull nomic-embed-text
ollama serve
```

### Issue: "Error generating chat response"
**Solution:**
```powershell
ollama pull llama2
# Or your chosen model
```

### Issue: ChromaDB errors
**Solution:** Delete the ChromaDB directory and restart:
```powershell
Remove-Item -Recurse -Force backend/data/chromadb
```

### Issue: Out of memory
**Solution:** Use a smaller model:
```powershell
ollama pull gemma:2b
```
Update `.env`:
```
OLLAMA_CHAT_MODEL=gemma:2b
```

### Issue: Slow responses
**Solutions:**
1. Use a smaller, faster model (gemma:2b)
2. Reduce context chunks (edit `n_results` in code)
3. Upgrade hardware (Ollama benefits from GPU)

## Performance Tips

1. **GPU Acceleration:** Ollama automatically uses GPU if available
2. **Model Selection:** 
   - Development: `gemma:2b` (fastest)
   - Production: `llama3` or `mistral` (better quality)
3. **Chunk Size:** Default 500 chars works well, adjust in `document_processor.py`
4. **Context Limit:** Default 5 chunks, increase for more context (but slower)

## Database Storage

- **MongoDB:** Stores document metadata, chat history, sessions
- **ChromaDB:** Stores vector embeddings (located in `backend/data/chromadb/`)
- Backup ChromaDB directory regularly for production

## Security Notes

1. `service_token` should be kept secure
2. Chat endpoint is public but requires valid `service_token`
3. Admin endpoints require JWT authentication
4. Consider rate limiting for production
5. Sanitize user inputs

## Next Steps

1. ✅ Install Ollama and models
2. ✅ Install Python dependencies
3. ✅ Test RAG status endpoint
4. Build frontend UI for document upload
5. Create chat widget for website embedding
6. Add WhatsApp/Messenger integrations
7. Implement feedback collection
8. Monitor and improve responses

## Additional Resources

- Ollama Documentation: https://ollama.ai/docs
- ChromaDB Documentation: https://docs.trychroma.com
- LangChain Documentation: https://python.langchain.com

## Support

For issues or questions:
1. Check Ollama logs: `ollama logs`
2. Check backend logs
3. Review MongoDB collections
4. Test individual components
