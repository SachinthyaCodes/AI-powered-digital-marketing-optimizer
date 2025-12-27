"""
RAG Routes for MarketMatic Chatbot
Uses Ollama with Llama3 for LLM inference and ChromaDB for vector storage
"""
from flask import Blueprint, request, jsonify
from auth.decorators import admin_required
from services.document_processor import DocumentProcessor
from services.ollama_service import get_ollama_service
from utils.cloudinary_service import CloudinaryService
from models.document import Document, ChatMessage, ChatSession
from database import db_instance
import traceback
from datetime import datetime

rag_bp = Blueprint('rag', __name__, url_prefix='/api/rag')

# Initialize lightweight services only
document_processor = DocumentProcessor()
cloudinary_service = CloudinaryService()

def get_ai_service():
    """Get Ollama AI service with Llama3"""
    return get_ollama_service()


# ============== ADMIN ENDPOINTS ==============

@rag_bp.route('/upload-document', methods=['POST'])
@admin_required
def upload_document(current_user):
    """
    Upload and process a document (PDF, Excel, Word, Text)
    Extracts content, generates embeddings, and stores in vector DB
    """
    try:
        service_id = current_user['service_id']
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get file extension
        file_ext = file.filename.rsplit('.', 1)[-1].lower()
        allowed_extensions = ['pdf', 'docx', 'xlsx', 'xls', 'txt']
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}), 400
        
        # Read file content
        file_content = file.read()
        
        # Create document record
        doc = Document.create(
            service_id=service_id,
            filename=file.filename,
            file_type=file_ext,
            status='processing'
        )
        
        try:
            # Upload to Cloudinary (optional, for PDF previews)
            if file_ext == 'pdf':
                try:
                    cloudinary_url = cloudinary_service.upload_file(
                        file_content,
                        f"documents/{service_id}/{doc['_id']}"
                    )
                    Document.update(doc['_id'], {'cloudinary_url': cloudinary_url})
                except Exception as e:
                    print(f"Cloudinary upload failed: {str(e)}")
            
            # Process file based on type
            if file_ext == 'pdf':
                content = document_processor.process_pdf(file_content)
            elif file_ext in ['xlsx', 'xls']:
                content = document_processor.process_excel(file_content)
            elif file_ext == 'docx':
                content = document_processor.process_word(file_content)
            else:  # txt
                content = document_processor.process_text(file_content)
            
            if not content or not content.strip():
                Document.update(doc['_id'], {'status': 'failed', 'error': 'No content extracted'})
                return jsonify({'error': 'No content could be extracted from file'}), 400
            
            # Chunk the content
            chunks = document_processor.chunk_text(content)
            
            # Generate embeddings and add to vector DB
            metadata = {
                'document_id': str(doc['_id']),
                'filename': file.filename,
                'file_type': file_ext,
                'source': 'upload'
            }
            
            ai_service = get_ai_service()
            num_chunks = ai_service.add_documents(
                service_id=service_id,
                chunks=chunks,
                metadata=metadata
            )
            
            # Extract metadata
            doc_metadata = document_processor.extract_metadata(content)
            
            # Update document record
            Document.update(doc['_id'], {
                'status': 'completed',
                'content': content[:1000],  # Store first 1000 chars
                'chunks_count': num_chunks,
                'metadata': doc_metadata
            })
            
            return jsonify({
                'message': 'Document uploaded and processed successfully',
                'document_id': str(doc['_id']),
                'filename': file.filename,
                'chunks_created': num_chunks,
                'metadata': doc_metadata
            }), 201
            
        except Exception as e:
            # Update document status to failed
            Document.update(doc['_id'], {
                'status': 'failed',
                'error': str(e)
            })
            raise
            
    except Exception as e:
        print(f"Error uploading document: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@rag_bp.route('/sync-faqs', methods=['POST'])
@admin_required
def sync_faqs(current_user):
    """Sync FAQs from database to vector DB"""
    try:
        service_id = current_user['service_id']
        
        # Get FAQs from database
        db = db_instance.get_db()
        faqs = list(db.faqs.find({'service_id': service_id}))
        
        if not faqs:
            return jsonify({'message': 'No FAQs found'}), 200
        
        # Process FAQs
        faq_content = document_processor.process_faq(faqs)
        chunks = document_processor.chunk_text(faq_content)
        
        # Add to vector DB
        metadata = {
            'source': 'faq',
            'count': len(faqs)
        }
        
        ai_service = get_ai_service()
        num_chunks = ai_service.add_documents(
            service_id=service_id,
            chunks=chunks,
            metadata=metadata
        )
        
        return jsonify({
            'message': 'FAQs synced successfully',
            'faqs_count': len(faqs),
            'chunks_created': num_chunks
        }), 200
        
    except Exception as e:
        print(f"Error syncing FAQs: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@rag_bp.route('/sync-products', methods=['POST'])
@admin_required
def sync_products(current_user):
    """Sync products from database to vector DB"""
    try:
        service_id = current_user['service_id']
        
        # Get products from database
        db = db_instance.get_db()
        products = list(db.products.find({'service_id': service_id}))
        
        if not products:
            return jsonify({'message': 'No products found'}), 200
        
        # Process products
        product_content = document_processor.process_products(products)
        chunks = document_processor.chunk_text(product_content)
        
        # Add to vector DB
        metadata = {
            'source': 'product',
            'count': len(products)
        }
        
        ai_service = get_ai_service()
        num_chunks = ai_service.add_documents(
            service_id=service_id,
            chunks=chunks,
            metadata=metadata
        )
        
        return jsonify({
            'message': 'Products synced successfully',
            'products_count': len(products),
            'chunks_created': num_chunks
        }), 200
        
    except Exception as e:
        print(f"Error syncing products: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@rag_bp.route('/sync-policies', methods=['POST'])
@admin_required
def sync_policies(current_user):
    """Sync policies from database to vector DB"""
    try:
        service_id = current_user['service_id']
        
        # Get policies from database
        db = db_instance.get_db()
        policies = list(db.policies.find({'service_id': service_id}))
        
        if not policies:
            return jsonify({'message': 'No policies found'}), 200
        
        # Process policies
        policy_content = document_processor.process_policies(policies)
        chunks = document_processor.chunk_text(policy_content)
        
        # Add to vector DB
        metadata = {
            'source': 'policy',
            'count': len(policies)
        }
        
        ai_service = get_ai_service()
        num_chunks = ai_service.add_documents(
            service_id=service_id,
            chunks=chunks,
            metadata=metadata
        )
        
        return jsonify({
            'message': 'Policies synced successfully',
            'policies_count': len(policies),
            'chunks_created': num_chunks
        }), 200
        
    except Exception as e:
        print(f"Error syncing policies: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@rag_bp.route('/sync-all', methods=['POST'])
@admin_required
def sync_all(current_user):
    """Sync all data (FAQs, products, policies) to vector DB"""
    try:
        service_id = current_user['service_id']
        db = db_instance.get_db()
        results = {}
        ai_service = get_ai_service()  # Initialize only when needed
        
        # Sync FAQs
        faqs = list(db.faqs.find({'service_id': service_id}))
        if faqs:
            content = document_processor.process_faq(faqs)
            chunks = document_processor.chunk_text(content)
            num_chunks = ai_service.add_documents(
                service_id, chunks, {'source': 'faq'}
            )
            results['faqs'] = {'count': len(faqs), 'chunks': num_chunks}
        
        # Sync products
        products = list(db.products.find({'service_id': service_id}))
        if products:
            content = document_processor.process_products(products)
            chunks = document_processor.chunk_text(content)
            num_chunks = ai_service.add_documents(
                service_id, chunks, {'source': 'product'}
            )
            results['products'] = {'count': len(products), 'chunks': num_chunks}
        
        # Sync policies
        policies = list(db.policies.find({'service_id': service_id}))
        if policies:
            content = document_processor.process_policies(policies)
            chunks = document_processor.chunk_text(content)
            num_chunks = ai_service.add_documents(
                service_id, chunks, {'source': 'policy'}
            )
            results['policies'] = {'count': len(policies), 'chunks': num_chunks}
        
        return jsonify({
            'message': 'All data synced successfully',
            'results': results
        }), 200
        
    except Exception as e:
        print(f"Error syncing all data: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@rag_bp.route('/documents', methods=['GET'])
@admin_required
def get_documents(current_user):
    """Get all uploaded documents for this service"""
    try:
        service_id = current_user['service_id']
        documents = Document.find_by_service(service_id)
        
        return jsonify({
            'documents': documents,
            'count': len(documents)
        }), 200
        
    except Exception as e:
        print(f"Error fetching documents: {str(e)}")
        return jsonify({'error': str(e)}), 500


@rag_bp.route('/documents/<document_id>', methods=['DELETE'])
@admin_required
def delete_document(current_user, document_id):
    """Delete an uploaded document"""
    try:
        service_id = current_user['service_id']
        
        # Get document
        doc = Document.find_by_id(document_id)
        if not doc:
            return jsonify({'error': 'Document not found'}), 404
        
        # Verify ownership
        if doc['service_id'] != service_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Delete document record
        Document.delete(document_id)
        
        # Note: Vector embeddings for this document remain in ChromaDB
        # To fully clean up, we'd need to track chunk IDs and delete them
        
        return jsonify({'message': 'Document deleted successfully'}), 200
        
    except Exception as e:
        print(f"Error deleting document: {str(e)}")
        return jsonify({'error': str(e)}), 500


@rag_bp.route('/test-query', methods=['POST'])
@admin_required
def test_query(current_user):
    """Test RAG query (for admins to test chatbot)"""
    try:
        service_id = current_user['service_id']
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        
        # Use Ollama service with Llama3
        ollama_service = get_ollama_service()
        
        if not ollama_service.check_service_available():
            return jsonify({
                'error': 'AI service unavailable. Please make sure Ollama is running.'
            }), 503
        
        # Search for relevant documents
        search_results = ollama_service.search_similar_documents(
            query=query,
            service_id=service_id,
            k=5
        )
        
        # Build context from retrieved documents
        context = "\n\n".join([doc['content'] for doc in search_results])
        
        if not context:
            context = "No relevant information found in the knowledge base."
        
        # Generate response using Llama3
        response = ollama_service.generate_chat_response(
            query=query,
            context=context,
            conversation_history=[],
            language='en'
        )
        
        # Simple intent detection
        intent = 'general'
        confidence = 0.8
        
        return jsonify({
            'query': query,
            'response': response,
            'intent': intent,
            'confidence': confidence,
            'context_sources': [
                {
                    'content': doc['content'],
                    'similarity': 1 - doc.get('distance', 0),
                    'metadata': doc.get('metadata', {})
                }
                for doc in search_results
            ]
        }), 200
        
    except Exception as e:
        print(f"Error testing query: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============== PUBLIC ENDPOINTS ==============

@rag_bp.route('/welcome', methods=['POST'])
def welcome():
    """
    Get welcome message for a service
    Requires service_token in request body
    """
    try:
        data = request.get_json()
        
        # Validate request
        if not data or 'service_token' not in data:
            return jsonify({'error': 'service_token is required'}), 400
        
        service_token = data['service_token']
        
        # Get database connection
        db = db_instance.get_db()
        
        # Verify service token  
        db = db_instance.get_db()
        service = db.services.find_one({'token': service_token, 'status': 'active'})
        if not service:
            return jsonify({'error': 'Invalid service token'}), 401
        
        service_id = str(service['_id'])
        
        # Get bot configuration
        bot_config = db.bot_configurations.find_one({'service_id': service_id})
        
        if not bot_config:
            return jsonify({'error': 'Bot not configured for this service'}), 400
        
        if not bot_config.get('is_active', True):
            return jsonify({'error': 'Bot is currently inactive'}), 503
        
        # Get welcome message
        welcome_message = bot_config.get('welcome_message', '')
        
        # If no welcome message configured, provide a default based on service
        if not welcome_message:
            service_name = service.get('business_name', 'Our Business')
            welcome_message = f"Welcome to {service_name}! How can I assist you today?"
        
        return jsonify({
            'welcome_message': welcome_message,
            'service_name': service.get('business_name', 'Business'),
            'languages_supported': bot_config.get('language_support', ['en', 'si']),
            'session_id': None  # Will be created when first message is sent
        }), 200
        
    except Exception as e:
        print(f"Error in welcome: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500


@rag_bp.route('/chat', methods=['POST'])
def chat():
    """
    Public chatbot endpoint with SinLlama integration
    Requires service_token in request body
    """
    try:
        data = request.get_json()
        
        # Validate request
        if not data or 'service_token' not in data or 'message' not in data:
            return jsonify({'error': 'service_token and message are required'}), 400
        
        service_token = data['service_token']
        message = data['message']
        session_id = data.get('session_id')
        
        # Get database connection
        db = db_instance.get_db()
        
        # Verify service token
        service = db.services.find_one({'token': service_token, 'status': 'active'})
        if not service:
            return jsonify({'error': 'Invalid service token'}), 401
        
        service_id = str(service['_id'])
        
        # Get bot configuration for this service
        bot_config = db.bot_configurations.find_one({'service_id': service_id})
        if not bot_config:
            return jsonify({'error': 'Bot not configured for this service'}), 400
        
        # Check if bot is active
        if not bot_config.get('is_active', True):
            return jsonify({'error': 'Bot is currently inactive'}), 503
        
        # Get response mode setting
        response_mode = bot_config.get('response_mode', 'hybrid')  # 'documents_only' or 'hybrid'
        use_general_knowledge = bot_config.get('use_general_knowledge', True)
        
        # Get or create chat session
        if session_id:
            session = ChatSession.find_by_session_id(session_id)
            if session:
                ChatSession.update_activity(session_id)
            else:
                session_id = None
        
        if not session_id:
            session = ChatSession.create(service_id=service_id)
            session_id = session['session_id']
        
        # Use Ollama service with Llama3
        ollama_service = get_ollama_service()
        
        if not ollama_service.check_service_available():
            return jsonify({
                'error': 'AI service unavailable. Please make sure Ollama is running.'
            }), 503
        
        # Simple language detection (check for Sinhala unicode)
        language = 'si' if any('\u0D80' <= char <= '\u0DFF' for char in message) else 'en'
        
        # Simple intent detection
        intent = 'general'
        confidence = 0.8
        
        # Search for relevant context from documents, FAQs, and products
        search_results = ollama_service.search_similar_documents(
            query=message,
            service_id=service_id,
            k=8  # Increased for better context
        )
        
        # Build comprehensive context based on response mode
        context_parts = []
        has_relevant_content = False
        
        # Add search results from uploaded documents
        if search_results:
            context_parts.append("DOCUMENT INFORMATION:")
            context_parts.extend([doc['content'] for doc in search_results])
            has_relevant_content = True
        
        # Only add database content if in hybrid mode or if no documents found
        if response_mode == 'hybrid' or not has_relevant_content:
            # Get FAQs and Products for additional context
            faqs = list(db.faqs.find({'service_id': service_id, 'is_active': True}))
            products = list(db.products.find({'service_id': service_id, 'is_active': True}))
            policies = list(db.policies.find({'service_id': service_id, 'is_active': True}))
            
            # Add FAQs if relevant
            if faqs:
                context_parts.append("\nFREQUENTLY ASKED QUESTIONS:")
                for faq in faqs[:5]:  # Limit to 5 FAQs
                    context_parts.append(f"Q: {faq['question']}\nA: {faq['answer']}")
                has_relevant_content = True
            
            # Add product information if relevant to product queries
            if any(word in message.lower() for word in ['product', 'price', 'item', 'sell', 'buy', 'stock', 'available']) and products:
                context_parts.append("\nPRODUCT CATALOG:")
                for product in products[:10]:  # Limit to 10 products
                    context_parts.append(f"- {product['name']}: {product['description']} - Rs. {product['price']} (Stock: {product['stock']})")
                has_relevant_content = True
            
            # Add policies if relevant
            if any(word in message.lower() for word in ['policy', 'return', 'shipping', 'delivery', 'refund']) and policies:
                context_parts.append("\nPOLICIES:")
                for policy in policies[:3]:  # Limit to 3 policies
                    context_parts.append(f"{policy['title']}: {policy['content'][:200]}...")
                has_relevant_content = True
        
        # Handle documents-only mode
        if response_mode == 'documents_only' and not has_relevant_content:
            documents_only_msg = bot_config.get('documents_only_message', 
                "I can only answer based on the documents uploaded by the business. I don't have information about your query in the uploaded documents.")
            
            # Save messages
            ChatMessage.create(
                service_id=service_id,
                session_id=session_id,
                role='user',
                message=message,
                language=language,
                intent=intent,
                confidence=confidence
            )
            
            ChatMessage.create(
                service_id=service_id,
                session_id=session_id,
                role='assistant',
                message=documents_only_msg,
                language=language,
                context_used="documents_only_mode"
            )
            
            return jsonify({
                'session_id': session_id,
                'response': documents_only_msg,
                'language': language,
                'intent': intent,
                'confidence': confidence,
                'context_sources': 0,
                'response_mode': 'documents_only',
                'model': 'Rule-based'
            }), 200
        
        context = "\n\n".join(context_parts) if context_parts else "No specific information available."
        
        # Get conversation history
        history = ChatMessage.get_session_history(session_id, limit=5)
        conversation_history = [
            {
                'role': msg['role'],
                'content': msg['message']
            }
            for msg in history
        ]
        
        # Generate response using SinLlama
        response = modal_service.generate_chat_response(
            query=message,
            context=context,
            conversation_history=conversation_history,
            language=language,
            max_tokens=512,
            temperature=0.7
        )
        
        # If response is empty or too generic, use fallback
        if not response or len(response.strip()) < 10:
            fallback = bot_config.get('fallback_message', 'I apologize, but I need more information to help you. Could you please provide more details about what you\'re looking for?')
            if language == 'si':
                fallback = 'සමාවෙන්න, ඔබට උදව් වීමට මට තවත් තොරතුරු අවශ්‍යයි. ඔබ සොයන දේ ගැන වැඩි විස්තර ලබා දිය හැකිද?'
            response = fallback
        
        # Save messages
        ChatMessage.create(
            service_id=service_id,
            session_id=session_id,
            role='user',
            message=message,
            language=language,
            intent=intent,
            confidence=confidence
        )
        
        ChatMessage.create(
            service_id=service_id,
            session_id=session_id,
            role='assistant',
            message=response,
            language=language,
            context_used=context[:1000]  # Store first 1000 chars of context
        )
        
        return jsonify({
            'session_id': session_id,
            'response': response,
            'language': language,
            'intent': intent,
            'confidence': confidence,
            'context_sources': len(search_results['documents']),
            'response_mode': response_mode,
            'model': 'SinLlama'  # Indicate which model was used
        }), 200
        
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        traceback.print_exc()
        
        # Return appropriate error message based on detected language
        error_msg = 'An error occurred processing your message'
        try:
            if 'language' in locals() and language == 'si':
                error_msg = 'ඔබගේ පණිවිඩය සැකසීමේදී දෝෂයක් සිදුවිය'
        except:
            pass
            
        return jsonify({'error': error_msg}), 500


@rag_bp.route('/chat/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = ChatMessage.get_session_history(session_id, limit=limit)
        
        return jsonify({
            'session_id': session_id,
            'messages': history,
            'count': len(history)
        }), 200
        
    except Exception as e:
        print(f"Error fetching chat history: {str(e)}")
        return jsonify({'error': str(e)}), 500


@rag_bp.route('/status', methods=['GET'])
def check_status():
    """Check RAG system status"""
    try:
        modal_service = get_modal_service()
        status = modal_service.check_service_available()
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
