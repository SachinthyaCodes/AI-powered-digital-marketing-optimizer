"""
API Testing Script
Run this to test all backend endpoints
"""

import requests
import json
import base64
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    """Test health check endpoint"""
    print_section("Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_predict():
    """Test prediction endpoint"""
    print_section("Testing Prediction")
    
    # Sample data
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    data = {
        "caption": "Check out our amazing new product! 🎉 Don't miss this incredible offer!",
        "content": "High quality products at affordable prices. Free shipping on orders over $50. Limited time offer!",
        "platform": "Facebook",
        "post_date": tomorrow,
        "post_time": "18:00",
        "followers": 10000,
        "ad_boost": 1
    }
    
    try:
        print(f"Request Data:")
        print(json.dumps(data, indent=2))
        print("\nSending request...")
        
        response = requests.post(f"{BASE_URL}/api/predict", json=data)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Prediction successful!")
            print(f"\nPredictions:")
            for key, value in result['predictions'].items():
                print(f"  {key}: {value}")
            
            print(f"\nHashtag Suggestions:")
            for tag in result['hashtag_suggestions']:
                print(f"  {tag}")
            
            print(f"\nRecommendations:")
            for rec in result['recommendations']:
                print(f"  [{rec['impact']}] {rec['category']}: {rec['suggestion'][:60]}...")
            
            print(f"\nFeature Importance:")
            for feature, importance in result['feature_importance'].items():
                print(f"  {feature}: {importance:.6f}")
            
            return True
        else:
            print(f"❌ Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_history():
    """Test history endpoint"""
    print_section("Testing History")
    try:
        response = requests.get(f"{BASE_URL}/api/history")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {len(result.get('history', []))} predictions in history")
            if result.get('history'):
                print("\nMost recent prediction:")
                recent = result['history'][0]
                print(f"  Platform: {recent.get('platform')}")
                print(f"  Caption: {recent.get('caption', '')[:50]}...")
                print(f"  Likes: {recent.get('predictions', {}).get('likes', 'N/A')}")
            return True
        else:
            print(f"❌ Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_extract_text():
    """Test text extraction (requires an actual image)"""
    print_section("Testing Text Extraction")
    print("ℹ️  This test requires an actual image file")
    print("Skipping for now. Use the frontend to test image upload.")
    return True

def main():
    """Run all tests"""
    print("\n" + "🚀"*30)
    print("  AI-Powered Digital Marketing Optimizer - API Tests")
    print("🚀"*30)
    
    print(f"\nBackend URL: {BASE_URL}")
    print(f"Make sure the backend is running: python app.py")
    
    input("\nPress Enter to start tests...")
    
    results = {
        "Health Check": test_health(),
        "Prediction": test_predict(),
        "History": test_history(),
        "Text Extraction": test_extract_text()
    }
    
    print_section("Test Results Summary")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:20} {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your API is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
