from functools import wraps
from flask import request, jsonify
from auth.jwt_handler import decode_token
import inspect

def superadmin_required(f):
    """Decorator to protect routes that require superadmin access"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Extract and validate token
        token = None
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
        
        # Check role
        if request.current_user.get('role') != 'superadmin':
            return jsonify({'message': 'Superadmin access required'}), 403
        
        # Check if function expects 'current_user' parameter
        sig = inspect.signature(f)
        if 'current_user' in sig.parameters:
            return f(current_user=request.current_user, *args, **kwargs)
        else:
            return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to protect routes that require admin or superadmin access"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Extract and validate token
        token = None
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
        
        # Check role
        role = request.current_user.get('role')
        if role not in ['admin', 'superadmin']:
            return jsonify({'message': 'Admin access required'}), 403
        
        # Check if function expects 'current_user' parameter
        sig = inspect.signature(f)
        if 'current_user' in sig.parameters:
            return f(current_user=request.current_user, *args, **kwargs)
        else:
            return f(*args, **kwargs)
    
    return decorated
