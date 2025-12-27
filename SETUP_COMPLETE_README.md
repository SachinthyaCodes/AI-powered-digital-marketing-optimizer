# 🎯 MarketMatic - Quick Setup & Run Guide

## ✅ Your Application is Now Ready!

Your MarketMatic application has been successfully set up with Python 3.11 environment and all dependencies installed.

## 🚀 Quick Start

### Option 1: Use the Startup Script (Recommended)
```bash
# Activate the conda environment
conda activate marketmatic

# Run the application manager
python start_app.py
```

### Option 2: Use Windows Batch File
Double-click `start_marketmatic.bat` file in the project root.

### Option 3: Manual Startup

**Backend Server:**
```bash
conda activate marketmatic
cd backend
python run_server.py
# Server runs at: http://127.0.0.1:5000
```

**Frontend Server:**
```bash
cd frontend  
npm run dev
# Server runs at: http://localhost:5173
```

## 🔧 Environment Details

- **Python Version:** 3.11.14
- **Environment Name:** marketmatic
- **Backend Framework:** Flask
- **Frontend Framework:** React + Vite
- **Database:** MongoDB
- **Vector Database:** ChromaDB

## 📁 Project Structure

```
marketmatic/
├── backend/              # Flask API server
│   ├── app.py           # Main Flask application
│   ├── run_server.py    # Production server runner
│   ├── requirements.txt # Python dependencies
│   ├── .env            # Environment variables
│   └── ...
├── frontend/            # React frontend
│   ├── package.json    # Node.js dependencies
│   ├── src/            # React components
│   └── ...
├── start_app.py        # Application manager script
└── start_marketmatic.bat # Windows startup script
```

## 🌐 Application URLs

- **Frontend (User Interface):** http://localhost:5173
- **Backend API:** http://127.0.0.1:5000
- **API Health Check:** http://127.0.0.1:5000/api/health

## 🔑 Key Features Available

1. **User Authentication:** Login, registration, password reset
2. **Bot Management:** Create and configure chatbots
3. **Document Upload:** RAG system with vector embeddings
4. **Chat Interface:** Interactive chatbot conversations
5. **Admin Dashboard:** Service and user management
6. **Super Admin Panel:** Full system administration

## ⚙️ Environment Configuration

Your `.env` file is already configured with:
- MongoDB connection
- JWT authentication
- Email service (Gmail)
- Cloudinary (image uploads)
- Modal service (LLM inference)

## 🛠️ Common Commands

**Check Python environment:**
```bash
conda activate marketmatic
python --version
```

**Install new backend dependencies:**
```bash
conda activate marketmatic
cd backend
pip install <package-name>
```

**Install new frontend dependencies:**
```bash
cd frontend
npm install <package-name>
```

**Update requirements.txt:**
```bash
conda activate marketmatic
cd backend
pip freeze > requirements.txt
```

## 🐛 Troubleshooting

**If backend won't start:**
1. Ensure conda environment is activated: `conda activate marketmatic`
2. Check Python version: `python --version` (should be 3.11.x)
3. Verify dependencies: `pip list`

**If frontend won't start:**
1. Delete `node_modules`: `rm -rf node_modules`
2. Reinstall: `npm install`
3. Try: `npm run dev`

**Database connection issues:**
1. Check MongoDB URL in `.env`
2. Verify network connectivity
3. Check firewall settings

## 📊 Monitoring

- **Backend logs:** Check terminal where backend is running
- **Frontend logs:** Check browser developer tools
- **Database:** Monitor MongoDB connection status

## 🔐 Security Notes

- Never commit `.env` file to version control
- Keep JWT secret keys secure
- Use strong database passwords
- Enable HTTPS in production

## 🚀 Production Deployment

For production deployment, consider:
- Use production WSGI server (gunicorn, uwsgi)
- Set up reverse proxy (nginx)
- Use production database
- Enable SSL/TLS
- Set up monitoring and logging

---

**🎉 Congratulations! Your MarketMatic application is ready to use!**

Need help? Check the individual README files in backend/ and frontend/ directories for more detailed information.