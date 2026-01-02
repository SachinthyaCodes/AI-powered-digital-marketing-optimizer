from flask import Blueprint, request, jsonify
from database import SessionLocal
from auth.decorators import admin_required
from models.sqlalchemy_models import Service, FAQ, Product, Policy, User
from utils.cloudinary_service import CloudinaryService
from datetime import datetime
import uuid
import json

bot_bp = Blueprint('bot', __name__, url_prefix='/api/bot')

# ==================== BOT CONFIGURATION ====================

@bot_bp.route('/config', methods=['GET'])
@admin_required
def get_bot_config():
    """Get bot configuration for admin's service"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        
        # Get user and service_id
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.service_id
        if not service_id:
            return jsonify({'message': 'No service associated with this admin'}), 404
        
        # Get service with config
        service = db.query(Service).filter(Service.id == service_id).first()
        
        if not service:
            return jsonify({'message': 'Service not found'}), 404
        
        return jsonify({'config': service.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching bot config: {str(e)}'}), 500
    finally:
        db.close()

@bot_bp.route('/config', methods=['PUT'])
@admin_required
def update_bot_config():
    """Update bot configuration"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        data = request.get_json()
        
        # Get user and service_id
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.service_id
        
        # Get service
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return jsonify({'message': 'Service not found'}), 404
        
        # Update configuration with proper JSON serialization
        if 'welcome_message' in data:
            # Convert dict to JSON string for Text column
            service.welcome_message = json.dumps(data['welcome_message']) if isinstance(data['welcome_message'], dict) else data['welcome_message']
        if 'fallback_message' in data:
            # Convert dict to JSON string for Text column
            service.fallback_message = json.dumps(data['fallback_message']) if isinstance(data['fallback_message'], dict) else data['fallback_message']
        if 'language_support' in data:
            # Convert array to comma-separated string
            service.language_support = ','.join(data['language_support']) if isinstance(data['language_support'], list) else data['language_support']
        if 'rag_enabled' in data:
            service.rag_enabled = data['rag_enabled']
        if 'nlp_enabled' in data:
            service.nlp_enabled = data['nlp_enabled']
        if 'is_active' in data:
            service.is_active = data['is_active']
        if 'response_mode' in data:
            service.response_mode = data['response_mode']
        if 'documents_only_message' in data:
            # Convert dict to JSON string for Text column
            service.documents_only_message = json.dumps(data['documents_only_message']) if isinstance(data['documents_only_message'], dict) else data['documents_only_message']
        if 'use_general_knowledge' in data:
            service.use_general_knowledge = data['use_general_knowledge']
        
        # Response configuration
        if 'max_response_tokens' in data:
            tokens = int(data['max_response_tokens'])
            service.max_response_tokens = max(100, min(1000, tokens))  # Clamp between 100-1000
        if 'response_temperature' in data:
            temp = float(data['response_temperature'])
            service.response_temperature = max(0.0, min(1.0, temp))  # Clamp between 0.0-1.0
        if 'response_timeout' in data:
            timeout = int(data['response_timeout'])
            service.response_timeout = max(10, min(120, timeout))  # Clamp between 10-120 seconds
        
        service.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(service)
        
        return jsonify({'config': service.to_dict()}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'Error updating bot config: {str(e)}'}), 500
    finally:
        db.close()

# ==================== FAQ MANAGEMENT ====================

@bot_bp.route('/faqs', methods=['GET'])
@admin_required
def get_faqs():
    """Get all FAQs for admin's service"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        
        # Get user and service_id
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.service_id
        faqs = db.query(FAQ).filter(FAQ.service_id == service_id).all()
        
        return jsonify({'faqs': [faq.to_dict() for faq in faqs]}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching FAQs: {str(e)}'}), 500
    finally:
        db.close()

@bot_bp.route('/faqs', methods=['POST'])
@admin_required
def create_faq():
    """Create new FAQ"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        data = request.get_json()
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.service_id
        
        # Validate required fields
        if not data.get('question') or not data.get('answer'):
            return jsonify({'message': 'Question and answer are required'}), 400
        
        new_faq = FAQ(
            id=str(uuid.uuid4()),
            service_id=service_id,
            question=data['question'],
            answer=data['answer'],
            language=data.get('language', 'en'),
            is_active=data.get('is_active', True)
        )
        
        db.add(new_faq)
        db.commit()
        db.refresh(new_faq)
        
        return jsonify(new_faq.to_dict()), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'Error creating FAQ: {str(e)}'}), 500
    finally:
        db.close()

@bot_bp.route('/faqs/<faq_id>', methods=['PUT'])
@admin_required
def update_faq(faq_id):
    """Update FAQ"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        data = request.get_json()
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.service_id
        
        # Check if FAQ belongs to this service
        faq = db.query(FAQ).filter(
            FAQ.id == faq_id,
            FAQ.service_id == service_id
        ).first()
        
        if not faq:
            return jsonify({'message': 'FAQ not found'}), 404
        
        if 'question' in data:
            faq.question = data['question']
        if 'answer' in data:
            faq.answer = data['answer']
        if 'language' in data:
            faq.language = data['language']
        if 'is_active' in data:
            faq.is_active = data['is_active']
        
        faq.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(faq)
        
        return jsonify(faq.to_dict()), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'Error updating FAQ: {str(e)}'}), 500
    finally:
        db.close()

@bot_bp.route('/faqs/<faq_id>', methods=['DELETE'])
@admin_required
def delete_faq(faq_id):
    """Delete FAQ"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.service_id
        
        faq = db.query(FAQ).filter(
            FAQ.id == faq_id,
            FAQ.service_id == service_id
        ).first()
        
        if not faq:
            return jsonify({'message': 'FAQ not found'}), 404
        
        db.delete(faq)
        db.commit()
        
        return jsonify({'message': 'FAQ deleted successfully'}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'Error deleting FAQ: {str(e)}'}), 500
    finally:
        db.close()

# ==================== PRODUCT MANAGEMENT ====================

@bot_bp.route('/products', methods=['GET'])
@admin_required
def get_products():
    """Get all products for admin's service"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.service_id
        products = db.query(Product).filter(Product.service_id == service_id).all()
        
        return jsonify({'products': [product.to_dict() for product in products]}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching products: {str(e)}'}), 500
    finally:
        db.close()

@bot_bp.route('/products', methods=['POST'])
@admin_required
def create_product():
    """Create new product with image upload"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.service_id
        
        # Handle both JSON and form-data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        # Validate required fields
        required_fields = ['name', 'price', 'stock']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'{field} is required'}), 400
        
        # Handle image uploads to Cloudinary
        image_urls = []
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename:
                    result = CloudinaryService.upload_image(file, folder=f"marketmatic/{service_id}/products")
                    if result:
                        image_urls.append(result['url'])
        
        # If images were sent as URLs in JSON (from previous upload)
        if not image_urls and 'images' in data:
            if isinstance(data['images'], list):
                image_urls = data['images']
            elif isinstance(data['images'], str):
                try:
                    image_urls = json.loads(data['images'])
                except:
                    image_urls = [data['images']] if data['images'] else []
        
        # Product model has image_url (singular), take first image if multiple
        image_url = image_urls[0] if image_urls else None
        
        new_product = Product(
            id=str(uuid.uuid4()),
            service_id=service_id,
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            stock=int(data['stock']),
            category=data.get('category', 'general'),
            image_url=image_url,  # Fixed: use image_url not images
            is_active=data.get('is_active', True)
        )
        
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        return jsonify(new_product.to_dict()), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'Error creating product: {str(e)}'}), 500
    finally:
        db.close()

@bot_bp.route('/products/<product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """Update product with optional image upload"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.service_id
        
        # Check if product belongs to this service
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.service_id == service_id
        ).first()
        
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        # Handle both JSON and form-data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = float(data['price'])
        if 'stock' in data:
            product.stock = int(data['stock'])
        if 'category' in data:
            product.category = data['category']
        if 'is_active' in data:
            product.is_active = data['is_active']
        
        # Handle new image uploads
        if 'images' in request.files:
            image_urls = product.images or []
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename:
                    result = CloudinaryService.upload_image(file, folder=f"marketmatic/{service_id}/products")
                    if result:
                        image_urls.append(result['url'])
            product.images = image_urls
        elif 'images' in data:
            # Handle images sent as JSON array or string
            if isinstance(data['images'], list):
                product.images = data['images']
            elif isinstance(data['images'], str):
                try:
                    product.images = json.loads(data['images'])
                except:
                    pass
        
        product.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(product)
        
        return jsonify(product.to_dict()), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'Error updating product: {str(e)}'}), 500
    finally:
        db.close()

@bot_bp.route('/products/<product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """Delete product"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.service_id
        
        # Get product to delete images
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.service_id == service_id
        ).first()
        
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        # Note: Images in product.images are URLs, not public_ids
        # If needed, implement image deletion based on URL
        
        db.delete(product)
        db.commit()
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'Error deleting product: {str(e)}'}), 500
    finally:
        db.close()

# ==================== IMAGE UPLOAD ====================

@bot_bp.route('/upload-image', methods=['POST'])
@admin_required
def upload_image():
    """Upload image(s) to Cloudinary"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        # Accept both 'image' and 'images' field names
        files = request.files.getlist('images') or request.files.getlist('image')
        
        if not files:
            return jsonify({'message': 'No image file provided'}), 400
        
        service_id = user.service_id
        uploaded_urls = []
        
        # Upload each file to Cloudinary
        for file in files:
            if file.filename == '':
                continue
                
            result = CloudinaryService.upload_image(file, folder=f"marketmatic/{service_id}")
            
            if result:
                uploaded_urls.append(result['url'])
        
        if not uploaded_urls:
            return jsonify({'message': 'Failed to upload images'}), 500
        
        return jsonify({
            'message': 'Images uploaded successfully',
            'urls': uploaded_urls,
            'url': uploaded_urls[0] if uploaded_urls else None  # For backward compatibility
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error uploading image: {str(e)}'}), 500
    finally:
        db.close()

@bot_bp.route('/products/<product_id>/images', methods=['POST'])
@admin_required
def add_product_image(product_id):
    """Add multiple images to product"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.service_id
        
        # Check if product exists and belongs to this service
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.service_id == service_id
        ).first()
        
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        if 'images' not in request.files and 'image' not in request.files:
            return jsonify({'message': 'No image files provided'}), 400
        
        uploaded_images = []
        errors = []
        
        # Handle multiple files
        files = request.files.getlist('images') or [request.files.get('image')]
        files = [f for f in files if f and f.filename]  # Filter out empty files
        
        for file in files:
            try:
                # Validate image file
                if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    errors.append(f"Invalid image format for {file.filename}")
                    continue
                
                # Upload to Cloudinary
                result = CloudinaryService.upload_image(
                    file, 
                    folder=f"marketmatic/{service_id}/products/{product_id}"
                )
                
                if result:
                    uploaded_images.append(result['url'])
                else:
                    errors.append(f"Failed to upload {file.filename}")
                    
            except Exception as e:
                errors.append(f"Error uploading {file.filename}: {str(e)}")
        
        if uploaded_images:
            # Add images to product
            if not product.images:
                product.images = []
            product.images.extend(uploaded_images)
            product.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(product)
        
        return jsonify({
            'message': f'{len(uploaded_images)} images uploaded successfully',
            'uploaded_images': uploaded_images,
            'errors': errors
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'Error adding product images: {str(e)}'}), 500
    finally:
        db.close()

@bot_bp.route('/products/<product_id>/images/<image_id>', methods=['DELETE'])
@admin_required
def remove_product_image(product_id, image_id):
    """Remove a specific image from product"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.service_id
        
        # Get product
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.service_id == service_id
        ).first()
        
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        # Remove image by URL (image_id is the URL)
        if product.images and image_id in product.images:
            product.images.remove(image_id)
            product.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(product)
            return jsonify({'message': 'Image removed successfully'}), 200
        
        return jsonify({'message': 'Image not found'}), 404
        
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'Error removing product image: {str(e)}'}), 500
    finally:
        db.close()

# ==================== POLICY MANAGEMENT ====================

@bot_bp.route('/policies', methods=['GET'])
@admin_required
def get_policies():
    """Get all policies for admin's service"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.service_id
        policies = db.query(Policy).filter(Policy.service_id == service_id).all()
        
        return jsonify({'policies': [policy.to_dict() for policy in policies]}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching policies: {str(e)}'}), 500
    finally:
        db.close()

@bot_bp.route('/policies', methods=['POST'])
@admin_required
def create_policy():
    """Create new policy"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        data = request.get_json()
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.service_id
        
        # Validate required fields
        if not data.get('title') or not data.get('content'):
            return jsonify({'message': 'Title and content are required'}), 400
        
        new_policy = Policy(
            id=str(uuid.uuid4()),
            service_id=service_id,
            title=data['title'],
            content=data['content'],
            policy_type=data.get('policy_type', 'general'),
            is_active=data.get('is_active', True)
        )
        
        db.add(new_policy)
        db.commit()
        db.refresh(new_policy)
        
        return jsonify(new_policy.to_dict()), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'Error creating policy: {str(e)}'}), 500
    finally:
        db.close()

@bot_bp.route('/policies/<policy_id>', methods=['PUT'])
@admin_required
def update_policy(policy_id):
    """Update policy"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        data = request.get_json()
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.service_id
        
        policy = db.query(Policy).filter(
            Policy.id == policy_id,
            Policy.service_id == service_id
        ).first()
        
        if not policy:
            return jsonify({'message': 'Policy not found'}), 404
        
        if 'title' in data:
            policy.title = data['title']
        if 'content' in data:
            policy.content = data['content']
        if 'policy_type' in data:
            policy.policy_type = data['policy_type']
        if 'is_active' in data:
            policy.is_active = data['is_active']
        
        policy.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(policy)
        
        return jsonify(policy.to_dict()), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'Error updating policy: {str(e)}'}), 500
    finally:
        db.close()

@bot_bp.route('/policies/<policy_id>', methods=['DELETE'])
@admin_required
def delete_policy(policy_id):
    """Delete policy"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.service_id
        
        policy = db.query(Policy).filter(
            Policy.id == policy_id,
            Policy.service_id == service_id
        ).first()
        
        if not policy:
            return jsonify({'message': 'Policy not found'}), 404
        
        db.delete(policy)
        db.commit()
        
        return jsonify({'message': 'Policy deleted successfully'}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'Error deleting policy: {str(e)}'}), 500
    finally:
        db.close()
