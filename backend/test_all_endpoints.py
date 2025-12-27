"""
Complete API Test Suite for Supabase PostgreSQL Backend
Tests all major endpoints to ensure they work correctly
"""
import requests
import json

BASE_URL = "http://localhost:5000"

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def test_health():
    """Test health endpoint"""
    print(f"\n{BLUE}Testing Health Endpoint{RESET}")
    print("-" * 60)
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"{GREEN}✓ Health check passed{RESET}")
            print(f"  Status: {data.get('status')}")
            print(f"  Database: {data.get('database')}")
            return True
        else:
            print(f"{RED}✗ Health check failed: {response.status_code}{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Health check error: {e}{RESET}")
        return False

def test_superadmin_register():
    """Test superadmin registration"""
    print(f"\n{BLUE}Testing Superadmin Registration{RESET}")
    print("-" * 60)
    try:
        payload = {
            "email": "superadmin@test.com",
            "password": "SuperPass123!",
            "full_name": "Super Admin"
        }
        response = requests.post(f"{BASE_URL}/api/superadmin/register", json=payload, timeout=5)
        
        if response.status_code in [201, 409]:  # 201 = created, 409 = already exists
            print(f"{GREEN}✓ Superadmin registration endpoint working{RESET}")
            if response.status_code == 409:
                print(f"{YELLOW}  Note: Superadmin already exists{RESET}")
            return True
        else:
            print(f"{RED}✗ Registration failed: {response.status_code}{RESET}")
            print(f"  Response: {response.json()}")
            return False
    except Exception as e:
        print(f"{RED}✗ Registration error: {e}{RESET}")
        return False

def test_superadmin_login():
    """Test superadmin login and return token"""
    print(f"\n{BLUE}Testing Superadmin Login{RESET}")
    print("-" * 60)
    try:
        # Use hardcoded credentials
        payload = {
            "username": "superadmin",
            "password": "superadmin"
        }
        response = requests.post(f"{BASE_URL}/api/superadmin/login", json=payload, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"{GREEN}✓ Login successful{RESET}")
            print(f"  Token: {token[:20]}...{token[-20:]}")
            return token
        else:
            print(f"{RED}✗ Login failed: {response.status_code}{RESET}")
            print(f"  Response: {response.json()}")
            return None
    except Exception as e:
        print(f"{RED}✗ Login error: {e}{RESET}")
        return None

def test_service_creation(token):
    """Test service creation"""
    print(f"\n{BLUE}Testing Service Creation{RESET}")
    print("-" * 60)
    
    if not token:
        print(f"{YELLOW}⊘ Skipping (no token){RESET}")
        return None
    
    try:
        import time
        import random
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "shop_name": "Test Shop",
            "owner_name": "Test Owner",
            "address": "123 Test Street",
            "email": f"testshop{random.randint(1000,9999)}@example.com",  # Unique email
            "phone": "+1234567890",
            "subscription_duration": 12,
            "subscription_unit": "month"
        }
        
        response = requests.post(f"{BASE_URL}/api/services/", json=payload, headers=headers, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            service = data.get('service')
            print(f"{GREEN}✓ Service created successfully{RESET}")
            print(f"  Service ID: {service.get('id')}")
            print(f"  Service Token: {service.get('service_token')}")
            print(f"  Shop Name: {service.get('shop_name')}")
            return service
        else:
            print(f"{RED}✗ Service creation failed: {response.status_code}{RESET}")
            print(f"  Response: {response.json()}")
            return None
    except Exception as e:
        print(f"{RED}✗ Service creation error: {e}{RESET}")
        import traceback
        print(traceback.format_exc())
        return None

def test_get_services(token):
    """Test getting all services"""
    print(f"\n{BLUE}Testing Get All Services{RESET}")
    print("-" * 60)
    
    if not token:
        print(f"{YELLOW}⊘ Skipping (no token){RESET}")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/services/", headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            services = data.get('services', [])
            print(f"{GREEN}✓ Retrieved {len(services)} services{RESET}")
            for service in services[:3]:  # Show first 3
                print(f"  - {service.get('shop_name')} ({service.get('email')})")
            if len(services) > 3:
                print(f"  ... and {len(services) - 3} more")
            return True
        else:
            print(f"{RED}✗ Get services failed: {response.status_code}{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Get services error: {e}{RESET}")
        return False

def test_admin_signup(service_token):
    """Test admin signup with service token"""
    print(f"\n{BLUE}Testing Admin Signup{RESET}")
    print("-" * 60)
    
    if not service_token:
        print(f"{YELLOW}⊘ Skipping (no service token){RESET}")
        return None
    
    try:
        import time
        payload = {
            "email": f"admin_{int(time.time())}@test.com",
            "password": "AdminPass123!",
            "full_name": "Test Admin",
            "company_name": "Test Company",
            "is_admin": True,
            "service_token": service_token
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/signup", json=payload, timeout=5)
        
        if response.status_code == 201:
            data = response.json()
            print(f"{GREEN}✓ Admin created successfully{RESET}")
            print(f"  Email: {payload['email']}")
            return data
        else:
            print(f"{RED}✗ Admin signup failed: {response.status_code}{RESET}")
            print(f"  Response: {response.json()}")
            return None
    except Exception as e:
        print(f"{RED}✗ Admin signup error: {e}{RESET}")
        return None

def run_all_tests():
    """Run all API tests"""
    print("=" * 60)
    print(f"{BLUE}MARKETMATIC API TEST SUITE{RESET}")
    print(f"{BLUE}Supabase PostgreSQL Backend{RESET}")
    print("=" * 60)
    
    results = {
        'passed': 0,
        'failed': 0,
        'skipped': 0
    }
    
    # Test 1: Health check
    if test_health():
        results['passed'] += 1
    else:
        results['failed'] += 1
        print(f"\n{RED}⚠ Backend is not running or unhealthy. Stopping tests.{RESET}")
        return results
    
    # Test 2: Superadmin registration
    if test_superadmin_register():
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 3: Superadmin login
    token = test_superadmin_login()
    if token:
        results['passed'] += 1
    else:
        results['failed'] += 1
        print(f"\n{RED}⚠ Cannot continue without token{RESET}")
        return results
    
    # Test 4: Service creation
    service = test_service_creation(token)
    if service:
        results['passed'] += 1
        service_token = service.get('service_token')
    else:
        results['failed'] += 1
        service_token = None
    
    # Test 5: Get all services
    if test_get_services(token):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 6: Admin signup
    if service_token:
        if test_admin_signup(service_token):
            results['passed'] += 1
        else:
            results['failed'] += 1
    else:
        print(f"\n{YELLOW}⊘ Skipping admin signup (no service token){RESET}")
        results['skipped'] += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print("=" * 60)
    print(f"{GREEN}✓ Passed: {results['passed']}{RESET}")
    print(f"{RED}✗ Failed: {results['failed']}{RESET}")
    print(f"{YELLOW}⊘ Skipped: {results['skipped']}{RESET}")
    print("=" * 60)
    
    return results

if __name__ == '__main__':
    results = run_all_tests()
    exit(0 if results['failed'] == 0 else 1)
