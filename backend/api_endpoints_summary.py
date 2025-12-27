"""
API Endpoints Summary - Supabase PostgreSQL Edition
All endpoints use SQLAlchemy ORM with Supabase PostgreSQL
"""

print("=" * 80)
print("MARKETMATIC API ENDPOINTS - SUPABASE POSTGRESQL")
print("=" * 80)

endpoints = {
    "Authentication": [
        "POST   /api/auth/signup           - Register new user/admin",
        "POST   /api/auth/login            - Login and get JWT token",
        "POST   /api/auth/forgot-password  - Request password reset",
        "POST   /api/auth/reset-password   - Reset password with token",
        "GET    /api/auth/verify-token     - Verify JWT token validity",
    ],
    
    "Superadmin Authentication": [
        "POST   /api/superadmin/login       - Superadmin login",
        "POST   /api/superadmin/register    - Register superadmin (first time only)",
    ],
    
    "Service Management (Superadmin)": [
        "GET    /api/services/              - Get all services",
        "GET    /api/services/<id>          - Get service by ID",
        "POST   /api/services/              - Create new service",
        "PUT    /api/services/<id>          - Update service",
        "DELETE /api/services/<id>          - Delete service",
        "GET    /api/services/<id>/admins   - Get service admins",
        "POST   /api/services/<id>/admins   - Add admin to service",
        "DELETE /api/services/<id>/admins/<admin_id> - Remove admin",
    ],
    
    "Bot Configuration (Admin)": [
        "GET    /api/bot/config             - Get bot configuration",
        "PUT    /api/bot/config             - Update bot configuration",
        "GET    /api/bot/stats              - Get bot statistics",
    ],
    
    "FAQ Management (Admin)": [
        "GET    /api/bot/faqs               - Get all FAQs",
        "POST   /api/bot/faqs               - Create new FAQ",
        "PUT    /api/bot/faqs/<id>          - Update FAQ",
        "DELETE /api/bot/faqs/<id>          - Delete FAQ",
        "POST   /api/bot/faqs/bulk          - Bulk create FAQs",
    ],
    
    "Product Management (Admin)": [
        "GET    /api/bot/products           - Get all products",
        "POST   /api/bot/products           - Create new product",
        "PUT    /api/bot/products/<id>      - Update product",
        "DELETE /api/bot/products/<id>      - Delete product",
    ],
    
    "Policy Management (Admin)": [
        "GET    /api/bot/policies           - Get all policies",
        "POST   /api/bot/policies           - Create new policy",
        "PUT    /api/bot/policies/<id>      - Update policy",
        "DELETE /api/bot/policies/<id>      - Delete policy",
    ],
    
    "Document Management (Admin)": [
        "GET    /api/documents/             - Get all documents",
        "POST   /api/documents/upload       - Upload document",
        "DELETE /api/documents/<id>         - Delete document",
        "GET    /api/documents/embeddings   - Get document embeddings count",
    ],
    
    "RAG (Vector Search)": [
        "POST   /api/rag/query              - Query documents with RAG",
        "POST   /api/rag/embed              - Generate embeddings",
        "GET    /api/rag/status             - Get RAG service status",
    ],
    
    "Chat (Public)": [
        "POST   /api/chat/<service_token>   - Send chat message",
        "GET    /api/chat/<service_token>/history - Get chat history",
    ],
}

for category, routes in endpoints.items():
    print(f"\n{category}")
    print("-" * 80)
    for route in routes:
        print(f"  {route}")

print("\n" + "=" * 80)
print("DATABASE: Supabase PostgreSQL with pgvector")
print("AI: Ollama (llama3 + nomic-embed-text)")
print("=" * 80)
print("\nAll endpoints use SQLAlchemy ORM connecting to Supabase PostgreSQL")
print("Tables: users, services, faqs, products, policies, documents,")
print("        document_embeddings, chat_messages")
print("=" * 80)
