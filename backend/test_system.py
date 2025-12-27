"""
Test the complete chatbot system to verify all fixes
"""
import requests
import json

def test_backend_health():
    """Test if the Flask backend is running and healthy"""
    try:
        # Test a known endpoint instead of /health
        response = requests.get('http://127.0.0.1:5000/', timeout=5)
        if response.status_code in [200, 404]:  # 404 is fine, means server is running
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend unexpected status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not reachable: {e}")
        return False

def test_modal_service():
    """Test if Modal service endpoints are accessible"""
    try:
        # Test embedding endpoint
        embed_url = 'https://sanudasandipa29--marketmatic-rag-embed.modal.run'
        response = requests.post(
            embed_url,
            json={'text': 'Hello test'},
            timeout=30
        )
        print(f"🔧 Modal embedding service status: {response.status_code}")
        
        # Test chat endpoint  
        chat_url = 'https://sanudasandipa29--marketmatic-rag-chat.modal.run'
        response = requests.post(
            chat_url,
            json={
                'query': 'Hello',
                'context': 'Test context for the chatbot response',
                'language': 'en'
            },
            timeout=60
        )
        print(f"🔧 Modal chat service status: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"⚠️  Modal service test: {e}")
        return False

def test_chatbot_integration():
    """Test the complete chatbot integration"""
    try:
        base_url = 'http://127.0.0.1:5000/api/rag'
        service_token = 'demo_freshmart_token_2025'
        
        # Test welcome message
        print("\n🤖 Testing welcome message...")
        response = requests.post(
            f'{base_url}/welcome',
            json={'service_token': service_token},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Welcome message: {data.get('welcome_message', '')[:100]}...")
        else:
            print(f"❌ Welcome failed: {response.status_code}")
            
        # Test chat
        print("\n💬 Testing chat...")
        response = requests.post(
            f'{base_url}/chat',
            json={
                'service_token': service_token,
                'message': 'What products do you sell?'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat response: {data.get('response', '')[:100]}...")
            print(f"   Language: {data.get('language', 'Unknown')}")
            print(f"   Model: {data.get('model', 'Unknown')}")
        else:
            print(f"❌ Chat failed: {response.status_code} - {response.text}")
            
        return True
    except Exception as e:
        print(f"❌ Chatbot test error: {e}")
        return False

def main():
    print("🚀 Testing MarketMatic Chatbot System")
    print("=" * 50)
    
    # Test backend health
    if not test_backend_health():
        print("\n❌ Backend not running. Start with: python app.py")
        return
    
    # Test Modal service
    print("\n🔧 Testing Modal service...")
    test_modal_service()
    
    # Test chatbot integration
    print("\n🤖 Testing chatbot integration...")
    test_chatbot_integration()
    
    print("\n" + "=" * 50)
    print("🎉 System test complete!")
    print("\nTo test the frontend:")
    print("1. cd ../frontend")
    print("2. npm run dev") 
    print("3. Visit http://localhost:3000/demo")
    print("4. Click the green chatbot widget")

if __name__ == "__main__":
    main()