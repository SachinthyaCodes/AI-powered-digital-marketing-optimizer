"""
Simplified Chat Routes for MarketMatic using SQLAlchemy
Uses SinLlama GGUF model for AI-powered conversations with Sinhala support
Integrated with RAG (Retrieval-Augmented Generation) using pgvector
"""
from flask import Blueprint, request, jsonify
from database import SessionLocal
from models.sqlalchemy_models import ChatMessage, Service, FAQ, Product, Policy, User, DocumentEmbedding
from services.ollama_service import OllamaService
from services.vector_service import VectorService
from datetime import datetime
from sqlalchemy import text
import uuid
import json

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Initialize services
ollama_service = OllamaService()
vector_service = VectorService()

def get_business_context(service_id: uuid.UUID, db_session=None) -> str:
    """
    Fetch all business data (FAQs, Products, Policies) for a service
    and format it as context for the AI
    """
    if not db_session:
        db_session = SessionLocal()
        should_close = True
    else:
        should_close = False
        
    context_parts = []
    
    try:
        # Ensure service_id is a string
        service_id_str = str(service_id) if service_id else None
        if not service_id_str:
            return ""
        
        # Get FAQs
        faqs = db_session.query(FAQ).filter(
            FAQ.service_id == service_id_str,
            FAQ.is_active == True
        ).limit(20).all()
        
        if faqs:
            context_parts.append("=== Frequently Asked Questions ===")
            for faq in faqs:
                context_parts.append(f"Q ({faq.language}): {faq.question}")
                context_parts.append(f"A: {faq.answer}")
                context_parts.append("")
        
        # Get Products
        products = db_session.query(Product).filter(
            Product.service_id == service_id_str,
            Product.is_active == True
        ).limit(30).all()
        
        if products:
            context_parts.append("=== Available Products ===")
            for product in products:
                product_info = f"Product: {product.name}"
                if product.category:
                    product_info += f" (Category: {product.category})"
                product_info += f"\nPrice: Rs. {product.price}"
                product_info += f"\nStock: {product.stock} units"
                if product.description:
                    product_info += f"\nDescription: {product.description}"
                
                context_parts.append(product_info)
                context_parts.append("")
        
        # Get Policies
        policies = db_session.query(Policy).filter(
            Policy.service_id == service_id_str,
            Policy.is_active == True
        ).limit(10).all()
        
        if policies:
            context_parts.append("=== Business Policies ===")
            for policy in policies:
                context_parts.append(f"Policy: {policy.title} ({policy.policy_type})")
                context_parts.append(policy.content)
                context_parts.append("")
        
        # Get service/bot configuration
        service = db_session.query(Service).filter(Service.id == service_id_str).first()
        if service and service.welcome_message:
            context_parts.insert(0, f"=== Welcome Message ===\n{service.welcome_message}\n")
        
        return "\n".join(context_parts)
        
    except Exception as e:
        print(f"Error getting business context: {e}")
        # Rollback transaction on error
        try:
            db_session.rollback()
        except:
            pass
        return "Business information is being loaded. Please ask your question."
    finally:
        if should_close:
            db_session.close()


def get_document_context(query: str, service_id: str, db_session=None, limit: int = 3) -> str:
    """
    Retrieve relevant document chunks using RAG (pgvector similarity search)
    Returns formatted context from uploaded documents
    BUSINESS-SPECIFIC: Only retrieves documents for the specific service
    """
    if not db_session:
        db_session = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        # Ensure service_id is a string
        service_id_str = str(service_id) if service_id else None
        if not service_id_str:
            return ""
        
        # Check if there are any document embeddings for this service
        embedding_count = db_session.query(DocumentEmbedding).filter(
            DocumentEmbedding.service_id == service_id_str
        ).count()
        
        if embedding_count == 0:
            print(f"[RAG] No uploaded documents for SERVICE {str(service_id)[:8]}")
            return ""  # No documents uploaded yet
        
        print(f"[RAG] 📚 Service has {embedding_count} document chunks available")
        print(f"[RAG] 🔍 Searching for: '{query[:60]}...'")
        
        # Use vector service to search similar documents
        relevant_chunks = vector_service.search_similar_documents(
            query=query,
            service_id=service_id,
            limit=limit,
            db_session=db_session
        )
        
        if not relevant_chunks:
            print("[RAG] ℹ️ No relevant chunks found in documents")
            return ""
        
        # Format document context with STRICT relevance filtering
        context_parts = []
        relevant_count = 0
        
        for i, chunk in enumerate(relevant_chunks, 1):
            similarity_score = chunk.get('similarity_score', 0)
            
            # STRICT THRESHOLD: Only include highly relevant chunks (0.65+ for quality)
            if similarity_score >= 0.65:
                if relevant_count == 0:
                    context_parts.append("📄 === INFORMATION FROM YOUR UPLOADED DOCUMENTS ===\n")
                
                context_parts.append(f"[Relevant Info {relevant_count + 1}]:")
                context_parts.append(chunk.get('chunk_text', ''))
                context_parts.append("")
                relevant_count += 1
        
        if relevant_count > 0:
            print(f"✅ RAG: Found {relevant_count} highly relevant chunks (threshold: 0.65+)")
            return "\n".join(context_parts)
        else:
            print("[RAG] ⚠️ No chunks met relevance threshold (0.65). Chunks found but not relevant enough.")
            return ""
        
    except Exception as e:
        print(f"⚠️ RAG search error: {e}")
        import traceback
        traceback.print_exc()
        # Rollback transaction on error
        try:
            db_session.rollback()
        except:
            pass
        return ""  # Fail gracefully - chat can still work without RAG
    finally:
        if should_close:
            db_session.close()


@chat_bp.route('/message', methods=['POST'])
def send_chat_message():
    """
    Send a chat message and get AI response
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'message' not in data or 'service_id' not in data:
            return jsonify({
                'error': 'Missing required fields: message, service_id'
            }), 400
        
        user_message = data['message'].strip()
        service_id = data['service_id']
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Store user message
        user_msg = ChatMessage(
            id=str(uuid.uuid4()),
            service_id=uuid.UUID(service_id) if isinstance(service_id, str) else service_id,
            session_id=session_id,
            sender='user',
            message=user_message
        )
        
        db.add(user_msg)
        db.commit()
        
        # Get service configuration to check if documents-only mode is enabled
        service = db.query(Service).filter(Service.id == str(user_msg.service_id)).first()
        documents_only_mode = service.documents_only_message if service else None
        use_general_knowledge = service.use_general_knowledge if service else True
        
        # Get document context using RAG (vector search in uploaded documents)
        document_context = get_document_context(user_message, user_msg.service_id, db, limit=5)
        
        # If documents-only mode is enabled and no relevant documents found
        if documents_only_mode and not document_context:
            print("[DOCUMENTS-ONLY] No relevant documents found, using fallback message")
            response_message = documents_only_message if documents_only_message else "I can only answer questions based on the uploaded documents. I couldn't find relevant information for your question."
            
            # Store bot response
            bot_msg = ChatMessage(
                id=str(uuid.uuid4()),
                service_id=user_msg.service_id,
                session_id=session_id,
                sender='bot',
                message=response_message
            )
            
            db.add(bot_msg)
            db.commit()
            db.refresh(bot_msg)
            
            return jsonify({
                'session_id': session_id,
                'user_message': user_msg.to_dict(),
                'bot_message': bot_msg.to_dict()
            }), 200
        
        # Get business-specific context (FAQs, Products, Policies) only if general knowledge allowed
        business_context = ""
        if use_general_knowledge:
            business_context = get_business_context(user_msg.service_id, db)
        
        # Combine contexts
        full_context = ""
        if document_context:
            full_context = document_context
            print("[OK] ✅ RAG document context included")
        
        if business_context and use_general_knowledge:
            if full_context:
                full_context += "\n\n" + business_context
            else:
                full_context = business_context
            print("[OK] Business context added")
        
        # Get recent conversation history
        recent_messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id,
            ChatMessage.service_id == user_msg.service_id
        ).order_by(ChatMessage.created_at.desc()).limit(6).all()
        
        # Format conversation history for Ollama
        conversation_history = []
        for msg in reversed(recent_messages[-5:]):  # Last 5 messages in order
            conversation_history.append({
                'role': msg.sender,
                'content': msg.message
            })
        
        # Generate AI response using SinLlama GGUF model (100% OFFLINE)
        try:
            print(f"[SinLlama] 🤖 Processing: {user_message[:60]}...")
            response_message = sinllama_service.generate_chat_response(
                query=user_message,
                context=full_context,  # Includes structured data + RAG documents
                conversation_history=conversation_history,
                language='mixed',      # Auto-detects Sinhala/English/Mixed
                max_tokens=350,        # Increased for better responses
                temperature=0.75       # More natural, less robotic
            )
            print(f"✅ SinLlama response generated (OFFLINE mode)")
        except Exception as e:
            print(f"❌ SinLlama error: {e}")
            import traceback
            traceback.print_exc()
            response_message = "I'm experiencing technical difficulties right now 😔 Please try again in a moment."
        
        # Store bot response
        bot_msg = ChatMessage(
            id=str(uuid.uuid4()),
            service_id=user_msg.service_id,
            session_id=session_id,
            sender='bot',
            message=response_message
        )
        
        db.add(bot_msg)
        db.commit()
        db.refresh(bot_msg)
        
        return jsonify({
            'session_id': session_id,
            'user_message': user_msg.to_dict(),
            'bot_message': bot_msg.to_dict()
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Error processing message: {str(e)}'}), 500
    finally:
        db.close()


@chat_bp.route('/history/<session_id>', methods=['GET', 'OPTIONS'])
def get_chat_history(session_id):
    """
    Get chat history for a session
    """
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    db = SessionLocal()
    try:
        service_id = request.args.get('service_id')
        
        if not service_id:
            return jsonify({'error': 'service_id is required'}), 400
        
        # Convert service_id to string for comparison (stored as String in DB)
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id,
            ChatMessage.service_id == str(service_id)
        ).order_by(ChatMessage.created_at).all()
        
        return jsonify({
            'session_id': session_id,
            'messages': [msg.to_dict() for msg in messages]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error fetching chat history: {str(e)}'}), 500
    finally:
        db.close()


@chat_bp.route('/test', methods=['GET'])
def test_chat():
    """
    Test endpoint to verify chat service is working (100% OFFLINE)
    """
    try:
        # Get Ollama service info
        service_available = ollama_service.test_connection()
        
        return jsonify({
            'message': 'Chat service is operational',
            'status': 'ok',
            'ollama_available': service_available,
            'offline_mode': True,
            'internet_required': False,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': f'Chat service error: {str(e)}'}), 500


@chat_bp.route('/ollama/status', methods=['GET'])
def ollama_status():
    """
    Get detailed Ollama service status
    Confirms 100% OFFLINE operation
    """
    try:
        is_available = ollama_service.test_connection()
        
        return jsonify({
            'status': 'operational' if is_available else 'unavailable',
            'base_url': ollama_service.base_url,
            'chat_model': ollama_service.chat_model,
            'embedding_model': ollama_service.embedding_model,
            'ready': is_available,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@chat_bp.route('/demo/message', methods=['POST'])
def send_demo_message():
    """
    Demo endpoint - NOW USES REAL RAG + BUSINESS DATA
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get service_id from request (or use default)
        service_id = data.get('service_id', '95450d32-0c6b-4d74-bef1-ae5f7c0643fc')
        
        try:
            service_uuid = uuid.UUID(service_id)
        except ValueError:
            return jsonify({'error': 'Invalid service ID'}), 400
        
        # STEP 1: Get business context (FAQs, Products, Policies from DB)
        print(f"[DEMO] Fetching business context for service {service_id}...")
        business_context = get_business_context(service_uuid, db)
        
        # STEP 2: Get RAG document context (uploaded documents)
        print(f"[DEMO] RAG search for: {user_message[:50]}...")
        document_context = get_document_context(user_message, service_uuid, db, limit=5)
        
        # Combine contexts
        full_context = ""
        if business_context:
            full_context += business_context
            print("[OK] Business context added")
        
        if document_context:
            full_context += "\n\n" + document_context
            print("[OK] RAG document context added")
        
        if not full_context.strip():
            print("[WARN] No data found, using fallback")
            full_context = "I don't have any business information yet. Please upload documents or add FAQs/Products in the admin panel."
        
        # Get service configuration for response settings
        service = db.query(Service).filter(Service.id == str(service_uuid)).first()
        max_tokens = service.max_response_tokens if service and service.max_response_tokens else 300
        temperature = service.response_temperature if service and service.response_temperature else 0.7
        
        # Generate AI response using Ollama
        try:
            print(f"[Ollama] Activating for demo query: {user_message[:50]}...")
            bot_response = ollama_service.generate_chat_response(
                query=user_message,
                context=full_context,  # RAG + business data!
                conversation_history=None,
                language='en',
                max_tokens=max_tokens,
                temperature=temperature
            )
            print(f"[OK] Ollama demo response generated successfully")
        except Exception as e:
            print(f"[ERROR] Ollama demo error: {e}")
            import traceback
            traceback.print_exc()
            bot_response = "I'm experiencing technical difficulties. Please try again."
        
        return jsonify({
            'user_message': user_message,
            'bot_response': bot_response,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        import traceback
        print(f"❌ Demo error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Error: {str(e)}'}), 500
    finally:
        db.close()


@chat_bp.route('/business-info/<service_id>', methods=['GET'])
def get_business_info(service_id):
    """
    Get business information for a service (FAQs, Products, Policies)
    """
    db = SessionLocal()
    try:
        # Convert string to UUID
        try:
            service_uuid = uuid.UUID(service_id)
        except ValueError:
            return jsonify({'error': 'Invalid service ID format'}), 400
        
        # Get service
        service = db.query(Service).filter(Service.id == str(service_uuid)).first()
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        # Get FAQs
        faqs = db.query(FAQ).filter(
            FAQ.service_id == str(service_uuid),
            FAQ.is_active == True
        ).all()
        
        # Get Products
        products = db.query(Product).filter(
            Product.service_id == str(service_uuid),
            Product.is_active == True
        ).all()
        
        # Get Policies
        policies = db.query(Policy).filter(
            Policy.service_id == str(service_uuid),
            Policy.is_active == True
        ).all()
        
        return jsonify({
            'service': service.to_dict(),
            'faqs': [faq.to_dict() for faq in faqs],
            'products': [product.to_dict() for product in products],
            'policies': [policy.to_dict() for policy in policies]
        }), 200
        
    except Exception as e:
        import traceback
        print(f"Error fetching business info: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Error fetching business info: {str(e)}'}), 500
    finally:
        db.close()
