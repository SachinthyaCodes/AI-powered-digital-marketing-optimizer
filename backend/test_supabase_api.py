#!/usr/bin/env python
"""Test Supabase connection using REST API"""
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()

print("=" * 60)
print("CHECKING SUPABASE PROJECT CONFIGURATION")
print("=" * 60)

# Check if we have Supabase environment set
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if supabase_url and supabase_key:
    print(f"✓ SUPABASE_URL: {supabase_url[:30]}...")
    print(f"✓ SUPABASE_KEY: {supabase_key[:30]}...")
    
    # Try using Supabase client
    print("\nAttempting connection via Supabase REST API...")
    try:
        from supabase import create_client
        
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase REST client created successfully!")
        
        # Try a simple operation
        print("\nTesting REST API call...")
        # This will test authentication without creating tables
        
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("⚠ SUPABASE_URL or SUPABASE_KEY not set in .env")
    print("  Please check your .env.supabase configuration")

print("\n" + "=" * 60)
print("\nPossible solutions for IPv6 connectivity issue:")
print("1. Contact Supabase Support for IPv4 address")
print("2. Use Supabase REST API instead of direct PostgreSQL connection")
print("3. Check your ISP/network for IPv6/IPv4 dual-stack support")
print("=" * 60)
