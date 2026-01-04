# 🚀 MarketMatic - AI-Powered Digital Marketing Optimizer

> An intelligent chatbot platform for SMEs to enhance customer engagement with AI-powered conversations, smart document processing, and bilingual support (English & Sinhala).

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## 🎯 Overview

**MarketMatic** is a comprehensive AI chatbot platform designed specifically for Small and Medium Enterprises (SMEs). It enables businesses to create intelligent, customizable chatbots that can:

- 💬 Handle customer queries in **English and Sinhala**
- 🤖 Powered by **SinLlama** - A specialized bilingual AI model (8.1B parameters)
- 📚 Learn from uploaded documents (PDFs, DOCX, Excel)
- 🧠 Provide intelligent responses using **RAG (Retrieval Augmented Generation)**
- 🎨 Customize bot appearance and behavior
- 📊 Manage FAQs, products, and policies
- 🔒 Secure multi-user authentication system

> **⚠️ Note:** SinLlama model is currently under active development and optimization to improve response quality, speed, and accuracy for better user experience.

### Who is it for?

- **SME Owners** - Build smart chatbots for their websites
- **Admins** - Manage bot configurations and content
- **Customers** - Get instant, intelligent responses 24/7

---

## ✨ Features

### 🤖 Intelligent Chatbot
- **AI-Powered Responses** using **SinLlama** - specialized bilingual model (8.1B parameters, Q4_K quantization)
- **Native Sinhala Support** - Unlike standard models, SinLlama is trained for Sinhala language
- **RAG System** for context-aware answers from your documents
- **Bilingual Support** (English & Sinhala) with automatic language detection
- **Customizable Personality** - Set tone, greeting messages, and fallback responses
- **🔬 Under Active Development** - Continuous improvements for better accuracy and speed

### 📄 Document Processing
- Upload and process multiple file formats:
  - 📕 PDF documents
  - 📘 Word documents (.docx)
  - 📗 Excel spreadsheets (.xlsx)
- Automatic text extraction and indexing
- Vector embeddings for semantic search

### 🎨 Bot Customization
- Custom bot name and welcome messages
- Configurable response tone and style
- FAQ management system
- Product catalog integration
- Policy document storage

### 🔐 Security & Authentication
- JWT-based authentication
- Role-based access control (User/Admin/SuperAdmin)
- Password reset via email
- Secure API endpoints

### 📊 Dashboard & Management
- User-friendly admin dashboard
- Real-time bot configuration
- Document upload interface
- Chat history and analytics

---

## 🤖 About SinLlama Model

**SinLlama** is a specialized bilingual AI model designed specifically for English and Sinhala language support, making it ideal for Sri Lankan businesses.

### Key Specifications

| Feature | Details |
|---------|---------|
| **Base Model** | Llama 3.1 8B |
| **Total Parameters** | 8.1 Billion |
| **Quantization** | Q4_K Medium (4-bit) |
| **File Size** | 4.63 GB |
| **Languages** | English, Sinhala, Code-mixed |
| **Context Window** | 4096 tokens |
| **Deployment** | CPU-optimized (10 threads) |

### Current Performance Metrics

| Metric | Performance |
|--------|-------------|
| **Overall Accuracy** | 85% |
| **Pricing Information** | 95% |
| **Product Listing** | 90% |
| **Language Detection** | 90% |
| **Response Time** | 15.5s average |
| **Generation Speed** | 0.72 words/second |

### 🚧 Development Status

SinLlama is **actively under development** with the following improvement areas:

- ✅ **Completed:** Basic bilingual support (English + Sinhala)
- ✅ **Completed:** RAG integration with document processing
- ✅ **Completed:** Context-aware response generation
- 🔄 **In Progress:** Response speed optimization
- 🔄 **In Progress:** Accuracy improvements for complex queries
- 🔄 **In Progress:** Enhanced Sinhala language understanding
- 📋 **Planned:** GPU acceleration support
- 📋 **Planned:** Larger context window (8192 tokens)

### Why SinLlama?

- **🇱🇰 Native Sinhala Support** - Unlike standard models that struggle with Sinhala
- **💰 Zero Operational Cost** - Runs locally, no API fees
- **🔒 Complete Privacy** - Data never leaves your server
- **🎯 Specialized for SMEs** - Optimized for business use cases
- **🌐 Bilingual by Design** - Seamlessly handles English and Sinhala

> **Research Documentation:** Detailed metrics and evaluation reports are available in [`SINLLAMA_RESEARCH_METRICS.md`](backend/SINLLAMA_RESEARCH_METRICS.md)

---

## 🏗️ Architecture

![MarketMatic System Architecture](architecture%20diagram%201.png)

### Data Flow

1. **User Request** → Frontend sends query to backend
2. **Authentication** → JWT token validated
3. **Language Detection** → Automatically detect English or Sinhala
4. **RAG Processing**:
   - Query embedded using Ollama (nomic-embed-text)
   - Similar documents retrieved from FAISS vector store
   - Context passed to **SinLlama** model for bilingual processing
5. **AI Response** → SinLlama generates contextual response in appropriate language
6. **Display** → Chat interface shows response to user

> **Model Performance:** SinLlama achieves 85% overall accuracy with 95% accuracy on pricing queries. Active development ongoing for improvements.

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose | Version |
|------------|---------|---------|
| **React** | UI Framework | 18.2.0 |
| **Vite** | Build Tool | 5.0.8 |
| **Tailwind CSS** | Styling | 3.4.0 |
| **React Router** | Navigation | 6.21.0 |
| **Axios** | HTTP Client | 1.6.2 |
| **Lucide React** | Icons | 0.294.0 |

### Backend
| Technology | Purpose | Version |
|------------|---------|---------|
| **Flask** | Web Framework | 3.0.0 |
| **SQLAlchemy** | ORM | 2.0.44 |
| **PostgreSQL** | Database | (Supabase) |
| **PyJWT** | Authentication | 2.8.0 |
| **Bcrypt** | Password Hashing | 4.1.2 |

### AI & ML
| Technology | Purpose | Version |
|------------|---------|---------|
| **SinLlama** | Bilingual Chat Model (Primary) | 8.1B-Q4_K |
| **Ollama** | LLM Runtime & Embeddings | Latest |
| **Llama 3.1 8B** | Base Architecture for SinLlama | - |
| **nomic-embed-text** | Text Embeddings | - |
| **FAISS** | Vector Search | 1.7.4+ |
| **Sentence Transformers** | Text Processing | 2.2.0+ |
| **LangDetect** | Language Detection | 1.0.9 |

> **SinLlama Model Status:** 🚧 **In Development** - Currently achieving 85% accuracy with ongoing optimizations for improved performance.

### Document Processing
| Technology | Purpose | Version |
|------------|---------|---------|
| **PyPDF** | PDF Extraction | 3.17.4 |
| **python-docx** | Word Documents | 1.1.0 |
| **openpyxl** | Excel Files | 3.1.2 |
| **Pandas** | Data Processing | 2.2.0+ |

### Infrastructure
| Service | Purpose |
|---------|---------|
| **Supabase** | PostgreSQL Database + Auth |
| **Cloudinary** | Image Storage & CDN |
| **Ollama** | Local LLM Server |
| **SinLlama (GGUF)** | Bilingual AI Model (English + Sinhala) |

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

### Required
- **Python** 3.9 or higher ([Download](https://www.python.org/downloads/))
- **Node.js** 18+ and npm ([Download](https://nodejs.org/))
- **Ollama** for AI models ([Download](https://ollama.ai/))
- **Git** for version control ([Download](https://git-scm.com/))

### Accounts Needed
- **Supabase Account** (Free tier) - [Sign up](https://supabase.com/)
- **Cloudinary Account** (Free tier) - [Sign up](https://cloudinary.com/)
- **Gmail Account** (for email service)

### System Requirements
- **RAM**: 8GB minimum (16GB recommended for Ollama)
- **Disk Space**: 10GB minimum
- **OS**: Windows 10/11, macOS, or Linux

---

## 🚀 Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/SachinthyaCodes/AI-powered-digital-marketing-optimizer.git
cd AI-powered-digital-marketing-optimizer
```

### 2️⃣ Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (see Configuration section)
# Copy and edit the configuration
cp .env.example .env

# Run database migrations (if needed)
python migrate_add_response_config.py

# Start the backend server
python start_simple.py
```

Backend will run on: **http://localhost:5000**

### 3️⃣ Setup Frontend

Open a **new terminal** window:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file
# Add: VITE_API_URL=http://localhost:5000

# Start development server
npm run dev
```

Frontend will run on: **http://localhost:5173**

### 4️⃣ Setup Ollama & SinLlama

```bash
# Install Ollama from https://ollama.ai/

# Pull required models
ollama pull nomic-embed-text  # For embeddings

# Download SinLlama model (bilingual English-Sinhala)
# Place sinllama-q4_k_m.gguf in backend/models/ directory
# Model size: ~4.6 GB
# Download link: [Contact team for model access]

# Verify Ollama installation
ollama list
```

> **Note:** SinLlama is a specialized model for Sinhala language support. The model is currently being optimized for better performance.

### 5️⃣ Access the Application

1. Open browser and navigate to **http://localhost:5173**
2. Create an account (first user becomes admin)
3. Start configuring your chatbot!

---

## ⚙️ Configuration

### Backend Configuration (.env)

Create a `.env` file in the `backend/` directory:

```env
# Database Configuration
DATABASE_URL=your_supabase_database_url
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SECRET_KEY=your_supabase_secret_key

# JWT Secret (generate a random string)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Email Configuration (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Frontend URL
FRONTEND_URL=http://localhost:5173

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# SinLlama Model Configuration (Bilingual English-Sinhala)
SINLLAMA_MODEL_PATH=./models/sinllama-q4_k_m.gguf
SINLLAMA_CONTEXT_LENGTH=4096
SINLLAMA_CPU_THREADS=10
```

### Frontend Configuration (.env)

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_URL=http://localhost:5000
```

### Getting API Keys

#### Supabase Setup
1. Go to [supabase.com](https://supabase.com/) and create a project
2. Go to **Settings** → **API**
3. Copy the **Project URL** and **anon/public key**
4. Go to **Settings** → **Database** and copy the connection string

#### Cloudinary Setup
1. Sign up at [cloudinary.com](https://cloudinary.com/)
2. Go to **Dashboard**
3. Copy **Cloud Name**, **API Key**, and **API Secret**

#### Gmail App Password
1. Enable 2-Factor Authentication on your Gmail
2. Go to **Google Account** → **Security** → **App Passwords**
3. Generate a new app password for "Mail"
4. Use this password in `MAIL_PASSWORD`

---

## 📁 Project Structure

```
AI-powered-digital-marketing-optimizer/
│
├── 📁 backend/                          # Backend Application
│   ├── 📄 app.py                        # Main Flask app
│   ├── 📄 config.py                     # Configuration
│   ├── 📄 database.py                   # Database setup
│   ├── 📄 requirements.txt              # Python dependencies
│   ├── 📄 start_simple.py               # Server starter
│   │
│   ├── 📁 auth/                         # Authentication
│   │   ├── jwt_handler.py               # JWT token management
│   │   └── decorators.py                # Auth decorators
│   │
│   ├── 📁 models/                       # Database Models
│   │   └── sqlalchemy_models.py         # User, Bot, FAQ, etc.
│   │
│   ├── 📁 routes/                       # API Endpoints
│   │   ├── auth_routes.py               # Login, signup, password reset
│   │   ├── bot_routes.py                # Bot management
│   │   ├── chat_routes.py               # Chat endpoints
│   │   ├── document_routes.py           # Document upload
│   │   └── rag_routes.py                # RAG system
│   │
│   ├── 📁 services/                     # Business Logic
│   │   ├── ollama_service.py            # Ollama integration
│   │   ├── rag_service.py               # RAG system
│   │   ├── document_service.py          # Document processing
│   │   └── embedding_service.py         # Text embeddings
│   │
│   ├── 📁 utils/                        # Utilities
│   │   ├── email_service.py             # Email sending
│   │   ├── cloudinary_service.py        # Image upload
│   │   └── document_parser.py           # File parsing
│   │
│   └── 📁 data/                         # Data Storage
│       ├── chromadb/                    # ChromaDB files (deprecated)
│       └── rag_indices/                 # FAISS indices
│
├── 📁 frontend/                         # Frontend Application
│   ├── 📁 src/
│   │   ├── 📁 pages/                    # React Pages
│   │   │   ├── Login.jsx
│   │   │   ├── Signup.jsx
│   │   │   ├── AdminDashboard.jsx
│   │   │   ├── BotManagement.jsx
│   │   │   └── BusinessChatDemo.jsx
│   │   │
│   │   ├── 📁 components/               # Reusable Components
│   │   │   ├── ChatWidget.jsx
│   │   │   ├── ProtectedRoute.jsx
│   │   │   └── DocumentUploader.jsx
│   │   │
│   │   ├── 📁 context/                  # React Context
│   │   │   └── AuthContext.jsx
│   │   │
│   │   ├── 📁 services/                 # API Services
│   │   │   └── api.js
│   │   │
│   │   ├── App.jsx                      # Main App Component
│   │   └── main.jsx                     # Entry Point
│   │
│   ├── 📄 package.json                  # Node dependencies
│   ├── 📄 vite.config.js                # Vite configuration
│   └── 📄 tailwind.config.js            # Tailwind CSS config
│
├── 📁 instrctions/                      # Documentation Archive
│   ├── ARCHITECTURE.md
│   ├── RAG_SYSTEM_GUIDE.md
│   ├── SETUP_COMPLETE_README.md
│   └── ... (other docs)
│
└── 📄 README.md                         # This file
```

---

## 📚 API Documentation

### Authentication Endpoints

#### POST /api/auth/signup
Register a new user

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "name": "John Doe",
  "role": "user"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "token": "jwt.token.here"
}
```

#### POST /api/auth/login
Login user

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "token": "jwt.token.here",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user"
  }
}
```

### Bot Management Endpoints

#### GET /api/bot/config
Get bot configuration (requires authentication)

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "bot_name": "My Assistant",
  "welcome_message": "Hello! How can I help?",
  "response_tone": "friendly",
  "fallback_message": "I'm not sure about that..."
}
```

#### PUT /api/bot/config
Update bot configuration

**Request Body:**
```json
{
  "bot_name": "Updated Bot Name",
  "welcome_message": "New welcome message",
  "response_tone": "professional"
}
```

### Chat Endpoints

#### POST /api/chat/message
Send a message to the chatbot

**Request Body:**
```json
{
  "message": "What are your business hours?",
  "bot_id": "bot-uuid",
  "language": "en"
}
```

**Response:**
```json
{
  "response": "Our business hours are 9 AM to 5 PM, Monday to Friday.",
  "language": "en",
  "sources": ["document1.pdf", "faq.docx"]
}
```

### Document Endpoints

#### POST /api/documents/upload
Upload documents for RAG

**Request:** Multipart form data
- `file`: Document file (PDF/DOCX/XLSX)
- `bot_id`: Bot UUID

**Response:**
```json
{
  "message": "Document uploaded successfully",
  "filename": "document.pdf",
  "indexed": true
}
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. **Ollama Connection Error**

**Problem:** `Connection refused to localhost:11434`

**Solution:**
```bash
# Check if Ollama is running
ollama list

# If not running, start Ollama service
# On Windows: Start from Start Menu
# On macOS/Linux:
ollama serve
```

#### 2. **Database Connection Error**

**Problem:** `Could not connect to Supabase`

**Solution:**
- Verify your `DATABASE_URL` in `.env` is correct
- Check Supabase project is active
- Ensure you're using the correct connection string

#### 3. **Module Not Found Error**

**Problem:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate

# Then reinstall
pip install -r requirements.txt
```

#### 4. **Port Already in Use**

**Problem:** `Address already in use: 5000`

**Solution:**
```bash
# Find and kill process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:5000 | xargs kill -9
```

#### 5. **CORS Error**

**Problem:** `CORS policy blocked`

**Solution:**
- Verify `FRONTEND_URL` in backend `.env` matches your frontend URL
- Check Flask-CORS is installed: `pip install flask-cors`

### Getting Help

- 📖 Check the [documentation](./instrctions/) folder
- 🐛 [Open an issue](https://github.com/SachinthyaCodes/AI-powered-digital-marketing-optimizer/issues)
- 💬 Contact the development team

---

## 🧪 Running Tests

### Backend Tests

```bash
cd backend

# Test database connection
python test_db_connection.py

# Test RAG system
python test_rag_integration.py

# Test response configuration
python test_response_config.py
```

### Frontend Tests

```bash
cd frontend

# Run linting
npm run lint

# Build for production (tests build process)
npm run build
```

---

## 🚢 Deployment

### Production Build

#### Backend
```bash
cd backend

# Install production dependencies
pip install -r requirements.txt

# Set environment to production
export FLASK_ENV=production

# Use Gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Frontend
```bash
cd frontend

# Build for production
npm run build

# The dist/ folder contains production files
# Deploy to Vercel, Netlify, or any static hosting
```

### Recommended Hosting

- **Backend**: Railway, Render, or AWS EC2
- **Frontend**: Vercel, Netlify, or AWS S3 + CloudFront
- **Database**: Supabase (already cloud-hosted)

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow existing code style
- Write clear commit messages
- Add comments for complex logic
- Test your changes thoroughly
- Update documentation as needed

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

Developed with ❤️ by the MarketMatic Team

- **Project Lead**: Sachinthya
- **Repository**: [AI-powered-digital-marketing-optimizer](https://github.com/SachinthyaCodes/AI-powered-digital-marketing-optimizer)

---

## 🙏 Acknowledgments

- **Ollama** for local LLM capabilities
- **Supabase** for database infrastructure
- **Cloudinary** for image hosting
- **React & Flask** communities

---

## 📞 Support

Need help? Reach out to us:

- 📧 Email: support@marketmatic.com
- 🐛 Issues: [GitHub Issues](https://github.com/SachinthyaCodes/AI-powered-digital-marketing-optimizer/issues)
- 📚 Documentation: [/instrctions](./instrctions/)

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ for SMEs worldwide

</div>
