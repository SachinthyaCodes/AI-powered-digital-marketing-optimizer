"""
Script to create a superadmin user in the database
Run this once to add the superadmin account
"""

from database import SessionLocal, init_db
from models.sqlalchemy_models import User
import uuid

def create_superadmin():
    # Initialize database if not already done
    init_db()
    
    db = SessionLocal()
    try:
        # Check if superadmin already exists
        existing = db.query(User).filter(User.email == 'superadmin@marketmatic.com').first()
        
        if existing:
            print("[OK] Superadmin already exists!")
            return
        
        # Create superadmin user
        superadmin = User(
            id=str(uuid.uuid4()),
            email='superadmin@marketmatic.com',
            password=User.hash_password('superadmin'),
            full_name='Super Administrator',
            company_name='MarketMatic',
            role='superadmin'
        )
        
        db.add(superadmin)
        db.commit()
        
        print(f"[OK] Superadmin created successfully with ID: {superadmin.id}")
        print("Email: superadmin@marketmatic.com")
        print("Password: superadmin")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to create superadmin: {str(e)}")
    finally:
        db.close()

if __name__ == '__main__':
    create_superadmin()
