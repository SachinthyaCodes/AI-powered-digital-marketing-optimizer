"""
Demo Service Setup for FreshMart
Creates a demo service with token for testing the chatbot
"""
from database import db_instance
from models.service import Service
from models.bot_models import BotConfiguration
import uuid

def create_demo_service():
    db = db_instance.get_db()
    
    # Check if demo service already exists
    existing_service = db.services.find_one({'business_name': 'FreshMart Demo'})
    if existing_service:
        print(f"Demo service already exists with token: {existing_service['token']}")
        return existing_service['token']
    
    # Create demo service
    demo_service = {
        'business_name': 'FreshMart Demo',
        'email': 'demo@freshmart.lk',
        'phone': '+94 77 123 4567',
        'address': '123 Main Street, Colombo 07, Sri Lanka',
        'business_type': 'grocery',
        'status': 'active',
        'token': 'demo_freshmart_token_2025',
        'created_at': 'datetime.utcnow()',
        'subscription_plan': 'demo'
    }
    
    result = db.services.insert_one(demo_service)
    service_id = str(result.inserted_id)
    
    # Create bot configuration for demo service
    bot_config = {
        'service_id': service_id,
        'admin_id': None,
        'is_active': True,
        'welcome_message': 'Welcome to FreshMart! We offer fresh organic groceries delivered to your door. How can I help you today? (ආයුබෝවන්! අපි ඔබේ ගෙදරට නැවුම් කාබනික කරට්ටු භාණ්ඩ බෙදා හරිනවා. ඔබට අද කොහොමද උදව් කරන්න පුළුවන්?)',
        'fallback_message': 'I\'m sorry, I didn\'t quite understand that. Could you please rephrase your question about our products, prices, or delivery? (සමාවෙන්න, මට ඒක හරියටම තේරුණේ නැහැ. කරුණාකර අපේ භාණ්ඩ, මිල, හෝ බෙදාහැරීම ගැන ඔබේ ප්‍රශ්නය නැවත කියන්න පුළුවන්ද?)',
        'language_support': ['en', 'si'],
        'rag_enabled': True,
        'nlp_enabled': True,
        'created_at': 'datetime.utcnow()',
        'updated_at': 'datetime.utcnow()'
    }
    
    db.bot_configurations.insert_one(bot_config)
    
    # Add some demo FAQs
    demo_faqs = [
        {
            'service_id': service_id,
            'question': 'What are your delivery charges?',
            'answer': 'We offer free delivery for orders above Rs. 2,000 within Colombo. For orders below Rs. 2,000, delivery charges are Rs. 200 within Colombo and Rs. 350 outside Colombo.',
            'language': 'en',
            'is_active': True,
            'created_at': 'datetime.utcnow()'
        },
        {
            'service_id': service_id,
            'question': 'ඔබේ බෙදාහැරීමේ ගාස්තු කීයද?',
            'answer': 'කොළඹ තුළ රුපියල් 2,000කට වඩා වැඩි ඇණවුම් සඳහා අපි නොමිලේ බෙදාහැරීම සපයනවා. රුපියල් 2,000කට අඩු ඇණවුම් සඳහා කොළඹ තුළ රුපියල් 200ක් සහ කොළඹෙන් පිටත රුපියල් 350ක් බෙදාහැරීමේ ගාස්තුවක් තියෙනවා.',
            'language': 'si',
            'is_active': True,
            'created_at': 'datetime.utcnow()'
        },
        {
            'service_id': service_id,
            'question': 'What are your store hours?',
            'answer': 'We are open Monday to Saturday from 8:00 AM to 8:00 PM. We are closed on Sundays and public holidays.',
            'language': 'en',
            'is_active': True,
            'created_at': 'datetime.utcnow()'
        },
        {
            'service_id': service_id,
            'question': 'How do I track my order?',
            'answer': 'You can track your order using the tracking number sent to your email after placing the order. Alternatively, you can call us at +94 77 123 4567.',
            'language': 'en',
            'is_active': True,
            'created_at': 'datetime.utcnow()'
        }
    ]
    
    db.faqs.insert_many(demo_faqs)
    
    # Add some demo products
    demo_products = [
        {
            'service_id': service_id,
            'name': 'Fresh Apples',
            'description': 'Crispy red apples imported from New Zealand. Rich in vitamins and perfect for snacking.',
            'price': 450,
            'stock': 50,
            'category': 'fruits',
            'is_active': True,
            'created_at': 'datetime.utcnow()'
        },
        {
            'service_id': service_id,
            'name': 'Organic Bananas',
            'description': 'Sweet organic bananas grown locally. High in potassium and natural sugars.',
            'price': 280,
            'stock': 100,
            'category': 'fruits',
            'is_active': True,
            'created_at': 'datetime.utcnow()'
        },
        {
            'service_id': service_id,
            'name': 'Fresh Carrots',
            'description': 'Crunchy orange carrots perfect for cooking or eating raw. Rich in beta-carotene.',
            'price': 120,
            'stock': 75,
            'category': 'vegetables',
            'is_active': True,
            'created_at': 'datetime.utcnow()'
        },
        {
            'service_id': service_id,
            'name': 'Organic Free Range Eggs',
            'description': 'Fresh eggs from free-range chickens. No hormones or antibiotics.',
            'price': 580,
            'stock': 30,
            'category': 'dairy',
            'is_active': True,
            'created_at': 'datetime.utcnow()'
        }
    ]
    
    db.products.insert_many(demo_products)
    
    print(f"✅ Demo service created successfully!")
    print(f"Service Token: {demo_service['token']}")
    print(f"Business Name: {demo_service['business_name']}")
    print(f"Added {len(demo_faqs)} FAQs and {len(demo_products)} products")
    
    return demo_service['token']

if __name__ == "__main__":
    print("Setting up FreshMart demo service...")
    token = create_demo_service()
    print(f"\n🎉 Setup complete! Use token: {token}")
    print("\nNow you can:")
    print("1. Start the frontend: npm start")
    print("2. Open the demo page and test the chatbot")
    print("3. Ask questions in English or Sinhala")