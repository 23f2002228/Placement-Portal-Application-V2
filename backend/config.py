import os
from datetime import timedelta

# Configuration for development
SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL',
    'sqlite:///placement_portal_final.db'
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# JWT Configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

# Debug mode
DEBUG = True
