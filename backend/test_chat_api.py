#!/usr/bin/env python3
"""
Test the chat API endpoint
"""
import requests
import json

def test_chat_api():
    """Test the chat API endpoint"""
    print("🧪 Testing Chat API Endpoint")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    # Test data
    chat_data = {
        "message": "What is MarketMatic?",
        "language": "en"
    }
    
    try:
        # Make request to chat endpoint
        response = requests.post(
            f"{base_url}/api/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat API working!")
            print(f"Response: {result.get('response', 'No response')}")
            print(f"Language: {result.get('language', 'Unknown')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server")
        print("Make sure the backend is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chat_api()