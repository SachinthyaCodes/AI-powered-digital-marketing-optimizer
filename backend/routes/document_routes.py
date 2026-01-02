"""
Document Management Routes for MarketMatic
Redirects to RAG routes for actual document processing
"""
from flask import Blueprint, request, jsonify, redirect, url_for
from database import SessionLocal
from models.sqlalchemy_models import User, Document
from auth.decorators import admin_required
from datetime import datetime
import uuid

document_bp = Blueprint('documents', __name__, url_prefix='/api/documents')

@document_bp.route('/status', methods=['GET'])
def document_status():
    """Check document management status"""
    try:
        return jsonify({
            'message': 'Document management service operational',
            'note': 'FAQs, Products, Policies now managed via /api/bot endpoints',
            'note2': 'Document upload and RAG via /api/rag endpoints',
            'status': 'ok'
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@document_bp.route('/upload', methods=['POST', 'OPTIONS'])
@admin_required
def upload_document():
    """
    Upload document - redirects to RAG service
    """
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    # Import here to avoid circular dependency
    from routes.rag_routes import upload_document as rag_upload
    return rag_upload()

@document_bp.route('/', methods=['GET'])
@admin_required
def get_documents():
    """Get all documents for admin's service with pagination"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        service_id = user.service_id
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit
        
        # Get total count
        total_count = db.query(Document).filter(Document.service_id == service_id).count()
        
        # Get paginated documents
        documents = db.query(Document).filter(
            Document.service_id == service_id
        ).order_by(
            Document.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit  # Ceiling division
        
        return jsonify({
            'documents': [doc.to_dict() for doc in documents],
            'total': total_count,
            'pagination': {
                'page': page,
                'pages': total_pages,
                'limit': limit,
                'total': total_count
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500
    finally:
        db.close()

@document_bp.route('/<document_id>', methods=['DELETE'])
@admin_required  
def delete_document(document_id):
    """Delete a document"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.service_id == user.service_id
        ).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        db.delete(document)
        db.commit()
        
        return jsonify({'message': 'Document deleted successfully'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Error: {str(e)}'}), 500
    finally:
        db.close()

@document_bp.route('/stats', methods=['GET'])
@admin_required
def get_document_stats():
    """Get document statistics for admin's service"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        service_id = user.service_id
        
        # Count documents
        total_docs = db.query(Document).filter(Document.service_id == service_id).count()
        processed_docs = db.query(Document).filter(
            Document.service_id == service_id,
            Document.is_processed == True
        ).count()
        
        return jsonify({
            'total_documents': total_docs,
            'processed_documents': processed_docs,
            'pending_documents': total_docs - processed_docs
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500
    finally:
        db.close()

@document_bp.route('/health', methods=['GET'])
def health():
    """Health check for document service"""
    try:
        db = SessionLocal()
        user_count = db.query(User).count()
        db.close()
        
        return jsonify({
            'status': 'healthy',
            'users': user_count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
