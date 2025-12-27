#!/usr/bin/env python3
"""
Basic test script to verify MarketMatic backend functionality
"""
import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def test_core_imports():
    """Test importing core backend modules"""
    print("🔍 Testing Core Backend Imports...")
    
    try:
        # Test core Flask app import
        from app import app
        print("✅ Flask app imported successfully")
        
        # Test database connection
        from database import check_connection
        print("✅ Database module imported successfully")
        
        # Test models
        from models.user import User
        from models.bot_models import Bot
        print("✅ Model classes imported successfully")
        
        # Test services
        from services.document_processor import DocumentProcessor
        print("✅ Document processor imported successfully")
        
        # Test vector service (our newly fixed one)
        from services.vector_service import VectorDatabaseService
        print("✅ Vector database service imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_vector_service():
    """Test vector database service"""
    print("\n🔍 Testing Vector Database Service...")
    
    try:
        from services.vector_service import VectorDatabaseService
        
        # Initialize service (should create ChromaDB collection)
        vector_service = VectorDatabaseService()
        print("✅ Vector service initialized successfully")
        
        # Test embedding generation (using Modal service)
        test_text = "This is a test document for MarketMatic"
        
        # Note: This will use the Modal service we deployed
        print("📡 Testing Modal embedding integration...")
        embedding = vector_service.get_embedding(test_text)
        
        if embedding and len(embedding) > 0:
            print(f"✅ Modal embedding service working! Vector length: {len(embedding)}")
            return True
        else:
            print("❌ Modal embedding service returned empty result")
            return False
            
    except Exception as e:
        print(f"❌ Vector service error: {e}")
        return False

def test_basic_flask():
    """Test basic Flask app functionality"""
    print("\n🔍 Testing Basic Flask App...")
    
    try:
        from app import app
        
        # Test Flask app configuration
        with app.app_context():
            print(f"✅ App name: {app.name}")
            print(f"✅ App config loaded: {len(app.config)} settings")
            
            # Test basic route
            with app.test_client() as client:
                response = client.get('/health')
                if response.status_code == 200:
                    print("✅ Health endpoint working")
                    return True
                else:
                    print(f"⚠️ Health endpoint returned {response.status_code}")
                    return False
                    
    except Exception as e:
        print(f"❌ Flask app error: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n🔍 Testing Environment Configuration...")
    
    try:
        # Check if .env file exists
        env_file = os.path.join(backend_dir, '.env')
        if os.path.exists(env_file):
            print("✅ .env file found")
        else:
            print("⚠️ No .env file found (using defaults)")
            
        # Check key environment variables
        from config import Config
        config = Config()
        
        print(f"✅ MongoDB URL configured: {'✅' if hasattr(config, 'MONGODB_URL') else '❌'}")
        print(f"✅ JWT Secret configured: {'✅' if hasattr(config, 'JWT_SECRET_KEY') else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment configuration error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 MarketMatic Backend Test Suite")
    print("=" * 50)
    
    # Run tests
    results = []
    results.append(("Core Imports", test_core_imports()))
    results.append(("Environment", test_environment()))
    results.append(("Flask App", test_basic_flask()))
    results.append(("Vector Service", test_vector_service()))
    
    # Print summary
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall Score: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! MarketMatic backend is ready!")
        print("✅ You can now start the Flask app with: py -3.11 app.py")
    else:
        print(f"\n⚠️  {len(results) - passed} tests failed. Check the issues above.")
        
    return passed == len(results)

if __name__ == "__main__":
    main()