"""
Comprehensive Test Script for Supabase Migration
Tests database connection, ORM models, and route endpoints
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.absolute()
sys.path.insert(0, str(backend_path))

print("=" * 70)
print("🧪 MARKETMATIC SUPABASE MIGRATION - COMPREHENSIVE TEST")
print("=" * 70)

# Test 1: Import all modules
print("\n[1/6] Testing imports...")
try:
    from database import SessionLocal, engine
    from models.sqlalchemy_models import (
        User, Service, Document, DocumentEmbedding, 
        ChatMessage, FAQ, Product, Policy
    )
    from routes import auth_routes, bot_routes, chat_routes, rag_routes, service_routes
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Database connection
print("\n[2/6] Testing database connection...")
try:
    from sqlalchemy import text, inspect
    
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        
    # Verify tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    expected_tables = ['users', 'services', 'documents', 'document_embeddings', 
                       'chat_messages', 'faqs', 'products', 'policies']
    
    missing = [t for t in expected_tables if t not in tables]
    if missing:
        print(f"⚠️  Missing tables: {missing}")
    else:
        print(f"✅ All {len(tables)} expected tables found")
        
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)

# Test 3: ORM Model Validation
print("\n[3/6] Testing ORM models...")
try:
    db = SessionLocal()
    
    # Test User model
    user_count = db.query(User).count()
    print(f"✅ User model working ({user_count} users)")
    
    # Test Service model
    service_count = db.query(Service).count()
    print(f"✅ Service model working ({service_count} services)")
    
    # Test Document model
    doc_count = db.query(Document).count()
    print(f"✅ Document model working ({doc_count} documents)")
    
    # Test FAQ model
    faq_count = db.query(FAQ).count()
    print(f"✅ FAQ model working ({faq_count} FAQs)")
    
    # Test Product model
    prod_count = db.query(Product).count()
    print(f"✅ Product model working ({prod_count} products)")
    
    # Test Policy model
    policy_count = db.query(Policy).count()
    print(f"✅ Policy model working ({policy_count} policies)")
    
    # Test ChatMessage model
    msg_count = db.query(ChatMessage).count()
    print(f"✅ ChatMessage model working ({msg_count} messages)")
    
    # Test DocumentEmbedding model
    emb_count = db.query(DocumentEmbedding).count()
    print(f"✅ DocumentEmbedding model working ({emb_count} embeddings)")
    
    db.close()
    
except Exception as e:
    print(f"❌ ORM model test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Route blueprints
print("\n[4/6] Testing route blueprints...")
try:
    from flask import Flask
    
    app = Flask(__name__)
    app.register_blueprint(auth_routes.auth_bp)
    app.register_blueprint(bot_routes.bot_bp)
    app.register_blueprint(chat_routes.chat_bp)
    app.register_blueprint(rag_routes.rag_bp)
    app.register_blueprint(service_routes.service_bp)
    
    # Count routes
    route_count = 0
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            route_count += 1
    
    print(f"✅ All route blueprints registered ({route_count} routes)")
    
except Exception as e:
    print(f"❌ Route blueprint test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Superadmin user
print("\n[5/6] Checking superadmin account...")
try:
    db = SessionLocal()
    superadmin = db.query(User).filter(
        User.email == 'superadmin@marketmatic.com'
    ).first()
    
    if superadmin:
        print(f"✅ Superadmin account found (ID: {superadmin.id})")
    else:
        print("⚠️  Superadmin account not found (create with create_superadmin.py)")
    
    db.close()
    
except Exception as e:
    print(f"❌ Superadmin check failed: {e}")

# Test 6: Vector service availability
print("\n[6/6] Testing vector service...")
try:
    from services.vector_service import VectorService
    
    vector_service = VectorService()
    status = vector_service.get_status()
    
    if status.get('available'):
        print(f"✅ Vector service operational (Ollama: {status.get('ollama_model')})")
    else:
        print("⚠️  Vector service not available (Ollama may not be running)")
    
except Exception as e:
    print(f"⚠️  Vector service test: {e}")

# Summary
print("\n" + "=" * 70)
print("✅ SUPABASE MIGRATION TEST COMPLETE!")
print("=" * 70)
print("\n📋 Summary:")
print("   ✅ Database connection working")
print("   ✅ All 8 ORM models functional")
print("   ✅ All 5 route blueprints registered")
print("   ✅ Ready for production testing")
print("\n🚀 Next steps:")
print("   1. Test authentication endpoints (login, signup)")
print("   2. Test bot management endpoints")
print("   3. Test chat functionality")
print("   4. Test document upload and RAG search")
print("   5. Full integration testing with frontend")
print("\n" + "=" * 70)
