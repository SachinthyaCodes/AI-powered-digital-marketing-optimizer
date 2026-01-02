# 🚀 Supabase Migration Guide

## Migration Status: In Progress

✅ **Completed:**
- `requirements.txt` - Replaced pymongo/chromadb with sqlalchemy/psycopg2/pgvector
- `models/sqlalchemy_models.py` - All ORM models created (User, Service, Document, DocumentEmbedding, ChatMessage, Product, FAQ, Policy)
- `database.py` - SQLAlchemy engine setup with Supabase PostgreSQL connection
- `services/vector_service.py` - Replaced ChromaDB with pgvector implementation
- `supabase_setup.py` - Database initialization script
- `.env.supabase` - Template environment file with Supabase credentials

🔄 **In Progress:**
- Route files need updating to use SQLAlchemy instead of MongoDB

---

## Step 1: Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up / login
3. Create a new project
4. Wait for database to be provisioned (~2 minutes)
5. Go to **Settings** → **Database** → **Connection String**
6. Copy the connection string in **URI** format

Example format:
```
postgresql://postgres:[YOUR_PASSWORD]@db.[PROJECT_ID].supabase.co:5432/postgres
```

---

## Step 2: Update Environment Variables

1. Open `backend/.env.supabase`
2. Replace `YOUR_SUPABASE_PASSWORD` with your database password
3. Replace `YOUR_SUPABASE_HOST` with your Supabase host (e.g., `db.xyzabc.supabase.co`)
4. Or paste full `DATABASE_URL` from Supabase console

Example:
```env
DATABASE_URL=postgresql://postgres:MyPassword123@db.xyzabc.supabase.co:5432/postgres
```

5. Copy contents to `.env`:
```bash
cd backend
cp .env.supabase .env
```

---

## Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `sqlalchemy==2.0.23` - ORM
- `psycopg2-binary==2.9.9` - PostgreSQL driver
- `pgvector==0.2.4` - Vector support
- All other required packages

---

## Step 4: Initialize Database

```bash
cd backend
python supabase_setup.py
```

This will:
1. ✅ Test Supabase connection
2. ✅ Enable pgvector extension
3. ✅ Create all tables
4. ✅ Create superadmin account (`superadmin@marketmatic.com` / `superadmin`)
5. ✅ Create indexes for performance

---

## Step 5: Architecture Overview

### Before (MongoDB + ChromaDB)
```
Frontend ↔ Backend ↔ MongoDB (users, services, etc.)
                  ↔ ChromaDB (embeddings)
                  ↔ Ollama (llama3, embeddings)
```

### After (Supabase + pgvector)
```
Frontend ↔ Backend ↔ Supabase PostgreSQL (everything!)
                  ↔ Ollama (llama3, embeddings)
```

**Benefits:**
- ✅ Single database for all data
- ✅ pgvector handles embeddings natively
- ✅ Better performance with SQL joins
- ✅ ACID transactions
- ✅ Easier backup/restore
- ✅ Managed service (automatic updates)

---

## Step 6: Database Schema

### Tables Created:

1. **users** - User accounts
   - id, email, password, full_name, company_name, role, service_id
   - Unique: email

2. **services** - Business services
   - id, shop_name, owner_name, service_token, bot_name, etc.
   - Unique: service_token

3. **documents** - Uploaded documents
   - id, service_id, filename, content, document_type, is_processed, chunk_count
   - Index: (service_id, created_at)

4. **document_embeddings** (pgvector)
   - id, service_id, document_id, content, embedding (768-dim vector)
   - Stores chunks + embeddings from documents
   - Index: service_id

5. **chat_messages** - Conversation history
   - id, service_id, session_id, role, content, context, metadata
   - Index: (session_id, timestamp), (service_id, timestamp)

6. **products** - Product catalog
   - id, service_id, name, description, price, image_url

7. **faqs** - Frequently asked questions
   - id, service_id, question, answer, language

8. **policies** - Business policies
   - id, service_id, title, content, policy_type

---

## Step 7: Key Differences from MongoDB

### Before (MongoDB):
```python
# MongoDB (old)
db = MongoClient(url)[database_name]
users_collection = db['users']
user = users_collection.insert_one({
    'email': 'test@example.com',
    'password': hashed_pw,
    'created_at': datetime.utcnow()
})
```

### After (Supabase/SQLAlchemy):
```python
# Supabase with SQLAlchemy (new)
from database import SessionLocal
from models.sqlalchemy_models import User

db = SessionLocal()
user = User(
    email='test@example.com',
    password=User.hash_password('password'),
)
db.add(user)
db.commit()
```

### Embedding Search:

**Before (ChromaDB):**
```python
results = chroma_collection.query(
    query_embeddings=[embedding],
    n_results=5
)
```

**After (pgvector):**
```python
results = db.query(DocumentEmbedding).order_by(
    text("embedding <-> :query_embedding")
).limit(5).params(query_embedding=embedding).all()
```

---

## Step 8: Remaining Work

### Routes to Update:

1. **auth_routes.py**
   - Replace `db['users'].find_one()` with `db.query(User).filter(...)`
   - Replace `db['users'].insert_one()` with `db.add(User(...))`
   - Keep JWT logic same

2. **bot_routes.py**
   - Replace `db['services'].find_one()` with `db.query(Service).filter(...)`
   - Replace `db['services'].update_one()` with `db.query(Service).update()`

3. **document_routes.py**
   - Replace `db['documents'].insert_one()` with `db.add(Document(...))`
   - Use `vector_service.add_document_embeddings()` for embeddings

4. **rag_routes.py**
   - Replace document retrieval with SQLAlchemy queries
   - Use `vector_service.search_similar_documents()` for semantic search

5. **chat_routes.py**
   - Replace `db['chat_messages'].insert_one()` with `db.add(ChatMessage(...))`
   - Use pgvector search for context retrieval

6. **Other routes:**
   - service_routes.py
   - superadmin_routes.py
   - etc.

---

## Step 9: Testing Checklist

```
☐ Install dependencies (pip install -r requirements.txt)
☐ Run supabase_setup.py (python supabase_setup.py)
☐ Start backend (python app.py)
☐ Login with superadmin@marketmatic.com / superadmin
☐ Create service
☐ Upload document
☐ Check DocumentEmbedding table in Supabase
☐ Test chatbot queries
☐ Verify embeddings are stored correctly
```

---

## Step 10: Migration from Old MongoDB Data (Optional)

If you have existing MongoDB data:

```bash
# Create migration script (will create migrate_data.py)
python create_migration_script.py

# Run migration
python migrate_data.py
```

This will:
1. Read from MongoDB
2. Create equivalent records in Supabase
3. Generate embeddings for documents
4. Store in pgvector

---

## Troubleshooting

### "Connection refused" to Supabase
- Check DATABASE_URL in .env
- Verify Supabase project is active
- Check network connectivity
- Verify IP is whitelisted in Supabase

### "pgvector extension not found"
- Run: `python supabase_setup.py` again
- It creates the extension automatically

### Embeddings not being generated
- Check Ollama is running: `ollama serve`
- Verify OLLAMA_BASE_URL in .env

### Slow queries
- pgvector automatically creates HNSW indexes
- Check SQL query plans in Supabase

---

## Performance Tips

1. **Batch operations** - Insert multiple embeddings at once
2. **Use indexes** - Already created on service_id, (session_id, timestamp)
3. **Limit embedding search** - Use LIMIT clause (default: 5 results)
4. **Connection pooling** - SQLAlchemy handles this automatically

---

## Resources

- [Supabase Docs](https://supabase.com/docs)
- [pgvector Guide](https://github.com/pgvector/pgvector)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [PostgreSQL Full Text Search](https://www.postgresql.org/docs/current/textsearch.html)

---

## Summary

**What's Changed:**
- ❌ MongoDB → ✅ PostgreSQL (Supabase)
- ❌ ChromaDB → ✅ pgvector (in PostgreSQL)
- ❌ Manual ORM → ✅ SQLAlchemy ORM
- ✅ Ollama stays (local embeddings & chat)

**Result:**
- Simpler architecture (1 database)
- Better performance
- Production-ready
- Easier scaling
- Native vector support

Let's get started! 🚀
