from flask import Blueprint, request, jsonify
from database import db_instance
from models.user import User
from auth.jwt_handler import create_access_token, token_required
from email_validator import validate_email, EmailNotValidError
from utils.email_service import EmailService
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user or admin"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'full_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        full_name = data['full_name'].strip()
        company_name = data.get('company_name', '').strip()
        is_admin = data.get('is_admin', False)
        service_token = data.get('service_token', '').strip()
        
        # Validate email format
        try:
            validate_email(email)
        except EmailNotValidError:
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Validate password strength
        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists
        db = db_instance.get_db()
        existing_user = db.users.find_one({'email': email})
        
        if existing_user:
            return jsonify({'message': 'User already exists'}), 409
        
        # Determine role
        role = 'user'
        service_id = None
        
        # If registering as admin, verify service token
        if is_admin:
            if not service_token:
                return jsonify({'message': 'Service token is required for admin registration'}), 400
            
            # Verify service token
            service = db.services.find_one({'service_token': service_token.upper()})
            
            if not service:
                return jsonify({'message': 'Invalid service token'}), 401
            
            if not service.get('is_active', True):
                return jsonify({'message': 'This service is currently inactive'}), 403
            
            # Check if admin already exists for this service
            existing_admin = db.users.find_one({
                'role': 'admin',
                'service_id': str(service['_id'])
            })
            
            if existing_admin:
                return jsonify({'message': 'An admin already exists for this service'}), 409
            
            role = 'admin'
            service_id = str(service['_id'])
            # Use service shop name as company name if not provided
            if not company_name:
                company_name = service.get('shop_name', '')
        
        # Create new user
        new_user = User(email, password, full_name, company_name, role)
        user_dict = new_user.to_dict()
        
        # Add service_id for admin users
        if service_id:
            user_dict['service_id'] = service_id
        
        result = db.users.insert_one(user_dict)
        
        # Create JWT token
        token = create_access_token(str(result.inserted_id), email, role, service_id)
        
        return jsonify({
            'message': f'{"Admin" if is_admin else "User"} created successfully',
            'token': token,
            'user': {
                'id': str(result.inserted_id),
                'email': email,
                'full_name': full_name,
                'company_name': company_name,
                'role': role,
                'service_id': service_id
            }
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error creating user: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Find user
        db = db_instance.get_db()
        user = db.users.find_one({'email': email})
        
        if not user:
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Verify password
        if not User.verify_password(password, user['password']):
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Create JWT token
        user_role = user.get('role', 'user')
        # Always include service_id: use existing service_id or user's own ID as fallback
        service_id = user.get('service_id', str(user['_id']))
        token = create_access_token(str(user['_id']), email, user_role, service_id)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': User.serialize(user)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error logging in: {str(e)}'}), 500

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token():
    """Verify if token is valid"""
    try:
        user_id = request.current_user['user_id']
        
        # Get user from database
        db = db_instance.get_db()
        from bson import ObjectId
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'message': 'Token is valid',
            'user': User.serialize(user)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error verifying token: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current user information"""
    try:
        user_id = request.current_user['user_id']
        
        # Get user from database
        db = db_instance.get_db()
        from bson import ObjectId
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'user': User.serialize(user)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error getting user: {str(e)}'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({'message': 'Email is required'}), 400
        
        email = data['email'].lower().strip()
        
        # Validate email format
        try:
            validate_email(email)
        except EmailNotValidError:
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Find user
        db = db_instance.get_db()
        user = db.users.find_one({'email': email})
        
        # Always return success to prevent email enumeration
        # Even if user doesn't exist, we say email was sent
        if not user:
            return jsonify({
                'message': 'If an account with that email exists, we have sent a password reset link.'
            }), 200
        
        # Generate reset token
        reset_token = User.generate_reset_token()
        reset_token_expiry = User.get_reset_token_expiry()
        
        # Update user with reset token
        from bson import ObjectId
        db.users.update_one(
            {'_id': ObjectId(user['_id'])},
            {
                '$set': {
                    'reset_token': reset_token,
                    'reset_token_expiry': reset_token_expiry
                }
            }
        )
        
        # Send password reset email
        email_sent = EmailService.send_password_reset_email(
            to_email=email,
            reset_token=reset_token,
            user_name=user['full_name']
        )
        
        if not email_sent:
            return jsonify({
                'message': 'Error sending email. Please try again later or contact support.'
            }), 500
        
        return jsonify({
            'message': 'If an account with that email exists, we have sent a password reset link.'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error processing request: {str(e)}'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('token') or not data.get('password'):
            return jsonify({'message': 'Token and new password are required'}), 400
        
        token = data['token']
        new_password = data['password']
        
        # Validate password strength
        if len(new_password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters'}), 400
        
        # Find user with valid token
        db = db_instance.get_db()
        user = db.users.find_one({
            'reset_token': token,
            'reset_token_expiry': {'$gt': datetime.utcnow()}
        })
        
        if not user:
            return jsonify({'message': 'Invalid or expired reset token'}), 400
        
        # Hash new password
        hashed_password = User.hash_password(new_password)
        
        # Update password and clear reset token
        from bson import ObjectId
        db.users.update_one(
            {'_id': ObjectId(user['_id'])},
            {
                '$set': {
                    'password': hashed_password,
                    'updated_at': datetime.utcnow()
                },
                '$unset': {
                    'reset_token': '',
                    'reset_token_expiry': ''
                }
            }
        )
        
        return jsonify({
            'message': 'Password has been reset successfully. You can now login with your new password.'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error resetting password: {str(e)}'}), 500

@auth_bp.route('/verify-reset-token', methods=['POST'])
def verify_reset_token():
    """Verify if reset token is valid"""
    try:
        data = request.get_json()
        
        if not data.get('token'):
            return jsonify({'message': 'Token is required'}), 400
        
        token = data['token']
        
        print(f"Verifying token: {token[:20]}...")  # Debug log
        
        # Find user with valid token
        db = db_instance.get_db()
        user = db.users.find_one({
            'reset_token': token,
            'reset_token_expiry': {'$gt': datetime.utcnow()}
        })
        
        if not user:
            print(f"No user found with valid token")  # Debug log
            return jsonify({'valid': False, 'message': 'Invalid or expired reset token'}), 200
        
        print(f"Token valid for user: {user['email']}")  # Debug log
        return jsonify({
            'valid': True,
            'email': user['email']
        }), 200
        
    except Exception as e:
        print(f"Error verifying token: {str(e)}")  # Debug log
        return jsonify({'message': f'Error verifying token: {str(e)}'}), 500
