# 🚀 MarketMatic - Quick Start Guide

## ⚡ One Command to Start Everything

Simply double-click or run:

```bash
start.bat
```

That's it! This will:
1. ✅ Start the backend server on http://localhost:5000
2. ✅ Start the frontend server on http://localhost:5173
3. ✅ Open both in separate terminal windows so you can monitor them

## 🤖 NEW: Enhanced SinLlama AI (100% OFFLINE)

Your MarketMatic now features **ADVANCED AI** with:

### ✨ Smooth, Natural Responses
- **Advanced Prompt Engineering**: Professional yet friendly tone
- **Smart Language Detection**: Auto-switches between English, Sinhala, or Mixed
- **Response Polishing**: Removes repetition, fixes formatting automatically
- **Context-Aware**: Remembers conversation history for natural flow

### 🌐 100% OFFLINE Operation
- ✅ **NO Internet Required**: Works completely offline
- ✅ **Local Model**: SinLlama GGUF runs on your machine
- ✅ **Privacy First**: Your data never leaves your computer
- ✅ **Fast & Reliable**: No API calls, no rate limits

### 🎯 Optimized for Quality
- **Mirostat 2.0**: Better coherence and natural language
- **Anti-repetition**: Smart detection prevents repeated text
- **Temperature 0.75**: Perfect balance of creativity and accuracy
- **Bilingual Support**: සිංහල + English seamlessly mixed

## First Time Setup

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```

### 3. Environment Configuration
Make sure `backend/.env` file exists with your database configuration.

## That's All!

After setup, just use `start.bat` every time. No confusion, no multiple commands.

---

## Alternative: Manual Start

If you prefer to start services manually:

### Backend Only:
```bash
cd backend
python start_simple.py
```

### Frontend Only:
```bash
cd frontend
npm run dev
```

## 🧪 Testing the AI

Visit http://localhost:5173 and try these:

**English:**
- "What plans do you offer?"
- "How much is the Pro plan?"

**Sinhala:**
- "ඔයාට මොනවද plans තියෙන්නේ?"
- "Basic plan එකේ මිල කීයද?"

**Mixed:**
- "Pro plan එකේ features මොනවද?"

## Stopping the Application

Close the terminal windows or press `Ctrl+C` in each terminal.

## 📊 Check AI Status

Visit: http://localhost:5000/api/chat/sinllama/status

This shows offline status and all AI capabilities!
