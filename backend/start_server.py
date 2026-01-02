"""
Simple server starter without console issues
"""
import sys
import os

# Suppress Flask banner to avoid console errors
os.environ['FLASK_SKIP_DOTENV'] = '1'

# Import app
from app import app

if __name__ == '__main__':
    print("Starting MarketMatic Backend Server...")
    print("Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    # Run without debug mode to avoid console issues
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
