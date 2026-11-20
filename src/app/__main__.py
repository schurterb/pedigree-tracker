"""
Main application entry point.
"""
import os

from . import create_app
from .config import DEBUG

if __name__ == "__main__":
    app = create_app()
    app.run(debug=DEBUG, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
