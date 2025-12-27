"""
Test Service Creation Endpoint
"""
import requests
import json

# First login as superadmin
print("Testing Service Creation...")
print("=" * 60)

# Test data
service_data = {
    "shop_name": "Test Shop",
    "owner_name": "Test Owner",
    "address": "123 Test Street",
    "email": "testshop@example.com",
    "phone": "+1234567890",
    "subscription_duration": 12,
    "subscription_unit": "month"
}

# You need to login first and get the token
print("Step 1: Login as superadmin to get token")
print("(You need to run this manually with your superadmin credentials)")
print()
print("Step 2: Test service creation")
print(f"POST http://localhost:5000/api/services/")
print(f"Headers: Authorization: Bearer <YOUR_TOKEN>")
print(f"Body: {json.dumps(service_data, indent=2)}")
print()
print("Testing without auth (should fail with 401)...")

try:
    response = requests.post(
        'http://localhost:5000/api/services/',
        json=service_data,
        timeout=5
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

print()
print("=" * 60)
print("To test with authentication:")
print("1. Get superadmin token from login")
print("2. Run: curl -X POST http://localhost:5000/api/services/ \\")
print("        -H 'Authorization: Bearer <TOKEN>' \\")
print("        -H 'Content-Type: application/json' \\")
print(f"        -d '{json.dumps(service_data)}'")
