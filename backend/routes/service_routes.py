from flask import Blueprint, request, jsonify
from database import SessionLocal
from models.sqlalchemy_models import Service, User
from auth.jwt_handler import token_required
from auth.decorators import superadmin_required
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
import uuid

service_bp = Blueprint('service', __name__, url_prefix='/api/services')

@service_bp.route('/', methods=['GET'])
@token_required
@superadmin_required
def get_all_services():
    """Get all services (superadmin only)"""
    db = SessionLocal()
    try:
        services = db.query(Service).all()
        
        return jsonify({
            'services': [service.to_dict() for service in services],
            'total': len(services)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching services: {str(e)}'}), 500
    finally:
        db.close()

@service_bp.route('/<service_id>', methods=['GET'])
@token_required
@superadmin_required
def get_service(service_id):
    """Get a single service by ID"""
    db = SessionLocal()
    try:
        service = db.query(Service).filter(Service.id == service_id).first()
        
        if not service:
            return jsonify({'message': 'Service not found'}), 404
        
        return jsonify({
            'service': service.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching service: {str(e)}'}), 500
    finally:
        db.close()

@service_bp.route('/', methods=['POST'])
@token_required
@superadmin_required
def create_service():
    """Create a new service (superadmin only)"""
    db = SessionLocal()
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
        existing_service = db.query(Service).filter(
            Service.email == data['email'].lower()
        ).first()
        
        if existing_service:
            return jsonify({'message': 'Service with this email already exists'}), 409
        
        # Generate unique service token
        service_token = Service.generate_token()
        
        # Ensure token is unique
        while db.query(Service).filter(Service.service_token == service_token).first():
            service_token = Service.generate_token()
        
        # Create new service
        new_service = Service(
            id=str(uuid.uuid4()),
            shop_name=data['shop_name'].strip(),
            owner_name=data['owner_name'].strip(),
            address=data['address'].strip(),
            email=data['email'].lower().strip(),
            phone=data['phone'].strip(),
            service_token=service_token,
            subscription_duration=data.get('subscription_duration'),
            subscription_unit=data.get('subscription_unit', 'month')
        )
        
        # Set subscription dates if duration is provided
        if new_service.subscription_duration:
            new_service.subscription_start = datetime.utcnow()
            # Calculate subscription end based on duration and unit
            try:
                from dateutil.relativedelta import relativedelta
                if new_service.subscription_unit == 'month':
                    new_service.subscription_end = new_service.subscription_start + relativedelta(months=new_service.subscription_duration)
                elif new_service.subscription_unit == 'year':
                    new_service.subscription_end = new_service.subscription_start + relativedelta(years=new_service.subscription_duration)
                elif new_service.subscription_unit == 'day':
                    new_service.subscription_end = new_service.subscription_start + relativedelta(days=new_service.subscription_duration)
            except ImportError:
                # Fallback to timedelta if dateutil is not available
                from datetime import timedelta
                if new_service.subscription_unit == 'month':
                    new_service.subscription_end = new_service.subscription_start + timedelta(days=30 * new_service.subscription_duration)
                elif new_service.subscription_unit == 'year':
                    new_service.subscription_end = new_service.subscription_start + timedelta(days=365 * new_service.subscription_duration)
                elif new_service.subscription_unit == 'day':
                    new_service.subscription_end = new_service.subscription_start + timedelta(days=new_service.subscription_duration)
        
        db.add(new_service)
        db.commit()
        db.refresh(new_service)
        
        return jsonify({
            'message': 'Service created successfully',
            'service': new_service.to_dict()
        }), 201
        
    except Exception as e:
        db.rollback()
        import traceback
        print(f"Error creating service: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'Error creating service: {str(e)}'}), 500
    finally:
        db.close()

@service_bp.route('/<service_id>', methods=['PUT'])
@token_required
@superadmin_required
def update_service(service_id):
    """Update a service (superadmin only)"""
    db = SessionLocal()
    try:
        data = request.get_json()
        
        # Check if service exists
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return jsonify({'message': 'Service not found'}), 404
        
        # Update allowed fields
        allowed_fields = ['shop_name', 'owner_name', 'address', 'email', 'phone', 
                         'subscription_duration', 'subscription_unit', 'is_active']
        
        for field in allowed_fields:
            if field in data:
                if field == 'email':
                    # Validate email
                    try:
                        validate_email(data[field])
                        setattr(service, field, data[field].lower().strip())
                    except EmailNotValidError:
                        return jsonify({'message': 'Invalid email format'}), 400
                elif field in ['shop_name', 'owner_name', 'address', 'phone']:
                    setattr(service, field, data[field].strip())
                else:
                    setattr(service, field, data[field])
        
        # Recalculate subscription end date if duration or unit changed
        if 'subscription_duration' in data or 'subscription_unit' in data:
            from dateutil.relativedelta import relativedelta
            
            subscription_start = service.subscription_start or datetime.utcnow()
            subscription_duration = data.get('subscription_duration', service.subscription_duration)
            subscription_unit = data.get('subscription_unit', service.subscription_unit)
            
            if subscription_duration:
                service.subscription_start = subscription_start
                if subscription_unit == 'month':
                    service.subscription_end = subscription_start + relativedelta(months=subscription_duration)
                elif subscription_unit == 'year':
                    service.subscription_end = subscription_start + relativedelta(years=subscription_duration)
                elif subscription_unit == 'day':
                    service.subscription_end = subscription_start + relativedelta(days=subscription_duration)
        
        service.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(service)
        
        return jsonify({
            'message': 'Service updated successfully',
            'service': service.to_dict()
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'Error updating service: {str(e)}'}), 500
    finally:
        db.close()

@service_bp.route('/<service_id>', methods=['DELETE'])
@token_required
@superadmin_required
def delete_service(service_id):
    """Delete a service (superadmin only)"""
    db = SessionLocal()
    try:
        # Check if service exists
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return jsonify({'message': 'Service not found'}), 404
        
        # Delete service
        db.delete(service)
        db.commit()
        
        return jsonify({
            'message': 'Service deleted successfully'
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'Error deleting service: {str(e)}'}), 500
    finally:
        db.close()

@service_bp.route('/<service_id>/subscription', methods=['PUT'])
@token_required
@superadmin_required
def update_subscription(service_id):
    """Update service subscription (superadmin only)"""
    db = SessionLocal()
    try:
        data = request.get_json()
        
        # Check if service exists
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return jsonify({'message': 'Service not found'}), 404
        
        subscription_duration = data.get('subscription_duration')
        subscription_unit = data.get('subscription_unit', 'month')
        
        if not subscription_duration:
            return jsonify({'message': 'subscription_duration is required'}), 400
        
        # Calculate new subscription dates
        from dateutil.relativedelta import relativedelta
        
        subscription_start = datetime.utcnow()
        
        if subscription_unit == 'month':
            subscription_end = subscription_start + relativedelta(months=subscription_duration)
        elif subscription_unit == 'year':
            subscription_end = subscription_start + relativedelta(years=subscription_duration)
        elif subscription_unit == 'day':
            subscription_end = subscription_start + relativedelta(days=subscription_duration)
        else:
            subscription_end = subscription_start + relativedelta(months=subscription_duration)
        
        # Update service
        service.subscription_duration = subscription_duration
        service.subscription_unit = subscription_unit
        service.subscription_start = subscription_start
        service.subscription_end = subscription_end
        service.is_active = True
        service.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(service)
        
        return jsonify({
            'message': 'Subscription updated successfully',
            'service': service.to_dict()
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'message': f'Error updating subscription: {str(e)}'}), 500
    finally:
        db.close()

@service_bp.route('/my-service', methods=['GET'])
@token_required
def get_my_service():
    """Get service information for the current admin user"""
    db = SessionLocal()
    try:
        user_id = request.current_user['user_id']
        user_role = request.current_user.get('role', 'user')
        
        # Only admin users can access this endpoint
        if user_role != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        
        # Get user to find their service_id
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        service_id = user.service_id
        
        if not service_id:
            return jsonify({'message': 'No service linked to this account'}), 404
        
        # Get service information
        service = db.query(Service).filter(Service.id == service_id).first()
        
        if not service:
            return jsonify({'message': 'Service not found'}), 404
        
        return jsonify({
            'service': service.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching service: {str(e)}'}), 500
    finally:
        db.close()
