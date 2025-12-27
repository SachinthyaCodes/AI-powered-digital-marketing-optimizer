#!/usr/bin/env python
"""
Create a hybrid database setup that can use SQLite locally or PostgreSQL in production
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Determine which database to use
USE_SQLITE = os.getenv('USE_SQLITE', 'true').lower() == 'true'
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

print("=" * 70)
print("DATABASE SETUP WIZARD")
print("=" * 70)
print(f"\nEnvironment: {ENVIRONMENT}")
print(f"Use SQLite (local development): {USE_SQLITE}")

if USE_SQLITE:
    print("\n✓ Configuring SQLite database for local development...")
    DATABASE_URL = 'sqlite:///./test.db'
    print(f"  Database file: test.db")
    print(f"  This is perfect for development and testing")
    print(f"  When ready for production, set USE_SQLITE=false")
else:
    print("\n✓ Configuring PostgreSQL (Supabase) for production...")
    # Try to build from components
    db_host = os.getenv('DB_HOST', '')
    db_user = os.getenv('DB_USER', '')
    db_password = os.getenv('DB_PASSWORD', '')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'postgres')
    
    if all([db_host, db_user, db_password]):
        import urllib.parse
        encoded_password = urllib.parse.quote(db_password, safe='')
        DATABASE_URL = f'postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}'
        print(f"  Host: {db_host}")
        print(f"  User: {db_user}")
        print(f"  Database: {db_name}")
    else:
        print("  ⚠ Missing database credentials in .env")
        print("  Falling back to SQLite...")
        DATABASE_URL = 'sqlite:///./test.db'
        USE_SQLITE = True

print("\n" + "=" * 70)
print("\nNEXT STEPS:")
print("\n1. For LOCAL DEVELOPMENT (recommended):")
print("   - Use SQLite (default)")
print("   - Run: python supabase_setup.py")
print("   - Tables will be created in test.db")
print("   - You can develop and test locally")

print("\n2. For PRODUCTION with Supabase:")
print("   - Go to Supabase Console → Project Settings → API")
print("   - Copy your Project URL and anon key")
print("   - Add to .env:")
print("     SUPABASE_URL=<your-project-url>")
print("     SUPABASE_KEY=<your-anon-key>")
print("   - Set: USE_SQLITE=false")
print("   - If IPv6 connectivity fails, contact Supabase support")

print("\n3. Alternative if Supabase direct PostgreSQL doesn't work:")
print("   - Use Supabase REST API + Supabase Python client")
print("   - We'll configure this if direct connection fails")

print("\n" + "=" * 70)
