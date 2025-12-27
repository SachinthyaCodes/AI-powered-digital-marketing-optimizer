#!/usr/bin/env python3
"""
Complete test of Modal service and RAG system functionality
"""
from services.modal_service import get_modal_service
from services.vector_service import VectorDatabaseService
import json

def test_modal_service():
    """Test Modal service functionality"""
    print("🧪 Testing Modal Service")
    print("=" * 50)
    
    ms = get_modal_service()
    print(f"Modal Service Status:")
    print(f"- Configured: {ms.is_configured}")
    print(f"- Embedding URL: {ms.embedding_url}")
    print(f"- Chat URL: {ms.chat_url}")
    print()

    # Test embedding generation
    print("Testing embedding generation...")
    result = ms.generate_embedding("Hello world, this is a test message")
    print(f"- Success: {result.get('success')}")
    print(f"- Message: {result.get('message')}")
    embedding = result.get('embedding', [])
    print(f"- Embedding size: {len(embedding) if embedding else 0}")
    if embedding:
        print(f"- First 5 values: {embedding[:5]}")
    print()

    # Test chat generation
    print("Testing chat generation...")
    chat_result = ms.generate_chat_response(
        query="What is your name?", 
        context="You are a helpful assistant for MarketMatic", 
        language="en"
    )
    print(f"- Response: {chat_result}")
    print()

def test_vector_service():
    """Test vector database functionality"""
    print("🧪 Testing Vector Database Service")
    print("=" * 50)
    
    try:
        vs = VectorDatabaseService()
        print(f"Vector service initialized: {vs.client is not None}")
        print(f"Collection available: {vs.collection is not None}")
        
        # Test database status
        status = vs.get_database_status()
        print("Database status:")
        for key, value in status.items():
            print(f"- {key}: {value}")
        print()
        
        # Test adding a document
        test_service_id = "test_service_123"
        print(f"Testing document addition for service: {test_service_id}")
        
        result = vs.add_documents(
            service_id=test_service_id,
            chunks=["This is a test document about MarketMatic features"],
            metadata={"test": True, "doc_type": "faq"}
        )
        print(f"- Documents added: {result}")
        
        # Test search
        print("Testing semantic search...")
        search_results = vs.semantic_search(
            query="MarketMatic features",
            service_id=test_service_id,
            limit=3
        )
        print(f"- Search results: {search_results}")
        results = search_results.get('results', [])
        print(f"- Results found: {len(results)}")
        for i, result in enumerate(results[:2]):
            content = result.get('content', result.get('document', ''))
            print(f"  Result {i+1}: {content[:100]}...")
        
    except Exception as e:
        print(f"❌ Vector service error: {e}")

def test_chat_integration():
    """Test complete chat integration"""
    print("🧪 Testing Complete Chat Integration")
    print("=" * 50)
    
    try:
        from routes.chat_routes import RAGService
        
        rag_service = RAGService()
        print("RAG service initialized successfully")
        
        # Test chat response
        response = rag_service.generate_response(
            query="What can you tell me about your services?",
            context="You are a helpful assistant for MarketMatic e-commerce platform",
            language="en"
        )
        
        print("Chat response test:")
        print(f"- Response: {response}")
        
    except Exception as e:
        print(f"❌ Chat integration error: {e}")

if __name__ == "__main__":
    print("🚀 MarketMatic RAG System Test Suite")
    print("=" * 60)
    print()
    
    test_modal_service()
    print()
    test_vector_service() 
    print()
    test_chat_integration()
    
    print("✅ Test Suite Complete!")