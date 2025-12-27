# Supabase Migration - Quick Reference Card

## 📦 Installation

```bash
cd backend
pip install -r requirements.txt
```

**New packages:**
- sqlalchemy==2.0.23
- psycopg2-binary==2.9.9
- pgvector==0.2.4
- supabase==2.3.4

---

## 🔑 Environment Setup

**1. Create Supabase project:** https://supabase.com

**2. Get connection string:**
- Settings → Database → Connection String (URI format)
- Copy: `postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres`

**3. Update `.env`:**
```env
DATABASE_URL=postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

---

## ⚡ Initialize Database

```bash
python supabase_setup.py
```

**Output:**
```
✅ Supabase connection successful
✅ pgvector extension enabled
✅ All tables created (8 tables)
✅ Superadmin created: superadmin@marketmatic.com / superadmin
```

---

## 🗄️ Database Tables

| Table | Purpose | Key Columns |
|-------|---------|------------|
| **users** | User accounts | id, email, password, role, service_id |
| **services** | Business services | id, shop_name, service_token, bot_name |
| **documents** | Uploaded files | id, service_id, filename, is_processed |
| **document_embeddings** | Vector embeddings | id, service_id, content, **embedding** (768-dim) |
| **chat_messages** | Conversations | id, session_id, role, content, context |
| **products** | Product catalog | id, service_id, name, price, image_url |
| **faqs** | FAQ items | id, service_id, question, answer |
| **policies** | Business policies | id, service_id, title, content |

---

## 🔄 Common SQLAlchemy Patterns

### Query Single Record
```python
from database import SessionLocal
from models.sqlalchemy_models import User

db = SessionLocal()
user = db.query(User).filter(User.email == email).first()
db.close()
```

### Insert Record
```python
user = User(
    email='test@example.com',
    password=User.hash_password('password'),
    full_name='John Doe'
)
db.add(user)
db.commit()
```

### Update Record
```python
user = db.query(User).filter(User.id == user_id).first()
user.full_name = 'Jane Doe'
db.commit()
```

### Delete Record
```python
db.query(User).filter(User.id == user_id).delete()
db.commit()
```

### Vector Search (pgvector)
```python
from sqlalchemy import text

results = db.query(
    DocumentEmbedding.id,
    DocumentEmbedding.content,
    text("1 - (embedding <-> :query_embedding) as similarity")
).filter(
    DocumentEmbedding.service_id == service_id
).order_by(
    text("embedding <-> :query_embedding")
).limit(5).params(
    query_embedding=query_vector
).all()
```

---

## 🧩 Service Integration

### Vector Service
```python
from database import SessionLocal
from services.vector_service import get_vector_service

db = SessionLocal()
vector_service = get_vector_service(db)

# Add embeddings
success, count, error = vector_service.add_document_embeddings(
    service_id=service_id,
    document_id=document_id,
    chunks=['chunk1', 'chunk2', 'chunk3']
)

# Search similar
results = vector_service.search_similar_documents(
    service_id=service_id,
    query='What are your hours?',
    limit=5
)

# Get status
status = vector_service.get_status()
```

---

## 📝 Session Management

**Pattern 1: Dependency Injection (Best)**
```python
@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user.to_dict() if user else None
    finally:
        db.close()
```

**Pattern 2: Context Manager**
```python
from contextlib import contextmanager

@contextmanager
def get_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

# Usage
with get_session() as db:
    user = db.query(User).filter(User.id == user_id).first()
```

---

## 🚀 Superadmin Credentials

```
Email: superadmin@marketmatic.com
Password: superadmin
```

Change password after first login!

---

## 🔧 Troubleshooting

### Connection Failed
```
Error: "could not connect to server"

✓ Check DATABASE_URL format
✓ Verify Supabase project is active
✓ Check network connectivity
✓ Verify IP whitelisting (if enabled)
```

### pgvector Not Available
```
Error: "relation 'document_embeddings' does not exist"

✓ Run: python supabase_setup.py
✓ Verify pgvector extension created
✓ Check column type is Vector(768)
```

### Session Issues
```
Error: "scoped session already begun"

✓ Always close session: db.close()
✓ Or use try/finally block
✓ Or use context manager
```

---

## 📊 Performance Tips

| Optimization | Impact | How |
|---|---|---|
| Connection pooling | ⚡⚡⚡ | SQLAlchemy default (enabled) |
| Indexes | ⚡⚡⚡ | Already created on: service_id, (session_id, timestamp) |
| Batch inserts | ⚡⚡ | Use `db.add_all()` for multiple records |
| Limit results | ⚡⚡ | Always use `.limit()` for searches |
| Lazy loading | ⚡ | Relationships auto-lazy (OK for REST) |

---

## 📚 Documentation Files

- **SUPABASE_MIGRATION_GUIDE.md** - Complete step-by-step setup
- **SUPABASE_MIGRATION_SUMMARY.md** - Technical architecture details
- **models/sqlalchemy_models.py** - All ORM model definitions
- **database.py** - Connection and session management
- **services/vector_service.py** - Vector database operations

---

## ✅ Pre-Launch Checklist

- [ ] Supabase project created
- [ ] DATABASE_URL set in .env
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Database initialized: `python supabase_setup.py`
- [ ] Superadmin account created
- [ ] Ollama running: `ollama serve`
- [ ] All route files updated to use SQLAlchemy
- [ ] Tests passing
- [ ] Frontend environment updated

---

## 🎯 Migration Timeline

- ✅ **Phase 1:** Foundation (COMPLETE)
  - ORM models created
  - Database layer ready
  - Vector service implemented

- ⏳ **Phase 2:** Route Updates (NEXT)
  - auth_routes.py
  - bot_routes.py
  - document_routes.py
  - rag_routes.py
  - chat_routes.py

- ⏳ **Phase 3:** Testing & Launch
  - Integration tests
  - End-to-end tests
  - Production deployment

---

## 🆘 Support

**Common Issues:**

1. **"No such table: users"**
   - Run: `python supabase_setup.py`

2. **"AI service unavailable"**
   - Check: `ollama serve` is running

3. **"Vector dimension mismatch"**
   - Verify: nomic-embed-text produces 768-dim vectors

4. **"Connection pool exhausted"**
   - Increase: `pool_size` in engine config
   - Or: reduce query complexity

---

**Status:** Foundation ✅ COMPLETE  
**Last Updated:** December 8, 2025  
**Ollama Version:** Latest (with llama3 + nomic-embed-text)  
**Database:** Supabase PostgreSQL + pgvector  

