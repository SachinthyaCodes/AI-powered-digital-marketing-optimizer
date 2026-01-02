# 🎯 AI-Powered Digital Marketing Optimizer - Clean Project Structure

## 📁 Project Overview
Bilingual (English-Sinhala) RAG Chatbot for Sri Lankan SMEs powered by SinLlama GGUF model.

---

## 🗂️ Directory Structure

```
AI-powered-digital-marketing-optimizer/
│
├── 📁 backend/                      # Backend application
│   ├── 📄 app.py                    # Main Flask application
│   ├── 📄 config.py                 # Configuration settings
│   ├── 📄 database.py               # Database models and setup
│   ├── 📄 requirements.txt          # Python dependencies
│   ├── 📄 start_simple.py           # Start the server
│   │
│   ├── 📁 auth/                     # Authentication & JWT
│   ├── 📁 models/                   # Database models
│   ├── 📁 routes/                   # API routes
│   ├── 📁 services/                 # Business logic (SinLlama service)
│   ├── 📁 utils/                    # Utility functions
│   ├── 📁 data/                     # ChromaDB and data storage
│   │
│   ├── 📊 SINLLAMA_RESEARCH_METRICS.md         # Research documentation
│   ├── 📊 SINLLAMA_RESEARCH_REPORT.json        # Metrics data
│   └── 📊 SinLlama_Research_Report.pdf         # Final PDF report
│
├── 📁 frontend/                     # React frontend
│   ├── 📁 src/
│   │   ├── 📁 pages/
│   │   │   └── BusinessChatDemo.jsx  # Main chatbot UI
│   │   ├── 📁 components/
│   │   └── ...
│   ├── 📄 package.json
│   ├── 📄 vite.config.js
│   └── 📄 tailwind.config.js
│
├── 📁 instrctions/                  # Documentation archive
│
└── 📄 README.md                     # Project documentation
```

---

## 🚀 Quick Start

### 1. Start Backend
```bash
cd backend
python start_simple.py
```
Server runs on: `http://localhost:5000`

### 2. Start Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on: `http://localhost:5173`

---

## 🤖 SinLlama Model Configuration

**Model:** sinllama-q4_k_m.gguf (8.1B parameters, Q4_K quantization)

**Performance:**
- Context Window: 4096 tokens
- CPU Threads: 10
- Speed: ~0.72 words/second
- Accuracy: 85% overall
- Pricing Accuracy: 95%
- Language Matching: 90%

**Location:** `backend/services/sinllama_service.py`

---

## 📊 Research Reports

All research documentation is in the `backend/` directory:

1. **SinLlama_Research_Report.pdf** - Professional PDF report
2. **SINLLAMA_RESEARCH_REPORT.json** - Complete metrics data
3. **SINLLAMA_RESEARCH_METRICS.md** - Formatted documentation

---

## 🗄️ Database

- **Type:** PostgreSQL (Supabase)
- **Vector Store:** pgvector (768 dimensions)
- **Embeddings:** nomic-embed-text via Ollama
- **Configuration:** See `.env.example` in backend/

---

## 🧹 Cleanup Summary

**Removed (57 files):**
- 24 test files (test_*.py)
- 13 obsolete setup/utility scripts
- 5 Modal deployment files (no longer used)
- 6 obsolete documentation files
- 3 duplicate JSON report files
- 2 redundant server start scripts
- 1 old database file (test.db)

**Kept (Essential):**
- Core application files (app.py, config.py, database.py)
- All routes, models, services, utils
- SinLlama service implementation
- Final research reports (PDF, JSON, MD)
- Requirements and configuration files
- Complete frontend application

---

## 📝 Notes

- The chatbot UI has been redesigned with a modern two-column layout
- SinLlama model is optimized for CPU performance
- Prompt engineering implemented for bilingual (English-Sinhala) responses
- RAG system uses Supabase pgvector for document retrieval
- All research metrics have been collected and documented

---

## 🛠️ Technology Stack

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- Lucide Icons

**Backend:**
- Flask
- SQLAlchemy
- PostgreSQL (Supabase)
- llama-cpp-python
- SinLlama GGUF

**AI/ML:**
- SinLlama 8.1B (GGUF format)
- Ollama (nomic-embed-text embeddings)
- pgvector (RAG)

---

**Last Updated:** December 30, 2024
**Status:** ✅ Production Ready
