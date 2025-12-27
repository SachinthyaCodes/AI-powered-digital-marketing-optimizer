#!/usr/bin/env python
"""Test Supabase connection with different password encodings"""
import urllib.parse
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Get credentials
db_host = os.getenv('DB_HOST', 'db.fhzrfzxrxvirydkeetme.supabase.co')
db_user = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD', '')
db_port = int(os.getenv('DB_PORT', '5432'))
db_name = os.getenv('DB_NAME', 'postgres')

print("=" * 60)
print("TESTING SUPABASE CONNECTION")
print("=" * 60)
print(f"Host: {db_host}")
print(f"User: {db_user}")
print(f"Password: {'*' * len(db_password)}")
print(f"Port: {db_port}")
print(f"Database: {db_name}")
print("=" * 60)

# Test 1: Direct psycopg2 connection with components
print("\n✓ Test 1: Using psycopg2.connect() with individual parameters...")
try:
    conn = psycopg2.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        port=db_port,
        database=db_name,
        connect_timeout=5
    )
    print("✅ Connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")

# Test 2: Using connection string with URL encoding
print("\n✓ Test 2: Using URL-encoded password in connection string...")
encoded_pwd = urllib.parse.quote(db_password, safe='')
url = f'postgresql://{db_user}:{encoded_pwd}@{db_host}:{db_port}/{db_name}'
print(f"URL: {url[:50]}...@{db_host}...")
try:
    conn = psycopg2.connect(url)
    print("✅ Connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")

# Test 3: Raw password in URL
print("\n✓ Test 3: Using raw password in connection string...")
url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
print(f"URL (password hidden): postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")
try:
    conn = psycopg2.connect(url)
    print("✅ Connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")

print("\n" + "=" * 60)
print("Testing complete!")
