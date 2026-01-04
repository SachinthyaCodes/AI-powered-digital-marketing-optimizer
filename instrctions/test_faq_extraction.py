"""
Test FAQ extraction from document
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.ollama_rag_service import OllamaRAGService

# Test document with FAQs
test_document = """
Welcome to Our Store!

Q: What are your business hours?
A: We are open Monday to Friday, 9 AM to 6 PM. Closed on weekends and public holidays.

Q: Do you offer free shipping?
A: Yes, we offer free shipping on orders over $50 within the United States.

Question: How can I track my order?
Answer: You can track your order using the tracking number sent to your email after shipment.

Q: What is your return policy?
A: We accept returns within 30 days of purchase with original receipt and packaging.

Additional Information:
Our store specializes in quality products and excellent customer service.
"""

print("=" * 80)
print("TESTING FAQ EXTRACTION")
print("=" * 80)

# Initialize RAG service
print("\n[1/3] Initializing Ollama RAG Service...")
rag = OllamaRAGService('test-service')
print("✅ RAG service initialized")

# Extract FAQs
print("\n[2/3] Extracting FAQs from test document...")
faqs = rag.extract_faqs_from_text(test_document)
print(f"✅ Found {len(faqs)} FAQs\n")

# Display results
print("[3/3] Extracted FAQs:")
print("-" * 80)
for i, faq in enumerate(faqs, 1):
    print(f"\nFAQ #{i}:")
    print(f"Q: {faq['question']}")
    print(f"A: {faq['answer']}")
    print("-" * 80)

if len(faqs) > 0:
    print(f"\n✅ SUCCESS! FAQ extraction is working correctly!")
    print(f"   {len(faqs)} FAQs would be added to the database")
else:
    print(f"\n❌ WARNING! No FAQs were extracted")
    print("   Check document format - use Q:/A: or Question:/Answer: format")

print("\n" + "=" * 80)
