"""
Auto Database Reset Script - No confirmation required
Clears MongoDB and ChromaDB completely
"""
import os
import shutil
from pymongo import MongoClient
from dotenv import load_dotenv
import chromadb
from pathlib import Path

# Load environment variables
load_dotenv()

print("\n" + "="*60)
print("🔄 AUTOMATIC DATABASE RESET")
print("="*60)

# 1. Reset MongoDB
print("\n📦 Resetting MongoDB...")
try:
    mongo_url = os.getenv('MONGODB_URL')
    db_name = os.getenv('DATABASE_NAME', 'marketmatic_service')
    
    client = MongoClient(mongo_url)
    db = client[db_name]
    
    collections = db.list_collection_names()
    print(f"   Found {len(collections)} collections")
    
    for collection_name in collections:
        db[collection_name].drop()
        print(f"   ✅ Dropped: {collection_name}")
    
    # Recreate indexes
    print("\n   Creating indexes...")
    db.users.create_index('email', unique=True)
    db.users.create_index('service_id')
    db.services.create_index('service_token', unique=True)
    db.chat_messages.create_index([('session_id', 1), ('timestamp', -1)])
    db.chat_messages.create_index('service_id')
    db.documents.create_index([('service_id', 1), ('created_at', -1)])
    db.faqs.create_index('service_id')
    db.products.create_index('service_id')
    db.policies.create_index('service_id')
    
    print("   ✅ All indexes created")
    client.close()
    print("\n✅ MongoDB reset complete!")
    
except Exception as e:
    print(f"\n❌ MongoDB reset failed: {e}")

# 2. Reset ChromaDB
print("\n🔍 Resetting ChromaDB...")
try:
    chroma_path = Path(__file__).parent / 'data' / 'chromadb'
    
    if chroma_path.exists():
        shutil.rmtree(chroma_path)
        print(f"   ✅ Deleted: {chroma_path}")
    
    chroma_path.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ Recreated: {chroma_path}")
    
    # Initialize empty ChromaDB
    client = chromadb.PersistentClient(path=str(chroma_path))
    print("   ✅ ChromaDB initialized")
    
    print("\n✅ ChromaDB reset complete!")
    
except Exception as e:
    print(f"\n❌ ChromaDB reset failed: {e}")

# 3. Verify Ollama
print("\n🦙 Checking Ollama...")
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        models = [m['name'] for m in response.json().get('models', [])]
        print(f"   ✅ Ollama running with models: {models}")
    else:
        print("   ⚠️  Ollama status unknown")
except Exception as e:
    print(f"   ⚠️  Ollama not responding: {e}")

print("\n" + "="*60)
print("🎉 DATABASE RESET COMPLETE!")
print("="*60)
print("\nNext steps:")
print("1. Restart backend: python app.py")
print("2. Create superadmin: python create_superadmin.py")
print("3. Login and start fresh!")
print("="*60 + "\n")
