"""
Test script for Modal SinLlama deployment
Run this after deploying to Modal to verify endpoints
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EMBEDDING_URL = os.getenv('MODAL_EMBEDDING_URL', '')
CHAT_URL = os.getenv('MODAL_CHAT_URL', '')


def test_embedding():
    """Test embedding generation"""
    print("\n" + "="*60)
    print("Testing Embedding Generation")
    print("="*60)
    
    if not EMBEDDING_URL:
        print("❌ MODAL_EMBEDDING_URL not set in .env file")
        return False
    
    test_texts = [
        "What products do you sell?",
        "අපේ කඩේ විකුණන භාණ්ඩ මොනවාද?",
        "මේ products වල price එක කීයද?"
    ]
    
    for text in test_texts:
        try:
            response = requests.post(
                EMBEDDING_URL,
                json={"text": text},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            embedding = result.get('embedding', [])
            print(f"\n✅ Text: {text}")
            print(f"   Embedding dimensions: {len(embedding)}")
            print(f"   First 5 values: {embedding[:5]}")
            
        except Exception as e:
            print(f"\n❌ Error with text '{text}': {str(e)}")
            return False
    
    return True


def test_chat():
    """Test chat with SinLlama"""
    print("\n" + "="*60)
    print("Testing Chat with SinLlama Model")
    print("="*60)
    
    if not CHAT_URL:
        print("❌ MODAL_CHAT_URL not set in .env file")
        return False
    
    test_cases = [
        {
            "query": "What products do you sell?",
            "context": """
Our shop sells:
- T-shirts: Rs. 1500
- Jeans: Rs. 3500
- Shoes: Rs. 4500
- Bags: Rs. 2000

We accept cash and card payments.
Delivery available within Colombo.
            """,
            "language": "en"
        },
        {
            "query": "අපේ කඩේ විකුණන භාණ්ඩ මොනවාද?",
            "context": """
අපේ කඩේ විකුණන භාණ්ඩ:
- ටී ෂර්ට්: රු. 1500
- ජීන්ස්: රු. 3500
- සපත්තු: රු. 4500
- බෑග්: රු. 2000

අපි මුදල් සහ කාඩ් ගෙවීම් භාර ගන්නවා.
කොළඹ තුල බෙදාහැරීම් තියෙනවා.
            """,
            "language": "si"
        },
        {
            "query": "Do you have delivery service?",
            "context": """
Delivery Information:
- Free delivery for orders above Rs. 5000
- Delivery within Colombo: Rs. 300
- Delivery outside Colombo: Rs. 500
- Delivery time: 2-3 business days
            """,
            "language": "en"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"\n--- Test Case {i} ---")
            print(f"Query: {test_case['query']}")
            print(f"Language: {test_case['language']}")
            
            response = requests.post(
                CHAT_URL,
                json=test_case,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"\n✅ Response: {result.get('response', '')}")
            
        except Exception as e:
            print(f"\n❌ Error with test case {i}: {str(e)}")
            return False
    
    return True


def test_conversation_history():
    """Test chat with conversation history"""
    print("\n" + "="*60)
    print("Testing Conversation History")
    print("="*60)
    
    if not CHAT_URL:
        print("❌ MODAL_CHAT_URL not set in .env file")
        return False
    
    conversation_history = [
        {"role": "user", "content": "What products do you sell?"},
        {"role": "assistant", "content": "We sell t-shirts, jeans, shoes, and bags."}
    ]
    
    try:
        response = requests.post(
            CHAT_URL,
            json={
                "query": "What are the prices?",
                "context": """
Product Prices:
- T-shirts: Rs. 1500
- Jeans: Rs. 3500
- Shoes: Rs. 4500
- Bags: Rs. 2000
                """,
                "conversation_history": conversation_history,
                "language": "en"
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"Query: What are the prices?")
        print(f"✅ Response: {result.get('response', '')}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Modal SinLlama Deployment Test Suite")
    print("="*60)
    
    if not EMBEDDING_URL or not CHAT_URL:
        print("\n⚠️  Modal URLs not configured!")
        print("\nPlease deploy your Modal service first:")
        print("  modal deploy modal_rag_service.py")
        print("\nThen copy the URLs to your .env file:")
        print("  MODAL_EMBEDDING_URL=https://...")
        print("  MODAL_CHAT_URL=https://...")
        return
    
    print(f"\n📍 Embedding URL: {EMBEDDING_URL}")
    print(f"📍 Chat URL: {CHAT_URL}")
    
    # Run tests
    results = {
        "Embedding": test_embedding(),
        "Chat": test_chat(),
        "Conversation History": test_conversation_history()
    }
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Your Modal service is working correctly.")
        print("\nNext steps:")
        print("1. Start your Flask backend: python app.py")
        print("2. Upload business documents via admin panel")
        print("3. Test the chatbot via API or frontend")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
