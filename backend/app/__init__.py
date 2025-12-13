"""
Flask application factory pattern with SocketIO support
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from .extensions import mysql, bcrypt, socketio
from .config import config

def create_app(config_name=None):
    """Create and configure Flask app"""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")
    
    app = Flask(__name__,
                template_folder="../../frontend/templates",
                static_folder="../../frontend/static")
    
    # Load config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    mysql.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    
    # Setup logging
    setup_logging(app)
    
    # Test DB connection
    from .utils.db_helpers import test_db_connection
    test_db_connection(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create necessary folders
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    return app

def register_blueprints(app):
    """Register all blueprints"""
    from .routes import auth_bp, profile_bp, pages_bp, courses_bp, media_bp, ml_bp, api_bp
    from .routes.activity_api import activity_api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(media_bp)
    app.register_blueprint(ml_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(activity_api_bp)

def register_error_handlers(app):
    """Register error handlers"""
    from flask import jsonify, render_template, request
    
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Not found"}), 404
        return jsonify({"error": "Page not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal error: {error}")
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal server error"}), 500
        return jsonify({"error": "Internal server error"}), 500

def setup_logging(app):
    """Setup application logging"""
    if not app.debug and not app.testing:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            app.config.get("LOG_FILE", "logs/app.log"),
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info("VediSpeak startup")
