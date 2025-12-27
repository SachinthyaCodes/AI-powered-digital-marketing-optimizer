from flask import Flask, jsonify
from flask_cors import CORS
from database import engine, SessionLocal
from routes.auth_routes import auth_bp
from routes.superadmin_routes import superadmin_auth_bp
from routes.service_routes import service_bp
from routes.bot_routes import bot_bp
from routes.rag_routes import rag_bp
from routes.chat_routes import chat_bp
from routes.document_routes import document_bp
from config import Config

app = Flask(__name__)

# Configure CORS with comprehensive settings
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
        "supports_credentials": True,
        "expose_headers": ["Content-Range", "X-Content-Range"]
    }
})

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(superadmin_auth_bp)
app.register_blueprint(service_bp)
app.register_blueprint(bot_bp)
app.register_blueprint(rag_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(document_bp)

@app.route('/')
def home():
    return jsonify({
        'message': 'MarketMatic API',
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/api/health')
def health():
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'database': db_status
    })

@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler"""
    import traceback
    print(f"Unhandled exception: {str(e)}")
    print(traceback.format_exc())
    return jsonify({
        'message': f'Internal server error: {str(e)}'
    }), 500

@app.before_request
def before_request():
    """Initialize database connection before first request - SQLAlchemy handles this"""
    pass

@app.teardown_appcontext
def teardown_db(exception=None):
    """Close database connection when app context ends"""
    pass  # SQLAlchemy session cleanup handled by SessionLocal

if __name__ == '__main__':
    print("Starting MarketMatic Backend Server...")
    
    # Display database info
    if Config.USE_SQLITE:
        print("Database: SQLite (Local Development)")
    elif Config.DATABASE_URL:
        # Extract database name from URL for display
        db_info = Config.DATABASE_URL.split('@')[-1] if '@' in Config.DATABASE_URL else 'PostgreSQL'
        print(f"Database: Supabase PostgreSQL ({db_info})")
    else:
        print("Database: None (Configuration Error!)")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
