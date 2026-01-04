# Ollama Setup Guide for MarketMatic

## ✅ Migration Complete: SinLlama → Ollama

The system has been migrated from SinLlama to **Ollama** for English-only RAG processing.

---

## 📋 Prerequisites

### 1. Install Ollama

**Windows:**
```bash
# Download and install from: https://ollama.ai/download
# Or use winget:
winget install Ollama.Ollama
```

**Mac:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

---

## 🚀 Quick Start

### 1. Start Ollama Server

```bash
ollama serve
```

This will start Ollama on `http://localhost:11434`

### 2. Pull Required Models

```bash
# Chat model (4GB - for answer generation)
ollama pull llama3

# Embedding model (274MB - for document embeddings)
ollama pull nomic-embed-text
```

### 3. Verify Installation

```bash
# Test chat model
ollama run llama3 "Hello, how are you?"

# Test embedding model
ollama run nomic-embed-text "Test embedding"
```

### 4. Start Backend

```bash
cd backend
python app.py
```

---

## 🔧 Configuration

Your `.env` file is already configured:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

---

## 📊 System Architecture

```
User Uploads Document
    ↓
Extract Text (PDF/DOCX/TXT)
    ↓
Chunk Text (500 words, 50 word overlap)
    ↓
Extract FAQs (Q:/A: pattern matching)
    ↓
Generate Embeddings (all-MiniLM-L6-v2)
    ↓
Store in FAISS Index
    ↓
Save FAQs to Database

User Asks Question
    ↓
Search FAISS (find relevant chunks)
    ↓
Generate Answer (Ollama llama3)
    ↓
Return Answer + Sources
```

---

## 🎯 API Endpoints

### Test System
```bash
curl http://localhost:5000/api/rag/test
```

### Upload Document
```bash
curl -X POST http://localhost:5000/api/rag/upload-document \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "service_id=my-service"
```

### Query RAG
```bash
curl -X POST http://localhost:5000/api/rag/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is your return policy?",
    "service_id": "my-service",
    "top_k": 3
  }'
```

### Search Only (no answer)
```bash
curl -X POST http://localhost:5000/api/rag/search \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "shipping information",
    "service_id": "my-service",
    "top_k": 5
  }'
```

### Get Status
```bash
curl http://localhost:5000/api/rag/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Rebuild Index
```bash
curl -X POST http://localhost:5000/api/rag/rebuild-index \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"service_id": "my-service"}'
```

---

## 📝 Document Format for FAQ Extraction

Your documents should use Q&A format:

**Example:**
```
Q: What is your return policy?
A: We accept returns within 30 days of purchase.

Q: How long does shipping take?
A: Standard shipping takes 5-7 business days.

Question: Do you offer international shipping?
Answer: Yes, we ship to over 50 countries worldwide.
```

---

## 🔍 Models Used

### Chat Model: Llama 3 (8B)
- **Size:** ~4GB
- **Purpose:** Generate answers to user questions
- **Context:** 8K tokens
- **Language:** English

### Embedding Model: all-MiniLM-L6-v2
- **Size:** ~90MB
- **Purpose:** Convert text to 384D vectors
- **Speed:** Very fast (sentence-transformers)
- **Language:** English

### Alternative Models (Optional)

You can change models in `.env`:

**Smaller/Faster Chat:**
```env
OLLAMA_CHAT_MODEL=llama3:8b-instruct-fp16
# or
OLLAMA_CHAT_MODEL=mistral
```

**Larger/Better Chat:**
```env
OLLAMA_CHAT_MODEL=llama3:70b
```

---

## ⚡ Performance Tips

### 1. Keep Ollama Running
```bash
# Run as background service (Windows)
ollama serve

# Or install as Windows service
```

### 2. Optimize Chunk Size
Edit in `ollama_rag_service.py`:
```python
chunks = self.chunk_text(text, chunk_size=500, overlap=50)
```

### 3. Adjust Top K Results
```python
# In query request
{"question": "...", "top_k": 5}  # Default: 3
```

### 4. GPU Acceleration (Optional)
Ollama automatically uses GPU if available (NVIDIA CUDA, Apple Metal)

---

## 🛠️ Troubleshooting

### Ollama Not Running
```bash
# Check if running
curl http://localhost:11434/api/tags

# Start if not running
ollama serve
```

### Model Not Found
```bash
# Pull required models
ollama pull llama3
ollama pull nomic-embed-text

# List installed models
ollama list
```

### Port Already in Use
```bash
# Change port in .env
OLLAMA_BASE_URL=http://localhost:11435

# Start Ollama on different port
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

### Slow Response
```bash
# Use smaller model
ollama pull llama3:8b-instruct-q4_0

# Update .env
OLLAMA_CHAT_MODEL=llama3:8b-instruct-q4_0
```

---

## 📂 Files Changed

### New Files:
- ✅ `backend/services/ollama_rag_service.py` - Main RAG service
- ✅ `OLLAMA_SETUP.md` - This guide
- ✅ `OLLAMA_MIGRATION.md` - Migration summary

### Updated Files:
- ✅ `backend/.env` - Enabled Ollama config
- ✅ `backend/routes/rag_routes.py` - All RAG endpoints
- ✅ `backend/services/ollama_service.py` - Added logging
- ✅ `backend/requirements.txt` - Dependencies

### Removed:
- ❌ All SinLlama-related code
- ❌ All tokenizer-specific code
- ❌ All Sinhala/code-mix processing

---

## ✅ What Works Now

1. **Document Upload** - PDF, DOCX, TXT, XLSX
2. **Automatic Chunking** - 500 words per chunk
3. **FAQ Extraction** - Automatic Q&A detection
4. **Vector Search** - Fast FAISS similarity search
5. **Answer Generation** - Ollama llama3
6. **Multi-tenant** - Isolated per service_id
7. **Database Storage** - FAQs saved to PostgreSQL

---

## 🎉 Test It!

```bash
# 1. Start Ollama
ollama serve

# 2. Start backend
cd backend
python app.py

# 3. Test system
curl http://localhost:5000/api/rag/test

# 4. Upload a document (via frontend or API)

# 5. Ask questions!
```

---

**System is ready for English-only RAG processing with Ollama! 🚀**
