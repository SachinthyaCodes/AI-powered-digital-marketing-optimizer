"""
Chat Routes for MarketMatic Smart Assistant
Handles real-time customer interactions with the AI chatbot
Integrates with Modal RAG service and enhanced vector database
"""
from flask import Blueprint, request, jsonify
from bson import ObjectId
from database import db_instance
from auth.decorators import admin_required
from models.chat_models import ChatSession, ChatMessage
from services.vector_service import VectorDatabaseService
from services.modal_service import ModalService
import datetime
import uuid
import requests
import os
import re
from typing import List, Dict, Any, Tuple

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Get database instance
db = db_instance.get_db()

class LanguageDetector:
    """Simple language detection for Sinhala/English/Tamil"""
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect language of input text
        Returns: 'si', 'ta', 'en', or 'mixed'
        """
        # Sinhala Unicode range: 0D80-0DFF
        sinhala_chars = len(re.findall(r'[\u0D80-\u0DFF]', text))
        # Tamil Unicode range: 0B80-0BFF
        tamil_chars = len(re.findall(r'[\u0B80-\u0BFF]', text))
        # English characters
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        total_chars = len(text.replace(' ', '').replace('\n', '').replace('\t', ''))
        
        if total_chars == 0:
            return 'en'
        
        # Calculate percentages
        sinhala_pct = sinhala_chars / total_chars
        tamil_pct = tamil_chars / total_chars
        english_pct = english_chars / total_chars
        
        # Determine dominant language
        if sinhala_pct > 0.3:
            if english_pct > 0.2:
                return 'mixed'  # Code-mixed Sinhala-English
            return 'si'
        elif tamil_pct > 0.3:
            if english_pct > 0.2:
                return 'mixed'  # Code-mixed Tamil-English
            return 'ta'
        elif english_pct > 0.5:
            return 'en'
        else:
            return 'mixed'

class IntentClassifier:
    """Rule-based intent classification for customer queries"""
    
    # Intent patterns with multilingual support
    INTENT_PATTERNS = {
        'product_inquiry': {
            'en': ['what products', 'do you sell', 'available items', 'catalog', 'inventory', 'stock'],
            'si': ['නිෂ්පාදන', 'භාණඩ', 'කුමක් විකුණනවාද', 'තිබේද', 'ලැයිස්තුව'],
            'ta': ['தயாரிப்புகள்', 'பொருட்கள்', 'என்ன விற்கிறீர்கள்']
        },
        'pricing': {
            'en': ['price', 'cost', 'how much', 'rate', 'fee', 'charge'],
            'si': ['මිල', 'කීයද', 'වියදම', 'ගාස්තුව', 'ගණන්'],
            'ta': ['விலை', 'எவ்வளவு', 'கட்டணம்', 'செலவு']
        },
        'order_tracking': {
            'en': ['order status', 'tracking', 'delivery', 'shipped', 'when will'],
            'si': ['ඇණවුම', 'ට්‍රැකිං', 'බෙදාහැරීම', 'කවදා ලැබේද', 'ස්ථිතිය'],
            'ta': ['ஆர்டர்', 'டிராக்கிங்', 'டெலிவரி', 'எப்போது வரும்']
        },
        'delivery_info': {
            'en': ['delivery', 'shipping', 'location', 'area', 'transport'],
            'si': ['බෙදාහැරීම', 'ප්‍රදේශ', 'ප්‍රවාහනය', 'ගෙන්වා දෙනවාද'],
            'ta': ['டெலிவரி', 'இடம்', 'போக்குவரத்து', 'பகுதி']
        },
        'payment': {
            'en': ['payment', 'pay', 'card', 'cash', 'bank'],
            'si': ['ගෙවීම', 'පේමන්ට්', 'කාර්ඩ්', 'මුදල්', 'බැංකු'],
            'ta': ['பேமெண்ட்', 'பணம்', 'கார்ட்', 'வங்கி']
        },
        'complaint': {
            'en': ['complaint', 'problem', 'issue', 'wrong', 'defective', 'damaged'],
            'si': ['පැමිණිල්ල', 'ගැටලුව', 'වරදයි', 'හානි', 'දෝෂය'],
            'ta': ['புகார்', 'பிரச்சனை', 'தவறு', 'சேதம்']
        },
        'greeting': {
            'en': ['hello', 'hi', 'good morning', 'good afternoon', 'good evening'],
            'si': ['හෙලෝ', 'හායි', 'සුභ උදෑසනක්', 'සුභ දවසක්', 'සුභ සවසක්'],
            'ta': ['வணக்கம்', 'ஹலோ', 'காலை வணக்கம்', 'மாலை வணக்கம්']
        }
    }
    
    @classmethod
    def classify_intent(cls, text: str, language: str = 'en') -> str:
        """
        Classify intent of user message
        Returns intent name or 'general' if no match
        """
        text_lower = text.lower()
        
        # Check each intent
        for intent, patterns in cls.INTENT_PATTERNS.items():
            # Get patterns for detected language, fallback to English
            lang_patterns = patterns.get(language, patterns.get('en', []))
            
            # Also check English patterns for mixed language
            if language == 'mixed':
                lang_patterns.extend(patterns.get('en', []))
            
            # Check if any pattern matches
            for pattern in lang_patterns:
                if pattern.lower() in text_lower:
                    return intent
        
        return 'general'

class RAGService:
    """Integration with Enhanced Vector Database and Modal RAG service"""
    
    def __init__(self):
        self.vector_service = VectorDatabaseService()
        self.modal_service = ModalService()
    
    def get_relevant_context(self, query: str, service_id: str, intent: str, language: str = 'en') -> str:
        """
        Retrieve relevant context using enhanced semantic search
        """
        try:
            # Use vector database for semantic search
            search_results = self.vector_service.semantic_search(
                service_id=service_id,
                query=query,
                intent=intent,
                language=language,
                limit=8
            )
            
            context = search_results.get('context', '')
            
            # If no context found from vectors, fall back to basic retrieval
            if not context or context == "No relevant information found.":
                context = self._get_fallback_context(service_id, intent)
            
            return context
            
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return self._get_fallback_context(service_id, intent)
    
    def _get_fallback_context(self, service_id: str, intent: str) -> str:
        """
        Fallback context retrieval when vector search fails
        """
        context_parts = []
        
        try:
            # Get bot configuration for fallback messages
            config = db.bot_configurations.find_one({'service_id': service_id})
            
            if intent == 'greeting':
                if config and config.get('welcome_message'):
                    return config['welcome_message'].get('en', '') + '\n' + config['welcome_message'].get('si', '')
            
            # Search FAQs for relevant information
            if intent in ['product_inquiry', 'general', 'faq']:
                faqs = db.faqs.find({'service_id': service_id, 'is_active': True}).limit(3)
                for faq in faqs:
                    context_parts.append(f"Q: {faq.get('question', '')}\nA: {faq.get('answer', '')}")
            
            # Get product information for product-related queries
            if intent in ['product_inquiry', 'pricing']:
                products = db.products.find({'service_id': service_id, 'is_active': True}).limit(5)
                product_info = []
                for product in products:
                    product_info.append(f"{product.get('name', '')}: Rs. {product.get('price', 'N/A')} - {product.get('description', '')}")
                
                if product_info:
                    context_parts.append("Available Products:\n" + "\n".join(product_info))
            
            # Get relevant policies
            if intent in ['delivery_info', 'payment', 'complaint', 'policy']:
                policies = db.policies.find({'service_id': service_id, 'is_active': True}).limit(2)
                for policy in policies:
                    context_parts.append(f"{policy.get('title', '')}: {policy.get('content', '')}")
            
            # Combine all context
            full_context = "\n\n".join(context_parts)
            
            # If no specific context found, use fallback
            if not full_context.strip() and config:
                fallback = config.get('fallback_message', {})
                full_context = fallback.get('en', 'I am here to help you with any questions about our products and services.')
            
            return full_context
            
        except Exception as e:
            print(f"Error in fallback context: {e}")
            return "I am here to help you with any questions about our products and services."
    
    def generate_response(self, query: str, context: str, language: str = 'en', 
                         conversation_history: List[Dict] = None) -> str:
        """
        Generate response using Modal chat service with enhanced context
        """
        try:
            # Use Modal service for response generation
            response = self.modal_service.generate_chat_response(
                query=query,
                context=context,
                conversation_history=conversation_history or [],
                language=language,
                max_tokens=300,
                temperature=0.7
            )
            
            return response
                
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._get_fallback_response(language)
    
    def _get_fallback_response(self, language: str) -> str:
        """Fallback responses when AI service is unavailable"""
        fallbacks = {
            'en': "Thank you for your message. I'm here to help you with information about our products and services. Could you please be more specific about what you're looking for?",
            'si': "ඔබේ පණිවිඩයට ස්තූතියි. අපගේ නිෂ්පාදන සහ සේවා පිළිබඳ තොරතුරු සමඟ ඔබට උදව් කිරීමට මම මෙහි සිටිමි. කරුණාකර ඔබ සොයන දේ ගැන වඩාත් නිශ්චිතව කියන්න?",
            'ta': "உங்கள் செய்திக்கு நன்றி. எங்கள் தயாரிப்புகள் மற்றும் சேவைகள் பற்றிய தகவல்களுடன் உங்களுக்கு உதவ நான் இங்கே இருக்கிறேன். நீங்கள் தேடுவது என்ன என்பதை மேலும் குறிப்பிட்டு சொல்ல முடியுமா?"
        }
        return fallbacks.get(language, fallbacks['en'])

# Initialize services
rag_service = RAGService()
language_detector = LanguageDetector()
intent_classifier = IntentClassifier()

@chat_bp.route('/send-message', methods=['POST'])
def send_message():
    """
    Handle customer chat messages
    Process with NLP and return AI-generated response
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'message' not in data or 'service_id' not in data:
            return jsonify({
                'error': 'Missing required fields: message, service_id'
            }), 400
        
        message = data['message'].strip()
        service_id = data['service_id']
        session_id = data.get('session_id', str(uuid.uuid4()))
        user_name = data.get('user_name', 'Guest')
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Detect language and classify intent
        detected_language = language_detector.detect_language(message)
        intent = intent_classifier.classify_intent(message, detected_language)
        
        # Get conversation history
        conversation_history = get_conversation_history(session_id, service_id)
        
        # Get relevant context from bot data
        context = rag_service.get_relevant_context(message, service_id, intent)
        
        # Generate AI response
        ai_response = rag_service.generate_response(
            query=message,
            context=context,
            language=detected_language,
            conversation_history=conversation_history
        )
        
        # Store conversation in database
        timestamp = datetime.datetime.utcnow()
        
        # Store user message
        user_message = {
            'session_id': session_id,
            'service_id': service_id,
            'user_name': user_name,
            'message': message,
            'sender': 'user',
            'timestamp': timestamp,
            'language': detected_language,
            'intent': intent
        }
        db.chat_messages.insert_one(user_message)
        
        # Store bot response
        bot_message = {
            'session_id': session_id,
            'service_id': service_id,
            'user_name': user_name,
            'message': ai_response,
            'sender': 'bot',
            'timestamp': timestamp,
            'language': detected_language,
            'intent': intent,
            'context_used': context[:100] + '...' if len(context) > 100 else context
        }
        db.chat_messages.insert_one(bot_message)
        
        # Update or create session
        db.chat_sessions.update_one(
            {'session_id': session_id, 'service_id': service_id},
            {
                '$set': {
                    'user_name': user_name,
                    'last_activity': timestamp,
                    'status': 'active'
                },
                '$inc': {'message_count': 2}  # User message + bot response
            },
            upsert=True
        )
        
        return jsonify({
            'response': ai_response,
            'session_id': session_id,
            'detected_language': detected_language,
            'intent': intent,
            'timestamp': timestamp.isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error in send_message: {e}")
        return jsonify({
            'error': 'An error occurred processing your message',
            'details': str(e)
        }), 500

@chat_bp.route('/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        service_id = request.args.get('service_id')
        if not service_id:
            return jsonify({'error': 'service_id parameter required'}), 400
        
        messages = db.chat_messages.find({
            'session_id': session_id,
            'service_id': service_id
        }).sort('timestamp', 1)
        
        history = []
        for msg in messages:
            history.append({
                'message': msg['message'],
                'sender': msg['sender'],
                'timestamp': msg['timestamp'].isoformat(),
                'language': msg.get('language', 'en'),
                'intent': msg.get('intent', 'general')
            })
        
        return jsonify({'history': history}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/sessions', methods=['GET'])
@admin_required
def get_chat_sessions():
    """Get all active chat sessions for a service (Admin only)"""
    try:
        service_id = request.args.get('service_id')
        if not service_id:
            return jsonify({'error': 'service_id parameter required'}), 400
        
        sessions = db.chat_sessions.find({
            'service_id': service_id
        }).sort('last_activity', -1).limit(50)
        
        session_list = []
        for session in sessions:
            session_list.append({
                'session_id': session['session_id'],
                'user_name': session.get('user_name', 'Guest'),
                'last_activity': session['last_activity'].isoformat(),
                'message_count': session.get('message_count', 0),
                'status': session.get('status', 'active')
            })
        
        return jsonify({'sessions': session_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/sync-vectors', methods=['POST'])
@admin_required
def sync_vectors_to_database(current_user):
    """
    Synchronize all business data (FAQs, Products, Policies) to vector database
    This ensures the chatbot has the latest information for semantic search
    """
    try:
        service_id = current_user['service_id']
        
        # Initialize vector service
        vector_service = VectorDatabaseService()
        
        # Perform synchronization
        results = vector_service.sync_business_data_to_vectors(service_id)
        
        if results['success']:
            return jsonify({
                'message': 'Vector database synchronized successfully',
                'results': results,
                'timestamp': datetime.datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'error': 'Synchronization failed',
                'results': results
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': f'Synchronization error: {str(e)}'
        }), 500

@chat_bp.route('/vector-status', methods=['GET'])
@admin_required
def get_vector_database_status(current_user):
    """
    Get status of vector database and synchronization history
    """
    try:
        service_id = current_user['service_id']
        
        vector_service = VectorDatabaseService()
        
        # Get sync history
        sync_history = vector_service.get_sync_history(service_id, limit=5)
        
        # Check Modal service status
        modal_status = vector_service.modal_service.check_service_available()
        
        # Count current data
        db = db_instance.get_db()
        data_counts = {
            'faqs': db.faqs.count_documents({'service_id': service_id}),
            'products': db.products.count_documents({'service_id': service_id}),
            'policies': db.policies.count_documents({'service_id': service_id})
        }
        
        return jsonify({
            'modal_service_status': modal_status,
            'data_counts': data_counts,
            'sync_history': sync_history,
            'last_sync': sync_history[0] if sync_history else None
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Status check error: {str(e)}'
        }), 500

@chat_bp.route('/clear-vectors', methods=['POST'])
@admin_required
def clear_vector_database(current_user):
    """
    Clear all vector data for the service (useful for fresh start)
    """
    try:
        service_id = current_user['service_id']
        
        vector_service = VectorDatabaseService()
        success = vector_service.clear_service_vectors(service_id)
        
        if success:
            return jsonify({
                'message': 'Vector database cleared successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Failed to clear vector database'
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': f'Clear vectors error: {str(e)}'
        }), 500
def get_chat_analytics():
    """Get basic chat analytics for a service (Admin only)"""
    try:
        service_id = request.args.get('service_id')
        if not service_id:
            return jsonify({'error': 'service_id parameter required'}), 400
        
        # Get date range (default: last 7 days)
        from_date = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        
        # Total messages
        total_messages = db.chat_messages.count_documents({
            'service_id': service_id,
            'timestamp': {'$gte': from_date}
        })
        
        # Active sessions
        active_sessions = db.chat_sessions.count_documents({
            'service_id': service_id,
            'last_activity': {'$gte': from_date}
        })
        
        # Intent distribution
        intent_pipeline = [
            {'$match': {
                'service_id': service_id,
                'sender': 'user',
                'timestamp': {'$gte': from_date}
            }},
            {'$group': {
                '_id': '$intent',
                'count': {'$sum': 1}
            }}
        ]
        intent_results = list(db.chat_messages.aggregate(intent_pipeline))
        
        # Language distribution
        language_pipeline = [
            {'$match': {
                'service_id': service_id,
                'sender': 'user',
                'timestamp': {'$gte': from_date}
            }},
            {'$group': {
                '_id': '$language',
                'count': {'$sum': 1}
            }}
        ]
        language_results = list(db.chat_messages.aggregate(language_pipeline))
        
        return jsonify({
            'total_messages': total_messages,
            'active_sessions': active_sessions,
            'intent_distribution': intent_results,
            'language_distribution': language_results,
            'period': '7 days'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_conversation_history(session_id: str, service_id: str, limit: int = 5) -> List[Dict]:
    """Get recent conversation history for context"""
    try:
        messages = db.chat_messages.find({
            'session_id': session_id,
            'service_id': service_id
        }).sort('timestamp', -1).limit(limit * 2)  # Get both user and bot messages
        
        history = []
        for msg in reversed(list(messages)):
            history.append({
                'role': 'user' if msg['sender'] == 'user' else 'assistant',
                'content': msg['message']
            })
        
        return history
        
    except Exception as e:
        print(f"Error getting conversation history: {e}")
        return []