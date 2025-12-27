"""
Simplified Chat Routes for MarketMatic
Uses Ollama with Llama3 for AI-powered conversations with business-specific knowledge
"""
from flask import Blueprint, request, jsonify
from bson import ObjectId
from database import db_instance
from services.ollama_service import get_ollama_service
from datetime import datetime
import uuid
import os

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

def get_business_context(service_id: str) -> str:
    """
    Fetch all business data (FAQs, Products, Policies) for a service
    and format it as context for the AI
    """
    db = db_instance.get_db()
    context_parts = []
    
    try:
        # Get FAQs
        faqs = list(db.faqs.find({'service_id': service_id, 'is_active': True}).limit(20))
        if faqs:
            context_parts.append("=== Frequently Asked Questions ===")
            for faq in faqs:
                q = faq.get('question', '')
                a = faq.get('answer', '')
                lang = faq.get('language', 'en')
                context_parts.append(f"Q ({lang}): {q}")
                context_parts.append(f"A: {a}")
                context_parts.append("")
        
        # Get Products
        products = list(db.products.find({'service_id': service_id, 'is_active': True}).limit(30))
        if products:
            context_parts.append("=== Available Products ===")
            for product in products:
                name = product.get('name', '')
                desc = product.get('description', '')
                price = product.get('price', 0)
                stock = product.get('stock', 0)
                category = product.get('category', '')
                
                product_info = f"Product: {name}"
                if category:
                    product_info += f" (Category: {category})"
                product_info += f"\nPrice: Rs. {price}"
                product_info += f"\nStock: {stock} units"
                if desc:
                    product_info += f"\nDescription: {desc}"
                
                context_parts.append(product_info)
                context_parts.append("")
        
        # Get Policies
        policies = list(db.policies.find({'service_id': service_id, 'is_active': True}).limit(10))
        if policies:
            context_parts.append("=== Business Policies ===")
            for policy in policies:
                title = policy.get('title', '')
                content = policy.get('content', '')
                policy_type = policy.get('policy_type', '')
                
                context_parts.append(f"Policy: {title} ({policy_type})")
                context_parts.append(content)
                context_parts.append("")
        
        # Get bot configuration
        config = db.bot_configurations.find_one({'service_id': service_id})
        if config:
            welcome = config.get('welcome_message', '')
            if welcome:
                context_parts.insert(0, f"=== Welcome Message ===\n{welcome}\n")
        
        return "\n".join(context_parts)
        
    except Exception as e:
        print(f"Error getting business context: {e}")
        return "Business information is being loaded. Please ask your question."


@chat_bp.route('/message', methods=['POST'])
def send_chat_message():
    """
    Send a chat message and get AI response using Modal service
    """
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
        
        # Get business-specific context
        business_context = get_business_context(service_id)
        
        # Get conversation history from session
        db = db_instance.get_db()
        recent_messages = list(
            db.chat_messages.find({
                'session_id': session_id,
                'service_id': service_id
            }).sort('timestamp', -1).limit(6)
        )
        
        # Format conversation history for Modal
        conversation_history = []
        for msg in reversed(recent_messages):
            role = 'user' if msg['sender'] == 'user' else 'assistant'
            conversation_history.append({
                'role': role,
                'content': msg['message']
            })
        
        # Generate AI response using Ollama (local) with Modal fallback
        # Create prompt with business context
        system_prompt = f"""You are a helpful customer service assistant for this business. 
Use the following business information to answer customer questions accurately:

{business_context}

Guidelines:
- Answer questions based on the business information provided above
- Be friendly, helpful, and professional
- If asked about products, mention names, prices, and availability
- If asked about policies, quote the relevant policy
- If you don't know something, admit it politely and offer to help with something else
- Support English, Sinhala (සිංහල), and Tamil (தමிழ்) languages
- Keep responses concise and relevant"""

        # Generate AI response using Ollama with Llama3
        ollama_service = get_ollama_service()
        
        if not ollama_service.check_service_available():
            return jsonify({
                'error': 'AI service unavailable. Please make sure Ollama is running.',
                'hint': 'Run: ollama serve'
            }), 503
        
        ai_response = ollama_service.generate_chat_response(
            query=user_message,
            context=system_prompt,
            conversation_history=conversation_history,
            language='en',
            max_tokens=300,
            temperature=0.7
        )
        
        # Store messages in database
        timestamp = datetime.utcnow()
        
        # Store user message
        user_msg_doc = {
            'session_id': session_id,
            'service_id': service_id,
            'message': user_message,
            'sender': 'user',
            'timestamp': timestamp
        }
        db.chat_messages.insert_one(user_msg_doc)
        
        # Store bot response
        bot_msg_doc = {
            'session_id': session_id,
            'service_id': service_id,
            'message': ai_response,
            'sender': 'bot',
            'timestamp': timestamp
        }
        db.chat_messages.insert_one(bot_msg_doc)
        
        # Update session
        db.chat_sessions.update_one(
            {'session_id': session_id, 'service_id': service_id},
            {
                '$set': {
                    'last_activity': timestamp,
                    'status': 'active'
                },
                '$inc': {'message_count': 2}
            },
            upsert=True
        )
        
        return jsonify({
            'response': ai_response,
            'session_id': session_id,
            'timestamp': timestamp.isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({
            'error': 'Failed to process message',
            'details': str(e)
        }), 500


@chat_bp.route('/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        service_id = request.args.get('service_id')
        if not service_id:
            return jsonify({'error': 'service_id parameter required'}), 400
        
        db = db_instance.get_db()
        messages = list(
            db.chat_messages.find({
                'session_id': session_id,
                'service_id': service_id
            }).sort('timestamp', 1)
        )
        
        history = []
        for msg in messages:
            history.append({
                'message': msg['message'],
                'sender': msg['sender'],
                'timestamp': msg['timestamp'].isoformat()
            })
        
        return jsonify({'history': history}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/test', methods=['GET'])
def test_chat():
    """Test endpoint to verify chat service is working"""
    service_id = request.args.get('service_id', 'test')
    
    try:
        # Get business context
        context = get_business_context(service_id)
        
        # Test Ollama service with Llama3
        ollama_service = get_ollama_service()
        
        if not ollama_service.check_service_available():
            return jsonify({
                'status': 'error',
                'ai_service': 'ollama',
                'error': 'Ollama is not running. Please start it with: ollama serve'
            }), 503
        
        test_response = ollama_service.generate_chat_response(
            query="Hello",
            context=context[:500],
            conversation_history=[],
            language='en',
            max_tokens=100,
            temperature=0.7
        )
        
        return jsonify({
            'status': 'operational',
            'ai_service': 'ollama-llama3',
            'context_length': len(context),
            'test_response': test_response
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


# ==================== DEMO CHATBOT ENDPOINTS ====================

@chat_bp.route('/demo/message', methods=['POST'])
def send_demo_message():
    """
    Demo chatbot endpoint - uses Ollama Llama3 with business-specific knowledge
    No authentication required for demo purposes
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data or 'service_id' not in data:
            return jsonify({
                'error': 'Missing required fields: message, service_id'
            }), 400
        
        user_message = data['message'].strip()
        service_id = data['service_id']
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get business-specific context
        business_context = get_business_context(service_id)
        
        # Get conversation history
        db = db_instance.get_db()
        recent_messages = list(
            db.chat_messages.find({
                'session_id': session_id,
                'service_id': service_id
            }).sort('timestamp', -1).limit(6)
        )
        
        # Format conversation history
        conversation_history = []
        for msg in reversed(recent_messages):
            role = 'user' if msg['sender'] == 'user' else 'assistant'
            conversation_history.append({
                'role': role,
                'content': msg['message']
            })
        
        # Get bot configuration if exists
        bot_config = db.bot_configurations.find_one({'service_id': service_id})
        bot_name = bot_config.get('bot_name', 'Assistant') if bot_config else 'Assistant'
        
        # Create system prompt with business context
        system_prompt = f"""You are {bot_name}, a helpful AI assistant for this business.

Use the following business information to answer customer questions accurately:

{business_context}

Guidelines:
- Answer based on the business information provided above
- Be friendly, helpful, and professional
- If asked about products, mention names, prices, and availability
- If asked about FAQs, provide accurate answers
- If asked about policies, quote the relevant policy
- Support both English and Sinhala (සිංහල) languages
- Keep responses concise and relevant
- If you don't know something, admit it politely"""

        # Generate AI response using Ollama with Llama3
        ollama_service = get_ollama_service()
        
        if not ollama_service.check_service_available():
            return jsonify({
                'error': 'AI service unavailable. Please make sure Ollama is running.',
                'hint': 'Run: ollama serve'
            }), 503
        
        ai_response = ollama_service.generate_chat_response(
            query=user_message,
            context=system_prompt,
            conversation_history=conversation_history,
            language='en',
            max_tokens=300,
            temperature=0.7
        )
        
        # Store messages in database
        timestamp = datetime.utcnow()
        
        # Store user message
        user_msg_doc = {
            'session_id': session_id,
            'service_id': service_id,
            'message': user_message,
            'sender': 'user',
            'timestamp': timestamp,
            'is_demo': True
        }
        db.chat_messages.insert_one(user_msg_doc)
        
        # Store bot response
        bot_msg_doc = {
            'session_id': session_id,
            'service_id': service_id,
            'message': ai_response,
            'sender': 'bot',
            'timestamp': timestamp,
            'is_demo': True
        }
        db.chat_messages.insert_one(bot_msg_doc)
        
        return jsonify({
            'response': ai_response,
            'session_id': session_id,
            'timestamp': timestamp.isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error in demo chat: {e}")
        return jsonify({
            'error': 'Failed to process message',
            'details': str(e)
        }), 500


@chat_bp.route('/business-info/<service_id>', methods=['GET'])
def get_business_info(service_id):
    """Get basic business information for demo page"""
    try:
        db = db_instance.get_db()
        
        # Get service details
        service = db.services.find_one({'_id': ObjectId(service_id)})
        
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        # Get bot configuration if exists
        bot_config = db.bot_configurations.find_one({'service_id': service_id})
        
        # Count business data
        faq_count = db.faqs.count_documents({'service_id': service_id, 'is_active': True})
        product_count = db.products.count_documents({'service_id': service_id, 'is_active': True})
        policy_count = db.policies.count_documents({'service_id': service_id, 'is_active': True})
        
        return jsonify({
            'service_name': service.get('service_name', 'Business'),
            'bot_name': bot_config.get('bot_name', 'Assistant') if bot_config else 'Assistant',
            'faq_count': faq_count,
            'product_count': product_count,
            'policy_count': policy_count,
            'has_bot_config': bot_config is not None
        }), 200
        
    except Exception as e:
        print(f"Error getting business info: {e}")
        return jsonify({'error': str(e)}), 500
