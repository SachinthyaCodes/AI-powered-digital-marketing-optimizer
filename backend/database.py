"""
Supabase PostgreSQL Database Connection and Session Management
Replaces MongoDB with SQLAlchemy ORM
Supports SQLite for local development and PostgreSQL for production
"""
import os
import urllib.parse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, StaticPool
from dotenv import load_dotenv
from models.sqlalchemy_models import Base

# Load environment variables
load_dotenv()

# Determine database backend
USE_SQLITE = os.getenv('USE_SQLITE', 'true').lower() == 'true'

if USE_SQLITE:
    # SQLite for local development
    DATABASE_URL = 'sqlite:///./test.db'
    engine_kwargs = {
        'echo': False,
        'connect_args': {'check_same_thread': False},
        'poolclass': StaticPool,  # StaticPool for SQLite
    }
else:
    # PostgreSQL for production
    # First try to use DATABASE_URL directly from .env
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        # Fallback to building from components
        db_host = os.getenv('DB_HOST', 'db.fhzrfzxrxvirydkeetme.supabase.co')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'postgres')
        
        if db_password:
            # URL encode the password for safety
            encoded_password = urllib.parse.quote(db_password, safe='')
            DATABASE_URL = f'postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}'
        else:
            raise ValueError(
                "Missing database credentials for PostgreSQL. "
                "Set DATABASE_URL or individual DB_* variables in .env"
            )
    
    engine_kwargs = {
        'echo': False,
        'poolclass': NullPool,
        'connect_args': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'
        }
    }

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Session:
    """
    Get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database: create all tables and enable pgvector
    Run this once at startup
    """
    try:
        # Enable pgvector extension
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized - all tables created")
        print("✅ pgvector extension enabled")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def drop_all_tables():
    """
    Drop all tables - CAREFUL! Used for development/testing
    """
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped")
        return True
    except Exception as e:
        print(f"❌ Failed to drop tables: {e}")
        return False

def reset_database():
    """
    Complete database reset: drop and recreate all tables
    """
    if drop_all_tables():
        if init_db():
            print("✅ Database reset complete")
            return True
    return False

def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Supabase PostgreSQL connection successful")
            return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

# Legacy compatibility - keep for old code
db_instance = None
