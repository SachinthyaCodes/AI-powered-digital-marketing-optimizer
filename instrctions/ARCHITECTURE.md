# MarketMatic Bot Management - System Architecture

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  (React + Tailwind CSS + Lucide Icons + React Router)          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                           │
├─────────────────────────────────────────────────────────────────┤
│  📱 Pages:                                                       │
│    ├── Login.jsx                                                │
│    ├── Signup.jsx                                               │
│    ├── AdminDashboard.jsx                                       │
│    ├── BotManagement.jsx ⭐ (NEW)                               │
│    └── SMEHomePage.jsx                                          │
│                                                                  │
│  🔐 Context:                                                     │
│    └── AuthContext.jsx (JWT + User State)                       │
│                                                                  │
│  🛡️ Components:                                                 │
│    └── ProtectedRoute.jsx                                       │
│                                                                  │
│  🌐 Services:                                                    │
│    └── api.js (Axios + Interceptors)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ API Calls
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (Flask)                            │
├─────────────────────────────────────────────────────────────────┤
│  🚀 Routes:                                                      │
│    ├── auth_routes.py (Login, Signup, Password Reset)          │
│    ├── superadmin_routes.py (Service Management)               │
│    ├── service_routes.py (Service Info)                        │
│    └── bot_routes.py ⭐ (NEW - Bot Management)                  │
│                                                                  │
│  🔐 Auth:                                                        │
│    ├── jwt_handler.py (Token Generation/Validation)            │
│    └── decorators.py (@admin_required, @superadmin_required)   │
│                                                                  │
│  📦 Models:                                                      │
│    ├── user.py (User, Admin, SuperAdmin)                        │
│    ├── service.py (Service Registration)                        │
│    └── bot_models.py ⭐ (NEW - Bot Configuration)               │
│         ├── BotConfiguration                                    │
│         ├── FAQ                                                 │
│         ├── Product                                             │
│         └── Policy                                              │
│                                                                  │
│  🛠️ Utils:                                                       │
│    ├── email_service.py (SMTP Gmail)                           │
│    └── cloudinary_service.py ⭐ (NEW - Image Upload)            │
│                                                                  │
│  ⚙️ Config:                                                      │
│    ├── config.py (Environment Variables)                        │
│    ├── .env (Secrets)                                           │
│    └── database.py (MongoDB Connection)                         │
└─────────────────────────────────────────────────────────────────┘
                    │                    │
                    │                    │
                    ▼                    ▼
    ┌───────────────────────┐   ┌──────────────────┐
    │   MONGODB ATLAS       │   │   CLOUDINARY     │
    │   (Database)          │   │   (Image CDN)    │
    ├───────────────────────┤   ├──────────────────┤
    │  Collections:         │   │  Features:       │
    │  • users              │   │  • Image Storage │
    │  • services           │   │  • Auto Optimize │
    │  • bot_configurations │   │  • CDN Delivery  │
    │  • faqs ⭐            │   │  • Transforms    │
    │  • products ⭐        │   │  • 25GB Free     │
    │  • policies ⭐        │   └──────────────────┘
    └───────────────────────┘
```

## 🔄 Data Flow

### 1. Admin Login Flow
```
User → Login Page → API /api/auth/login → MongoDB (users)
                     ↓
                JWT Token → localStorage → All API Requests
```

### 2. Bot Configuration Flow
```
Admin → Bot Management → GET /api/bot/config
                          ↓
                    MongoDB (bot_configurations)
                          ↓
                    Return Config → Display Form
                          
Admin → Edit Form → PUT /api/bot/config
                     ↓
                MongoDB (Update) → Success Message
```

### 3. FAQ Management Flow
```
Admin → FAQs Tab → POST /api/bot/faqs
                    ↓
              { question, answer, language, category }
                    ↓
              MongoDB (faqs) → Success
                    ↓
              Refresh List → Display All FAQs
```

### 4. Product with Image Flow
```
Admin → Products Tab → Select Images → POST /api/bot/upload-image
                                         ↓
                                   Cloudinary Upload
                                         ↓
                                   Return URLs
                                         ↓
                    POST /api/bot/products (with image URLs)
                                         ↓
                                   MongoDB (products)
                                         ↓
                                   Display Product Card
```

### 5. Policy Management Flow
```
Admin → Policies Tab → Write Policy → POST /api/bot/policies
                                        ↓
                              { title, content, type }
                                        ↓
                              MongoDB (policies) → Success
```

## 🔐 Authentication Flow

```
┌────────────┐         ┌──────────────┐         ┌──────────────┐
│   Client   │         │    Backend   │         │   MongoDB    │
└────────────┘         └──────────────┘         └──────────────┘
      │                       │                       │
      │   POST /auth/login    │                       │
      │───────────────────────>                       │
      │   { email, password } │                       │
      │                       │   Query user          │
      │                       │──────────────────────>│
      │                       │                       │
      │                       │   User data           │
      │                       │<──────────────────────│
      │                       │                       │
      │                       │ Validate password     │
      │                       │ (bcrypt)              │
      │                       │                       │
      │                       │ Generate JWT          │
      │                       │ (jwt_handler)         │
      │                       │                       │
      │   JWT Token           │                       │
      │<───────────────────────                       │
      │                       │                       │
      │ Store in localStorage │                       │
      │                       │                       │
      │   API Request         │                       │
      │   + Bearer Token      │                       │
      │───────────────────────>                       │
      │                       │                       │
      │                       │ @admin_required       │
      │                       │ Verify JWT            │
      │                       │ Check role = admin    │
      │                       │                       │
      │                       │   Query service       │
      │                       │──────────────────────>│
      │                       │                       │
      │   Response Data       │                       │
      │<───────────────────────                       │
```

## 🖼️ Image Upload Flow

```
┌────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
│   Admin    │     │   Frontend   │     │   Backend    │     │Cloudinary│
└────────────┘     └──────────────┘     └──────────────┘     └──────────┘
      │                   │                     │                   │
      │ Select images     │                     │                   │
      │──────────────────>│                     │                   │
      │                   │                     │                   │
      │                   │ FormData (images)   │                   │
      │                   │────────────────────>│                   │
      │                   │                     │                   │
      │                   │                     │ Upload images     │
      │                   │                     │──────────────────>│
      │                   │                     │                   │
      │                   │                     │ Optimize          │
      │                   │                     │ (1000x1000 max)   │
      │                   │                     │                   │
      │                   │                     │ Image URLs        │
      │                   │                     │<──────────────────│
      │                   │                     │                   │
      │                   │   URLs              │                   │
      │                   │<────────────────────│                   │
      │                   │                     │                   │
      │ Image previews    │                     │                   │
      │<──────────────────│                     │                   │
      │                   │                     │                   │
      │ Save product      │                     │                   │
      │──────────────────>│                     │                   │
      │                   │                     │                   │
      │                   │ POST /bot/products  │                   │
      │                   │ { ...data, images } │                   │
      │                   │────────────────────>│                   │
      │                   │                     │                   │
      │                   │                     │ MongoDB           │
      │                   │                     │ (store URLs)      │
      │                   │                     │                   │
      │                   │   Success           │                   │
      │                   │<────────────────────│                   │
```

## 📂 File Structure

```
marketmatic/
├── backend/
│   ├── app.py                    # Flask app entry point
│   ├── config.py                 # Configuration
│   ├── database.py               # MongoDB connection
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Environment secrets
│   ├── auth/
│   │   ├── jwt_handler.py        # JWT operations
│   │   └── decorators.py         # Auth decorators
│   ├── models/
│   │   ├── user.py               # User models
│   │   ├── service.py            # Service models
│   │   └── bot_models.py ⭐      # Bot models (NEW)
│   ├── routes/
│   │   ├── auth_routes.py        # Auth endpoints
│   │   ├── service_routes.py     # Service endpoints
│   │   ├── superadmin_routes.py  # SuperAdmin endpoints
│   │   └── bot_routes.py ⭐      # Bot endpoints (NEW)
│   └── utils/
│       ├── email_service.py      # Email sending
│       └── cloudinary_service.py ⭐ # Image upload (NEW)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Main app component
│   │   ├── main.jsx              # Entry point
│   │   ├── index.css             # Global styles
│   │   ├── components/
│   │   │   └── ProtectedRoute.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── AdminDashboard.jsx
│   │   │   ├── BotManagement.jsx ⭐ (NEW)
│   │   │   └── ...
│   │   └── services/
│   │       └── api.js
│   └── package.json
│
├── QUICK_START.md ⭐              # Quick reference (NEW)
├── BOT_MANAGEMENT_README.md ⭐   # Feature docs (NEW)
├── CLOUDINARY_SETUP.md ⭐        # Setup guide (NEW)
└── IMPLEMENTATION_SUMMARY.md ⭐  # Complete summary (NEW)
```

## 🎯 Key Components

### Backend
- **Flask**: Web framework (v3.0.0)
- **PyMongo**: MongoDB driver (v4.6.0)
- **PyJWT**: Token authentication (v2.8.0)
- **Cloudinary**: Image hosting (v1.44.1)
- **Pillow**: Image processing (v12.0.0)

### Frontend
- **React**: UI library (v18)
- **Vite**: Build tool
- **Tailwind CSS**: Styling framework
- **Lucide React**: Icon library
- **Axios**: HTTP client

### Database
- **MongoDB Atlas**: Cloud database
- **Collections**: 6 collections (users, services, bot_configurations, faqs, products, policies)

### External Services
- **Cloudinary**: Image CDN (25GB free)
- **Gmail SMTP**: Email service (500/day free)

## 🔗 API Endpoints Summary

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | /api/bot/config | Get bot config | Admin |
| PUT | /api/bot/config | Update bot config | Admin |
| GET | /api/bot/faqs | List FAQs | Admin |
| POST | /api/bot/faqs | Add FAQ | Admin |
| PUT | /api/bot/faqs/:id | Update FAQ | Admin |
| DELETE | /api/bot/faqs/:id | Delete FAQ | Admin |
| GET | /api/bot/products | List products | Admin |
| POST | /api/bot/products | Add product | Admin |
| PUT | /api/bot/products/:id | Update product | Admin |
| DELETE | /api/bot/products/:id | Delete product | Admin |
| POST | /api/bot/products/:id/images | Upload product images | Admin |
| GET | /api/bot/policies | List policies | Admin |
| POST | /api/bot/policies | Add policy | Admin |
| PUT | /api/bot/policies/:id | Update policy | Admin |
| DELETE | /api/bot/policies/:id | Delete policy | Admin |
| POST | /api/bot/upload-image | Upload general image | Admin |

## ✨ Features Implemented

✅ Bot configuration management
✅ FAQ management (multilingual)
✅ Product catalog with images
✅ Policy management
✅ Cloudinary integration
✅ Admin authentication
✅ Responsive UI
✅ Real-time feedback
✅ Image optimization
✅ Multi-tenant support (service_id scoped)

## 🚀 Ready to Deploy!

All systems are implemented and tested. Just configure Cloudinary and start using! 🎉
