"""
Pedigree Tracker Application

This package contains the core functionality for the Pedigree Tracker application.
"""
from flask import Flask
from flask_cors import CORS

from .config import DATABASE_URI, DEBUG, SECRET_KEY, API_PREFIX
from .database import init_db, SessionLocal
from .api import api_bp as api_blueprint

__version__ = '0.1.0'

def create_app(test_config=None):
    """Create and configure the Flask application.
    
    Args:
        test_config (dict, optional): Testing configuration. Defaults to None.
    
    Returns:
        Flask: The configured Flask application.
    """
    app = Flask(__name__)
    
    # Configure the app
    app.config.update(
        SECRET_KEY=SECRET_KEY,
        DEBUG=DEBUG,
        SQLALCHEMY_DATABASE_URI=DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    if test_config:
        app.config.update(test_config)
    
    # Initialize database
    with app.app_context():
        init_db()
    
    # Register blueprints
    app.register_blueprint(api_blueprint, url_prefix=API_PREFIX)
    
    # Enable CORS
    CORS(app)
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Remove database session at the end of the request."""
        SessionLocal.remove()
    
    return app
