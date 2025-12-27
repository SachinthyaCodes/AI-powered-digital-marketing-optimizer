#!/usr/bin/env python3
"""
Clean Server Startup Script for MarketMatic Backend
Handles proper initialization and error recovery
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_server():
    """Start the Flask server with proper error handling"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from app import app
        from config import Config
        
        print("=" * 60)
        print("🚀 Starting MarketMatic Backend Server")
        print("=" * 60)
        print(f"📊 Database: {Config.DATABASE_NAME}")
        print(f"🌐 Server: http://localhost:5000")
        print(f"🔗 Frontend: http://localhost:3000")
        print("=" * 60)
        print("\n✅ Server is ready! Press CTRL+C to stop.\n")
        
        # Start server with minimal debug output
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Server error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    start_server()
