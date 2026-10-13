from .base import *
import os
import dj_database_url

# Allow PyMySQL for MySQL connections (common on Aiven MySQL)
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    pass

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production-random-string')

# Turn off DEBUG in production (can be enabled via DEBUG=True environment variable for debugging)
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1')

# PythonAnywhere host format matches `yourusername.pythonanywhere.com` or custom domains
ALLOWED_HOSTS = ['*']

# CSRF trusted origins for PythonAnywhere & custom domains
CSRF_TRUSTED_ORIGINS = [
    'https://*.pythonanywhere.com',
    'http://*.pythonanywhere.com',
]
if os.environ.get('CUSTOM_DOMAIN'):
    CSRF_TRUSTED_ORIGINS.append(f"https://{os.environ.get('CUSTOM_DOMAIN')}")
    CSRF_TRUSTED_ORIGINS.append(f"http://{os.environ.get('CUSTOM_DOMAIN')}")

# Add whitenoise to middleware right after SecurityMiddleware (which is index 0)
# This serves static files efficiently in production.
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Database configuration: supports Aiven PostgreSQL / MySQL via DATABASE_URL or individual env vars
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('AIVEN_DATABASE_URL')

if DATABASE_URL:
    is_postgres = 'postgres' in DATABASE_URL.lower()
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=is_postgres
        )
    }
    # Ensure SSL settings for PostgreSQL if using psycopg2
    if is_postgres and 'postgresql' in DATABASES['default'].get('ENGINE', ''):
        DATABASES['default'].setdefault('OPTIONS', {})['sslmode'] = os.environ.get('DB_SSLMODE', 'require')
elif os.environ.get('DB_HOST') and os.environ.get('DB_NAME'):
    # In case user enters individual fields instead of URI
    engine = 'django.db.backends.postgresql' if os.environ.get('DB_ENGINE', '').lower() in ('postgres', 'postgresql') else 'django.db.backends.mysql'
    DATABASES = {
        'default': {
            'ENGINE': engine,
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': os.environ.get('DB_PORT', '5432' if 'postgresql' in engine else '3306'),
            'OPTIONS': {
                'sslmode': os.environ.get('DB_SSLMODE', 'require')
            } if 'postgresql' in engine else {
                'ssl': {'ssl_mode': 'REQUIRED'}
            }
        }
    }
else:
    # Safe fallback to local SQLite if no external DB configured
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Production static settings
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# Enable WhiteNoise compression and caching
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
