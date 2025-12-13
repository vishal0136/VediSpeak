"""
Blueprint registration
"""
from .auth import auth_bp
from .profile import profile_bp
from .pages import pages_bp
from .courses import courses_bp
from .media import media_bp
from .ml import ml_bp
from .api import api_bp

__all__ = ["auth_bp", "profile_bp", "pages_bp", "courses_bp", "media_bp", "ml_bp", "api_bp"]
