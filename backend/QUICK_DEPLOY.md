# 🚀 Quick Start: Deploy SinLlama on Modal

## ⚡ 3-Minute Setup

### 1️⃣ Install & Authenticate
```powershell
cd "d:\Research project\PP1 progress\marketmatic\backend"
.\venv\Scripts\Activate.ps1
pip install modal
python -m modal setup
```
> Browser opens → Login to Modal → Done!

### 2️⃣ Deploy to Modal
```powershell
modal deploy modal_rag_service.py
```
> Wait 2-3 minutes for first deployment (downloads SinLlama model)

### 3️⃣ Copy URLs to .env
After deployment, you'll see:
```
Web endpoints:
├── embed => https://username--marketmatic-rag-embed.modal.run
└── chat => https://username--marketmatic-rag-chat.modal.run
```

Add to `.env`:
```env
MODAL_EMBEDDING_URL=https://username--marketmatic-rag-embed.modal.run
MODAL_CHAT_URL=https://username--marketmatic-rag-chat.modal.run
```

### 4️⃣ Test It
```powershell
python test_modal_service.py
```

### 5️⃣ Start Backend
```powershell
python app.py
```

---

## 🧪 Quick Tests

### Test Embedding (PowerShell):
```powershell
$body = @{ text = "Hello world" } | ConvertTo-Json
Invoke-RestMethod -Uri "YOUR_EMBEDDING_URL" -Method Post -Body $body -ContentType "application/json"
```

### Test Chat (PowerShell):
```powershell
$body = @{
    query = "අපේ කඩේ මොනවාද විකුණන්නේ?"
    context = "අපේ කඩේ ටී ෂර්ට්, ජීන්ස්, සපත්තු විකුණනවා"
    language = "si"
} | ConvertTo-Json

Invoke-RestMethod -Uri "YOUR_CHAT_URL" -Method Post -Body $body -ContentType "application/json"
```

---

## 🎯 What You Get

✅ **SinLlama Model**: Native Sinhala + English support  
✅ **GPU Acceleration**: T4 GPU auto-assigned  
✅ **Auto-Scaling**: Handles traffic spikes  
✅ **Remote Access**: HTTPS endpoints ready  
✅ **Free Tier**: 30 credits/month  

---

## 📊 Modal Commands Cheat Sheet

| Command | Purpose |
|---------|---------|
| `modal setup` | Authenticate with Modal |
| `modal deploy modal_rag_service.py` | Deploy to production |
| `modal run modal_rag_service.py --test-type chat` | Test locally |
| `modal app list` | List your apps |
| `modal app logs marketmatic-rag` | View logs |
| `modal app stop marketmatic-rag` | Stop the app |

---

## 🔍 Troubleshooting

### "Python 3.13 not supported"
Use Python 3.11 or 3.12:
```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### "Modal URLs not configured"
Make sure you:
1. Deployed: `modal deploy modal_rag_service.py`
2. Copied URLs to `.env` file
3. Restarted Flask: `python app.py`

### "First request is slow"
Cold start takes 5-10 seconds. Subsequent requests are <1 second.

---

## 📚 Learn More

- **Modal Dashboard**: https://modal.com/
- **Your Apps**: https://modal.com/apps
- **Documentation**: https://modal.com/docs
- **SinLlama Model**: https://huggingface.co/polyglots/SinLlama_v01

---

## 🎉 Success Checklist

- [ ] Modal authenticated (`python -m modal setup`)
- [ ] Service deployed (`modal deploy modal_rag_service.py`)
- [ ] URLs in `.env` file
- [ ] Tests pass (`python test_modal_service.py`)
- [ ] Flask backend running (`python app.py`)
- [ ] Can chat with bot

---

**Need Help?** Check `deploy_modal.md` for detailed guide or `MODAL_SETUP.md` for architecture details.
