# Quick Start Guide

## First Time Setup

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
setup.bat
```

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

## Running the Application

### Easy Way (Windows)

Open two terminals:

**Terminal 1 - Backend:**
```bash
start-backend.bat
```

**Terminal 2 - Frontend:**
```bash
start-frontend.bat
```

### Manual Way

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/macOS
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

## First Time Checklist

Before running the application, ensure:

- [ ] Python 3.8+ is installed (`python --version`)
- [ ] Node.js 14+ is installed (`node --version`)
- [ ] Backend dependencies installed (`pip list`)
- [ ] Frontend dependencies installed (check `frontend/node_modules/`)
- [ ] Models exist in `backend/SavedModels/`:
  - [ ] `Transformer.keras`
  - [ ] `tokenizer.json`
  - [ ] `y_scaler.pkl`
- [ ] `.env` file configured in `backend/`
- [ ] MongoDB connection string is valid

## Testing the Application

1. **Backend Health Check:**
   Open browser: `http://localhost:5000/health`
   
   Expected response:
   ```json
   {
     "status": "healthy",
     "model_loaded": true,
     "mongodb_connected": true
   }
   ```

2. **Frontend:**
   Should automatically open `http://localhost:3000`
   
3. **Test Prediction:**
   - Fill in the form
   - Upload an image (optional)
   - Click "Predict Performance"
   - Check results display

## Common Issues

### Backend won't start
```
Error: No module named 'flask'
```
**Solution:** Activate venv and run `pip install -r requirements.txt`

### Model files missing
```
Error: Cannot load model
```
**Solution:** Run `reach.ipynb` to train and save models

### Frontend won't start
```
Error: Cannot find module 'axios'
```
**Solution:** Run `npm install` in frontend directory

### MongoDB connection fails
```
Error: MongoDB connection error
```
**Solution:** Check MongoDB URI in `.env` file

## Sample Test Data

Use this data for your first test:

- **Caption:** "Check out our amazing new product! 🎉"
- **Content:** "High quality, affordable prices, free shipping"
- **Platform:** Facebook
- **Post Date:** Tomorrow's date
- **Post Time:** 18:00 (6 PM)
- **Followers:** 10000
- **Ad Boost:** Yes

## Expected Behavior

After clicking "Predict Performance":

1. Loading indicator appears
2. Results section displays with:
   - ❤️ Predicted Likes
   - 💬 Predicted Comments
   - 🔄 Predicted Shares
   - 👆 Predicted Clicks
   - ⭐ Quality Score
3. Recommendations section appears
4. Hashtag suggestions appear
5. Timing analysis shows optimal posting times
6. Feature importance bars display

## Next Steps

1. Try different platforms (Facebook, Instagram, Twitter)
2. Test with various follower counts
3. Upload images with text
4. Test different posting times
5. Compare predictions with/without ad boost

## URLs Reference

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **Health Check:** http://localhost:5000/health
- **MongoDB Atlas:** https://cloud.mongodb.com

## Support

If you encounter issues:
1. Check the terminal for error messages
2. Verify all prerequisites are met
3. Review the main README.md
4. Check the troubleshooting section

---

**Pro Tip:** Keep both terminals open to see real-time logs from backend and frontend!
