from datetime import datetime
from database import db_instance
from bson import ObjectId
import uuid

class Document:
    """Model for storing uploaded documents metadata"""
    
    # Document categories for better organization
    DOCUMENT_TYPES = {
        'faq': 'Frequently Asked Questions',
        'product': 'Product Information',
        'policy': 'Policies & Terms',
        'store': 'Store Details & Information',
        'general': 'General Documents'
    }
    
    @staticmethod
    def create(data):
        document = {
            'service_id': data['service_id'],
            'filename': data['filename'],
            'file_type': data['file_type'],  # 'pdf', 'excel', 'text', 'docx', 'txt'
            'document_type': data.get('document_type', 'general'),  # 'faq', 'product', 'policy', 'store', 'general'
            'file_url': data.get('file_url'),  # Cloudinary URL if applicable
            'content': data.get('content'),  # Extracted text content
            'content_preview': data.get('content_preview', ''),  # First 500 chars for preview
            'metadata': data.get('metadata', {}),  # Additional info
            'chunk_ids': data.get('chunk_ids', []),  # IDs of text chunks in vector DB
            'chunks_count': data.get('chunks_count', 0),  # Number of chunks created
            'file_size': data.get('file_size', 0),  # File size in bytes
            'status': data.get('status', 'processing'),  # 'processing', 'completed', 'failed'
            'error_message': data.get('error_message'),
            'is_active': data.get('is_active', True),  # For soft delete
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        db = db_instance.get_db()
        result = db.documents.insert_one(document)
        document['_id'] = result.inserted_id
        return document
    
    @staticmethod
    def find_by_id(doc_id):
        db = db_instance.get_db()
        return db.documents.find_one({'_id': ObjectId(doc_id)})
    
    @staticmethod
    def find_by_service(service_id, document_type=None, is_active=True):
        db = db_instance.get_db()
        query = {'service_id': service_id, 'is_active': is_active}
        if document_type:
            query['document_type'] = document_type
        return list(db.documents.find(query).sort('created_at', -1))
    
    @staticmethod
    def update(doc_id, data):
        data['updated_at'] = datetime.utcnow()
        db = db_instance.get_db()
        db.documents.update_one(
            {'_id': ObjectId(doc_id)},
            {'$set': data}
        )
        return Document.find_by_id(doc_id)
    
    @staticmethod
    def delete(doc_id):
        db = db_instance.get_db()
        result = db.documents.delete_one({'_id': ObjectId(doc_id)})
        return result.deleted_count > 0
    
    @staticmethod
    def soft_delete(doc_id):
        """Soft delete by marking as inactive"""
        data = {
            'is_active': False,
            'updated_at': datetime.utcnow()
        }
        db = db_instance.get_db()
        result = db.documents.update_one(
            {'_id': ObjectId(doc_id)},
            {'$set': data}
        )
        return result.matched_count > 0
    
    @staticmethod
    def serialize(doc):
        """Serialize document for JSON response"""
        if doc:
            return {
                'id': str(doc['_id']),
                'service_id': doc['service_id'],
                'filename': doc['filename'],
                'file_type': doc['file_type'],
                'document_type': doc.get('document_type', 'general'),
                'file_url': doc.get('file_url'),
                'content_preview': doc.get('content_preview', ''),
                'metadata': doc.get('metadata', {}),
                'chunks_count': doc.get('chunks_count', 0),
                'file_size': doc.get('file_size', 0),
                'status': doc.get('status', 'processing'),
                'error_message': doc.get('error_message'),
                'is_active': doc.get('is_active', True),
                'created_at': doc['created_at'].isoformat() if isinstance(doc['created_at'], datetime) else doc['created_at'],
                'updated_at': doc['updated_at'].isoformat() if isinstance(doc['updated_at'], datetime) else doc['updated_at']
            }
        return None
    
    @staticmethod
    def get_stats_by_service(service_id):
        """Get document statistics for a service"""
        db = db_instance.get_db()
        pipeline = [
            {'$match': {'service_id': service_id, 'is_active': True}},
            {'$group': {
                '_id': '$document_type',
                'count': {'$sum': 1},
                'total_chunks': {'$sum': '$chunks_count'},
                'completed': {'$sum': {'$cond': [{'$eq': ['$status', 'completed']}, 1, 0]}},
                'failed': {'$sum': {'$cond': [{'$eq': ['$status', 'failed']}, 1, 0]}}
            }}
        ]
        return list(db.documents.aggregate(pipeline))
    
    @staticmethod
    def get_by_status(service_id, status):
        db = db_instance.get_db()
        return list(db.documents.find({
            'service_id': ObjectId(service_id),
            'status': status
        }))


class ChatMessage:
    """Model for storing chat messages"""
    
    @staticmethod
    def create(service_id, session_id, role, message, language='en', intent=None, confidence=None, context_used=None):
        msg = {
            'service_id': service_id,
            'session_id': session_id,
            'role': role,  # 'user' or 'assistant'
            'message': message,
            'language': language,
            'intent': intent,
            'confidence': confidence,
            'context_used': context_used,
            'timestamp': datetime.utcnow()
        }
        db = db_instance.get_db()
        result = db.chat_messages.insert_one(msg)
        msg['_id'] = result.inserted_id
        return msg
    
    @staticmethod
    def get_session_history(session_id, limit=10):
        db = db_instance.get_db()
        return list(db.chat_messages.find(
            {'session_id': session_id}
        ).sort('timestamp', -1).limit(limit))
    
    @staticmethod
    def get_service_history(service_id, limit=50):
        db = db_instance.get_db()
        return list(db.chat_messages.find(
            {'service_id': service_id}
        ).sort('timestamp', -1).limit(limit))
    
    @staticmethod
    def delete_session_messages(session_id):
        db = db_instance.get_db()
        result = db.chat_messages.delete_many({'session_id': session_id})
        return result.deleted_count


class ChatSession:
    """Model for managing chat sessions"""
    
    @staticmethod
    def create(service_id):
        session = {
            'session_id': str(uuid.uuid4()),
            'service_id': service_id,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'is_active': True,
            'message_count': 0,
            'user_info': {}
        }
        db = db_instance.get_db()
        result = db.chat_sessions.insert_one(session)
        session['_id'] = result.inserted_id
        return session
    
    @staticmethod
    def find_by_session_id(session_id):
        db = db_instance.get_db()
        return db.chat_sessions.find_one({'session_id': session_id})
    
    @staticmethod
    def update_activity(session_id):
        db = db_instance.get_db()
        db.chat_sessions.update_one(
            {'session_id': session_id},
            {'$set': {'last_activity': datetime.utcnow()}}
        )
    
    @staticmethod
    def increment_message_count(session_id):
        db = db_instance.get_db()
        db.chat_sessions.update_one(
            {'session_id': session_id},
            {'$inc': {'message_count': 1}}
        )
    
    @staticmethod
    def end_session(session_id):
        db = db_instance.get_db()
        db.chat_sessions.update_one(
            {'session_id': session_id},
            {'$set': {'is_active': False, 'ended_at': datetime.utcnow()}}
        )
    
    @staticmethod
    def get_active_sessions(service_id):
        db = db_instance.get_db()
        return list(db.chat_sessions.find({
            'service_id': service_id,
            'is_active': True
        }))
    
    @staticmethod
    def cleanup_old_sessions(hours=24):
        from datetime import timedelta
        db = db_instance.get_db()
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        result = db.chat_sessions.delete_many({
            'last_activity': {'$lt': cutoff_time}
        })
        return result.deleted_count