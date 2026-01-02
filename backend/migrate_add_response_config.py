"""
Database Migration: Add Response Configuration to Services
Adds max_response_tokens, response_temperature, and response_timeout columns
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    """Add response configuration columns to services table"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    engine = create_engine(database_url)
    
    migrations = [
        {
            'name': 'Add max_response_tokens column',
            'sql': '''
                ALTER TABLE services 
                ADD COLUMN IF NOT EXISTS max_response_tokens INTEGER DEFAULT 300;
            '''
        },
        {
            'name': 'Add response_temperature column',
            'sql': '''
                ALTER TABLE services 
                ADD COLUMN IF NOT EXISTS response_temperature REAL DEFAULT 0.7;
            '''
        },
        {
            'name': 'Add response_timeout column',
            'sql': '''
                ALTER TABLE services 
                ADD COLUMN IF NOT EXISTS response_timeout INTEGER DEFAULT 30;
            '''
        },
        {
            'name': 'Update existing services with defaults',
            'sql': '''
                UPDATE services 
                SET 
                    max_response_tokens = COALESCE(max_response_tokens, 300),
                    response_temperature = COALESCE(response_temperature, 0.7),
                    response_timeout = COALESCE(response_timeout, 30)
                WHERE max_response_tokens IS NULL 
                   OR response_temperature IS NULL 
                   OR response_timeout IS NULL;
            '''
        }
    ]
    
    print("\n" + "=" * 80)
    print("DATABASE MIGRATION: Response Configuration")
    print("=" * 80 + "\n")
    
    try:
        with engine.connect() as conn:
            for migration in migrations:
                print(f"Running: {migration['name']}...")
                try:
                    conn.execute(text(migration['sql']))
                    conn.commit()
                    print(f"✅ {migration['name']} completed")
                except Exception as e:
                    print(f"⚠️  {migration['name']}: {str(e)}")
            
            # Verify columns exist
            result = conn.execute(text("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_name = 'services'
                AND column_name IN ('max_response_tokens', 'response_temperature', 'response_timeout')
                ORDER BY column_name;
            """))
            
            print("\n" + "-" * 80)
            print("Verification - New Columns:")
            print("-" * 80)
            for row in result:
                print(f"  ✅ {row[0]} ({row[1]}) - Default: {row[2]}")
            
            print("\n" + "=" * 80)
            print("✅ MIGRATION COMPLETED SUCCESSFULLY")
            print("=" * 80 + "\n")
            return True
            
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    success = run_migration()
    if success:
        print("You can now configure response settings in the admin panel:")
        print("  • Max Response Tokens: 100-1000 (default: 300)")
        print("  • Temperature: 0.0-1.0 (default: 0.7)")
        print("  • Timeout: 10-120 seconds (default: 30)")
    else:
        print("Migration failed. Please check the error messages above.")
