# 🚀 Fresh Start Guide - Ollama-Only System

## ✅ System Status

**Backend**: Running on http://localhost:5000  
**Database**: Completely reset (MongoDB + ChromaDB)  
**AI Service**: Ollama (llama3:latest + nomic-embed-text:latest)  
**Superadmin**: Created

---

## 🔑 Login Credentials

```
Email: superadmin@marketmatic.com
Password: superadmin
```

---

## 📝 Testing Steps

### 1️⃣ Start Frontend (if not running)
```bash
cd frontend
npm run dev
```
Frontend: http://localhost:3001

### 2️⃣ Login as Superadmin
- Navigate to: http://localhost:3001/login
- Use credentials above
- Should redirect to dashboard

### 3️⃣ Create Test Business Account
**Option A**: Register as new user
- Go to: http://localhost:3001/signup
- Email: `test@business.com`
- Password: `password123`
- Complete registration

**Option B**: Use superadmin to create service

### 4️⃣ Configure Bot Settings
- Navigate to Bot Management
- Configure:
  - ✅ Bot name
  - ✅ Welcome message
  - ✅ Business description
  - ✅ Operating hours
  - ✅ Contact info

### 5️⃣ Upload Test Document
**Test FAQ Document Content**:
```
Q: What are your business hours?
A: We are open Monday to Friday, 9 AM to 6 PM.

Q: How can I contact support?
A: You can email us at support@business.com or call +94 77 123 4567.

Q: Do you accept online payments?
A: Yes, we accept credit cards, debit cards, and digital wallets.

Q: Loss ekak unoth monawada karanne?
A: Kripaakaral amathanna +94 77 123 4567 anuva, api obata wedipurama udhau karanawa.
```

**Upload Steps**:
1. Save above content as `test_faq.txt`
2. Go to "Upload Documents" or "Document Management"
3. Upload the file
4. Wait for: `✅ Added X chunks to vector DB using Ollama`
5. **No duplicate warnings** should appear (clean database)

### 6️⃣ Test Demo Chatbot
- Navigate to: "Demo Chatbot" button in Admin Dashboard
- Or go to: http://localhost:3001/demo-chat/:service_id

**Test Queries**:
```
1. "What are your business hours?"
   Expected: Response about Monday-Friday 9-6

2. "Loss ekak unoth monawada karanne?"
   Expected: Sinhala response with contact info

3. "Do you accept online payments?"
   Expected: Info about payment methods
```

---

## 🔍 What to Look For

### ✅ Success Indicators
- **Backend logs**:
  ```
  🦙 Activating Ollama Llama3 for query: ...
  ✅ Ollama chat response generated successfully
  ```
- **Response time**: 2-5 seconds typical (180s timeout as backup)
- **No warnings**: No ChromaDB duplicate embedding IDs
- **No Modal**: No Modal-related errors/messages
- **Bilingual**: Works with both English and Sinhala

### ❌ Issues to Report
- Timeout errors (even with 180s timeout)
- Duplicate embedding warnings
- Any Modal service references
- Slow responses (>10 seconds consistently)
- Sinhala not working properly

---

## 🛠️ Troubleshooting

### Issue: "AI service unavailable"
```bash
# Check Ollama status
ollama list

# Should show:
# llama3:latest      4.7 GB
# nomic-embed-text   274 MB

# If not running:
ollama serve
```

### Issue: Timeout Errors
**Current timeout**: 180 seconds (3 minutes)

If still timing out:
1. Check Ollama is running: `ollama ps`
2. Check system resources (CPU/RAM)
3. Try simpler query first
4. Check backend logs for actual error

### Issue: ChromaDB Warnings
**If you see "Add of existing embedding ID"**:
```bash
cd backend
python auto_reset.py
python create_superadmin.py
```
Then re-upload documents.

### Issue: Backend Not Running
```bash
cd backend
python app.py

# Should show:
# Starting MarketMatic Backend Server...
# Database: marketmatic_service
# Running on http://127.0.0.1:5000
```

---

## 🎯 Expected Performance

| Operation | Expected Time |
|-----------|---------------|
| Simple query (English) | 2-5 seconds |
| Complex query (context-heavy) | 5-15 seconds |
| Sinhala query | 3-8 seconds |
| Document embedding (per chunk) | 1-2 seconds |
| Full document (20 chunks) | 20-40 seconds |

**Maximum timeout**: 180 seconds (very complex queries only)

---

## 📊 System Architecture

```
Frontend (React) → Backend (Flask) → Ollama (Local)
                                   ↓
                             ChromaDB (Local)
                                   ↓
                             MongoDB (Cloud/Local)
```

**No Modal Service**: Completely removed from codebase

---

## 🔐 Important Notes

1. **Database is clean**: No old embeddings or documents
2. **Timeout increased**: 60s → 180s (3 minutes)
3. **Context window**: 2048 tokens
4. **Ollama only**: No fallback services
5. **Fail-fast**: Returns 503 if Ollama unavailable

---

## 📞 Quick Commands

```bash
# Backend
cd backend
python app.py

# Frontend  
cd frontend
npm run dev

# Reset everything
cd backend
python auto_reset.py
python create_superadmin.py

# Check Ollama
ollama list
ollama ps
ollama serve

# Test Ollama directly
curl http://localhost:11434/api/generate -d '{"model": "llama3", "prompt": "Hello"}'
```

---

## ✨ Success Criteria

- ✅ Login works
- ✅ Can upload documents without duplicate warnings
- ✅ Chatbot responds in 2-5 seconds
- ✅ Both English and Sinhala work
- ✅ No Modal-related errors
- ✅ No timeout errors (unless extreme edge case)
- ✅ Accurate responses based on uploaded documents

---

**Last Updated**: December 2, 2025  
**Ollama Version**: Latest  
**Models**: llama3:latest (4.7GB), nomic-embed-text:latest (274MB)  
**System**: Completely Modal-free, Ollama-exclusive architecture
