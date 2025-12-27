from datetime import datetime, timedelta
import bcrypt
import secrets
from bson import ObjectId

class User:
    def __init__(self, email, password, full_name, company_name=None, role='user'):
        self.email = email
        self.password = self.hash_password(password)
        self.full_name = full_name
        self.company_name = company_name
        self.role = role  # 'superadmin', 'admin', 'user'
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @staticmethod
    def hash_password(password):
        """Hash a password for storing."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(plain_password, hashed_password):
        """Verify a stored password against one provided by user"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'email': self.email,
            'password': self.password,
            'full_name': self.full_name,
            'company_name': self.company_name,
            'role': self.role,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def serialize(user_doc):
        """Serialize user document from MongoDB"""
        if user_doc:
            return {
                'id': str(user_doc['_id']),
                'email': user_doc['email'],
                'full_name': user_doc['full_name'],
                'company_name': user_doc.get('company_name'),
                'role': user_doc.get('role', 'user'),
                'service_id': user_doc.get('service_id'),  # Include service_id
                'created_at': user_doc['created_at'].isoformat() if isinstance(user_doc['created_at'], datetime) else user_doc['created_at']
            }
        return None
    
    @staticmethod
    def generate_reset_token():
        """Generate a secure password reset token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def get_reset_token_expiry():
        """Get expiry time for reset token (1 hour from now)"""
        return datetime.utcnow() + timedelta(hours=1)
