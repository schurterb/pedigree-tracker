"""
Main application entry point.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .config import LOG_LEVEL, LOG_FILE, DEBUG
from .database import init_db

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

# Create a file handler for logging
file_handler = RotatingFileHandler(
    LOG_FILE, 
    maxBytes=1024 * 1024,  # 1MB
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(getattr(logging, LOG_LEVEL))
logger.addHandler(file_handler)

def create_app():
    """
    Application factory function to create and configure the Flask app.
    
    Returns:
        Flask: The configured Flask application instance.
    """
    # Get project root directory
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    www_folder = os.path.join(project_dir, 'www')
    
    app = Flask(__name__, static_folder=None)  # Disable default static folder
    
    # Enable CORS for all routes
    CORS(app)
    
    # Load configuration
    app.config.from_object('src.app.config')
    
    # Initialize database
    with app.app_context():
        from .database import init_db
        init_db()
    
    # Register blueprints
    from .api import api_bp
    
    # Register API blueprint at root path
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Serve static files from www directory
    @app.route('/', defaults={'path': 'index.html'})
    @app.route('/<path:path>')
    def serve_static(path):
        # Avoid serving files from /api path
        if path.startswith('api/'):
            return jsonify({
                'error': 'Not Found',
                'message': 'The requested URL was not found on the server.'
            }), 404
        return send_from_directory(www_folder, path)
        
    # Serve static files from www directory under / route
    @app.route('/', defaults={'path': 'index.html'})
    @app.route('/<path:path>')
    def serve_pedigree_tracker(path):
        # Avoid serving files from /api path
        if path.startswith('api/'):
            return jsonify({
                'error': 'Not Found',
                'message': 'The requested URL was not found on the server.'
            }), 404
        return send_from_directory(www_folder, path)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested URL was not found on the server.'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An internal server error occurred.'
        }), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({
            'error': error.name,
            'message': error.description
        }), error.code
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy'})
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=DEBUG, host='0.0.0.0', port=8000)
