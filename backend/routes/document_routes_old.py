"""
Enhanced Document Management Routes for MarketMatic
Supports different document types: FAQs, Products, Policies, Store Details
Full CRUD operations with proper categorization
"""
from flask import Blueprint, request, jsonify
from auth.decorators import admin_required
from services.document_processor import DocumentProcessor
from services.ollama_service import get_ollama_service
from services.vector_service import get_vector_service
from utils.cloudinary_service import CloudinaryService
from models.document import Document
from database import db_instance
import traceback
from datetime import datetime
import os

document_bp = Blueprint('documents', __name__, url_prefix='/api/documents')

# Initialize services
document_processor = DocumentProcessor()
cloudinary_service = CloudinaryService()

def get_ai_service():
    """Get Ollama AI service with Llama3"""
    return get_ollama_service()

class FAQ:
    def __init__(self, service_id, question, answer, language='en'):
        self.service_id = service_id
        self.question = question
        self.answer = answer
        self.language = language
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'service_id': self.service_id,
            'question': self.question,
            'answer': self.answer,
            'language': self.language,
            'created_at': self.created_at
        }

class Product:
    def __init__(self, service_id, name, description='', price=0.0, stock=0, category='general'):
        self.service_id = service_id
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.category = category
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'service_id': self.service_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'category': self.category,
            'created_at': self.created_at
        }

class Policy:
    def __init__(self, service_id, title, content, policy_type='general'):
        self.service_id = service_id
        self.title = title
        self.content = content
        self.policy_type = policy_type
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'service_id': self.service_id,
            'title': self.title,
            'content': self.content,
            'policy_type': self.policy_type,
            'created_at': self.created_at
        }


# ============== DOCUMENT MANAGEMENT ==============

@document_bp.route('/', methods=['GET'])
@admin_required
def get_documents(current_user):
    """Get all documents for admin's service with filtering"""
    try:
        service_id = current_user['service_id']
        
        # Get query parameters
        document_type = request.args.get('type')  # faq, product, policy, store, general
        status = request.args.get('status')  # processing, completed, failed
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Build query
        query = {'service_id': service_id, 'is_active': True}
        if document_type:
            query['document_type'] = document_type
        if status:
            query['status'] = status
        
        # Get documents with pagination
        db = db_instance.get_db()
        total = db.documents.count_documents(query)
        skip = (page - 1) * limit
        
        documents = list(
            db.documents.find(query)
            .sort('created_at', -1)
            .skip(skip)
            .limit(limit)
        )
        
        # Serialize documents
        serialized_docs = [Document.serialize(doc) for doc in documents]
        
        # Get statistics
        stats = Document.get_stats_by_service(service_id)
        
        return jsonify({
            'documents': serialized_docs,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            },
            'statistics': stats,
            'document_types': Document.DOCUMENT_TYPES
        }), 200
        
    except Exception as e:
        print(f"Error fetching documents: {str(e)}")
        return jsonify({'error': str(e)}), 500


@document_bp.route('/upload', methods=['POST'])
@admin_required
def upload_document():
    """Upload and process a document with type categorization"""
    try:
        # Get current user from request context
        current_user = request.current_user
        service_id = current_user.get('service_id', current_user.get('user_id', 'default_service'))
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get document type from form data
        document_type = request.form.get('document_type', 'general')
        if document_type not in Document.DOCUMENT_TYPES:
            return jsonify({'error': 'Invalid document type'}), 400
        
        # Get file extension and validate
        file_ext = file.filename.rsplit('.', 1)[-1].lower()
        allowed_extensions = ['pdf', 'docx', 'xlsx', 'xls', 'txt']
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}), 400
        
        # Read file content
        file_content = file.read()
        file_size = len(file_content)
        
        # Create document record
        doc_data = {
            'service_id': service_id,
            'filename': file.filename,
            'file_type': file_ext,
            'document_type': document_type,
            'file_size': file_size,
            'status': 'processing'
        }
        
        doc = Document.create(doc_data)
        doc_id = str(doc['_id'])
        
        try:
            # Upload to Cloudinary
            cloudinary_result = cloudinary_service.upload_file(
                file_content,
                f"documents/{service_id}/{doc_id}",
                folder=f"marketmatic/{service_id}/documents",
                resource_type="auto"
            )
            
            if cloudinary_result:
                Document.update(doc['_id'], {'file_url': cloudinary_result['url']})
            
            # Process file based on type
            content = ""
            if file_ext == 'pdf':
                content = document_processor.process_pdf(file_content)
            elif file_ext in ['xlsx', 'xls']:
                content = document_processor.process_excel(file_content)
            elif file_ext == 'docx':
                content = document_processor.process_word(file_content)
            else:  # txt
                content = document_processor.process_text(file_content)
            
            if not content or not content.strip():
                Document.update(doc['_id'], {
                    'status': 'failed',
                    'error_message': 'No content extracted from file'
                })
                return jsonify({'error': 'No content could be extracted from file'}), 400
            
            # Create content preview
            content_preview = content[:500] + "..." if len(content) > 500 else content
            
            # Chunk the content
            chunks = document_processor.chunk_text(content)
            
            # Generate embeddings and add to vector DB
            metadata = {
                'document_id': doc_id,
                'filename': file.filename,
                'file_type': file_ext,
                'document_type': document_type,
                'service_id': service_id,
                'source': 'upload'
            }
            
            # Use Ollama for document embeddings
            ai_service = get_ai_service()
            num_chunks = ai_service.add_documents(
                service_id=service_id,
                chunks=chunks,
                metadata=metadata
            )
            
            # Extract metadata
            doc_metadata = document_processor.extract_metadata(file.filename, file_ext, content)
            
            # Update document record
            Document.update(doc['_id'], {
                'status': 'completed',
                'content': content,
                'content_preview': content_preview,
                'chunks_count': num_chunks,
                'metadata': doc_metadata
            })
            
            # If document type is FAQ, Product, or Policy, also process and add to respective collections
            db = db_instance.get_db()
            
            if document_type == 'faq':
                # Process FAQs from document content
                faq_data = extract_faqs_from_content(content)
                for faq in faq_data:
                    faq_record = FAQ(
                        service_id=service_id,
                        question=faq['question'],
                        answer=faq['answer'],
                        language='en'
                    )
                    db.faqs.insert_one(faq_record.to_dict())
            
            elif document_type == 'product':
                # Process products from document content  
                product_data = extract_products_from_content(content)
                for product in product_data:
                    product_record = Product(
                        service_id=service_id,
                        name=product['name'],
                        description=product.get('description', ''),
                        price=float(product.get('price', 0)),
                        stock=int(product.get('stock', 0)),
                        category=product.get('category', 'general')
                    )
                    db.products.insert_one(product_record.to_dict())
            
            elif document_type == 'policy':
                # Process policies from document content
                policy_data = extract_policies_from_content(content)
                for policy in policy_data:
                    policy_record = Policy(
                        service_id=service_id,
                        title=policy['title'],
                        content=policy['content'],
                        policy_type=policy.get('type', 'general')
                    )
                    db.policies.insert_one(policy_record.to_dict())
            
            return jsonify({
                'message': 'Document uploaded and processed successfully',
                'document': {
                    'id': doc_id,
                    'filename': file.filename,
                    'document_type': document_type,
                    'chunks_count': num_chunks,
                    'file_size': file_size,
                    'file_url': cloudinary_result['url'] if cloudinary_result else None,
                    'status': 'completed'
                }
            }), 201
            
        except Exception as e:
            # Update document status to failed
            Document.update(doc['_id'], {
                'status': 'failed',
                'error_message': str(e)
            })
            raise
            
    except Exception as e:
        print(f"Error uploading document: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def extract_faqs_from_content(content):
    """Extract FAQ pairs from document content"""
    faqs = []
    lines = content.split('\n')
    
    current_q = ""
    current_a = ""
    in_answer = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for question patterns
        if any(q_indicator in line.lower() for q_indicator in ['q:', 'question:', '?']):
            if current_q and current_a:
                faqs.append({'question': current_q.strip(), 'answer': current_a.strip()})
            current_q = line.replace('Q:', '').replace('Question:', '').strip()
            current_a = ""
            in_answer = False
        # Look for answer patterns  
        elif any(a_indicator in line.lower() for a_indicator in ['a:', 'answer:', 'ans:']):
            current_a = line.replace('A:', '').replace('Answer:', '').replace('Ans:', '').strip()
            in_answer = True
        elif in_answer:
            current_a += " " + line
        elif current_q and not in_answer:
            current_a = line
            in_answer = True
    
    # Add the last FAQ if exists
    if current_q and current_a:
        faqs.append({'question': current_q.strip(), 'answer': current_a.strip()})
    
    return faqs


def extract_products_from_content(content):
    """Extract product information from document content"""
    products = []
    lines = content.split('\n')
    
    current_product = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for product patterns (name, price, stock, description)
        if any(keyword in line.lower() for keyword in ['product:', 'name:', 'item:']):
            if current_product.get('name'):
                products.append(current_product.copy())
                current_product = {}
            current_product['name'] = line.split(':', 1)[-1].strip()
        elif any(keyword in line.lower() for keyword in ['price:', 'cost:', 'rs.', '$']):
            price_text = line.split(':', 1)[-1].strip()
            # Extract numeric value
            import re
            price_match = re.search(r'[\d,]+\.?\d*', price_text)
            if price_match:
                current_product['price'] = price_match.group().replace(',', '')
        elif any(keyword in line.lower() for keyword in ['stock:', 'quantity:', 'qty:']):
            stock_text = line.split(':', 1)[-1].strip()
            import re
            stock_match = re.search(r'\d+', stock_text)
            if stock_match:
                current_product['stock'] = stock_match.group()
        elif any(keyword in line.lower() for keyword in ['description:', 'desc:']):
            current_product['description'] = line.split(':', 1)[-1].strip()
        elif current_product.get('name') and not any(keyword in line.lower() for keyword in ['product:', 'name:', 'price:', 'stock:']):
            # Continuation of description
            if 'description' not in current_product:
                current_product['description'] = line
            else:
                current_product['description'] += " " + line
    
    # Add the last product if exists
    if current_product.get('name'):
        products.append(current_product)
    
    return products


def extract_policies_from_content(content):
    """Extract policy information from document content"""
    policies = []
    
    # Simple approach: split by major headings and treat each as a policy
    sections = content.split('\n\n')
    
    for section in sections:
        lines = section.strip().split('\n')
        if len(lines) > 1:
            title = lines[0].strip()
            content_text = '\n'.join(lines[1:]).strip()
            
            if len(title) < 100 and len(content_text) > 50:  # Basic validation
                policy_type = 'general'
                if any(keyword in title.lower() for keyword in ['return', 'refund']):
                    policy_type = 'return'
                elif any(keyword in title.lower() for keyword in ['shipping', 'delivery']):
                    policy_type = 'shipping'
                elif any(keyword in title.lower() for keyword in ['privacy']):
                    policy_type = 'privacy'
                
                policies.append({
                    'title': title,
                    'content': content_text,
                    'type': policy_type
                })
    
    return policies


@document_bp.route('/<document_id>', methods=['GET'])
@admin_required
def get_document(current_user, document_id):
    """Get a specific document"""
    try:
        service_id = current_user['service_id']
        
        doc = Document.find_by_id(document_id)
        if not doc:
            return jsonify({'error': 'Document not found'}), 404
        
        # Verify ownership
        if doc['service_id'] != service_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({
            'document': Document.serialize(doc)
        }), 200
        
    except Exception as e:
        print(f"Error fetching document: {str(e)}")
        return jsonify({'error': str(e)}), 500


@document_bp.route('/<document_id>', methods=['PUT'])
@admin_required
def update_document(current_user, document_id):
    """Update document metadata (not content)"""
    try:
        service_id = current_user['service_id']
        data = request.get_json()
        
        doc = Document.find_by_id(document_id)
        if not doc:
            return jsonify({'error': 'Document not found'}), 404
        
        # Verify ownership
        if doc['service_id'] != service_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Prepare update data
        update_data = {}
        
        if 'document_type' in data and data['document_type'] in Document.DOCUMENT_TYPES:
            update_data['document_type'] = data['document_type']
        
        if 'is_active' in data:
            update_data['is_active'] = data['is_active']
        
        if update_data:
            update_data['updated_at'] = datetime.utcnow()
            Document.update(document_id, update_data)
        
        return jsonify({'message': 'Document updated successfully'}), 200
        
    except Exception as e:
        print(f"Error updating document: {str(e)}")
        return jsonify({'error': str(e)}), 500


@document_bp.route('/<document_id>', methods=['DELETE'])
@admin_required
def delete_document(current_user, document_id):
    """Delete a document (soft delete)"""
    try:
        service_id = current_user['service_id']
        
        doc = Document.find_by_id(document_id)
        if not doc:
            return jsonify({'error': 'Document not found'}), 404
        
        # Verify ownership
        if doc['service_id'] != service_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Soft delete (mark as inactive)
        success = Document.soft_delete(document_id)
        
        if success:
            return jsonify({'message': 'Document deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete document'}), 500
        
    except Exception as e:
        print(f"Error deleting document: {str(e)}")
        return jsonify({'error': str(e)}), 500


@document_bp.route('/<document_id>/reprocess', methods=['POST'])
@admin_required
def reprocess_document(current_user, document_id):
    """Reprocess a failed document"""
    try:
        service_id = current_user['service_id']
        
        doc = Document.find_by_id(document_id)
        if not doc:
            return jsonify({'error': 'Document not found'}), 404
        
        # Verify ownership
        if doc['service_id'] != service_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if doc['status'] != 'failed':
            return jsonify({'error': 'Only failed documents can be reprocessed'}), 400
        
        # Mark as processing again
        Document.update(document_id, {
            'status': 'processing',
            'error_message': None,
            'updated_at': datetime.utcnow()
        })
        
        # Here you would implement the reprocessing logic
        # For now, just return success
        return jsonify({'message': 'Document reprocessing started'}), 200
        
    except Exception as e:
        print(f"Error reprocessing document: {str(e)}")
        return jsonify({'error': str(e)}), 500


@document_bp.route('/stats', methods=['GET'])
@admin_required
def get_document_stats(current_user):
    """Get document statistics for the service"""
    try:
        service_id = current_user['service_id']
        
        stats = Document.get_stats_by_service(service_id)
        
        # Get total documents count
        db = db_instance.get_db()
        total_docs = db.documents.count_documents({
            'service_id': service_id,
            'is_active': True
        })
        
        # Get recent uploads (last 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_uploads = db.documents.count_documents({
            'service_id': service_id,
            'is_active': True,
            'created_at': {'$gte': week_ago}
        })
        
        return jsonify({
            'statistics': stats,
            'summary': {
                'total_documents': total_docs,
                'recent_uploads': recent_uploads,
                'document_types': Document.DOCUMENT_TYPES
            }
        }), 200
        
    except Exception as e:
        print(f"Error fetching document stats: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============== BULK OPERATIONS ==============

@document_bp.route('/bulk/sync', methods=['POST'])
@admin_required
def bulk_sync_documents(current_user):
    """Sync all existing data (FAQs, products, policies) to vector DB"""
    try:
        service_id = current_user['service_id']
        data = request.get_json() or {}
        sync_types = data.get('types', ['faq', 'product', 'policy'])
        
        db = db_instance.get_db()
        results = {}
        ai_service = get_ai_service()  # Use Ollama instead of Modal
        
        # Sync FAQs
        if 'faq' in sync_types:
            faqs = list(db.faqs.find({'service_id': service_id, 'is_active': True}))
            if faqs:
                content = document_processor.process_faq(faqs)
                chunks = document_processor.chunk_text(content)
                num_chunks = ai_service.add_documents(
                    service_id, chunks, {
                        'source': 'faq',
                        'document_type': 'faq',
                        'service_id': service_id
                    }
                )
                results['faqs'] = {'count': len(faqs), 'chunks': num_chunks}
        
        # Sync products
        if 'product' in sync_types:
            products = list(db.products.find({'service_id': service_id, 'is_active': True}))
            if products:
                content = document_processor.process_products(products)
                chunks = document_processor.chunk_text(content)
                num_chunks = ai_service.add_documents(
                    service_id, chunks, {
                        'source': 'product',
                        'document_type': 'product',
                        'service_id': service_id
                    }
                )
                results['products'] = {'count': len(products), 'chunks': num_chunks}
        
        # Sync policies
        if 'policy' in sync_types:
            policies = list(db.policies.find({'service_id': service_id, 'is_active': True}))
            if policies:
                content = document_processor.process_policies(policies)
                chunks = document_processor.chunk_text(content)
                num_chunks = ai_service.add_documents(
                    service_id, chunks, {
                        'source': 'policy',
                        'document_type': 'policy',
                        'service_id': service_id
                    }
                )
                results['policies'] = {'count': len(policies), 'chunks': num_chunks}
        
        return jsonify({
            'message': 'Bulk sync completed successfully',
            'results': results
        }), 200
        
    except Exception as e:
        print(f"Error in bulk sync: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@document_bp.route('/types', methods=['GET'])
@admin_required
def get_document_types(current_user):
    """Get available document types"""
    try:
        return jsonify({
            'document_types': Document.DOCUMENT_TYPES
        }), 200
        
    except Exception as e:
        print(f"Error fetching document types: {str(e)}")
        return jsonify({'error': str(e)}), 500