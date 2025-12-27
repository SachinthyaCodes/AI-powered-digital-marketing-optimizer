"""
Supabase Setup and Database Initialization
Replaces MongoDB and ChromaDB with PostgreSQL + pgvector
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text

# Load environment
load_dotenv()

# Get database connection
try:
    from database import engine, SessionLocal, init_db
    from models.sqlalchemy_models import User, Service, Document, DocumentEmbedding, ChatMessage, Product, FAQ, Policy
    
    print("\n" + "="*70)
    print("🚀 SUPABASE DATABASE SETUP")
    print("="*70)
    
    # Test connection
    print("\n📡 Testing Supabase connection...")
    from database import test_connection
    if not test_connection():
        print("❌ Failed to connect to Supabase")
        print("\nPlease ensure:")
        print("1. Supabase project is created at https://supabase.com")
        print("2. DATABASE_URL is set in .env")
        print("3. Connection string format: postgresql://postgres:PASSWORD@HOST:5432/postgres")
        sys.exit(1)
    
    # Initialize database
    print("\n📦 Creating database tables and indexes...")
    if not init_db():
        print("❌ Failed to initialize database")
        sys.exit(1)
    
    # Create superadmin user
    print("\n👤 Creating superadmin account...")
    from models.sqlalchemy_models import User
    
    db = SessionLocal()
    
    # Check if superadmin exists
    existing_admin = db.query(User).filter(User.email == 'superadmin@marketmatic.com').first()
    if existing_admin:
        print("⚠️  Superadmin already exists")
    else:
        superadmin = User(
            email='superadmin@marketmatic.com',
            password=User.hash_password('superadmin'),
            full_name='System Administrator',
            role='superadmin'
        )
        db.add(superadmin)
        db.commit()
        print(f"✅ Superadmin created: {superadmin.id}")
    
    db.close()
    
    # Verify pgvector
    print("\n🔍 Verifying pgvector extension...")
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT version FROM pg_extension WHERE extname='vector'"))
        version = result.scalar()
        print(f"✅ pgvector extension active (version: {version})")
    except:
        print("⚠️  pgvector extension not found - it will be created automatically")
    db.close()
    
    # Show connection info
    print("\n" + "="*70)
    print("✅ SUPABASE SETUP COMPLETE!")
    print("="*70)
    print("\n📊 Database Information:")
    print(f"   Database: Supabase PostgreSQL with pgvector")
    print(f"   Tables: 8 (users, services, documents, embeddings, chat_messages, products, faqs, policies)")
    print(f"   Vector Dimension: 768 (nomic-embed-text)")
    print(f"   Embedding Model: Ollama llama3")
    
    print("\n🔑 Superadmin Credentials:")
    print(f"   Email: superadmin@marketmatic.com")
    print(f"   Password: superadmin")
    
    print("\n📝 Next Steps:")
    print("   1. Update .env with your Supabase DATABASE_URL")
    print("   2. Install dependencies: pip install -r requirements.txt")
    print("   3. Start backend: python app.py")
    print("   4. Login with superadmin credentials")
    
    print("\n" + "="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ Setup failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
