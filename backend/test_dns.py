#!/usr/bin/env python
"""Test IPv4 vs IPv6 connectivity to Supabase"""
import socket
import os
from dotenv import load_dotenv

load_dotenv()

db_host = os.getenv('DB_HOST', 'db.fhzrfzxrxvirydkeetme.supabase.co')

print("=" * 60)
print("TESTING DNS RESOLUTION")
print("=" * 60)

try:
    # Get all addresses
    results = socket.getaddrinfo(db_host, 5432, socket.AF_UNSPEC, socket.SOCK_STREAM)
    print(f"\nResolution results for {db_host}:")
    for family, socktype, proto, canonname, sockaddr in results:
        family_name = "IPv6" if family == socket.AF_INET6 else "IPv4"
        print(f"  {family_name}: {sockaddr[0]}:{sockaddr[1]}")
    
    # Try to connect with IPv4 only
    print(f"\nAttempting IPv4 connection to {db_host}:5432...")
    results_ipv4 = socket.getaddrinfo(db_host, 5432, socket.AF_INET, socket.SOCK_STREAM)
    if results_ipv4:
        for family, socktype, proto, canonname, sockaddr in results_ipv4:
            print(f"  IPv4 Address: {sockaddr[0]}")
            try:
                sock = socket.socket(family, socktype, proto)
                sock.settimeout(5)
                sock.connect(sockaddr)
                print(f"  ✅ Connected to {sockaddr[0]}:{sockaddr[1]}")
                sock.close()
            except Exception as e:
                print(f"  ❌ Failed to connect: {e}")
    else:
        print("  No IPv4 addresses found")
        
except Exception as e:
    print(f"Error during DNS resolution: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
