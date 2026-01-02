"""
RAG Routes for MarketMatic using Ollama (English Only)
Document processing, embedding generation, and semantic search
MULTI-BUSINESS SUPPORT: Each service has isolated document storage
"""
from flask import Blueprint, request, jsonify
from database import SessionLocal
from models.sqlalchemy_models import Document, User, Service, FAQ
from auth.decorators import admin_required
from services.ollama_rag_service import OllamaRAGService
from datetime import datetime
import uuid
import traceback
import os

rag_bp = Blueprint('rag', __name__, url_prefix='/api/rag')

# Cache RAG services per service_id
rag_services = {}


# ============== ADMIN ENDPOINTS ==============

def get_rag_service(service_id: str) -> OllamaRAGService:
    """Get or create RAG service for a service_id"""
    if service_id not in rag_services:
        rag_services[service_id] = OllamaRAGService(service_id)
    return rag_services[service_id]


@rag_bp.route('/upload-document', methods=['POST'])
@admin_required
def upload_document():
    """
    Upload and process a document with Ollama RAG
    Extracts content, generates embeddings, and stores in database
    Also extracts FAQs automatically (English only)
    """
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        service_id = user.service_id
        
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
        
        # Get RAG service for this service_id
        rag_service = get_rag_service(service_id)
        
        # Process document
        process_result = rag_service.process_document_file(file_content, file.filename)
        
        if not process_result['success']:
            return jsonify({'error': process_result.get('error', 'Document processing failed')}), 400
        
        text = process_result['text']
        chunks = process_result['chunks']
        
        # Create document record
        doc = Document(
            id=str(uuid.uuid4()),
            service_id=service_id,
            filename=file.filename,
            content=text[:10000],  # Store first 10k chars
            document_type=file_ext,
            file_size=len(file_content),
            is_processed=True,
            chunk_count=len(chunks)
        )
        
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        try:
            # Add document to RAG system
            rag_result = rag_service.add_document_to_rag(
                document_id=str(doc.id),
                text=text,
                metadata={
                    'filename': file.filename,
                    'document_type': file_ext,
                    'service_id': service_id
                }
            )
            
            if not rag_result['success']:
                return jsonify({
                    'error': f"RAG indexing failed: {rag_result.get('error')}",
                    'document_id': str(doc.id)
                }), 500
            
            # Extract FAQs (English only)
            faqs_extracted = []
            try:
                print(f"[FAQ] Extracting FAQs from document: {file.filename}")
                extracted_faqs = rag_service.extract_faqs_from_text(text)
                print(f"[FAQ] Found {len(extracted_faqs)} FAQ pairs")
                
                for faq_data in extracted_faqs:
                    faq = FAQ(
                        id=str(uuid.uuid4()),
                        service_id=service_id,
                        question=faq_data['question'],
                        answer=faq_data['answer'],
                        language='en',
                        is_active=True
                    )
                    db.add(faq)
                    faqs_extracted.append({
                        'question': faq_data['question'],
                        'answer': faq_data['answer']
                    })
                    print(f"[FAQ] Added: {faq_data['question'][:50]}...")
                
                db.commit()
                print(f"✅ [FAQ] Successfully saved {len(faqs_extracted)} FAQs to database")
                
            except Exception as faq_error:
                print(f"⚠️ FAQ extraction failed: {faq_error}")
                import traceback
                traceback.print_exc()
            
            return jsonify({
                'success': True,
                'message': 'Document uploaded and processed successfully',
                'document_id': str(doc.id),
                'filename': doc.filename,
                'chunks': len(chunks),
                'total_chars': process_result['total_chars'],
                'faqs_extracted': len(faqs_extracted),
                'faqs': faqs_extracted
            }), 201
            
        except Exception as e:
            db.rollback()
            return jsonify({
                'error': f'Error processing document: {str(e)}',
                'document_id': str(doc.id)
            }), 500
            
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        db.close()


@rag_bp.route('/documents', methods=['GET'])
@admin_required
def get_documents():
    """
    Get all documents for admin's service
    """
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        service_id = user.service_id
        
        documents = db.query(Document).filter(
            Document.service_id == service_id
        ).all()
        
        return jsonify({
            'documents': [doc.to_dict() for doc in documents],
            'total': len(documents)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error fetching documents: {str(e)}'}), 500
    finally:
        db.close()


@rag_bp.route('/documents/<document_id>', methods=['DELETE'])
@admin_required
def delete_document(document_id):
    """
    Delete a document and its embeddings
    """
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        service_id = user.service_id
        
        # Get document
        doc = db.query(Document).filter(
            Document.id == document_id,
            Document.service_id == service_id
        ).first()
        
        if not doc:
            return jsonify({'error': 'Document not found'}), 404
        
        # Delete associated embeddings
        # (No embeddings table with Ollama RAG - handled by FAISS index)
        
        # Delete document
        db.delete(doc)
        db.commit()
        
        # Rebuild RAG index without this document
        try:
            rag_service = get_rag_service(service_id)
            rag_service.rebuild_index_from_database()
        except Exception as rebuild_error:
            print(f"⚠️ Failed to rebuild index: {rebuild_error}")
        
        return jsonify({'message': 'Document deleted successfully'}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Error deleting document: {str(e)}'}), 500
    finally:
        db.close()


@rag_bp.route('/documents/all', methods=['DELETE'])
@admin_required
def delete_all_documents():
    """
    Delete all documents and embeddings for the service (clear RAG database)
    """
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        service_id = user.service_id
        
        # Get all documents for this service
        documents = db.query(Document).filter(Document.service_id == service_id).all()
        doc_count = len(documents)
        
        # Delete all documents
        db.query(Document).filter(Document.service_id == service_id).delete()
        db.commit()
        
        # Clear RAG index
        try:
            rag_service = get_rag_service(service_id)
            rag_service.rag_system.clear()
            rag_service.rag_system.save_index()
        except Exception as clear_error:
            print(f"⚠️ Failed to clear RAG index: {clear_error}")
        
        return jsonify({
            'message': f'Successfully deleted {doc_count} documents',
            'deleted_documents': doc_count
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Error deleting documents: {str(e)}'}), 500
    finally:
        db.close()


# ============== SEARCH/QUERY ENDPOINTS ==============

@rag_bp.route('/query', methods=['POST'])
def query_rag():
    """
    Query RAG system with Ollama (English only)
    Retrieves relevant context and generates answer
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        
        if not data or 'question' not in data or 'service_id' not in data:
            return jsonify({'error': 'question and service_id are required'}), 400
        
        question = data['question'].strip()
        service_id = data['service_id']
        top_k = data.get('top_k', 5)
        model = data.get('model', 'llama2')
        
        if not question:
            return jsonify({'error': 'Question cannot be empty'}), 400
        
        # Get RAG service
        rag_service = get_rag_service(service_id)
        
        # Query with Ollama
        result = rag_service.query_with_ollama(
            question=question,
            top_k=top_k,
            model=model
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Error querying RAG: {str(e)}'}), 500
    finally:
        db.close()


@rag_bp.route('/search', methods=['POST'])
def search_documents():
    """
    Search documents using Ollama RAG (retrieval only, no generation)
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        
        if not data or 'query' not in data or 'service_id' not in data:
            return jsonify({'error': 'query and service_id are required'}), 400
        
        query = data['query'].strip()
        service_id = data['service_id']
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Get RAG service
        rag_service = get_rag_service(service_id)
        
        # Search only (no generation)
        results = rag_service.rag_system.search(
            query=query,
            top_k=top_k,
            min_similarity=0.3
        )
        
        return jsonify({
            'query': query,
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error searching documents: {str(e)}'}), 500
    finally:
        db.close()


@rag_bp.route('/rebuild-index', methods=['POST'])
@admin_required
def rebuild_index():
    """
    Rebuild RAG index from all documents in database
    """
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        service_id = user.service_id
        
        # Get RAG service
        rag_service = get_rag_service(service_id)
        
        # Rebuild index
        result = rag_service.rebuild_index_from_database()
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'error': f'Error rebuilding index: {str(e)}'}), 500
    finally:
        db.close()


@rag_bp.route('/status', methods=['GET'])
def get_rag_status():
    """
    Get RAG system status (Ollama version)
    """
    db = SessionLocal()
    try:
        # Get total documents
        total_documents = db.query(Document).count()
        total_services_with_docs = db.query(Document.service_id).distinct().count()
        
        return jsonify({
            'status': 'operational',
            'system': 'Ollama RAG (English Only)',
            'embedding_model': 'all-MiniLM-L6-v2',
            'vector_db': 'FAISS',
            'total_documents': total_documents,
            'total_services': total_services_with_docs,
            'ollama_available': True,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    finally:
        db.close()


@rag_bp.route('/test', methods=['GET'])
def test_rag():
    """
    Test RAG system with sample data
    """
    try:
        # Create a test service
        test_service_id = "test-service-123"
        rag_service = get_rag_service(test_service_id)
        
        # Test document
        test_doc = """
        Q: What is MarketMatic?
        A: MarketMatic is a digital marketing platform that helps businesses automate their marketing campaigns.
        
        Q: How does it work?
        A: MarketMatic uses AI to analyze customer data and create personalized marketing strategies.
        """
        
        # Add test document
        result = rag_service.rag_system.add_documents([{
            'text': test_doc,
            'metadata': {'test': True}
        }])
        
        if not result['success']:
            return jsonify({'error': 'Failed to add test document'}), 500
        
        # Test query
        query_result = rag_service.rag_system.query("What is MarketMatic?")
        
        return jsonify({
            'success': True,
            'test_results': {
                'document_added': result,
                'query_result': query_result
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


# ============== UTILITY ENDPOINTS ==============

# Test endpoint removed - use /status instead

        
        return jsonify({
            'message': 'RAG system test successful',
            'document_processor': 'working',
            'chunks_created': len(chunks),
            'vector_service': status,
            'timestamp': datetime.utcnow().isoformat()
        }), 200

# ============== END OF ROUTES ==============

