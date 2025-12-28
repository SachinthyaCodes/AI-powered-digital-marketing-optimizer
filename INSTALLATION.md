# Installation Instructions

## Prerequisites Check

Before installing, ensure you have:

1. **Python 3.8 or higher**
   ```bash
   python --version
   ```

2. **Node.js 14 or higher**
   ```bash
   node --version
   ```

3. **pip (Python package manager)**
   ```bash
   pip --version
   ```

4. **npm (Node package manager)**
   ```bash
   npm --version
   ```

## Installation Steps

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Note:** Installing EasyOCR may take 5-10 minutes as it downloads language models.

### 2. Verify Model Files

Ensure these files exist in `backend/SavedModels/`:
- ✅ `Transformer.keras`
- ✅ `tokenizer.json`
- ✅ `y_scaler.pkl`

If missing, run the training notebook:
```bash
# Open and run reach.ipynb
jupyter notebook reach.ipynb
```

### 3. Configure Environment

Edit `backend/.env` and verify:
```env
STORAGE_TOKEN=AIzaSyDq4OganKVo1zTRFaNu-Xx-v7ONYpTTihQ
MONGODB_URI=mongodb+srv://ishghn1234:ishghn2000@cluster0.vo2av.mongodb.net/
DB_NAME=marketing_optimizer
FLASK_ENV=development
FLASK_DEBUG=True
```

### 4. Test Backend

```bash
# Make sure you're in backend/ with venv activated
python app.py
```

You should see:
```
Initializing Marketing Optimizer API...
Loading Transformer model...
Model loaded successfully
Loading tokenizer...
Tokenizer loaded successfully
Loading scaler...
Scaler loaded successfully
Initializing EasyOCR...
EasyOCR initialized successfully
MongoDB connected successfully
Starting Flask server...
 * Running on http://0.0.0.0:5000
```

### 5. Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install
```

This will install:
- React 19
- Axios
- Testing libraries
- All other dependencies

### 6. Test Frontend

```bash
# Start development server
npm start
```

Browser should automatically open to `http://localhost:3000`

## Common Installation Issues

### Issue: "pip is not recognized"
**Solution:**
```bash
python -m pip install --upgrade pip
```

### Issue: "python: command not found"
**Solution:**
- On Windows: Add Python to PATH
- On Linux/macOS: Use `python3` instead of `python`

### Issue: "Cannot activate venv"
**Solution (Windows):**
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: "EasyOCR installation fails"
**Solution:**
```bash
# Install PyTorch first
pip install torch torchvision
# Then install EasyOCR
pip install easyocr
```

### Issue: "Module 'tensorflow' not found"
**Solution:**
```bash
pip install tensorflow==2.15.0
```

### Issue: "npm ERR! code ERESOLVE"
**Solution:**
```bash
npm install --legacy-peer-deps
```

### Issue: "Port 5000 already in use"
**Solution:**
- Find and kill the process using port 5000
- Or change port in app.py: `app.run(port=5001)`

### Issue: "MongoDB connection failed"
**Solution:**
- Check internet connection
- Verify MongoDB URI in .env
- Ensure IP is whitelisted in MongoDB Atlas
- Test connection: `mongosh "your_connection_string"`

## Verification Checklist

After installation, verify:

- [ ] Backend starts without errors
- [ ] `http://localhost:5000/health` returns healthy status
- [ ] Frontend starts and loads UI
- [ ] No console errors in browser
- [ ] Can submit form (even with dummy data)

## Package Versions

### Backend (Python)
- Flask 3.0.0
- TensorFlow 2.15.0
- NumPy 1.24.3
- Pandas 2.1.4
- scikit-learn 1.3.2
- EasyOCR 1.7.1
- PyMongo 4.6.1
- google-generativeai 0.3.2

### Frontend (Node.js)
- React 19.2.3
- Axios 1.6.2
- React Scripts 5.0.1

## System Requirements

### Minimum
- CPU: Dual-core processor
- RAM: 4GB
- Storage: 5GB free space
- OS: Windows 10, macOS 10.15, Ubuntu 20.04

### Recommended
- CPU: Quad-core processor
- RAM: 8GB or more
- Storage: 10GB free space
- GPU: Not required but helps with model inference

## Installation Time

- Backend setup: 10-15 minutes
- Frontend setup: 3-5 minutes
- Total: ~20 minutes

## Need Help?

1. Check error message in terminal
2. Review this installation guide
3. Check QUICKSTART.md
4. Review troubleshooting in README.md
5. Run test scripts to diagnose issues

## Next Steps

After successful installation:
1. Read QUICKSTART.md for usage guide
2. Test with sample data
3. Review PROJECT_SUMMARY.md for features
4. Start building your campaigns! 🚀
