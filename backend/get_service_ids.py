from database import db_instance
from bson import ObjectId

db = db_instance.get_db()

# Get all services
services = list(db.services.find())

print("\n=== Available Services ===\n")
if services:
    for service in services:
        service_id = str(service['_id'])
        service_name = service.get('service_name', 'N/A')
        admin_name = service.get('admin_name', 'N/A')
        print(f"Service: {service_name}")
        print(f"Admin: {admin_name}")
        print(f"Service ID: {service_id}")
        print(f"Chat URL: http://localhost:3000/chat/{service_id}")
        print("-" * 50)
else:
    print("No services found. Please create a service first via SuperAdmin.")

# Get users with admin role
print("\n=== Admin Users ===\n")
admins = list(db.users.find({'role': 'admin'}))
for admin in admins:
    admin_id = str(admin['_id'])
    email = admin.get('email', 'N/A')
    service_id = admin.get('service_id', 'N/A')
    print(f"Admin Email: {email}")
    print(f"Service ID: {service_id}")
    print("-" * 50)
