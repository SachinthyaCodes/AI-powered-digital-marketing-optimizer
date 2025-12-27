#!/usr/bin/env python
"""
Production server runner for MarketMatic Backend
"""
from flask import Flask, jsonify
from flask_cors import CORS
from database import db_instance
from routes.auth_routes import auth_bp
from routes.superadmin_routes import superadmin_auth_bp
from routes.service_routes import service_bp
from routes.bot_routes import bot_bp
from routes.rag_routes import rag_bp
from routes.chat_routes import chat_bp
from config import Config

def create_app():
    app = Flask(__name__)

    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(superadmin_auth_bp)
    app.register_blueprint(service_bp)
    app.register_blueprint(bot_bp)
    app.register_blueprint(rag_bp)
    app.register_blueprint(chat_bp)

    @app.route('/')
    def home():
        return jsonify({
            'message': 'MarketMatic API',
            'version': '1.0.0',
            'status': 'running'
        })

    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'database': 'connected' if db_instance.get_db() else 'disconnected'
        })

    @app.before_request
    def before_request():
        """Initialize database connection before first request"""
        db_instance.get_db()

    @app.teardown_appcontext
    def teardown_db(exception=None):
        """Close database connection when app context ends"""
        pass  # Keep connection alive for reuse

    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting MarketMatic Backend Server...")
    print(f"Database: {Config.DATABASE_URL}")
    print("Server running at:")
    print("- Local: http://127.0.0.1:5000")
    print("- Network: http://0.0.0.0:5000")
    print("Press Ctrl+C to stop the server")
    
    # Run in production mode without debug
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)