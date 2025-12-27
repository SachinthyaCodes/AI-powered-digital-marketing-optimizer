from datetime import datetime
from bson import ObjectId

class BotConfiguration:
    def __init__(self, service_id, admin_id):
        self.service_id = service_id
        self.admin_id = admin_id
        self.is_active = True
        # No default messages - admin must configure
        self.welcome_message = ""
        self.fallback_message = ""
        self.language_support = ['en', 'si']  # English and Sinhala
        self.rag_enabled = True
        self.nlp_enabled = True
        # Response mode settings
        self.response_mode = 'hybrid'  # 'documents_only', 'hybrid'
        self.documents_only_message = "I can only answer based on the documents uploaded by the business."
        self.use_general_knowledge = True  # Whether to use general knowledge in hybrid mode
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'service_id': self.service_id,
            'admin_id': self.admin_id,
            'is_active': self.is_active,
            'welcome_message': self.welcome_message,
            'fallback_message': self.fallback_message,
            'language_support': self.language_support,
            'rag_enabled': self.rag_enabled,
            'nlp_enabled': self.nlp_enabled,
            'response_mode': self.response_mode,
            'documents_only_message': self.documents_only_message,
            'use_general_knowledge': self.use_general_knowledge,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class FAQ:
    def __init__(self, service_id, question, answer, language='en'):
        self.service_id = service_id
        self.question = question
        self.answer = answer
        self.language = language
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'service_id': self.service_id,
            'question': self.question,
            'answer': self.answer,
            'language': self.language,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Product:
    def __init__(self, service_id, name, description, price, stock, category='general', images=None):
        self.service_id = service_id
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.category = category
        self.images = images if images is not None else []
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'service_id': self.service_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'category': self.category,
            'images': self.images,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Policy:
    def __init__(self, service_id, title, content, policy_type='general'):
        self.service_id = service_id
        self.title = title
        self.content = content
        self.policy_type = policy_type  # general, return, shipping, privacy, etc.
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'service_id': self.service_id,
            'title': self.title,
            'content': self.content,
            'policy_type': self.policy_type,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
