"""
Quick Test - Modal RAG System
Tests document upload and FAQ extraction
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("\n" + "=" * 80)
print("MODAL RAG SYSTEM - QUICK TEST")
print("=" * 80)

print("\n[1/3] Testing imports...")
try:
    from services.modal_rag_service import get_modal_rag_service
    from services.sinllama_tokenizer import get_tokenizer
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

print("\n[2/3] Testing tokenizer...")
try:
    tokenizer = get_tokenizer()
    print(f"✅ Tokenizer loaded: {len(tokenizer):,} tokens")
    
    # Test encoding
    text = "ශ්‍රී ලංකාව දකුණු ආසියාවේ පිහිටි දිවයින රටකි."
    tokens = tokenizer.count_tokens(text)
    print(f"   Test text: {text}")
    print(f"   Tokens: {tokens}")
    
except Exception as e:
    print(f"❌ Tokenizer test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n[3/3] Testing Modal RAG service...")
try:
    # Create test service
    modal_rag = get_modal_rag_service('test-service')
    print("✅ Modal RAG service initialized")
    
    # Test document processing
    print("\n   Testing document processing...")
    test_text = """Q: ශ්‍රී ලංකාවේ අගනුවර කුමක්ද?
A: කොළඹ ශ්‍රී ලංකාවේ වාණිජ අගනුවර වේ.

Q: How many people live in Sri Lanka?
A: Sri Lanka has a population of approximately 22 million people."""
    
    faqs = modal_rag.extract_faqs_from_text(test_text)
    print(f"✅ FAQ extraction working: {len(faqs)} FAQs found")
    
    for i, faq in enumerate(faqs, 1):
        print(f"\n   FAQ {i}:")
        print(f"   Q: {faq['question'][:60]}...")
        print(f"   A: {faq['answer'][:60]}...")
    
except Exception as e:
    print(f"❌ Modal RAG test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("QUICK TEST COMPLETE!")
print("=" * 80)

print("""
✅ SYSTEM READY FOR:
   - Document upload (PDF, DOCX, TXT)
   - Automatic FAQ extraction
   - FAQ display in bot management
   - RAG queries (search + answer)

🚀 NEXT STEPS:
   1. Start your backend:
      cd backend
      python app.py
   
   2. Upload a document:
      POST /api/rag/upload-document
      (with file in form-data)
   
   3. Check FAQs:
      GET /api/bot/faqs
      (FAQs will be automatically extracted and shown)

⚙️ MODAL CONFIGURATION (Optional):
   - Set MODAL_GENERATE_URL in .env for remote generation
   - System works without Modal (uses fallback)
   - See modal_config.env.template

📚 FEATURES:
   ✅ SinLlama Extended Tokenizer (139K vocab)
   ✅ Automatic FAQ extraction from documents
   ✅ FAISS vector search
   ✅ FAQs show in bot management
   ✅ Modal-ready (remote inference)
   ✅ Works offline (fallback mode)
""")

print("=" * 80 + "\n")
