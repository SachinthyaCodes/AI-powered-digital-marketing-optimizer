"""
RAG Routes for MarketMatic using Modal for Remote Inference
Document processing with SinLlama tokenizer, embeddings via Modal
INTEGRATED with Bot Management - FAQs extracted automatically
"""
from flask import Blueprint, request, jsonify
from database import SessionLocal
from models.sqlalchemy_models import Document, User, Service, FAQ
from auth.decorators import admin_required
from services.modal_rag_service import get_modal_rag_service
from datetime import datetime
import uuid
import traceback

rag_bp = Blueprint('rag', __name__, url_prefix='/api/rag')


# ══════════════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS - DOCUMENT MANAGEMENT
# ══════════════════════════════════════════════════════════════════════

@rag_bp.route('/upload-document', methods=['POST'])
@admin_required
def upload_document():
    """
    Upload and process document - INTEGRATED with Bot Management
    - Extracts text from PDF/DOCX/TXT
    - Chunks with SinLlama tokenizer  
    - Indexes in FAISS
    - Extracts FAQs automatically
    - Shows FAQs in bot management
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
        
        # Validate file type
        file_ext = file.filename.rsplit('.', 1)[-1].lower()
        allowed_extensions = ['pdf', 'docx', 'xlsx', 'xls', 'txt']
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
            }), 400
        
        # Read file
        file_content = file.read()
        
        # Initialize Modal RAG service
        modal_rag = get_modal_rag_service(service_id)
        
        # 1. Process document file
        print(f"📄 Processing {file.filename}...")
        process_result = modal_rag.process_document_file(file_content, file.filename)
        
        if not process_result['success']:
            return jsonify({'error': process_result['error']}), 400
        
        # 2. Create document record
        doc_id = str(uuid.uuid4())
        doc = Document(
            id=doc_id,
            service_id=service_id,
            filename=file.filename,
            content=process_result['text'],
            document_type=file_ext,
            file_size=len(file_content),
            is_processed=False,
            chunk_count=process_result['chunk_count']
        )
        
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        # 3. Add to RAG system and extract FAQs
        print(f"🔍 Indexing and extracting FAQs...")
        rag_result = modal_rag.add_document_to_rag(
            document_id=doc_id,
            text=process_result['text'],
            filename=file.filename,
            extract_faqs=True  # Extract FAQs automatically
        )
        
        if not rag_result['success']:
            return jsonify({
                'error': rag_result['error'],
                'document_id': doc_id
            }), 500
        
        # 4. Save extracted FAQs to database
        saved_faqs = []
        if rag_result.get('faqs'):
            print(f"💡 Saving {len(rag_result['faqs'])} FAQs to database...")
            for faq_data in rag_result['faqs']:
                faq = FAQ(
                    id=str(uuid.uuid4()),
                    service_id=service_id,
                    question=faq_data['question'],
                    answer=faq_data['answer'],
                    category='auto_extracted',
                    language='mixed',  # Auto-detect or default
                    is_active=True,
                    source='document',
                    source_document_id=doc_id
                )
                db.add(faq)
                saved_faqs.append(faq.to_dict())
            
            db.commit()
        
        # 5. Mark document as processed
        doc.is_processed = True
        doc.chunk_count = rag_result['chunks']
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded and processed successfully',
            'document_id': doc_id,
            'filename': file.filename,
            'chunks': rag_result['chunks'],
            'tokens': rag_result['tokens'],
            'faqs_extracted': len(saved_faqs),
            'faqs': saved_faqs[:5],  # Return first 5 FAQs
            'document': doc.to_dict()
        }), 201
        
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        return jsonify({'error': f'Error: {str(e)}'}), 500
    finally:
        db.close()


@rag_bp.route('/documents', methods=['GET'])
@admin_required
def get_documents():
    """Get all documents for admin's service"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        service_id = user.service_id
        
        documents = db.query(Document).filter(
            Document.service_id == service_id
        ).order_by(Document.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'documents': [doc.to_dict() for doc in documents],
            'total': len(documents)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@rag_bp.route('/documents/<document_id>', methods=['DELETE'])
@admin_required
def delete_document(document_id):
    """Delete a document (note: vector index needs manual rebuild)"""
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
        
        # Delete document
        db.delete(doc)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Document deleted successfully',
            'note': 'Vector index will be rebuilt on next upload'
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ══════════════════════════════════════════════════════════════════════
# RAG QUERY ENDPOINTS
# ══════════════════════════════════════════════════════════════════════

@rag_bp.route('/query', methods=['POST'])
def query_rag():
    """
    Query RAG system with Modal for generation
    Returns answer generated by Modal (remote) with retrieved context
    
    Body:
        question: User's question (Sinhala or English)
        service_id: Service to query
        top_k: Number of chunks to retrieve (default: 5)
        language: Response language 'si' or 'en' (default: 'si')
        use_modal: Use Modal for generation (default: True)
    """
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        
        question = data.get('question', '').strip()
        service_id = data.get('service_id')
        top_k = data.get('top_k', 5)
        language = data.get('language', 'si')
        use_modal = data.get('use_modal', True)
        
        if not question:
            return jsonify({'error': 'Question cannot be empty'}), 400
        
        if not service_id:
            return jsonify({'error': 'Service ID is required'}), 400
        
        # Initialize Modal RAG service
        modal_rag = get_modal_rag_service(service_id)
        
        # Query with Modal
        result = modal_rag.query_with_modal(
            question=question,
            top_k=top_k,
            language=language,
            use_modal=use_modal
        )
        
        return jsonify(result), 200 if result.get('success') else 500
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@rag_bp.route('/search', methods=['POST'])
def search_documents():
    """
    Search documents without generating answer
    Returns only retrieved chunks with scores
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data.get('query', '').strip()
        service_id = data.get('service_id')
        top_k = data.get('top_k', 5)
        min_score = data.get('min_score', 0.3)
        
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        if not service_id:
            return jsonify({'error': 'Service ID is required'}), 400
        
        # Search
        vector_service = VectorService(service_id=service_id)
        results = vector_service.search(
            query=query,
            top_k=top_k,
            min_score=min_score
        )
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ══════════════════════════════════════════════════════════════════════
# SYSTEM STATUS & STATS
# ══════════════════════════════════════════════════════════════════════

@rag_bp.route('/status', methods=['GET'])
def rag_status():
    """Get RAG system status"""
    try:
        service_id = request.args.get('service_id')
        
        import os
        modal_configured = bool(
            os.getenv('MODAL_EMBEDDING_URL') and 
            os.getenv('MODAL_GENERATE_URL')
        )
        
        stats = {}
        if service_id:
            modal_rag = get_modal_rag_service(service_id)
            stats = modal_rag.get_stats()
        
        return jsonify({
            'success': True,
            'rag_system': {
                'status': 'operational',
                'tokenizer': 'SinLlama Extended (139K vocab)',
                'embedding': 'Multilingual Sentence-BERT',
                'vector_db': 'FAISS',
                'model': 'Modal (Remote)' if modal_configured else 'Local Fallback'
            },
            'modal': {
                'configured': modal_configured,
                'embedding_url': bool(os.getenv('MODAL_EMBEDDING_URL')),
                'generate_url': bool(os.getenv('MODAL_GENERATE_URL')),
                'status': 'connected' if modal_configured else 'not_configured'
            },
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@rag_bp.route('/rebuild-index', methods=['POST'])
@admin_required
def rebuild_index():
    """
    Rebuild RAG index from all documents
    Useful after deleting documents or system updates
    """
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        service_id = user.service_id
        
        # Initialize Modal RAG service
        modal_rag = get_modal_rag_service(service_id)
        
        # Rebuild
        result = modal_rag.rebuild_index()
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Index rebuilt successfully',
                'documents': result.get('documents', 0),
                'chunks': result.get('chunks', 0),
                'tokens': result.get('tokens', 0)
            }), 200
        else:
            return jsonify({
                'error': result.get('error', 'Rebuild failed')
            }), 500
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# ══════════════════════════════════════════════════════════════════════
# TESTING ENDPOINT
# ══════════════════════════════════════════════════════════════════════

@rag_bp.route('/test', methods=['GET'])
def test_rag():
    """Test RAG system with sample data"""
    try:
        # Create test RAG system
        test_service_id = 'test-service-' + str(uuid.uuid4())[:8]
        modal_rag = get_modal_rag_service(test_service_id)
        
        # Sample Sinhala documents
        documents = [
            "ශ්‍රී ලංකාව දකුණු ආසියාවේ පිහිටි දිවයින රටකි. එය ඉන්දියානු සාගරයේ පිහිටා ඇත. ශ්‍රී ලංකාවේ ජනගහනය මිලියන 22 කි. කොළඹ ශ්‍රී ලංකාවේ වාණිජ අගනුවර වේ.",
            "සිංහල භාෂාව ශ්‍රී ලංකාවේ නිල භාෂාවකි. සිංහල භාෂාව කතා කරන්නේ මිලියන 17ක් පමණ ජනතාවක් විසිනි."
        ]
        
        # Index documents
        result = modal_rag.rag_system.add_documents(documents)
        
        # Test query (search only, no generation to avoid local model)
        test_query = "ශ්‍රී ලංකාවේ අගනුවර කුමක්ද?"
        search_results = modal_rag.rag_system.search(test_query, top_k=2)
        
        # Format search results safely
        formatted_results = []
        if search_results and len(search_results) > 0:
            for result_item in search_results[:2]:
                if isinstance(result_item, dict):
                    formatted_results.append({
                        'text': result_item.get('text', '')[:200],
                        'score': result_item.get('score', 0)
                    })
        
        return jsonify({
            'success': True,
            'test': 'RAG System Test',
            'indexing': {
                'documents': len(documents),
                'chunks': result.get('num_chunks', 0),
                'tokens': result.get('total_tokens', 0)
            },
            'query': test_query,
            'search_results': formatted_results,
            'note': 'Configure MODAL_GENERATE_URL in .env for answer generation'
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
