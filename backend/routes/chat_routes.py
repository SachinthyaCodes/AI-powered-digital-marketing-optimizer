"""
Simplified Chat Routes for MarketMatic using SQLAlchemy
Uses Ollama with Llama3 for AI-powered conversations
"""
from flask import Blueprint, request, jsonify
from database import SessionLocal
from models.sqlalchemy_models import ChatMessage, Service, FAQ, Product, Policy, User
from services.ollama_service import OllamaService
from datetime import datetime
import uuid
import json

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Initialize Ollama service
ollama_service = OllamaService()

def get_business_context(service_id: uuid.UUID) -> str:
    """
    Fetch all business data (FAQs, Products, Policies) for a service
    and format it as context for the AI
    """
    db = SessionLocal()
    context_parts = []
    
    try:
        # Get FAQs
        faqs = db.query(FAQ).filter(
            FAQ.service_id == service_id,
            FAQ.is_active == True
        ).limit(20).all()
        
        if faqs:
            context_parts.append("=== Frequently Asked Questions ===")
            for faq in faqs:
                context_parts.append(f"Q ({faq.language}): {faq.question}")
                context_parts.append(f"A: {faq.answer}")
                context_parts.append("")
        
        # Get Products
        products = db.query(Product).filter(
            Product.service_id == service_id,
            Product.is_active == True
        ).limit(30).all()
        
        if products:
            context_parts.append("=== Available Products ===")
            for product in products:
                product_info = f"Product: {product.name}"
                if product.category:
                    product_info += f" (Category: {product.category})"
                product_info += f"\nPrice: Rs. {product.price}"
                product_info += f"\nStock: {product.stock} units"
                if product.description:
                    product_info += f"\nDescription: {product.description}"
                
                context_parts.append(product_info)
                context_parts.append("")
        
        # Get Policies
        policies = db.query(Policy).filter(
            Policy.service_id == service_id,
            Policy.is_active == True
        ).limit(10).all()
        
        if policies:
            context_parts.append("=== Business Policies ===")
            for policy in policies:
                context_parts.append(f"Policy: {policy.title} ({policy.policy_type})")
                context_parts.append(policy.content)
                context_parts.append("")
        
        # Get service/bot configuration
        service = db.query(Service).filter(Service.id == service_id).first()
        if service and service.welcome_message:
            context_parts.insert(0, f"=== Welcome Message ===\n{service.welcome_message}\n")
        
        return "\n".join(context_parts)
        
    except Exception as e:
        print(f"Error getting business context: {e}")
        return "Business information is being loaded. Please ask your question."
    finally:
        db.close()


@chat_bp.route('/message', methods=['POST'])
def send_chat_message():
    """
    Send a chat message and get AI response
    """
    db = SessionLocal()
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
        
        # Store user message
        user_msg = ChatMessage(
            id=str(uuid.uuid4()),
            service_id=uuid.UUID(service_id) if isinstance(service_id, str) else service_id,
            session_id=session_id,
            sender='user',
            message=user_message
        )
        
        db.add(user_msg)
        db.commit()
        
        # Get business-specific context
        business_context = get_business_context(user_msg.service_id)
        
        # Get recent conversation history
        recent_messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id,
            ChatMessage.service_id == user_msg.service_id
        ).order_by(ChatMessage.created_at.desc()).limit(6).all()
        
        # Format conversation history for Ollama
        conversation_history = []
        for msg in reversed(recent_messages[-5:]):  # Last 5 messages in order
            conversation_history.append({
                'role': msg.sender,
                'content': msg.message
            })
        
        # Generate AI response using Ollama Llama3
        try:
            response_message = ollama_service.generate_chat_response(
                query=user_message,
                context=business_context,
                conversation_history=conversation_history,
                language='mixed',  # Support both English and Sinhala
                max_tokens=300,
                temperature=0.7
            )
        except Exception as e:
            print(f"❌ Ollama error: {e}")
            response_message = "I'm experiencing technical difficulties. Please try again in a moment."
        
        # Store bot response
        bot_msg = ChatMessage(
            id=str(uuid.uuid4()),
            service_id=user_msg.service_id,
            session_id=session_id,
            sender='bot',
            message=response_message
        )
        
        db.add(bot_msg)
        db.commit()
        db.refresh(bot_msg)
        
        return jsonify({
            'session_id': session_id,
            'user_message': user_msg.to_dict(),
            'bot_message': bot_msg.to_dict()
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Error processing message: {str(e)}'}), 500
    finally:
        db.close()


@chat_bp.route('/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """
    Get chat history for a session
    """
    db = SessionLocal()
    try:
        service_id = request.args.get('service_id')
        
        if not service_id:
            return jsonify({'error': 'service_id is required'}), 400
        
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id,
            ChatMessage.service_id == uuid.UUID(service_id)
        ).order_by(ChatMessage.created_at).all()
        
        return jsonify({
            'session_id': session_id,
            'messages': [msg.to_dict() for msg in messages]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error fetching chat history: {str(e)}'}), 500
    finally:
        db.close()


@chat_bp.route('/test', methods=['GET'])
def test_chat():
    """
    Test endpoint to verify chat service is working
    """
    try:
        return jsonify({
            'message': 'Chat service is operational',
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': f'Chat service error: {str(e)}'}), 500


@chat_bp.route('/demo/message', methods=['POST'])
def send_demo_message():
    """
    Demo endpoint - sends a message without requiring authentication
    Uses Ollama Llama3 for intelligent responses
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Demo context
        demo_context = """
        === Demo Business Information ===
        
        Welcome to MarketMatic Demo!
        
        FAQs:
        Q: What is MarketMatic?
        A: MarketMatic is an AI-powered digital marketing optimizer that helps businesses automate customer interactions and improve engagement.
        
        Q: How does the chatbot work?
        A: Our chatbot uses advanced AI (Llama3) to understand and respond to customer queries in both English and Sinhala.
        
        Products:
        - Basic Plan: Rs. 2,500/month - For small businesses
        - Pro Plan: Rs. 5,000/month - Advanced features
        - Enterprise Plan: Rs. 10,000/month - Full customization
        
        Features:
        - 24/7 automated customer support
        - Multilingual support (English & Sinhala)
        - Product recommendations
        - Order tracking
        - FAQ automation
        """
        
        # Generate AI response using Ollama
        try:
            bot_response = ollama_service.generate_chat_response(
                query=user_message,
                context=demo_context,
                conversation_history=None,
                language='mixed',
                max_tokens=200,
                temperature=0.7
            )
        except Exception as e:
            print(f"❌ Ollama demo error: {e}")
            bot_response = "Hello! I'm the MarketMatic demo chatbot. I'm currently experiencing technical difficulties, but I'm here to help you learn about our AI-powered marketing solutions!"
        
        return jsonify({
            'user_message': user_message,
            'bot_response': bot_response,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error processing demo message: {str(e)}'}), 500


@chat_bp.route('/business-info/<service_id>', methods=['GET'])
def get_business_info(service_id):
    """
    Get business information for a service (FAQs, Products, Policies)
    """
    db = SessionLocal()
    try:
        # Convert string to UUID
        try:
            service_uuid = uuid.UUID(service_id)
        except ValueError:
            return jsonify({'error': 'Invalid service ID format'}), 400
        
        # Get service
        service = db.query(Service).filter(Service.id == str(service_uuid)).first()
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        # Get FAQs
        faqs = db.query(FAQ).filter(
            FAQ.service_id == str(service_uuid),
            FAQ.is_active == True
        ).all()
        
        # Get Products
        products = db.query(Product).filter(
            Product.service_id == str(service_uuid),
            Product.is_active == True
        ).all()
        
        # Get Policies
        policies = db.query(Policy).filter(
            Policy.service_id == str(service_uuid),
            Policy.is_active == True
        ).all()
        
        return jsonify({
            'service': service.to_dict(),
            'faqs': [faq.to_dict() for faq in faqs],
            'products': [product.to_dict() for product in products],
            'policies': [policy.to_dict() for policy in policies]
        }), 200
        
    except Exception as e:
        import traceback
        print(f"Error fetching business info: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Error fetching business info: {str(e)}'}), 500
    finally:
        db.close()
