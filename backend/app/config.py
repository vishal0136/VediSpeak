"""
Configuration management for different environments
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.environ.get("VEDISPEAK_SECRET", "dev-secret-change-me")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16MB
    
    # Database
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DB = os.environ.get("MYSQL_DB", "isl_app")
    MYSQL_CURSORCLASS = "DictCursor"
    
    # Upload
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "storage/uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf", "docx"}
    
    # Session
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Redis Cache
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TYPE = "redis" if os.environ.get("REDIS_URL") else "simple"
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = "isl_"
    
    # Celery
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
    
    # ML Model
    MODEL_PATH = os.environ.get("MODEL_PATH", "checkpoints/best.pth")
    MODEL_ARCH = os.environ.get("MODEL_ARCH", "efficientnet_b0")
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL", "memory://")
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    
    # OTP Configuration
    OTP_EXPIRY_MINUTES = int(os.environ.get("OTP_EXPIRY_MINUTES", 10))
    
    # Twilio (SMS)
    TWILIO_SID = os.environ.get("TWILIO_SID")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE = os.environ.get("TWILIO_PHONE")
    TWILIO_MESSAGING_SERVICE_SID = os.environ.get("TWILIO_MESSAGING_SERVICE_SID")
    
    # SendGrid (Email)
    SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
    
    # Google OAuth
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
    
    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE = os.environ.get("LOG_FILE", "logs/app.log")

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

# Testing configuration removed for production deployment

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
