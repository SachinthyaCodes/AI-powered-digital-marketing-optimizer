# AI-Powered Digital Marketing Optimizer

AI-Powered Digital Marketing Optimizer is an intelligent platform that helps Sri Lankan SMEs enhance their marketing performance using AI, ML, and NLP. It provides campaign optimization, sentiment analysis, forecasting, and smart insights through web and mobile applications.

##  Features

- **Performance Prediction**: Predict likes, comments, shares, clicks, and quality scores using Transformer deep learning model
- 
- **Explainability**: Feature importance analysis using gradient-based methods
- **Smart Recommendations**: Get actionable suggestions to improve engagement
- **Hashtag Suggestions**: AI-powered hashtag recommendations based on content
- **Timing Analysis**: Optimal posting time insights based on historical trends
- **MongoDB Integration**: Store predictions and access history

##  Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- MongoDB Atlas account (or local MongoDB)
- Git

##  Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
  ```bash
  .\venv\Scripts\activate
  ```
- macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

5. Ensure your trained models are in the `SavedModels` folder:
- `Transformer.keras`
- `tokenizer.json`
- `y_scaler.pkl`
- Optional: `BiLSTM.keras`, `BiGRU.keras`

6. Update the `.env` file if needed with your credentials

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

##  Running the Application

### Start Backend Server

1. Navigate to backend directory and activate virtual environment:
```bash
cd backend
.\venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # macOS/Linux
```

2. Run the Flask server:
```bash
python app.py
```

The backend will start on `http://localhost:5000`

### Start Frontend Development Server

1. In a new terminal, navigate to frontend directory:
```bash
cd frontend
```

2. Start the React development server:
```bash
npm start
```

The frontend will start on `http://localhost:3000` and automatically open in your browser

##  Usage

1. Open your browser and go to `http://localhost:3000`

2. Fill in the campaign details:
   - **Caption**: Your post caption/title
   - **Content**: Upload an image to extract text OR enter manually
   - **Platform**: Choose between Facebook, Instagram, or Twitter
   - **Post Date & Time**: When you plan to post
   - **Followers**: Your follower count
   - **Ad Boost**: Whether you'll use paid promotion

3. Click "🔮 Predict Performance" to get:
   - Predicted engagement metrics (Likes, Comments, Shares, Clicks)
   - Quality Score prediction
   - Personalized recommendations to improve performance
   - Hashtag suggestions
   - Optimal timing insights
   - Feature importance analysis

##  Configuration

### Backend Configuration (`.env`)

```env
STORAGE_TOKEN=AIzaSyDq4OganKVo1zTRFaNu-Xx-v7ONYpTTihQ
MONGODB_URI=mongodb+srv://ishghn1234:ishghn2000@cluster0.vo2av.mongodb.net/
DB_NAME=marketing_optimizer
FLASK_ENV=development
FLASK_DEBUG=True
```

### Model Requirements

Ensure these files exist in `backend/SavedModels/`:
- `Transformer.keras` - Trained Transformer model
- `tokenizer.json` - Text tokenizer (max 30,000 vocabulary)
- `y_scaler.pkl` - StandardScaler for target variables

##  API Endpoints

### Health Check
```
GET /health
Response: { "status": "healthy", "model_loaded": true, "mongodb_connected": true }
```

### Extract Text from Image
```
POST /api/extract-text
Body: { "image": "base64_encoded_image" }
Response: { "success": true, "text": "extracted_text" }
```

### Make Prediction
```
POST /api/predict
Body: {
  "caption": "string",
  "content": "string",
  "platform": "Facebook|Instagram|Twitter",
  "post_date": "YYYY-MM-DD",
  "post_time": "HH:MM",
  "followers": number,
  "ad_boost": 0|1
}
Response: {
  "success": true,
  "predictions": { ... },
  "hashtag_suggestions": [ ... ],
  "feature_importance": { ... },
  "recommendations": [ ... ],
  "timing_analysis": { ... }
}
```

### Get History
```
GET /api/history
Response: { "success": true, "history": [ ... ] }
```

##  Model Architecture

The application uses a **Transformer-based deep learning model** trained on social media campaign data with:
- **Multi-head attention mechanism** (4 heads, 128 dimensions)
- **Text embedding layer** (30,000 vocabulary size, 128 dimensions)
- **Global average pooling** for sequence aggregation
- **Numerical feature integration** (6 features)
- **Dense layers** with dropout for regularization
- **Multi-output regression** for 5 targets

### Model Training Details

The model was trained using:
- **Optimizer**: Adam (learning rate: 1e-4)
- **Loss**: Huber loss (robust to outliers)
- **Epochs**: 36
- **Batch size**: 64
- **Validation split**: 80/10/10 train/val/test

##  Features Used for Prediction

### Text Features
- Caption + Content (combined and tokenized)
- Max sequence length: 80 tokens

### Numerical Features
1. **Platform ID**: Encoded (Facebook: 0, Instagram: 1, Twitter: 2)
2. **Post Hour**: Hour of day (0-23)
3. **Day of Week**: 0 (Monday) to 6 (Sunday)
4. **Is Weekend**: Binary (0 or 1)
5. **Followers (log)**: Log-transformed follower count
6. **Ad Boost**: Binary (0 or 1)

### Target Variables (Predictions)
1. **Likes**: Predicted number of likes
2. **Comments**: Predicted number of comments
3. **Shares**: Predicted number of shares
4. **Clicks**: Predicted number of clicks
5. **Quality Score**: Post timing quality score

##  Tech Stack

### Backend
- **Flask** - Python web framework
- **TensorFlow/Keras** - Deep learning framework
- **EasyOCR** - OCR for text extraction from images
- **Google Generative AI** - Gemini API for Sinhala text extraction
- **PyMongo** - MongoDB integration
- **scikit-learn** - Data preprocessing and scaling
- **NumPy & Pandas** - Data manipulation

### Frontend
- **React 19** - UI framework
- **Axios** - HTTP client for API requests
- **CSS3** - Modern styling with gradients and animations

### Database
- **MongoDB Atlas** - Cloud-hosted NoSQL database

##  Explainability Features

### 1. Feature Importance
- Gradient-based importance calculation
- Shows which features most influence predictions
- Visual bar charts for easy interpretation

### 2. Recommendations
Categorized suggestions for improvement:
- **Caption**: Length and engagement tips
- **Hashtags**: Usage recommendations
- **Content**: Quality and clarity suggestions
- **Timing**: Optimal posting times
- **Ad Boost**: When to use paid promotion

### 3. Hashtag Suggestions
- Context-aware recommendations
- Category-based hashtag database
- Up to 10 relevant hashtags per post

### 4. Timing Analysis
- **Best Days**: Saturday, Sunday, Wednesday
- **Best Hours**: 9 AM, 12 PM, 3 PM, 6 PM, 8-9 PM
- **Worst Times**: Early morning (1-6 AM), Mondays, Tuesdays
- **Insights**: Peak engagement patterns

##  Troubleshooting

### Backend Issues

**Model Loading Error:**
```
Error: Cannot load model files
```
**Solution**: 
- Ensure all model files are in `backend/SavedModels/`
- Check TensorFlow version: `pip show tensorflow`
- Re-train models if necessary using `reach.ipynb`

**OCR Errors:**
```
Error: EasyOCR initialization failed
```
**Solution**:
- Install dependencies: `pip install easyocr torch`
- For Sinhala text, the system will fallback to Gemini API
- Verify Storage Token (Gemini API key) in `.env`

**MongoDB Connection Error:**
```
Error: MongoDB connection failed
```
**Solution**:
- Verify MongoDB URI in `.env`
- Check network connectivity
- Ensure IP address is whitelisted in MongoDB Atlas
- Test connection: `mongosh "your_connection_string"`

### Frontend Issues

**CORS Errors:**
```
Error: CORS policy blocked
```
**Solution**:
- Ensure Flask-CORS is installed: `pip install flask-cors`
- Backend should be running on port 5000
- Check CORS configuration in `app.py`

**API Connection Failed:**
```
Error: Network Error
```
**Solution**:
- Verify backend server is running on `http://localhost:5000`
- Check `API_BASE_URL` in `App.js`
- Test API: `curl http://localhost:5000/health`

**Dependencies Error:**
```
Error: Module not found
```
**Solution**:
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Clear npm cache: `npm cache clean --force`

##  Project Structure

```
AI-powered-digital-marketing-optimizer/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   ├── reach.ipynb           # Model training notebook
│   ├── Datasets/             # Training datasets (5 Excel files)
│   └── SavedModels/
│       ├── Transformer.keras # Trained model
│       ├── tokenizer.json    # Text tokenizer
│       └── y_scaler.pkl      # Target scaler
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # Styling
│   │   └── index.js          # Entry point
│   ├── public/
│   │   └── index.html        # HTML template
│   └── package.json          # Node dependencies
└── README.md                 # This file
```

##  Security Notes

- Never commit `.env` files to version control
- Keep API keys secure
- Use environment variables for sensitive data
- Implement rate limiting for production
- Add authentication for production deployment

##  Deployment

### Backend (Python/Flask)
- **Heroku**: `heroku create` and push
- **AWS EC2**: Deploy with Gunicorn
- **Google Cloud Run**: Containerize with Docker

### Frontend (React)
- **Vercel**: `vercel deploy`
- **Netlify**: Connect GitHub repo
- **AWS S3 + CloudFront**: Static hosting

### Database
- **MongoDB Atlas**: Already cloud-hosted
- Configure IP whitelist for production servers

##  Future Enhancements

- [ ] User authentication and accounts
- [ ] Save and compare multiple campaigns
- [ ] A/B testing recommendations
- [ ] Real-time social media integration
- [ ] Advanced analytics dashboard
- [ ] Mobile application (React Native)
- [ ] Multi-language support (Sinhala UI)
- [ ] Automated posting scheduler
- [ ] Competitor analysis
- [ ] Sentiment analysis integration

##  Research Paper

This project is part of a research initiative focusing on AI-powered digital marketing optimization for Sri Lankan SMEs. The research explores:
- Deep learning for social media engagement prediction
- Multi-modal content analysis (text + images)
- Explainable AI for marketing decisions
- Optimal timing strategies for content distribution

##  Contributors

- Research Team - SLIIT University, Y4 S1

##  Acknowledgments

- SLIIT University for research support
- TensorFlow and Keras teams
- React community
- EasyOCR contributors
- Google Generative AI team

##  Support

For issues, questions, or contributions:
- Create an issue in the repository
- Contact the research team
- Check documentation for common issues

##  License

This project is developed for academic and research purposes.

---

**⚠️ Important**: This application requires trained models. Ensure you have run the training notebook (`reach.ipynb`) with your datasets and saved the models in `backend/SavedModels/` before running the web application.

**🎯 Quick Start**: 
1. Backend: `cd backend && .\venv\Scripts\activate && python app.py`
2. Frontend: `cd frontend && npm start`
3. Access: `http://localhost:3000`

Happy Optimizing! 
