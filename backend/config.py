import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_SECRET = os.environ.get('JWT_SECRET', 'your-jwt-secret-change-in-production')
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL', 'your-supabase-url')
    SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', 'your-supabase-anon-key')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', 'your-supabase-service-key')
    
    # JWT Configuration
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
    
    # Database Configuration
    DATABASE_TABLES = {
        'users': 'users',
        'posts': 'marketplace_posts',
        'chats': 'user_chats',
        'messages': 'chat_messages',
        'profiles': 'user_profiles'
    }
    
    # CORS Configuration
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:8000",
        "https://farmlinkk.netlify.app",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:8000"
    ]
    
    # Server Configuration
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('FLASK_ENV') == 'development'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    config_name = os.environ.get('FLASK_ENV', 'default')
    return config.get(config_name, config['default'])
