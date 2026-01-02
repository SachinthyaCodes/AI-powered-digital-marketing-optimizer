# 🧠 RAG System Deep Analysis - MarketMatic

## Architecture Overview

Your RAG (Retrieval-Augmented Generation) system uses a **hybrid approach** combining:
1. **Structured Data** (FAQs, Products, Policies) from PostgreSQL
2. **Vector Search** (Document embeddings) using Supabase pgvector
3. **AI Generation** using SinLlama GGUF model (8.1B parameters)

---

## 📊 System Components

### 1. **Vector Database: Supabase pgvector**
```sql
Extension: vector (PostgreSQL extension)
Embedding Dimension: 768 (nomic-embed-text)
Similarity Metric: Cosine distance (<-> operator)
```

**Table Structure:**
```python
document_embeddings:
- id (UUID)
- service_id (UUID) - Multi-tenant isolation
- document_id (UUID) - Link to source document
- chunk_index (Integer) - Chunk position
- chunk_text (Text) - Original text chunk
- embedding (Vector<768>) - Embedding vector
- chunk_metadata (JSON) - Additional metadata
```

### 2. **Embedding Model: Ollama + nomic-embed-text**
- **Model**: nomic-embed-text
- **Dimension**: 768
- **Runtime**: Ollama (Local server at localhost:11434)
- **Purpose**: Convert text chunks to vector embeddings

**Process:**
```python
Text → Ollama API → nomic-embed-text → 768-dim vector
```

### 3. **Document Processing Pipeline**
```
Upload → Extract Content → Chunk Text → Generate Embeddings → Store in pgvector
```

**Supported Formats:**
- PDF (via pypdf)
- Excel (.xlsx, .xls via pandas/openpyxl)
- Word (.docx via python-docx)
- Plain Text (.txt)

**Chunking Strategy:**
- **Chunk Size**: 512 characters
- **Overlap**: 50 characters
- **Smart Splitting**: Breaks at sentence boundaries (`.!?\n`)
- **Purpose**: Preserve context while enabling granular retrieval

---

## 🔄 RAG Workflow

### **Document Upload Flow:**

```
1. Admin uploads document
   ↓
2. DocumentProcessor extracts content based on file type
   ↓
3. Content split into 512-char chunks with 50-char overlap
   ↓
4. For each chunk:
   - Generate embedding via Ollama (nomic-embed-text)
   - Create DocumentEmbedding record
   - Store in Supabase pgvector
   ↓
5. Update Document record:
   - is_processed = True
   - chunk_count = N
   - embedding_count = N
```

**Code Location:** `routes/rag_routes.py::upload_document()`

---

### **Chat Query Flow:**

```
1. User sends message
   ↓
2. Get business context:
   - FAQs (20 latest active)
   - Products (30 latest active)
   - Policies (10 latest active)
   ↓
3. Get conversation history (last 5 messages)
   ↓
4. Generate response using SinLlama:
   - Input: query + business_context + history
   - Model: SinLlama GGUF (8.1B)
   - Output: Bilingual response (English/Sinhala)
   ↓
5. Store user message + bot response
   ↓
6. Return to frontend
```

**Code Location:** `routes/chat_routes.py::send_chat_message()`

---

### **Vector Search Flow (RAG):**

```
1. Receive search query
   ↓
2. Generate query embedding:
   Ollama.embed(query) → 768-dim vector
   ↓
3. Cosine similarity search in pgvector:
   SELECT * FROM document_embeddings
   WHERE service_id = :id
   ORDER BY embedding <-> :query_embedding
   LIMIT 5
   ↓
4. Return ranked results with similarity scores:
   [
     {
       "chunk_text": "...",
       "similarity_score": 0.87,
       "document_id": "...",
       "chunk_index": 3
     }
   ]
```

**Code Location:** `services/vector_service.py::search_similar_documents()`

---

## 🔍 Current Implementation Status

### ✅ **What's Working:**

1. **Document Upload**
   - PDF, Excel, Word, Text extraction ✅
   - Chunking with overlap ✅
   - Embedding generation (Ollama) ✅
   - Storage in pgvector ✅

2. **Vector Search**
   - Query embedding generation ✅
   - Cosine similarity search ✅
   - Multi-tenant isolation (service_id) ✅
   - Result ranking by similarity ✅

3. **Chat System**
   - Structured data retrieval (FAQs, Products, Policies) ✅
   - Conversation history ✅
   - SinLlama integration ✅
   - Bilingual support (English/Sinhala) ✅

### ⚠️ **Gap Identified: RAG NOT Integrated in Chat**

**Current Issue:** 
The chat system (`chat_routes.py`) uses **structured data only** (FAQs, Products, Policies) but **does NOT use vector search** for document retrieval!

**Evidence:**
```python
# chat_routes.py::send_chat_message()
business_context = get_business_context(service_id)  # Only structured data
# No vector search here! ❌

# vs what should happen:
relevant_chunks = vector_service.search_similar_documents(
    query=user_message,
    service_id=service_id,
    limit=5
)
```

---

## 📈 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                          │
│  • BusinessChatDemo.jsx                                      │
│  • Sends message to /api/chat/message                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                 Backend (Flask)                              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Chat Routes (chat_routes.py)                        │  │
│  │  • Receives user message                             │  │
│  │  • Gets structured context (FAQs, Products, Policies)│  │
│  │  • ❌ MISSING: Vector search for documents           │  │
│  │  • Calls SinLlama for response generation            │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               │                                              │
│               ├──→ SinLlama Service (sinllama_service.py)   │
│               │    • Generates bilingual response            │
│               │    • n_ctx=2048, 10 CPU threads             │
│               │                                              │
│               └──→ PostgreSQL (Supabase)                    │
│                    • Fetch FAQs, Products, Policies         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  RAG Routes (rag_routes.py)                          │  │
│  │  • /upload-document - Upload & process documents     │  │
│  │  • /search - Vector search endpoint                  │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               │                                              │
│               ├──→ Document Processor (document_processor)  │
│               │    • Extract text from PDF/Excel/Word/TXT   │
│               │    • Chunk into 512-char pieces             │
│               │                                              │
│               ├──→ Vector Service (vector_service.py)       │
│               │    • Generate embeddings (Ollama)           │
│               │    • Store in pgvector                      │
│               │    • Cosine similarity search               │
│               │                                              │
│               └──→ Ollama Service (localhost:11434)         │
│                    • nomic-embed-text (768-dim)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│          Supabase PostgreSQL + pgvector                      │
│                                                              │
│  Tables:                                                     │
│  • users, services, faqs, products, policies                │
│  • documents (uploaded files)                               │
│  • document_embeddings (768-dim vectors) ← pgvector         │
│  • chat_messages (conversation history)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Data Flow Examples

### **Example 1: Document Upload**

```
Admin uploads "product_catalog.pdf"
  ↓
Extract: "Our premium coffee beans are sourced from..."
  ↓
Chunk 1: "Our premium coffee beans are sourced from Ella..."
Chunk 2: "from Ella region. Price: Rs. 2,500 per kg..."
  ↓
Ollama embedding:
  Chunk 1 → [0.234, -0.123, 0.567, ...] (768 dims)
  Chunk 2 → [0.156, -0.289, 0.421, ...] (768 dims)
  ↓
Store in document_embeddings table with pgvector
```

### **Example 2: Vector Search**

```
Query: "Tell me about coffee prices"
  ↓
Ollama embedding:
  Query → [0.245, -0.134, 0.543, ...] (768 dims)
  ↓
pgvector cosine search:
  SELECT * WHERE service_id = '...'
  ORDER BY embedding <-> query_embedding
  LIMIT 5
  ↓
Results:
  1. "...Price: Rs. 2,500 per kg..." (score: 0.89)
  2. "...Premium coffee beans..." (score: 0.82)
  3. "...Ella region..." (score: 0.76)
```

### **Example 3: Current Chat (Without RAG)**

```
User: "කෝපි මිල කීයද?" (What's the coffee price?)
  ↓
Get business context:
  • FAQs: 20 items
  • Products: 30 items (may or may not have coffee)
  • Policies: 10 items
  ↓
SinLlama generates response based on structured data only
  ↓
Response: "Based on our product catalog, ..."
```

**Problem:** If coffee prices are in uploaded PDF documents, they won't be retrieved!

---

## 🚨 Critical Gap: RAG Integration Missing

### **What You Have:**
✅ Vector database (pgvector) with embeddings
✅ Search endpoint (`/api/rag/search`)  
✅ Document upload and processing
✅ Ollama embedding generation

### **What's Missing:**
❌ Integration of vector search into chat flow
❌ Chat doesn't call `vector_service.search_similar_documents()`
❌ Document knowledge is isolated from conversations

### **Impact:**
- Uploaded documents are **stored but unused** in chat
- Chat relies **only on FAQs/Products/Policies** in database
- RAG capability exists but is **not active**

---

## 🔧 Recommended Fixes

### **Priority 1: Integrate Vector Search into Chat**

Modify `chat_routes.py::send_chat_message()`:

```python
# BEFORE (current):
business_context = get_business_context(service_id)

# AFTER (with RAG):
business_context = get_business_context(service_id)

# Add vector search for documents
from services.vector_service import VectorService
vector_service = VectorService()

relevant_docs = vector_service.search_similar_documents(
    query=user_message,
    service_id=service_id,
    limit=5,
    db_session=db
)

# Append document context
if relevant_docs:
    business_context += "\n\n=== Relevant Document Information ===\n"
    for doc in relevant_docs:
        business_context += f"{doc['chunk_text']}\n\n"
```

### **Priority 2: Add Document Context Indicator**

Show users when answers come from uploaded documents vs structured data.

### **Priority 3: Improve Chunking Strategy**

Current: Fixed 512 chars  
Better: Semantic chunking (paragraph/section-based)

### **Priority 4: Add Retrieval Metrics**

Track:
- Average similarity scores
- Number of documents retrieved per query
- Context utilization rate

---

## 📊 Current Database Schema

```sql
-- Documents table
documents:
  id              UUID PRIMARY KEY
  service_id      UUID FOREIGN KEY → services
  filename        VARCHAR(255)
  content         TEXT
  document_type   VARCHAR(50)
  is_processed    BOOLEAN DEFAULT false
  chunk_count     INTEGER DEFAULT 0
  embedding_count INTEGER DEFAULT 0
  created_at      TIMESTAMP

-- Vector embeddings (pgvector)
document_embeddings:
  id              UUID PRIMARY KEY
  service_id      UUID FOREIGN KEY → services
  document_id     UUID FOREIGN KEY → documents
  chunk_index     INTEGER
  content         TEXT
  embedding       VECTOR(768)  ← pgvector type
  chunk_metadata  JSON
  created_at      TIMESTAMP

-- Index for vector search
CREATE INDEX ON document_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

---

## 🎓 Technologies Used

1. **pgvector** - PostgreSQL extension for vector similarity search
2. **Ollama** - Local LLM server for embeddings
3. **nomic-embed-text** - 768-dimensional embedding model
4. **SinLlama GGUF** - 8.1B parameter bilingual LLM
5. **SQLAlchemy** - ORM for database operations
6. **pypdf, python-docx, openpyxl** - Document processing

---

## 💡 Next Steps

1. **Integrate RAG into chat** (Priority 1)
2. **Test with sample documents** (product catalogs, FAQs)
3. **Monitor retrieval quality** (similarity scores)
4. **Optimize chunk size** (experiment with 256, 512, 1024)
5. **Add hybrid search** (combine vector + keyword search)
6. **Implement re-ranking** (reorder results for better relevance)

---

**System Status:** ⚠️ **Partially Functional**  
- Vector database: ✅ Working
- Document upload: ✅ Working  
- Vector search endpoint: ✅ Working
- **RAG in chat: ❌ Not integrated**

**Recommendation:** Integrate vector search into chat flow to unlock full RAG capabilities!
