from flask import Blueprint, request, jsonify
from database import SessionLocal
from models.sqlalchemy_models import User
from auth.jwt_handler import create_access_token
from email_validator import validate_email, EmailNotValidError

superadmin_auth_bp = Blueprint('superadmin_auth', __name__, url_prefix='/api/superadmin')

# Hardcoded superadmin credentials (fallback)
SUPERADMIN_USERNAME = 'superadmin'
SUPERADMIN_PASSWORD = 'superadmin'

@superadmin_auth_bp.route('/register', methods=['POST'])
def register_superadmin():
    """Register first superadmin (can only be done once)"""
    db = SessionLocal()
    try:
        # Check if any superadmin already exists
        existing_superadmin = db.query(User).filter(User.role == 'superadmin').first()
        
        if existing_superadmin:
            return jsonify({'message': 'Superadmin already exists. Use hardcoded credentials or existing account.'}), 409
        
        data = request.get_json()
        
        # Validate required fields
        email = data.get('email', '').lower().strip()
        password = data.get('password', '').strip()
        full_name = data.get('full_name', '').strip()
        
        if not all([email, password, full_name]):
            return jsonify({'message': 'Email, password, and full name are required'}), 400
        
        # Validate email
        try:
            validate_email(email)
        except EmailNotValidError:
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Create superadmin user
        import uuid
        new_superadmin = User(
            id=str(uuid.uuid4()),
            email=email,
            password=User.hash_password(password),
            full_name=full_name,
            role='superadmin',
            service_id=None
        )
        
        db.add(new_superadmin)
        db.commit()
        db.refresh(new_superadmin)
        
        # Create token
        token = create_access_token(new_superadmin.id, new_superadmin.email, 'superadmin')
        
        return jsonify({
            'message': 'Superadmin registered successfully',
            'token': token,
            'user': new_superadmin.to_dict()
        }), 201
        
    except Exception as e:
        db.rollback()
        import traceback
        print(f"Error registering superadmin: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'Error registering superadmin: {str(e)}'}), 500
    finally:
        db.close()

@superadmin_auth_bp.route('/login', methods=['POST'])
def superadmin_login():
    """Superadmin login with database or hardcoded credentials"""
    db = SessionLocal()
    try:
        data = request.get_json()
        
        # Support both username and email
        identifier = data.get('username') or data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not identifier or not password:
            return jsonify({'message': 'Email/username and password are required'}), 400
        
        # Try database login first
        user = db.query(User).filter(
            User.email == identifier.lower(),
            User.role == 'superadmin'
        ).first()
        
        if user and User.verify_password(password, user.password):
            # Database superadmin
            token = create_access_token(user.id, user.email, 'superadmin')
            return jsonify({
                'message': 'Superadmin login successful',
                'token': token,
                'user': user.to_dict()
            }), 200
        
        # Fallback to hardcoded credentials
        if identifier == SUPERADMIN_USERNAME and password == SUPERADMIN_PASSWORD:
            token = create_access_token('superadmin_id', SUPERADMIN_USERNAME, 'superadmin')
            return jsonify({
                'message': 'Superadmin login successful',
                'token': token,
                'user': {
                    'id': 'superadmin_id',
                    'email': 'superadmin@marketmatic.com',
                    'full_name': 'Super Administrator',
                    'role': 'superadmin'
                }
            }), 200
        
        return jsonify({'message': 'Invalid credentials'}), 401
        
    except Exception as e:
        import traceback
        print(f"Error logging in: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'Error logging in: {str(e)}'}), 500
    finally:
        db.close()
