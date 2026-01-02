"""
Quick test script for Ollama RAG system
Run this to verify everything is working
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 80)
print("OLLAMA RAG SYSTEM TEST")
print("=" * 80)

# Test 1: Check Ollama connection
print("\n[1/5] Testing Ollama connection...")
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f"✅ Ollama is running")
        print(f"   Models: {[m['name'] for m in models]}")
    else:
        print("❌ Ollama returned unexpected response")
        sys.exit(1)
except Exception as e:
    print(f"❌ Ollama not running: {e}")
    print("   Please run: ollama serve")
    sys.exit(1)

# Test 2: Import RAG service
print("\n[2/5] Importing RAG service...")
try:
    from services.ollama_rag_service import OllamaRAGService
    print("✅ RAG service imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 3: Initialize RAG service
print("\n[3/5] Initializing RAG service...")
try:
    rag = OllamaRAGService('test-service')
    print("✅ RAG service initialized")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Get status
print("\n[4/5] Getting system status...")
try:
    status = rag.get_status()
    print("✅ Status retrieved:")
    print(f"   Service ID: {status['service_id']}")
    print(f"   Embedding Dimension: {status['embedding_dim']}")
    print(f"   Ollama Available: {status['ollama_available']}")
    print(f"   Number of Chunks: {status['num_chunks']}")
except Exception as e:
    print(f"❌ Status check failed: {e}")
    sys.exit(1)

# Test 5: Test chunking and FAQ extraction
print("\n[5/5] Testing text processing...")
try:
    test_text = """
Q: What is your return policy?
A: We accept returns within 30 days of purchase with original receipt.

Q: How long does shipping take?
A: Standard shipping takes 5-7 business days within the US.

This is additional context about our services. We provide excellent customer support.
"""
    
    # Test chunking
    chunks = rag.rag_system.chunk_document(test_text, metadata={'test': True})
    print(f"✅ Text chunking working: {len(chunks)} chunks created")
    
    # Test FAQ extraction
    faqs = rag.extract_faqs_from_text(test_text)
    print(f"✅ FAQ extraction working: {len(faqs)} FAQs found")
    for i, faq in enumerate(faqs, 1):
        print(f"   FAQ {i}: {faq['question'][:50]}...")
    
except Exception as e:
    print(f"❌ Processing failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED! Ollama RAG system is ready!")
print("=" * 80)
print("\nNext steps:")
print("1. Start backend: cd backend && python start_server.py")
print("2. Test endpoint: curl http://localhost:5000/api/rag/test")
print("3. Upload documents via API")
print("\=" * 80)
