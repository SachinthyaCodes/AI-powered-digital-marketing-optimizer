"""
Quick verification script to test Supabase connection
"""
import os
from dotenv import load_dotenv
from database import engine, SessionLocal
from models.sqlalchemy_models import User, Service, Document, DocumentEmbedding
from sqlalchemy import inspect, text

load_dotenv()

print("=" * 60)
print("🔍 SUPABASE CONNECTION VERIFICATION")
print("=" * 60)

try:
    # Test connection
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✅ Database connection successful")
    
    # Verify tables exist
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\n📊 Tables in database ({len(tables)}):")
    for table in sorted(tables):
        print(f"   - {table}")
    
    # Test ORM with a query
    db = SessionLocal()
    user_count = db.query(User).count()
    print(f"\n👥 User records: {user_count}")
    
    service_count = db.query(Service).count()
    print(f"🤖 Service records: {service_count}")
    
    document_count = db.query(Document).count()
    print(f"📄 Document records: {document_count}")
    
    embedding_count = db.query(DocumentEmbedding).count()
    print(f"🔢 Embedding records: {embedding_count}")
    
    db.close()
    
    print("\n" + "=" * 60)
    print("✅ VERIFICATION COMPLETE - SYSTEM READY!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Verification failed: {e}")
    import traceback
    traceback.print_exc()
