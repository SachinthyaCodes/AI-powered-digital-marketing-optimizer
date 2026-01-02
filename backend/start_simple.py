"""
Simple Flask server runner for MarketMatic with SinLlama
"""
import os
import sys

# Suppress llama.cpp verbose output
os.environ['LLAMA_CPP_LOG_LEVEL'] = '2'  # Only show errors

from app import app, engine
from models.sqlalchemy_models import Base
from config import Config
from werkzeug.serving import run_simple

def initialize_database():
    """Initialize database tables if they don't exist"""
    try:
        print("[DB] Connecting to database...")
        from sqlalchemy import text
        
        # Test connection first with timeout
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        print("[OK] Database connected!")
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("[OK] Database tables ready!")
        
    except Exception as e:
        print(f"[WARN] Database connection issue: {str(e)[:100]}...")
        print("   Server will start but database features may not work")
        print("   Please check your database credentials and network connection")

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("[MarketMatic] Backend Server with SinLlama")
    print("=" * 60)
    
    # Display database info
    if Config.USE_SQLITE:
        print("[DB] Database: SQLite (Local)")
    else:
        print("[DB] Database: Supabase PostgreSQL")
    
    # Initialize database
    initialize_database()
    
    print("[Server] http://localhost:5000")
    print("[SinLlama] AI Model: SinLlama (Sinhala + English)")
    print("=" * 60 + "\n")
    
    try:
        run_simple('0.0.0.0', 5000, app, use_reloader=False, use_debugger=False)
    except KeyboardInterrupt:
        print("\n\n[EXIT] Server stopped\n")
        sys.exit(0)
