"""
Complete Database Reset Script
Clears MongoDB collections and ChromaDB vector database, then recreates them
"""
import os
import shutil
from pymongo import MongoClient
from dotenv import load_dotenv
import chromadb
from pathlib import Path

# Load environment variables
load_dotenv()

def reset_mongodb():
    """Clear all MongoDB collections"""
    print("\n" + "="*60)
    print("RESETTING MONGODB")
    print("="*60)
    
    try:
        # Connect to MongoDB
        mongo_url = os.getenv('MONGODB_URL')
        db_name = os.getenv('DATABASE_NAME', 'marketmatic_service')
        
        client = MongoClient(mongo_url)
        db = client[db_name]
        
        # Get all collections
        collections = db.list_collection_names()
        print(f"\nFound {len(collections)} collections")
        
        # Drop each collection
        for collection_name in collections:
            print(f"  Dropping: {collection_name}")
            db[collection_name].drop()
        
        print("\n✅ MongoDB cleared successfully!")
        
        # Recreate essential indexes
        print("\nRecreating indexes...")
        
        # Users collection indexes
        db.users.create_index('email', unique=True)
        db.users.create_index('service_id')
        print("  ✅ Users indexes created")
        
        # Services collection indexes
        db.services.create_index('service_token', unique=True)
        print("  ✅ Services indexes created")
        
        # Chat messages indexes
        db.chat_messages.create_index([('session_id', 1), ('timestamp', -1)])
        db.chat_messages.create_index('service_id')
        print("  ✅ Chat messages indexes created")
        
        # Documents indexes
        db.documents.create_index([('service_id', 1), ('created_at', -1)])
        print("  ✅ Documents indexes created")
        
        # FAQs, Products, Policies indexes
        db.faqs.create_index('service_id')
        db.products.create_index('service_id')
        db.policies.create_index('service_id')
        print("  ✅ Content indexes created")
        
        print("\n✅ All indexes recreated!")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error resetting MongoDB: {e}")
        return False


def reset_chromadb():
    """Clear ChromaDB vector database"""
    print("\n" + "="*60)
    print("RESETTING CHROMADB")
    print("="*60)
    
    try:
        # Path to ChromaDB data
        chroma_path = Path(__file__).parent / 'data' / 'chromadb'
        
        if chroma_path.exists():
            print(f"\nDeleting ChromaDB directory: {chroma_path}")
            shutil.rmtree(chroma_path)
            print("✅ ChromaDB directory deleted")
        else:
            print(f"\n⚠️  ChromaDB directory not found: {chroma_path}")
        
        # Recreate empty directory
        chroma_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ ChromaDB directory recreated: {chroma_path}")
        
        # Initialize new ChromaDB
        client = chromadb.PersistentClient(path=str(chroma_path))
        print("✅ ChromaDB initialized with empty database")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error resetting ChromaDB: {e}")
        return False


def verify_ollama():
    """Verify Ollama is running"""
    print("\n" + "="*60)
    print("VERIFYING OLLAMA")
    print("="*60)
    
    try:
        import requests
        
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            print("\n✅ Ollama is running!")
            print(f"📦 Available models: {model_names}")
            
            # Check for required models
            has_llama3 = any('llama3' in name for name in model_names)
            has_nomic = any('nomic-embed-text' in name for name in model_names)
            
            if has_llama3 and has_nomic:
                print("✅ All required models present (llama3, nomic-embed-text)")
                return True
            else:
                print("\n⚠️  Missing required models!")
                if not has_llama3:
                    print("   Missing: llama3")
                    print("   Run: ollama pull llama3")
                if not has_nomic:
                    print("   Missing: nomic-embed-text")
                    print("   Run: ollama pull nomic-embed-text")
                return False
        else:
            print(f"❌ Ollama returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Ollama is not running!")
        print(f"   Error: {e}")
        print("   Start Ollama with: ollama serve")
        return False


def main():
    """Main reset function"""
    print("\n" + "="*60)
    print("MARKETMATIC DATABASE RESET")
    print("="*60)
    print("\n⚠️  WARNING: This will delete ALL data!")
    print("   - All MongoDB collections")
    print("   - All ChromaDB vectors")
    print("   - All chat history")
    print("   - All documents and embeddings")
    
    confirm = input("\nType 'YES' to continue: ")
    
    if confirm != 'YES':
        print("\n❌ Reset cancelled")
        return
    
    # Verify Ollama first
    print("\n" + "="*60)
    print("STEP 1: VERIFY OLLAMA")
    print("="*60)
    ollama_ok = verify_ollama()
    
    if not ollama_ok:
        print("\n⚠️  Ollama issues detected. Continue anyway?")
        confirm2 = input("Type 'YES' to continue: ")
        if confirm2 != 'YES':
            print("\n❌ Reset cancelled")
            return
    
    # Reset MongoDB
    print("\n" + "="*60)
    print("STEP 2: RESET MONGODB")
    print("="*60)
    mongo_ok = reset_mongodb()
    
    # Reset ChromaDB
    print("\n" + "="*60)
    print("STEP 3: RESET CHROMADB")
    print("="*60)
    chroma_ok = reset_chromadb()
    
    # Summary
    print("\n" + "="*60)
    print("RESET SUMMARY")
    print("="*60)
    print(f"MongoDB:  {'✅ Success' if mongo_ok else '❌ Failed'}")
    print(f"ChromaDB: {'✅ Success' if chroma_ok else '❌ Failed'}")
    print(f"Ollama:   {'✅ Running' if ollama_ok else '⚠️  Issues'}")
    
    if mongo_ok and chroma_ok:
        print("\n🎉 Database reset complete!")
        print("\nNext steps:")
        print("1. Restart the backend server:")
        print("   python app.py")
        print("\n2. Create a new superadmin (if needed):")
        print("   python create_superadmin.py")
        print("\n3. Login and start fresh!")
    else:
        print("\n⚠️  Reset completed with errors. Check logs above.")


if __name__ == '__main__':
    main()
