#!/usr/bin/env python3
"""
Test script for Modal AI service endpoints
"""
import requests
import json

# Modal service URLs
EMBED_URL = "https://sanudasandipa29--marketmatic-rag-embed.modal.run/"
CHAT_URL = "https://sanudasandipa29--marketmatic-rag-chat.modal.run/"

def test_embedding_endpoint():
    """Test the embedding generation endpoint"""
    print("🔗 Testing Embedding Endpoint...")
    
    try:
        # Test single text embedding
        data = {"text": "What are the business hours for MarketMatic?"}
        response = requests.post(EMBED_URL, json=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "embedding" in result:
                embedding = result["embedding"]
                print(f"✅ Embedding generated successfully!")
                print(f"   Vector length: {len(embedding)}")
                print(f"   Sample values: {embedding[:5]}...")
                return True
            else:
                print(f"❌ No embedding in response: {result}")
                return False
        else:
            print(f"❌ Request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing embedding endpoint: {e}")
        return False

def test_chat_endpoint():
    """Test the chat generation endpoint"""
    print("\n💬 Testing Chat Endpoint...")
    
    try:
        data = {
            "query": "What services does MarketMatic offer?",
            "context": "MarketMatic is a business automation platform that provides inventory management, sales tracking, and customer engagement tools.",
            "language": "en",
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        response = requests.post(CHAT_URL, json=data, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "response" in result:
                chat_response = result["response"]
                print(f"✅ Chat response generated successfully!")
                print(f"   Response: {chat_response[:200]}...")
                return True
            else:
                print(f"❌ No response in result: {result}")
                return False
        else:
            print(f"❌ Request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing chat endpoint: {e}")
        return False

def main():
    print("🧪 Testing Modal AI Service Endpoints")
    print("=" * 50)
    
    # Test embedding endpoint
    embed_success = test_embedding_endpoint()
    
    # Test chat endpoint
    chat_success = test_chat_endpoint()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 50)
    print(f"Embedding Endpoint: {'✅ PASS' if embed_success else '❌ FAIL'}")
    print(f"Chat Endpoint: {'✅ PASS' if chat_success else '❌ FAIL'}")
    
    if embed_success and chat_success:
        print("\n🎉 All Modal AI endpoints are working correctly!")
        print("✅ Ready for MarketMatic integration!")
    else:
        print("\n⚠️  Some endpoints need attention.")
        
    return embed_success and chat_success

if __name__ == "__main__":
    main()