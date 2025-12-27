#!/usr/bin/env python3
"""
Quick test of core functionality after fixes
"""

def test_imports():
    """Test all critical imports"""
    try:
        from bson import ObjectId
        print("✅ BSON/ObjectId works")
        
        import pymongo
        print("✅ PyMongo works")
        
        from services.vector_service import VectorDatabaseService
        print("✅ Vector service imported")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_vector_service():
    """Test vector service functionality"""
    try:
        from services.vector_service import VectorDatabaseService
        
        # Initialize service
        vs = VectorDatabaseService()
        print("✅ Vector service initialized")
        
        # Test embedding
        embed = vs.get_embedding('test embedding for marketmatic')
        if embed and len(embed) > 0:
            print(f"✅ Embedding works: vector length {len(embed)}")
            return True
        else:
            print("❌ Embedding failed")
            return False
            
    except Exception as e:
        print(f"❌ Vector service error: {e}")
        return False

def test_flask_app():
    """Test Flask app import"""
    try:
        from app import app
        print("✅ Flask app imported")
        
        with app.app_context():
            print("✅ Flask app context works")
            return True
            
    except Exception as e:
        print(f"❌ Flask app error: {e}")
        return False

def main():
    print("🔧 Quick Test After Fixes")
    print("=" * 40)
    
    results = []
    results.append(test_imports())
    results.append(test_vector_service()) 
    results.append(test_flask_app())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All fixes successful! Backend is ready!")
    else:
        print("⚠️ Some issues remain")

if __name__ == "__main__":
    main()