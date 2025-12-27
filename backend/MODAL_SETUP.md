# Modal RAG Setup Guide for MarketMatic

## Issue: Python 3.13 Compatibility
Modal SDK currently requires Python 3.11 or 3.12 (not 3.13).

## Solution Options

### Option 1: Use Python 3.11/3.12 Virtual Environment (Recommended)
1. **Install Python 3.11 or 3.12**:
   - Download from https://www.python.org/downloads/
   - Install alongside Python 3.13 (don't uninstall 3.13)

2. **Create new virtual environment with Python 3.11/3.12**:
   ```powershell
   # Navigate to backend folder
   cd "d:\Research project\PP1 progress\marketmatic\backend"
   
   # Remove old venv
   Remove-Item -Recurse -Force venv
   
   # Create new venv with Python 3.11/3.12
   py -3.11 -m venv venv  # or py -3.12
   
   # Activate
   .\venv\Scripts\Activate.ps1
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Setup Modal**:
   ```powershell
   python -m modal setup
   # This opens browser for authentication
   ```

4. **Test Modal service**:
   ```powershell
   modal run modal_rag_service.py --test-type embedding
   modal run modal_rag_service.py --test-type chat
   ```

5. **Deploy Modal service**:
   ```powershell
   modal deploy modal_rag_service.py
   # Copy the URLs displayed after deployment
   ```

6. **Update .env with Modal URLs**:
   ```
   MODAL_EMBEDDING_URL=https://your-workspace--marketmatic-rag-embed.modal.run
   MODAL_CHAT_URL=https://your-workspace--marketmatic-rag-chat.modal.run
   ```

### Option 2: Use Alternative LLM Service (Quick Start)
If you want to test immediately without Python version changes, use OpenAI or other API-based services.

## Modal Service Features

### What Modal Provides:
- **Serverless GPU**: Automatic scaling with T4 GPU
- **Fast cold starts**: ~2-3 seconds
- **Pay per use**: Only charged when running
- **No infrastructure**: No Docker/Kubernetes setup
- **HTTP endpoints**: Easy REST API integration

### Models Used:
1. **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
   - 384-dimensional vectors
   - Fast and efficient
   - Good for semantic search

2. **Chat**: `polyglots/SinLlama_v01`
   - Sinhala-English bilingual LLaMA model
   - Specifically trained for Sinhala language
   - Based on LLaMA architecture
   - Excellent for Sri Lankan business context
   - Native Sinhala and English support

### Cost Estimate:
- Free tier: 30 credits/month (enough for testing)
- T4 GPU: ~$0.30/hour
- Typical chatbot request: ~1 second = $0.00008

## Architecture

```
User Query
    ↓
Flask Backend (rag_routes.py)
    ↓
Modal Service (modal_rag_service.py)
    ↓
├─ Embedding Model (sentence-transformers)
│  ↓
│  ChromaDB (local vector storage)
│  ↓
│  Semantic Search
│  ↓
└─ Chat Model (Qwen2.5-1.5B)
   ↓
Response to User
```

## API Endpoints

### After Modal Deployment:

1. **Generate Embedding** (POST):
   ```
   https://your-workspace--marketmatic-rag-embed.modal.run
   
   Request:
   {
     "text": "What products do you sell?"
   }
   
   Response:
   {
     "embedding": [0.123, -0.456, ...]  // 384-dim vector
   }
   ```

2. **Generate Chat Response** (POST):
   ```
   https://your-workspace--marketmatic-rag-chat.modal.run
   
   Request:
   {
     "query": "What are your prices?",
     "context": "Product catalog: T-shirts Rs. 1500...",
     "conversation_history": [...],
     "language": "en"
   }
   
   Response:
   {
     "response": "Our prices are: T-shirts Rs. 1500..."
   }
   ```

## Flask Backend Integration

Your Flask backend (`services/modal_service.py`) will:
1. Receive user queries via `/api/rag/chat`
2. Search ChromaDB for relevant documents
3. Call Modal's chat endpoint with query + context
4. Return AI-generated response
5. Store conversation history in MongoDB

## Testing

### 1. Test Modal Service (Remote):
```powershell
# Test embedding generation
modal run modal_rag_service.py --test-type embedding

# Test chat response
modal run modal_rag_service.py --test-type chat
```

### 2. Test Flask Backend (Local):
```powershell
# Start Flask server
python app.py

# Test RAG status
curl http://localhost:5000/api/rag/status

# Test document upload (requires admin login)
curl -X POST http://localhost:5000/api/rag/upload-document \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@document.pdf"

# Test chatbot (requires service token)
curl -X POST http://localhost:5000/api/rag/chat \
  -H "Content-Type: application/json" \
  -d '{
    "service_token": "YOUR_SERVICE_TOKEN",
    "message": "What products do you sell?"
  }'
```

## Troubleshooting

### Python Version Error:
```
RuntimeError: This version of Modal does not support Python 3.13+
```
**Solution**: Use Python 3.11 or 3.12 (see Option 1 above)

### Modal URLs Not Configured:
```
ValueError: MODAL_EMBEDDING_URL not configured in .env file
```
**Solution**: Deploy Modal service and update .env with the URLs

### ChromaDB Permission Error:
**Solution**: Check `backend/data/chromadb/` folder exists and has write permissions

### Modal Authentication Failed:
```
modal setup
```
This opens browser for authentication. If it doesn't open:
1. Go to https://modal.com
2. Sign up/login
3. Get API token from settings
4. Run `modal token set --token-id YOUR_ID --token-secret YOUR_SECRET`

## Next Steps

1. **Install Python 3.11/3.12** (if needed)
2. **Recreate virtual environment**
3. **Setup Modal authentication**
4. **Deploy Modal service**
5. **Update .env with URLs**
6. **Test Flask backend**
7. **Build frontend UI** (Tasks 8-9 in todo list)

## Alternative: Use Existing LLM APIs

If Modal setup is complex, you can modify `services/modal_service.py` to use:
- **OpenAI API**: GPT-3.5/4 for chat, text-embedding-3-small for embeddings
- **Cohere API**: Command model for chat, embed-multilingual for embeddings
- **Hugging Face Inference API**: Various open models

This requires less setup but has per-request costs.
