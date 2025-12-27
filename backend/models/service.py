from datetime import datetime
import secrets

class Service:
    def __init__(self, shop_name, owner_name, address, email, phone, subscription_duration=None, subscription_unit='month'):
        self.shop_name = shop_name
        self.owner_name = owner_name
        self.address = address
        self.email = email
        self.phone = phone
        self.service_token = self.generate_token()
        self.subscription_duration = subscription_duration  # e.g., 1, 2, 3
        self.subscription_unit = subscription_unit  # 'week', 'month', 'year'
        self.subscription_start = None
        self.subscription_end = None
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @staticmethod
    def generate_token():
        """Generate a unique 32-character service token"""
        return secrets.token_hex(16).upper()

    def calculate_subscription_end(self):
        """Calculate subscription end date based on duration and unit"""
        if not self.subscription_start or not self.subscription_duration:
            return None
        
        from dateutil.relativedelta import relativedelta
        
        if self.subscription_unit == 'week':
            delta = relativedelta(weeks=self.subscription_duration)
        elif self.subscription_unit == 'month':
            delta = relativedelta(months=self.subscription_duration)
        elif self.subscription_unit == 'year':
            delta = relativedelta(years=self.subscription_duration)
        else:
            return None
        
        return self.subscription_start + delta

    def to_dict(self):
        """Convert service object to dictionary"""
        return {
            'shop_name': self.shop_name,
            'owner_name': self.owner_name,
            'address': self.address,
            'email': self.email,
            'phone': self.phone,
            'service_token': self.service_token,
            'subscription_duration': self.subscription_duration,
            'subscription_unit': self.subscription_unit,
            'subscription_start': self.subscription_start,
            'subscription_end': self.subscription_end,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def serialize(service_doc):
        """Serialize service document from MongoDB"""
        if service_doc:
            # Handle both old schema (business_name) and new schema (shop_name)
            shop_name = service_doc.get('shop_name') or service_doc.get('business_name', '')
            owner_name = service_doc.get('owner_name', '')
            address = service_doc.get('address', '')
            email = service_doc.get('email', '')
            phone = service_doc.get('phone', '')
            
            # Handle both service_token and token fields
            service_token = service_doc.get('service_token') or service_doc.get('token', '')
            
            # Handle datetime fields safely
            created_at = service_doc.get('created_at')
            updated_at = service_doc.get('updated_at')
            subscription_start = service_doc.get('subscription_start')
            subscription_end = service_doc.get('subscription_end')
            
            # Convert datetime objects to ISO format
            def safe_datetime_convert(dt_obj):
                if dt_obj:
                    if isinstance(dt_obj, datetime):
                        return dt_obj.isoformat()
                    elif isinstance(dt_obj, str):
                        return dt_obj
                return None
            
            return {
                'id': str(service_doc['_id']),
                'shop_name': shop_name,
                'owner_name': owner_name,
                'address': address,
                'email': email,
                'phone': phone,
                'service_token': service_token,
                'subscription_duration': service_doc.get('subscription_duration'),
                'subscription_unit': service_doc.get('subscription_unit'),
                'subscription_start': safe_datetime_convert(subscription_start),
                'subscription_end': safe_datetime_convert(subscription_end),
                'is_active': service_doc.get('is_active', True),
                'status': service_doc.get('status', 'active'),  # Include status field for backward compatibility
                'business_type': service_doc.get('business_type', ''),  # Include business_type for backward compatibility
                'subscription_plan': service_doc.get('subscription_plan', ''),  # Include subscription_plan for backward compatibility
                'created_at': safe_datetime_convert(created_at),
                'updated_at': safe_datetime_convert(updated_at)
            }
        return None
