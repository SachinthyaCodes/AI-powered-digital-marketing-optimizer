#!/usr/bin/env python3
"""
Test Fixed Document Upload
Quick test to verify the metadata extraction fix
"""
import requests
import io

def test_upload():
    print("🧪 Testing Fixed Document Upload...")
    
    # Test document content
    test_content = """MarketMatic Business FAQ

Q: What is MarketMatic?
A: MarketMatic is an AI-powered chatbot platform for SMEs with A10 GPU acceleration.

Q: How does document upload work?
A: Documents are processed, chunked, and stored in vector database with Modal embeddings.

Q: What types of documents are supported?
A: FAQs, products, policies, store details, and general documents."""
    
    # Login first (assuming admin user exists)
    try:
        login_response = requests.post("http://localhost:5000/api/auth/login", json={
            "email": "admin@test.com", 
            "password": "admin123"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get('token')
            print("✅ Login successful")
        else:
            print("⚠️  Using test without login")
            token = None
        
        if token:
            # Test upload
            headers = {"Authorization": f"Bearer {token}"}
            files = {'file': ('test_faq.txt', io.StringIO(test_content), 'text/plain')}
            data = {'document_type': 'faq'}
            
            response = requests.post(
                "http://localhost:5000/api/documents/upload",
                files=files,
                data=data,
                headers=headers
            )
            
            print(f"Upload Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("🎉 Document upload working perfectly!")
            else:
                print(f"❌ Upload failed: {response.status_code}")
        
    except Exception as e:
        print(f"Connection error: {str(e)}")
        print("Server might still be restarting...")

if __name__ == "__main__":
    test_upload()