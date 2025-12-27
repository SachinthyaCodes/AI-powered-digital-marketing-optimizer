"""
Test the chatbot functionality with the demo service
"""
import requests
import json

def test_chatbot():
    service_token = 'demo_freshmart_token_2025'
    base_url = 'http://127.0.0.1:5000/api/rag'
    
    print("🤖 Testing FreshMart Chatbot with SinLlama")
    print("=" * 50)
    
    # Test welcome message
    print("\n1. Testing welcome message...")
    try:
        response = requests.post(f'{base_url}/welcome', 
            json={'service_token': service_token})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Welcome: {data.get('welcome_message', 'No message')[:100]}...")
        else:
            print(f"❌ Welcome failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Welcome error: {e}")
    
    # Test chat messages
    test_messages = [
        "Hello, what products do you sell?",
        "ඔබේ කඩේ මොනවද විකුණන්නේ?",
        "What are your delivery charges?",
        "බෙදාහැරීමේ ගාස්තු කීයද?",
        "How much are the apples?",
        "Store hours"
    ]
    
    session_id = None
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing: '{message}'")
        try:
            payload = {
                'service_token': service_token,
                'message': message
            }
            if session_id:
                payload['session_id'] = session_id
                
            response = requests.post(f'{base_url}/chat', json=payload)
            
            if response.status_code == 200:
                data = response.json()
                session_id = data.get('session_id')
                print(f"✅ Response: {data.get('response', 'No response')[:100]}...")
                print(f"   Language: {data.get('language', 'Unknown')}")
                print(f"   Model: {data.get('model', 'Unknown')}")
                print(f"   Context Sources: {data.get('context_sources', 0)}")
            else:
                print(f"❌ Chat failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Chat error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test complete! Check the results above.")
    print("\nTo test the frontend:")
    print("1. Open http://localhost:3000/demo")
    print("2. Click the chatbot widget (green circle with AI badge)")
    print("3. Try asking questions in English or Sinhala")
    print("\nExample questions:")
    print("• What products do you sell?")
    print("• ඔබේ මිල කීයද? (What are your prices?)")
    print("• Do you deliver?")
    print("• අපල් ටිකේ මිල කීයද? (How much are the apples?)")

if __name__ == "__main__":
    test_chatbot()