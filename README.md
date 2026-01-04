# 🚀 AI-Powered Digital Marketing Optimizer

> A comprehensive intelligent platform designed to help Sri Lankan Small and Medium Enterprises (SMEs) enhance their digital marketing performance through AI, Machine Learning, and Natural Language Processing.

![System Architecture](https://img.shields.io/badge/AI-Powered-blueviolet) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![React](https://img.shields.io/badge/React-19-61DAFB) ![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange) ![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Key Features](#-key-features)
- [Project Modules](#-project-modules)
- [Technology Stack](#-technology-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Running the Application](#-running-the-application)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Branch Information](#-branch-information)
- [Dependencies](#-dependencies)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

The **AI-Powered Digital Marketing Optimizer** is a complete ecosystem of intelligent tools designed specifically for Sri Lankan SMEs to revolutionize their digital marketing strategies. The platform combines cutting-edge AI technologies to provide:

- **Campaign Performance Prediction** - Forecast engagement metrics before posting
- **Intelligent Chatbot Assistant (MarketMatic)** - AI-powered customer engagement with bilingual support
- **Personalized Marketing Strategy Recommendations** - Custom strategies based on business goals
- **Real-time Analytics** - Data-driven insights for marketing optimization

### 🎓 Who Is This For?

- **SME Owners** - Optimize marketing campaigns and customer engagement
- **Marketing Teams** - Get AI-powered insights and predictions
- **Business Analysts** - Access comprehensive analytics dashboards
- **Customers** - Receive instant, intelligent responses through chatbots

---

## 🏗️ System Architecture

The complete system consists of four integrated layers working together to provide comprehensive marketing optimization:

### Architecture Components

#### 1️⃣ **SME Inputs Layer**
- Business goals and objectives
- Ad content (images & captions)
- Customer queries and interactions
- SME profile data

#### 2️⃣ **AI-Powered Core Engine**
- **Intelligent Content Generator** (Sinhala & English)
  - Text generation for campaigns
  - Content optimization
  - Multi-language support

- **Customer Engagement Chatbot** (Sinhala & English)
  - MarketMatic AI assistant
  - RAG-based responses
  - Bilingual conversation handling

- **Campaign Performance Predictor**
  - Transformer-based deep learning
  - Engagement metrics forecasting
  - Feature importance analysis

- **Personalized Strategy Recommender**
  - Business goal alignment
  - Platform-specific strategies
  - Actionable recommendations

#### 3️⃣ **Platform Outputs**
- ✅ Generated marketing content
- ⚡ Automated customer responses
- 📊 Predicted campaign metrics
- 💡 SME-specific recommendations

#### 4️⃣ **User Interface**
- **SME Mobile App** (Sinhala & English)
  - Campaign management
  - Chatbot integration
  - Performance dashboard

- **Analytics Dashboard**
  - Visual reports
  - Performance tracking
  - Historical analysis

### Data Flow

```
User Input → Frontend → Backend API → AI Processing → Database → Response → UI Display
     ↓
  [Image OCR, Text Analysis, RAG Processing]
     ↓
  [Transformer Prediction, SinLlama Chatbot, Recommendation Engine]
     ↓
  [Supabase (PostgreSQL) Storage & Retrieval]
```

---

## ✨ Key Features

### 🎯 Campaign Performance Prediction
- **AI-Powered Forecasting**: Predict likes, comments, shares, clicks, and quality scores
- **Transformer Model**: State-of-the-art deep learning architecture
- **OCR Integration**: Extract text from marketing images (Sinhala & English)
- **Explainable AI**: Feature importance analysis with actionable insights
- **Smart Recommendations**: Get suggestions to improve engagement
- **Hashtag Generation**: AI-powered hashtag recommendations
- **Timing Optimization**: Optimal posting time insights
- **Prediction History**: Track and compare past predictions

### 🤖 MarketMatic Smart Assistant
- **Bilingual Chatbot**: Native Sinhala and English support
- **SinLlama AI Model**: Specialized 8.1B parameter model for Sri Lankan context
- **RAG System**: Context-aware responses from uploaded documents
- **Document Processing**: Support for PDF, DOCX, Excel files
- **Customizable Personality**: Configure bot tone and behavior
- **FAQ Management**: Structured question-answer database
- **Product Catalog**: Integrated product information system
- **Multi-user Support**: Role-based access control

### 📈 Personalized Marketing Strategies
- **Goal-Based Recommendations**: Aligned with business objectives
- **Platform Optimization**: Facebook, Instagram, Twitter-specific strategies
- **Audience Analysis**: Target demographic insights
- **Content Strategy**: Personalized content planning
- **Budget Optimization**: Cost-effective campaign planning

### 📊 Analytics & Insights
- **Real-time Dashboards**: Visual performance metrics
- **Historical Trends**: Track performance over time
- **Comparative Analysis**: Benchmark against industry standards
- **Export Reports**: Generate detailed PDF/Excel reports

---

## 📦 Project Modules

The platform is organized into specialized modules, each developed in separate branches:

### 1. Campaign Performance Prediction Module
**Branch:** `feature/Campaign-Performance-Prediction`

**Core Functionality:**
- Transformer-based deep learning model for engagement prediction
- Multi-input processing (text + numerical features)
- OCR text extraction (EasyOCR + Gemini API fallback)
- Gradient-based explainability
- Supabase (PostgreSQL) integration for history tracking

**Technologies:**
- TensorFlow/Keras, EasyOCR, Google Generative AI
- Flask backend, React frontend
- Supabase (PostgreSQL)

### 2. MarketMatic Smart Assistant Module
**Branch:** `feature/MarketMatic-Smart-Assistant`

**Core Functionality:**
- SinLlama 8.1B parameter AI model
- RAG (Retrieval Augmented Generation) system
- Document processing pipeline
- Bilingual conversation handling
- Vector database (FAISS) for semantic search

**Technologies:**
- Ollama (SinLlama model), LangChain, FAISS
- FastAPI backend, React frontend
- Supabase (PostgreSQL)

### 3. Personalized Marketing Strategy Recommender
**Branch:** `feature/personalized-marketing-strategy-recommender`

**Core Functionality:**
- Business goal analysis
- Platform-specific strategy generation
- Audience segmentation
- Content strategy recommendations

**Technologies:**
- Machine Learning recommendation engine
- NLP for strategy generation
- React-based recommendation interface

### 4. Development Branch
**Branch:** `dev`

**Purpose:**
- Integration testing
- Feature merging and compatibility checks
- Quality assurance

---

## 🛠️ Technology Stack

### Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | Flask / FastAPI | 3.0 / 0.109+ | RESTful API development |
| **Deep Learning** | TensorFlow | 2.15+ | Transformer model training |
| **AI Model** | SinLlama (Ollama) | 8.1B params | Bilingual chatbot |
| **OCR** | EasyOCR | Latest | Text extraction from images |
| **AI Integration** | Google Generative AI | Latest | Gemini API for text extraction |
| **RAG Framework** | LangChain | Latest | Document processing & retrieval |
| **Vector DB** | FAISS | Latest | Semantic search |
| **Database** | Supabase (PostgreSQL) | 15+ | Data persistence |
| **Auth** | JWT | Latest | Authentication & authorization |
| **Data Processing** | Pandas, NumPy | Latest | Data manipulation |
| **ML Libraries** | scikit-learn | 1.3+ | Preprocessing & metrics |

### Frontend Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | React | 19 | UI development |
| **HTTP Client** | Axios | Latest | API communication |
| **Styling** | CSS3 | - | Custom responsive design |
| **State Management** | React Hooks | Built-in | Component state |
| **Routing** | React Router | Latest | Navigation |
| **Charts** | Chart.js / Recharts | Latest | Data visualization |

### DevOps & Tools

| Tool | Purpose |
|------|---------|
| **Git** | Version control |
| **Docker** | Containerization (optional) |
| **Postman** | API testing |
| **VS Code** | Development IDE |

---

## 📋 Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 8GB (16GB recommended for SinLlama)
- **Storage**: 10GB free space
- **Internet**: Stable connection for API calls and Supabase

### Software Requirements

1. **Python** 3.8 or higher
   ```bash
   python --version
   ```

2. **Node.js** 14 or higher & npm
   ```bash
   node --version
   npm --version
   ```

3. **Git** for version control
   ```bash
   git --version
   ```

4. **Supabase Account** (Free tier available)
   - Sign up at [Supabase](https://supabase.com)
   - Create a new project
   - Get connection string and API keys

5. **Google Gemini API Key** (Optional, for image OCR)
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Generate API key

6. **Ollama** (For MarketMatic chatbot)
   - Download from [Ollama.ai](https://ollama.ai/)
   - Install SinLlama model:
     ```bash
     ollama pull sinllama
     ```

---

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/SachinthyaCodes/AI-powered-digital-marketing-optimizer.git
cd AI-powered-digital-marketing-optimizer
```

### Step 2: Choose Your Module

The project has multiple feature branches. Choose the module you want to work with:

#### Option A: Campaign Performance Prediction

```bash
git checkout feature/Campaign-Performance-Prediction
```

#### Option B: MarketMatic Smart Assistant

```bash
git checkout feature/MarketMatic-Smart-Assistant
```

#### Option C: Personalized Strategy Recommender

```bash
git checkout feature/personalized-marketing-strategy-recommender
```

### Step 3: Backend Setup

#### For Campaign Performance Prediction & Strategy Recommender:

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### For MarketMatic Smart Assistant:

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Ensure Ollama is running
ollama serve

# Pull SinLlama model (if not already done)
ollama pull sinllama
```

### Step 4: Environment Configuration

Create a `.env` file in the backend directory:

**For Campaign Performance Prediction:**

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_DB_URL=postgresql://postgres.xxxxx:password@db.xxxxx.supabase.co:5432/postgres

# Google Gemini API (Optional - for OCR fallback)
GEMINI_API_KEY=your-gemini-api-key-here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

**For MarketMatic Smart Assistant:**

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_DB_URL=postgresql://postgres.xxxxx:password@db.xxxxx.supabase.co:5432/postgres

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=sinllama

# Email Configuration (for password reset)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 5: Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Configure proxy (if needed)
# The package.json already includes proxy configuration
```

### Step 6: Verify Model Files

**For Campaign Performance Prediction:**

Ensure these files exist in `backend/SavedModels/`:
- `Transformer.keras`
- `tokenizer.json`
- `y_scaler.pkl`

If missing, you need to train the model first using the provided notebooks.

**For MarketMatic:**

Ensure Ollama is running and SinLlama model is downloaded:

```bash
ollama list  # Should show sinllama
```

---

## 🎮 Running the Application

### Automated Setup (Windows)

**Campaign Performance Prediction Module:**

```bash
# First time setup
setup.bat

# Start backend
start-backend.bat

# Start frontend (in new terminal)
start-frontend.bat
```

### Manual Startup

#### Start Backend

**For Campaign Performance Prediction:**

```bash
cd backend
# Activate virtual environment
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # macOS/Linux

# Run Flask server
python app.py
```

Backend will be available at: `http://localhost:5000`

**For MarketMatic Smart Assistant:**

```bash
# Ensure Ollama is running first
ollama serve

# In another terminal
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run FastAPI server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

#### Start Frontend

```bash
cd frontend
npm start
```

Frontend will be available at: `http://localhost:3000`

### Health Check

**Campaign Performance Prediction:**
```bash
curl http://localhost:5000/health
```

**MarketMatic:**
```bash
curl http://localhost:8000/health
```

---

## 🌿 Branch Information

### Main Branches

| Branch | Purpose | Status | Key Features |
|--------|---------|--------|--------------|
| `main` | Production-ready code | ✅ Stable | Integrated & tested features |
| `dev` | Development integration | 🔄 Active | Feature testing & QA |

### Feature Branches

#### 1. `feature/Campaign-Performance-Prediction`

**Description:** Complete ML-powered campaign performance prediction system

**Features:**
- Transformer deep learning model
- OCR text extraction (Sinhala + English)
- Explainable AI with feature importance
- Smart hashtag generation
- Optimal timing recommendations
- Supabase (PostgreSQL) history tracking

**Tech Stack:**
- Flask, TensorFlow, EasyOCR, React
- Supabase (PostgreSQL), Google Gemini API

**Status:** ✅ Complete & Production-Ready

#### 2. `feature/MarketMatic-Smart-Assistant`

**Description:** AI-powered bilingual chatbot for SME customer engagement

**Features:**
- SinLlama 8.1B parameter model
- RAG system with document processing
- Bilingual support (English & Sinhala)
- Vector database for semantic search
- Multi-user authentication
- Bot customization interface

**Tech Stack:**
- FastAPI, Ollama, LangChain, FAISS, React
- Supabase (PostgreSQL), FAISS vector store

**Status:** ✅ Complete & Under Active Development

**Note:** SinLlama model is actively being improved for better accuracy and speed.

#### 3. `feature/personalized-marketing-strategy-recommender`

**Description:** Personalized marketing strategy recommendation engine

**Features:**
- Goal-based strategy generation
- Platform-specific recommendations
- Audience analysis
- Content strategy planning
- Budget optimization

**Tech Stack:**
- Flask/FastAPI, ML recommendation engine, React
- NLP for strategy generation

**Status:** 🔄 In Development

### Branch Workflow

```
main (production)
  ↑
  └── dev (integration testing)
       ↑
       ├── feature/Campaign-Performance-Prediction
       ├── feature/MarketMatic-Smart-Assistant
       └── feature/personalized-marketing-strategy-recommender
```

### Switching Between Branches

```bash
# View all branches
git branch -a

# Switch to a specific branch
git checkout feature/Campaign-Performance-Prediction
git checkout feature/MarketMatic-Smart-Assistant
git checkout feature/personalized-marketing-strategy-recommender

# Switch to development branch
git checkout dev

# Return to main
git checkout main
```

---

## 📚 Dependencies

### Backend Dependencies

#### Campaign Performance Prediction

```txt
flask==3.0.0
tensorflow==2.15.0
keras==2.15.0
numpy==1.24.3
pandas==2.1.3
scikit-learn==1.3.2
supabase==2.0.0
python-dotenv==1.0.0
flask-cors==4.0.0
easyocr==1.7.0
google-generativeai==0.3.1
pillow==10.1.0
psycopg2-binary==2.9.9
```

#### MarketMatic Smart Assistant

```txt
fastapi==0.109.0
uvicorn==0.25.0
python-multipart==0.0.6
pydantic==2.5.3
supabase==2.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
langchain==0.1.0
langchain-community==0.0.10
ollama==0.1.5
faiss-cpu==1.7.4
sentence-transformers==2.2.2
pypdf2==3.0.1
python-docx==1.1.0
openpyxl==3.1.2
pandas==2.1.3
numpy==1.24.3
psycopg2-binary==2.9.9
```

### Frontend Dependencies

```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0"
  }
}
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Model Loading Errors

**Problem:** `FileNotFoundError: Transformer.keras not found`

**Solution:**
```bash
# Ensure model files exist
ls backend/SavedModels/

# If missing, train the model using provided notebooks
```

#### 2. Supabase Connection Failed

**Problem:** `ConnectionError: Failed to connect to Supabase`

**Solution:**
- Verify Supabase connection string in `.env`
- Check that your project is active in Supabase dashboard
- Ensure API keys are correct (anon key vs service role key)
- Test connection:
```python
from supabase import create_client
client = create_client(supabase_url, supabase_key)
print(client.table('predictions').select('*').limit(1).execute())
```

#### 3. SinLlama Not Responding

**Problem:** Ollama service not running or model not loaded

**Solution:**
```bash
# Check Ollama status
ollama list

# Restart Ollama
ollama serve

# Reload model
ollama pull sinllama
```

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👥 Team & Contact

**Project Maintainer:** SachinthyaCodes

**Repository:** [https://github.com/SachinthyaCodes/AI-powered-digital-marketing-optimizer](https://github.com/SachinthyaCodes/AI-powered-digital-marketing-optimizer)

---

## 📊 Project Status

| Module | Status | Version | Last Updated |
|--------|--------|---------|--------------|
| Campaign Performance Prediction | ✅ Complete | 1.0.0 | Jan 2026 |
| MarketMatic Smart Assistant | 🔄 Active Dev | 0.9.0 | Jan 2026 |
| Strategy Recommender | 🚧 In Progress | 0.5.0 | Jan 2026 |

---

<div align="center">

**Made with ❤️ for Sri Lankan SMEs**

⭐ Star this repo if you find it helpful!

[Report Bug](https://github.com/SachinthyaCodes/AI-powered-digital-marketing-optimizer/issues) • [Request Feature](https://github.com/SachinthyaCodes/AI-powered-digital-marketing-optimizer/issues)

</div>
