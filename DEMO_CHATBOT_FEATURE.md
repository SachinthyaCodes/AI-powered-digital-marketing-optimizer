# Business-Specific Chatbot Demo Feature

## Overview
This feature allows SME admins to view and test their custom chatbot in a dedicated demo page. Each business gets a unique chatbot powered by SinLlama (Modal AI) that uses their specific FAQs, Products, and Policies.

## What Was Created

### Backend (Flask)
**File**: `backend/routes/chat_routes.py`

Added two new endpoints:

1. **POST `/api/chat/demo/message`**
   - Handles demo chatbot messages
   - Uses Modal AI (SinLlama) for responses
   - Fetches business-specific context (FAQs, Products, Policies)
   - No authentication required (demo purpose)
   - Marks messages with `is_demo: True` in database

2. **GET `/api/chat/business-info/<service_id>`**
   - Returns business information for demo page
   - Shows counts of FAQs, Products, Policies
   - Gets bot configuration if exists

### Frontend (React)

#### 1. New Page: `BusinessChatDemo.jsx`
- **Route**: `/demo/chat/:serviceId`
- **Features**:
  - Full-screen chat interface
  - Gradient header with bot information
  - Real-time messaging with SinLlama AI
  - Auto-scroll to latest message
  - Loading indicators (typing animation)
  - Back to dashboard button
  - Info card explaining chatbot features

#### 2. Updated: `Dashboard.jsx`
- Added prominent "View Chatbot Demo" button
- Button navigates to `/demo/chat/{service_id}`
- Styled with gradient (indigo to purple)
- Shows above feature grid

#### 3. Updated: `App.jsx`
- Added route: `/demo/chat/:serviceId` → `BusinessChatDemo`
- Protected with `ProtectedRoute` (requires login)

## How It Works

### For Admin Users:

1. **Login** to admin dashboard
2. **Click** "View Chatbot Demo" button
3. **Opens** dedicated demo page with chatbot
4. **Chat** with AI assistant that knows your business data
5. **See** responses powered by SinLlama Modal AI

### Behind the Scenes:

```
User sends message
    ↓
POST /api/chat/demo/message
    ↓
Backend fetches business context:
  - FAQs (up to 20)
  - Products (up to 30)
  - Policies (up to 10)
    ↓
Formats context as system prompt
    ↓
Calls Modal AI (SinLlama)
    ↓
Returns AI response
    ↓
Stores in MongoDB (marked as demo)
    ↓
Displays in chat interface
```

## Key Features

### 1. Business-Specific Knowledge
Each chatbot only knows about its own business:
- Service ID isolation in database queries
- Context built from service's FAQs, Products, Policies
- Unique bot name from configuration

### 2. Modal AI Integration
- Uses SinLlama model on Modal
- Supports English and Sinhala languages
- Temperature: 0.7 (balanced creativity)
- Max tokens: 300 (concise responses)

### 3. Professional Demo Experience
- Clean, modern UI with gradients
- Real-time typing indicators
- Message timestamps
- Error handling
- Smooth animations

### 4. Conversation History
- Session-based chat history
- Last 6 messages included in context
- Stored in MongoDB `chat_messages` collection

## Database Schema

### chat_messages Collection
```javascript
{
  _id: ObjectId,
  session_id: "demo_1234567890_abc123",
  service_id: "service_id_string",
  message: "What products do you sell?",
  sender: "user" | "bot",
  timestamp: ISODate,
  is_demo: true  // Marks demo messages
}
```

## API Endpoints

### Demo Chatbot
```
POST /api/chat/demo/message
Body: {
  "message": "Hello, what products do you have?",
  "service_id": "67489380778afa972e4f2158",
  "session_id": "demo_1234567890_abc123"
}
Response: {
  "response": "We have fresh vegetables, fruits...",
  "session_id": "demo_1234567890_abc123",
  "timestamp": "2025-11-29T11:30:00"
}
```

### Business Info
```
GET /api/chat/business-info/67489380778afa972e4f2158
Response: {
  "service_name": "FreshMart",
  "bot_name": "FreshBot",
  "faq_count": 5,
  "product_count": 12,
  "policy_count": 3,
  "has_bot_config": true
}
```

## System Prompt Example

```
You are FreshBot, a helpful AI assistant for this business.

Use the following business information to answer customer questions accurately:

=== Frequently Asked Questions ===
Q (en): What are your delivery hours?
A: We deliver from 9 AM to 8 PM daily

=== Available Products ===
Product: Fresh Tomatoes (Category: Vegetables)
Price: Rs. 200
Stock: 50 units
Description: Locally grown fresh tomatoes

=== Business Policies ===
Policy: Delivery Policy (shipping)
Free delivery on orders above Rs. 2000

Guidelines:
- Answer based on the business information provided above
- Be friendly, helpful, and professional
- If asked about products, mention names, prices, and availability
- Support both English and Sinhala (සිංහල) languages
- Keep responses concise and relevant
```

## Testing Instructions

### 1. Start Servers
```bash
# Backend
cd backend
python app.py

# Frontend
cd frontend
npm run dev
```

### 2. Test Flow
1. Navigate to `http://localhost:3000/login`
2. Login as admin (e.g., sanuda@gmail.com)
3. Click "View Chatbot Demo" button on dashboard
4. Ask questions:
   - "What products do you have?"
   - "What is your delivery policy?"
   - "මිල කීයද?" (Sinhala: What's the price?)

### 3. Verify
- ✓ Chatbot responds with business-specific information
- ✓ Answers include product names, prices, stock
- ✓ FAQ answers are accurate
- ✓ Policies are quoted correctly
- ✓ Supports English and Sinhala

## Advantages

1. **Zero Configuration**: Works immediately with existing business data
2. **Isolated**: Each service_id gets its own chatbot
3. **Multilingual**: Sinhala + English support via SinLlama
4. **Smart**: Uses Modal AI for natural language understanding
5. **Demo-Friendly**: No authentication barriers for testing
6. **Customizable**: Uses bot configuration if set by admin

## Future Enhancements

- [ ] Add chat export feature
- [ ] Voice input support
- [ ] Suggested questions based on FAQs
- [ ] Chat analytics dashboard
- [ ] Customer satisfaction ratings
- [ ] Public shareable demo link
- [ ] Embed code for websites

---

**Status**: ✅ Fully Implemented and Ready
**Technology**: React + Flask + MongoDB + Modal AI (SinLlama)
**Created**: November 29, 2025
