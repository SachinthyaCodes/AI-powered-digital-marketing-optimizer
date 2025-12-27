#!/usr/bin/env python3
"""
Test Document Upload API
Tests the fixed document upload endpoint with proper authentication
"""
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# Test document upload
def test_document_upload():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Document Upload API...")
    
    # First, let's login to get a token
    print("\n1. Testing login to get authentication token...")
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code != 200:
        # Try to create admin user first
        print("   Creating admin user...")
        signup_data = {
            "email": "admin@test.com",
            "password": "admin123",
            "full_name": "Test Admin",
            "company_name": "Test Company",
            "role": "admin"
        }
        signup_response = requests.post(f"{base_url}/api/auth/signup", json=signup_data)
        if signup_response.status_code == 201:
            token = signup_response.json().get('token')
            print("   ✅ Admin user created and logged in")
        else:
            print(f"   ❌ Failed to create admin user: {signup_response.text}")
            return
    else:
        token = response.json().get('token')
        print("   ✅ Login successful")
    
    # Now test document upload
    print("\n2. Testing document upload...")
    
    # Create a test file
    test_content = """
    MarketMatic Product Information
    
    Q: What is MarketMatic?
    A: MarketMatic is an AI-powered chatbot platform designed for small businesses. 
    It provides intelligent customer support, document management, and automated response systems.
    
    Q: What features does MarketMatic offer?
    A: MarketMatic offers:
    - AI-powered chatbots with A10 GPU acceleration
    - Document upload and processing for FAQs, products, policies
    - Vector database integration for semantic search
    - Multi-SME support for multiple businesses
    - Real-time chat interface
    - Admin dashboard for bot management
    
    Q: How does the document processing work?
    A: Documents are automatically processed, chunked, and converted to embeddings using our A10 GPU Modal service.
    These embeddings are stored in ChromaDB for fast semantic search and retrieval.
    """
    
    # Create temporary file
    test_file_path = "test_faq_document.txt"
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        # Upload the document
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_faq_document.txt', f, 'text/plain')}
            data = {'document_type': 'faq'}
            
            response = requests.post(
                f"{base_url}/api/documents/upload",
                files=files,
                data=data,
                headers=headers
            )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Document upload successful!")
            print(f"   📄 Document ID: {result.get('document_id')}")
            print(f"   🧠 Chunks processed: {result.get('chunks_count', 'N/A')}")
        else:
            print(f"   ❌ Document upload failed: {response.text}")
            
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
    
    print("\n🏁 Document upload test completed!")

if __name__ == "__main__":
    test_document_upload()