import jwt
from datetime import datetime, timedelta
from config import Config
from functools import wraps
from flask import request, jsonify

def create_access_token(user_id, email, role='user', service_id=None):
    """Create a JWT access token"""
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'service_id': service_id or user_id,  # Always include service_id, use user_id as fallback
        'exp': datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
        
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    return token

def decode_token(token):
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        # Decode token
        payload = decode_token(token)
        if payload is None:
            return jsonify({'message': 'Token is invalid or expired'}), 401
        
        # Add user info to request context
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated
