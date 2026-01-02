"""
SQLAlchemy ORM Models for Supabase PostgreSQL
Replaces MongoDB models with relational schema
"""
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, ForeignKey, Text, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import bcrypt
import secrets
from uuid import uuid4

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    company_name = Column(String(255))
    role = Column(String(50), default='user')  # 'superadmin', 'admin', 'user'
    service_id = Column(String(36), ForeignKey('services.id'), nullable=True, index=True)

    # Password reset
    reset_token = Column(String(255), nullable=True, unique=True)
    reset_token_expiry = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    service = relationship("Service", back_populates="users")
    chat_messages = relationship("ChatMessage", back_populates="user")

    @staticmethod
    def hash_password(password):
        """Hash a password for storing."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(plain_password, hashed_password):
        """Verify a stored password against one provided by user"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def generate_reset_token():
        """Generate a secure password reset token"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def get_reset_token_expiry():
        """Get expiry time for reset token (1 hour from now)"""
        return datetime.utcnow() + timedelta(hours=1)

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'company_name': self.company_name,
            'role': self.role,
            'service_id': self.service_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Service(Base):
    __tablename__ = 'services'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    shop_name = Column(String(255), nullable=False)
    owner_name = Column(String(255), nullable=False)
    address = Column(String(255))
    email = Column(String(255), nullable=False)
    phone = Column(String(20))
    service_token = Column(String(100), unique=True, nullable=False, index=True)

    # Business info
    business_description = Column(Text)
    operating_hours = Column(JSON)  # Store as JSON: {"monday": "9-6", "tuesday": "9-6", ...}
    contact_info = Column(JSON)

    # Bot configuration
    bot_name = Column(String(255))
    bot_description = Column(Text)
    welcome_message = Column(Text)
    fallback_message = Column(Text)
    language_support = Column(String(100))  # Comma-separated languages
    rag_enabled = Column(Boolean, default=True)
    nlp_enabled = Column(Boolean, default=True)
    response_mode = Column(String(50))  # e.g., 'auto', 'manual'
    documents_only_message = Column(Text)
    use_general_knowledge = Column(Boolean, default=True)
    
    # Response configuration
    max_response_tokens = Column(Integer, default=300)  # Max tokens in bot response (100-1000)
    response_temperature = Column(Float, default=0.7)  # Creativity (0.0-1.0)
    response_timeout = Column(Integer, default=30)  # Seconds before timeout (10-120)

    # Subscription
    subscription_duration = Column(Integer)
    subscription_unit = Column(String(20))  # 'week', 'month', 'year'
    subscription_start = Column(DateTime)
    subscription_end = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    users = relationship("User", back_populates="service")
    documents = relationship("Document", back_populates="service")
    products = relationship("Product", back_populates="service")
    faqs = relationship("FAQ", back_populates="service")
    policies = relationship("Policy", back_populates="service")
    chat_sessions = relationship("ChatMessage", back_populates="service")
    embeddings = relationship("DocumentEmbedding", back_populates="service")

    @staticmethod
    def generate_token():
        """Generate a unique service token"""
        return secrets.token_hex(16).upper()

    def to_dict(self):
        """Convert to dictionary for API responses"""
        import json
        
        # Helper function to parse JSON strings
        def parse_json_field(value):
            if value is None:
                return None
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except:
                    return value
            return value
        
        return {
            'id': self.id,
            'shop_name': self.shop_name,
            'owner_name': self.owner_name,
            'address': self.address,
            'email': self.email,
            'phone': self.phone,
            'service_token': self.service_token,
            'business_description': self.business_description,
            'operating_hours': self.operating_hours,
            'contact_info': self.contact_info,
            'bot_name': self.bot_name,
            'bot_description': self.bot_description,
            'welcome_message': parse_json_field(self.welcome_message),
            'fallback_message': parse_json_field(self.fallback_message),
            'documents_only_message': parse_json_field(self.documents_only_message),
            'language_support': self.language_support.split(',') if self.language_support else [],
            'rag_enabled': self.rag_enabled,
            'nlp_enabled': self.nlp_enabled,
            'response_mode': self.response_mode,
            'use_general_knowledge': self.use_general_knowledge,
            'max_response_tokens': self.max_response_tokens,
            'response_temperature': self.response_temperature,
            'response_timeout': self.response_timeout,
            'subscription_duration': self.subscription_duration,
            'subscription_unit': self.subscription_unit,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Document(Base):
    __tablename__ = 'documents'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    service_id = Column(String(36), ForeignKey('services.id'), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    document_type = Column(String(50))  # 'pdf', 'docx', 'excel', 'txt'
    file_size = Column(Integer)

    # Processing info
    is_processed = Column(Boolean, default=False)
    chunk_count = Column(Integer, default=0)
    embedding_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    service = relationship("Service", back_populates="documents")
    embeddings = relationship("DocumentEmbedding", back_populates="document", cascade="all, delete-orphan")

    # Index for faster queries
    __table_args__ = (
        Index('idx_service_created', 'service_id', 'created_at'),
    )

    def to_dict(self):
        """Convert to dictionary for API responses"""
        # Determine status based on is_processed flag
        if self.is_processed:
            status = 'completed'
        else:
            status = 'processing'
        
        return {
            'id': self.id,
            'service_id': self.service_id,
            'filename': self.filename,
            'document_type': self.document_type,
            'file_size': self.file_size,
            'is_processed': self.is_processed,
            'status': status,  # Add status field for frontend
            'chunk_count': self.chunk_count,
            'chunks_count': self.chunk_count,  # Alias for frontend compatibility
            'embedding_count': self.embedding_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DocumentEmbedding(Base):
    __tablename__ = 'document_embeddings'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    service_id = Column(String(36), ForeignKey('services.id'), nullable=False, index=True)
    document_id = Column(String(36), ForeignKey('documents.id'), nullable=False, index=True)

    # Content and embedding
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=False)  # nomic-embed-text produces 768-dim vectors

    # Additional metadata
    chunk_metadata = Column(JSON)  # Store additional info like page number, section, etc.

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    service = relationship("Service", back_populates="embeddings")
    document = relationship("Document", back_populates="embeddings")

    # Index for faster similarity search
    __table_args__ = (
        Index('idx_service_embedding', 'service_id'),
    )

    def to_dict(self):
        """Convert to dictionary (without embedding for API responses)"""
        return {
            'id': self.id,
            'service_id': self.service_id,
            'document_id': self.document_id,
            'chunk_index': self.chunk_index,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    service_id = Column(String(36), ForeignKey('services.id'), nullable=False, index=True)
    session_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=True)

    # Message content
    role = Column(String(20), nullable=False)  # 'user', 'assistant'
    content = Column(Text, nullable=False)

    # Context
    context = Column(Text)  # Retrieved context from documents
    message_metadata = Column(JSON)  # Store language, intent, confidence, etc.

    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    service = relationship("Service", back_populates="chat_sessions")
    user = relationship("User", back_populates="chat_messages")

    # Index for faster queries
    __table_args__ = (
        Index('idx_session_timestamp', 'session_id', 'timestamp'),
        Index('idx_service_timestamp', 'service_id', 'timestamp'),
    )

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'service_id': self.service_id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'context': self.context,
            'message_metadata': self.message_metadata,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class Product(Base):
    __tablename__ = 'products'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    service_id = Column(String(36), ForeignKey('services.id'), nullable=False, index=True)

    # Product info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float)
    image_url = Column(String(255))
    category = Column(String(100))
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    service = relationship("Service", back_populates="products")

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'service_id': self.service_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'category': self.category,
            'stock': self.stock,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class FAQ(Base):
    __tablename__ = 'faqs'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    service_id = Column(String(36), ForeignKey('services.id'), nullable=False, index=True)

    # FAQ content
    question = Column(String(500), nullable=False)
    answer = Column(Text, nullable=False)
    language = Column(String(10), default='en')  # 'en', 'si', etc.
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    service = relationship("Service", back_populates="faqs")

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'service_id': self.service_id,
            'question': self.question,
            'answer': self.answer,
            'language': self.language,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Policy(Base):
    __tablename__ = 'policies'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    service_id = Column(String(36), ForeignKey('services.id'), nullable=False, index=True)

    # Policy content
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    policy_type = Column(String(50))  # 'privacy', 'terms', 'shipping', etc.
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    service = relationship("Service", back_populates="policies")

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'service_id': self.service_id,
            'title': self.title,
            'content': self.content,
            'policy_type': self.policy_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
