from flask import Blueprint, request, jsonify
from database import db_instance
from models.service import Service
from auth.jwt_handler import token_required
from auth.decorators import superadmin_required
from bson import ObjectId
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

service_bp = Blueprint('service', __name__, url_prefix='/api/services')

@service_bp.route('/', methods=['GET'])
@token_required
@superadmin_required
def get_all_services():
    """Get all services (superadmin only)"""
    try:
        db = db_instance.get_db()
        services = list(db.services.find())
        
        return jsonify({
            'services': [Service.serialize(service) for service in services],
            'total': len(services)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching services: {str(e)}'}), 500

@service_bp.route('/<service_id>', methods=['GET'])
@token_required
@superadmin_required
def get_service(service_id):
    """Get a single service by ID"""
    try:
        db = db_instance.get_db()
        service = db.services.find_one({'_id': ObjectId(service_id)})
        
        if not service:
            return jsonify({'message': 'Service not found'}), 404
        
        return jsonify({
            'service': Service.serialize(service)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching service: {str(e)}'}), 500

@service_bp.route('/', methods=['POST'])
@token_required
@superadmin_required
def create_service():
    """Create a new service (superadmin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['shop_name', 'owner_name', 'address', 'email', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Validate email
        try:
            validate_email(data['email'])
        except EmailNotValidError:
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Check if service with same email already exists
        db = db_instance.get_db()
        existing_service = db.services.find_one({'email': data['email'].lower()})
        if existing_service:
            return jsonify({'message': 'Service with this email already exists'}), 409
        
        # Create new service
        new_service = Service(
            shop_name=data['shop_name'].strip(),
            owner_name=data['owner_name'].strip(),
            address=data['address'].strip(),
            email=data['email'].lower().strip(),
            phone=data['phone'].strip(),
            subscription_duration=data.get('subscription_duration'),
            subscription_unit=data.get('subscription_unit', 'month')
        )
        
        # Set subscription dates if duration is provided
        if new_service.subscription_duration:
            new_service.subscription_start = datetime.utcnow()
            new_service.subscription_end = new_service.calculate_subscription_end()
        
        result = db.services.insert_one(new_service.to_dict())
        
        # Fetch the created service
        created_service = db.services.find_one({'_id': result.inserted_id})
        
        return jsonify({
            'message': 'Service created successfully',
            'service': Service.serialize(created_service)
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error creating service: {str(e)}'}), 500

@service_bp.route('/<service_id>', methods=['PUT'])
@token_required
@superadmin_required
def update_service(service_id):
    """Update a service (superadmin only)"""
    try:
        data = request.get_json()
        db = db_instance.get_db()
        
        # Check if service exists
        service = db.services.find_one({'_id': ObjectId(service_id)})
        if not service:
            return jsonify({'message': 'Service not found'}), 404
        
        # Prepare update data
        update_data = {
            'updated_at': datetime.utcnow()
        }
        
        # Update allowed fields
        allowed_fields = ['shop_name', 'owner_name', 'address', 'email', 'phone', 
                         'subscription_duration', 'subscription_unit', 'is_active']
        
        for field in allowed_fields:
            if field in data:
                if field == 'email':
                    # Validate email
                    try:
                        validate_email(data[field])
                        update_data[field] = data[field].lower().strip()
                    except EmailNotValidError:
                        return jsonify({'message': 'Invalid email format'}), 400
                elif field in ['shop_name', 'owner_name', 'address', 'phone']:
                    update_data[field] = data[field].strip()
                else:
                    update_data[field] = data[field]
        
        # Recalculate subscription end date if duration or unit changed
        if 'subscription_duration' in update_data or 'subscription_unit' in update_data:
            subscription_start = service.get('subscription_start') or datetime.utcnow()
            subscription_duration = update_data.get('subscription_duration', service.get('subscription_duration'))
            subscription_unit = update_data.get('subscription_unit', service.get('subscription_unit'))
            
            if subscription_duration:
                # Create temporary service object to calculate end date
                temp_service = Service('', '', '', '', '')
                temp_service.subscription_start = subscription_start
                temp_service.subscription_duration = subscription_duration
                temp_service.subscription_unit = subscription_unit
                
                update_data['subscription_start'] = subscription_start
                update_data['subscription_end'] = temp_service.calculate_subscription_end()
        
        # Update service
        db.services.update_one(
            {'_id': ObjectId(service_id)},
            {'$set': update_data}
        )
        
        # Fetch updated service
        updated_service = db.services.find_one({'_id': ObjectId(service_id)})
        
        return jsonify({
            'message': 'Service updated successfully',
            'service': Service.serialize(updated_service)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error updating service: {str(e)}'}), 500

@service_bp.route('/<service_id>', methods=['DELETE'])
@token_required
@superadmin_required
def delete_service(service_id):
    """Delete a service (superadmin only)"""
    try:
        db = db_instance.get_db()
        
        # Check if service exists
        service = db.services.find_one({'_id': ObjectId(service_id)})
        if not service:
            return jsonify({'message': 'Service not found'}), 404
        
        # Delete service
        db.services.delete_one({'_id': ObjectId(service_id)})
        
        return jsonify({
            'message': 'Service deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error deleting service: {str(e)}'}), 500

@service_bp.route('/<service_id>/subscription', methods=['PUT'])
@token_required
@superadmin_required
def update_subscription(service_id):
    """Update service subscription (superadmin only)"""
    try:
        data = request.get_json()
        db = db_instance.get_db()
        
        # Check if service exists
        service = db.services.find_one({'_id': ObjectId(service_id)})
        if not service:
            return jsonify({'message': 'Service not found'}), 404
        
        subscription_duration = data.get('subscription_duration')
        subscription_unit = data.get('subscription_unit', 'month')
        
        if not subscription_duration:
            return jsonify({'message': 'subscription_duration is required'}), 400
        
        # Calculate new subscription dates
        subscription_start = datetime.utcnow()
        
        temp_service = Service('', '', '', '', '')
        temp_service.subscription_start = subscription_start
        temp_service.subscription_duration = subscription_duration
        temp_service.subscription_unit = subscription_unit
        subscription_end = temp_service.calculate_subscription_end()
        
        # Update service
        db.services.update_one(
            {'_id': ObjectId(service_id)},
            {'$set': {
                'subscription_duration': subscription_duration,
                'subscription_unit': subscription_unit,
                'subscription_start': subscription_start,
                'subscription_end': subscription_end,
                'is_active': True,
                'updated_at': datetime.utcnow()
            }}
        )
        
        # Fetch updated service
        updated_service = db.services.find_one({'_id': ObjectId(service_id)})
        
        return jsonify({
            'message': 'Subscription updated successfully',
            'service': Service.serialize(updated_service)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error updating subscription: {str(e)}'}), 500

@service_bp.route('/my-service', methods=['GET'])
@token_required
def get_my_service():
    """Get service information for the current admin user"""
    try:
        db = db_instance.get_db()
        user_id = request.current_user['user_id']
        user_role = request.current_user.get('role', 'user')
        
        # Only admin users can access this endpoint
        if user_role != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        
        # Get user to find their service_id
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        service_id = user.get('service_id')
        
        if not service_id:
            return jsonify({'message': 'No service linked to this account'}), 404
        
        # Get service information
        service = db.services.find_one({'_id': ObjectId(service_id)})
        
        if not service:
            return jsonify({'message': 'Service not found'}), 404
        
        return jsonify({
            'service': Service.serialize(service)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching service: {str(e)}'}), 500
