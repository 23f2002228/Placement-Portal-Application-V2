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

# Redis/Celery configuration for background jobs.
REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/2'

# Local email configuration. MailHog listens on localhost:1025 during development.
SMTP_HOST = os.environ.get('SMTP_HOST') or 'localhost'
SMTP_PORT = int(os.environ.get('SMTP_PORT') or 1025)
SENDER_EMAIL = os.environ.get('SENDER_EMAIL') or 'placement.portal@example.com'
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD') or ''
