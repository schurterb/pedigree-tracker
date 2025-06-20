"""
Application configuration settings.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# Database configuration
DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{BASE_DIR}/data/pedigree.db')

# Application settings
DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# API settings
API_PREFIX = '/api/v1'

# Logging configuration
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FILE = os.environ.get('LOG_FILE', str(BASE_DIR / 'logs' / 'app.log'))

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
