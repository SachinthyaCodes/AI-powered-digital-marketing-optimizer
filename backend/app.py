import os
import json
import numpy as np
import pandas as pd
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import StandardScaler
import pickle
from pymongo import MongoClient
import shap
from PIL import Image
import io
import base64
import easyocr
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Configuration
STORAGE_TOKEN = os.getenv('STORAGE_TOKEN', 'AIzaSyDq4OganKVo1zTRFaNu-Xx-v7ONYpTTihQ')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://ishghn1234:ishghn2000@cluster0.vo2av.mongodb.net/')
DB_NAME = os.getenv('DB_NAME', 'marketing_optimizer')

# Configure Gemini
genai.configure(api_key=STORAGE_TOKEN)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# MongoDB connection
try:
    mongo_client = MongoClient(MONGODB_URI)
    db = mongo_client[DB_NAME]
    predictions_collection = db['predictions']
    print("MongoDB connected successfully")
except Exception as e:
    print(f"MongoDB connection error: {e}")
    mongo_client = None

# Model paths
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'SavedModels')
MODEL_PATH = os.path.join(MODEL_DIR, 'Transformer_fixed.keras')
TOKENIZER_PATH = os.path.join(MODEL_DIR, 'tokenizer.json')
SCALER_PATH = os.path.join(MODEL_DIR, 'y_scaler.pkl')

# Global variables
model = None
tokenizer = None
y_scaler = None
easyocr_reader = None
MAX_LEN = 80
platform_map = {0: 'Facebook', 1: 'Instagram', 2: 'Twitter'}
inv_platform_map = {'Facebook': 0, 'Instagram': 1, 'Twitter': 2}
targets = ["likes", "comments", "shares", "clicks", "timing_quality_score"]
num_features = ["platform_id", "post_hour", "day_of_week", "is_weekend", "followers_log", "ad_boost"]

# Hashtag suggestions database (can be extended)
HASHTAG_SUGGESTIONS = {
    'food': ['#foodie', '#delicious', '#yummy', '#foodporn', '#instafood', '#foodlover'],
    'travel': ['#travel', '#wanderlust', '#explore', '#adventure', '#travelgram', '#vacation'],
    'fashion': ['#fashion', '#style', '#ootd', '#fashionista', '#fashionblogger', '#trendy'],
    'fitness': ['#fitness', '#gym', '#workout', '#fitfam', '#health', '#motivation'],
    'technology': ['#tech', '#technology', '#innovation', '#gadgets', '#digital', '#future'],
    'business': ['#business', '#entrepreneur', '#marketing', '#success', '#startup', '#leadership'],
    'beauty': ['#beauty', '#makeup', '#skincare', '#beautytips', '#glam', '#cosmetics'],
    'photography': ['#photography', '#photooftheday', '#instagood', '#picoftheday', '#photographer', '#camera'],
}

def load_models():
    """Load ML models and preprocessing utilities"""
    global model, tokenizer, y_scaler, easyocr_reader
    
    try:
        # Load fixed Transformer model
        print("Loading Transformer model...")
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        print("Model loaded successfully")
        
        # Load tokenizer
        print("Loading tokenizer...")
        with open(TOKENIZER_PATH, 'r') as f:
            tokenizer_json = f.read()  # Read as string, not dict
            tokenizer = tokenizer_from_json(tokenizer_json)
        print("Tokenizer loaded successfully")
        
        # Load y_scaler
        print("Loading scaler...")
        with open(SCALER_PATH, 'rb') as f:
            y_scaler = pickle.load(f)
        print("Scaler loaded successfully")
        
        # Initialize EasyOCR for English (Sinhala not supported, will use Gemini for Sinhala)
        print("Initializing EasyOCR...")
        easyocr_reader = easyocr.Reader(['en'], gpu=False)
        print("EasyOCR initialized successfully")
        print("Note: Using Gemini API for Sinhala text extraction")
        
    except Exception as e:
        print(f"Error loading models: {e}")
        raise e

def extract_text_from_image(image_data):
    """Extract text from image using EasyOCR, fallback to Gemini API"""
    try:
        # Decode base64 image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Try EasyOCR first
        try:
            # Convert PIL Image to numpy array
            image_np = np.array(image)
            result = easyocr_reader.readtext(image_np)
            
            if result:
                # Combine all detected text into meaningful lines
                extracted_text = ' '.join([detection[1] for detection in result])
                if extracted_text.strip():
                    print(f"Text extracted via EasyOCR: {extracted_text[:100]}...")
                    return extracted_text.strip()
        except Exception as e:
            print(f"EasyOCR failed: {e}")
        
        # Fallback to Gemini API for Sinhala/English content
        print("Using Storage API for text extraction...")
        image.save('temp_image.jpg')
        
        with open('temp_image.jpg', 'rb') as img_file:
            image_parts = [{"mime_type": "image/jpeg", "data": img_file.read()}]
        
        prompt = "Extract all text from this image. If the text is in Sinhala or mixed Sinhala-English, please extract it accurately. Return the text as a single paragraph, not line by line."
        
        response = gemini_model.generate_content([prompt, image_parts[0]])
        extracted_text = response.text.strip()
        
        # Clean up temp file
        if os.path.exists('temp_image.jpg'):
            os.remove('temp_image.jpg')
        
        print(f"Text extracted via Storage API: {extracted_text[:100]}...")
        return extracted_text
        
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

def preprocess_input(caption, content, platform, post_date, post_time, followers, ad_boost):
    """Preprocess input data for model prediction"""
    try:
        # Combine caption and content for text features
        text = f"{caption} {content}"
        
        # Text sequence
        sequences = tokenizer.texts_to_sequences([text])
        text_seq = pad_sequences(sequences, maxlen=MAX_LEN, padding='post', truncating='post')
        
        # Platform encoding
        platform_id = inv_platform_map.get(platform, 0)
        
        # Time features
        post_datetime = datetime.strptime(f"{post_date} {post_time}", "%Y-%m-%d %H:%M")
        post_hour = post_datetime.hour
        day_of_week = post_datetime.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0
        
        # Followers log transform
        followers_log = np.log1p(float(followers))
        
        # Numerical features
        num_data = np.array([[
            platform_id,
            post_hour,
            day_of_week,
            is_weekend,
            followers_log,
            int(ad_boost)
        ]], dtype='float32')
        
        return text_seq, num_data
        
    except Exception as e:
        print(f"Error preprocessing input: {e}")
        raise e

def make_prediction(text_seq, num_data):
    """Make prediction using the Transformer model"""
    try:
        # Predict
        y_pred_scaled = model.predict([text_seq, num_data], verbose=0)
        
        # Inverse transform
        y_pred = y_scaler.inverse_transform(y_pred_scaled)
        
        # Inverse log transform for likes, comments, shares, clicks
        predictions = {}
        for i, target in enumerate(targets):
            if target in ['likes', 'comments', 'shares', 'clicks']:
                predictions[target] = max(0, int(np.expm1(y_pred[0][i])))
            else:
                predictions[target] = float(y_pred[0][i])
        
        return predictions
        
    except Exception as e:
        print(f"Error making prediction: {e}")
        raise e

def generate_hashtag_suggestions(caption, content):
    """Generate hashtag suggestions based on caption and content"""
    text = f"{caption} {content}".lower()
    suggested_hashtags = []
    
    # Check for keywords and suggest relevant hashtags
    for category, hashtags in HASHTAG_SUGGESTIONS.items():
        if category in text:
            suggested_hashtags.extend(hashtags[:3])
    
    # Generic popular hashtags if no specific match
    if not suggested_hashtags:
        suggested_hashtags = ['#viral', '#trending', '#instagood', '#photooftheday', '#like4like']
    
    return list(set(suggested_hashtags))[:10]

def get_feature_importance(text_seq, num_data):
    """Calculate feature importance using model gradients"""
    try:
        # Create a wrapper function for SHAP
        def predict_wrapper(combined_input):
            # Split combined input back to text and numerical
            text_input = combined_input[:, :MAX_LEN].astype(int)
            num_input = combined_input[:, MAX_LEN:].astype(float)
            return model.predict([text_input, num_input], verbose=0)
        
        # Combine inputs for SHAP
        combined = np.concatenate([text_seq, num_data], axis=1)
        
        # Use gradient-based importance
        with tf.GradientTape() as tape:
            text_tensor = tf.constant(text_seq, dtype=tf.int32)
            num_tensor = tf.constant(num_data, dtype=tf.float32)
            tape.watch(num_tensor)
            predictions = model([text_tensor, num_tensor])
        
        # Get gradients for numerical features
        gradients = tape.gradient(predictions, num_tensor)
        importance = np.abs(gradients.numpy()[0])
        
        # Create importance dictionary
        feature_importance = {}
        for i, feature in enumerate(num_features):
            feature_importance[feature] = float(importance[i])
        
        return feature_importance
        
    except Exception as e:
        print(f"Error calculating feature importance: {e}")
        return {}

def generate_recommendations(predictions, feature_importance, caption, content, post_hour, day_of_week):
    """Generate actionable recommendations to improve metrics"""
    recommendations = []
    
    # Caption recommendations
    if len(caption) < 20:
        recommendations.append({
            "category": "Caption",
            "suggestion": "Your caption is quite short. Try making it more descriptive and engaging (aim for 20-50 characters).",
            "impact": "Medium"
        })
    
    # Hashtag recommendations
    current_hashtags = caption.count('#') + content.count('#')
    if current_hashtags < 3:
        recommendations.append({
            "category": "Hashtags",
            "suggestion": "Add 3-7 relevant hashtags to increase discoverability and reach a wider audience.",
            "impact": "High"
        })
    
    # Content recommendations
    if len(content) < 30:
        recommendations.append({
            "category": "Content",
            "suggestion": "Your content description is brief. Add more details or emotional appeal to engage viewers.",
            "impact": "Medium"
        })
    
    # Timing recommendations
    optimal_hours = [9, 12, 15, 18, 20, 21]  # Peak engagement hours
    if post_hour not in optimal_hours:
        recommendations.append({
            "category": "Timing",
            "suggestion": f"Consider posting during peak hours (9AM, 12PM, 3PM, 6PM, 8-9PM) instead of {post_hour}:00. Current timing may reduce visibility.",
            "impact": "High"
        })
    
    # Weekend vs weekday
    if day_of_week < 5:
        recommendations.append({
            "category": "Timing",
            "suggestion": "Weekends (especially Saturday and Sunday) often see higher engagement. Consider scheduling important posts for weekends.",
            "impact": "Medium"
        })
    
    # Quality score specific
    if predictions.get('timing_quality_score', 0) < 0.5:
        recommendations.append({
            "category": "Quality Score",
            "suggestion": "Your timing quality score is low. Try posting during peak engagement times and on weekends.",
            "impact": "High"
        })
    
    # Ad boost recommendation
    if predictions.get('likes', 0) < 100:
        recommendations.append({
            "category": "Ad Boost",
            "suggestion": "Consider using ad boost to increase initial visibility and potentially trigger organic growth.",
            "impact": "High"
        })
    
    return recommendations

def get_optimal_timing_analysis():
    """Provide insights on optimal posting times based on general trends"""
    return {
        "best_days": ["Saturday", "Sunday", "Wednesday"],
        "best_hours": [9, 12, 15, 18, 20, 21],
        "worst_days": ["Monday", "Tuesday"],
        "worst_hours": [1, 2, 3, 4, 5, 6, 23],
        "insights": {
            "weekend_boost": "Weekend posts typically receive 30-40% more engagement",
            "morning_peak": "9-10 AM is ideal for breakfast/morning content",
            "lunch_peak": "12-1 PM catches lunch break scrollers",
            "evening_peak": "6-9 PM is prime time for maximum engagement",
            "avoid": "Early morning (1-6 AM) sees minimal engagement"
        }
    }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'mongodb_connected': mongo_client is not None
    })

@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    """Extract text from uploaded image"""
    try:
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        extracted_text = extract_text_from_image(image_data)
        
        return jsonify({
            'success': True,
            'text': extracted_text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    try:
        data = request.json
        
        # Extract input data
        caption = data.get('caption', '')
        content = data.get('content', '')
        platform = data.get('platform', 'Facebook')
        post_date = data.get('post_date')
        post_time = data.get('post_time')
        followers = data.get('followers', 0)
        ad_boost = data.get('ad_boost', 0)
        
        # Validate required fields
        if not post_date or not post_time:
            return jsonify({'error': 'post_date and post_time are required'}), 400
        
        # Preprocess input
        text_seq, num_data = preprocess_input(
            caption, content, platform, post_date, post_time, followers, ad_boost
        )
        
        # Make prediction
        predictions = make_prediction(text_seq, num_data)
        
        # Generate hashtag suggestions
        hashtags = generate_hashtag_suggestions(caption, content)
        
        # Get feature importance
        feature_importance = get_feature_importance(text_seq, num_data)
        
        # Generate recommendations
        post_datetime = datetime.strptime(f"{post_date} {post_time}", "%Y-%m-%d %H:%M")
        recommendations = generate_recommendations(
            predictions, feature_importance, caption, content,
            post_datetime.hour, post_datetime.weekday()
        )
        
        # Get optimal timing analysis
        timing_analysis = get_optimal_timing_analysis()
        
        # Prepare response
        response_data = {
            'success': True,
            'predictions': predictions,
            'hashtag_suggestions': hashtags,
            'feature_importance': feature_importance,
            'recommendations': recommendations,
            'timing_analysis': timing_analysis
        }
        
        # Save to MongoDB
        if mongo_client:
            try:
                document = {
                    'caption': caption,
                    'content': content,
                    'platform': platform,
                    'post_date': post_date,
                    'post_time': post_time,
                    'followers': followers,
                    'ad_boost': ad_boost,
                    'predictions': predictions,
                    'hashtag_suggestions': hashtags,
                    'created_at': datetime.utcnow()
                }
                predictions_collection.insert_one(document)
                print("Prediction saved to MongoDB")
            except Exception as e:
                print(f"Error saving to MongoDB: {e}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get prediction history"""
    try:
        if not mongo_client:
            return jsonify({'error': 'Database not connected'}), 500
        
        # Get last 50 predictions
        predictions = list(predictions_collection.find(
            {},
            {'_id': 0}
        ).sort('created_at', -1).limit(50))
        
        return jsonify({
            'success': True,
            'history': predictions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Initializing Marketing Optimizer API...")
    load_models()
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
