from flask import Blueprint, request, jsonify
from database import db_instance
from auth.decorators import admin_required
from models.bot_models import BotConfiguration, FAQ, Product, Policy
from utils.cloudinary_service import CloudinaryService
from bson import ObjectId
from datetime import datetime

bot_bp = Blueprint('bot', __name__, url_prefix='/api/bot')

# ==================== BOT CONFIGURATION ====================

@bot_bp.route('/config', methods=['GET'])
@admin_required
def get_bot_config():
    """Get bot configuration for admin's service"""
    try:
        user_id = request.current_user['user_id']
        
        # Get user and service_id
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.get('service_id')
        if not service_id:
            return jsonify({'message': 'No service associated with this admin'}), 404
        
        # Get or create bot config
        config = db.bot_configurations.find_one({'service_id': service_id})
        
        if not config:
            # Create default configuration
            new_config = BotConfiguration(service_id, user_id)
            db.bot_configurations.insert_one(new_config.to_dict())
            config = db.bot_configurations.find_one({'service_id': service_id})
        
        config['_id'] = str(config['_id'])
        return jsonify({'config': config}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching bot config: {str(e)}'}), 500

@bot_bp.route('/config', methods=['PUT'])
@admin_required
def update_bot_config():
    """Update bot configuration"""
    try:
        user_id = request.current_user['user_id']
        data = request.get_json()
        
        # Get user and service_id
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.get('service_id')
        
        # Update configuration
        update_data = {
            'welcome_message': data.get('welcome_message'),
            'fallback_message': data.get('fallback_message'),
            'language_support': data.get('language_support', ['en', 'si']),
            'rag_enabled': data.get('rag_enabled', True),
            'nlp_enabled': data.get('nlp_enabled', True),
            'is_active': data.get('is_active', True),
            'response_mode': data.get('response_mode', 'hybrid'),
            'documents_only_message': data.get('documents_only_message'),
            'use_general_knowledge': data.get('use_general_knowledge', True),
            'updated_at': datetime.utcnow()
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        db.bot_configurations.update_one(
            {'service_id': service_id},
            {'$set': update_data},
            upsert=True
        )
        
        return jsonify({'message': 'Bot configuration updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error updating bot config: {str(e)}'}), 500

# ==================== FAQ MANAGEMENT ====================

@bot_bp.route('/faqs', methods=['GET'])
@admin_required
def get_faqs():
    """Get all FAQs for admin's service"""
    try:
        user_id = request.current_user['user_id']
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.get('service_id')
        faqs = list(db.faqs.find({'service_id': service_id}))
        
        for faq in faqs:
            faq['_id'] = str(faq['_id'])
        
        return jsonify({'faqs': faqs}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching FAQs: {str(e)}'}), 500

@bot_bp.route('/faqs', methods=['POST'])
@admin_required
def create_faq():
    """Create new FAQ"""
    try:
        user_id = request.current_user['user_id']
        data = request.get_json()
        
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.get('service_id')
        
        # Validate required fields
        if not data.get('question') or not data.get('answer'):
            return jsonify({'message': 'Question and answer are required'}), 400
        
        new_faq = FAQ(
            service_id=service_id,
            question=data['question'],
            answer=data['answer'],
            language=data.get('language', 'en')
        )
        
        result = db.faqs.insert_one(new_faq.to_dict())
        
        # Return the created FAQ with all data
        created_faq = db.faqs.find_one({'_id': result.inserted_id})
        created_faq['_id'] = str(created_faq['_id'])
        
        return jsonify(created_faq), 201
        
    except Exception as e:
        return jsonify({'message': f'Error creating FAQ: {str(e)}'}), 500

@bot_bp.route('/faqs/<faq_id>', methods=['PUT'])
@admin_required
def update_faq(faq_id):
    """Update FAQ"""
    try:
        user_id = request.current_user['user_id']
        data = request.get_json()
        
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.get('service_id')
        
        # Check if FAQ belongs to this service
        faq = db.faqs.find_one({'_id': ObjectId(faq_id), 'service_id': service_id})
        if not faq:
            return jsonify({'message': 'FAQ not found'}), 404
        
        update_data = {
            'question': data.get('question'),
            'answer': data.get('answer'),
            'language': data.get('language'),
            'is_active': data.get('is_active'),
            'updated_at': datetime.utcnow()
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        db.faqs.update_one(
            {'_id': ObjectId(faq_id)},
            {'$set': update_data}
        )
        
        # Return updated FAQ
        updated_faq = db.faqs.find_one({'_id': ObjectId(faq_id)})
        updated_faq['_id'] = str(updated_faq['_id'])
        
        return jsonify(updated_faq), 200
        
    except Exception as e:
        return jsonify({'message': f'Error updating FAQ: {str(e)}'}), 500

@bot_bp.route('/faqs/<faq_id>', methods=['DELETE'])
@admin_required
def delete_faq(faq_id):
    """Delete FAQ"""
    try:
        user_id = request.current_user['user_id']
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.get('service_id')
        
        result = db.faqs.delete_one({'_id': ObjectId(faq_id), 'service_id': service_id})
        
        if result.deleted_count == 0:
            return jsonify({'message': 'FAQ not found'}), 404
        
        return jsonify({'message': 'FAQ deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error deleting FAQ: {str(e)}'}), 500

# ==================== PRODUCT MANAGEMENT ====================

@bot_bp.route('/products', methods=['GET'])
@admin_required
def get_products():
    """Get all products for admin's service"""
    try:
        user_id = request.current_user['user_id']
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.get('service_id')
        products = list(db.products.find({'service_id': service_id}))
        
        for product in products:
            product['_id'] = str(product['_id'])
        
        return jsonify({'products': products}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching products: {str(e)}'}), 500

@bot_bp.route('/products', methods=['POST'])
@admin_required
def create_product():
    """Create new product with image upload"""
    try:
        user_id = request.current_user['user_id']
        
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.get('service_id')
        
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
                import json
                try:
                    image_urls = json.loads(data['images'])
                except:
                    image_urls = [data['images']] if data['images'] else []
        
        new_product = Product(
            service_id=service_id,
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            stock=int(data['stock']),
            category=data.get('category', 'general'),
            images=image_urls
        )
        
        result = db.products.insert_one(new_product.to_dict())
        
        # Return the created product with all data
        created_product = db.products.find_one({'_id': result.inserted_id})
        created_product['_id'] = str(created_product['_id'])
        
        return jsonify(created_product), 201
        
    except Exception as e:
        return jsonify({'message': f'Error creating product: {str(e)}'}), 500

@bot_bp.route('/products/<product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """Update product with optional image upload"""
    try:
        user_id = request.current_user['user_id']
        
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.get('service_id')
        
        # Check if product belongs to this service
        product = db.products.find_one({'_id': ObjectId(product_id), 'service_id': service_id})
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        # Handle both JSON and form-data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        update_data = {
            'name': data.get('name'),
            'description': data.get('description'),
            'price': float(data['price']) if data.get('price') else None,
            'stock': int(data['stock']) if data.get('stock') else None,
            'category': data.get('category'),
            'is_active': data.get('is_active'),
            'updated_at': datetime.utcnow()
        }
        
        # Handle new image uploads
        if 'images' in request.files:
            image_urls = product.get('images', [])
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename:
                    result = CloudinaryService.upload_image(file, folder=f"marketmatic/{service_id}/products")
                    if result:
                        image_urls.append(result['url'])
            update_data['images'] = image_urls
        elif 'images' in data:
            # Handle images sent as JSON array or string
            if isinstance(data['images'], list):
                update_data['images'] = data['images']
            elif isinstance(data['images'], str):
                import json
                try:
                    update_data['images'] = json.loads(data['images'])
                except:
                    pass
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update_data}
        )
        
        # Return updated product
        updated_product = db.products.find_one({'_id': ObjectId(product_id)})
        updated_product['_id'] = str(updated_product['_id'])
        
        return jsonify(updated_product), 200
        
    except Exception as e:
        return jsonify({'message': f'Error updating product: {str(e)}'}), 500

@bot_bp.route('/products/<product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """Delete product"""
    try:
        user_id = request.current_user['user_id']
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.get('service_id')
        
        # Get product to delete images
        product = db.products.find_one({'_id': ObjectId(product_id), 'service_id': service_id})
        if product and product.get('images'):
            for image in product['images']:
                CloudinaryService.delete_image(image.get('public_id'))
        
        result = db.products.delete_one({'_id': ObjectId(product_id), 'service_id': service_id})
        
        if result.deleted_count == 0:
            return jsonify({'message': 'Product not found'}), 404
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error deleting product: {str(e)}'}), 500

# ==================== IMAGE UPLOAD ====================

@bot_bp.route('/upload-image', methods=['POST'])
@admin_required
def upload_image():
    """Upload image(s) to Cloudinary"""
    try:
        user_id = request.current_user['user_id']
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        # Accept both 'image' and 'images' field names
        files = request.files.getlist('images') or request.files.getlist('image')
        
        if not files:
            return jsonify({'message': 'No image file provided'}), 400
        
        service_id = user.get('service_id')
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

@bot_bp.route('/products/<product_id>/images', methods=['POST'])
@admin_required
def add_product_image(product_id):
    """Add multiple images to product"""
    try:
        user_id = request.current_user['user_id']
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.get('service_id')
        
        # Check if product exists and belongs to this service
        product = db.products.find_one({'_id': ObjectId(product_id), 'service_id': service_id})
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
                    uploaded_images.append({
                        'url': result['url'],
                        'public_id': result['public_id'],
                        'filename': file.filename,
                        'uploaded_at': datetime.utcnow()
                    })
                else:
                    errors.append(f"Failed to upload {file.filename}")
                    
            except Exception as e:
                errors.append(f"Error uploading {file.filename}: {str(e)}")
        
        if uploaded_images:
            # Add images to product
            db.products.update_one(
                {'_id': ObjectId(product_id), 'service_id': service_id},
                {
                    '$push': {'images': {'$each': uploaded_images}},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
        
        return jsonify({
            'message': f'{len(uploaded_images)} images uploaded successfully',
            'uploaded_images': uploaded_images,
            'errors': errors
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error adding product images: {str(e)}'}), 500


@bot_bp.route('/products/<product_id>/images/<image_id>', methods=['DELETE'])
@admin_required
def remove_product_image(product_id, image_id):
    """Remove a specific image from product"""
    try:
        user_id = request.current_user['user_id']
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.get('service_id')
        
        # Get product and find image
        product = db.products.find_one({'_id': ObjectId(product_id), 'service_id': service_id})
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        # Find image by public_id
        image_to_remove = None
        for img in product.get('images', []):
            if img.get('public_id') == image_id:
                image_to_remove = img
                break
        
        if not image_to_remove:
            return jsonify({'message': 'Image not found'}), 404
        
        # Delete from Cloudinary
        CloudinaryService.delete_image(image_id)
        
        # Remove from product
        db.products.update_one(
            {'_id': ObjectId(product_id), 'service_id': service_id},
            {
                '$pull': {'images': {'public_id': image_id}},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        return jsonify({'message': 'Image removed successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error removing product image: {str(e)}'}), 500

# ==================== POLICY MANAGEMENT ====================

@bot_bp.route('/policies', methods=['GET'])
@admin_required
def get_policies():
    """Get all policies for admin's service"""
    try:
        user_id = request.current_user['user_id']
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.get('service_id')
        policies = list(db.policies.find({'service_id': service_id}))
        
        for policy in policies:
            policy['_id'] = str(policy['_id'])
        
        return jsonify({'policies': policies}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching policies: {str(e)}'}), 500

@bot_bp.route('/policies', methods=['POST'])
@admin_required
def create_policy():
    """Create new policy"""
    try:
        user_id = request.current_user['user_id']
        data = request.get_json()
        
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.get('service_id')
        
        # Validate required fields
        if not data.get('title') or not data.get('content'):
            return jsonify({'message': 'Title and content are required'}), 400
        
        new_policy = Policy(
            service_id=service_id,
            title=data['title'],
            content=data['content'],
            policy_type=data.get('policy_type', 'general')
        )
        
        result = db.policies.insert_one(new_policy.to_dict())
        
        # Return the created policy with all data
        created_policy = db.policies.find_one({'_id': result.inserted_id})
        created_policy['_id'] = str(created_policy['_id'])
        
        return jsonify(created_policy), 201
        
    except Exception as e:
        return jsonify({'message': f'Error creating policy: {str(e)}'}), 500

@bot_bp.route('/policies/<policy_id>', methods=['PUT'])
@admin_required
def update_policy(policy_id):
    """Update policy"""
    try:
        user_id = request.current_user['user_id']
        data = request.get_json()
        
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.get('service_id')
        
        update_data = {
            'title': data.get('title'),
            'content': data.get('content'),
            'policy_type': data.get('policy_type'),
            'is_active': data.get('is_active'),
            'updated_at': datetime.utcnow()
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        result = db.policies.update_one(
            {'_id': ObjectId(policy_id), 'service_id': service_id},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'message': 'Policy not found'}), 404
        
        # Return updated policy
        updated_policy = db.policies.find_one({'_id': ObjectId(policy_id)})
        updated_policy['_id'] = str(updated_policy['_id'])
        
        return jsonify(updated_policy), 200
        
    except Exception as e:
        return jsonify({'message': f'Error updating policy: {str(e)}'}), 500

@bot_bp.route('/policies/<policy_id>', methods=['DELETE'])
@admin_required
def delete_policy(policy_id):
    """Delete policy"""
    try:
        user_id = request.current_user['user_id']
        db = db_instance.get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        
        service_id = user.get('service_id')
        
        result = db.policies.delete_one({'_id': ObjectId(policy_id), 'service_id': service_id})
        
        if result.deleted_count == 0:
            return jsonify({'message': 'Policy not found'}), 404
        
        return jsonify({'message': 'Policy deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error deleting policy: {str(e)}'}), 500
