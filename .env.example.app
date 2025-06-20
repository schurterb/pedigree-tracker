# Application Configuration
FLASK_APP=src/app/__main__.py
FLASK_ENV=development
FLASK_DEBUG=1

# Database Configuration
DATABASE_URL=sqlite:///data/pedigree.db

# Application Settings
SECRET_KEY=dev-key-change-in-production
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# API Configuration
API_PREFIX=/api/v1

# CORS Configuration (if needed)
# CORS_ORIGINS=*

# Authentication (to be implemented)
# JWT_SECRET_KEY=your-jwt-secret-key
# JWT_ACCESS_TOKEN_EXPIRES=86400  # 24 hours in seconds
