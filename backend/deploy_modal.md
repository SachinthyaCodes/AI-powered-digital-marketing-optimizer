# Quick Deploy Guide for Modal with SinLlama

## Prerequisites
✅ You have a Modal account at https://modal.com/
✅ Python 3.11 or 3.12 installed (not 3.13)

## Step 1: Setup Modal Authentication

```powershell
# Make sure you're in the backend directory
cd "d:\Research project\PP1 progress\marketmatic\backend"

# Activate your virtual environment (with Python 3.11 or 3.12)
.\venv\Scripts\Activate.ps1

# Install Modal if not already installed
pip install modal

# Authenticate with Modal (opens browser)
python -m modal setup
```

This will open your browser to authenticate. Once done, you're ready to deploy!

## Step 2: Test Modal Service Locally

```powershell
# Test embedding generation
modal run modal_rag_service.py --test-type embedding

# Test chat with SinLlama model
modal run modal_rag_service.py --test-type chat
```

Expected output:
- Embedding test: Shows 384-dimensional vector
- Chat test: Shows response from SinLlama model

## Step 3: Deploy to Modal

```powershell
modal deploy modal_rag_service.py
```

This will:
1. Build the container image with SinLlama model
2. Deploy two endpoints:
   - `embed` - for generating embeddings
   - `chat` - for chat completions with SinLlama
3. Display the endpoint URLs

**Example output:**
```
✓ Created objects.
├── 🔨 Created mount /d:/Research project/PP1 progress/marketmatic/backend/modal_rag_service.py
├── 🔨 Created function embed.
├── 🔨 Created function chat.
└── 🔨 Created class RAGService.

✓ App deployed! 🎉

View Deployment: https://modal.com/your-workspace/apps/marketmatic-rag

Web endpoints:
├── embed => https://your-workspace--marketmatic-rag-embed.modal.run
└── chat => https://your-workspace--marketmatic-rag-chat.modal.run
```

## Step 4: Update .env File

Copy the endpoint URLs and add them to your `.env` file:

```env
# Modal RAG Service Endpoints
MODAL_EMBEDDING_URL=https://your-workspace--marketmatic-rag-embed.modal.run
MODAL_CHAT_URL=https://your-workspace--marketmatic-rag-chat.modal.run
```

## Step 5: Test the Deployed Endpoints

### Test Embedding Endpoint:
```powershell
$body = @{
    text = "අපේ කඩේ විකුණන භාණ්ඩ මොනවාද?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "YOUR_EMBEDDING_URL" -Method Post -Body $body -ContentType "application/json"
```

### Test Chat Endpoint:
```powershell
$body = @{
    query = "අපේ කඩේ විකුණන භාණ්ඩ මොනවාද?"
    context = "අපේ කඩේ විකුණන භාණ්ඩ: ටී ෂර්ට් රු. 1500, ජීන්ස් රු. 3500, සපත්තු රු. 4500"
    language = "si"
} | ConvertTo-Json

Invoke-RestMethod -Uri "YOUR_CHAT_URL" -Method Post -Body $body -ContentType "application/json"
```

## Step 6: Start Your Flask Backend

```powershell
# Make sure .env is updated with Modal URLs
python app.py
```

## Test Full RAG Pipeline

```powershell
# 1. Test RAG status
curl http://localhost:5000/api/rag/status

# 2. Upload a document (requires admin login)
# First login and get token, then:
curl -X POST http://localhost:5000/api/rag/upload-document `
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" `
  -F "file=@sample_document.txt"

# 3. Chat with the bot (requires service token)
$chatBody = @{
    service_token = "YOUR_SERVICE_TOKEN"
    message = "මෙම ව්‍යාපාරය ගැන කියන්න"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/rag/chat" `
  -Method Post -Body $chatBody -ContentType "application/json"
```

## SinLlama Model Features

### What makes SinLlama special:
- **Native Sinhala Support**: Trained specifically for Sinhala language
- **Bilingual**: Handles both Sinhala and English seamlessly
- **Sri Lankan Context**: Better understanding of local business terms
- **LLaMA Architecture**: Based on Meta's powerful LLaMA model
- **Efficient**: Optimized for inference

### Example Queries:
```
English: "What products do you sell?"
Sinhala: "අපේ කඩේ විකුණන භාණ්ඩ මොනවාද?"
Mixed: "මේ products වල price එක කීයද?"
```

## Modal Pricing & Performance

### Free Tier:
- 30 credits per month
- Each credit = ~$1 worth of compute
- Enough for testing and light usage

### Performance:
- **Cold start**: 5-10 seconds (first request)
- **Warm inference**: <1 second per request
- **GPU**: T4 GPU automatically assigned
- **Concurrent requests**: Auto-scales

### Cost Estimate:
- T4 GPU: ~$0.30/hour
- Typical request: 1-2 seconds
- Cost per request: ~$0.0001 - $0.0002

## Troubleshooting

### "RuntimeError: This version of Modal does not support Python 3.13+"
**Solution**: Use Python 3.11 or 3.12 to create your virtual environment

### "Modal URLs not configured"
**Solution**: Make sure you deployed and copied the URLs to `.env`

### "Model download timeout"
**Solution**: First deployment takes longer (downloads model). Wait 2-3 minutes.

### "GPU out of memory"
**Solution**: SinLlama is optimized but if issues occur, Modal auto-restarts with fresh GPU

## Monitoring & Logs

View your deployments and logs:
```
https://modal.com/your-workspace/apps/marketmatic-rag
```

You can see:
- Request count
- Response times
- Error logs
- GPU usage
- Cost tracking

## Next Steps

1. ✅ Deploy Modal service with SinLlama
2. ✅ Update .env with endpoints
3. ✅ Test Flask backend
4. 🔄 Upload business documents
5. 🔄 Test chatbot conversations
6. 🔄 Build frontend UI
7. 🔄 Production deployment

## Remote Access (as per Modal docs)

Modal provides automatic remote access via HTTPS endpoints. No additional configuration needed!

Your deployed functions are accessible via:
- Direct Python SDK: `RAGService().generate_chat_response.remote(...)`
- HTTP REST API: `POST https://your-workspace--marketmatic-rag-chat.modal.run`
- Modal CLI: `modal run modal_rag_service.py`

All remote calls are authenticated with your Modal token automatically.
