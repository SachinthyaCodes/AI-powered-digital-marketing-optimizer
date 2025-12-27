"""
RAG Routes for MarketMatic using SQLAlchemy and pgvector
Document processing, embedding generation, and semantic search
"""
from flask import Blueprint, request, jsonify
from database import SessionLocal
from models.sqlalchemy_models import Document, DocumentEmbedding, User, Service
from auth.decorators import admin_required
from services.document_processor import DocumentProcessor
from services.vector_service import VectorService
from utils.cloudinary_service import CloudinaryService
from datetime import datetime
import uuid
import traceback

rag_bp = Blueprint('rag', __name__, url_prefix='/api/rag')

# Initialize services
document_processor = DocumentProcessor()
vector_service = VectorService()
cloudinary_service = CloudinaryService()


# ============== ADMIN ENDPOINTS ==============

@rag_bp.route('/upload-document', methods=['POST'])
@admin_required
def upload_document():
    """
    Upload and process a document (PDF, Excel, Word, Text)
    Extracts content, generates embeddings with pgvector, and stores in database
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
        
        # Create document record
        doc = Document(
            id=str(uuid.uuid4()),
            service_id=service_id,
            filename=file.filename,
            file_type=file_ext,
            status='processing'
        )
        
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        try:
            # Process file based on type
            if file_ext == 'pdf':
                content = document_processor.process_pdf(file_content)
            elif file_ext in ['xlsx', 'xls']:
                content = document_processor.process_excel(file_content)
            elif file_ext == 'docx':
                content = document_processor.process_docx(file_content)
            else:  # txt
                content = file_content.decode('utf-8', errors='ignore')
            
            if not content:
                doc.status = 'failed'
                doc.error_message = 'No content extracted from document'
                db.commit()
                return jsonify({
                    'error': 'Could not extract content from document',
                    'document_id': str(doc.id)
                }), 400
            
            # Split content into chunks and generate embeddings using pgvector
            chunks = document_processor.chunk_text(content, chunk_size=512, chunk_overlap=50)
            
            # Generate embeddings and store in database using pgvector
            embedding_ids = vector_service.add_document_embeddings(
                document_id=doc.id,
                service_id=service_id,
                chunks=chunks,
                db_session=db
            )
            
            # Update document status
            doc.status = 'completed'
            doc.chunk_count = len(chunks)
            doc.processed_at = datetime.utcnow()
            db.commit()
            db.refresh(doc)
            
            return jsonify({
                'message': 'Document uploaded and processed successfully',
                'document': doc.to_dict(),
                'chunks_processed': len(chunks),
                'embeddings_created': len(embedding_ids)
            }), 201
            
        except Exception as e:
            db.rollback()
            doc.status = 'failed'
            doc.error_message = str(e)
            db.commit()
            
            return jsonify({
                'error': f'Error processing document: {str(e)}',
                'document_id': str(doc.id)
            }), 500
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Error uploading document: {str(e)}'}), 500
    finally:
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
        db.query(DocumentEmbedding).filter(
            DocumentEmbedding.document_id == doc.id
        ).delete()
        
        # Delete document
        db.delete(doc)
        db.commit()
        
        return jsonify({'message': 'Document deleted successfully'}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Error deleting document: {str(e)}'}), 500
    finally:
        db.close()


# ============== SEARCH ENDPOINTS ==============

@rag_bp.route('/search', methods=['POST'])
def search_documents():
    """
    Search documents using semantic similarity with pgvector
    """
    db = SessionLocal()
    try:
        data = request.get_json()
        
        if not data or 'query' not in data or 'service_id' not in data:
            return jsonify({'error': 'query and service_id are required'}), 400
        
        query = data['query'].strip()
        service_id = uuid.UUID(data['service_id'])
        limit = data.get('limit', 5)
        
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Get vector service status
        status = vector_service.get_status()
        if not status.get('available'):
            return jsonify({'error': 'Vector service is not available'}), 503
        
        # Search similar documents
        results = vector_service.search_similar_documents(
            query=query,
            service_id=service_id,
            limit=limit,
            db_session=db
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


@rag_bp.route('/status', methods=['GET'])
def get_rag_status():
    """
    Get RAG system status
    """
    try:
        status = vector_service.get_status()
        
        return jsonify({
            'status': 'operational' if status.get('available') else 'unavailable',
            'vector_service': status,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


# ============== UTILITY ENDPOINTS ==============

@rag_bp.route('/test', methods=['GET'])
def test_rag():
    """
    Test RAG system
    """
    try:
        # Test document processor
        test_text = "This is a test document for RAG system. It contains multiple sentences. Each sentence adds information."
        chunks = document_processor.chunk_text(test_text, chunk_size=50)
        
        # Test vector service
        status = vector_service.get_status()
        
        return jsonify({
            'message': 'RAG system test successful',
            'document_processor': 'working',
            'chunks_created': len(chunks),
            'vector_service': status,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'RAG system test failed: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
