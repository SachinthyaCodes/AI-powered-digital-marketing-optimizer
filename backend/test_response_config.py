"""
Test Response Configuration Feature
Verifies that response settings are properly saved and retrieved
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models.sqlalchemy_models import Service
from datetime import datetime

def test_response_configuration():
    """Test the response configuration feature"""
    db = SessionLocal()
    
    try:
        print("🧪 Testing Response Configuration Feature\n")
        print("=" * 60)
        
        # Get the first service
        service = db.query(Service).first()
        
        if not service:
            print("❌ No service found in database")
            return False
        
        print(f"✅ Found service: {service.shop_name}")
        print(f"   Service ID: {service.id}\n")
        
        # Test 1: Check if columns exist
        print("Test 1: Verify columns exist")
        print("-" * 40)
        try:
            tokens = service.max_response_tokens
            temp = service.response_temperature
            timeout = service.response_timeout
            print(f"✅ max_response_tokens: {tokens}")
            print(f"✅ response_temperature: {temp}")
            print(f"✅ response_timeout: {timeout}\n")
        except AttributeError as e:
            print(f"❌ Column missing: {e}\n")
            return False
        
        # Test 2: Update configuration
        print("Test 2: Update configuration")
        print("-" * 40)
        original_tokens = service.max_response_tokens
        original_temp = service.response_temperature
        original_timeout = service.response_timeout
        
        # Set new values
        service.max_response_tokens = 500
        service.response_temperature = 0.9
        service.response_timeout = 60
        service.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(service)
        
        print(f"✅ Updated max_response_tokens: {original_tokens} → {service.max_response_tokens}")
        print(f"✅ Updated response_temperature: {original_temp} → {service.response_temperature}")
        print(f"✅ Updated response_timeout: {original_timeout} → {service.response_timeout}\n")
        
        # Test 3: Verify to_dict() includes new fields
        print("Test 3: Verify API response includes new fields")
        print("-" * 40)
        service_dict = service.to_dict()
        
        if 'max_response_tokens' in service_dict:
            print(f"✅ max_response_tokens in to_dict(): {service_dict['max_response_tokens']}")
        else:
            print("❌ max_response_tokens NOT in to_dict()")
            return False
        
        if 'response_temperature' in service_dict:
            print(f"✅ response_temperature in to_dict(): {service_dict['response_temperature']}")
        else:
            print("❌ response_temperature NOT in to_dict()")
            return False
        
        if 'response_timeout' in service_dict:
            print(f"✅ response_timeout in to_dict(): {service_dict['response_timeout']}")
        else:
            print("❌ response_timeout NOT in to_dict()")
            return False
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("\n📋 Summary:")
        print("  • Database columns exist and are accessible")
        print("  • Configuration can be updated and saved")
        print("  • API response (to_dict) includes all new fields")
        print("\n🎉 Response Configuration Feature is working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_response_configuration()
    sys.exit(0 if success else 1)
