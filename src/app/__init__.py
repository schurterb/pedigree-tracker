"""
Pedigree Tracker Application

This package contains the core functionality for the Pedigree Tracker application.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .config import DATABASE_URI, DEBUG, SECRET_KEY, API_PREFIX, LOG_LEVEL, LOG_FILE
from . import database as app_db
from .database import init_db
from .api import api_bp as api_blueprint

__version__ = "0.1.0"


def _configure_logging():
    """Configure root/app logging with a rotating file handler."""
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=1024 * 1024, backupCount=10  # 1MB
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    file_handler.setLevel(getattr(logging, LOG_LEVEL))

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
        root_logger.addHandler(file_handler)


def create_app(test_config=None):
    """Create and configure the Flask application.

    Args:
        test_config (dict, optional): Testing configuration. Defaults to None.

    Returns:
        Flask: The configured Flask application.
    """
    _configure_logging()

    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    www_folder = os.path.join(project_dir, "www")

    app = Flask(__name__, static_folder=None)

    # Configure the app
    app.config.update(
        SECRET_KEY=SECRET_KEY,
        DEBUG=DEBUG,
        SQLALCHEMY_DATABASE_URI=DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    # Accept both /path and /path/ for all routes without redirects.
    # Must be set before blueprints/routes are registered (bound at first request).
    app.url_map.strict_slashes = False

    # Initialize database
    with app.app_context():
        init_db()

    # Register blueprints
    app.register_blueprint(api_blueprint, url_prefix=API_PREFIX)

    # Enable CORS - Allow all methods on '/api/*' from same domain/IP (any port)
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        vary_header=True,
    )

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Remove database session at the end of the request."""
        app_db.SessionLocal.remove()

    # Serve static files from www directory
    @app.route("/", defaults={"path": "index.html"})
    @app.route("/<path:path>")
    def serve_static(path):
        # Avoid serving files from /api path
        if path.startswith("api/"):
            return (
                jsonify(
                    {
                        "error": "Not Found",
                        "message": "The requested URL was not found on the server.",
                    }
                ),
                404,
            )
        return send_from_directory(www_folder, path)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": "The requested URL was not found on the server.",
                }
            ),
            404,
        )

    @app.errorhandler(500)
    def internal_error(error):
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An internal server error occurred.",
                }
            ),
            500,
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({"error": error.name, "message": error.description}), error.code

    # Health check endpoint
    @app.route("/health")
    def health_check():
        return jsonify({"status": "healthy"})

    return app
