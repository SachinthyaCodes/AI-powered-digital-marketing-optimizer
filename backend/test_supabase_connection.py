"""
Test Supabase PostgreSQL Connection
Verifies database connectivity and configuration
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import sys

load_dotenv()

def test_supabase_connection():
    """Test connection to Supabase PostgreSQL database"""
    
    print("=" * 60)
    print("SUPABASE CONNECTION TEST")
    print("=" * 60)
    
    # Check environment variables
    print("\n1. Checking Environment Variables...")
    print("-" * 60)
    
    use_sqlite = os.getenv('USE_SQLITE', 'false').lower() == 'true'
    database_url = os.getenv('DATABASE_URL')
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
    supabase_service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    print(f"USE_SQLITE: {use_sqlite}")
    print(f"SUPABASE_URL: {supabase_url if supabase_url else '❌ NOT SET'}")
    print(f"DATABASE_URL: {database_url[:50] + '...' if database_url else '❌ NOT SET'}")
    print(f"SUPABASE_ANON_KEY: {'✅ Set (' + str(len(supabase_anon_key)) + ' chars)' if supabase_anon_key else '❌ NOT SET'}")
    print(f"SUPABASE_SERVICE_ROLE_KEY: {'✅ Set (' + str(len(supabase_service_role_key)) + ' chars)' if supabase_service_role_key else '❌ NOT SET'}")
    
    if use_sqlite:
        print("\n⚠️  WARNING: USE_SQLITE is set to 'true'")
        print("   Using local SQLite instead of Supabase PostgreSQL")
        print("   Set USE_SQLITE=false in .env to use Supabase")
        return False
    
    if not database_url:
        print("\n❌ ERROR: DATABASE_URL is not set in .env file")
        return False
    
    # Test database connection
    print("\n2. Testing Database Connection...")
    print("-" * 60)
    
    try:
        engine = create_engine(
            database_url,
            echo=False,
            connect_args={'connect_timeout': 10}
        )
        
        with engine.connect() as conn:
            # Test basic query
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL")
            print(f"   Version: {version}")
            
            # Check pgvector extension
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_extension WHERE extname = 'vector'
                );
            """))
            has_pgvector = result.fetchone()[0]
            
            if has_pgvector:
                print("✅ pgvector extension is installed")
            else:
                print("⚠️  pgvector extension is NOT installed")
                print("   Run: CREATE EXTENSION vector; in your Supabase SQL editor")
            
            # List tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"\n✅ Found {len(tables)} tables:")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("\n⚠️  No tables found. Run database initialization:")
                print("   python -c \"from database import init_db; init_db()\"")
            
        print("\n" + "=" * 60)
        print("✅ SUPABASE CONNECTION TEST PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\n" + "=" * 60)
        print("❌ SUPABASE CONNECTION TEST FAILED")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("1. Verify DATABASE_URL in .env is correct")
        print("2. Check Supabase project is active at https://supabase.com/dashboard")
        print("3. Verify password is URL-encoded (e.g., @ becomes %40)")
        print("4. Check firewall/network allows connection to Supabase")
        return False

if __name__ == '__main__':
    success = test_supabase_connection()
    sys.exit(0 if success else 1)
