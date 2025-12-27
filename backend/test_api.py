#!/usr/bin/env python3
"""
Quick API test script to verify backend endpoints are working
"""
import requests
import json

BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

def test_endpoint(method, endpoint, data=None, headers=None):
    """Test an API endpoint"""
    if headers is None:
        headers = HEADERS
    
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            resp = requests.post(url, json=data, headers=headers, timeout=5)
        else:
            return None
        
        return {
            'status': resp.status_code,
            'data': resp.json() if resp.text else None,
            'error': None
        }
    except Exception as e:
        return {
            'status': None,
            'data': None,
            'error': str(e)
        }

def main():
    print("\n" + "="*70)
    print("MARKETMATIC API TEST SUITE")
    print("="*70)
    
    # Test 1: Health check
    print("\n[1] Testing /api/health...")
    result = test_endpoint("GET", "/api/health")
    print(f"Status: {result['status']}")
    if result['data']:
        print(f"Response: {json.dumps(result['data'], indent=2)}")
    
    # Test 2: Home endpoint
    print("\n[2] Testing / (home)...")
    result = test_endpoint("GET", "/")
    print(f"Status: {result['status']}")
    if result['data']:
        print(f"Response: {json.dumps(result['data'], indent=2)}")
    
    # Test 3: Superadmin login
    print("\n[3] Testing /api/superadmin/login...")
    login_data = {
        "username": "superadmin",
        "password": "superadmin"
    }
    result = test_endpoint("POST", "/api/superadmin/login", login_data)
    print(f"Status: {result['status']}")
    if result['data']:
        print(f"Response: {json.dumps(result['data'], indent=2)}")
        token = result['data'].get('token')
        if token:
            print(f"\n[OK] Got authentication token: {token[:20]}...")
    else:
        print(f"Error: {result['error']}")
    
    # Test 4: Document status
    print("\n[4] Testing /api/documents/status...")
    result = test_endpoint("GET", "/api/documents/status")
    print(f"Status: {result['status']}")
    if result['data']:
        print(f"Response: {json.dumps(result['data'], indent=2)}")
    
    # Test 5: Document health
    print("\n[5] Testing /api/documents/health...")
    result = test_endpoint("GET", "/api/documents/health")
    print(f"Status: {result['status']}")
    if result['data']:
        print(f"Response: {json.dumps(result['data'], indent=2)}")
    
    # Test 6: RAG status
    print("\n[6] Testing /api/rag/status...")
    result = test_endpoint("GET", "/api/rag/status")
    print(f"Status: {result['status']}")
    if result['data']:
        print(f"Response: {json.dumps(result['data'], indent=2)}")
    
    # Test 7: RAG test
    print("\n[7] Testing /api/rag/test...")
    result = test_endpoint("GET", "/api/rag/test")
    print(f"Status: {result['status']}")
    if result['data']:
        print(f"Response: {json.dumps(result['data'], indent=2)}")
    
    # Test 8: Chat demo
    print("\n[8] Testing /api/chat/demo/message...")
    chat_data = {
        "message": "Hello, test message"
    }
    result = test_endpoint("POST", "/api/chat/demo/message", chat_data)
    print(f"Status: {result['status']}")
    if result['data']:
        print(f"Response: {json.dumps(result['data'], indent=2)}")
    
    print("\n" + "="*70)
    print("[OK] API TEST COMPLETE")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
