"""
Quick database connection test
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

print("🔍 Testing database connection...")
print(f"Database URL: {DATABASE_URL[:50]}..." if DATABASE_URL else "No DATABASE_URL found")

try:
    # Create engine with short timeout
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            'connect_timeout': 5
        }
    )
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        
        # Check if users table exists
        result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"))
        table_exists = result.scalar()
        
        if table_exists:
            print("✅ Users table exists!")
            # Count users
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"📊 Users in database: {count}")
        else:
            print("⚠️  Users table does not exist - needs initialization")
            
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check if the password is correct")
    print("2. Verify your internet connection")
    print("3. Check if Supabase project is active")
    print("4. Try enabling IPv4 instead of IPv6")
