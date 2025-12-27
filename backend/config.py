import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    USE_SQLITE = os.getenv('USE_SQLITE', 'false').lower() == 'true'
    DATABASE_URL = os.getenv('DATABASE_URL')
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    SUPABASE_SECRET_KEY = os.getenv('SUPABASE_SECRET_KEY')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-secret-key')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
    
    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')  # Your email
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # Your app password
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))
    
    # Frontend URL (for password reset links)
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    
    # Cloudinary Configuration (for image uploads)
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
    
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_CHAT_MODEL = os.getenv('OLLAMA_CHAT_MODEL', 'llama3')
    OLLAMA_EMBEDDING_MODEL = os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')
    
    # Modal RAG Service Configuration (Optional)
    MODAL_EMBEDDING_URL = os.getenv('MODAL_EMBEDDING_URL')
    MODAL_CHAT_URL = os.getenv('MODAL_CHAT_URL')
