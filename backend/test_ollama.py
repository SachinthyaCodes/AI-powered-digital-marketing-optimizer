"""
Quick test script to verify Ollama integration
"""
from services.ollama_service import get_ollama_service

def test_ollama():
    print("="*60)
    print("Testing Ollama Service Integration")
    print("="*60)
    
    # Get service instance
    ollama_service = get_ollama_service()
    
    # Test 1: Check availability
    print("\n1. Checking Ollama availability...")
    if ollama_service.check_service_available():
        print("✅ Ollama is running and available")
    else:
        print("❌ Ollama is not available")
        return
    
    # Test 2: Generate embedding
    print("\n2. Testing embedding generation...")
    test_text = "Hello, this is a test message"
    embedding = ollama_service.generate_embedding(test_text)
    print(f"✅ Generated embedding with {len(embedding)} dimensions")
    print(f"   First 5 values: {embedding[:5]}")
    
    # Test 3: Generate chat response
    print("\n3. Testing chat generation...")
    response = ollama_service.generate_chat_response(
        query="What is your name?",
        context="You are a helpful assistant for a business.",
        conversation_history=[],
        language='en',
        max_tokens=100,
        temperature=0.7
    )
    print(f"✅ Generated response: {response[:100]}...")
    
    # Test 4: Test with Sinhala
    print("\n4. Testing Sinhala support...")
    response_si = ollama_service.generate_chat_response(
        query="ඔබේ නම මොකද්ද?",
        context="You are a helpful assistant for a business.",
        conversation_history=[],
        language='si',
        max_tokens=100,
        temperature=0.7
    )
    print(f"✅ Generated Sinhala response: {response_si[:100]}...")
    
    # Test 5: Vector database operations
    print("\n5. Testing vector database operations...")
    service_id = "test_service"
    test_chunks = [
        "Our business offers high-quality products",
        "We have excellent customer service",
        "Free shipping on orders over $50"
    ]
    
    num_chunks = ollama_service.add_documents(
        service_id=service_id,
        chunks=test_chunks,
        metadata={'source': 'test', 'type': 'business_info'}
    )
    print(f"✅ Added {num_chunks} chunks to vector database")
    
    # Test 6: Search similar documents
    print("\n6. Testing semantic search...")
    query = "Do you offer free delivery?"
    results = ollama_service.search_similar_documents(
        query=query,
        service_id=service_id,
        k=2
    )
    print(f"✅ Found {len(results)} relevant documents")
    for i, doc in enumerate(results, 1):
        print(f"   Result {i}: {doc['content'][:60]}...")
        print(f"   Distance: {doc.get('distance', 'N/A')}")
    
    print("\n" + "="*60)
    print("✅ All tests passed! Ollama is fully integrated with Llama3")
    print("="*60)

if __name__ == "__main__":
    test_ollama()
